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

from app.main import app
from app.core.database.connection import Base, get_db
from app.config import settings


# Set testing environment
os.environ["TESTING"] = "true"

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
    """Create test database session."""
    # Create tables
    Base.metadata.create_all(bind=test_db_engine)
    
    # Create session
    session = test_db_session_factory()
    
    yield session
    
    # Cleanup
    session.close()
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


# Test data fixtures
@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }


@pytest.fixture
def sample_portfolio_data():
    """Sample portfolio data for testing."""
    return {
        "name": "Test Portfolio",
        "description": "A test portfolio for testing purposes",
        "risk_tolerance": "moderate"
    }


@pytest.fixture
def sample_asset_data():
    """Sample asset data for testing."""
    return {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "asset_type": "stock",
        "quantity": 100,
        "purchase_price": 150.0
    }


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Clean up test files after tests."""
    yield
    
    # Remove test database file if it exists
    test_db_path = Path("./test.db")
    if test_db_path.exists():
        test_db_path.unlink()
    
    # Remove coverage files
    coverage_files = [
        Path("./.coverage"),
        Path("./coverage.xml"),
        Path("./htmlcov")
    ]
    
    for file_path in coverage_files:
        if file_path.exists():
            if file_path.is_file():
                file_path.unlink()
            elif file_path.is_dir():
                import shutil
                shutil.rmtree(file_path)
