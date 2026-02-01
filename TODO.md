# PyViz - To-Do List
Here are the planned features and improvements for the Python Visualizer.

## Features to Add
- [ ] **Web Controller**: Create a web-based controller to adjust settings remotely (e.g., using Flask or FastAPI).
- [ ] **Networked Audio**: Allow visualizing audio from a remote source.
- [ ] **Audio Recording**: Add ability to record the audio input to a WAV file.
- [ ] **Visual Recording**: Add ability to record the visualization to a video/GIF file.
- [ ] **WASAPI Loopback**: Support system audio capture on Windows (visualize what you hear).
- [ ] **Custom Color Palette Editor**: A TUI screen for creating and saving custom color themes.
- [ ] **Frequency Range Control**: Allow configuring Min/Max Hz frequencies for the visualization bars.
- [ ] **Preset Management UI**: Add Save/Load buttons to the TUI to manage configuration presets.
- [ ] **Screensaver Mode**: Run without window borders or taskbar icon.
- [ ] **Interactive Mode**: Mouse interaction to spawn particles or effects.

## Improvements
- [ ] **Advanced Beat Detection**: Implement FFT-based onset detection for more accurate beat syncing.
- [ ] **Cross-Platform**: Further improve support for macOS and Linux (e.g., specific terminal handling).
- [x] **Performance**: Optimize the rendering loop for higher FPS on lower-end hardware (Implemented RLE rendering and resolution scaling).
- [ ] **Configuration**: Add a GUI for creating and saving custom color themes.
- [x] **Error Handling**: Improve error messages and recovery when audio devices are disconnected.
- [x] **Settings**: Expose all configuration options (Gravity, Smoothing, Mirror, Text, AFK) in the TUI.

## Bugs
- [ ] Fix `start cmd` usage for non-Windows platforms (Partially addressed).
- [x] Fix "filename, directory name, or volume label syntax is incorrect" on Windows by correcting quote handling in TUI launcher.

## Completed
- [x] Refactor into modular architecture (`pyviz.py`, `config.py`, `audio_engine.py`, `renderer.py`, `tui.py`).
- [x] Add detailed logging to `pyviz.log` for better diagnostics.
- [x] Implement robust launcher scripts (`run_pyviz.bat`, `run_pyviz.sh`).
- [x] Optimize rendering performance for fullscreen usage.
- [x] Update TUI with Tabbed interface and full setting controls.
