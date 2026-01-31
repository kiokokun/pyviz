# PyViz - To-Do List
Here are the planned features and improvements for the Python Visualizer.

## Features to Add
- [ ] **Beat Detection**: Implement a more advanced beat detection algorithm to trigger specific visual effects on beat drops.
- [ ] **More Themes**: Add more color themes and visual styles.
- [ ] **Web Controller**: Create a web-based controller to adjust settings remotely (e.g., using Flask or FastAPI).
- [ ] **Networked Audio**: Allow visualizing audio from a remote source.
- [ ] **Recording**: Add ability to record the visualization to a video file.
- [ ] **Modular Effects**: Refactor the rendering engine to support pluggable effects modules.

## Improvements
- [ ] **Cross-Platform**: Further improve support for macOS and Linux (e.g., specific terminal handling).
- [ ] **Performance**: Optimize the rendering loop for higher FPS on lower-end hardware.
- [ ] **Configuration**: Add a GUI for creating and saving custom color themes.
- [ ] **Error Handling**: Improve error messages and recovery when audio devices are disconnected.

## Bugs
- [ ] Fix `start cmd` usage for non-Windows platforms (Partially addressed).
- [x] Fix "filename, directory name, or volume label syntax is incorrect" on Windows by correcting quote handling in TUI launcher.

## Completed
- [x] Refactor into modular architecture (`pyviz.py`, `config.py`, `audio_engine.py`, `renderer.py`, `tui.py`).
- [x] Add detailed logging to `pyviz.log` for better diagnostics.
- [x] Implement robust launcher scripts (`run_pyviz.bat`, `run_pyviz.sh`).
