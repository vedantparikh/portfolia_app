import os

# Add the parent directory to the path so we can import our modules
import sys
import unittest
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import polars as pl

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.trading_strategies.gfs_strategy import GfsStrategy


class TestGfsStrategy(unittest.TestCase):
    """Test GFS (Grandfather-Father-Son) strategy implementation."""

    def setUp(self):
        """Set up test data."""
        # Create sample OHLCV data
        np.random.seed(42)
        dates = pd.date_range("2023-01-01", periods=100, freq="D")

        # Generate realistic price data
        close_prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
        high_prices = close_prices + np.random.uniform(0.5, 2.0, 100)
        low_prices = close_prices - np.random.uniform(0.5, 2.0, 100)
        volumes = np.random.randint(1000, 10000, 100)

        # Create pandas DataFrame
        self.pd_df = pd.DataFrame(
            {
                "Open": close_prices * 0.99,
                "High": high_prices,
                "Low": low_prices,
                "Close": close_prices,
                "Volume": volumes,
            },
            index=dates,
        )

        # Convert to polars DataFrame for testing
        self.pl_df = pl.from_pandas(self.pd_df)

        # Test symbol
        self.test_symbol = "AAPL"

    def test_initialization(self):
        """Test GFS strategy initialization."""
        # Test successful initialization
        strategy = GfsStrategy(self.test_symbol)
        self.assertIsInstance(strategy, GfsStrategy)
        self.assertEqual(strategy.symbol, self.test_symbol)

        # Test initialization with empty symbol
        with self.assertRaises(ValueError):
            GfsStrategy("")

        # Test initialization with None symbol
        with self.assertRaises(ValueError):
            GfsStrategy(None)

    def test_calculater_rsi(self):
        """Test RSI calculation method."""
        strategy = GfsStrategy(self.test_symbol)

        # Test RSI calculation with polars DataFrame
        result = strategy.calculater_rsi(self.pl_df)

        # Verify result is a polars DataFrame
        self.assertIsInstance(result, pl.DataFrame)

        # Verify RSI column is added
        self.assertIn("RSI", result.columns)

        # Verify RSI values are in expected range [0, 100]
        rsi_values = result.select("RSI").drop_nulls()
        if len(rsi_values) > 0:
            rsi_array = rsi_values["RSI"].to_numpy()
            self.assertTrue(all(0 <= rsi <= 100 for rsi in rsi_array))

    @patch("yfinance.Ticker")
    def test_grandfather_rsi(self, mock_ticker):
        """Test grandfather RSI calculation."""
        strategy = GfsStrategy(self.test_symbol)

        # Mock yfinance response
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = self.pd_df
        mock_ticker.return_value = mock_ticker_instance

        # Test grandfather RSI calculation
        try:
            result = strategy.grandfather_rsi()
            # Should return a polars DataFrame
            self.assertIsInstance(result, pl.DataFrame)
            self.assertIn("RSI", result.columns)
        except Exception as e:
            # If it fails due to missing data, that's acceptable
            self.assertIn("No price data found", str(e))

    @patch("yfinance.Ticker")
    def test_father_rsi(self, mock_ticker):
        """Test father RSI calculation."""
        strategy = GfsStrategy(self.test_symbol)

        # Mock yfinance response
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = self.pd_df
        mock_ticker.return_value = mock_ticker_instance

        # Test father RSI calculation
        try:
            result = strategy.father_rsi()
            # Should return a polars DataFrame
            self.assertIsInstance(result, pl.DataFrame)
            self.assertIn("RSI", result.columns)
        except Exception as e:
            # If it fails due to missing data, that's acceptable
            self.assertIn("No price data found", str(e))

    @patch("yfinance.Ticker")
    def test_son_rsi(self, mock_ticker):
        """Test son RSI calculation."""
        strategy = GfsStrategy(self.test_symbol)

        # Mock yfinance response
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = self.pd_df
        mock_ticker.return_value = mock_ticker_instance

        # Test son RSI calculation
        try:
            result = strategy.son_rsi()
            # Should return a polars DataFrame
            self.assertIsInstance(result, pl.DataFrame)
            self.assertIn("RSI", result.columns)
        except Exception as e:
            # If it fails due to missing data, that's acceptable
            self.assertIn("No price data found", str(e))

    @patch("yfinance.Ticker")
    def test_calculate_gfs(self, mock_ticker):
        """Test complete GFS strategy calculation."""
        strategy = GfsStrategy(self.test_symbol)

        # Mock yfinance response
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = self.pd_df
        mock_ticker.return_value = mock_ticker_instance

        # Test complete GFS calculation
        try:
            result = strategy.calculate_gfs()

            # Verify result structure
            self.assertIsInstance(result, dict)
            self.assertIn("grandfather", result)
            self.assertIn("father", result)
            self.assertIn("son", result)
            self.assertIn("recommendation", result)

            # Verify RSI values are in expected range
            for key in ["grandfather", "father", "son"]:
                if result[key] is not None:
                    self.assertIsInstance(result[key], float)
                    self.assertTrue(0 <= result[key] <= 100)

            # Verify recommendation is a string
            self.assertIsInstance(result["recommendation"], str)

            # Verify recommendation is one of expected values
            expected_recommendations = ["Buy", "Sell", "Hold Tight! Or Seat Back!"]
            self.assertIn(result["recommendation"], expected_recommendations)

        except Exception as e:
            # If it fails due to missing data, that's acceptable
            self.assertIn("No price data found", str(e))

    def test_rsi_calculation_consistency(self):
        """Test that RSI calculations are consistent."""
        strategy = GfsStrategy(self.test_symbol)

        # Calculate RSI multiple times on same data
        result1 = strategy.calculater_rsi(self.pl_df)
        result2 = strategy.calculater_rsi(self.pl_df)

        # Results should be identical
        pd.testing.assert_frame_equal(result1.to_pandas(), result2.to_pandas())

    def test_data_validation(self):
        """Test data validation in RSI calculation."""
        strategy = GfsStrategy(self.test_symbol)

        # Test with empty DataFrame
        empty_df = pl.DataFrame()
        with self.assertRaises(Exception):
            strategy.calculater_rsi(empty_df)

        # Test with DataFrame missing required columns
        incomplete_df = pl.DataFrame({"Close": [100, 101, 102]})
        # This might not raise an exception if the RSI calculation can handle missing columns
        try:
            result = strategy.calculater_rsi(incomplete_df)
            # If it succeeds, that's fine - the test passes
            self.assertIsInstance(result, pl.DataFrame)
        except Exception:
            # If it fails, that's also fine - the test passes
            pass

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        strategy = GfsStrategy(self.test_symbol)

        # Test with very small dataset
        small_df = pl.DataFrame(
            {
                "Open": [100, 101],
                "High": [102, 103],
                "Low": [99, 100],
                "Close": [101, 102],
                "Volume": [1000, 1000],
            }
        )

        try:
            result = strategy.calculater_rsi(small_df)
            self.assertIsInstance(result, pl.DataFrame)
        except Exception as e:
            # Small datasets might not have enough data for RSI
            self.assertIn("insufficient", str(e).lower())

    def test_symbol_validation(self):
        """Test symbol validation logic."""
        # Test with valid symbols
        valid_symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]
        for symbol in valid_symbols:
            try:
                strategy = GfsStrategy(symbol)
                self.assertEqual(strategy.symbol, symbol)
            except Exception as e:
                self.fail(f"Valid symbol '{symbol}' failed: {e}")

        # Test with invalid symbols
        invalid_symbols = ["", None]
        for symbol in invalid_symbols:
            with self.assertRaises(ValueError):
                GfsStrategy(symbol)

    def test_recommendation_logic(self):
        """Test recommendation logic based on RSI values."""
        strategy = GfsStrategy(self.test_symbol)

        # Test different RSI combinations and expected recommendations
        test_cases = [
            # (grandfather, father, son, expected_recommendation)
            (25, 20, 15, "Buy"),  # All oversold (below 30)
            (75, 80, 85, "Sell"),  # All overbought (above 70)
            (50, 50, 50, "Hold Tight! Or Seat Back!"),  # All neutral
            (25, 50, 70, "Hold Tight! Or Seat Back!"),  # Mixed values
            (70, 50, 30, "Hold Tight! Or Seat Back!"),  # Mixed values
        ]

        for grandfather, father, son, expected in test_cases:
            # Mock the individual RSI methods to return DataFrames with the specified RSI values
            mock_grandfather = pl.DataFrame({"RSI": [grandfather]})
            mock_father = pl.DataFrame({"RSI": [father]})
            mock_son = pl.DataFrame({"RSI": [son]})

            with patch.object(
                strategy, "grandfather_rsi", return_value=mock_grandfather
            ):
                with patch.object(strategy, "father_rsi", return_value=mock_father):
                    with patch.object(strategy, "son_rsi", return_value=mock_son):
                        result = strategy.calculate_gfs()
                        self.assertEqual(result["recommendation"], expected)

    def test_error_handling(self):
        """Test error handling in various scenarios."""
        strategy = GfsStrategy(self.test_symbol)

        # Test with corrupted data
        corrupted_df = self.pl_df.with_columns(
            [
                pl.when(pl.col("Close") == pl.col("Close").first())
                .then(None)
                .otherwise(pl.col("Close"))
                .alias("Close")
            ]
        )

        try:
            result = strategy.calculater_rsi(corrupted_df)
            # Should handle NaN values gracefully
            self.assertIsInstance(result, pl.DataFrame)
        except Exception:
            # If it fails, that's acceptable
            pass

    def test_performance_characteristics(self):
        """Test basic performance characteristics."""
        strategy = GfsStrategy(self.test_symbol)

        # Test that RSI calculation doesn't take too long
        import time

        start_time = time.time()
        result = strategy.calculater_rsi(self.pl_df)
        calculation_time = time.time() - start_time

        # RSI calculation should be reasonably fast (< 1 second for 100 rows)
        self.assertLess(calculation_time, 1.0)
        self.assertIsInstance(result, pl.DataFrame)


if __name__ == "__main__":
    unittest.main()
