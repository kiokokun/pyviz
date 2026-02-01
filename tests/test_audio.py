import unittest
from unittest.mock import MagicMock
import sys

# Mock sounddevice and numpy before importing audio_engine
sys.modules['sounddevice'] = MagicMock()
sys.modules['numpy'] = MagicMock()

from audio_engine import AudioPump

class TestAudioEngine(unittest.TestCase):
    def test_initialization(self):
        pump = AudioPump()
        self.assertEqual(pump.volume, 0.0)
        self.assertEqual(pump.status, "IDLE")
        self.assertFalse(pump.is_beat)

    def test_device_setting(self):
        pump = AudioPump()

        # Mock query_devices to return a matching device
        pump.sd = MagicMock()
        pump.sd.query_devices.return_value = {'name': 'Test Device', 'max_input_channels': 2}

        # Mock default device
        pump.sd.default.device = [99, 88] # [Input, Output]

        # This will now pass verification
        pump.set_device("[1] Test Device")
        self.assertEqual(pump.device_index, 1)

        # Test Default behavior
        pump.set_device("Default")
        self.assertEqual(pump.device_index, 99)

if __name__ == '__main__':
    unittest.main()
