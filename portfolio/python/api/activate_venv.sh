#!/bin/bash

# Simple script to activate the virtual environment
echo "🐍 Activating Python virtual environment..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv .venv
fi

# Activate the virtual environment
source .venv/bin/activate

echo "✅ Virtual environment activated!"
echo "📦 Current Python: $(which python)"
echo "📦 Python version: $(python --version)"
echo "📦 Pip version: $(pip --version)"

echo ""
echo "💡 To deactivate, run: deactivate"
echo "💡 To install dependencies: pip install -r requirements.txt"
echo "💡 To run tests: ./run_tests.sh all"
