#!/bin/bash

# Script to generate environment files for local and Docker development
# Creates .env (localhost) and .env.docker (Docker service names)

echo "🔧 Generating environment configuration files..."

# Function to create local .env file
create_local_env() {
    echo "💻 Creating .env for local development..."
    
    cat > .env << 'EOF'
# Local Development Environment Configuration

# Database Configuration
POSTGRES_HOST=localhost
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
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
LOG_LEVEL=info

# Security (CHANGE THESE IN PRODUCTION!)
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# External APIs
YAHOO_FINANCE_API_KEY=
ALPHA_VANTAGE_API_KEY=
EOF

    echo "✅ .env created successfully!"
}

# Function to create Docker .env.docker file
create_docker_env() {
    echo "🐳 Creating .env.docker for Docker development..."
    
    cat > .env.docker << 'EOF'
# Docker Environment Configuration
# Same as .env but with Docker-specific host values

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
LOG_LEVEL=info

# Security (CHANGE THESE IN PRODUCTION!)
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# External APIs
YAHOO_FINANCE_API_KEY=
ALPHA_VANTAGE_API_KEY=
EOF

    echo "✅ .env.docker created successfully!"
}

# Main execution
echo ""
echo "🚀 Environment Configuration Generator"
echo "====================================="
echo ""

# Check if files exist and ask for overwrite
if [ -f ".env" ]; then
    echo "⚠️  .env already exists!"
    read -p "Overwrite .env? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_local_env
    else
        echo "⏭️  Skipping .env creation"
    fi
else
    create_local_env
fi

echo ""

if [ -f ".env.docker" ]; then
    echo "⚠️  .env.docker already exists!"
    read -p "Overwrite .env.docker? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_docker_env
    else
        echo "⏭️  Skipping .env.docker creation"
    fi
else
    create_docker_env
fi

echo ""
echo "🎉 Environment files generated successfully!"
echo ""
echo "📋 Configuration Summary:"
echo "   - Local development: .env (localhost hosts)"
echo "   - Docker development: .env.docker (Docker service names)"
echo ""
echo "🔍 Key differences:"
echo "   - .env: POSTGRES_HOST=localhost, REDIS_HOST=localhost"
echo "   - .env.docker: POSTGRES_HOST=postgres, REDIS_HOST=redis"
echo ""
echo "🚀 Usage:"
echo "   - Local: uvicorn app.main:app --reload"
echo "   - Docker: docker-compose --env-file .env.docker up -d"
echo ""
echo "⚠️  Security Note: Change SECRET_KEY and JWT_SECRET_KEY in production!"
