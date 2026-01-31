@echo off
title PyViz Launcher
echo Starting PyViz...

if not exist ".venv" (
    echo Virtual environment not found.
    set /p install="Do you want to create one and install requirements? (y/n): "
    if /i "%install%"=="y" (
        echo Creating virtual environment...
        python -m venv .venv
        echo Activating and installing requirements...
        call .venv\Scripts\activate
        pip install -r requirements.txt
        echo.
        echo Setup complete. Starting PyViz...
        python pyviz.py
    ) else (
        echo Running with system python...
        echo NOTE: Ensure dependencies are installed with 'pip install -r requirements.txt'
        python pyviz.py
    )
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
