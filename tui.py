from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.widgets import Header, Footer, Button, Label, Select, Input, Static, TabbedContent, TabPane, Switch
from textual.reactive import reactive
import json
import os
import sys
import shutil
import subprocess
from config import CONFIG_FILE, DEFAULT_STATE, THEMES
from logger import setup_logger

logger = setup_logger("TUI")

class PyVizController(App):
    CSS = """
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
    """

    TITLE = "PyViz Controller"
    SUB_TITLE = "Terminal Interface"

    def compose(self) -> ComposeResult:
        yield Header()

        with TabbedContent():
            with TabPane("Main", id="tab_main"):
                with Vertical(classes="box"):
                    yield Label("Audio Source")
                    yield Select([], id="dev_select", prompt="Select Input Device")
                    yield Button("Refresh Devices", id="refresh_dev", variant="primary")

                with Vertical(classes="box"):
                    yield Label("Sensitivity")
                    with Horizontal():
                        yield Button("-", id="sens_down")
                        yield Label("1.0", id="sens_val")
                        yield Button("+", id="sens_up")

                    yield Label("Theme")
                    yield Select([(k, k) for k in THEMES.keys()], id="theme_select")

                yield Button(">>> LAUNCH ENGINE <<<", id="launch_btn", variant="success")

            with TabPane("Visuals", id="tab_visuals"):
                with ScrollableContainer():
                    with Vertical(classes="box"):
                        yield Label("Visual Style")
                        yield Select([("Char", "2"), ("Block", "1"), ("Line", "0")], id="style_select")

                        yield Label("Bar Characters")
                        yield Input(value="  ▂▃▄▅▆▇█", id="bar_chars_input")

                        with Horizontal(classes="control-row"):
                            yield Label("Show Stars", classes="control-label")
                            yield Switch(value=True, id="stars_switch")

                        with Horizontal(classes="control-row"):
                            yield Label("Show Peaks", classes="control-label")
                            yield Switch(value=True, id="peaks_switch")

                        with Horizontal(classes="control-row"):
                            yield Label("Mirror Mode", classes="control-label")
                            yield Switch(value=False, id="mirror_switch")

                    with Vertical(classes="box"):
                        yield Label("Physics Settings")

                        yield Label("Gravity")
                        with Horizontal():
                            yield Button("-", id="grav_down")
                            yield Label("0.25", id="grav_val")
                            yield Button("+", id="grav_up")

                        yield Label("Smoothing")
                        with Horizontal():
                            yield Button("-", id="smooth_down")
                            yield Label("0.15", id="smooth_val")
                            yield Button("+", id="smooth_up")

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

        yield Footer()

    def on_mount(self) -> None:
        self.load_state()
        self.refresh_devices()

    def load_state(self):
        if not os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'w') as f: json.dump(DEFAULT_STATE, f)

        try:
            with open(CONFIG_FILE, 'r') as f:
                self.state = json.load(f)
        except:
            self.state = DEFAULT_STATE.copy()

        # Update UI Elements
        # Main
        self.query_one("#sens_val", Label).update(str(self.state.get('sens', 1.0)))
        theme_sel = self.query_one("#theme_select", Select)
        theme_sel.value = self.state.get('theme_name', 'Vaporeon')

        # Visuals
        # Style logic: config stores 0, 1, 2. Select expects str value? No, value is whatever we passed.
        # But Select values in constructor were strings.
        style_val = str(self.state.get('style', 2))
        self.query_one("#style_select", Select).value = style_val
        self.query_one("#bar_chars_input", Input).value = self.state.get('bar_chars', "  ▂▃▄▅▆▇█")
        self.query_one("#stars_switch", Switch).value = self.state.get('stars', True)
        self.query_one("#peaks_switch", Switch).value = self.state.get('peaks_on', True)
        self.query_one("#mirror_switch", Switch).value = self.state.get('mirror', False)

        self.query_one("#grav_val", Label).update(str(self.state.get('gravity', 0.25)))
        self.query_one("#smooth_val", Label).update(str(self.state.get('smoothing', 0.15)))

        # Text
        self.query_one("#text_input", Input).value = self.state.get('text_str', '')
        self.query_one("#text_switch", Switch).value = self.state.get('text_on', True)
        self.query_one("#text_glitch_switch", Switch).value = self.state.get('text_glitch', False)
        self.query_one("#font_select", Select).value = self.state.get('text_font', 'Standard')

        self.query_one("#afk_switch", Switch).value = self.state.get('afk_enabled', True)
        self.query_one("#afk_text_input", Input).value = self.state.get('afk_text', 'brb')
        self.query_one("#afk_timeout_input", Input).value = str(self.state.get('afk_timeout', 30))


    def save_state(self):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.state, f)
        except: pass

    # --- Event Handlers ---

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "refresh_dev":
            self.refresh_devices()
        elif bid == "launch_btn":
            self.launch_engine()
        elif bid == "sens_up":
            self.state['sens'] = round(self.state.get('sens', 1.0) + 0.1, 1)
            self.query_one("#sens_val", Label).update(str(self.state['sens']))
            self.save_state()
        elif bid == "sens_down":
            self.state['sens'] = round(max(0.1, self.state.get('sens', 1.0) - 0.1), 1)
            self.query_one("#sens_val", Label).update(str(self.state['sens']))
            self.save_state()
        elif bid == "grav_up":
            self.state['gravity'] = round(min(1.0, self.state.get('gravity', 0.25) + 0.05), 2)
            self.query_one("#grav_val", Label).update(str(self.state['gravity']))
            self.save_state()
        elif bid == "grav_down":
            self.state['gravity'] = round(max(0.05, self.state.get('gravity', 0.25) - 0.05), 2)
            self.query_one("#grav_val", Label).update(str(self.state['gravity']))
            self.save_state()
        elif bid == "smooth_up":
            self.state['smoothing'] = round(min(0.95, self.state.get('smoothing', 0.15) + 0.05), 2)
            self.query_one("#smooth_val", Label).update(str(self.state['smoothing']))
            self.save_state()
        elif bid == "smooth_down":
            self.state['smoothing'] = round(max(0.05, self.state.get('smoothing', 0.15) - 0.05), 2)
            self.query_one("#smooth_val", Label).update(str(self.state['smoothing']))
            self.save_state()

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

        self.save_state()

    def on_input_changed(self, event: Input.Changed) -> None:
        iid = event.input.id
        val = event.value

        if iid == "text_input":
            self.state['text_str'] = val
        elif iid == "bar_chars_input":
            self.state['bar_chars'] = val
        elif iid == "afk_text_input":
            self.state['afk_text'] = val
        elif iid == "afk_timeout_input":
            try: self.state['afk_timeout'] = int(val)
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
        elif sid == "afk_switch": self.state['afk_enabled'] = val

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
            if os.name == 'nt':
                 # Windows: start requires a title as the first quoted argument.
                 # cmd /k needs the entire command to be wrapped in quotes if it contains quotes
                 # to prevent it from stripping the first and last quote incorrectly.
                 # We wrap the command in outer quotes with spaces to ensure cmd processing preserves the inner quotes.
                 cmd_str = f'start "PyViz Engine" cmd /k " "{py_exe}" "{cmd_path}" --engine "'
                 logger.info(f"Launching on Windows with command: {cmd_str}")
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
                     subprocess.Popen(term_cmd)
                 else:
                     self.notify("No terminal found. Running in background.", severity="warning")
                     bg_cmd = [py_exe, cmd_path, '--engine']
                     logger.info(f"Launching in background (no terminal found): {bg_cmd}")
                     subprocess.Popen(bg_cmd)
        except Exception as e:
            logger.error(f"Failed to launch engine: {e}", exc_info=True)
            self.notify(f"Launch Error: {str(e)}", severity="error")

if __name__ == "__main__":
    import shutil
    app = PyVizController()
    app.run()
