import os
import random
import time
from typing import List, Tuple, Any, Callable, Optional, Union
from config import THEMES, FONT_MAP, CHAR_SETS
from effects.glitch import GlitchEffect
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich.panel import Panel
from rich.console import Console

try:
    from PIL import Image, ImageSequence # type: ignore
    import numpy as np
except ImportError:
    Image = None
    np = None

try:
    import pyfiglet # type: ignore
    HAS_FIGLET = True
except ImportError:
    HAS_FIGLET = False

# Global Constants
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Helpers
_IMG_CACHE = {}
def process_image(path: str, w: int, h: int) -> Union[List[List[Tuple[int, int, int]]], List[List[List[Tuple[int, int, int]]]]]:
    """
    Returns either a single buffer (static image) or a list of buffers (animated GIF).
    Buffer = List of Rows, Row = List of RGB Tuples (No Chars yet).
    """
    key = (path, w, h)
    if key in _IMG_CACHE: return _IMG_CACHE[key]

    if not path or not os.path.exists(path): return []
    if Image is None: return []

    try:
        im = Image.open(path)

        frames = []
        is_animated = getattr(im, "is_animated", False)
        # Proper Loop
        frames = []
        frame_iter = ImageSequence.Iterator(im) if is_animated else [im]
        for frame in frame_iter:
            f_img = frame.copy().resize((w, h)).convert("RGB")
            px = f_img.load()
            frame_buf = []
            for y in range(h):
                row = []
                for x in range(w):
                    r,g,b = px[x,y]
                    row.append((r,g,b))
                frame_buf.append(row)
            frames.append(frame_buf)

        result = frames if is_animated else frames[0]

        # Simple cache eviction
        if len(_IMG_CACHE) > 5: _IMG_CACHE.clear() # Lower limit for GIFs

        # Memory Safety: Cap frames
        if is_animated and len(result) > 100:
            result = result[:100] # Limit to first 100 frames to prevent OOM

        _IMG_CACHE[key] = result
        return result
    except Exception: return []

# Cached gradient calculation
_GRADIENT_CACHE = {}
def get_gradient_color(y: int, h: int, start_rgb: Union[List[int], Tuple[int, int, int]], end_rgb: Union[List[int], Tuple[int, int, int]]) -> Tuple[int, int, int]:
    # Ensure hashable keys (convert lists to tuples)
    s_key = tuple(start_rgb)
    e_key = tuple(end_rgb)
    key = (y, h, s_key, e_key)

    if key in _GRADIENT_CACHE: return _GRADIENT_CACHE[key]

    ratio = y / max(h, 1)
    r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
    g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
    b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
    res = (r, g, b)

    if len(_GRADIENT_CACHE) > 2000: _GRADIENT_CACHE.clear()
    _GRADIENT_CACHE[key] = res
    return res

def col_style(fg: Tuple[int,int,int], bg: Tuple[int,int,int]=BLACK) -> Tuple[Tuple[int,int,int], Tuple[int,int,int]]:
    return (fg, bg)

class Star:
    """
    Represents a single star in the background starfield effect.
    """
    def __init__(self) -> None:
        self.reset(True)

    def reset(self, rz: bool = False) -> None:
        self.x = (random.random() - 0.5) * 2
        self.y = (random.random() - 0.5) * 2
        self.z = random.random() * 2.0 if rz else 2.0

    def move(self, spd: float) -> None:
        self.z -= spd
        if self.z <= 0.05:
            self.reset()

    def draw(self, buf: List[List[str]], cbf: List[List[Tuple[Tuple[int,int,int], Tuple[int,int,int]]]], w: int, h: int, col_style_fn: Callable) -> None:
        if self.z <= 0:
            return

        fx = int((self.x / self.z) * w * 0.5 + w / 2)
        fy = int((self.y / self.z) * h * 0.5 + h / 2)

        if 0 <= fx < w and 0 <= fy < h:
            try:
                if buf[fy][fx] == " ":
                    buf[fy][fx] = '.'
                    cbf[fy][fx] = col_style_fn((255, 255, 255))
            except Exception:
                pass

