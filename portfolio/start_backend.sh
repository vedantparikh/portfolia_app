#!/bin/bash

echo "🚀 Starting FastAPI Backend..."
cd python/api
source .venv/bin/activate
echo "✅ Virtual environment activated"
echo "📡 Starting server on http://localhost:8080"
echo "📚 API docs available at http://localhost:8080/docs"
uvicorn main:app --reload --host 0.0.0.0 --port 8080
