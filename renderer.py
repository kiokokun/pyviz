import os
import random
import time
from typing import List, Tuple, Any, Callable, Optional, Union
from config import THEMES, FONT_MAP
from effects.glitch import GlitchEffect
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich.panel import Panel
from rich.console import Console

try:
    from PIL import Image # type: ignore
    import numpy as np
except ImportError:
    Image = None
    np = None

try:
    import pyfiglet # type: ignore
    HAS_FIGLET = True
except ImportError:
    HAS_FIGLET = False

# Helpers (moved/adapted from original renderer)
def process_image(path: str, w: int, h: int) -> List[List[Tuple[str, Tuple[int, int, int]]]]:
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

def get_gradient_color(y: int, h: int, start_rgb: Tuple[int, int, int], end_rgb: Tuple[int, int, int]) -> Tuple[int, int, int]:
    ratio = y / max(h, 1)
    r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
    g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
    b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
    return (r, g, b)

class Star:
    def __init__(self) -> None: self.reset(True)
    def reset(self, rz: bool=False) -> None: self.x=(random.random()-0.5)*2; self.y=(random.random()-0.5)*2; self.z=random.random()*2.0 if rz else 2.0
    def move(self, spd: float) -> None:
        self.z -= spd
        if self.z <= 0.05: self.reset()
    # Updated draw signature to match Rich Renderer needs (modifying buffers directly)
    def draw(self, buf: List[List[str]], cbf: List[List[Tuple[Tuple[int,int,int], Tuple[int,int,int]]]], w: int, h: int, col_style: Callable) -> None:
        if self.z <= 0: return
        fx = int((self.x/self.z)*w*0.5+w/2); fy = int((self.y/self.z)*h*0.5+h/2)
        if 0<=fx<w and 0<=fy<h:
            try:
                if buf[fy][fx] == " ":
                    buf[fy][fx] = '.'
                    cbf[fy][fx] = col_style((255,255,255))
            except: pass

class Renderer:
    def __init__(self) -> None:
        self.bands: Any = np.zeros(100) if np else []
        self.peak_heights: Any = np.zeros(100) if np else []
        self.stars_list: List[Star] = [Star() for _ in range(100)]

        self.effects: List[Any] = [GlitchEffect()] # Initialize effects

        self.buf_bg: List[List[Tuple[str, Tuple[int, int, int]]]] = []
        self.buf_fg: List[List[Tuple[str, Tuple[int, int, int]]]] = []
        self.last_w: int = 0
        self.last_h: int = 0
        self.console = Console()

    def generate_frame(self, state: dict, audio: Any, w: int, h: int) -> Text:
        if not np:
            return Text("Numpy missing - Cannot render", style="bold red")

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
        # Init buffers
        # Type: List[List[str]]
        buf = [[" " for _ in range(w)] for _ in range(h)]
        # Type: List[List[Tuple[FG_RGB, BG_RGB]]]
        cbf = [[((255,255,255), (0,0,0)) for _ in range(w)] for _ in range(h)] # Default

        def col_style(fg: Tuple[int,int,int], bg: Tuple[int,int,int]=(0,0,0)) -> Tuple[Tuple[int,int,int], Tuple[int,int,int]]:
            return (fg, bg)

        # BG Layer
        if state['img_bg_on'] and self.buf_bg:
            for y in range(h):
                for x in range(w):
                    # Tiling check
                    if y < len(self.buf_bg) and x < len(self.buf_bg[0]):
                        res = self.buf_bg[y][x]
                        # res is (char, rgb)
                        if state['style'] != 0:
                            cbf[y][x] = col_style(res[1])
                            buf[y][x] = res[0]
                        else:
                            cbf[y][x] = col_style((255,255,255), res[1])
                            buf[y][x] = " "

        # Stars
        if state['stars']:
            for star in self.stars_list:
                star.move(0.02 + (audio.volume * 0.01))
                if star.z > 0:
                    star.draw(buf, cbf, w, h, col_style)

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
                        cbf[y][x] = col_style((255,255,255), final_rgb) # BG color
                        buf[y][x] = " "
                    else: # Char
                        char_idx = int((inv_y/max(bar_val,1)) * (len(chars)-1))
                        cbf[y][x] = col_style(final_rgb)
                        buf[y][x] = chars[char_idx]

                # Peak
                if state['peaks_on'] and inv_y == int(self.peak_heights[x]):
                    cbf[y][x] = col_style((255,255,255), (200,200,200)) # White FG, Light Gray BG
                    buf[y][x] = " "

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
                            cbf[sy+i][dx] = col_style((255,255,255), (0,0,0))
                            buf[sy+i][dx] = c

        # Effects
        for effect in self.effects:
            effect.update(state, audio)

            def dummy_col(rgb: Tuple[int,int,int]) -> Tuple[Tuple[int,int,int], Tuple[int,int,int]]:
                return (rgb, (0,0,0))

            try:
                effect.draw(buf, cbf, w, h, dummy_col)
            except: pass

        # Build Rich Text
        screen_text = Text()
        for y in range(h):
            line = Text()
            for x in range(w):
                char = buf[y][x]
                fg, bg = cbf[y][x]
                style = f"rgb({fg[0]},{fg[1]},{fg[2]})"
                if bg != (0,0,0):
                    style += f" on rgb({bg[0]},{bg[1]},{bg[2]})"
                line.append(char, style=style)
            screen_text.append(line)
            screen_text.append("\n")

        return screen_text

    def render_loop(self, state_provider: Callable, audio_provider: Any) -> None:
        """
        Main loop using Rich Live
        """
        with Live(console=self.console, refresh_per_second=30, screen=True) as live:
            while True:
                # Update State
                state = state_provider()
                # Update Audio
                # (Done in thread)

                # Dimensions
                w = self.console.width
                h = self.console.height - 2 # Reserve space for HUD?

                # Generate Frame
                frame_text = self.generate_frame(state, audio_provider, w, h)

                # HUD
                vol_bar = "#" * int(min(20, audio_provider.volume))
                hud_text = Text(f"DEVICE: {audio_provider.connected_device:<30} | VOL: {vol_bar:<20} | STATE: {audio_provider.status}", style="bold white on black")

                # Layout
                layout = Layout()
                layout.split(
                    Layout(hud_text, size=1),
                    Layout(frame_text)
                )

                live.update(layout)

                # FPS limiter
                time.sleep(0.001)
