#!/bin/bash
echo "Starting PyViz..."

if [ -d ".venv" ]; then
    source .venv/bin/activate
    python3 pyviz.py
else
    echo "Virtual environment not found."
    read -p "Create one and install requirements? (y/n): " choice
    if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
        echo "Creating virtual environment..."
        python3 -m venv .venv
        source .venv/bin/activate
        echo "Installing requirements..."
        pip install -r requirements.txt
        echo "Starting PyViz..."
        python3 pyviz.py
    else
        echo "Running with system python..."
        python3 pyviz.py
    fi
fi

if [ $? -ne 0 ]; then
    echo
    echo "PyViz exited with an error. Check pyviz.log for details."
    read -p "Press Enter to exit..."
fi
