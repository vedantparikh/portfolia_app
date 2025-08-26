#!/usr/bin/env python3
"""
Comprehensive testing script for Portfolia application.
This script tests all major components: environment, database, API, and functionality.
"""

import os
import sys
import time
import requests
import json
from pathlib import Path
from typing import Dict, Any, List

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))


class PortfoliaTester:
    """Comprehensive tester for Portfolia application."""

    def __init__(self):
        self.results = {}
        self.errors = []
        self.warnings = []

    def log_result(
        self, test_name: str, success: bool, message: str = "", details: Any = None
    ):
        """Log test result."""
        self.results[test_name] = {
            "success": success,
            "message": message,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")

        if not success and details:
            print(f"   Details: {details}")

    def log_warning(self, message: str):
        """Log a warning."""
        self.warnings.append(message)
        print(f"⚠️  WARNING: {message}")

    def log_error(self, message: str):
        """Log an error."""
        self.errors.append(message)
        print(f"❌ ERROR: {message}")

    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("🎯 PORTFOLIA COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)

        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r["success"])
        failed_tests = total_tests - passed_tests

        print(f"\n📊 Test Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   ⚠️  Warnings: {len(self.warnings)}")
        print(f"   ❌ Errors: {len(self.errors)}")

        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for test_name, result in self.results.items():
                if not result["success"]:
                    print(f"   - {test_name}: {result['message']}")

        if self.warnings:
            print(f"\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   - {warning}")

        if self.errors:
            print(f"\n❌ Errors:")
            for error in self.errors:
                print(f"   - {error}")

        print(
            f"\n🎯 Overall Status: {'✅ ALL TESTS PASSED' if failed_tests == 0 else '❌ SOME TESTS FAILED'}"
        )

        return failed_tests == 0

    def test_environment_setup(self) -> bool:
        """Test environment configuration setup."""
        print("\n🔧 Testing Environment Setup...")

        # Check if .env file exists
        env_file = Path(".env")
        if env_file.exists():
            self.log_result("Environment File", True, ".env file exists")

            # Check file permissions
            stat = env_file.stat()
            if stat.st_mode & 0o777 == 0o600:
                self.log_result("File Permissions", True, "Proper permissions (600)")
            else:
                self.log_result(
                    "File Permissions",
                    False,
                    f"Wrong permissions: {oct(stat.st_mode & 0o777)}",
                )
                return False
        else:
            self.log_result("Environment File", False, ".env file not found")
            return False

        # Test environment variable loading
        try:
            from database.config import db_settings

            # Check required variables
            required_vars = [
                "POSTGRES_HOST",
                "POSTGRES_PORT",
                "POSTGRES_USER",
                "POSTGRES_PASSWORD",
                "POSTGRES_DB",
                "API_HOST",
                "API_PORT",
            ]

            missing_vars = []
            for var in required_vars:
                if not hasattr(db_settings, var):
                    missing_vars.append(var)

            if missing_vars:
                self.log_result(
                    "Environment Variables", False, f"Missing variables: {missing_vars}"
                )
                return False
            else:
                self.log_result(
                    "Environment Variables", True, "All required variables present"
                )

            # Test URL generation
            postgres_url = db_settings.postgres_url
            if postgres_url and "postgresql://" in postgres_url:
                self.log_result(
                    "Database URL Generation",
                    True,
                    "PostgreSQL URL generated correctly",
                )
            else:
                self.log_result(
                    "Database URL Generation", False, f"Invalid URL: {postgres_url}"
                )
                return False

        except Exception as e:
            self.log_result(
                "Environment Loading", False, f"Failed to load environment: {e}"
            )
            return False

        return True

    def test_database_connection(self) -> bool:
        """Test database connectivity."""
        print("\n🗄️  Testing Database Connection...")

        try:
            from database.connection import health_check, redis_health_check

            # Test PostgreSQL connection
            db_health = health_check()
            if db_health:
                self.log_result(
                    "PostgreSQL Connection", True, "Database connection successful"
                )
            else:
                self.log_result(
                    "PostgreSQL Connection", False, "Database connection failed"
                )
                return False

            # Test Redis connection
            redis_health = redis_health_check()
            if redis_health:
                self.log_result("Redis Connection", True, "Redis connection successful")
            else:
                self.log_result("Redis Connection", False, "Redis connection failed")
                # Don't fail the test for Redis, just warn
                self.log_warning("Redis connection failed - some features may not work")

        except Exception as e:
            self.log_result(
                "Database Connection", False, f"Connection test failed: {e}"
            )
            return False

        return True

    def test_database_models(self) -> bool:
        """Test database models and schema."""
        print("\n🏗️  Testing Database Models...")

        try:
            from database.models import User, Portfolio, Asset, Transaction, ManualEntry
            from database.connection import Base, engine

            # Test model imports
            models = [User, Portfolio, Asset, Transaction, ManualEntry]
            for model in models:
                if model and hasattr(model, "__tablename__"):
                    self.log_result(
                        f"Model Import: {model.__name__}",
                        True,
                        f"Model loaded successfully",
                    )
                else:
                    self.log_result(
                        f"Model Import: {model.__name__}",
                        False,
                        "Model not properly loaded",
                    )
                    return False

            # Test table creation (without actually creating tables)
            metadata = Base.metadata
            if metadata:
                self.log_result(
                    "Database Metadata", True, "SQLAlchemy metadata accessible"
                )
            else:
                self.log_result(
                    "Database Metadata", False, "SQLAlchemy metadata not accessible"
                )
                return False

        except Exception as e:
            self.log_result("Database Models", False, f"Model test failed: {e}")
            return False

        return True

    def test_database_utilities(self) -> bool:
        """Test database utility functions."""
        print("\n🔧 Testing Database Utilities...")

        try:
            from database.utils import (
                get_database_stats,
                validate_database_integrity,
                calculate_portfolio_value,
                get_portfolio_performance_summary,
            )

            # Test utility function imports
            utilities = [
                get_database_stats,
                validate_database_integrity,
                calculate_portfolio_value,
                get_portfolio_performance_summary,
            ]

            for utility in utilities:
                if callable(utility):
                    self.log_result(
                        f"Utility Import: {utility.__name__}",
                        True,
                        "Utility function accessible",
                    )
                else:
                    self.log_result(
                        f"Utility Import: {utility.__name__}",
                        False,
                        "Utility function not accessible",
                    )
                    return False

            # Test database stats function
            from database.connection import get_db_context

            with get_db_context() as db:
                try:
                    stats = get_database_stats(db)
                    if isinstance(stats, dict):
                        self.log_result(
                            "Database Stats Function", True, "Stats function working"
                        )
                    else:
                        self.log_result(
                            "Database Stats Function",
                            False,
                            "Stats function returned wrong type",
                        )
                        return False
                except Exception as e:
                    self.log_result(
                        "Database Stats Function", False, f"Stats function failed: {e}"
                    )
                    return False

        except Exception as e:
            self.log_result("Database Utilities", False, f"Utility test failed: {e}")
            return False

        return True

    def test_api_structure(self) -> bool:
        """Test API structure and routes."""
        print("\n🌐 Testing API Structure...")

        try:
            from main import app

            # Check if FastAPI app is properly configured
            if hasattr(app, "routes") and app.routes:
                self.log_result("FastAPI App", True, "FastAPI application loaded")
            else:
                self.log_result(
                    "FastAPI App", False, "FastAPI application not properly loaded"
                )
                return False

            # Check for required routes
            routes = [route.path for route in app.routes]
            required_routes = ["/health", "/health/detailed", "/api/market/symbols"]

            missing_routes = []
            for route in required_routes:
                if route not in routes:
                    missing_routes.append(route)

            if missing_routes:
                self.log_result(
                    "API Routes", False, f"Missing routes: {missing_routes}"
                )
                return False
            else:
                self.log_result("API Routes", True, "All required routes present")

            # Check OpenAPI schema
            if hasattr(app, "openapi"):
                self.log_result("OpenAPI Schema", True, "OpenAPI schema accessible")
            else:
                self.log_result(
                    "OpenAPI Schema", False, "OpenAPI schema not accessible"
                )

        except Exception as e:
            self.log_result("API Structure", False, f"API structure test failed: {e}")
            return False

        return True

    def test_api_endpoints(self) -> bool:
        """Test API endpoints functionality."""
        print("\n🔌 Testing API Endpoints...")

        # Check if API server is running
        try:
            # Try to connect to the API
            response = requests.get("http://localhost:8080/health", timeout=5)
            if response.status_code == 200:
                self.log_result("Health Endpoint", True, "Health endpoint responding")

                # Parse response
                try:
                    data = response.json()
                    if "status" in data and "database" in data:
                        self.log_result(
                            "Health Response Format",
                            True,
                            "Health response format correct",
                        )
                    else:
                        self.log_result(
                            "Health Response Format",
                            False,
                            "Health response format incorrect",
                        )
                        return False
                except json.JSONDecodeError:
                    self.log_result(
                        "Health Response Format",
                        False,
                        "Health response not valid JSON",
                    )
                    return False

            else:
                self.log_result(
                    "Health Endpoint",
                    False,
                    f"Health endpoint returned status {response.status_code}",
                )
                return False

        except requests.exceptions.ConnectionError:
            self.log_result(
                "API Connection", False, "Cannot connect to API server - is it running?"
            )
            self.log_warning("API server not running - start with: python main.py")
            return False
        except Exception as e:
            self.log_result("API Endpoints", False, f"API endpoint test failed: {e}")
            return False

        return True

    def test_dependencies(self) -> bool:
        """Test Python dependencies and imports."""
        print("\n📦 Testing Dependencies...")

        try:
            # Test core dependencies
            import fastapi
            import sqlalchemy
            import polars
            import redis
            import pydantic_settings

            self.log_result("FastAPI", True, f"FastAPI {fastapi.__version__}")
            self.log_result("SQLAlchemy", True, f"SQLAlchemy {sqlalchemy.__version__}")
            self.log_result("Polars", True, f"Polars {polars.__version__}")
            self.log_result("Redis", True, f"Redis {redis.__version__}")
            self.log_result(
                "Pydantic Settings",
                True,
                f"Pydantic Settings {pydantic_settings.__version__}",
            )

            # Test additional dependencies
            import uvicorn
            import psycopg2
            import alembic

            self.log_result("Uvicorn", True, f"Uvicorn {uvicorn.__version__}")
            self.log_result("Psycopg2", True, "Psycopg2 available")
            self.log_result("Alembic", True, f"Alembic {alembic.__version__}")

        except ImportError as e:
            self.log_result("Dependencies", False, f"Missing dependency: {e}")
            return False
        except Exception as e:
            self.log_result("Dependencies", False, f"Dependency test failed: {e}")
            return False

        return True

    def test_file_structure(self) -> bool:
        """Test project file structure."""
        print("\n📁 Testing File Structure...")

        required_files = [
            "main.py",
            "requirements.txt",
            ".env",
            "database/__init__.py",
            "database/config.py",
            "database/connection.py",
            "database/models/__init__.py",
            "database/models/user.py",
            "database/models/portfolio.py",
            "database/models/asset.py",
            "database/models/transaction.py",
            "database/utils.py",
            "alembic.ini",
            "alembic/env.py",
            "setup_database.sh",
            "setup_environment.sh",
        ]

        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)

        if missing_files:
            self.log_result("File Structure", False, f"Missing files: {missing_files}")
            return False
        else:
            self.log_result("File Structure", True, "All required files present")

        return True

    def run_all_tests(self) -> bool:
        """Run all tests."""
        print("🚀 Starting Portfolia Comprehensive Testing...")
        print("=" * 60)

        tests = [
            ("Environment Setup", self.test_environment_setup),
            ("File Structure", self.test_file_structure),
            ("Dependencies", self.test_dependencies),
            ("Database Models", self.test_database_models),
            ("Database Connection", self.test_database_connection),
            ("Database Utilities", self.test_database_utilities),
            ("API Structure", self.test_api_structure),
            ("API Endpoints", self.test_api_endpoints),
        ]

        for test_name, test_func in tests:
            try:
                success = test_func()
                if not success:
                    self.log_error(f"Test '{test_name}' failed")
            except Exception as e:
                self.log_error(f"Test '{test_name}' crashed: {e}")
                self.results[test_name] = {
                    "success": False,
                    "message": f"Test crashed: {e}",
                    "details": None,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                }

        return self.print_summary()


def main():
    """Main test runner."""
    tester = PortfoliaTester()

    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Testing failed with unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
