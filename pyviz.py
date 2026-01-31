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
CONFIG_FILE = "deck_settings.json"
PRESETS_FILE = "deck_presets.json"

DEFAULT_STATE = {
    "dev_name": "Default",
    "sens": 1.0, "auto_gain": True, "noise_floor": -60.0,
    "rise_speed": 0.6, "gravity": 0.25, "smoothing": 0.15,
    "style": 2, "mirror": False, "glitch": 0.0, "bass_thresh": 0.7,
    "fps": 30,
    "color_mode": "Theme", "solid_color": [0, 255, 128],
    "grad_start": [0, 0, 255], "grad_end": [0, 255, 255], "theme_name": "Vaporeon",
    "stars": True, "show_vu": False, "peaks_on": True, "peak_gravity": 0.15,
    "bar_chars": "  ▂▃▄▅▆▇█",
    "text_on": True, "text_str": "SYSTEM\nONLINE", "text_font": "Standard",
    "text_scroll": False, "text_glitch": False, "text_pos_y": 0.5,
    "afk_enabled": True, "afk_timeout": 30, "afk_text": "brb", "force_afk": False,
    "img_bg_path": "", "img_bg_on": False, "img_bg_flip": False,
    "img_fg_path": "", "img_fg_on": False, "img_fg_flip": False
}

THEMES = {
    "Eevee": ([160, 110, 60], [230, 220, 180]),
    "Vaporeon": ([20, 50, 180], [100, 220, 255]),
    "Jolteon": ([255, 200, 0], [255, 255, 200]),
    "Flareon": ([200, 40, 0], [255, 180, 100]),
    "Espeon": ([180, 60, 180], [255, 160, 255]),
    "Umbreon": ([20, 20, 20], [255, 230, 50]),
    "Leafeon": ([60, 160, 80], [240, 230, 160]),
    "Glaceon": ([80, 180, 220], [200, 240, 255]),
    "Sylveon": ([255, 140, 180], [160, 220, 255]),
    "Cyberpunk": ([0, 255, 255], [255, 0, 128]),
    "Sunset": ([100, 0, 180], [255, 200, 0]),
    "Matrix": ([0, 50, 0], [50, 255, 50]),
    "Fire": ([255, 0, 0], [255, 255, 0]),
    "Ice": ([0, 50, 255], [200, 255, 255]),
    "Toxic": ([100, 0, 200], [0, 255, 0]),
    "Ocean": ([0, 0, 100], [0, 200, 200]),
    "Candy": ([255, 100, 100], [100, 100, 255]),
    "Gold": ([150, 100, 0], [255, 255, 100]),
    "Neon": ([50, 50, 50], [0, 255, 0]),
    "Vampire": ([50, 0, 0], [255, 0, 0]),
    "Void": ([20, 20, 30], [80, 80, 120]),
    "Forest": ([10, 50, 10], [100, 200, 100]),
    "Love": ([100, 0, 50], [255, 100, 150]),
    "Sky": ([0, 100, 255], [255, 255, 255])
}

FONT_MAP = {"Tiny":"term", "Standard":"standard", "Big":"big", "Slant":"slant", "Block":"block", "Lean":"lean"}

