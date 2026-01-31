## 11. TUI Input Validation
**File:** `tui.py`
**Description:** If a user types non-numeric text (e.g., "abc") into numeric inputs like "Sensitivity", the underlying state is not updated (caught by `try...except`), but the UI input field retains the invalid "abc" string, misleading the user.
**Severity:** Low (UX).

## 12. Windows Launch Spam
**File:** `tui.py`
**Description:** On Windows, the `start` command detaches the process immediately. The TUI cannot track the PID of the actual engine window. Consequently, users can click "Launch Engine" multiple times, spawning multiple conflicting visualizer windows.
**Severity:** Medium (UX/Resource).

## 13. Crash on Small Terminals
**File:** `renderer.py`
**Description:** If the terminal height is very small (< 3 lines), the calculation `h = self.console.height - 2` results in 0 or negative values. This can cause layout errors in `rich` or logic errors in buffer generation.
**Severity:** Medium (Crash).

## 14. Floating Point Drift in UI
**File:** `tui.py`
**Description:** Repeatedly clicking "+" on float controls (like Sensitivity) adds `0.1`. Due to floating point arithmetic, this eventually results in ugly values like `1.30000000004`, which are displayed raw in the Input field.
**Severity:** Low (Cosmetic).

## 15. Config Type Safety
**File:** `renderer.py`
**Description:** The renderer assumes `state['sens']` etc. are numbers. If a user manually edits `pyviz_settings.json` and inserts a string, the renderer loop will crash with a `TypeError` during math operations.
**Severity:** Medium (Crash).

## 16. Log Permission Failure
**File:** `logger.py`
**Description:** `setup_logger` sets up a file handler. If the script is running in a read-only directory (common in some deployment scenarios), this raises `PermissionError` and crashes the app immediately on startup.
**Severity:** High (Startup Crash).

## 17. Missing Engine Dependency Checks
**File:** `pyviz.py`
**Description:** The dependency check only verifies `textual` for the controller. If `pyfiglet`, `Pillow`, or `numpy` (required for engine) are missing, `run_engine` will crash mid-execution or produce errors, but `pyviz.py` allows it to start.
**Severity:** Medium (Crash).

## 18. Infinite Audio Loop on Empty Device List
**File:** `audio_engine.py`
**Description:** If `sd.query_devices()` returns an empty list (no audio devices), `set_device` sets `device_index = None`. The `run` loop continuously checks `if device_index is None: continue`, spinning at 100% CPU (or fast sleep loop) without ever notifying the user.
**Severity:** Medium (Resource Usage).

## 19. Hardcoded Audio Blocksize
**File:** `audio_engine.py`
**Description:** The audio stream uses a hardcoded `blocksize=2048`. Some audio interfaces (e.g., rigid ASIO setups or Bluetooth drivers) may require specific power-of-two blocksizes or fail.
**Severity:** Low (Compatibility).

## 20. Effect State Leak
**File:** `renderer.py`
**Description:** Effects are initialized once in `__init__`. If an effect accumulates state (like `GlitchEffect.duration`) and the renderer persists across re-launches (not the case here, but good practice), it could be buggy. More importantly, if `state` changes drastically, effects aren't reset.
**Severity:** Low (Logic).
