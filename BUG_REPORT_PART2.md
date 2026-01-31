## 6. Zombie Processes on Controller Exit
**File:** `tui.py` / `pyviz.py`
**Description:** When the TUI controller is closed, the separate "PyViz Engine" process (launched via `subprocess.Popen`) is not automatically terminated. It continues running in the background until manually killed, confusing users.
**Severity:** Medium (User Experience).

## 7. Font Loading Vulnerability
**File:** `renderer.py`
**Description:** The renderer attempts to load FIGlet fonts specified in the configuration. If the font name is invalid or the font file is missing, `pyfiglet.figlet_format` raises an exception. While there is a generic `try...except`, it simply hides the text, confusing the user. It should fallback to a standard font.
**Severity:** Low (Feature Robustness).

## 8. Missing Preset Management Logic
**File:** `tui.py`
**Description:** `config.py` defines `PRESETS_FILE`, implying a feature to save/load settings profiles. However, `tui.py` has no UI or logic to interact with this file, leaving the feature completely unimplemented.
**Severity:** Medium (Missing Feature).

## 9. Unclean Engine Shutdown (Resource Leak)
**File:** `pyviz.py`
**Description:** If the renderer loop crashes or is interrupted by `KeyboardInterrupt`, the `audio` thread is not explicitly stopped or joined. This can leave the audio device open or the thread hanging, requiring a force kill.
**Severity:** Medium (Stability).

## 10. Dependency Check Failure
**File:** `pyviz.py`
**Description:** The script imports `tui` immediately in `run_controller`. If `textual` is not installed, the script crashes with a raw `ModuleNotFoundError`. A friendly check and error message is needed for better UX.
**Severity:** Low (User Experience).
