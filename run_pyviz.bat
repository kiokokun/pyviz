@echo off
title PyViz Launcher
echo Starting PyViz...

if not exist ".venv" (
    echo Virtual environment not found. Please install requirements first.
    echo Running with system python...
    python pyviz.py
) else (
    echo Activating virtual environment...
    call .venv\Scripts\activate
    python pyviz.py
)

if %errorlevel% neq 0 (
    echo.
    echo PyViz exited with an error. Check pyviz.log for details.
    pause
)
