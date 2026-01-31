import sys
import time
import random
import threading
import math
import traceback
import shutil
import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, colorchooser

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
    if os.name == 'nt':
        os.system("title ULTRA_DECK REBORN")
    else:
        sys.stdout.write("\x1b]2;ULTRA_DECK REBORN\x07")
    os.system("cls" if os.name=='nt' else "clear")

    # 1. Start Audio Thread
    audio = AudioPump()
    audio.start()

    # 2. Setup Renderer
    renderer = Renderer()

    # 3. State Init
    state = DEFAULT_STATE.copy()
    last_load = 0

    # 4. Main Loop
    last_dev_name = ""

    while True:
        try:
            # A. Sync Config
            if os.path.exists(CONFIG_FILE) and os.path.getmtime(CONFIG_FILE) > last_load:
                with open(CONFIG_FILE, 'r') as f:
                    new_state = DEFAULT_STATE.copy()
                    new_state.update(json.load(f))
                    state = new_state
                    last_load = time.time()

            # B. Push Device to Audio Thread
            if state['dev_name'] != last_dev_name:
                audio.set_device(state['dev_name'])
                last_dev_name = state['dev_name']

            # C. Screen Size
            cols, lines = shutil.get_terminal_size()
            h = lines - 2; w = cols

            # D. Render
            output = renderer.render(state, audio, w, h)

            sys.stdout.write(output)
            sys.stdout.flush()
            time.sleep(1.0 / state['fps'])

        except Exception:
            pass # Keep alive

# ==========================================
# /// CONTROLLER ///
# ==========================================
def run_controller():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as f: json.dump(DEFAULT_STATE, f)
    state = DEFAULT_STATE.copy()

    root = tk.Tk(); root.title("ULTRA_DECK REBORN"); root.geometry("500x950"); root.configure(bg="#151515"); style = ttk.Style(); style.theme_use('clam')

    def save_state():
        try:
            with open(CONFIG_FILE, 'w') as f: json.dump(state, f)
        except: pass
    def set_val(k, v): state[k] = v; save_state()

    def launch():
        import subprocess
        cmd_path = os.path.abspath(__file__)
        py_exe = sys.executable

        if os.name == 'nt':
             # "start" on Windows takes the first quoted argument as the window title
             subprocess.Popen(f'start "ULTRA_DECK REBORN" cmd /k "{py_exe}" "{cmd_path}" --engine', shell=True)
        else:
             # Try to find a terminal emulator
             terminals = ['x-terminal-emulator', 'gnome-terminal', 'konsole', 'xterm']
             term_cmd = None
             for t in terminals:
                 if shutil.which(t):
                     if t == 'gnome-terminal':
                         term_cmd = [t, '--', py_exe, cmd_path, '--engine']
                     elif t == 'x-terminal-emulator' or t == 'xterm':
                         term_cmd = [t, '-e', f'{py_exe} "{cmd_path}" --engine']
                     elif t == 'konsole':
                          term_cmd = [t, '-e', py_exe, cmd_path, '--engine']
                     break

             if term_cmd:
                 subprocess.Popen(term_cmd)
             else:
                 # Fallback
                 print("No known terminal emulator found. Running in background.")
                 subprocess.Popen([py_exe, cmd_path, '--engine'])

    tk.Button(root, text=">>> START ENGINE <<<", command=launch, bg="#00ff00").pack(fill="x", padx=10, pady=10)

    nb = ttk.Notebook(root); nb.pack(fill="both", expand=True)
    t_main = tk.Frame(nb, bg="#151515"); nb.add(t_main, text="MAIN")
    t_opt = tk.Frame(nb, bg="#151515"); nb.add(t_opt, text="OPTIONS")

    # --- AUDIO DEVICE SELECTOR ---
    def get_devs():
        try: import sounddevice as sd; return [f"[{i}] {d['name']}" for i, d in enumerate(sd.query_devices()) if d['max_input_channels']>0]
        except: return []

    tk.Label(t_main, text="AUDIO SOURCE", bg="#151515", fg="white").pack(pady=5)
    cb_dev = ttk.Combobox(t_main, values=get_devs())
    cb_dev.pack(fill="x", padx=5)
    cb_dev.bind("<<ComboboxSelected>>", lambda e: set_val('dev_name', cb_dev.get()))
    tk.Button(t_main, text="REFRESH DEVICES", command=lambda: cb_dev.config(values=get_devs())).pack(fill="x", padx=5)

    # --- CONTROLS ---
    tk.Scale(t_main, from_=0.1, to=10.0, resolution=0.1, orient="horizontal", label="SENSITIVITY", bg="#222", fg="white", command=lambda v: set_val('sens', float(v))).pack(fill="x", padx=5)
    tk.Scale(t_main, from_=-90, to=-10, orient="horizontal", label="NOISE FLOOR", bg="#222", fg="white", command=lambda v: set_val('noise_floor', float(v))).pack(fill="x", padx=5)

    cb_theme = ttk.Combobox(t_main, values=list(THEMES.keys()))
    cb_theme.set("Vaporeon")
    cb_theme.pack(fill="x", padx=5, pady=5)
    cb_theme.bind("<<ComboboxSelected>>", lambda e: set_val('theme_name', cb_theme.get()))

    # --- TEXT ---
    t_input = tk.Text(t_opt, height=5, bg="#222", fg="white"); t_input.insert("1.0", "SYSTEM\nONLINE"); t_input.pack(fill="x")
    t_input.bind("<KeyRelease>", lambda e: set_val('text_str', t_input.get("1.0", "end-1c")))
    tk.Button(t_opt, text="TOGGLE TEXT", command=lambda: set_val('text_on', not state['text_on'])).pack(fill="x")

    # --- IMAGES ---
    def set_img(k):
        p = filedialog.askopenfilename()
        if p: state[k] = p; state[k.replace('path','on')] = True; save_state()
    def clr_img(k): state[k] = ""; state[k.replace('path','on')] = False; save_state()

    tk.Button(t_opt, text="LOAD BG IMAGE", command=lambda: set_img('img_bg_path')).pack(fill="x", pady=5)
    tk.Button(t_opt, text="CLEAR BG", command=lambda: clr_img('img_bg_path')).pack(fill="x")
    tk.Button(t_opt, text="LOAD FG TEXTURE", command=lambda: set_img('img_fg_path')).pack(fill="x", pady=5)
    tk.Button(t_opt, text="CLEAR FG", command=lambda: clr_img('img_fg_path')).pack(fill="x")

    root.mainloop()

if __name__ == "__main__":
    if "--engine" in sys.argv:
        run_engine()
    else:
        run_controller()
