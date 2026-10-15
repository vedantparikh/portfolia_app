"""
Test API endpoints to verify routing works correctly.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to Portfolia API"
    assert "version" in data
    assert "environment" in data


def test_health_endpoint():
    """Test the health endpoint."""
    response = client.get("/health/")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_health_detailed_endpoint():
    """Test the detailed health endpoint."""
    response = client.get("/health/detailed")
    # This endpoint may fail if database is not available
    if response.status_code == 200:
        data = response.json()
        assert "status" in data
        assert "database" in data
    elif response.status_code == 503:
        # Service unavailable due to database connection failure
        data = response.json()
        assert "detail" in data
        assert "Health check failed" in data["detail"]
    else:
        pytest.fail(f"Unexpected status code: {response.status_code}")


def test_test_router_endpoint():
    """Test the test router endpoint."""
    response = client.get("/app/v1/test/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Test endpoint working!"
    assert data["status"] == "success"
    assert data["router"] == "test_router"


def test_test_router_health():
    """Test the test router health endpoint."""
    response = client.get("/app/v1/test/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "test_router"


def test_openapi_docs():
    """Test that OpenAPI documentation is available."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_schema():
    """Test that OpenAPI schema is available."""
    response = client.get("/app/v1/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data


if __name__ == "__main__":
    pytest.main([__file__])
