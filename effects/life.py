import random
from typing import List, Tuple, Callable, Any
from .base import BaseEffect

RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

class GameOfLifeEffect(BaseEffect):
    def __init__(self) -> None:
        super().__init__()
        self.enabled = False
        self.grid = []
        self.w = 0
        self.h = 0
        self.frame_skip = 0

    def update(self, state: dict, audio_data: Any) -> None:
        self.enabled = state.get('life_mode', False)
        if not self.enabled: return

        # Beat triggers random spawn
        if audio_data.is_beat:
             # Add random noise
             if self.w > 0 and self.h > 0:
                 for _ in range(20):
                     rx = random.randint(0, self.w-1)
                     ry = random.randint(0, self.h-1)
                     self.grid[ry][rx] = 1

    def step(self):
        if self.w == 0 or self.h == 0: return
        new_grid = [[0 for _ in range(self.w)] for _ in range(self.h)]

        for y in range(self.h):
            for x in range(self.w):
                # Count neighbors
                n = 0
                for dy in [-1,0,1]:
                    for dx in [-1,0,1]:
                        if dx==0 and dy==0: continue
                        nx, ny = x+dx, y+dy
                        if 0 <= nx < self.w and 0 <= ny < self.h:
                            if self.grid[ny][nx]: n += 1

                if self.grid[y][x]:
                    if n == 2 or n == 3: new_grid[y][x] = 1
                else:
                    if n == 3: new_grid[y][x] = 1

        self.grid = new_grid

    def draw(self, buf: List[List[str]], cbf: List[List[Any]], w: int, h: int, color_func: Callable) -> None:
        if not self.enabled: return

        # Resize grid if needed
        if w != self.w or h != self.h:
            self.w = w
            self.h = h
            self.grid = [[0 for _ in range(w)] for _ in range(h)]
            # Init random
            for y in range(h):
                for x in range(w):
                    if random.random() < 0.2: self.grid[y][x] = 1

        # Evolution speed control
        self.frame_skip += 1
        if self.frame_skip > 2: # Every 3rd frame
            self.step()
            self.frame_skip = 0

        for y in range(h):
            for x in range(w):
                if self.grid[y][x]:
                    buf[y][x] = "o"
                    cbf[y][x] = color_func(YELLOW, BLACK)
