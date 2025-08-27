# Migration Guide

This guide helps you migrate from the old Portfolia API structure to the new, restructured version.

## 🔄 What Changed

### Directory Structure

**Old Structure:**
```
api/
├── auth/
├── database/
├── market/
├── statistical_indicators/
├── trading_strategy/
├── main.py
├── health_check.py
└── ...
```

**New Structure:**
```
api/
├── app/                          # Main application
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

### Key Changes

1. **Centralized Configuration**: All settings now in `app/config.py`
2. **Separated Concerns**: Business logic moved to `services/`, schemas to `models/`
3. **Cleaner Imports**: Better organized import paths
4. **Modern Packaging**: Added `pyproject.toml` for better dependency management
5. **Enhanced Testing**: Reorganized test structure with better organization

## 🚀 Migration Steps

### Step 1: Backup Your Current Code

```bash
# Create a backup branch
git checkout -b backup/old-structure
git push origin backup/old-structure

# Return to main branch
git checkout main
```

### Step 2: Update Dependencies

**Old requirements.txt:**
```txt
fastapi==0.108.0
uvicorn==0.25.0
sqlalchemy==2.0.25
# ... other dependencies
```

**New requirements.txt:**
```txt
# FastAPI and ASGI
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
redis==5.0.1

# ... more organized dependencies
```

**Install new dependencies:**
```bash
pip install -r requirements.txt
# Or use the new pyproject.toml
pip install -e ".[dev]"
```

### Step 3: Update Import Statements

#### Database Models

**Old:**
```python
from database.models import User, Portfolio
from database.connection import get_db
```

**New:**
```python
from app.core.database.models import User, Portfolio
from app.core.database.connection import get_db
```

#### Authentication

**Old:**
```python
from auth.router import auth_router
from auth.utils import create_access_token
```

**New:**
```python
from app.core.auth.router import auth_router
from app.core.auth.utils import create_access_token
```

#### Market Data

**Old:**
```python
from market.routers import router as market_router
from market.stock import get_stock_data
```

**New:**
```python
from api.v1.market.routers import router as market_router
from services.market_service import MarketService
```

#### Statistical Indicators

**Old:**
```python
from statistical_indicators.momentum_indicators import calculate_rsi
from statistical_indicators.trend_indicators import calculate_sma
```

**New:**
```python
from utils.indicators.momentum_indicators import calculate_rsi
from utils.indicators.trend_indicators import calculate_sma
```

#### Trading Strategies

**Old:**
```python
from trading_strategy.trend_strategy.gfs_strategy.gfs import GFSStrategy
from trading_strategy.trend_strategy.macd_strategy import MACDStrategy
```

**New:**
```python
from utils.trading_strategies.gfs_strategy import GFSStrategy
from utils.trading_strategies.macd_strategy import MACDStrategy
```

### Step 4: Update Configuration

**Old config approach:**
```python
# database/config.py
class DBSettings:
    postgres_url: str = "postgresql://..."
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
```

**New config approach:**
```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://..."
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    class Config:
        env_file = ".env"
```

**Update your .env file:**
```bash
# Old variables
POSTGRES_URL=postgresql://...
API_HOST=0.0.0.0
API_PORT=8000

# New variables
DATABASE_URL=postgresql://...
API_HOST=0.0.0.0
API_PORT=8000
```

### Step 5: Update Main Application

**Old main.py:**
```python
from fastapi import FastAPI
from market.routers import router as market_router
from auth import auth_router

app = FastAPI(title="Portfolia API")
app.include_router(market_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
```

**New main.py:**
```python
from fastapi import FastAPI
from app.config import settings
from app.health_check import router as health_router

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    debug=settings.debug
)

# Include routers
app.include_router(health_router, prefix="/health", tags=["health"])

# Import and include API routers
try:
    from api.v1.auth.router import router as auth_router
    from api.v1.market.routers import router as market_router
    
    app.include_router(auth_router, prefix=f"{settings.api_v1_str}/auth", tags=["authentication"])
    app.include_router(market_router, prefix=f"{settings.api_v1_str}/market", tags=["market"])
    
except ImportError as e:
    logger.warning(f"Could not import some routers: {e}")
```

### Step 6: Update Test Files

**Old test structure:**
```
tests/
├── test_auth_system.py
├── test_market_stock.py
├── test_momentum_indicators.py
└── ...
```

**New test structure:**
```
tests/
├── unit/
│   ├── test_services/
│   ├── test_models/
│   └── test_utils/
├── integration/
│   ├── test_api/
│   └── test_database/
└── conftest.py
```

**Move test files:**
```bash
# Create new test directories
mkdir -p tests/unit tests/integration

# Move unit tests
mv tests/test_*.py tests/unit/

# Update test imports
# Old: from database.models import User
# New: from app.core.database.models import User
```

### Step 7: Update Scripts and Documentation

**Move script files:**
```bash
# Move shell scripts to scripts directory
mv *.sh scripts/
mv setup_*.py scripts/
```

**Update script paths:**
```bash
# Old: python setup_env.py
# New: python scripts/setup_env.py

