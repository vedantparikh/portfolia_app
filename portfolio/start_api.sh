#!/bin/bash

# Portfolia API Startup Script
# This script will start the API with automatic database initialization

echo "🚀 Starting Portfolia API..."

# Change to the API directory
cd python/api

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies if requirements.txt is newer than .venv
if [ requirements.txt -nt .venv/pyvenv.cfg ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
fi

# Set environment variables
export DEBUG=true
export HOST=0.0.0.0
export PORT=8000

# Start the API with automatic database initialization
echo "🌐 Starting API with automatic database initialization..."
python start_api.py
