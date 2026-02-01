# PyViz Feature Roadmap

This document lists planned features and ideas for future development.

## High Priority
- [ ] **Web Controller**: A web interface (FastAPI/Flask) to control the visualizer from a phone/browser.
    - Should include a QR code generator in the TUI to easily link devices.
- [ ] **Video Player Support**: Extend the current image/GIF renderer to support video files (`.mp4`, `.avi`) using `opencv-python`.

## Visual Modes
- [ ] **Waterfall / Spectrogram**: A scrolling history of frequency analysis, useful for analyzing tracks.
- [ ] **Oscilloscope**: A real-time line drawing of the audio waveform.
- [ ] **Lissajous Figures**: X-Y phase plotting of stereo channels.
- [ ] **Game of Life**: Conway's Game of Life simulation where audio triggers cell births/deaths.

## Integrations
- [ ] **Spotify Integration**: Display currently playing track info (Artist/Title) using Spotify API.
    - Could control color palette based on Album Art.

## Enhancements
- [ ] **Smooth Transition**: Fade between themes instead of hard switching.
- [ ] **Preset Cycling**: Auto-load random presets on a timer.
