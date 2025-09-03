# 🌍 Environment Configuration Guide

## Overview

This document explains how to configure the Portfolia application using environment variables. The application supports both local development and Docker deployment configurations.

## 🚀 Quick Setup

### 1. Automatic Setup (Recommended)

```bash
# Run the comprehensive setup script
./setup_environment.sh
```

This script will:
- Create application `.env` file from `config.env.example`
- Create Docker `.env` file from `docker.env.example`
- Generate secure random keys for production
- Set proper file permissions

### 2. Manual Setup

```bash
# Copy example files
cp config.env.example .env
cp ../docker.env.example ../.env

# Edit the files with your configuration
nano .env
nano ../.env
```

## 📁 Configuration Files

### Application Configuration (`python/api/.env`)

This file contains application-specific settings:

```bash
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=username
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
API_PORT=8080
DEBUG=false
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_MINUTES=30

# External APIs
YAHOO_FINANCE_API_KEY=
ALPHA_VANTAGE_API_KEY=
```

### Docker Configuration (`docker.env`)

This file contains Docker-specific settings:

```bash
# API Configuration
API_PORT=8080
DEBUG=false

# Database Configuration
POSTGRES_PORT=5432
POSTGRES_USER=username
POSTGRES_PASSWORD=password
POSTGRES_DB=portfolio

# Redis Configuration
REDIS_PORT=6379

# Security
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
```

## 🔧 Environment Variables Reference

### Database Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_HOST` | `localhost` | PostgreSQL server hostname |
| `POSTGRES_PORT` | `5432` | PostgreSQL server port |
| `POSTGRES_USER` | `username` | Database username |
| `POSTGRES_PASSWORD` | `password` | Database password |
| `POSTGRES_DB` | `portfolio` | Database name |
| `POOL_SIZE` | `20` | Connection pool size |
| `MAX_OVERFLOW` | `30` | Maximum overflow connections |
| `POOL_TIMEOUT` | `30` | Connection timeout (seconds) |
| `POOL_RECYCLE` | `3600` | Connection recycle time (seconds) |

### Redis Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_HOST` | `localhost` | Redis server hostname |
| `REDIS_PORT` | `6379` | Redis server port |
| `REDIS_DB` | `0` | Redis database number |
| `REDIS_PASSWORD` | `` | Redis password (if required) |

### API Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `API_HOST` | `0.0.0.0` | API server host |
| `API_PORT` | `8080` | API server port |
| `DEBUG` | `false` | Enable debug mode |
| `LOG_LEVEL` | `INFO` | Logging level |

### Security Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `auto-generated` | Application secret key |
| `JWT_SECRET_KEY` | `auto-generated` | JWT signing secret |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token expiry |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token expiry |

## 🐳 Docker Deployment

### 1. Start with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### 2. Environment Variable Override

You can override environment variables when running Docker:

```bash
# Override specific variables
POSTGRES_PASSWORD=mypassword docker-compose up -d

# Use a different .env file
docker-compose --env-file .env.production up -d
```

### 3. Production Deployment

For production, create a separate `.env.production` file:

```bash
# Copy example
cp docker.env.example .env.production

# Edit with production values
nano .env.production

# Use production config
docker-compose --env-file .env.production up -d
```

## 🔒 Security Best Practices

### 1. Secret Management

- **Never commit `.env` files** to version control
- **Use strong, random keys** for production
- **Rotate secrets regularly**
- **Use different keys** for different environments

### 2. Production Configuration

```bash
# Generate strong secrets
openssl rand -hex 32
python3 -c "import secrets; print(secrets.token_hex(32))"

# Use environment-specific files
.env.development
.env.staging
.env.production
```

### 3. File Permissions

```bash
# Set restrictive permissions
chmod 600 .env
chmod 600 .env.production

# Verify ownership
chown $USER:$USER .env
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Environment Variables Not Loading

```bash
# Check if .env file exists
ls -la .env

# Verify file permissions
ls -la .env

# Test variable loading
source .env && echo $POSTGRES_HOST
```

#### 2. Docker Environment Issues

```bash
# Check Docker environment
docker-compose config

# Verify environment variables
docker-compose exec api env | grep POSTGRES

# Check service logs
docker-compose logs api
```

#### 3. Database Connection Issues

```bash
# Test database connection
pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER

# Check environment variables
echo "Host: $POSTGRES_HOST"
echo "Port: $POSTGRES_PORT"
echo "User: $POSTGRES_USER"
echo "Database: $POSTGRES_DB"
```

### Debug Mode

Enable debug mode for troubleshooting:

```bash
# Set in .env file
DEBUG=true
LOG_LEVEL=DEBUG

# Or override when running
DEBUG=true python main.py
```

## 📚 Additional Resources

- [FastAPI Environment Variables](https://fastapi.tiangolo.com/advanced/settings/)
- [Pydantic Settings](https://pydantic-docs.helpmanual.io/usage/settings/)
- [Docker Environment Variables](https://docs.docker.com/compose/environment-variables/)
- [PostgreSQL Connection](https://www.postgresql.org/docs/current/libpq-envars.html)

## 🤝 Contributing

When adding new environment variables:

1. **Update example files** (`config.env.example`, `docker.env.example`)
2. **Add to configuration class** (`database/config.py`)
3. **Update documentation** (this file)
4. **Test with different values**
5. **Verify Docker integration**

---

**Note**: Always keep your `.env` files secure and never commit them to version control. Use the example files as templates and customize them for your specific environment.
