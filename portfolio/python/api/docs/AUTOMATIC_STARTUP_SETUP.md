# Automatic Startup Setup for Portfolia API

## Overview

The Portfolia API now automatically handles database initialization, migrations, and schema creation on startup, eliminating the need to run separate commands. Additionally, tests now use SQLite instead of PostgreSQL for faster and more reliable testing.

## 🚀 **What Happens on Startup**

### 1. **Automatic Database Initialization**
- **Connection Test**: Waits for database to be ready
- **Schema Creation**: Automatically creates all database tables
- **Sample Data**: Initializes sample data if needed
- **Health Verification**: Confirms database is healthy before starting

### 2. **Graceful Degradation**
- If database initialization fails, the app starts with degraded functionality
- Health endpoints will report the current status
- Application remains accessible for debugging

## 🛠️ **How to Start the API**

### **Option 1: Local Development (Recommended)**
```bash
# From the portfolio directory
./start_api.sh

# Or manually from the api directory
cd python/api
python start_api.py
```

### **Option 2: Docker**
```bash
# Start all services with automatic initialization
docker-compose up

# Or just the API (will wait for database)
docker-compose up api
```

### **Option 3: Direct Python**
```bash
cd python/api
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📊 **Test Configuration**

### **SQLite for Testing**
- Tests automatically use in-memory SQLite database
- No external database required for testing
- Faster test execution
- Isolated test environment

### **Test Environment Variables**
```bash
# Automatically set by pytest.ini
TESTING=true
DATABASE_URL=sqlite:///./test.db
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=1
```

### **Running Tests**
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/unit/test_structure.py

# Run with coverage
python -m pytest --cov=app --cov-report=html
```

## 🔧 **Configuration Files**

### **pytest.ini**
- Configures test environment
- Sets SQLite database for tests
- Configures coverage reporting
- Defines test markers

### **conftest.py**
- Provides test fixtures
- Sets up test database
- Configures test clients
- Handles cleanup

## 🐳 **Docker Setup**

### **Dockerfile Features**
- **Startup Script**: Automatically waits for database
- **Health Checks**: Monitors application health
- **Dependencies**: Installs all required packages
- **Volume Mounting**: Supports development with live reload

### **docker-compose.yml Features**
- **Health Checks**: Ensures services are ready
- **Dependencies**: API waits for database and Redis
- **Networking**: Isolated network for services
- **Volumes**: Persistent data storage

## 📁 **File Structure**

```
portfolio/
├── start_api.sh                 # Main startup script
├── python/
│   └── api/
│       ├── start_api.py         # Python startup script
│       ├── app/
│       │   ├── main.py          # FastAPI app with lifespan
│       │   ├── config.py        # Configuration management
│       │   └── core/
│       │       └── database/
│       │           ├── connection.py    # Database connection
│       │           └── init_db.py       # Database initialization
│       ├── tests/
│       │   ├── conftest.py      # Test configuration
│       │   └── unit/            # Unit tests
│       ├── pytest.ini           # Pytest configuration
│       ├── Dockerfile           # Docker configuration
│       └── docker-compose.yml   # Service orchestration
```

## 🔍 **Health Endpoints**

### **Basic Health Check**
```bash
GET /health/
```
Returns overall application health status.

### **Detailed Health Check**
```bash
GET /health/detailed
```
Returns detailed health information including database statistics.

## 🚨 **Troubleshooting**

### **Database Connection Issues**
1. Check if PostgreSQL is running
2. Verify connection string in `.env`
3. Check database permissions
4. Review startup logs for specific errors

### **Test Failures**
1. Ensure `TESTING=true` environment variable is set
2. Check that all dependencies are installed
3. Verify test database configuration
4. Review test logs for specific errors

### **Docker Issues**
1. Check if all services are healthy
2. Review Docker logs: `docker-compose logs api`
3. Verify network connectivity
4. Check volume permissions

## 📈 **Benefits**

### **Development**
- **Single Command**: Start everything with one command
- **Automatic Setup**: No manual database initialization
- **Consistent Environment**: Same setup across all developers
- **Fast Iteration**: Quick restart and testing cycles

### **Testing**
- **Fast Execution**: SQLite in-memory database
- **Isolated Environment**: No external dependencies
- **Reliable**: Consistent test environment
- **Coverage**: Built-in coverage reporting

### **Deployment**
- **Self-Contained**: Application manages its own setup
- **Health Monitoring**: Built-in health checks
- **Graceful Degradation**: Continues running even with issues
- **Docker Ready**: Optimized for containerized deployment

## 🔄 **Migration from Old Setup**

### **Before (Old Way)**
```bash
# Start database manually
docker-compose up postgres

# Run migrations manually
python -m alembic upgrade head

# Start application
python -m uvicorn app.main:app --reload
```

### **After (New Way)**
```bash
# Single command starts everything
./start_api.sh

# Or with Docker
docker-compose up
```

## 🎯 **Next Steps**

1. **Test the Setup**: Run `./start_api.sh` to verify everything works
2. **Run Tests**: Execute `python -m pytest` to verify test configuration
3. **Docker Test**: Try `docker-compose up` to test containerized setup
4. **Customize**: Modify configuration files as needed for your environment

## 📚 **Additional Resources**

- [FastAPI Lifespan Documentation](https://fastapi.tiangolo.com/advanced/events/)
- [SQLAlchemy Async Support](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Pytest Configuration](https://docs.pytest.org/en/stable/reference/customize.html)
- [Docker Health Checks](https://docs.docker.com/engine/reference/builder/#healthcheck)
