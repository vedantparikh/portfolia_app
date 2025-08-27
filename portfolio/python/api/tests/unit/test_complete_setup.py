#!/usr/bin/env python3
"""
Comprehensive testing script for Portfolia application.
This script tests all major components: environment, database, API, and functionality.
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, List
import unittest

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))


class TestPortfoliaSetup(unittest.TestCase):
    """Test Portfolia application setup and configuration."""

    def setUp(self):
        """Set up test environment."""
        self.results = {}
        self.errors = []
        self.warnings = []

    def test_environment_setup(self):
        """Test environment configuration setup."""
        # Check if .env file exists
        env_file = Path("app/.env")
        if env_file.exists():
            self.assertTrue(True, ".env file exists")
        else:
            # Check if config.env.example exists
            example_env = Path("app/config.env.example")
            self.assertTrue(example_env.exists(), "config.env.example should exist")

    def test_configuration_loading(self):
        """Test configuration loading."""
        try:
            from app.config import settings
            self.assertIsNotNone(settings)
            self.assertEqual(settings.project_name, "Portfolia API")
            self.assertEqual(settings.version, "1.0.0")
        except ImportError as e:
            self.fail(f"Failed to import configuration: {e}")

    def test_database_models_import(self):
        """Test database models import."""
        try:
            from app.core.database.models import Base, User, Portfolio, Asset
            self.assertIsNotNone(Base)
            self.assertIsNotNone(User)
            self.assertIsNotNone(Portfolio)
            self.assertIsNotNone(Asset)
        except ImportError as e:
            self.fail(f"Failed to import database models: {e}")

    def test_database_connection(self):
        """Test database connection setup."""
        try:
            from app.core.database.connection import engine, SessionLocal
            self.assertIsNotNone(engine)
            self.assertIsNotNone(SessionLocal)
        except ImportError as e:
            self.fail(f"Failed to import database connection: {e}")

    def test_main_app_import(self):
        """Test main application import."""
        try:
            from app.main import app
            self.assertIsNotNone(app)
        except ImportError as e:
            self.fail(f"Failed to import main application: {e}")

    def test_health_check_import(self):
        """Test health check import."""
        try:
            from app.health_check import router
            self.assertIsNotNone(router)
        except ImportError as e:
            self.fail(f"Failed to import health check: {e}")

    def test_requirements_installed(self):
        """Test that required packages are installed."""
        required_packages = [
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "pydantic",
            "pydantic_settings"
        ]
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                self.fail(f"Required package {package} is not installed")

    def test_project_structure(self):
        """Test that project structure is correct."""
        required_dirs = [
            "app",
            "app/core",
            "app/core/database",
            "app/core/database/models",
            "api",
            "api/v1",
            "services",
            "models",
            "utils",
            "tests",
            "docs"
        ]
        
        for directory in required_dirs:
            dir_path = Path(directory)
            self.assertTrue(dir_path.exists(), f"Directory {directory} should exist")

    def test_documentation_files(self):
        """Test that documentation files exist."""
        required_docs = [
            "README.md",
            "docs/architecture/ARCHITECTURE.md",
            "docs/development/DEVELOPMENT.md",
            "docs/development/MIGRATION_GUIDE.md"
        ]
        
        for doc_file in required_docs:
            doc_path = Path(doc_file)
            self.assertTrue(doc_path.exists(), f"Documentation file {doc_file} should exist")


if __name__ == "__main__":
    unittest.main()
