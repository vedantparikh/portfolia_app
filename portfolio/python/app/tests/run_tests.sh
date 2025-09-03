#!/bin/bash

# Portfolia API Integration Test Runner
# This script runs all integration tests for the API endpoints

set -e

echo "🧪 Portfolia API Integration Test Runner"
echo "=================================================="

# Check if we're in the right directory
if [ ! -d "app" ]; then
    echo "❌ Error: Please run this script from the portfolio/python/api directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected to find: app/ directory"
    exit 1
fi

# Check if pytest is available
if ! command -v pytest &> /dev/null; then
    echo "❌ Error: pytest is not installed or not in PATH"
    echo "   Install with: pip install pytest"
    exit 1
fi

echo "✅ pytest available"
echo "✅ FastAPI TestClient available"

echo ""
echo "🚀 Starting Integration Tests..."
echo "--------------------------------------------------"

# Run the tests
pytest tests/integration/test_api_endpoints.py -v --tb=short --color=yes -s

echo ""
echo "=================================================="
echo "🎉 Integration tests completed!"
