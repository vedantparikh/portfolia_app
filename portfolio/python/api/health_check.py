#!/usr/bin/env python3
"""
Quick health check script for Portfolia application.
This script provides a simple way to check the health of all components.
"""

import sys
import time
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))


def check_environment():
    """Check environment configuration."""
    print("🔧 Environment Configuration:")

    try:
        from database.config import db_settings

        print(f"   ✅ Database URL: {db_settings.postgres_url}")
        print(f"   ✅ API Host: {db_settings.API_HOST}")
        print(f"   ✅ API Port: {db_settings.API_PORT}")
        print(f"   ✅ Redis Host: {db_settings.REDIS_HOST}")
        return True
    except Exception as e:
        print(f"   ❌ Environment Error: {e}")
        return False


def check_database():
    """Check database connectivity."""
    print("\n🗄️  Database Connectivity:")

    try:
        from database.connection import health_check, redis_health_check

        # Check PostgreSQL
        db_health = health_check()
        if db_health:
            print("   ✅ PostgreSQL: Connected")
        else:
            print("   ❌ PostgreSQL: Connection failed")
            return False

        # Check Redis
        redis_health = redis_health_check()
        if redis_health:
            print("   ✅ Redis: Connected")
        else:
            print("   ⚠️  Redis: Connection failed (optional)")

        return True
    except Exception as e:
        print(f"   ❌ Database Error: {e}")
        return False


def check_api():
    """Check API functionality."""
    print("\n🌐 API Functionality:")

    try:
        from main import app

        # Check routes
        routes = [route.path for route in app.routes]
        health_routes = [r for r in routes if "health" in r]

        if health_routes:
            print(f"   ✅ Health Routes: {health_routes}")
        else:
            print("   ❌ Health Routes: Not found")
            return False

        # Check OpenAPI
        if hasattr(app, "openapi"):
            print("   ✅ OpenAPI Schema: Available")
        else:
            print("   ❌ OpenAPI Schema: Not available")
            return False

        return True
    except Exception as e:
        print(f"   ❌ API Error: {e}")
        return False


def check_models():
    """Check database models."""
    print("\n🏗️  Database Models:")

    try:
        from database.models import User, Portfolio, Asset, Transaction, ManualEntry

        models = [User, Portfolio, Asset, Transaction, ManualEntry]
        for model in models:
            if model and hasattr(model, "__tablename__"):
                print(f"   ✅ {model.__name__}: {model.__tablename__}")
            else:
                print(f"   ❌ {model.__name__}: Invalid model")
                return False

        return True
    except Exception as e:
        print(f"   ❌ Models Error: {e}")
        return False


def main():
    """Run all health checks."""
    print("🏥 Portfolia Health Check")
    print("=" * 40)

    checks = [
        ("Environment", check_environment),
        ("Database", check_database),
        ("API", check_api),
        ("Models", check_models),
    ]

    results = []
    for check_name, check_func in checks:
        try:
            success = check_func()
            results.append((check_name, success))
        except Exception as e:
            print(f"   ❌ {check_name} check crashed: {e}")
            results.append((check_name, False))

    # Summary
    print("\n" + "=" * 40)
    print("📊 Health Check Summary:")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for check_name, success in results:
        status = "✅" if success else "❌"
        print(f"   {status} {check_name}")

    print(f"\nOverall: {passed}/{total} checks passed")

    if passed == total:
        print("🎉 All systems are healthy!")
        return 0
    else:
        print("⚠️  Some systems have issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())
