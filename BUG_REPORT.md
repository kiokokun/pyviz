# Bug Report

## 1. Division by Zero in Renderer
**File:** `renderer.py`
**Description:** The normalization logic uses `(0 - state['noise_floor'])` as a divisor. If `noise_floor` is set to `0`, this causes a `ZeroDivisionError`, crashing the renderer subprocess.
**Severity:** Critical (Crash).

## 2. Configuration File Corruption Risk
**File:** `tui.py`
**Description:** The `save_state` method writes directly to `CONFIG_FILE`. If the application crashes or power is lost during write, the file becomes empty or corrupt, causing startup failure on next run.
**Severity:** High (Data Loss).

## 3. Performance Degradation on Resize (Disk Thrashing)
**File:** `renderer.py`
**Description:** The `process_image` function is called every time `w` or `h` changes (e.g. while resizing the window). It re-opens and reads the image file from disk each time. This causes excessive disk I/O and CPU usage during resize operations.
**Severity:** Medium (Performance).

## 4. Fragile Audio Device Selection
**File:** `audio_engine.py`
**Description:** The `set_device` method parses the device index from the name string (e.g. `[1] Microphone`). If the system audio devices change (unplug/plug) and indices shift, the stored index might point to a different device, while the user expects the named device.
**Severity:** Medium (Unexpected Behavior).

## 5. Missing Configuration Controls
**File:** `tui.py`
**Description:** Several settings defined in `DEFAULT_STATE` (`noise_floor`, `auto_gain`, `rise_speed`, `bass_thresh`) are completely missing from the TUI, preventing the user from adjusting them without manually editing the JSON file.
**Severity:** Medium (Feature Gap).
