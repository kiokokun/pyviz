import sys
import time
import threading
import traceback
import shutil
import os
import json
import argparse
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

    # Ensure audio stops on exit
    import atexit
    _cleanup_done = False

    def cleanup():
        nonlocal _cleanup_done
        if _cleanup_done: return
        _cleanup_done = True

        logger.info("Stopping audio thread...")
        audio.running = False
        if audio.is_alive():
            audio.join(timeout=0.5)

    atexit.register(cleanup)

    audio.start()

    # 2. Setup Renderer
    renderer = Renderer()

    # 3. State Management Wrapper
    class StateManager:
        def __init__(self):
            self.state = DEFAULT_STATE.copy()
            self.last_load_time = 0
            self.last_check = 0
            self.last_dev_name = ""

        def get_state(self):
            # Performance: Only check file system every 1.0 seconds
            now = time.time()
            if now - self.last_check > 1.0:
                self.last_check = now
                try:
                    if os.path.exists(CONFIG_FILE):
                        mtime = os.path.getmtime(CONFIG_FILE)
                        if mtime > self.last_load_time:
                            with open(CONFIG_FILE, 'r') as f:
                                new_state = DEFAULT_STATE.copy()
                                new_state.update(json.load(f))
                                self.state = new_state
                                self.last_load_time = mtime
                except Exception:
                    pass

            # Push device update if changed
            if self.state['dev_name'] != self.last_dev_name:
                audio.set_device(self.state['dev_name'])
                self.last_dev_name = self.state['dev_name']

            # Push beat threshold
            audio.set_config(self.state)

            return self.state

    manager = StateManager()

    # 4. Hand over control to Rich Render Loop
    try:
        renderer.render_loop(manager.get_state, audio)
    except KeyboardInterrupt:
        logger.info("Engine stopped by user")
        # Cleanup handled by finally
    except Exception as e:
        logger.critical(f"Engine crash: {e}", exc_info=True)
        # Fallback to simple file for catastrophic failure
        with open("error.log", "w") as f:
            f.write(traceback.format_exc())
    finally:
        cleanup()

# ==========================================
# /// CONTROLLER ///
# ==========================================
def run_controller():
    # Check dependencies before importing TUI
    missing = []
    try: import textual
    except ImportError: missing.append("textual")

    try: import sounddevice
    except ImportError: missing.append("sounddevice")

    try: import numpy
    except ImportError: missing.append("numpy")

    try: import PIL
    except ImportError: missing.append("Pillow")

    if missing:
        print(f"ERROR: Missing libraries: {', '.join(missing)}")
        print("Please run 'pip install -r requirements.txt'")
        sys.exit(1)

    from tui import PyVizController
    app = PyVizController()
    app.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PyViz Audio Visualizer")
    parser.add_argument("--engine", action="store_true", help="Run the rendering engine directly")
    args = parser.parse_args()

    if args.engine:
        run_engine()
    else:
        run_controller()