class Renderer:
    """
    Main visualization renderer using Rich.
    Handles audio data processing, buffer generation, and drawing.
    """
    def __init__(self) -> None:
        self.bands: Any = np.zeros(100) if np else []
        self.peak_heights: Any = np.zeros(100) if np else []
        self.stars_list: List[Star] = [Star() for _ in range(100)]

        self.effects: List[Any] = [GlitchEffect()]

        self.buf_bg: Any = [] # List or List[List]
        self.buf_fg: Any = []
        self.last_w: int = 0
        self.last_h: int = 0
        self.frame_idx = 0
        self.console = Console()

        # Max resolution to prevent lag on huge terminals
        self.MAX_BARS = 160

    def generate_frame(self, state: dict, audio: Any, console_w: int, h: int) -> Text:
        if not np:
            return Text("Numpy missing - Cannot render", style="bold red")

        if h <= 0 or console_w <= 0:
            return Text("")

        # Logic for downsampling / limiting bars
        # If console width is huge, we calculate fewer bars and stretch them.
        w = console_w
        scale_x = 1

        if w > self.MAX_BARS:
            # e.g. w=200, MAX=160.
            # We want to render self.MAX_BARS bars.
            # But Rich Text needs full width.
            # We can run logic at MAX_BARS resolution, then expand during Text build.
            # Or simplified: if w > MAX_BARS, we set logical w = w // 2 (Double Width Mode)
            # This is cleaner than arbitrary scaling.
            scale_x = 2
            w = console_w // 2

        # D. Resize Buffers (Logical Width)
        if len(self.bands) != w:
            self.bands = np.zeros(w)
            self.peak_heights = np.zeros(w)

        # E. Reload Images (Logical Width)
        if w != self.last_w or h != self.last_h:
            if state['img_bg_path']: self.buf_bg = process_image(state['img_bg_path'], w, h)
            if state['img_fg_path']: self.buf_fg = process_image(state['img_fg_path'], w, h)
            self.last_w, self.last_h = w, h

        # Cycle frames (approx 30fps base)
        self.frame_idx += 1

        # F. Process Audio Data
        indices = np.linspace(0, 1023, w).astype(int)

        if len(audio.raw_fft) == 1024:
            raw_db = audio.raw_fft[indices]
        else:
            raw_db = np.zeros(w) - 100

        floor = state.get('noise_floor', -60.0)
        if floor == 0: floor = -0.001 # Prevent DivZero

        norm = (raw_db - floor) / (0 - floor)
        norm = np.clip(norm, 0, 1.0)

        s = state.get('smoothing', 0.15)
        self.bands = self.bands * s + norm * (1 - s)

        agc = 1.0
        if state['auto_gain']:
            peak = np.max(self.bands)
            if peak > 0: agc = 1.0 / peak
            agc = min(agc, 5.0)

        try:
            target_h = self.bands * h * agc * float(state.get('sens', 1.0))
        except (ValueError, TypeError):
            target_h = self.bands * h * agc # Fallback

        # Physics
        peak_g = float(state.get('peak_gravity', 0.15))
        for i in range(w):
            bh = target_h[i]
            if bh > h: bh = h
            if bh >= self.peak_heights[i]: self.peak_heights[i] = bh
            else: self.peak_heights[i] = max(0, self.peak_heights[i] - peak_g)

        # G. Drawing
        # Init buffers
        # We reuse list creation logic (python lists are fast enough for <10k items)
        # Type: List[List[str]]
        buf = [[" " for _ in range(w)] for _ in range(h)]
        # Type: List[List[Tuple[FG_RGB, BG_RGB]]]
        cbf = [[(WHITE, BLACK) for _ in range(w)] for _ in range(h)]

        # BG Layer
        if state['img_bg_on'] and self.buf_bg:
            # Handle Animation
            cur_bg = self.buf_bg

            # Heuristic: [Frames][Rows][RGB] vs [Rows][RGB]
            is_animated = False
            if len(cur_bg) > 0 and isinstance(cur_bg[0], list):
                if len(cur_bg[0]) > 0 and isinstance(cur_bg[0][0], list):
                     is_animated = True

            if is_animated:
                idx = (self.frame_idx // 2) % len(cur_bg)
                cur_bg = cur_bg[idx]

            # Prepare Char Set
            img_style = state.get('img_style', 2)
            img_chars = CHAR_SETS.get(state.get('img_char_set', 'Blocks'), CHAR_SETS['Blocks'])

            for y in range(h):
                for x in range(w):
                    if y < len(cur_bg):
                        row = cur_bg[y]
                        if x < len(row):
                            rgb = row[x]

                            if img_style == 1: # Block (Background color)
                                cbf[y][x] = col_style(WHITE, rgb)
                                buf[y][x] = " "
                            else: # Char (Foreground color)
                                # Calculate Luminance
                                lum = (0.299*rgb[0] + 0.587*rgb[1] + 0.114*rgb[2]) / 255.0
                                char_idx = int(lum * (len(img_chars) - 1))
                                char_idx = max(0, min(char_idx, len(img_chars)-1))

                                cbf[y][x] = col_style(rgb, BLACK)
                                buf[y][x] = img_chars[char_idx]

        # Stars
        if state['stars']:
            # Adjust star count based on resolution
            target_stars = min(300, max(50, (w * h) // 100))
            if len(self.stars_list) < target_stars:
                self.stars_list.extend([Star() for _ in range(target_stars - len(self.stars_list))])
            elif len(self.stars_list) > target_stars:
                self.stars_list = self.stars_list[:target_stars]

            for star in self.stars_list:
                star.move(0.02 + (audio.volume * 0.01))
                if star.z > 0:
                    star.draw(buf, cbf, w, h, col_style)

        # Bars
        theme_t = THEMES.get(state['theme_name'], THEMES['Vaporeon'])
        chars = state.get('bar_chars', "")
        if not chars: chars = "  ▂▃▄▅▆▇█" # Fallback to default if empty

        style_mode = state['style']
        peaks_on = state['peaks_on']
        mirror = state['mirror']

        # Pre-calc gradients for performance
        row_colors = [get_gradient_color(h - 1 - y, h, theme_t[0], theme_t[1]) for y in range(h)]

        for x in range(w):
            bar_val = target_h[x]
            peak_val = int(self.peak_heights[x])

            # Optimization: only iterate Y where bars exist
            # Max Y for this bar
            max_y_bar = int(bar_val)
            if max_y_bar >= h: max_y_bar = h - 1

            # Fill Bar
            # Because coordinates are y=0 (top) to h (bottom), we draw from bottom up.
            # inv_y = 0 at bottom.
            # Range of y to draw: h-1 down to h-1 - max_y_bar

            start_y = h - 1
            end_y = max(0, h - 1 - max_y_bar)

            for y in range(end_y, start_y + 1):
                inv_y = h - 1 - y
                final_rgb = row_colors[y]

                # FG Texture (if enabled, slow path)
                if state['img_fg_on'] and self.buf_fg:
                     # Handle Animation
                     cur_fg = self.buf_fg

                     is_anim_fg = False
                     if len(cur_fg) > 0 and isinstance(cur_fg[0], list):
                        if len(cur_fg[0]) > 0 and isinstance(cur_fg[0][0], list):
                             is_anim_fg = True

                     if is_anim_fg:
                         idx = (self.frame_idx // 2) % len(cur_fg)
                         cur_fg = cur_fg[idx]

                     if y < len(cur_fg) and x < len(cur_fg[y]):
                         final_rgb = cur_fg[y][x]

                if style_mode == 1: # Block
                    cbf[y][x] = (WHITE, final_rgb) # BG color
                    buf[y][x] = " "
                else: # Char
                    char_idx = int((inv_y/max(bar_val,1)) * (len(chars)-1))
                    if char_idx >= len(chars): char_idx = len(chars)-1
                    cbf[y][x] = (final_rgb, BLACK)
                    buf[y][x] = chars[char_idx]

            # Draw Peak
            if peaks_on:
                peak_y = h - 1 - peak_val
                if 0 <= peak_y < h:
                     cbf[peak_y][x] = (WHITE, (200,200,200))
                     buf[peak_y][x] = " "

        # Mirror (Post-Process)
        if mirror:
             # Simple approach: Mirror left half to right half
             mid = w // 2
             is_odd = (w % 2 != 0)

             def apply_mirror(row_data):
                 left_part = row_data[:mid]
                 right_part = left_part[::-1]
                 if is_odd:
                     return left_part + [row_data[mid]] + right_part
                 return left_part + right_part

             for y in range(h):
                 buf[y] = apply_mirror(buf[y])
                 cbf[y] = apply_mirror(cbf[y])

        # Text Overlay
        if state['text_on']:
            txt = state['text_str']
            banner = [txt]
            if HAS_FIGLET:
                try:
                    font = FONT_MAP.get(state['text_font'], 'standard')
                    banner = pyfiglet.figlet_format(txt, font=font).split('\n')
                except Exception as e:
                    # Font not found fallback
                    try: banner = pyfiglet.figlet_format(txt, font='standard').split('\n')
                    except: pass

            sy = int(state['text_pos_y'] * (h - len(banner)))

            # Scrolling Logic
            x_offset = 0
            if state.get('text_scroll', False):
                # Scroll speed: 1 char per 2 frames approx
                scroll_speed = 4
                total_w = max(len(l) for l in banner) if banner else 0
                cycle_len = w + total_w
                if cycle_len > 0:
                    raw_offset = (self.frame_idx // 2) % cycle_len
                    # Move from right to left: starts at w, goes to -total_w
                    x_offset = w - raw_offset
                # Override centering
                start_x = x_offset
            else:
                # Center text
                start_x = (w - (len(banner[0]) if banner else 0)) // 2

            for i, l in enumerate(banner):
                line_y = sy + i
                if not (0 <= line_y < h): continue

                row_start = start_x if state.get('text_scroll', False) else (w - len(l)) // 2

                for j, c in enumerate(l):
                    dx = row_start + j

                    # Text Glitch Logic
                    if state.get('text_glitch', False):
                        if random.random() < 0.05: # 5% chance per char
                            dx += random.choice([-1, 1]) # Jitter X
                        if random.random() < 0.02: # 2% chance scramble
                            c = random.choice("!@#$%^&*?")

                    if 0 <= dx < w:
                        if c != " ":
                            cbf[line_y][dx] = (WHITE, BLACK)
                            buf[line_y][dx] = c

        # Effects
        for effect in self.effects:
            effect.update(state, audio)
            try: effect.draw(buf, cbf, w, h, col_style)
            except: pass

        # Build Rich Text (Optimized)
        # Rich Text.append is slow.
        # We can construct lines with shared styles.
        screen_text = Text()

        for y in range(h):
            line = Text()

            # Optimization: Run Length Encoding for styles
            current_style = None
            current_text = []

            for x in range(w):
                char = buf[y][x]
                fg, bg = cbf[y][x]

                # Simple style key
                # Cache style strings?
                # Using rgb values directly
                style_key = (fg, bg)

                if style_key != current_style:
                    # Flush previous
                    if current_text:
                        s_fg, s_bg = current_style
                        style_str = f"rgb({s_fg[0]},{s_fg[1]},{s_fg[2]})"
                        if s_bg != BLACK:
                            style_str += f" on rgb({s_bg[0]},{s_bg[1]},{s_bg[2]})"

                        chunk = "".join(current_text)
                        if scale_x > 1:
                            # Expand horizontal pixels
                            chunk = "".join([c * scale_x for c in chunk])

                        line.append(chunk, style=style_str)

                    current_style = style_key
                    current_text = [char]
                else:
                    current_text.append(char)

            # Flush last chunk
            if current_text:
                s_fg, s_bg = current_style
                style_str = f"rgb({s_fg[0]},{s_fg[1]},{s_fg[2]})"
                if s_bg != BLACK:
                    style_str += f" on rgb({s_bg[0]},{s_bg[1]},{s_bg[2]})"

                chunk = "".join(current_text)
                if scale_x > 1:
                    chunk = "".join([c * scale_x for c in chunk])
                line.append(chunk, style=style_str)

            screen_text.append(line)
            screen_text.append("\n")

        return screen_text

    def render_loop(self, state_provider: Callable, audio_provider: Any) -> None:
        """
        Main loop using Rich Live
        """
        # Note: Live refresh rate is just for terminal update capping.
        # We control actual frame generation speed manually.
        with Live(console=self.console, refresh_per_second=60, screen=True) as live:
            while True:
                t0 = time.time()
                try:
                    # Update State
                    state = state_provider()
                    fps = state.get('fps', 30)
                    if fps <= 0: fps = 30

                    # Dimensions
                    w = self.console.width
                    h = self.console.height - 2

                    # Generate Frame
                    frame_text = self.generate_frame(state, audio_provider, w, h)

                    # HUD
                    vol_bar = "#" * int(min(20, audio_provider.volume))
                    hud_text = Text(f"DEVICE: {audio_provider.connected_device:<30} | VOL: {vol_bar:<20} | STATE: {audio_provider.status} | FPS: {fps}", style="bold white on black")

                    # Layout
                    layout = Layout()
                    layout.split(
                        Layout(hud_text, size=1),
                        Layout(frame_text)
                    )

                    live.update(layout)

                    # Frame Pacing
                    dt = time.time() - t0
                    wait = (1.0 / fps) - dt
                    if wait > 0:
                        time.sleep(wait)

                except Exception as e:
                    # Log error but don't crash
                    error_text = Text(f"RENDER ERROR: {e}", style="bold red")
                    live.update(Panel(error_text, title="Error"))
                    time.sleep(1)
