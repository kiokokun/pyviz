## 31. Tkinter/Textual Event Loop Conflict
**File:** `tui.py`
**Description:** Calling `tkinter.filedialog` (which uses the main thread) from within Textual's async event loop can cause freezes or crashes on some platforms (macOS/Linux) because Tkinter expects to own the main loop. On Windows it usually works but blocks the UI entirely.
**Severity:** Medium (Stability).

## 32. GIF Memory Exhaustion
**File:** `renderer.py`
**Description:** `process_image` loads *every* frame of a GIF into uncompressed RGB buffers. A long, high-resolution GIF can easily consume gigabytes of RAM, causing an OOM crash.
**Severity:** High (Resource).

## 33. Windows Zombie Processes
**File:** `tui.py`
**Description:** On Windows, `subprocess.Popen(..., shell=True)` creates a `cmd.exe` process which spawns `python.exe`. Calling `terminate()` only kills `cmd.exe`, leaving the visualizer window (`python.exe`) running as a zombie/orphan.
**Severity:** Medium (UX).

## 34. Ambiguous Audio Device Selection
**File:** `audio_engine.py`
**Description:** The fallback search logic selects the *first* device containing the name string. If multiple devices have the same name (e.g., "Virtual Cable 1", "Virtual Cable 2" matched by "Virtual Cable"), the user cannot reliably select the second one via this fallback.
**Severity:** Low (Feature).

## 35. Unimplemented Color Mode
**File:** `renderer.py`
**Description:** `config.py` defines `color_mode` (Theme/Solid/Gradient) and keys like `solid_color`, but `renderer.py` completely ignores these, always using the `THEMES` lookup. The TUI doesn't even expose `color_mode` switching properly (except implied via Theme select).
**Severity:** Low (Missing Feature).

## 36. Unimplemented Rise Speed
**File:** `renderer.py`
**Description:** The `rise_speed` setting exists in Config and TUI, but is unused in the physics calculation. The smoothing logic uses `state['smoothing']`, but nothing uses `rise_speed` to control attack time vs decay time.
**Severity:** Low (Logic).

## 37. Disconnected Bass Threshold
**File:** `audio_engine.py`
**Description:** Beat detection occurs inside `AudioPump`, but this class has no access to the dynamic `state` dictionary. It uses a hardcoded `1.4` multiplier. Changing `Bass Threshold` in the TUI has absolutely no effect on beat detection sensitivity.
**Severity:** Medium (Logic/Bug).

## 38. Disconnected Glitch Intensity
**File:** `effects/glitch.py`
**Description:** The `GlitchEffect` uses hardcoded probabilities (`0.3`, `0.05`). The `glitch` intensity slider in the TUI updates `state['glitch']`, but the effect class does not use this value to scale its probabilities.
**Severity:** Low (Logic).

## 39. UI Theme Crash Risk
**File:** `tui.py`
**Description:** If `pyviz_settings.json` contains a `ui_theme` that was removed or renamed in `UI_THEMES`, the `set_ui_theme` method might raise a `KeyError` or fail to apply a theme, leaving the UI in an inconsistent state.
**Severity:** Low (Stability).

## 40. Image Char Set Key Error
**File:** `renderer.py`
**Description:** If `state['img_char_set']` contains a value not in `CHAR_SETS` (e.g. from manual config editing), `CHAR_SETS.get(...)` correctly falls back, but if `img_style` is set to Char mode, verify fallback logic is robust.
**Severity:** Low (Robustness).
