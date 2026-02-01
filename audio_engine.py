import threading
import time
from typing import Optional, List, Any
from logger import setup_logger

logger = setup_logger("AudioEngine")

try:
    import sounddevice as sd # type: ignore
    import numpy as np
    AUDIO_AVAILABLE = True
except (ImportError, OSError) as e:
    sd = None
    np = None
    AUDIO_AVAILABLE = False
    logger.critical(f"Audio libraries missing: {e}")

class AudioPump(threading.Thread):
    """
    Handles audio input, FFT processing, and beat detection in a separate thread.
    """
    def __init__(self) -> None:
        super().__init__()
        self.daemon = True
        self.running: bool = True if AUDIO_AVAILABLE else False
        self.device_index: Optional[int] = None
        self.lock = threading.Lock()

        # Shared Data
        if AUDIO_AVAILABLE:
            self.raw_fft: Any = np.zeros(1024)
            self.raw_fft_left: Any = np.zeros(1024)
            self.raw_fft_right: Any = np.zeros(1024)
            self.raw_pcm: Any = np.zeros(2048) # Mono
            self.raw_pcm_left: Any = np.zeros(2048)
            self.raw_pcm_right: Any = np.zeros(2048)
        else:
            self.raw_fft = []
            self.raw_fft_left = []
            self.raw_fft_right = []
            self.raw_pcm = []
            self.raw_pcm_left = []
            self.raw_pcm_right = []

        self.volume: float = 0.0
        self.status: str = "IDLE"
        self.connected_device: str = "None"
        self.target_device_name: Optional[str] = None

        # Beat Detection
        self.is_beat: bool = False
        self.beat_confidence: float = 0.0
        self.last_beat_time: float = 0.0
        self.energy_history: List[float] = []
        self.beat_thresh: float = 1.4 # Default
        self.glitch_enabled: bool = False

        self.sd = sd if AUDIO_AVAILABLE else None
        self.np = np if AUDIO_AVAILABLE else None

    def set_config(self, config: dict) -> None:
        """Update audio engine config safely."""
        try:
            self.beat_thresh = 1.0 + float(config.get('bass_thresh', 0.7)) # 0.7 -> 1.7 threshold
            self.glitch_enabled = (float(config.get('glitch', 0.0)) > 0.0)
        except Exception: pass

    def set_device(self, dev_name: str) -> None:
        with self.lock:
            self.target_device_name = dev_name
            self._resolve_device_index()

    def _resolve_device_index(self):
        """Attempts to find the device index from self.target_device_name"""
        dev_name = self.target_device_name

        if not self.sd:
            self.device_index = None
            return

        # Handle Default / Empty
        if not dev_name or dev_name == "Default":
            try:
                # Use system default input device
                def_idx = self.sd.default.device[0]
                self.device_index = def_idx
                logger.info(f"Using system default input device index: {def_idx}")
                return
            except Exception as e:
                logger.warning(f"Could not get system default device: {e}")
                # Fallback to searching for first input
                pass

        if not dev_name:
             self.device_index = None
             return

        # Parse ID if present "[81] Name"
        if dev_name.startswith("["):
            try:
                idx_str = dev_name.split("]")[0].replace("[", "")
                target_idx = int(idx_str)

                # Verify if device at this index matches the name (roughly)
                try:
                    info = self.sd.query_devices(target_idx)
                    # Check if name roughly matches (ignoring partial variations)
                    if info['name'] in dev_name or dev_name.split("]")[1].strip() in info['name']:
                        self.device_index = target_idx
                        logger.info(f"Selected device index: {self.device_index}")
                        return
                    else:
                        logger.warning(f"Device index {target_idx} mismatch. Expected {dev_name}, got {info['name']}. Fallback to search.")
                except Exception:
                    pass
            except Exception:
                pass

        # Fallback: Search by name
        logger.info(f"Searching for device: {dev_name}")
        try:
            found_idx = None
            clean_name = dev_name
            if "]" in dev_name: clean_name = dev_name.split("]")[1].strip()

            for i, d in enumerate(self.sd.query_devices()):
                if clean_name in d['name'] and d['max_input_channels'] > 0:
                    found_idx = i
                    break

            self.device_index = found_idx
            if found_idx is not None:
                    logger.info(f"Found device '{clean_name}' at index {found_idx}")
            else:
                    logger.warning(f"Device '{clean_name}' not found. Using default.")
                    self.device_index = None
        except:
            self.device_index = None

    def _process_fft(self, signal):
        """Helper to compute FFT log magnitude"""
        if len(signal) == 0: return np.zeros(1024)
        win = signal * self.np.hanning(len(signal))
        fft = self.np.abs(self.np.fft.rfft(win))[:1024]
        # Log scaling
        db = 20 * self.np.log10(fft + 1e-9)
        return db

    def run(self) -> None:
        if not self.running:
            return

        while self.running:
            try:
                if self.device_index is None:
                    # Try to resolve again
                    if self.target_device_name:
                        self._resolve_device_index()

                    # Wait for device selection
                    time.sleep(0.5)
                    # Check again if devices appeared (in case of empty list earlier)
                    if self.sd:
                        try:
                            if len(self.sd.query_devices()) > 0:
                                # Trigger auto-search again? For now just wait.
                                pass
                        except: pass
                    continue

                if self.sd is None or self.np is None:
                    time.sleep(1)
                    continue

                # Open Stream in Blocking Mode (Robust)
                try:
                    dev_info = self.sd.query_devices(self.device_index, 'input')
                    rate = int(dev_info['default_samplerate'])
                    self.connected_device = f"{dev_info['name']} @ {rate}Hz"
                    self.status = "CONNECTED"
                    logger.info(f"Connected to {self.connected_device}")

                    # Safe blocksize logic
                    blocksize = 2048

                    # Try to open with 2 channels, but fallback if device only supports 1
                    channels = 2
                    if dev_info['max_input_channels'] < 2:
                        channels = 1
                        logger.info("Device only supports 1 channel. Forcing mono.")

                    with self.sd.InputStream(device=self.device_index, channels=channels, samplerate=rate, blocksize=blocksize) as stream:
                        while self.running and self.device_index is not None:
                            # Check stream status
                            if not stream.active:
                                raise OSError("Stream inactive")

                            # READ RAW DATA
                            data, overflow = stream.read(blocksize)
                            if overflow:
                                logger.warning("Audio buffer overflow")

                            if self.np.any(data):
                                # Extract Channels
                                if channels == 2:
                                    left = data[:, 0]
                                    right = data[:, 1]
                                    # Mono mix for beat detection
                                    mono = (left + right) / 2
                                else:
                                    # Mono Device
                                    if len(data.shape) > 1:
                                        mono = data[:, 0]
                                    else:
                                        mono = data
                                    left = mono
                                    right = mono

                                # Store Raw PCM
                                self.raw_pcm = mono
                                self.raw_pcm_left = left
                                self.raw_pcm_right = right

                                self.volume = float(self.np.linalg.norm(mono) * 10) # Rough volume

                                # Beat Detection (Simple Energy Based)
                                if self.glitch_enabled:
                                    # Focus on Bass frequencies (approx 20-150Hz)
                                    # Assuming 44.1kHz / 2048 samples -> ~21.5Hz per bin.
                                    # So bass is roughly first 10 bins
                                    bass_energy = float(self.np.sum(self.np.abs(mono))) # Simplified overall energy for now

                                    curr_time = time.time()
                                    self.energy_history.append(bass_energy)
                                    if len(self.energy_history) > 40: # ~1-2 seconds history
                                        self.energy_history.pop(0)

                                    avg_energy = sum(self.energy_history) / len(self.energy_history)

                                    # Threshold: Instant energy > Thresh * average
                                    if bass_energy > avg_energy * self.beat_thresh and (curr_time - self.last_beat_time) > 0.3:
                                        self.is_beat = True
                                        self.beat_confidence = min(1.0, (bass_energy / (avg_energy + 1e-5)) - 1.0)
                                        self.last_beat_time = curr_time
                                    else:
                                        self.is_beat = False
                                        self.beat_confidence = max(0.0, self.beat_confidence * 0.8) # Decay
                                else:
                                    self.is_beat = False

                                # Compute FFTs
                                self.raw_fft = self._process_fft(mono)
                                self.raw_fft_left = self._process_fft(left)
                                self.raw_fft_right = self._process_fft(right)
                            else:
                                self.volume = 0.0
                                self.is_beat = False
                except (OSError, self.sd.PortAudioError) as e:
                    self.status = f"AUDIO ERROR: {str(e)[:15]}... RETRYING"
                    logger.error(f"Audio stream error: {e}")
                    self.volume = 0.0
                    self.device_index = None # Force re-resolution
                    time.sleep(2) # Cooldown before reconnect

            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                self.status = f"CRITICAL: {str(e)[:20]}"
                logger.critical(f"Unexpected error in audio loop: {e}", exc_info=True)
                self.volume = 0.0
                time.sleep(2)
