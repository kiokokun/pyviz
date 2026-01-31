import threading
import time

try:
    import sounddevice as sd
    import numpy as np
    AUDIO_AVAILABLE = True
except (ImportError, OSError):
    AUDIO_AVAILABLE = False
    print("CRITICAL: AUDIO LIBS MISSING")

class AudioPump(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.running = True if AUDIO_AVAILABLE else False
        self.device_index = None
        self.lock = threading.Lock()

        # Shared Data
        if AUDIO_AVAILABLE:
            self.raw_fft = np.zeros(1024)
        else:
            self.raw_fft = []

        self.volume = 0.0
        self.status = "IDLE"
        self.connected_device = "None"

        # Beat Detection
        self.is_beat = False
        self.beat_confidence = 0.0
        self.last_beat_time = 0
        self.energy_history = []

        self.sd = sd if AUDIO_AVAILABLE else None
        self.np = np if AUDIO_AVAILABLE else None

    def set_device(self, dev_name):
        with self.lock:
            # Parse ID if present "[81] Name"
            if dev_name.startswith("["):
                try:
                    self.device_index = int(dev_name.split("]")[0].replace("[", ""))
                except:
                    self.device_index = None
            else:
                self.device_index = None # Auto-find later

    def run(self):
        if not self.running:
            return

        while self.running:
            try:
                if self.device_index is None:
                    time.sleep(1)
                    continue

                # Open Stream in Blocking Mode (Robust)
                dev_info = self.sd.query_devices(self.device_index, 'input')
                rate = int(dev_info['default_samplerate'])
                self.connected_device = f"{dev_info['name']} @ {rate}Hz"
                self.status = "CONNECTED"

                with self.sd.InputStream(device=self.device_index, channels=1, samplerate=rate, blocksize=2048) as stream:
                    while self.running and self.device_index is not None:
                        # READ RAW DATA
                        data, overflow = stream.read(2048)
                        if self.np.any(data):
                            # Process FFT
                            mono = data[:, 0]
                            self.volume = self.np.linalg.norm(mono) * 10 # Rough volume

                            # Beat Detection (Simple Energy Based)
                            # Focus on Bass frequencies (approx 20-150Hz)
                            # Assuming 44.1kHz / 2048 samples -> ~21.5Hz per bin.
                            # So bass is roughly first 10 bins
                            bass_energy = self.np.sum(self.np.abs(mono)) # Simplified overall energy for now

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

            except Exception as e:
                self.status = f"ERROR: {str(e)[:20]}"
                self.volume = 0.0
                time.sleep(2)
