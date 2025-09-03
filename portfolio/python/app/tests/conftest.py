import pytest
import asyncio
import os
import tempfile
from pathlib import Path
from typing import Generator, AsyncGenerator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import sys
import os

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Set testing environment BEFORE importing app modules
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["POSTGRES_HOST"] = "localhost"
os.environ["POSTGRES_PORT"] = "5432"
os.environ["POSTGRES_USER"] = "test_user"
os.environ["POSTGRES_PASSWORD"] = "test_password"
os.environ["POSTGRES_DB"] = "test_db"
os.environ["REDIS_HOST"] = "localhost"
os.environ["REDIS_PORT"] = "6379"
os.environ["REDIS_DB"] = "1"
os.environ["REDIS_PASSWORD"] = ""
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-key-for-testing-only"

# Force SQLite for testing
os.environ["FORCE_SQLITE"] = "true"

# Import after setting environment variables to ensure test config is used
from app.main import app
from app.core.database.connection import Base, get_db
from app.config import settings


# Create test database
@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine."""
    # Use in-memory SQLite for testing
    test_db_url = "sqlite:///:memory:"
    engine = create_engine(
        test_db_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    return engine


@pytest.fixture(scope="session")
def test_db_session_factory(test_db_engine):
    """Create test database session factory."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    return TestingSessionLocal


@pytest.fixture(scope="function")
def test_db(test_db_engine, test_db_session_factory):
    """
    Create test database session for each test function.
    
    Each test gets a fresh database session with:
    - Clean tables (recreated for each test)
    - Isolated data (no cross-test contamination)
    - Automatic cleanup after each test
    """
    # Create tables for this test
    Base.metadata.create_all(bind=test_db_engine)
    
    # Create session
    session = test_db_session_factory()
    
    yield session
    
    # Cleanup - rollback changes and close session
    session.rollback()
    session.close()
    
    # Clean tables after each test to ensure isolation
    Base.metadata.drop_all(bind=test_db_engine)


@pytest.fixture(scope="function")
def client(test_db) -> Generator:
    """Create test client with test database."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    # Override database dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Also override any other database-related dependencies
    try:
        from core.database.init_db import init_db
        app.dependency_overrides[init_db] = lambda: None
    except ImportError:
        pass
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Cleanup
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def async_client(test_db) -> AsyncGenerator:
    """Create async test client with test database."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    # Override database dependency
    app.dependency_overrides[get_db] = override_get_db
    
    from httpx import AsyncClient
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client
    
    # Cleanup
    app.dependency_overrides.clear()


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_database(test_db_engine):
    """
    Clean up test database after all tests complete.
    
    This fixture runs automatically after all tests finish and ensures:
    1. All SQLite tables are dropped
    2. Database engine is properly disposed
    3. No test data persists between test runs
    4. Clean test environment for next run
    """
    yield
    # Drop all tables and close engine after all tests
    Base.metadata.drop_all(bind=test_db_engine)
    test_db_engine.dispose()
    print("\n🧹 Test database cleaned up successfully!")


# Test data fixtures
@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "confirm_password": "testpassword123"
    }


@pytest.fixture
def sample_login_data():
    """Sample login data for testing."""
    return {
        "username": "testuser",
        "password": "testpassword123"
    }


@pytest.fixture
def sample_market_data():
    """Sample market data for testing."""
    return {
        "symbol": "AAPL",
        "period": "1d",
        "interval": "1m"
    }


@pytest.fixture
def sample_indicator_data():
    """Sample indicator data for testing."""
    return {
        "name": "AAPL",
        "period": 14,
        "interval": "1d"
    }
