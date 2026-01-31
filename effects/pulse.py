from .base import BaseEffect

class PulseEffect(BaseEffect):
    def __init__(self):
        super().__init__()
        self.active_color = (255, 255, 255)
        self.intensity = 0.0

    def update(self, state, audio_data):
        if audio_data.is_beat:
            self.intensity = 1.0
            # Use beat confidence to modulate brightness?
            # For now just max
        else:
            self.intensity *= 0.85 # Decay

        if self.intensity < 0.01:
            self.intensity = 0.0

    def draw(self, buf, cbf, w, h, color_func):
        if self.intensity <= 0: return

        # Flash background
        # We need to construct a background color that is a mix of current BG and Flash Color
        # But our simple renderer just sets BG codes.

        # Let's just override empty spaces with a flash color for now
        # Or change the background color of everything?

        # Simple approach: Flash the edges or random spots?
        # Actually, let's just make the HUD color flash
        pass
