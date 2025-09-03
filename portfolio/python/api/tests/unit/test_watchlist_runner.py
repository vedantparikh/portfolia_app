#!/usr/bin/env python3
"""
Test runner for watchlist service tests.

This script runs the watchlist service tests with proper setup and reporting.
"""

import os
import sys
from pathlib import Path

import pytest

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Set testing environment
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["FORCE_SQLITE"] = "true"


def run_watchlist_tests():
    """Run watchlist service tests with detailed output."""
    print("🧪 Running Watchlist Service Tests...")
    print("=" * 50)

    # Test file path
    test_file = Path(__file__).parent / "test_watchlist_service.py"

    # Run tests with verbose output
    result = pytest.main(
        [
            str(test_file),
            "-v",  # Verbose output
            "--tb=short",  # Short traceback format
            "--color=yes",  # Colored output
            "--durations=10",  # Show 10 slowest tests
            "-x",  # Stop on first failure
        ]
    )

    if result == 0:
        print("\n✅ All watchlist tests passed!")
    else:
        print("\n❌ Some watchlist tests failed!")

    return result


if __name__ == "__main__":
    exit_code = run_watchlist_tests()
    sys.exit(exit_code)
