import unittest
from unittest.mock import MagicMock
import sys

# Mock deps
sys.modules['PIL'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['rich'] = MagicMock()
sys.modules['rich.live'] = MagicMock()
sys.modules['rich.layout'] = MagicMock()
sys.modules['rich.text'] = MagicMock()
sys.modules['rich.panel'] = MagicMock()
sys.modules['rich.console'] = MagicMock()

# Mock numpy correctly for math operations
mock_np = MagicMock()
mock_np.zeros.return_value = MagicMock()
mock_np.linspace.return_value.astype.return_value = [0] * 100 # Indices
mock_np.max.return_value = 0.5 # Return float, not Mock
mock_np.clip.return_value = MagicMock()
# Allow math ops on mocks
def mock_op(self, other):
    return self
mock_np.zeros.return_value.__mul__ = mock_op
mock_np.zeros.return_value.__add__ = mock_op
# Mock indexing on the arrays
mock_np.zeros.return_value.__getitem__ = lambda self, idx: 0.1 # Return float for comparison
# Mock iteration to return floats
mock_np.zeros.return_value.__iter__ = lambda self: iter([0.1]*100)

sys.modules['numpy'] = mock_np

from renderer import Renderer
from config import DEFAULT_STATE

class TestRenderer(unittest.TestCase):
    def setUp(self):
        self.renderer = Renderer()
        self.mock_audio = MagicMock()
        # Mock raw_fft as a numpy array mock that handles indexing
        mock_array = MagicMock()
        mock_array.__getitem__.return_value = MagicMock() # Return mock on slice
        self.mock_audio.raw_fft = mock_array
        self.mock_audio.volume = 0.5
        self.mock_audio.connected_device = "Test"
        self.mock_audio.status = "OK"

    def test_frame_generation(self):
        # Since we mocked everything, we just check if it runs without error
        try:
            self.renderer.generate_frame(DEFAULT_STATE, self.mock_audio, 80, 24)
        except Exception as e:
            self.fail(f"generate_frame raised exception: {e}")

if __name__ == '__main__':
    unittest.main()
