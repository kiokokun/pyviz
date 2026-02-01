import random
from typing import List, Tuple, Callable, Any
from .base import BaseEffect

WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)

class PongEffect(BaseEffect):
    def __init__(self) -> None:
        super().__init__()
        # Ball
        self.bx = 0.5
        self.by = 0.5
        self.bvx = 0.015
        self.bvy = 0.01

        # Paddles (0.0 - 1.0 vertical pos)
        self.p1_y = 0.5
        self.p2_y = 0.5

        self.score_l = 0
        self.score_r = 0

        self.vol = 0.0
        self.is_beat = False
        self.enabled = False

    def update(self, state: dict, audio_data: Any) -> None:
        self.enabled = state.get('pong_mode', False)
        if not self.enabled: return

        self.vol = audio_data.volume
        self.is_beat = audio_data.is_beat

    def draw(self, buf: List[List[str]], cbf: List[List[Any]], w: int, h: int, color_func: Callable) -> None:
        if not self.enabled: return

        # Physics Step (Sub-stepping for smoothness?)
        # We just do one step per frame for TUI

        # Speed modulation by audio
        speed_mult = 1.0 + (self.vol * 0.1)
        if self.is_beat: speed_mult = 2.0

        # Move Ball
        self.bx += self.bvx * speed_mult
        self.by += self.bvy * speed_mult

        # Ceiling/Floor collision
        if self.by <= 0:
            self.by = 0
            self.bvy *= -1
        elif self.by >= 1.0:
            self.by = 1.0
            self.bvy *= -1

        # Paddle AI (Simple Tracking)
        # Left Paddle
        target_y = self.by
        # Reaction delay/error based on speed?
        self.p1_y += (target_y - self.p1_y) * 0.15

        # Right Paddle
        self.p2_y += (target_y - self.p2_y) * 0.15

        # Paddle Dimensions
        pad_h_norm = 0.2 # 20% of screen height

        # Paddle Collision logic
        # Left (x=0)
        if self.bx <= 0.02: # Near left edge
            # Check overlap
            if abs(self.p1_y - self.by) < pad_h_norm / 2:
                self.bvx = abs(self.bvx) # Bounce right
                self.bx = 0.02
                # Audio hit effect?
            elif self.bx < 0:
                # Score
                self.score_r += 1
                self.reset_ball()

        # Right (x=1)
        if self.bx >= 0.98:
            if abs(self.p2_y - self.by) < pad_h_norm / 2:
                self.bvx = -abs(self.bvx) # Bounce left
                self.bx = 0.98
            elif self.bx > 1:
                self.score_l += 1
                self.reset_ball()

        # Rendering

        # Draw Net
        mid_x = w // 2
        for y in range(0, h, 2):
            buf[y][mid_x] = "|"
            cbf[y][mid_x] = color_func(GRAY, BLACK)

        # Draw Paddles
        ph = int(h * pad_h_norm)

        # P1
        p1_cy = int(self.p1_y * h)
        p1_top = max(0, p1_cy - ph // 2)
        p1_bot = min(h, p1_top + ph)
        for y in range(p1_top, p1_bot):
            buf[y][1] = "█"
            cbf[y][1] = color_func(WHITE, BLACK)

        # P2
        p2_cy = int(self.p2_y * h)
        p2_top = max(0, p2_cy - ph // 2)
        p2_bot = min(h, p2_top + ph)
        for y in range(p2_top, p2_bot):
            buf[y][w-2] = "█"
            cbf[y][w-2] = color_func(WHITE, BLACK)

        # Draw Ball
        bx_int = int(self.bx * w)
        by_int = int(self.by * h)
        if 0 <= bx_int < w and 0 <= by_int < h:
            buf[by_int][bx_int] = "●"

            # Beat flash color
            col = (255, 50, 50) if self.is_beat else WHITE
            cbf[by_int][bx_int] = color_func(col, BLACK)

        # Draw Score
        score_str = f"{self.score_l}  {self.score_r}"
        sx = (w - len(score_str)) // 2
        if 0 <= sx < w:
            for i, c in enumerate(score_str):
                if 0 <= sx+i < w:
                    buf[1][sx+i] = c
                    cbf[1][sx+i] = color_func(WHITE, BLACK)

    def reset_ball(self):
        self.bx = 0.5
        self.by = 0.5
        self.bvx = random.choice([-0.015, 0.015])
        self.bvy = random.uniform(-0.01, 0.01)
