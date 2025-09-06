#!/usr/bin/env python3
"""
Integration Test Runner for Portfolia API

This script runs all integration tests for the API endpoints.
Usage: python run_integration_tests.py
"""

import os
import subprocess
import sys
from pathlib import Path


def main():
    """Run integration tests."""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    print("🧪 Portfolia API Integration Test Runner")
    print("=" * 50)

    # Check if we're in the right directory
    if not (project_root / "app").exists():
        print(
            "❌ Error: Please run this script from the portfolio/python/app directory"
        )
        print(f"   Current directory: {os.getcwd()}")
        print(f"   Expected to find: {project_root / 'app'}")
        sys.exit(1)

    # Check if pytest is available
    try:
        import pytest

        print(f"✅ pytest version: {pytest.__version__}")
    except ImportError:
        print("❌ Error: pytest is not installed")
        print("   Install with: pip install pytest")
        sys.exit(1)

    # Check if FastAPI test client is available
    try:
        from fastapi.testclient import TestClient

        print("✅ FastAPI TestClient available")
    except ImportError:
        print("❌ Error: FastAPI TestClient is not available")
        print("   Install with: pip install httpx")
        sys.exit(1)

    print("\n🚀 Starting Integration Tests...")
    print("-" * 50)

    # Run the tests
    test_file = script_dir / "integration" / "test_api_endpoints.py"

    if not test_file.exists():
        print(f"❌ Error: Test file not found: {test_file}")
        sys.exit(1)

    # Run pytest with verbose output
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(test_file),
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--color=yes",  # Colored output
        "-s",  # Show print statements
    ]

    print(f"Running: {' '.join(cmd)}")
    print()

    try:
        result = subprocess.run(cmd, cwd=project_root, check=False)

        print("\n" + "=" * 50)
        if result.returncode == 0:
            print("🎉 All integration tests passed!")
        else:
            print(f"❌ Some tests failed (exit code: {result.returncode})")

        return result.returncode

    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
