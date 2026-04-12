#!/bin/bash

# FAISS Backend Setup and Run Script

echo "=== FAISS Backend Setup ==="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

echo "=== Setup Complete ==="
echo ""
echo "To run the server:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run the server: python main.py"
echo ""
echo "Or use this script with 'run' argument: ./setup.sh run"

# If run argument is provided, start the server
if [ "$1" = "run" ]; then
    echo "Starting FAISS backend server..."
    python main.py
fi