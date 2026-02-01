# Brainstorming: Improving User Friendliness

## 1. Quick Wins (Low Effort, High Value)
- **Startup Audio Test:** Add a small VU meter in the TUI (Controller) itself, so you can see if the microphone is picking up sound *before* you launch the engine.
- **Help Button:** A "?" button that opens a modal explaining what "Gravity", "Smoothing", "Bass Threshold", etc. actually do, with examples.
- **Dependency Checker:** When launching, check if `ffmpeg` or other system tools are installed and guide the user if missing.
- **Theme Previews:** Show a small color swatch next to the theme dropdown.

## 2. Configuration & Presets
- **Preset Manager (Highly Requested):**
    - "Save As..." button to save current settings as `my_techno_setup.json`.
    - "Load Preset" dropdown to switch between saved configs instantly.
    - Default presets: "Chill", "Party", "Minimal", "Debug".
- **Custom Color Editor:**
    - A TUI screen with RGB sliders to create your own theme, instead of just picking from the list.
    - Save custom themes to `config.py` (or a separate `themes.json`).

## 3. Remote Control & Interaction
- **Web Controller:**
    - A simple web page (Flask/FastAPI) running on `localhost:5000`.
    - Allows you to change colors, sensitivity, and presets from your phone (same Wi-Fi).
    - Useful if the visualizer is running on a TV/Monitor across the room.
- **Keyboard Shortcuts (Engine):**
    - While the engine is running, press keys to toggle effects:
        - `G`: Toggle Gravity
        - `M`: Toggle Mirror
        - `S`: Toggle Stars
        - `R`: Reload Config (Force)
        - `1-9`: Switch Presets

## 4. Platform & Audio
- **"What U Hear" (System Audio):**
    - On Windows, automatically try to find the "Stereo Mix" or WASAPI Loopback device if no microphone is selected.
    - On Linux, guide users to use PulseAudio Monitor sources.

## 5. Visual Polish
- **Album Art:** If playing music from Spotify/System, try to fetch current album art and display it as the background image automatically. (Complex but cool).
- **Screensaver Mode:** Run without window borders or taskbar icon (Fullscreen exclusive).

## Which one should we tackle first?
My recommendation: **Preset Manager** + **Keyboard Shortcuts**. These give the most "power user" feel immediately.