# ==========================================
# /// AUDIO ENGINE REDUX ///
# ==========================================
class AudioPump(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.running = True
        self.device_index = None
        self.lock = threading.Lock()

        # Shared Data
        self.raw_fft = np.zeros(1024)
        self.volume = 0.0
        self.status = "IDLE"
        self.connected_device = "None"

        # Dependencies
        try:
            import sounddevice as sd
            import numpy as np
            self.sd = sd
            self.np = np
        except:
            print("CRITICAL: AUDIO LIBS MISSING")
            self.running = False

    def set_device(self, dev_name):
        with self.lock:
            # Parse ID if present "[81] Name"
            if dev_name.startswith("["):
                try:
                    self.device_index = int(dev_name.split("]")[0].replace("[", ""))
                except:
                    self.device_index = None
            else:
                self.device_index = None # Auto-find later

    def run(self):
        while self.running:
            try:
                if self.device_index is None:
                    time.sleep(1)
                    continue

                # Open Stream in Blocking Mode (Robust)
                dev_info = self.sd.query_devices(self.device_index, 'input')
                rate = int(dev_info['default_samplerate'])
                self.connected_device = f"{dev_info['name']} @ {rate}Hz"
                self.status = "CONNECTED"

                with self.sd.InputStream(device=self.device_index, channels=1, samplerate=rate, blocksize=2048) as stream:
                    while self.running and self.device_index is not None:
                        # READ RAW DATA
                        data, overflow = stream.read(2048)
                        if self.np.any(data):
                            # Process FFT
                            mono = data[:, 0]
                            self.volume = self.np.linalg.norm(mono) * 10 # Rough volume

                            win = mono * self.np.hanning(len(mono))
                            fft = self.np.abs(self.np.fft.rfft(win))[:1024]

                            # Log scaling
                            db = 20 * self.np.log10(fft + 1e-9)

                            # Thread-safe update
                            self.raw_fft = db
                        else:
                            self.volume = 0.0

            except Exception as e:
                self.status = f"ERROR: {str(e)[:20]}"
                self.volume = 0.0
                time.sleep(2)

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
    # 2. Setup Libraries
    try:
        from PIL import Image
        import numpy as np
    except: return

    try: import pyfiglet; HAS_FIGLET = True
    except: HAS_FIGLET = False

    # 3. State Init
    state = DEFAULT_STATE.copy()
    bands = np.zeros(100) # Will resize
    peak_heights = np.zeros(100)

    # Buffers
    buf_bg, buf_fg = [], []
    last_load = 0

    # Helpers
    def process_image(path, w, h):
        if not path or not os.path.exists(path): return []
        try:
            im = Image.open(path).resize((w, h)).convert("RGB"); px = im.load(); new_buf = []
            for y in range(h):
                row = []
                for x in range(w):
                    r,g,b = px[x,y]
                    # Simple char mapping
                    row.append((".", (r,g,b)))
                new_buf.append(row)
            return new_buf
        except: return []

    def get_gradient_color(y, h, start_rgb, end_rgb):
        ratio = y / max(h, 1)
        r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
        g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
        b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
        return (r, g, b)

    class Star:
        def __init__(self): self.reset(True)
        def reset(self, rz=False): self.x=(random.random()-0.5)*2; self.y=(random.random()-0.5)*2; self.z=random.random()*2.0 if rz else 2.0
        def move(self, spd):
            self.z -= spd
            if self.z <= 0.05: self.reset()
        def draw(self, buf, cbf, w, h, cf):
            if self.z <= 0: return
            fx = int((self.x/self.z)*w*0.5+w/2); fy = int((self.y/self.z)*h*0.5+h/2)
            if 0<=fx<w and 0<=fy<h:
                try:
                    if buf[fy][fx] == " ": buf[fy][fx] = '.'; cbf[fy][fx] = cf((255,255,255))
                except: pass

    stars_list = [Star() for _ in range(100)]

    # 4. Main Loop
    last_dev_name = ""
    last_w, last_h = 0, 0

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
            # D. Resize Buffers
            if len(bands) != w:
                bands = np.zeros(w)
                peak_heights = np.zeros(w)

            # E. Reload Images if size changed
            if w != last_w or h != last_h:
                if state['img_bg_path']: buf_bg = process_image(state['img_bg_path'], w, h)
                if state['img_fg_path']: buf_fg = process_image(state['img_fg_path'], w, h)
                last_w, last_h = w, h

            # F. Process Audio Data
            # Resample 1024 bins -> W columns
            indices = np.linspace(0, 1023, w).astype(int)

            # Retrieve raw dB from thread
            raw_db = audio.raw_fft[indices]

            # Normalize (-60dB floor)
            norm = (raw_db - state['noise_floor']) / (0 - state['noise_floor'])
            norm = np.clip(norm, 0, 1.0) # Clip 0-1

            # Smooth
            s = state.get('smoothing', 0.15)
            bands = bands * s + norm * (1 - s)

            # Auto Gain
            agc = 1.0
            if state['auto_gain']:
                peak = np.max(bands)
                if peak > 0: agc = 1.0 / peak
                agc = min(agc, 5.0) # Cap gain

            # Final Height
            target_h = bands * h * agc * state['sens']

            # Physics
            for i in range(w):
                bh = target_h[i]
                if bh > h: bh = h
                if bh >= peak_heights[i]: peak_heights[i] = bh
                else: peak_heights[i] = max(0, peak_heights[i] - state['peak_gravity'])

            # G. Drawing
            ESC = "\x1b"
            output = [f"{ESC}[H"]

            # HUD
            vol_bar = "#" * int(min(20, audio.volume))
            hud_col = f"{ESC}[32m" if audio.volume > 0.1 else f"{ESC}[31m"
            output.append(f"{ESC}[40m{hud_col}DEVICE: {audio.connected_device:<30} | VOL: {vol_bar:<20} | STATE: {audio.status} {ESC}[0m{ESC}[K")

            cbf = [[f"{ESC}[49m" for _ in range(w)] for _ in range(h)]
            buf = [[" " for _ in range(w)] for _ in range(h)]

            def col(rgb): return f"{ESC}[38;2;{int(rgb[0])};{int(rgb[1])};{int(rgb[2])}m"
            def bg(rgb): return f"{ESC}[48;2;{int(rgb[0])};{int(rgb[1])};{int(rgb[2])}m"

            # BG Layer
            if state['img_bg_on'] and buf_bg:
                for y in range(h):
                    for x in range(w):
                        # Tiling check
                        if y < len(buf_bg) and x < len(buf_bg[0]):
                            res = buf_bg[y][x]
                            cbf[y][x] = bg(res[1]) if state['style'] != 0 else col(res[1])
                            buf[y][x] = " " if state['style'] != 0 else res[0]

            # Stars
            if state['stars']:
                for star in stars_list:
                    star.move(0.02 + (audio.volume * 0.01))
                    star.draw(buf, cbf, w, h, lambda c: col(c))

            # Bars
            theme_t = THEMES.get(state['theme_name'], THEMES['Vaporeon'])
            chars = state['bar_chars']

            for y in range(h):
                inv_y = h - 1 - y
                # Gradient
                row_rgb = get_gradient_color(inv_y, h, theme_t[0], theme_t[1])

                for x in range(w):
                    # Height check
                    bar_val = target_h[x]

                    if inv_y < bar_val:
                        final_rgb = row_rgb
                        # FG Texture
                        if state['img_fg_on'] and buf_fg:
                             if y < len(buf_fg) and x < len(buf_fg[0]):
                                 final_rgb = buf_fg[y][x][1]

                        # Style
                        if state['style'] == 1: # Block
                            cbf[y][x] = bg(final_rgb); buf[y][x] = " "
                        else: # Char
                            char_idx = int((inv_y/max(bar_val,1)) * (len(chars)-1))
                            cbf[y][x] = col(final_rgb); buf[y][x] = chars[char_idx]

                    # Peak
                    if state['peaks_on'] and inv_y == int(peak_heights[x]):
                        cbf[y][x] = f"{ESC}[47m"; buf[y][x] = " "

            # Text Overlay
            if state['text_on']:
                txt = state['text_str']
                banner = [txt]
                if HAS_FIGLET:
                    try: banner = pyfiglet.figlet_format(txt, font=FONT_MAP.get(state['text_font'], 'standard')).split('\n')
                    except: pass

                sy = int(state['text_pos_y'] * (h - len(banner)))
                for i, l in enumerate(banner):
                    for j, c in enumerate(l):
                        dx = int((w - len(l))/2) + j # Center
                        if 0 <= sy+i < h and 0 <= dx < w:
                            if c != " ":
                                cbf[sy+i][dx] = f"{ESC}[40m{ESC}[37m"; buf[sy+i][dx] = c

            # Flush
            for y in range(h):
                row = "".join([cbf[y][x] + buf[y][x] for x in range(w)])
                output.append(row + f"{ESC}[0m{ESC}[K")

            sys.stdout.write("\n".join(output))
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
             subprocess.Popen(f'start cmd /k "{py_exe}" "{cmd_path}" --engine', shell=True)
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
