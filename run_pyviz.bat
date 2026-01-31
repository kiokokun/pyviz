@echo off
title PyViz Launcher
echo Starting PyViz...

if exist ".venv" goto :run_venv

echo Virtual environment not found.
set /p install="Do you want to create one and install requirements? (y/n): "
if /i "%install%"=="y" goto :install_venv

echo Running with system python...
echo NOTE: Ensure dependencies are installed with 'pip install -r requirements.txt'
python pyviz.py
goto :check_error

:install_venv
echo Creating virtual environment...
python -m venv .venv
echo Activating and installing requirements...
call .venv\Scripts\activate
pip install -r requirements.txt
echo.
echo Setup complete. Starting PyViz...
python pyviz.py
goto :check_error

:run_venv
echo Activating virtual environment...
call .venv\Scripts\activate
python pyviz.py
goto :check_error

:check_error
if %errorlevel% neq 0 (
    echo.
    echo PyViz exited with an error. Check pyviz.log for details.
    pause
)
