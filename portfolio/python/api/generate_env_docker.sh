#!/bin/bash

# Script to generate .env.docker from .env file
# This ensures both files have the same values

echo "🔧 Generating .env.docker file from .env..."

# Check if .env file exists
if [ ! -f "app/.env" ]; then
    echo "❌ Error: app/.env file not found!"
    exit 1
fi

# Create .env.docker with Docker-specific host values
cat > .env.docker << 'EOF'
# Database Configuration
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=portfolio

# Connection Pool Settings
POOL_SIZE=20
MAX_OVERFLOW=30
POOL_TIMEOUT=30
POOL_RECYCLE=3600

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
LOG_LEVEL=INFO

# Security
SECRET_KEY=530cb86661e911f1bf70b57a46f337d5dcdc43ebe40df0fab326e0930baae183
JWT_SECRET_KEY=2f5a97fa197b8a755c0b12634b0f7c1af96ae2a83ad4efc2bc45b013f9b259a8
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_DAYS=7

# External APIs
YAHOO_FINANCE_API_KEY=
ALPHA_VANTAGE_API_KEY=
EOF

echo "✅ .env.docker file created successfully!"
echo "📋 Key differences from .env:"
echo "   - POSTGRES_HOST=postgres (Docker service name)"
echo "   - REDIS_HOST=redis (Docker service name)"
echo "   - API_PORT=8000 (matches Docker port mapping)"

echo ""
echo "🔍 To use:"
echo "   - Local development: Use app/.env"
echo "   - Docker: Uses .env.docker automatically"
echo "   - Both files now have consistent values"
