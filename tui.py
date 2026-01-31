from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Header, Footer, Button, Label, Select, Input, Static
from textual.reactive import reactive
import json
import os
import sys
import shutil
import subprocess
from config import CONFIG_FILE, DEFAULT_STATE, THEMES

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
    """

    TITLE = "PyViz Controller"
    SUB_TITLE = "Terminal Interface"

    def compose(self) -> ComposeResult:
        yield Header()

        with Vertical(classes="box"):
            yield Label("Audio Source")
            yield Select([], id="dev_select", prompt="Select Input Device")
            yield Button("Refresh Devices", id="refresh_dev", variant="primary")

        with Vertical(classes="box"):
            yield Label("Sensitivity")
            # Textual doesn't have a Slider widget built-in yet (in older versions),
            # checking installed version capabilities or using buttons for now.
            # We will use Input for precision or Buttons for +/-
            with Horizontal():
                yield Button("-", id="sens_down")
                yield Label("1.0", id="sens_val")
                yield Button("+", id="sens_up")

            yield Label("Theme")
            yield Select([(k, k) for k in THEMES.keys()], id="theme_select")

        with Vertical(classes="box"):
            yield Label("Overlay Text")
            yield Input(placeholder="Enter text...", id="text_input")
            yield Button("Toggle Text", id="toggle_text")

        yield Button(">>> LAUNCH ENGINE <<<", id="launch_btn", variant="success")
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

        # Update UI
        self.query_one("#sens_val", Label).update(str(self.state.get('sens', 1.0)))
        self.query_one("#theme_select", Select).value = self.state.get('theme_name', 'Vaporeon')
        self.query_one("#text_input", Input).value = self.state.get('text_str', '')

    def save_state(self):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.state, f)
        except: pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "refresh_dev":
            self.refresh_devices()
        elif event.button.id == "launch_btn":
            self.launch_engine()
        elif event.button.id == "sens_up":
            self.state['sens'] = round(self.state.get('sens', 1.0) + 0.1, 1)
            self.query_one("#sens_val", Label).update(str(self.state['sens']))
            self.save_state()
        elif event.button.id == "sens_down":
            self.state['sens'] = round(max(0.1, self.state.get('sens', 1.0) - 0.1), 1)
            self.query_one("#sens_val", Label).update(str(self.state['sens']))
            self.save_state()
        elif event.button.id == "toggle_text":
            self.state['text_on'] = not self.state.get('text_on', True)
            self.save_state()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "theme_select" and event.value:
            self.state['theme_name'] = str(event.value)
            self.save_state()
        elif event.select.id == "dev_select" and event.value:
            self.state['dev_name'] = str(event.value)
            self.save_state()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "text_input":
            self.state['text_str'] = event.value
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

        if os.name == 'nt':
             # Windows: start requires a title as the first quoted argument.
             # cmd /k needs the entire command to be wrapped in quotes if it contains quotes
             # to prevent it from stripping the first and last quote incorrectly.
             subprocess.Popen(f'start "PyViz Engine" cmd /k ""{py_exe}" "{cmd_path}" --engine"', shell=True)
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
                 subprocess.Popen(term_cmd)
             else:
                 self.notify("No terminal found. Running in background.", severity="warning")
                 subprocess.Popen([py_exe, cmd_path, '--engine'])

if __name__ == "__main__":
    import shutil
    app = PyVizController()
    app.run()
