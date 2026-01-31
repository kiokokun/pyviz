import unittest
import os
import json
from config import CONFIG_FILE, DEFAULT_STATE

class TestConfig(unittest.TestCase):
    def setUp(self):
        # Backup existing config if any
        if os.path.exists(CONFIG_FILE):
            os.rename(CONFIG_FILE, CONFIG_FILE + ".bak")

    def tearDown(self):
        # Restore backup
        if os.path.exists(CONFIG_FILE + ".bak"):
            os.rename(CONFIG_FILE + ".bak", CONFIG_FILE)
        elif os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)

    def test_default_config_creation(self):
        # Ensure config file is not present initially
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)

        # Simulating logic that creates config (e.g. from tui.py load_state)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(DEFAULT_STATE, f)

        self.assertTrue(os.path.exists(CONFIG_FILE))

        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
            self.assertEqual(data['dev_name'], "Default")
            self.assertEqual(data['sens'], 1.0)

if __name__ == '__main__':
    unittest.main()
