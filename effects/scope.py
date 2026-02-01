from typing import List, Tuple, Callable, Any
from .base import BaseEffect

GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

class OscilloscopeEffect(BaseEffect):
    def __init__(self) -> None:
        super().__init__()
        self.enabled = False
        self.pcm = []

    def update(self, state: dict, audio_data: Any) -> None:
        self.enabled = state.get('scope_mode', False)
        if not self.enabled: return
        self.pcm = audio_data.raw_pcm

    def draw(self, buf: List[List[str]], cbf: List[List[Any]], w: int, h: int, color_func: Callable) -> None:
        if not self.enabled: return

        if len(self.pcm) == 0: return

        import numpy as np

        # Resample PCM to screen width
        indices = np.linspace(0, len(self.pcm)-1, w).astype(int)
        view = self.pcm[indices]

        prev_y = h // 2

        for x in range(w):
            sample = view[x] # Float -1.0 to 1.0

            # Map to screen Y
            y = int(((sample * -0.5) + 0.5) * h)
            y = max(0, min(h-1, y))

            # Draw line from prev_y to y
            # Simple Bresenham-like vertical fill
            start = min(prev_y, y)
            end = max(prev_y, y)

            for dy in range(start, end + 1):
                buf[dy][x] = "-" if dy == y else "|"
                cbf[dy][x] = color_func(GREEN, BLACK)

            prev_y = y