# Old: ./setup_database.sh
# New: ./scripts/setup_database.sh
```

## 🔧 Configuration Migration

### Environment Variables

**Old .env structure:**
```bash
POSTGRES_URL=postgresql://user:password@localhost/portfolia
REDIS_HOST=localhost
REDIS_PORT=6379
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-secret-key
```

**New .env structure:**
```bash
DATABASE_URL=postgresql://user:password@localhost/portfolia
REDIS_HOST=localhost
REDIS_PORT=6379
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

### Database Configuration

**Old database connection:**
```python
# database/connection.py
from database.config import db_settings

engine = create_engine(db_settings.postgres_url)
```

**New database connection:**
```python
# app/core/database/connection.py
from app.config import settings

engine = create_engine(settings.database_url)
```

## 📊 API Endpoint Changes

### URL Structure

**Old endpoints:**
```
/api/auth/login
/api/market/stock/AAPL
/api/indicators/rsi
```

**New endpoints:**
```
/api/v1/auth/login
/api/v1/market/stock/AAPL
/api/v1/indicators/rsi
```

### Response Models

**Old approach:**
```python
# Direct database model usage
@router.get("/portfolio/{portfolio_id}")
def get_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    return portfolio
```

**New approach:**
```python
# Use Pydantic schemas for responses
@router.get("/portfolio/{portfolio_id}", response_model=PortfolioResponse)
def get_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    return PortfolioResponse.from_orm(portfolio)
```

## 🧪 Testing Migration

### Test Configuration

**Old conftest.py:**
```python
import pytest
from database.connection import get_db
```

**New conftest.py:**
```python
import pytest
from app.core.database.connection import get_db
```

### Test Imports

**Update all test files:**
```python
# Old imports
from database.models import User, Portfolio
from auth.utils import create_access_token
from market.stock import get_stock_data

# New imports
from app.core.database.models import User, Portfolio
from app.core.auth.utils import create_access_token
from services.market_service import MarketService
```

## 🚀 Running the Migrated Application

### 1. Install Dependencies

```bash
# Install new dependencies
pip install -e ".[dev]"

# Or install requirements directly
pip install -r requirements.txt
```

### 2. Update Environment

```bash
# Copy and edit environment file
cp app/config.env.example app/.env
# Edit .env with your configuration
```

### 3. Run Database Migrations

```bash
# Apply any new migrations
alembic upgrade head
```

### 4. Start the Application

```bash
# Start with uvicorn
uvicorn app.main:app --reload

# Or use the main.py directly
python app/main.py
```

### 5. Verify Migration

```bash
# Check health endpoint
curl http://localhost:8000/health

# Check API documentation
open http://localhost:8000/docs

# Run tests
pytest
```

## 🔍 Troubleshooting Migration

### Common Issues

#### Import Errors

**Error:** `ModuleNotFoundError: No module named 'database'`

**Solution:** Update imports to use new paths
```python
# Old
from database.models import User

# New
from app.core.database.models import User
```

#### Configuration Errors

**Error:** `AttributeError: 'Settings' object has no attribute 'postgres_url'`

**Solution:** Update configuration references
```python
# Old
db_settings.postgres_url

# New
settings.database_url
```

#### Database Connection Issues

**Error:** `Database connection failed`

**Solution:** Check new environment variable names
```bash
# Old
POSTGRES_URL=postgresql://...

# New
DATABASE_URL=postgresql://...
```

#### Test Failures

**Error:** `ImportError in tests`

**Solution:** Update test imports and configuration
```python
# Update conftest.py and test files
from app.core.database.connection import get_db
```

### Getting Help

1. **Check the logs** for detailed error messages
2. **Review the new structure** to understand the organization
3. **Compare old and new files** to see what changed
4. **Run tests incrementally** to identify specific issues
5. **Check the documentation** for new usage patterns

## 📚 Post-Migration Benefits

### What You Gain

1. **Better Organization**: Clear separation of concerns
2. **Easier Testing**: Better test structure and organization
3. **Modern Packaging**: Better dependency management
4. **Cleaner Imports**: More intuitive import paths
5. **Better Documentation**: Comprehensive API documentation
6. **Enhanced Security**: Better configuration management
7. **Scalability**: Easier to add new features and maintain

### Next Steps

1. **Explore the new structure** to understand the organization
2. **Update your development workflow** to use new tools
3. **Take advantage of new features** like enhanced configuration
4. **Contribute to the project** using the new structure
5. **Provide feedback** on the new organization

## 🔄 Rollback Plan

If you encounter issues during migration:

1. **Keep your backup branch** (`backup/old-structure`)
2. **Document any issues** you encounter
3. **Test incrementally** rather than all at once
4. **Seek help** from the development team
5. **Consider partial migration** if needed

## 📞 Support

For migration assistance:

- **Documentation**: Check the new documentation structure
- **Issues**: Create GitHub issues for specific problems
- **Discussions**: Use GitHub discussions for general questions
- **Code Review**: Request help with migration PRs

Remember: The new structure is designed to make your development experience better. Take your time with the migration and don't hesitate to ask for help!
