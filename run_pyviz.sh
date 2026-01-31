#!/bin/bash
echo "Starting PyViz..."

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

python3 pyviz.py

if [ $? -ne 0 ]; then
    echo
    echo "PyViz exited with an error. Check pyviz.log for details."
    read -p "Press Enter to exit..."
fi
