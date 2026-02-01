CONFIG_FILE = "pyviz_settings.json"
PRESETS_FILE = "pyviz_presets.json"

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

CHAR_SETS = {
    "Blocks": "  ▂▃▄▅▆▇█",
    "Lines": "  --==##",
    "Dots": "  ....::::",
    "Digital": "  01",
    "ASCII": "  .,:;!|",
    "Shade": " ░▒▓█",
    "Thin": "  │┃",
    "Circles": "  ○●",
    "Math": "  +-x=",
    "Braille": " ⠀⠁⠂⠃⠄⠅⠆⠇⠈⠉⠊⠋⠌⠍⠎⠏",
    "Retro": "  _.-=*",
    "Sparkle": "  .*+@"
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
    "Sky": ([0, 100, 255], [255, 255, 255]),
    # New Themes
    "Cyberpunk 2077": ([255, 200, 0], [0, 255, 255]), # Yellow to Cyan
    "Matrix Rain": ([0, 20, 0], [0, 255, 50]), # Dark Green to Bright Green
    "Synthwave": ([80, 0, 120], [255, 100, 0]), # Purple to Orange
}

FONT_MAP = {"Tiny":"term", "Standard":"standard", "Big":"big", "Slant":"slant", "Block":"block", "Lean":"lean"}
