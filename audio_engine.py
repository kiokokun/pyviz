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
    def __init__(self) -> None:
        super().__init__()
        self.daemon = True
        self.running: bool = True if AUDIO_AVAILABLE else False
        self.device_index: Optional[int] = None
        self.lock = threading.Lock()

        # Shared Data
        if AUDIO_AVAILABLE:
            self.raw_fft: Any = np.zeros(1024)
        else:
            self.raw_fft = []

        self.volume: float = 0.0
        self.status: str = "IDLE"
        self.connected_device: str = "None"

        # Beat Detection
        self.is_beat: bool = False
        self.beat_confidence: float = 0.0
        self.last_beat_time: float = 0.0
        self.energy_history: List[float] = []

        self.sd = sd if AUDIO_AVAILABLE else None
        self.np = np if AUDIO_AVAILABLE else None

    def set_device(self, dev_name: str) -> None:
        with self.lock:
            # Parse ID if present "[81] Name"
            if dev_name.startswith("["):
                try:
                    idx_str = dev_name.split("]")[0].replace("[", "")
                    target_idx = int(idx_str)

                    # Verify if device at this index matches the name (roughly)
                    # This prevents index shifting issues
                    try:
                        info = self.sd.query_devices(target_idx)
                        if info['name'] in dev_name:
                            self.device_index = target_idx
                            logger.info(f"Selected device index: {self.device_index}")
                            return
                        else:
                            logger.warning(f"Device index {target_idx} mismatch. Expected {dev_name}, got {info['name']}. Fallback to search.")
                    except:
                        pass
                except:
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

    def run(self) -> None:
        if not self.running:
            return

        while self.running:
            try:
                if self.device_index is None:
                    time.sleep(1)
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

                    with self.sd.InputStream(device=self.device_index, channels=1, samplerate=rate, blocksize=2048) as stream:
                        while self.running and self.device_index is not None:
                            # Check stream status
                            if not stream.active:
                                raise OSError("Stream inactive")

                            # READ RAW DATA
                            data, overflow = stream.read(2048)
                            if overflow:
                                logger.warning("Audio buffer overflow")

                            if self.np.any(data):
                                # Process FFT
                                mono = data[:, 0]
                                self.volume = float(self.np.linalg.norm(mono) * 10) # Rough volume

                                # Beat Detection (Simple Energy Based)
                                # Focus on Bass frequencies (approx 20-150Hz)
                                # Assuming 44.1kHz / 2048 samples -> ~21.5Hz per bin.
                                # So bass is roughly first 10 bins
                                bass_energy = float(self.np.sum(self.np.abs(mono))) # Simplified overall energy for now

                                curr_time = time.time()
                                self.energy_history.append(bass_energy)
                                if len(self.energy_history) > 40: # ~1-2 seconds history
                                    self.energy_history.pop(0)

                                avg_energy = sum(self.energy_history) / len(self.energy_history)

                                # Threshold: Instant energy > 1.3x average
                                if bass_energy > avg_energy * 1.4 and (curr_time - self.last_beat_time) > 0.3:
                                    self.is_beat = True
                                    self.beat_confidence = min(1.0, (bass_energy / (avg_energy + 1e-5)) - 1.0)
                                    self.last_beat_time = curr_time
                                else:
                                    self.is_beat = False
                                    self.beat_confidence = max(0.0, self.beat_confidence * 0.8) # Decay

                                win = mono * self.np.hanning(len(mono))
                                fft = self.np.abs(self.np.fft.rfft(win))[:1024]

                                # Log scaling
                                db = 20 * self.np.log10(fft + 1e-9)

                                # Thread-safe update
                                self.raw_fft = db
                            else:
                                self.volume = 0.0
                                self.is_beat = False
                except (OSError, self.sd.PortAudioError) as e:
                    self.status = f"AUDIO ERROR: {str(e)[:15]}... RETRYING"
                    logger.error(f"Audio stream error: {e}")
                    self.volume = 0.0
                    time.sleep(2) # Cooldown before reconnect

            except Exception as e:
                self.status = f"CRITICAL: {str(e)[:20]}"
                logger.critical(f"Unexpected error in audio loop: {e}", exc_info=True)
                self.volume = 0.0
                time.sleep(2)
