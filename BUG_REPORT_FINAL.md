# Final Code Audit (30 Items)

## Code Quality & Style (PEP 8)
1.  **Bare Except (renderer.py:35)**: `except: return []` in `process_image`. Should be `except Exception`.
2.  **Bare Except (renderer.py:100)**: `except: pass` in `Star.draw`.
3.  **Bare Except (renderer.py:302)**: `except: pass` in FIGlet loading.
4.  **Bare Except (renderer.py:305)**: `except: pass` in fallback FIGlet loading.
5.  **Bare Except (audio_engine.py:64)**: `except: pass` in device index parsing.
6.  **Bare Except (audio_engine.py:66)**: `except: pass` in index fallback.
7.  **Bare Except (audio_engine.py:104)**: `except: pass` in device query retry.
8.  **Bare Except (audio_engine.py:125)**: `except: pass` in blocksize query.
9.  **Bare Except (tui.py:186)**: `except: self.state = DEFAULT_STATE.copy()` in `load_state`.
10. **Bare Except (tui.py:192)**: `except: pass` in `save_state`.
11. **Bare Except (tui.py:220)**: `except: pass` in device refresh.
12. **Bare Except (tui.py:285)**: `except: pass` in `afk_timeout` parsing.
13. **Bare Except (tui.py:291)**: `except: ...` in `sens` parsing.
14. **Bare Except (tui.py:297)**: `except: pass` in `gravity` parsing.
15. **Bare Except (tui.py:300)**: `except: pass` in `smoothing` parsing.
16. **Bare Except (tui.py:303)**: `except: pass` in `noise_floor` parsing.
17. **Bare Except (pyviz.py:48)**: `except: pass` in `get_state`.
18. **Unused Import**: `math` in `pyviz.py` is imported but not used.
19. **Unused Import**: `random` in `pyviz.py` is imported but not used.

## Maintainability & Documentation
20. **Missing Docstring**: `Star` class has no docstring explaining its purpose.
21. **Missing Docstring**: `Renderer` class has no docstring.
22. **Missing Docstring**: `AudioPump` class has no docstring.
23. **Missing Docstring**: `PyVizController` class has no docstring.
24. **Manual CLI Parsing**: `pyviz.py` uses `sys.argv` checks instead of `argparse`, making it hard to add help flags.
25. **Hardcoded Log Config**: `setup_logger` uses a hardcoded filename `pyviz.log` instead of a configurable one.

## Robustness & Logic
26. **Magic Number**: `audio_engine.py` uses `time.sleep(1)` and `time.sleep(2)` hardcoded delays.
27. **Magic Number**: `tui.py` uses `30` as default AFK timeout in code string, duplicating config default.
28. **Magic Number**: `renderer.py` uses `MAX_BARS = 160`. Should be configurable.
29. **Mutable Default Argument**: `col_style` in `renderer.py` uses `bg=BLACK`. While tuples are immutable, it's a pattern to watch.
30. **Redundant CSS**: `tui.py` defines a large CSS string inside the class. It should be extracted to a file or constant for readability.
