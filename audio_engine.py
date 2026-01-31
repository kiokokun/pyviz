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

                            win = mono * self.np.hanning(len(mono))
                            fft = self.np.abs(self.np.fft.rfft(win))[:1024]

                            # Log scaling
                            db = 20 * self.np.log10(fft + 1e-9)

                            # Thread-safe update
                            self.raw_fft = db
                        else:
                            self.volume = 0.0

            except Exception as e:
                self.status = f"ERROR: {str(e)[:20]}"
                self.volume = 0.0
                time.sleep(2)
