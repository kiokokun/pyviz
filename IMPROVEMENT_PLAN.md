# Detailed Improvement Plan for PyViz

This document outlines a step-by-step plan to refactor, enhance, and modernize the visualizer.

## Phase 1: Modularization & Cleanup (The Foundation)
**Goal:** Break the monolithic `pyviz.py` into maintainable modules to support future features.

### Step 1.1: Configuration Extraction
- [x] Create `config.py`.
- [x] Move `DEFAULT_STATE` dictionary to `config.py`.
- [x] Move `THEMES` dictionary to `config.py`.
- [x] Move `FONT_MAP` and file path constants (`CONFIG_FILE`, `PRESETS_FILE`) to `config.py`.
- [x] Update `pyviz.py` to import these from `config`.

### Step 1.2: Audio Engine Extraction
- [x] Create `audio_engine.py`.
- [x] Move `AudioPump` class to `audio_engine.py`.
- [x] Add necessary imports (`threading`, `numpy`, `sounddevice`) to `audio_engine.py`.
- [x] Remove `AudioPump` from `pyviz.py` and import it from `audio_engine`.
- [x] Verify audio input still works.

### Step 1.3: Renderer Refactoring
- [x] Create `renderer.py`.
- [x] Create a `Renderer` class to encapsulate the drawing logic (Screen size, buffers, helper functions like `get_gradient_color`).
- [x] Move `Star` class and `process_image` helper to `renderer.py`.
- [x] Move the main rendering loop logic (Stars, Bars, Text) into a `render_frame()` method in the `Renderer` class.
- [x] Update `pyviz.py` to use the `Renderer` class.

### Step 1.4: Effects System
- [x] Create an `effects/` directory with an `__init__.py`.
- [x] Create `effects/base.py` defining an abstract `BaseEffect` class with `update(state, audio_data)` and `draw(buffer)` methods.
- [ ] Refactor the current "Stars" logic into `effects/stars.py`.
- [ ] Refactor the current "Spectrum Bars" logic into `effects/spectrum.py`.
- [ ] Update the `Renderer` to hold a list of active effects and iterate through them.

## Phase 2: Visual Enhancements
**Goal:** Add more visual variety and responsiveness.

### Step 2.1: Advanced Beat Detection
- [x] In `audio_engine.py`, implement a "Spectral Flux" algorithm or simple energy thresholding.
- [x] Calculate the average energy of the lower frequencies (0-100Hz).
- [x] Add a `is_beat` boolean to the `AudioPump` shared state, set to `True` for 1 frame when a beat is detected.
- [x] Expose `beat_confidence` (0.0 to 1.0) for softer reactions.

### Step 2.2: Reactive Effects
- [x] Create `effects/pulse.py`: An effect that flashes the background color when `is_beat` is true.
- [x] Create `effects/glitch.py`: An effect that randomly shifts characters or colors in the buffer when a strong bass hit occurs.
- [x] Add configuration options to `config.py` to enable/disable these new effects.

### Step 2.3: New Themes
- [x] Add "Cyberpunk 2077" (Yellow/Black/Cyan) to `THEMES`.
- [x] Add "Matrix Rain" (Black background, multiple shades of Green) to `THEMES`.
- [x] Add "Synthwave" (Purple/Pink/Orange) to `THEMES`.

## Phase 3: Web Controller
**Goal:** Allow remote control via a browser.

### Step 3.1: API Backend
- [ ] Create `web_server.py`.
- [ ] Install `fastapi` and `uvicorn` (add to requirements).
- [ ] Create a `/state` GET endpoint that returns the current configuration.
- [ ] Create a `/state` POST endpoint that updates the configuration in `deck_settings.json`.
- [ ] Ensure the main engine loop reloads config frequently (it already does, but optimize if needed).

### Step 3.2: Web Frontend
- [ ] Create `templates/index.html`.
- [ ] Build a simple UI with sliders for Sensitivity, Noise Floor, and a dropdown for Themes.
- [ ] Add JavaScript to fetch current state on load and POST changes when controls are moved.
- [ ] Add a "Connect" status indicator.

### Step 3.3: Integration
- [ ] Add a `--web` argument to `pyviz.py`.
- [ ] If `--web` is present, start the `uvicorn` server in a separate thread or process.

## Phase 4: Network & Recording
**Goal:** Professional features.

### Step 4.1: Networked Audio
- [ ] Create `audio_sender.py` (runs on a different machine).
- [ ] Use `sounddevice` to record raw audio.
- [ ] Use `socket` (UDP) to broadcast audio chunks or pre-calculated FFT data.
- [ ] Add a "Network" mode to `AudioPump` in `audio_engine.py` to listen on a specific port.

### Step 4.2: Video Recording
- [ ] Add a `--record <filename.mp4>` argument.
- [ ] In `Renderer`, instead of (or in addition to) printing to stdout, write the frame string to a pipe.
- [ ] Use `subprocess` to spawn `ffmpeg` and feed the frames to it to generate a video.
