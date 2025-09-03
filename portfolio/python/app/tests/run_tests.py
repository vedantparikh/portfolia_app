#!/usr/bin/env python3
"""
Test runner for polars-based technical indicators.
Compares results with the ta package to ensure accuracy.
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_all_tests():
    """Run all test suites."""
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern="test_*.py")

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


def run_specific_test(test_name):
    """Run a specific test suite."""
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))

    # Map test names to test modules
    test_modules = {
        "momentum": "test_momentum_indicators",
        "trend": "test_trend_indicators",
        "volatility": "test_volatility_indicators",
        "volume": "test_volume_indicators",
        "market": "test_market_stock",
        "macd_strategy": "test_macd_strategy",
        "gfs_strategy": "test_gfs_strategy",
        "trading_strategies": "test_macd_strategy,test_gfs_strategy",
    }

    if test_name not in test_modules:
        print(f"Unknown test suite: {test_name}")
        print(f"Available test suites: {', '.join(test_modules.keys())}")
        return 1

    if test_name == "trading_strategies":
        # Run both trading strategy test files
        suite = unittest.TestSuite()
        for module_name in test_modules[test_name].split(","):
            try:
                module = __import__(module_name)
                suite.addTests(loader.loadTestsFromModule(module))
            except ImportError as e:
                print(f"Could not import {module_name}: {e}")
                return 1
    else:
        try:
            module = __import__(test_modules[test_name])
            suite = loader.loadTestsFromModule(module)
        except ImportError as e:
            print(f"Could not import {test_modules[test_name]}: {e}")
            return 1

    # Run the specific test suite
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test suite
        test_suite = sys.argv[1]
        exit_code = run_specific_test(test_suite)
    else:
        # Run all tests
        print("Running all test suites...")
        exit_code = run_all_tests()

    sys.exit(exit_code)
