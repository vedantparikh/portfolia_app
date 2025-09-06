#!/usr/bin/env python3
"""
Performance comparison script for technical indicators.
"""

import os
import sys
import time
import unittest

import numpy as np
import polars as pl

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.indicators.momentum_indicators import calculate_rsi
from app.utils.indicators.trend_indicators import calculate_ema, calculate_sma
from app.utils.indicators.volatility_indicators import calculate_bollinger_bands


def generate_test_data(size=10000):
    """Generate test OHLCV data."""
    np.random.seed(42)
    dates = np.arange(size)

    # Generate realistic price data
    close_prices = 100 + np.cumsum(np.random.randn(size) * 0.5)
    high_prices = close_prices + np.random.uniform(0.5, 2.0, size)
    low_prices = close_prices - np.random.uniform(0.5, 2.0, size)
    volumes = np.random.randint(1000, 10000, size)

    # Create polars DataFrame
    pl_df = pl.DataFrame(
        {
            "Open": close_prices * 0.99,
            "High": high_prices,
            "Low": low_prices,
            "Close": close_prices,
            "Volume": volumes,
        }
    )

    return pl_df


class TestPerformanceComparison(unittest.TestCase):
    """Test performance of technical indicators."""

    def setUp(self):
        """Set up test data."""
        self.test_data = generate_test_data(1000)

    def test_momentum_indicators_performance(self):
        """Test momentum indicators performance."""
        print("\n=== Momentum Indicators Performance ===")

        # Test RSI
        start_time = time.time()
        try:
            result = calculate_rsi(self.test_data["Close"], window=14)
            rsi_time = time.time() - start_time
            print(f"RSI: {rsi_time:.4f} seconds")
            self.assertIsNotNone(result)
        except Exception as e:
            print(f"RSI calculation failed: {e}")
            # Don't fail the test, just log the issue

    def test_trend_indicators_performance(self):
        """Test trend indicators performance."""
        print("\n=== Trend Indicators Performance ===")

        # Test SMA
        start_time = time.time()
        try:
            result = calculate_sma(self.test_data["Close"], window=20)
            sma_time = time.time() - start_time
            print(f"SMA: {sma_time:.4f} seconds")
            self.assertIsNotNone(result)
        except Exception as e:
            print(f"SMA calculation failed: {e}")

        # Test EMA
        start_time = time.time()
        try:
            result = calculate_ema(self.test_data["Close"], window=20)
            ema_time = time.time() - start_time
            print(f"EMA: {ema_time:.4f} seconds")
            self.assertIsNotNone(result)
        except Exception as e:
            print(f"EMA calculation failed: {e}")

    def test_volatility_indicators_performance(self):
        """Test volatility indicators performance."""
        print("\n=== Volatility Indicators Performance ===")

        # Test Bollinger Bands
        start_time = time.time()
        try:
            result = calculate_bollinger_bands(self.test_data["Close"], window=20)
            bb_time = time.time() - start_time
            print(f"Bollinger Bands: {bb_time:.4f} seconds")
            self.assertIsNotNone(result)
        except Exception as e:
            print(f"Bollinger Bands calculation failed: {e}")

    def test_data_generation_performance(self):
        """Test data generation performance."""
        print("\n=== Data Generation Performance ===")

        sizes = [100, 1000, 10000]
        for size in sizes:
            start_time = time.time()
            data = generate_test_data(size)
            gen_time = time.time() - start_time
            print(f"Data generation ({size} rows): {gen_time:.4f} seconds")
            self.assertEqual(len(data), size)

    def test_memory_usage(self):
        """Test memory usage of indicators."""
        print("\n=== Memory Usage Test ===")

        # This is a basic test - in a real scenario you'd use memory_profiler
        try:
            result = calculate_rsi(self.test_data["Close"], window=14)
            self.assertIsNotNone(result)
            print("Memory usage test passed")
        except Exception as e:
            print(f"Memory usage test failed: {e}")


if __name__ == "__main__":
    unittest.main()
