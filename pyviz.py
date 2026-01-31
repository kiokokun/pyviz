import sys
import time
import random
import threading
import math
import traceback
import shutil
import os
import json
from logger import setup_logger

logger = setup_logger("PyViz")

# ==========================================
# /// SYSTEM CORE ///
# ==========================================
from config import CONFIG_FILE, PRESETS_FILE, DEFAULT_STATE, THEMES, FONT_MAP
from audio_engine import AudioPump
from renderer import Renderer

# ==========================================
# /// VISUALIZER RENDERER ///
# ==========================================
def run_engine():
    logger.info("Starting Visualizer Engine")
    # 1. Start Audio Thread
    audio = AudioPump()
    audio.start()

    # 2. Setup Renderer
    renderer = Renderer()

    # 3. State Management Wrapper
    class StateManager:
        def __init__(self):
            self.state = DEFAULT_STATE.copy()
            self.last_load = 0
            self.last_dev_name = ""

        def get_state(self):
            try:
                if os.path.exists(CONFIG_FILE) and os.path.getmtime(CONFIG_FILE) > self.last_load:
                    with open(CONFIG_FILE, 'r') as f:
                        new_state = DEFAULT_STATE.copy()
                        new_state.update(json.load(f))
                        self.state = new_state
                        self.last_load = time.time()
            except: pass

            # Push device update if changed
            if self.state['dev_name'] != self.last_dev_name:
                audio.set_device(self.state['dev_name'])
                self.last_dev_name = self.state['dev_name']

            return self.state

    manager = StateManager()

    # 4. Hand over control to Rich Render Loop
    try:
        renderer.render_loop(manager.get_state, audio)
    except KeyboardInterrupt:
        logger.info("Engine stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Engine crash: {e}", exc_info=True)
        # Fallback to simple file for catastrophic failure
        with open("error.log", "w") as f:
            f.write(traceback.format_exc())

# ==========================================
# /// CONTROLLER ///
# ==========================================
def run_controller():
    # Deprecated Tkinter controller replaced by TUI
    from tui import PyVizController
    app = PyVizController()
    app.run()

if __name__ == "__main__":
    if "--engine" in sys.argv:
        run_engine()
    else:
        run_controller()
