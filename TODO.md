# PyViz - Development Roadmap & To-Do List

This document tracks the planned features, improvements, and known issues for the PyViz Audio Visualizer.

## 🚀 Planned Features

### Core Audio & Visuals
- [ ] **Frequency Range Control**: Allow configuring Min/Max Hz frequencies for the visualization bars (e.g., zoom in on bass).
- [ ] **Advanced Beat Detection**: Implement onset detection (spectral flux) for more accurate beat syncing.
- [ ] **Visual Recording**: Add ability to record the visualization to a video file (using FFmpeg pipe).
- [ ] **Interactive Mode**: Mouse interaction in the terminal to spawn particles or effects.

### User Interface
- [ ] **Custom Color Palette Editor**: A TUI screen for creating and saving custom color themes.
- [ ] **Preset Management UI**: Add Save/Load buttons to the TUI to manage multiple configuration files (e.g. `techno.json`, `chill.json`).
- [ ] **Web Controller**: Create a web-based controller (Flask/FastAPI) to adjust settings remotely from a phone.

### Platform Support
- [ ] **WASAPI Loopback (Windows)**: Support capturing system audio ("What U Hear") natively.
- [ ] **MacOS Audio Permissions**: Better handling/instructions for microphone access on macOS.

## 🛠 Improvements & Refactoring

### Code Quality
- [ ] **Unit Tests**: Add comprehensive unit tests for `renderer.py` logic (mocking `rich`).
- [ ] **Type Safety**: Enforce stricter type checking with `mypy` across the codebase.
- [ ] **Dependency Management**: Consider migrating to `poetry` or `uv` for better dependency locking.

### Performance
- [ ] **Cython / Numba**: Optimize the FFT and physics calculations using compiled extensions for extreme performance.
- [ ] **Async TUI**: Fully decouple TUI I/O from state updates using `asyncio` (currently uses atomic file writes).

## ✅ Completed Milestones

### Phase 5: Deep Polish & Bug Fixes (Recent)
- [x] **Performance**: Optimized config reload (1.0s cooldown) and removed redundant renderer logic.
- [x] **Stability**: Fixed race conditions, audio device index shifting, and potential crashes on invalid input.
- [x] **UX**: Added "Reset to Defaults" button, input sanitization, tooltips, and dynamic star field density.
- [x] **Code Quality**: Refactored monolithic scripts into modules (`audio_engine`, `renderer`, `tui`).

### Phase 1-4: Foundation & Features
- [x] **Modular Architecture**: Split code into `pyviz.py`, `config.py`, `audio_engine.py`, `renderer.py`, `tui.py`.
- [x] **Modern UI**: Replaced Tkinter with `textual` (TUI) and ANSI rendering with `rich`.
- [x] **Features**: Added GIF support, native file picker, UI Themes, Character Presets.
- [x] **Robustness**: Fixed 40+ bugs related to crashes, resource leaks (zombies), and Windows compatibility.
