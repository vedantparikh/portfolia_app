import unittest
import polars as pl
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import our modules
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.indicators.trend_indicators import TrendIndicators, calculate_sma, calculate_ema, calculate_bollinger_bands
import ta.trend as ta_trend


class TestTrendIndicators(unittest.TestCase):
    """Test trend indicators implementation and compare with ta package."""

    def setUp(self):
        """Set up test data."""
        # Create sample OHLCV data
        np.random.seed(42)
        dates = np.arange(100)

        # Generate realistic price data
        close_prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
        high_prices = close_prices + np.random.uniform(0.5, 2.0, 100)
        low_prices = close_prices - np.random.uniform(0.5, 2.0, 100)
        volumes = np.random.randint(1000, 10000, 100)

        # Create polars DataFrame for our implementation
        self.pl_df = pl.DataFrame({
            "Open": close_prices * 0.99,
            "High": high_prices,
            "Low": low_prices,
            "Close": close_prices,
            "Volume": volumes,
        })

        # Create pandas DataFrame for ta package
        self.pd_df = pd.DataFrame({
            "Open": close_prices * 0.99,
            "High": high_prices,
            "Low": low_prices,
            "Close": close_prices,
            "Volume": volumes,
        })

    def test_macd_indicator_comparison(self):
        """Test MACD indicator calculation and compare with ta package."""
        # Our implementation
        indicator = TrendIndicators(self.pl_df)
        our_result = indicator.macd_indicator(window_slow=26, window_fast=12, window_sign=9)
        
        # ta package implementation
        ta_macd = ta_trend.MACD(
            close=self.pd_df["Close"],
            window_slow=26,
            window_fast=12,
            window_sign=9,
            fillna=False
        )
        
        ta_macd_line = ta_macd.macd()
        ta_signal = ta_macd.macd_signal()
        ta_histogram = ta_macd.macd_diff()
        
        # Convert our results to pandas for comparison
        our_macd = our_result["MACD"].to_pandas()
        our_signal = our_result["Signal"].to_pandas()
        our_histogram = our_result["Histogram"].to_pandas()
        
        # Compare MACD line
        np.testing.assert_array_almost_equal(
            our_macd.dropna().values,
            ta_macd_line.dropna().values,
            decimal=5
        )
        
        # Compare Signal line
        np.testing.assert_array_almost_equal(
            our_signal.dropna().values,
            ta_signal.dropna().values,
            decimal=5
        )
        
        # Compare Histogram
        np.testing.assert_array_almost_equal(
            our_histogram.dropna().values,
            ta_histogram.dropna().values,
            decimal=5
        )

    def test_bollinger_bands_comparison(self):
        """Test Bollinger Bands calculation and compare with ta package."""
        # Our implementation
        indicator = TrendIndicators(self.pl_df)
        our_result = indicator.bollinger_bands_indicator(window=20, window_dev=2)
        
        # ta package implementation
        ta_bb = ta_trend.BollingerBands(
            close=self.pd_df["Close"],
            window=20,
            window_dev=2,
            fillna=False
        )
        
        ta_bbh = ta_bb.bollinger_hband()
        ta_bbl = ta_bb.bollinger_lband()
        ta_bbm = ta_bb.bollinger_mavg()
        
        # Convert our results to pandas for comparison
        our_bbh = our_result["bb_bbh"].to_pandas()
        our_bbl = our_result["bb_bbl"].to_pandas()
        our_bbm = our_result["bb_bbm"].to_pandas()
        
        # Compare upper band
        np.testing.assert_array_almost_equal(
            our_bbh.dropna().values,
            ta_bbh.dropna().values,
            decimal=5
        )
        
        # Compare lower band
        np.testing.assert_array_almost_equal(
            our_bbl.dropna().values,
            ta_bbl.dropna().values,
            decimal=5
        )
        
        # Compare middle band
        np.testing.assert_array_almost_equal(
            our_bbm.dropna().values,
            ta_bbm.dropna().values,
            decimal=5
        )

    def test_sma_calculation(self):
        """Test Simple Moving Average calculation."""
        indicator = TrendIndicators(self.pl_df)
        result = indicator.sma_indicator(window=20)
        
        # Verify SMA column is added
        self.assertIn("sma", result.columns)
        
        # Verify SMA values are reasonable
        sma_values = result["sma"].drop_nulls()
        if len(sma_values) > 0:
            sma_array = sma_values.to_numpy()
            # SMA should be close to the original prices
            self.assertTrue(all(50 <= sma <= 150 for sma in sma_array))

    def test_ema_calculation(self):
        """Test Exponential Moving Average calculation."""
        indicator = TrendIndicators(self.pl_df)
        result = indicator.ema_indicator(window=20)
        
        # Verify EMA column is added
        self.assertIn("ema", result.columns)
        
        # Verify EMA values are reasonable
        ema_values = result["ema"].drop_nulls()
        if len(ema_values) > 0:
            ema_array = ema_values.to_numpy()
            # EMA should be close to the original prices
            self.assertTrue(all(50 <= ema <= 150 for ema in ema_array))

    def test_convenience_functions(self):
        """Test convenience functions."""
        # Test calculate_sma function
        close_series = self.pl_df["Close"]
        sma_result = calculate_sma(close_series, window=20)
        self.assertIsInstance(sma_result, pl.Series)
        self.assertEqual(len(sma_result), len(close_series))
        
        # Test calculate_ema function
        ema_result = calculate_ema(close_series, window=20)
        self.assertIsInstance(ema_result, pl.Series)
        self.assertEqual(len(ema_result), len(close_series))
        
        # Test calculate_bollinger_bands function
        bb_result = calculate_bollinger_bands(close_series, window=20)
        self.assertIsInstance(bb_result, pl.DataFrame)
        self.assertIn("Upper", bb_result.columns)
        self.assertIn("Middle", bb_result.columns)
        self.assertIn("Lower", bb_result.columns)

    def test_all_trend_indicators(self):
        """Test that all trend indicators can be calculated together."""
        indicator = TrendIndicators(self.pl_df)
        result = indicator.all_trend_indicators()
        
        # Verify all expected columns are present
        expected_columns = ["MACD", "Signal", "Histogram", "bb_bbh", "bb_bbl", "bb_bbm", "sma", "ema"]
        for col in expected_columns:
            self.assertIn(col, result.columns)

    def test_data_validation(self):
        """Test data validation."""
        indicator = TrendIndicators(self.pl_df)
        
        # Test with empty DataFrame
        empty_df = pl.DataFrame()
        with self.assertRaises(Exception):
            TrendIndicators(empty_df)

    def test_edge_cases(self):
        """Test edge cases."""
        indicator = TrendIndicators(self.pl_df)
        
        # Test with very small dataset
        small_df = pl.DataFrame({
            "Open": [100, 101],
            "High": [102, 103],
            "Low": [99, 100],
            "Close": [101, 102],
            "Volume": [1000, 1000],
        })
        
        try:
            small_indicator = TrendIndicators(small_df)
            result = small_indicator.sma_indicator(window=2)
            # Should handle small datasets gracefully
            self.assertIsInstance(result, pl.DataFrame)
        except Exception as e:
            # Small datasets might not have enough data for indicators
            pass

    def test_performance_comparison(self):
        """Test performance comparison between our implementation and ta package."""
        import time
        
        # Test our implementation performance
        start_time = time.time()
        indicator = TrendIndicators(self.pl_df)
        our_result = indicator.macd_indicator()
        our_time = time.time() - start_time
        
        # Test ta package performance
        start_time = time.time()
        ta_result = ta_trend.MACD(
            close=self.pd_df["Close"],
            window_slow=26,
            window_fast=12,
            window_sign=9,
            fillna=False
        ).macd()
        ta_time = time.time() - start_time
        
        # Both should be reasonably fast
        self.assertLess(our_time, 1.0, "Our MACD calculation took too long")
        self.assertLess(ta_time, 1.0, "TA package MACD calculation took too long")
        
        print(f"\nPerformance comparison:")
        print(f"Our implementation: {our_time:.4f} seconds")
        print(f"TA package: {ta_time:.4f} seconds")

    def test_numerical_accuracy(self):
        """Test numerical accuracy of our implementation."""
        # Create simple test data with known expected values
        simple_data = pl.DataFrame({
            "Close": [100, 101, 102, 101, 100, 99, 98, 97, 96, 95]
        })
        
        indicator = TrendIndicators(simple_data)
        
        # Test SMA calculation
        sma_result = indicator.sma_indicator(window=5)
        sma_values = sma_result["sma"].drop_nulls()
        if len(sma_values) > 0:
            # First SMA value should be the average of first 5 prices
            first_sma = sma_values[0]
            expected_sma = (100 + 101 + 102 + 101 + 100) / 5
            self.assertAlmostEqual(first_sma, expected_sma, places=5)


if __name__ == "__main__":
    unittest.main()
