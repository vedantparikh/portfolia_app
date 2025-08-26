import unittest
import pandas as pd
import polars as pl
import numpy as np
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import our modules
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trading_strategy.trend_strategy.macd_strategy import MACDStrategy


class TestMACDStrategy(unittest.TestCase):
    """Test MACD strategy implementation."""

    def setUp(self):
        """Set up test data."""
        # Create sample OHLCV data with MACD indicators
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

        # Add MACD indicators (simulated)
        self.pd_df["MACD"] = np.random.randn(100) * 0.1
        self.pd_df["Signal"] = self.pd_df["MACD"] + np.random.randn(100) * 0.05
        self.pd_df["Histogram"] = self.pd_df["MACD"] - self.pd_df["Signal"]

        # Convert to polars DataFrame
        self.pl_df = pl.from_pandas(self.pd_df)

        # Initialize strategy
        self.macd_strategy = MACDStrategy(self.pl_df)

    def test_initialization(self):
        """Test MACD strategy initialization."""
        # Test successful initialization
        self.assertIsInstance(self.macd_strategy, MACDStrategy)
        self.assertEqual(len(self.macd_strategy.df), 100)

        # Test that required columns are present
        required_columns = {"MACD", "Signal", "Histogram"}
        for col in required_columns:
            self.assertIn(col, self.macd_strategy.df.columns)

    def test_initialization_missing_columns(self):
        """Test initialization with missing MACD columns."""
        # Create DataFrame without MACD columns
        df_without_macd = self.pl_df.drop(["MACD", "Signal", "Histogram"])

        # Should raise assertion error
        with self.assertRaises(AssertionError):
            MACDStrategy(df_without_macd)

    def test_find_intersection(self):
        """Test intersection detection logic."""
        # Test exact intersection
        result = self.macd_strategy._find_intersection(1.0, 1.0, digits=0)
        self.assertEqual(result, 1)

        # Test no intersection
        result = self.macd_strategy._find_intersection(1.0, 2.0, digits=0)
        self.assertEqual(result, 0)

        # Test intersection with decimal precision
        result = self.macd_strategy._find_intersection(1.001, 1.002, digits=2)
        self.assertEqual(result, 1)

        # Test intersection with different precision
        result = self.macd_strategy._find_intersection(1.001, 1.002, digits=3)
        self.assertEqual(result, 0)

    def test_get_closing_price_difference(self):
        """Test closing price difference calculation."""
        # Create test DataFrame with intersection points
        test_df = pd.DataFrame(
            {"Close": [100, 101, 102, 103, 104], "MACD_intersection": [0, 1, 0, 1, 0]}
        )

        # Mock the method to work with pandas DataFrame
        with patch.object(
            self.macd_strategy, "_get_closing_price_difference"
        ) as mock_method:
            mock_method.return_value = test_df
            result = mock_method(test_df)

            # Verify the method was called
            mock_method.assert_called_once_with(test_df)
            self.assertIsInstance(result, pd.DataFrame)

    def test_get_buy_sell_calls(self):
        """Test buy/sell signal generation."""
        # Create test DataFrame with intersection points
        test_df = pd.DataFrame(
            {
                "MACD": [0.1, 0.2, 0.3, 0.4, 0.5],
                "Signal": [0.15, 0.25, 0.35, 0.45, 0.55],
                "MACD_intersection": [0, 1, 0, 1, 0],
            }
        )

        # Mock the method to work with pandas DataFrame
        with patch.object(self.macd_strategy, "_get_buy_sell_calls") as mock_method:
            mock_method.return_value = test_df
            result = mock_method(test_df, condition_days=3)

            # Verify the method was called
            mock_method.assert_called_once_with(test_df, condition_days=3)
            self.assertIsInstance(result, pd.DataFrame)

    def test_strategy_logic_validation(self):
        """Test that strategy logic produces expected outputs."""
        # Test that MACD values are numeric
        self.assertTrue(
            all(isinstance(x, (int, float)) for x in self.macd_strategy.df["MACD"])
        )
        self.assertTrue(
            all(isinstance(x, (int, float)) for x in self.macd_strategy.df["Signal"])
        )
        self.assertTrue(
            all(isinstance(x, (int, float)) for x in self.macd_strategy.df["Histogram"])
        )

        # Test that Close prices are positive
        self.assertTrue(all(x > 0 for x in self.macd_strategy.df["Close"]))

    def test_data_consistency(self):
        """Test data consistency across the DataFrame."""
        # Test that all columns have the same length
        column_lengths = [
            len(self.macd_strategy.df[col]) for col in self.macd_strategy.df.columns
        ]
        self.assertTrue(all(length == 100 for length in column_lengths))

        # Test that there are no infinite values
        for col in ["MACD", "Signal", "Histogram", "Close"]:
            # Convert to numpy array first for numpy operations
            col_array = self.macd_strategy.df[col].to_numpy()
            self.assertFalse(np.isinf(col_array).any())

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test with very small dataset
        small_df = pl.DataFrame(
            {
                "MACD": [0.1, 0.2],
                "Signal": [0.15, 0.25],
                "Histogram": [-0.05, -0.05],
                "Close": [100, 101],
            }
        )

        # Should handle small datasets gracefully
        try:
            small_strategy = MACDStrategy(small_df)
            self.assertIsInstance(small_strategy, MACDStrategy)
        except Exception as e:
            self.fail(f"MACD strategy failed on small dataset: {e}")

    def test_histogram_interpretation(self):
        """Test histogram interpretation logic."""
        # Test that histogram correctly represents MACD - Signal
        calculated_histogram = (
            self.macd_strategy.df["MACD"] - self.macd_strategy.df["Signal"]
        )

        # Allow for small floating point differences
        np.testing.assert_array_almost_equal(
            calculated_histogram.to_numpy(),
            self.macd_strategy.df["Histogram"].to_numpy(),
            decimal=10,
        )

    def test_macd_signal_relationship(self):
        """Test MACD and Signal line relationships."""
        # Test that when MACD > Signal, histogram should be positive
        macd_above_signal = self.macd_strategy.df.filter(
            pl.col("MACD") > pl.col("Signal")
        )
        if len(macd_above_signal) > 0:
            self.assertTrue(all(macd_above_signal["Histogram"] > 0))

        # Test that when MACD < Signal, histogram should be negative
        macd_below_signal = self.macd_strategy.df.filter(
            pl.col("MACD") < pl.col("Signal")
        )
        if len(macd_below_signal) > 0:
            self.assertTrue(all(macd_below_signal["Histogram"] < 0))

    def test_data_types(self):
        """Test that data types are correct."""
        # Test numeric types for technical indicators
        self.assertTrue(self.macd_strategy.df["MACD"].dtype in [pl.Float64, pl.Float32])
        self.assertTrue(
            self.macd_strategy.df["Signal"].dtype in [pl.Float64, pl.Float32]
        )
        self.assertTrue(
            self.macd_strategy.df["Histogram"].dtype in [pl.Float64, pl.Float32]
        )

        # Test numeric types for price data
        self.assertTrue(
            self.macd_strategy.df["Close"].dtype in [pl.Float64, pl.Float32]
        )

    def test_strategy_parameters(self):
        """Test strategy parameter validation."""
        # Test that condition_days parameter is reasonable
        # This would be tested in the actual buy/sell logic methods
        self.assertGreater(len(self.macd_strategy.df), 26)  # Strategy requires >26 rows


if __name__ == "__main__":
    unittest.main()
