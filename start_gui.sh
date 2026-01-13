#!/bin/bash
# Startup script for UV Navigation Inspection GUI (Unix/Linux/Mac)

echo "Starting UV Navigation Inspection..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists and activate it
if [ -f ".venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Warning: No virtual environment found, using system Python"
fi

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "Error: Python is not installed or not in PATH"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Run the application
echo "Launching application..."
$PYTHON_CMD run_app.py

# Check exit status
if [ $? -ne 0 ]; then
    echo ""
    echo "Application exited with error"
    read -p "Press Enter to continue..."
fi
