import os
import random
from config import THEMES, FONT_MAP

try:
    from PIL import Image
    import numpy as np
except ImportError:
    Image = None
    np = None

try:
    import pyfiglet
    HAS_FIGLET = True
except ImportError:
    HAS_FIGLET = False

# Helpers
def process_image(path, w, h):
    if not path or not os.path.exists(path): return []
    if Image is None: return []
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

class Renderer:
    def __init__(self):
        self.bands = np.zeros(100) if np else []
        self.peak_heights = np.zeros(100) if np else []
        self.stars_list = [Star() for _ in range(100)]
        self.buf_bg = []
        self.buf_fg = []
        self.last_w = 0
        self.last_h = 0
        self.ESC = "\x1b"

    def render(self, state, audio, w, h):
        if not np:
            return "Numpy missing - Cannot render"

        # D. Resize Buffers
        if len(self.bands) != w:
            self.bands = np.zeros(w)
            self.peak_heights = np.zeros(w)

        # E. Reload Images if size changed
        if w != self.last_w or h != self.last_h:
            if state['img_bg_path']: self.buf_bg = process_image(state['img_bg_path'], w, h)
            if state['img_fg_path']: self.buf_fg = process_image(state['img_fg_path'], w, h)
            self.last_w, self.last_h = w, h

        # F. Process Audio Data
        # Resample 1024 bins -> W columns
        indices = np.linspace(0, 1023, w).astype(int)

        # Retrieve raw dB from thread
        # Handle empty/missing audio data
        if len(audio.raw_fft) == 1024:
            raw_db = audio.raw_fft[indices]
        else:
            raw_db = np.zeros(w) - 100 # Silence

        # Normalize (-60dB floor)
        norm = (raw_db - state['noise_floor']) / (0 - state['noise_floor'])
        norm = np.clip(norm, 0, 1.0) # Clip 0-1

        # Smooth
        s = state.get('smoothing', 0.15)
        self.bands = self.bands * s + norm * (1 - s)

        # Auto Gain
        agc = 1.0
        if state['auto_gain']:
            peak = np.max(self.bands)
            if peak > 0: agc = 1.0 / peak
            agc = min(agc, 5.0) # Cap gain

        # Final Height
        target_h = self.bands * h * agc * state['sens']

        # Physics
        for i in range(w):
            bh = target_h[i]
            if bh > h: bh = h
            if bh >= self.peak_heights[i]: self.peak_heights[i] = bh
            else: self.peak_heights[i] = max(0, self.peak_heights[i] - state['peak_gravity'])

        # G. Drawing
        output = [f"{self.ESC}[H"]

        # HUD
        vol_bar = "#" * int(min(20, audio.volume))
        hud_col = f"{self.ESC}[32m" if audio.volume > 0.1 else f"{self.ESC}[31m"
        output.append(f"{self.ESC}[40m{hud_col}DEVICE: {audio.connected_device:<30} | VOL: {vol_bar:<20} | STATE: {audio.status} {self.ESC}[0m{self.ESC}[K")

        cbf = [[f"{self.ESC}[49m" for _ in range(w)] for _ in range(h)]
        buf = [[" " for _ in range(w)] for _ in range(h)]

        def col(rgb): return f"{self.ESC}[38;2;{int(rgb[0])};{int(rgb[1])};{int(rgb[2])}m"
        def bg(rgb): return f"{self.ESC}[48;2;{int(rgb[0])};{int(rgb[1])};{int(rgb[2])}m"

        # BG Layer
        if state['img_bg_on'] and self.buf_bg:
            for y in range(h):
                for x in range(w):
                    # Tiling check
                    if y < len(self.buf_bg) and x < len(self.buf_bg[0]):
                        res = self.buf_bg[y][x]
                        cbf[y][x] = bg(res[1]) if state['style'] != 0 else col(res[1])
                        buf[y][x] = " " if state['style'] != 0 else res[0]

        # Stars
        if state['stars']:
            for star in self.stars_list:
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
                    if state['img_fg_on'] and self.buf_fg:
                            if y < len(self.buf_fg) and x < len(self.buf_fg[0]):
                                final_rgb = self.buf_fg[y][x][1]

                    # Style
                    if state['style'] == 1: # Block
                        cbf[y][x] = bg(final_rgb); buf[y][x] = " "
                    else: # Char
                        char_idx = int((inv_y/max(bar_val,1)) * (len(chars)-1))
                        cbf[y][x] = col(final_rgb); buf[y][x] = chars[char_idx]

                # Peak
                if state['peaks_on'] and inv_y == int(self.peak_heights[x]):
                    cbf[y][x] = f"{self.ESC}[47m"; buf[y][x] = " "

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
                            cbf[sy+i][dx] = f"{self.ESC}[40m{self.ESC}[37m"; buf[sy+i][dx] = c

        # Flush
        lines_out = []
        for y in range(h):
            row = "".join([cbf[y][x] + buf[y][x] for x in range(w)])
            lines_out.append(row + f"{self.ESC}[0m{self.ESC}[K")

        return "\n".join(output + lines_out)
