## 41. Race Condition in Config Reload
**File:** `pyviz.py`
**Description:** `get_state` reads the config file every frame (30 FPS) by checking `getmtime`. If the TUI is writing (even atomically), the filesystem check adds overhead. More importantly, checking `getmtime` this frequently is a performance bottleneck (Syscall spam).
**Severity:** Low (Performance).

## 42. Redundant Cleanup
**File:** `pyviz.py`
**Description:** `cleanup()` is registered with `atexit` AND called in `finally`. This causes double execution of shutdown logic. While currently safe, it's bad practice.
**Severity:** Low (Code Style).

## 43. Audio Thread Shutdown Lag
**File:** `pyviz.py`
**Description:** `audio.join(timeout=1.0)` blocks the main thread for up to 1 second on exit. If the audio thread is stuck (e.g. in `sd.read`), the application will hang for 1s then exit, leaving the thread daemonized.
**Severity:** Low (UX).

## 44. Dead Code in Renderer (Artifact)
**File:** `renderer.py`
**Description:** In `process_image`, lines 56-62 contain a "first attempt" loop that appends to a local `frames` list, which is then immediately discarded and overwritten by the "Proper Loop". This is waste of CPU cycles during image loading.
**Severity:** Medium (Code Quality/Performance).

## 45. Inefficient Text Rendering
**File:** `renderer.py`
**Description:** The `Text` object in `generate_frame` is rebuilt from scratch every frame using `Text.append`. While RLE was added, creating a new `Text` object and parsing styles 30 times a second for the whole screen is expensive for `rich`.
**Severity:** Medium (Performance).

## 46. Missing Input Sanitization (TUI)
**File:** `tui.py`
**Description:** Input fields like "Bar Characters" accept control characters, newlines, or excessively long strings. Rendering a 1000-char string in `renderer.py` will break the layout or cause massive lag.
**Severity:** Medium (DoS/Stability).

## 47. Unbounded Log Growth
**File:** `logger.py`
**Description:** `RotatingFileHandler` is configured, but if the app crashes repeatedly on startup (e.g. config error), it might spam logs. (Actually checks out ok, 5MB limit). But `error.log` in `pyviz.py` (line 82) is NOT rotated.
**Severity:** Low (Resource).

## 48. Config Type Validation Gap
**File:** `config.py`
**Description:** `DEFAULT_STATE` defines types, but `tui.py` loading logic blindly trusts JSON types. If `pyviz_settings.json` has `{"sens": "invalid"}`, `tui.py` might crash trying to set Input value or renderer might crash (fixed in renderer, but TUI vulnerability remains).
**Severity:** Low (Stability).

## 49. Missing Tooltips
**File:** `tui.py`
**Description:** The advanced settings (Rise Speed, Glitch, etc.) are opaque to the user. Textual supports tooltips.
**Severity:** Low (UX).

## 50. Audio Device Index Shift
**File:** `audio_engine.py`
**Description:** If a USB device is unplugged, indices shift. The logic tries to match name, but if it fails, it defaults to `None`. It doesn't strictly *retry* auto-discovery often enough or notify the user of "Device Lost".
**Severity:** Medium (UX).

## 51. Hardcoded Frame Rate
**File:** `pyviz.py` / `config.py`
**Description:** `fps` is in `DEFAULT_STATE` but `renderer.render_loop` hardcodes `time.sleep(0.001)` and `refresh_per_second=30`. It ignores the config.
**Severity:** Low (Feature Gap).

## 52. Renderer State Mutability
**File:** `renderer.py`
**Description:** `state` is passed to `generate_frame`. The renderer modifies `self.peak_heights`. If `state` logic were to modify shared lists (not currently, but in future), race conditions with TUI could occur if they shared memory (they don't, separate process).
**Severity:** Low (Architectural).

## 53. Uncaught KeyboardInterrupt in Audio
**File:** `audio_engine.py`
**Description:** The audio thread catches `Exception`, but `KeyboardInterrupt` is not an `Exception`. If user Ctrl+C's, audio thread might print traceback instead of clean exit.
**Severity:** Low (Cosmetic).

## 54. Missing "Reset to Defaults"
**File:** `tui.py`
**Description:** If user messes up config, there is no button to restore `DEFAULT_STATE`. They have to delete the JSON file manually.
**Severity:** Medium (UX).

## 55. Image Path Path Traversal
**File:** `tui.py`
**Description:** `FileOpenScreen` allows navigation. User can navigate to sensitive system dirs. (Not a huge risk for a local app, but "deep audit" notes it).
**Severity:** Low (Security).

## 56. PyFiglet Font Crash
**File:** `renderer.py`
**Description:** If `pyfiglet` is missing, `HAS_FIGLET` is False. Logic skips it. But if it's present and `font` is invalid, the fallback logic inside `generate_frame` swallows the exception but might flicker.
**Severity:** Low (Cosmetic).

## 57. Character Preset Overwrite
**File:** `tui.py`
**Description:** Selecting a Character Preset overwrites `bar_chars`. If user had a custom set, it's lost immediately without undo.
**Severity:** Low (UX).

## 58. Missing "Glitch" Toggle in Audio
**File:** `audio_engine.py`
**Description:** Audio engine calculates beats for glitch, but doesn't know if glitch is enabled. It does work, but optimization could skip beat detection if glitch is off (minor).
**Severity:** Low (Optimization).

## 59. Mirror Mode Center Column
**File:** `renderer.py`
**Description:** The fix for odd-width mirror mode copies the center column. If width is 1, `left_part` is empty, `center` is index 0. Works. But `cbf` (color buffer) mirroring logic duplicates the code of `buf`. DRY violation.
**Severity:** Low (Code Quality).

## 60. Star Field Density
**File:** `renderer.py`
**Description:** `Star` count is hardcoded to 100 in `__init__`. On large screens (4k terminal), this looks sparse. On small, crowded. Should scale with `w*h`.
**Severity:** Low (Visual).
