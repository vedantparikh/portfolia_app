#!/bin/bash

# Environment setup script for Portfolia application
# This script sets up both application and Docker environment files

set -e

echo "🚀 Setting up Portfolia environment configuration..."

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "📁 Script directory: $SCRIPT_DIR"
echo "📁 Project root: $PROJECT_ROOT"

# Function to create .env file from example
create_env_file() {
    local example_file="$1"
    local env_file="$2"
    local description="$3"
    
    if [ ! -f "$example_file" ]; then
        echo "❌ Example file not found: $example_file"
        return 1
    fi
    
    if [ -f "$env_file" ]; then
        echo "⚠️  $description already exists. Do you want to overwrite it? (y/N): "
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            echo "✅ Keeping existing $description"
            return 0
        fi
    fi
    
    echo "📝 Creating $description from $example_file..."
    cp "$example_file" "$env_file"
    chmod 600 "$env_file"
    echo "✅ $description created with proper permissions"
}

# Create application .env file
echo ""
echo "🔧 Setting up application environment..."
create_env_file "$SCRIPT_DIR/config.env.example" "$SCRIPT_DIR/.env" "application .env file"

# Create Docker .env file
echo ""
echo "🐳 Setting up Docker environment..."
create_env_file "$(dirname "$PROJECT_ROOT")/docker.env.example" "$PROJECT_ROOT/.env" "Docker .env file"

# Generate secure keys if they don't exist
echo ""
echo "🔐 Generating secure keys..."

# Function to generate secure key
generate_secure_key() {
    openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || echo "your-secret-key-change-in-production"
}

# Update application .env with secure keys
if [ -f "$SCRIPT_DIR/.env" ]; then
    echo "🔑 Updating application .env with secure keys..."
    
    # Generate and replace SECRET_KEY
    SECRET_KEY=$(generate_secure_key)
    sed -i.bak "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" "$SCRIPT_DIR/.env"
    
    # Generate and replace JWT_SECRET_KEY
    JWT_SECRET_KEY=$(generate_secure_key)
    sed -i.bak "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$JWT_SECRET_KEY/" "$SCRIPT_DIR/.env"
    
    # Clean up backup files
    rm -f "$SCRIPT_DIR/.env.bak"
    
    echo "✅ Secure keys generated and updated"
fi

# Update Docker .env with secure keys
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo "🔑 Updating Docker .env with secure keys..."
    
    # Generate and replace SECRET_KEY
    SECRET_KEY=$(generate_secure_key)
    sed -i.bak "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" "$PROJECT_ROOT/.env"
    
    # Generate and replace JWT_SECRET_KEY
    JWT_SECRET_KEY=$(generate_secure_key)
    sed -i.bak "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$JWT_SECRET_KEY/" "$PROJECT_ROOT/.env"
    
    # Clean up backup files
    rm -f "$PROJECT_ROOT/.env.bak"
    
    echo "✅ Secure keys generated and updated"
fi

echo ""
echo "🎉 Environment setup completed successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Review and customize the generated .env files"
echo "2. For production, change all default passwords and keys"
echo "3. Update database credentials if needed"
echo "4. Set external API keys if you have them"
echo ""
echo "🔧 To start the application:"
echo "   - With Docker: docker-compose up -d"
echo "   - Without Docker: python setup_database.sh && python main.py"
echo ""
echo "📚 Configuration files created:"
echo "   - Application: $SCRIPT_DIR/.env"
echo "   - Docker: $PROJECT_ROOT/.env"
