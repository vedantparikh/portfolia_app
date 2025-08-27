#!/bin/bash

# Database setup script for Portfolia application
# This script initializes the database and runs migrations

set -e

echo "🚀 Setting up Portfolia database..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Running environment setup first..."
    ./setup_environment.sh
    echo ""
fi

# Load environment variables
if [ -f ".env" ]; then
    echo "📝 Loading environment variables..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if PostgreSQL is running
echo "🔍 Checking PostgreSQL connection..."
if ! pg_isready -h localhost -p 5432 -U username > /dev/null 2>&1; then
    echo "❌ PostgreSQL is not running. Please start the database first:"
    echo "   docker-compose up -d db"
    exit 1
fi

echo "✅ PostgreSQL is running"

# Check if Redis is running
echo "🔍 Checking Redis connection..."
if ! redis-cli -h localhost -p 6379 ping > /dev/null 2>&1; then
    echo "⚠️  Redis is not running. Some features may not work properly."
    echo "   You can start Redis with: docker-compose up -d redis"
fi

# Initialize database tables
echo "🗄️  Initializing database tables..."
python database/init_db.py

# Initialize Alembic
echo "🔄 Setting up Alembic migrations..."
if [ ! -d "alembic/versions" ]; then
    echo "📝 Creating initial migration..."
    alembic init alembic
    echo "📝 Generating initial migration..."
    alembic revision --autogenerate -m "Initial database schema"
fi

# Run migrations
echo "🚀 Running database migrations..."
alembic upgrade head

echo "✅ Database setup completed successfully!"
echo ""
echo "📊 You can now:"
echo "   - Start the API: uvicorn main:app --reload --host 0.0.0.0 --port 8080"
echo "   - Check database health: curl http://localhost:8080/health"
echo "   - View detailed health: curl http://localhost:8080/health/detailed"
echo ""
echo "🔧 Database management commands:"
echo "   - Create new migration: alembic revision --autogenerate -m 'Description'"
echo "   - Apply migrations: alembic upgrade head"
echo "   - Rollback migration: alembic downgrade -1"
echo "   - View migration history: alembic history"
