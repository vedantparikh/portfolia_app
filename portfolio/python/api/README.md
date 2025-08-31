# Portfolia API

A modern, scalable financial portfolio analysis and trading strategy API built with FastAPI.

## 🏗️ Architecture Overview

The API follows a clean, layered architecture pattern:

```
api/
├── app/                          # Main application package
│   ├── main.py                   # FastAPI app instance
│   ├── config.py                 # Configuration management
│   └── core/                     # Core functionality
│       ├── database/             # Database layer
│       ├── auth/                 # Authentication
│       └── middleware/           # Custom middleware
├── api/                          # API endpoints
│   └── v1/                       # Version 1 API
│       ├── auth/                 # Authentication endpoints
│       ├── market/               # Market data endpoints
│       ├── portfolio/            # Portfolio management
│       └── statistical_indicators/ # Technical indicators
├── services/                     # Business logic layer
├── models/                       # Pydantic schemas
├── utils/                        # Utility functions
│   ├── indicators/               # Technical indicators
│   └── trading_strategies/      # Trading strategies
└── tests/                        # Test suite
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Redis 6+

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/portfolia/portfolia-api.git
   cd portfolia-api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   # Or for development:
   pip install -e ".[dev]"
   ```

4. **Set up environment variables**
   ```bash
   cp app/config.env.example app/.env
   # Edit .env with your configuration
   ```

5. **Set up database**
   ```bash
   # Run database migrations
   alembic upgrade head
   ```

6. **Start the API**
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

- **Interactive API docs**: `http://localhost:8000/docs`
- **OpenAPI schema**: `http://localhost:8000/openapi.json`
- **Health check**: `http://localhost:8000/health`

## 🏛️ Project Structure

### Core Application (`app/`)

- **`main.py`**: FastAPI application instance and configuration
- **`config.py`**: Centralized configuration management using Pydantic Settings
- **`core/`**: Core application components
  - **`database/`**: Database models, connection, and utilities
  - **`auth/`**: Authentication and authorization logic
  - **`middleware/`**: Custom middleware components

### API Endpoints (`api/`)

- **`v1/`**: Version 1 API endpoints
  - **`auth/`**: User authentication and management
  - **`market/`**: Market data and stock information
  - **`portfolio/`**: Portfolio management operations
  - **`statistical_indicators/`**: Technical analysis indicators

### Business Logic (`services/`)

- **`MarketService`**: Market data operations
- **`PortfolioService`**: Portfolio management logic
- **`StatisticalService`**: Statistical calculations and indicators

### Data Models (`models/`)

- **Pydantic schemas** for request/response validation
- **Database models** for ORM operations
- **Type definitions** for better code quality

### Utilities (`utils/`)

- **`indicators/`**: Technical analysis indicators
- **`trading_strategies/`**: Trading strategy implementations

## 🔧 Configuration

The API uses Pydantic Settings for configuration management. Key configuration options:

```python
# Database
database_url: str = "postgresql://user:password@localhost/portfolia"

# Security
secret_key: str = "your-secret-key-here"
algorithm: str = "HS256"
access_token_expire_minutes: int = 30

# API
api_v1_str: str = "/api/v1"
project_name: str = "Portfolia API"
version: str = "1.0.0"

# CORS
backend_cors_origins: list = ["http://localhost:3000", "http://localhost:8080"]
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov=api --cov=services --cov=schemas --cov=utils

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m slow          # Slow tests only
```

### Test Structure

```
tests/
├── unit/               # Unit tests
│   ├── test_services/
│   ├── test_models/
│   └── test_utils/
├── integration/        # Integration tests
│   ├── test_api/
│   └── test_database/
└── conftest.py         # Test configuration
```

## 🚀 Deployment

### Docker

```bash
# Build image
docker build -t portfolia-api .

# Run container
docker run -p 8000:8000 portfolia-api
```

### Production Considerations

- Use environment-specific configuration files
- Enable proper logging and monitoring
- Set up health checks and metrics
- Configure CORS for production domains
- Use proper secret management
- Set up database connection pooling

## 📖 Development

### Code Quality

The project uses several tools for code quality:

- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking
- **Pre-commit**: Git hooks

### Pre-commit Setup

```bash
pre-commit install
```

### Adding New Features

1. **Create models** in `app/core/database/models/`
2. **Create schemas** in `models/`
3. **Implement business logic** in `services/`
4. **Create API endpoints** in `api/v1/`
5. **Add tests** in `tests/`
6. **Update documentation**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Ensure code quality checks pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [API Docs](http://localhost:8000/docs)
- **Issues**: [GitHub Issues](https://github.com/portfolia/portfolia-api/issues)
- **Discussions**: [GitHub Discussions](https://github.com/portfolia/portfolia-api/discussions)

## 🔄 Migration Guide

If you're upgrading from the old structure:

1. **Update imports** to use new paths
2. **Update configuration** to use new config system
3. **Update tests** to use new test structure
4. **Check API endpoints** for new routing

## 📊 Performance

- **Database**: Optimized queries with proper indexing
- **Caching**: Redis integration for frequently accessed data
- **Async**: FastAPI async support for better concurrency
- **Validation**: Pydantic for efficient data validation

## 🔒 Security

- **Authentication**: JWT-based authentication
- **Authorization**: Role-based access control
- **Validation**: Input validation and sanitization
- **HTTPS**: Production-ready security headers
