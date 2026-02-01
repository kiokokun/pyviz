# Brainstorming: Improving User Friendliness & Feature Expansion

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
- **Cloud Sync:** Import/Export presets via Base64 strings or Gist URLs to share with friends.
- **Randomizer:** A button to shuffle all color and physics settings for chaotic fun.
- **Scheduled Profiles:** Auto-switch to a "Dark/Minimal" preset after 10 PM.

## 3. Remote Control & Interaction
- **Web Controller:**
    - A simple web page (Flask/FastAPI) running on `localhost:5000`.
    - Allows you to change colors, sensitivity, and presets from your phone (same Wi-Fi).
    - Useful if the visualizer is running on a TV/Monitor across the room.
- **Keyboard Shortcuts (Engine):**
    - `G`: Toggle Gravity
    - `M`: Toggle Mirror
    - `S`: Toggle Stars
    - `R`: Reload Config (Force)
    - `1-9`: Switch Presets
- **Twitch Chat Integration:** Allow chat commands (e.g., `!color red`, `!glitch`) to control the visualizer.
- **QR Code Generator:** Display a QR code in the TUI to instantly open the Web Controller on a phone.

## 4. Platform & Audio
- **"What U Hear" (System Audio):**
    - Windows: Auto-detect "Stereo Mix" or WASAPI Loopback.
    - Linux: Guide users to PulseAudio Monitor.
- **Stereo Separation:** Render Left channel on the left side, Right channel on the right side (Dual Visualizers).
- **Audio Device Hot-Swap:** Detect if a USB microphone is plugged in and switch to it automatically without restart.
- **Noise Gate:** A configurable cutoff to ignore background hum/fan noise.
- **BPM Counter:** Detect and display the estimated Beats Per Minute.
- **Input Gain Wizard:** A 5-second calibration mode that listens to the loudest part of a song and sets `Sensitivity` automatically.

## 5. New Visual Modes
- **Spectrogram (Waterfall):** A history view scrolling up, showing frequency intensity over time (classic Winamp style).
- **Oscilloscope:** A raw waveform line graph instead of frequency bars.
- **Circular Spectrum:** Bars radiating from the center (Kaleidoscope/Circle).
- **Particle System:** Physics-based particles that explode from the center on bass drops.
- **Matrix Digital Rain:** Falling characters (Matrix style) that glow brighter/faster with volume.
- **Lissajous Figures:** X-Y plotting of stereo channels (requires Stereo support).
- **ASCII Video Player:** Play a video file as the background instead of a static image.
- **"Breathing" Background:** Dim/Brighten the background image opacity based on overall volume.
- **Pong Mode:** Two paddles controlled by left/right volume channels playing a game.
- **Game of Life:** A Conway's Game of Life simulation seeded by audio data.

## 6. Smart Integrations
- **Discord Rich Presence:** Show "Visualizing: [Song Name] - [Preset]" in Discord status.
- **Philips Hue / LIFX:** Sync smart room lights to the visualizer's beat detection.
- **OBS WebSocket:** Trigger scene changes in OBS Studio on a "Beat Drop".
- **Spotify Integration:** Fetch the "Now Playing" track info and album art to display in the overlay.
- **MQTT Output:** Publish beat events to a local broker for Home Assistant automation.

## 7. TUI & UX Improvements
- **Wizard Mode:** A first-run guided tour to set up audio and explain controls.
- **Mouse Support:** Allow clicking on the visualizer to spawn effects or change modes.
- **CPU Monitor:** A small overlay showing CPU/RAM usage of the renderer.
- **Color Blind Modes:** Built-in themes optimized for Protanopia/Deuteranopia.
- **Log Viewer Tab:** A tab in the TUI to see the raw `pyviz.log` output in real-time (like `tail -f`).
- **"Boss Mode":** Press a key to instantly overlay a fake spreadsheet screenshot.
- **Resizable Panels:** Allow the user to drag the divider between the bars and the settings in the TUI.

## 8. Just For Fun / Experimental
- **Emoji Mode:** Use emojis (🔥, 🎵, 💯) instead of block characters for bars.
- **Text-to-Speech Announcer:** Robot voice announces "BASS DROP" when threshold is met.
- **"Bad Apple" Demo:** A hardcoded mode that plays the Bad Apple shadow art.
- **Binary Mode:** Render everything using only `0` and `1`.
- **DVD Logo:** A text banner bouncing around the screen, changing color on wall hits.
- **Lyrics Display:** Load a `.lrc` file and display synced lyrics.
- **Screensaver Mode:** Run fullscreen exclusive without borders/taskbar.
- **Mirror Dimension:** A "Kaleidoscope" effect that mirrors the screen 4-way (Quad Mirror).

## Which one should we tackle first?
My recommendation: **Preset Manager** + **Keyboard Shortcuts**. These give the most "power user" feel immediately.
