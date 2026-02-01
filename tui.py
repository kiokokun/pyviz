from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.widgets import Header, Footer, Button, Label, Select, Input, Static, TabbedContent, TabPane, Switch, DirectoryTree
from textual.screen import ModalScreen
from textual.reactive import reactive
import json
import os
import sys
import shutil
import subprocess
from config import CONFIG_FILE, DEFAULT_STATE, THEMES, CHAR_SETS
from logger import setup_logger

logger = setup_logger("TUI")

# Extracted CSS for better readability
MAIN_CSS = """
Screen {
    layout: vertical;
    background: $surface-darken-1;
}
.box {
    height: auto;
    border: solid green;
    margin: 1;
    padding: 1;
}
Button {
    width: 100%;
    margin-top: 1;
}
Label {
    margin-top: 1;
}
.control-row {
    height: auto;
    margin-bottom: 1;
    align: center middle;
}
.control-label {
    width: 50%;
}
Switch {
    width: auto;
}
/* Compact adjustment row */
.adjust-row {
    height: auto;
    align: center middle;
    margin-top: 1;
}
.adjust-btn {
    width: 4;
    min-width: 4;
}
.adjust-input {
    width: 1fr;
    height: auto;
    margin: 0 1;
    text-align: center;
}
.input-error {
    border: solid red;
}
/* File Picker */
FileOpenScreen {
    align: center middle;
}
#file_dialog {
    width: 80%;
    height: 80%;
    border: thick $accent;
    background: $surface;
}

/* UI Themes */
.theme-retro Screen {
    background: black;
    color: #ffb000;
}
.theme-retro .box {
    border: double #ffb000;
}
.theme-retro Button {
    color: black;
    background: #ffb000;
    border: none;
}

.theme-cyber Screen {
    background: #0d0221;
    color: #00ff41;
}
.theme-cyber .box {
    border: heavy #00f3ff;
}
.theme-cyber Button {
    background: #ff00ff;
    color: white;
}

.theme-gothic Screen {
    background: #1a0505;
    color: #8a0303;
}
.theme-gothic .box {
    border: ascii red;
}
.theme-gothic Button {
    background: #2b0000;
    color: #ff0000;
}
"""

UI_THEMES = {
    "Default": {
        "class": "",
        "title": "PyViz Controller"
    },
    "Retro": {
        "class": "theme-retro",
        "title": ">>> P Y V I Z <<<"
    },
    "Cyber": {
        "class": "theme-cyber",
        "title": "PYVIZ_NET_TERMINAL_V2"
    },
    "Gothic": {
        "class": "theme-gothic",
        "title": "The Visualizer"
    }
}

class FileOpenScreen(ModalScreen[str]):
    """Modal screen for selecting a file."""

    def compose(self) -> ComposeResult:
        start_path = os.path.expanduser("~")
        if not os.path.exists(start_path):
            start_path = "/" # Fallback

        with Vertical(id="file_dialog"):
            yield Label("Select Image File", id="file_title")
            yield DirectoryTree(start_path, id="tree")
            with Horizontal():
                yield Button("Cancel", id="cancel_btn", variant="error")

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        self.dismiss(str(event.path))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel_btn":
            self.dismiss(None)

