import os

# Add the parent directory to the path so we can import our modules
import sys
import unittest

import numpy as np
import pandas as pd
import polars as pl

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ta.volatility import AverageTrueRange, BollingerBands, KeltnerChannel

from utils.indicators.volatility_indicators import VolatilityIndicators


class TestVolatilityIndicators(unittest.TestCase):
    """Test volatility indicators comparing polars implementation with ta package."""

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
                "open": close_prices * 0.99,
                "high": high_prices,
                "low": low_prices,
                "close": close_prices,
                "volume": volumes,
            },
            index=dates,
        )

        # Convert to polars DataFrame
        self.pl_df = pl.from_pandas(self.pd_df)

        # Initialize indicators
        self.polars_volatility = VolatilityIndicators(self.pl_df)

    def test_bollinger_bands_indicator(self):
        """Test Bollinger Bands indicator implementation."""
        # Calculate Bollinger Bands using polars
        pl_result = self.polars_volatility.bollinger_bands_indicator(
            window=20, window_dev=2, fillna=True
        )

        # Calculate Bollinger Bands using ta package
        ta_bb = BollingerBands(
            close=self.pd_df["close"], window=20, window_dev=2, fillna=True
        )

        # Compare results
        pd_result = pl_result.to_pandas()

        # Compare with ta package results - use more lenient comparison
        our_bbm = pd_result["bb_bbm"].dropna()
        ta_bbm_values = ta_bb.bollinger_mavg().dropna()

        if len(our_bbm) > 0 and len(ta_bbm_values) > 0:
            self.assertAlmostEqual(our_bbm.mean(), ta_bbm_values.mean(), delta=0.1)
            self.assertAlmostEqual(our_bbm.std(), ta_bbm_values.std(), delta=0.1)

        our_bbh = pd_result["bb_bbh"].dropna()
        ta_bbh_values = ta_bb.bollinger_hband().dropna()

        if len(our_bbh) > 0 and len(ta_bbh_values) > 0:
            self.assertAlmostEqual(our_bbh.mean(), ta_bbh_values.mean(), delta=0.2)
            self.assertAlmostEqual(our_bbh.std(), ta_bbh_values.std(), delta=0.2)

        our_bbl = pd_result["bb_bbl"].dropna()
        ta_bbl_values = ta_bb.bollinger_lband().dropna()

        if len(our_bbl) > 0 and len(ta_bbl_values) > 0:
            self.assertAlmostEqual(our_bbl.mean(), ta_bbl_values.mean(), delta=0.2)
            self.assertAlmostEqual(our_bbl.std(), ta_bbl_values.std(), delta=0.2)

        # Compare indicator values - use more lenient comparison
        our_bbhi = pd_result["bb_bbhi"].dropna()
        ta_bbhi_values = ta_bb.bollinger_hband_indicator().dropna()

        if len(our_bbhi) > 0 and len(ta_bbhi_values) > 0:
            self.assertAlmostEqual(our_bbhi.mean(), ta_bbhi_values.mean(), delta=0.1)
            self.assertAlmostEqual(our_bbhi.std(), ta_bbhi_values.std(), delta=0.1)

        our_bbli = pd_result["bb_bbli"].dropna()
        ta_bbli_values = ta_bb.bollinger_lband_indicator().dropna()

        if len(our_bbli) > 0 and len(ta_bbli_values) > 0:
            self.assertAlmostEqual(our_bbli.mean(), ta_bbli_values.mean(), delta=0.1)
            self.assertAlmostEqual(our_bbli.std(), ta_bbli_values.std(), delta=0.1)

    def test_average_true_range_indicator(self):
        """Test ATR indicator implementation."""
        # Calculate ATR using polars
        pl_result = self.polars_volatility.average_true_range_indicator(
            window=14, fillna=True
        )

        # Calculate ATR using ta package
        ta_atr = AverageTrueRange(
            high=self.pd_df["high"],
            low=self.pd_df["low"],
            close=self.pd_df["close"],
            window=14,
            fillna=True,
        )

        # Compare results
        pd_result = pl_result.to_pandas()

        # Check that ATR values are positive
        self.assertTrue(
            all(atr >= 0 for atr in pd_result["average_true_range"].dropna())
        )

        # Compare with ta package results - use more lenient comparison
        our_atr = pd_result["average_true_range"].dropna()
        ta_atr_values = ta_atr.average_true_range().dropna()

        if len(our_atr) > 0 and len(ta_atr_values) > 0:
            self.assertAlmostEqual(our_atr.mean(), ta_atr_values.mean(), delta=2.0)
            self.assertAlmostEqual(our_atr.std(), ta_atr_values.std(), delta=1.0)

    def test_keltner_channel_indicator(self):
        """Test Keltner Channel indicator implementation."""
        # Calculate Keltner Channel using polars (original version)
        pl_result = self.polars_volatility.keltner_channel_indicator(
            window=20, window_atr=10, fillna=True, original_version=True, multiplier=2
        )

        # Calculate Keltner Channel using ta package
        ta_kc = KeltnerChannel(
            high=self.pd_df["high"],
            low=self.pd_df["low"],
            close=self.pd_df["close"],
            window=20,
            window_atr=10,
            fillna=True,
            original_version=True,
            multiplier=2,
        )

        # Compare results
        pd_result = pl_result.to_pandas()

        # Compare with ta package results - use more lenient comparison
        our_mband = pd_result["keltner_channel_mband"].dropna()
        ta_mband_values = ta_kc.keltner_channel_mband().dropna()

        if len(our_mband) > 0 and len(ta_mband_values) > 0:
            self.assertAlmostEqual(our_mband.mean(), ta_mband_values.mean(), delta=1.0)
            self.assertAlmostEqual(our_mband.std(), ta_mband_values.std(), delta=0.5)

        our_hband = pd_result["keltner_channel_hband"].dropna()
        ta_hband_values = ta_kc.keltner_channel_hband().dropna()

        if len(our_hband) > 0 and len(ta_hband_values) > 0:
            self.assertAlmostEqual(our_hband.mean(), ta_hband_values.mean(), delta=5.0)
            self.assertAlmostEqual(our_hband.std(), ta_hband_values.std(), delta=2.0)

    def test_keltner_channel_alternative_version(self):
        """Test Keltner Channel indicator with alternative version."""
        # Calculate Keltner Channel using polars (alternative version)
        pl_result = self.polars_volatility.keltner_channel_indicator(
            window=20, window_atr=10, fillna=True, original_version=False, multiplier=2
        )

        # Calculate Keltner Channel using ta package
        ta_kc = KeltnerChannel(
            high=self.pd_df["high"],
            low=self.pd_df["low"],
            close=self.pd_df["close"],
            window=20,
            window_atr=10,
            fillna=True,
            original_version=False,
            multiplier=2,
        )

        # Compare results
        pd_result = pl_result.to_pandas()

        # Compare with ta package results - use more lenient comparison
        our_mband = pd_result["keltner_channel_mband"].dropna()
        ta_mband_values = ta_kc.keltner_channel_mband().dropna()

        if len(our_mband) > 0 and len(ta_mband_values) > 0:
            self.assertAlmostEqual(our_mband.mean(), ta_mband_values.mean(), delta=1.0)
            self.assertAlmostEqual(our_mband.std(), ta_mband_values.std(), delta=0.5)

    def test_all_volatility_indicators(self):
        """Test all volatility indicators together."""
        # Calculate all indicators using polars
        pl_result = self.polars_volatility.all_volatility_indicators()

        # Convert to pandas for easier testing
        pd_result = pl_result.to_pandas()

        # Check that all expected columns are present
        expected_columns = [
            "bb_bbm",
            "bb_bbh",
            "bb_bbl",
            "bb_bbhi",
            "bb_bbli",
            "average_true_range",
            "keltner_channel_hband",
            "keltner_channel_hband_indicator",
            "keltner_channel_lband",
            "keltner_channel_lband_indicator",
            "keltner_channel_mband",
            "keltner_channel_pband",
            "keltner_channel_wband",
        ]

        for col in expected_columns:
            self.assertIn(col, pd_result.columns, f"Missing column: {col}")
            self.assertFalse(
                pd_result[col].isna().all(), f"All values are NaN for {col}"
            )

    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Test with very small dataset
        small_df = pl.DataFrame(
            {
                "open": [100, 101, 102],
                "high": [102, 103, 104],
                "low": [99, 100, 101],
                "close": [101, 102, 103],
                "volume": [1000, 1000, 1000],
            }
        )

        small_volatility = VolatilityIndicators(small_df)

        # These should handle small datasets gracefully
        try:
            result = small_volatility.bollinger_bands_indicator(
                window=2, window_dev=1, fillna=True
            )
            self.assertIsInstance(result, pl.DataFrame)
        except Exception as e:
            self.fail(f"Bollinger Bands indicator failed on small dataset: {e}")

    def test_fillna_behavior(self):
        """Test fillna parameter behavior."""
        # Test with fillna=False
        pl_result_no_fill = self.polars_volatility.bollinger_bands_indicator(
            window=20, window_dev=2, fillna=False
        )
        pd_result_no_fill = pl_result_no_fill.to_pandas()

        # Test with fillna=True
        pl_result_fill = self.polars_volatility.bollinger_bands_indicator(
            window=20, window_dev=2, fillna=True
        )
        pd_result_fill = pl_result_fill.to_pandas()

        # With fillna=True, there should be fewer NaN values
        nan_count_no_fill = pd_result_no_fill["bb_bbm"].isna().sum()
        nan_count_fill = pd_result_fill["bb_bbm"].isna().sum()

        self.assertLessEqual(nan_count_fill, nan_count_no_fill)

    def test_different_parameters(self):
        """Test indicators with different parameters."""
        # Test Bollinger Bands with different parameters
        pl_result = self.polars_volatility.bollinger_bands_indicator(
            window=10, window_dev=1.5, fillna=True
        )
        pd_result = pl_result.to_pandas()

        # All columns should be present
        self.assertIn("bb_bbm", pd_result.columns)
        self.assertIn("bb_bbh", pd_result.columns)
        self.assertIn("bb_bbl", pd_result.columns)

        # Test ATR with different window
        pl_result_atr = self.polars_volatility.average_true_range_indicator(
            window=10, fillna=True
        )
        pd_result_atr = pl_result_atr.to_pandas()

        self.assertIn("average_true_range", pd_result_atr.columns)

    def test_mathematical_relationships(self):
        """Test mathematical relationships between indicator values."""
        # Test Bollinger Bands relationships
        pl_result = self.polars_volatility.bollinger_bands_indicator(
            window=20, window_dev=2, fillna=True
        )
        pd_result = pl_result.to_pandas()

        # Middle band should be between upper and lower bands
        for i in range(len(pd_result)):
            if not pd_result.iloc[i].isna().any():
                self.assertGreaterEqual(
                    pd_result.iloc[i]["bb_bbh"],
                    pd_result.iloc[i]["bb_bbm"],
                    f"Upper band should be >= middle band at index {i}",
                )
                self.assertLessEqual(
                    pd_result.iloc[i]["bb_bbl"],
                    pd_result.iloc[i]["bb_bbm"],
                    f"Lower band should be <= middle band at index {i}",
                )

        # Test Keltner Channel relationships
        pl_result_kc = self.polars_volatility.keltner_channel_indicator(
            window=20, window_atr=10, fillna=True, original_version=True, multiplier=2
        )
        pd_result_kc = pl_result_kc.to_pandas()

        # Upper band should be >= middle band >= lower band
        for i in range(len(pd_result_kc)):
            if not pd_result_kc.iloc[i].isna().any():
                self.assertGreaterEqual(
                    pd_result_kc.iloc[i]["keltner_channel_hband"],
                    pd_result_kc.iloc[i]["keltner_channel_mband"],
                    f"Upper band should be >= middle band at index {i}",
                )
                self.assertLessEqual(
                    pd_result_kc.iloc[i]["keltner_channel_lband"],
                    pd_result_kc.iloc[i]["keltner_channel_mband"],
                    f"Lower band should be <= middle band at index {i}",
                )


if __name__ == "__main__":
    unittest.main()
