"""
Test to verify the new API structure works correctly.
"""

import unittest

from app.config import settings
from app.main import app


class TestPortfoliaStructure(unittest.TestCase):
    """Test the core application structure."""

    def test_app_creation(self):
        """Test that the FastAPI app is created correctly."""
        self.assertIsNotNone(app)
        self.assertEqual(app.title, "Portfolia API")
        self.assertEqual(app.version, "1.0.0")

    def test_config_loading(self):
        """Test that configuration loads correctly."""
        assert settings.PROJECT_NAME == "Portfolia API"
        assert settings.VERSION == "1.0.0"
        assert settings.HOST == "0.0.0.0"
        assert settings.PORT == 8000

    def test_health_endpoint_exists(self):
        """Test that health endpoints exist."""
        routes = [route.path for route in app.routes]
        assert "/health/" in routes
        assert "/health/detailed" in routes

    def test_api_v1_prefix(self):
        """Test that API v1 endpoints exist."""
        routes = [route.path for route in app.routes]
        assert "/app/v1/" in routes
        # Check for test router endpoints
        assert "/app/v1/health" in routes


if __name__ == "__main__":
    unittest.main()
