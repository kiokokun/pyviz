from typing import List, Tuple, Callable, Any
from .base import BaseEffect

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
BLACK = (0, 0, 0)

class WaterfallEffect(BaseEffect):
    def __init__(self) -> None:
        super().__init__()
        self.history = [] # List of rows (fft data)
        self.enabled = False

    def update(self, state: dict, audio_data: Any) -> None:
        self.enabled = state.get('waterfall_mode', False)
        if not self.enabled: return

        # Store current FFT row
        # Normalize?
        fft = audio_data.raw_fft
        if len(fft) > 0:
            # Downsample to some reasonable width if needed, but we do that in draw usually.
            # Let's store raw FFT for now.
            self.history.insert(0, fft)
            if len(self.history) > 200: # Limit history depth
                self.history.pop()

    def draw(self, buf: List[List[str]], cbf: List[List[Any]], w: int, h: int, color_func: Callable) -> None:
        if not self.enabled: return

        # Draw history top-down
        for y in range(h):
            if y < len(self.history):
                row_data = self.history[y]
                # Resample row to width w
                if len(row_data) == 0: continue

                import numpy as np
                indices = np.linspace(0, len(row_data)-1, w).astype(int)
                resampled = row_data[indices]

                for x in range(w):
                    val = resampled[x] # dB value approx -60 to 0

                    # Color map based on intensity
                    # -60 -> Blue, -30 -> Green, 0 -> Red
                    norm = (val + 60) / 60.0 # 0.0 to 1.0
                    norm = max(0.0, min(1.0, norm))

                    if norm > 0.1:
                        # Heatmap
                        r = int(norm * 255)
                        g = int((1.0 - abs(0.5 - norm) * 2) * 255)
                        b = int((1.0 - norm) * 255)

                        char = " "
                        if norm > 0.8: char = "#"
                        elif norm > 0.5: char = ":"
                        elif norm > 0.2: char = "."

                        buf[y][x] = char
                        cbf[y][x] = color_func((r,g,b), BLACK)
