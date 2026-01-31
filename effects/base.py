class BaseEffect:
    """
    Abstract base class for visual effects.
    """
    def __init__(self):
        self.enabled = True

    def update(self, state, audio_data):
        """
        Update internal state based on audio and configuration.

        Args:
            state (dict): The global configuration state.
            audio_data (object): The audio engine instance (access volume, raw_fft).
        """
        pass

    def draw(self, buf, cbf, w, h, color_func):
        """
        Draw to the character and color buffers.

        Args:
            buf (list): 2D list of characters (strings).
            cbf (list): 2D list of color strings (ANSI codes).
            w (int): Width of the buffer.
            h (int): Height of the buffer.
            color_func (callable): Function that takes (r,g,b) and returns ANSI color string.
        """
        pass