class PyVizController(App):
    """
    Main TUI Controller for PyViz.
    """
    engine_process = None
    CSS = MAIN_CSS

    TITLE = "PyViz Controller"
    SUB_TITLE = "Terminal Interface"

    def compose(self) -> ComposeResult:
        yield Header()

        with TabbedContent():
            with TabPane("Main", id="tab_main"):
                with Vertical(classes="box"):
                    yield Label("Audio Source")
                    yield Select([], id="dev_select", prompt="Select Input Device", tooltip="Select the audio input device (requires restart if engine running)")
                    yield Button("Refresh Devices", id="refresh_dev", variant="primary", tooltip="Reload list of audio devices")

                with Vertical(classes="box"):
                    yield Label("Sensitivity")
                    with Horizontal(classes="adjust-row"):
                        yield Button("-", id="sens_down", classes="adjust-btn")
                        yield Input(value="1.0", id="sens_input", classes="adjust-input", tooltip="Microphone sensitivity multiplier")
                        yield Button("+", id="sens_up", classes="adjust-btn")

                    yield Label("Theme")
                    yield Select([(k, k) for k in THEMES.keys()], id="theme_select", tooltip="Color palette for the visualizer")

                    yield Label("UI Theme (Controller)")
                    ui_opts = [(k, k) for k in UI_THEMES.keys()]
                    yield Select(ui_opts, id="ui_theme_select", value="Default", tooltip="Theme for this settings window")

            with TabPane("Visuals", id="tab_visuals"):
                with ScrollableContainer():
                    with Vertical(classes="box"):
                        yield Label("Visual Style")
                        yield Select([("Char", "2"), ("Block", "1"), ("Line", "0")], id="style_select", tooltip="Rendering style (Characters, Solid Blocks, or Line)")

                        yield Label("Character Preset")
                        char_opts = [(k, v) for k, v in CHAR_SETS.items()]
                        yield Select(char_opts, id="char_preset_select", prompt="Select Preset", tooltip="Select a predefined character set (Overwrites Bar Characters)")

                        yield Label("Bar Characters")
                        yield Input(value="  ▂▃▄▅▆▇█", id="bar_chars_input", tooltip="Custom characters for bars (from low to high volume)")

                        with Horizontal(classes="control-row"):
                            yield Label("Show Stars", classes="control-label")
                            yield Switch(value=True, id="stars_switch", tooltip="Enable background starfield effect")

                        with Horizontal(classes="control-row"):
                            yield Label("Show Peaks", classes="control-label")
                            yield Switch(value=True, id="peaks_switch", tooltip="Show falling peak indicators")

                        with Horizontal(classes="control-row"):
                            yield Label("Mirror Mode", classes="control-label")
                            yield Switch(value=False, id="mirror_switch", tooltip="Mirror the visualization horizontally")

                    with Vertical(classes="box"):
                        yield Label("Physics Settings")

                        yield Label("Gravity")
                        with Horizontal(classes="adjust-row"):
                            yield Button("-", id="grav_down", classes="adjust-btn")
                            yield Input(value="0.25", id="grav_input", classes="adjust-input")
                            yield Button("+", id="grav_up", classes="adjust-btn")

                        yield Label("Smoothing")
                        with Horizontal(classes="adjust-row"):
                            yield Button("-", id="smooth_down", classes="adjust-btn")
                            yield Input(value="0.15", id="smooth_input", classes="adjust-input")
                            yield Button("+", id="smooth_up", classes="adjust-btn")

                        yield Label("Noise Floor (dB)")
                        yield Input(value="-60.0", id="noise_input", classes="adjust-input")

                        yield Label("Auto Gain")
                        yield Switch(value=True, id="gain_switch")

            with TabPane("Advanced", id="tab_adv"):
                with ScrollableContainer():
                    with Vertical(classes="box"):
                        yield Label("Advanced Audio")
                        yield Label("Rise Speed")
                        yield Input(value="0.6", id="rise_input", classes="adjust-input", tooltip="How fast bars react to sound (0.0-1.0)")

                        yield Label("Bass Threshold")
                        yield Input(value="0.7", id="bass_input", classes="adjust-input", tooltip="Frequency cutoff for bass detection")

                    with Vertical(classes="box"):
                        yield Label("Advanced Visuals")
                        yield Label("Peak Gravity")
                        yield Input(value="0.15", id="peak_grav_input", classes="adjust-input", tooltip="How fast peak indicators fall")

                        yield Label("Glitch Intensity")
                        yield Input(value="0.0", id="glitch_input", classes="adjust-input", tooltip="Random visual glitch effect intensity")

                        yield Label("Target FPS")
                        yield Input(value="30", id="fps_input", classes="adjust-input", tooltip="Target Frames Per Second (default 30)")

                    yield Button("RESET TO DEFAULTS", id="reset_btn", variant="error", tooltip="Reset all settings to factory defaults")

            with TabPane("Images", id="tab_images"):
                with ScrollableContainer():
                    with Vertical(classes="box"):
                        yield Label("Background Image")
                        with Horizontal():
                            yield Input(placeholder="Path to image...", id="bg_img_path", classes="adjust-input")
                            yield Button("Browse", id="bg_browse_btn", classes="adjust-btn")

                        with Horizontal(classes="control-row"):
                            yield Label("Enabled", classes="control-label")
                            yield Switch(value=False, id="bg_img_switch")
                        with Horizontal(classes="control-row"):
                            yield Label("Flip", classes="control-label")
                            yield Switch(value=False, id="bg_img_flip")

                        yield Label("Image Style")
                        yield Select([("Char", "2"), ("Block", "1")], id="img_style_select")

                        yield Label("Image Char Set")
                        char_opts = [(k, k) for k in CHAR_SETS.keys()]
                        yield Select(char_opts, id="img_preset_select")

                    with Vertical(classes="box"):
                        yield Label("Foreground Image (Texture)")
                        with Horizontal():
                            yield Input(placeholder="Path to image...", id="fg_img_path", classes="adjust-input")
                            yield Button("Browse", id="fg_browse_btn", classes="adjust-btn")

                        with Horizontal(classes="control-row"):
                            yield Label("Enabled", classes="control-label")
                            yield Switch(value=False, id="fg_img_switch")
                        with Horizontal(classes="control-row"):
                            yield Label("Flip", classes="control-label")
                            yield Switch(value=False, id="fg_img_flip")

            with TabPane("Text & AFK", id="tab_text"):
                with ScrollableContainer():
                    with Vertical(classes="box"):
                        yield Label("Overlay Text")
                        yield Input(placeholder="Enter text...", id="text_input")

                        with Horizontal(classes="control-row"):
                            yield Label("Show Text", classes="control-label")
                            yield Switch(value=True, id="text_switch")

                        with Horizontal(classes="control-row"):
                            yield Label("Glitch Text", classes="control-label")
                            yield Switch(value=False, id="text_glitch_switch")

                        with Horizontal(classes="control-row"):
                            yield Label("Scroll Text", classes="control-label")
                            yield Switch(value=False, id="text_scroll_switch")

                        yield Label("Text Position Y (0.0-1.0)")
                        yield Input(value="0.5", id="text_pos_input", classes="adjust-input")

                        yield Label("Text Font")
                        # "Tiny":"term", "Standard":"standard", "Big":"big", "Slant":"slant", "Block":"block", "Lean":"lean"
                        fonts = [("Tiny", "Tiny"), ("Standard", "Standard"), ("Big", "Big"), ("Slant", "Slant"), ("Block", "Block"), ("Lean", "Lean")]
                        yield Select(fonts, id="font_select")

                    with Vertical(classes="box"):
                        yield Label("AFK Mode")
                        with Horizontal(classes="control-row"):
                            yield Label("Enable AFK", classes="control-label")
                            yield Switch(value=True, id="afk_switch")

                        yield Label("AFK Text")
                        yield Input(value="brb", id="afk_text_input")

                        yield Label("AFK Timeout (sec)")
                        yield Input(value="30", id="afk_timeout_input")

        yield Button(">>> LAUNCH ENGINE <<<", id="launch_btn", variant="success")
        yield Footer()

    def on_unmount(self) -> None:
        if self.engine_process:
            try:
                self.engine_process.terminate()
                logger.info("Terminated engine subprocess on exit.")
            except: pass

    def on_mount(self) -> None:
        self.load_state_from_file()
        self.refresh_devices()

    def load_state_from_file(self):
        if not os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'w') as f: json.dump(DEFAULT_STATE, f)

        try:
            with open(CONFIG_FILE, 'r') as f:
                self.state = json.load(f)
        except Exception:
            self.state = DEFAULT_STATE.copy()

        self.sync_ui_to_state()

    def sync_ui_to_state(self):
        # Update UI Elements
        # Main
        self.query_one("#sens_input", Input).value = str(self.state.get('sens', 1.0))
        theme_sel = self.query_one("#theme_select", Select)
        theme_sel.value = self.state.get('theme_name', 'Vaporeon')

        # Restore UI Theme (if we saved it, or just default)
        ui_theme = self.state.get('ui_theme', 'Default')
        if ui_theme in UI_THEMES:
            self.query_one("#ui_theme_select", Select).value = ui_theme
            self.set_ui_theme(ui_theme)

        # Visuals
        style_val = str(self.state.get('style', 2))
        self.query_one("#style_select", Select).value = style_val
        self.query_one("#bar_chars_input", Input).value = self.state.get('bar_chars', "  ▂▃▄▅▆▇█")
        self.query_one("#stars_switch", Switch).value = self.state.get('stars', True)
        self.query_one("#peaks_switch", Switch).value = self.state.get('peaks_on', True)
        self.query_one("#mirror_switch", Switch).value = self.state.get('mirror', False)

        self.query_one("#grav_input", Input).value = str(self.state.get('gravity', 0.25))
        self.query_one("#smooth_input", Input).value = str(self.state.get('smoothing', 0.15))
        self.query_one("#noise_input", Input).value = str(self.state.get('noise_floor', -60.0))
        self.query_one("#gain_switch", Switch).value = self.state.get('auto_gain', True)

        # Advanced
        self.query_one("#rise_input", Input).value = str(self.state.get('rise_speed', 0.6))
        self.query_one("#bass_input", Input).value = str(self.state.get('bass_thresh', 0.7))
        self.query_one("#peak_grav_input", Input).value = str(self.state.get('peak_gravity', 0.15))
        self.query_one("#glitch_input", Input).value = str(self.state.get('glitch', 0.0))
        self.query_one("#fps_input", Input).value = str(self.state.get('fps', 30))

        # Images
        self.query_one("#bg_img_path", Input).value = self.state.get('img_bg_path', '')
        self.query_one("#bg_img_switch", Switch).value = self.state.get('img_bg_on', False)
        self.query_one("#bg_img_flip", Switch).value = self.state.get('img_bg_flip', False)

        self.query_one("#img_style_select", Select).value = str(self.state.get('img_style', 2))
        self.query_one("#img_preset_select", Select).value = self.state.get('img_char_set', 'Blocks')

        self.query_one("#fg_img_path", Input).value = self.state.get('img_fg_path', '')
        self.query_one("#fg_img_switch", Switch).value = self.state.get('img_fg_on', False)
        self.query_one("#fg_img_flip", Switch).value = self.state.get('img_fg_flip', False)

        # Text
        self.query_one("#text_input", Input).value = self.state.get('text_str', '')
        self.query_one("#text_switch", Switch).value = self.state.get('text_on', True)
        self.query_one("#text_glitch_switch", Switch).value = self.state.get('text_glitch', False)
        self.query_one("#text_scroll_switch", Switch).value = self.state.get('text_scroll', False)
        self.query_one("#text_pos_input", Input).value = str(self.state.get('text_pos_y', 0.5))
        self.query_one("#font_select", Select).value = self.state.get('text_font', 'Standard')

        self.query_one("#afk_switch", Switch).value = self.state.get('afk_enabled', True)
        self.query_one("#afk_text_input", Input).value = self.state.get('afk_text', 'brb')
        self.query_one("#afk_timeout_input", Input).value = str(self.state.get('afk_timeout', 30))


    def save_state(self):
        try:
            # Atomic write
            tmp_file = CONFIG_FILE + ".tmp"
            with open(tmp_file, 'w') as f:
                json.dump(self.state, f)
            os.replace(tmp_file, CONFIG_FILE)
        except Exception: pass

    def set_ui_theme(self, theme_name: str):
        # Safe fallback
        if theme_name not in UI_THEMES:
            theme_name = "Default"

        if theme_name in UI_THEMES:
            t_data = UI_THEMES[theme_name]
            self.title = t_data["title"]
            # Reset classes then apply new one
            for t in UI_THEMES.values():
                if t["class"]:
                    self.remove_class(t["class"])

            if t_data["class"]:
                self.add_class(t_data["class"])

    # --- Event Handlers ---

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "refresh_dev":
            self.refresh_devices()
        elif bid == "launch_btn":
            self.launch_engine()
        elif bid == "bg_browse_btn":
            self.open_file_picker("bg")
        elif bid == "fg_browse_btn":
            self.open_file_picker("fg")
        elif bid == "sens_up":
            self.state['sens'] = round(self.state.get('sens', 1.0) + 0.1, 1)
            self.query_one("#sens_input", Input).value = str(self.state['sens'])
            self.save_state()
        elif bid == "sens_down":
            self.state['sens'] = round(max(0.1, self.state.get('sens', 1.0) - 0.1), 1)
            self.query_one("#sens_input", Input).value = str(self.state['sens'])
            self.save_state()
        elif bid == "grav_up":
            self.state['gravity'] = round(min(1.0, self.state.get('gravity', 0.25) + 0.05), 2)
            self.query_one("#grav_input", Input).value = str(self.state['gravity'])
            self.save_state()
        elif bid == "grav_down":
            self.state['gravity'] = round(max(0.05, self.state.get('gravity', 0.25) - 0.05), 2)
            self.query_one("#grav_input", Input).value = str(self.state['gravity'])
            self.save_state()
        elif bid == "smooth_up":
            self.state['smoothing'] = round(min(0.95, self.state.get('smoothing', 0.15) + 0.05), 2)
            self.query_one("#smooth_input", Input).value = str(self.state['smoothing'])
            self.save_state()
        elif bid == "smooth_down":
            self.state['smoothing'] = round(max(0.05, self.state.get('smoothing', 0.15) - 0.05), 2)
            self.query_one("#smooth_input", Input).value = str(self.state['smoothing'])
            self.save_state()
        elif bid == "reset_btn":
            self.state = DEFAULT_STATE.copy()
            self.sync_ui_to_state()
            self.save_state()
            self.notify("Reset to defaults!", severity="information")

    def open_file_picker(self, target: str):
        def set_file(path: str | None):
            if path:
                if target == "bg":
                    self.query_one("#bg_img_path", Input).value = path
                    self.state['img_bg_path'] = path
                else:
                    self.query_one("#fg_img_path", Input).value = path
                    self.state['img_fg_path'] = path
                self.save_state()

        # Try Native Picker (Windows/Desktop)
        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw() # Hide main window
            root.attributes('-topmost', True) # Bring to front

            path = filedialog.askopenfilename(
                title="Select Image",
                filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.gif;*.bmp"), ("All Files", "*.*")]
            )
            root.destroy()

            if path:
                set_file(path)
            return
        except Exception as e:
            logger.warning(f"Native file picker failed ({e}), falling back to TUI.")

        # Fallback to TUI Picker
        self.push_screen(FileOpenScreen(), set_file)

    def on_select_changed(self, event: Select.Changed) -> None:
        sid = event.select.id
        val = event.value
        if not val: return

        if sid == "theme_select":
            self.state['theme_name'] = str(val)
        elif sid == "dev_select":
            self.state['dev_name'] = str(val)
        elif sid == "style_select":
            self.state['style'] = int(val)
        elif sid == "font_select":
            self.state['text_font'] = str(val)
        elif sid == "char_preset_select":
            # Update bar_chars based on preset
            # Value is the chars themselves
            self.state['bar_chars'] = str(val)
            self.query_one("#bar_chars_input", Input).value = str(val)
        elif sid == "img_style_select":
            self.state['img_style'] = int(val)
        elif sid == "img_preset_select":
            self.state['img_char_set'] = str(val)
        elif sid == "ui_theme_select":
            self.state['ui_theme'] = str(val)
            self.set_ui_theme(str(val))

        self.save_state()

    def on_input_changed(self, event: Input.Changed) -> None:
        iid = event.input.id
        val = event.value

        # Sanitization & Type Conversion
        if iid == "text_input":
            if len(val) > 100: val = val[:100] # Cap length
            self.state['text_str'] = val
        elif iid == "bar_chars_input":
            val = val.replace('\n', '').replace('\r', '')
            if len(val) > 50: val = val[:50]
            self.state['bar_chars'] = val
        elif iid == "afk_text_input":
            if len(val) > 50: val = val[:50]
            self.state['afk_text'] = val
        elif iid == "bg_img_path":
            self.state['img_bg_path'] = val
        elif iid == "fg_img_path":
            self.state['img_fg_path'] = val
        elif iid == "afk_timeout_input":
            try: self.state['afk_timeout'] = max(1, int(val))
            except: pass
        # Numeric inputs
        elif iid == "sens_input":
            try:
                self.state['sens'] = float(val)
                self.query_one("#sens_input", Input).classes = "adjust-input"
            except:
                self.query_one("#sens_input", Input).classes = "adjust-input input-error"
        elif iid == "grav_input":
            try: self.state['gravity'] = float(val)
            except: pass
        elif iid == "smooth_input":
            try: self.state['smoothing'] = float(val)
            except: pass
        elif iid == "noise_input":
            try: self.state['noise_floor'] = float(val)
            except: pass
        elif iid == "rise_input":
            try: self.state['rise_speed'] = float(val)
            except: pass
        elif iid == "bass_input":
            try: self.state['bass_thresh'] = float(val)
            except: pass
        elif iid == "peak_grav_input":
            try: self.state['peak_gravity'] = float(val)
            except: pass
        elif iid == "glitch_input":
            try: self.state['glitch'] = float(val)
            except: pass
        elif iid == "text_pos_input":
            try: self.state['text_pos_y'] = float(val)
            except: pass
        elif iid == "fps_input":
            try: self.state['fps'] = int(val)
            except: pass

        self.save_state()

    def on_switch_changed(self, event: Switch.Changed) -> None:
        sid = event.switch.id
        val = event.value

        if sid == "stars_switch": self.state['stars'] = val
        elif sid == "peaks_switch": self.state['peaks_on'] = val
        elif sid == "mirror_switch": self.state['mirror'] = val
        elif sid == "text_switch": self.state['text_on'] = val
        elif sid == "text_glitch_switch": self.state['text_glitch'] = val
        elif sid == "text_scroll_switch": self.state['text_scroll'] = val
        elif sid == "afk_switch": self.state['afk_enabled'] = val
        elif sid == "gain_switch": self.state['auto_gain'] = val
        elif sid == "bg_img_switch": self.state['img_bg_on'] = val
        elif sid == "bg_img_flip": self.state['img_bg_flip'] = val
        elif sid == "fg_img_switch": self.state['img_fg_on'] = val
        elif sid == "fg_img_flip": self.state['img_fg_flip'] = val

        self.save_state()

    def refresh_devices(self):
        try:
            import sounddevice as sd
            devs = []
            for i, d in enumerate(sd.query_devices()):
                if d['max_input_channels'] > 0:
                    name = f"[{i}] {d['name']}"
                    devs.append((name, name))

            select = self.query_one("#dev_select", Select)
            select.set_options(devs)

            # Restore selection if exists
            current = self.state.get('dev_name', '')
            if any(d[0] == current for d in devs):
                select.value = current

        except:
            self.query_one("#dev_select", Select).set_options([("Error loading devices", "error")])

    def launch_engine(self):
        cmd_path = os.path.abspath("pyviz.py") # Assume in same dir
        py_exe = sys.executable

        try:
            # Check if previous exists
            if self.engine_process:
                if self.engine_process.poll() is None:
                    self.notify("Engine already running!", severity="warning")
                    return

            if os.name == 'nt':
                 # Windows: start requires a title as the first quoted argument.
                 # cmd /k needs the entire command to be wrapped in quotes if it contains quotes
                 # to prevent it from stripping the first and last quote incorrectly.
                 # We wrap the command in outer quotes with spaces to ensure cmd processing preserves the inner quotes.
                 cmd_str = f'start "PyViz Engine" cmd /k " "{py_exe}" "{cmd_path}" --engine "'
                 logger.info(f"Launching on Windows with command: {cmd_str}")
                 # For Windows 'start', we can't track the PID easily because 'start' exits immediately.
                 # So we rely on manual closing.
                 subprocess.Popen(cmd_str, shell=True)
            else:
                 terminals = ['x-terminal-emulator', 'gnome-terminal', 'konsole', 'xterm']
                 term_cmd = None
                 for t in terminals:
                     if shutil.which(t):
                         if t == 'gnome-terminal':
                             term_cmd = [t, '--', py_exe, cmd_path, '--engine']
                         elif t == 'x-terminal-emulator' or t == 'xterm':
                             # Ensure paths with spaces are quoted
                             term_cmd = [t, '-e', f'"{py_exe}" "{cmd_path}" --engine']
                         elif t == 'konsole':
                              term_cmd = [t, '-e', py_exe, cmd_path, '--engine']
                         break

                 if term_cmd:
                     logger.info(f"Launching on Linux/Mac with terminal command: {term_cmd}")
                     # If we launch a terminal, that terminal is the child.
                     self.engine_process = subprocess.Popen(term_cmd)
                 else:
                     self.notify("No terminal found. Running in background.", severity="warning")
                     bg_cmd = [py_exe, cmd_path, '--engine']
                     logger.info(f"Launching in background (no terminal found): {bg_cmd}")
                     self.engine_process = subprocess.Popen(bg_cmd)
        except Exception as e:
            logger.error(f"Failed to launch engine: {e}", exc_info=True)
            self.notify(f"Launch Error: {str(e)}", severity="error")

if __name__ == "__main__":
    import shutil
    app = PyVizController()
    app.run()
