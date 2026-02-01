from .base import BaseEffect
import random

class GlitchEffect(BaseEffect):
    def __init__(self):
        super().__init__()
        self.active = False
        self.duration = 0

    def update(self, state, audio_data):
        intensity = float(state.get('glitch', 0.0))
        if intensity <= 0:
            self.active = False
            return

        # Scale chance by intensity (0.0 to 1.0)
        # Base chance 30% at max intensity
        chance = 0.3 * intensity

        if audio_data.is_beat and random.random() < chance:
            self.active = True
            self.duration = 3

        if self.duration > 0:
            self.duration -= 1
        else:
            self.active = False

    def draw(self, buf, cbf, w, h, color_func):
        if not self.active: return

        # Random character replacements
        for _ in range(int(w * h * 0.05)): # 5% of screen
            rx = random.randint(0, w-1)
            ry = random.randint(0, h-1)
            char_pool = "!@#$%^&*()_+"
            buf[ry][rx] = random.choice(char_pool)
            # Maybe random color too
            cbf[ry][rx] = color_func((random.randint(0,255), random.randint(0,255), random.randint(0,255)))
