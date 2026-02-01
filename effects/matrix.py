import random
from typing import List, Tuple, Callable, Any
from .base import BaseEffect

GREEN = (0, 255, 0)
BRIGHT_GREEN = (150, 255, 150)
DARK_GREEN = (0, 50, 0)
BLACK = (0, 0, 0)

class MatrixColumn:
    def __init__(self, x: int, h: int):
        self.x = x
        self.y = float(random.randint(-h, 0))
        self.speed = random.uniform(0.2, 0.5)
        self.length = random.randint(5, 20)
        self.chars = [random.choice("0123456789") for _ in range(h + 20)]
        self.active = True

    def update(self, h: int, speed_mult: float):
        self.y += self.speed * speed_mult
        if self.y - self.length > h:
            self.y = float(random.randint(-10, -1))
            self.speed = random.uniform(0.2, 0.5)
            self.length = random.randint(5, 20)

class MatrixEffect(BaseEffect):
    def __init__(self) -> None:
        super().__init__()
        self.columns: List[MatrixColumn] = []
        self.chars = "01XY" # Simple matrix chars

    def update(self, state: dict, audio_data: Any) -> None:
        # Check if enabled via state? For now, we'll need a toggle in TUI.
        # But for this step, I'll assume it's always instanced but maybe toggled by a specific "Matrix" mode or just an effect switch.
        # The user asked for "Matrix Rain", so I'll add a boolean to config later.

        # Audio Reactivity
        vol = audio_data.volume
        is_beat = audio_data.is_beat

        speed_mult = 1.0 + (vol * 0.1)
        if is_beat: speed_mult += 2.0

        # We need width to manage columns.
        # Draw passes W/H, but Update usually doesn't.
        # We'll handle column creation in Draw if needed, or just update existing ones.
        pass

    def draw(self, buf: List[List[str]], cbf: List[List[Any]], w: int, h: int, color_func: Callable) -> None:
        # Initialize Columns if size changed
        if len(self.columns) != w:
            self.columns = [MatrixColumn(x, h) for x in range(w)]

        # We process update here because we need W/H context sometimes
        # But ideally update logic is separated. For simplicity in this visualizer structure,
        # doing physics in draw loop (if delta time isn't critical) is acceptable,
        # but let's try to be clean.

        # Since 'update' didn't get W/H, we do physics here.
        # Assuming we can access the audio volume from somewhere?
        # Actually update() was called just before draw().
        # But we didn't store audio_data. Let's store it in update.

        pass

    # Refactoring slightly to match the pattern:
    # Update stores data, Draw renders.

    def update(self, state: dict, audio_data: Any) -> None:
        self.vol = audio_data.volume
        self.is_beat = audio_data.is_beat
        self.enabled = state.get('matrix_rain', False)

    def draw(self, buf: List[List[str]], cbf: List[List[Any]], w: int, h: int, color_func: Callable) -> None:
        if not self.enabled: return

        if len(self.columns) != w:
            self.columns = [MatrixColumn(x, h) for x in range(w)]

        speed_mult = 1.0 + (self.vol * 0.2)
        if self.is_beat: speed_mult *= 1.5

        for col in self.columns:
            col.update(h, speed_mult)

            # Draw Column
            head_y = int(col.y)
            for i in range(col.length):
                y = head_y - i
                if 0 <= y < h:
                    # Char Logic
                    # Randomly flip char sometimes
                    if random.random() < 0.05:
                        col.chars[y] = random.choice("01XYZ<>*")

                    char = col.chars[y]

                    # Color Logic
                    if i == 0: # Head
                        rgb = BRIGHT_GREEN
                        char = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
                    elif i < 3:
                        rgb = GREEN
                    else:
                        # Fade out
                        fade = 1.0 - (i / col.length)
                        rgb = (0, int(255 * fade * 0.5), 0)

                    # Audio Flash
                    if self.is_beat:
                         rgb = (rgb[0] + 50, rgb[1] + 50, rgb[2] + 50)

                    # Write to buffer
                    # Note: Matrix typically overrides everything.
                    # If we want it as a background, we only write if empty?
                    # Or overlay? The user said "Matrix Rain Effect", implies overlay or mode.
                    # I will make it overlay (write over space).

                    buf[y][col.x] = char
                    cbf[y][col.x] = color_func(rgb, BLACK)
