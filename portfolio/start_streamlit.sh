#!/bin/bash

echo "📊 Starting Streamlit Dashboard..."
cd python/streamlit
source venv/bin/activate
echo "✅ Virtual environment activated"
echo "🌐 Starting dashboard on http://localhost:8501"
streamlit run main.py --server.port 8501 --server.address 0.0.0.0
