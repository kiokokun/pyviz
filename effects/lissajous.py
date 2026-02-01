from typing import List, Tuple, Callable, Any
from .base import BaseEffect

CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
BLACK = (0, 0, 0)

class LissajousEffect(BaseEffect):
    def __init__(self) -> None:
        super().__init__()
        self.enabled = False
        self.left = []
        self.right = []

    def update(self, state: dict, audio_data: Any) -> None:
        self.enabled = state.get('lissajous_mode', False)
        if not self.enabled: return
        self.left = audio_data.raw_pcm_left
        self.right = audio_data.raw_pcm_right

    def draw(self, buf: List[List[str]], cbf: List[List[Any]], w: int, h: int, color_func: Callable) -> None:
        if not self.enabled: return
        if len(self.left) == 0 or len(self.right) == 0: return

        # Plot Left vs Right
        # Downsample to a reasonable point count (e.g. 1000 points) to avoid too much density
        step = max(1, len(self.left) // 1000)

        center_x = w // 2
        center_y = h // 2

        for i in range(0, len(self.left), step):
            l = self.left[i] # X axis approx
            r = self.right[i] # Y axis approx

            # Rotate 45 deg?
            # Standard Lissajous: X=L, Y=R

            x = int(center_x + l * (w * 0.4))
            y = int(center_y - r * (h * 0.4))

            if 0 <= x < w and 0 <= y < h:
                buf[y][x] = "+"
                # Color gradient based on index (time)
                fade = i / len(self.left)
                r_col = int(255 * fade)
                b_col = int(255 * (1.0 - fade))
                cbf[y][x] = color_func((r_col, 0, b_col), BLACK)
