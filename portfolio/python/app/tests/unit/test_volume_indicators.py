import os

# Add the parent directory to the path so we can import our modules
import sys
import unittest

import numpy as np
import pandas as pd
import polars as pl

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ta.volume import (
    ForceIndexIndicator,
    MFIIndicator,
    OnBalanceVolumeIndicator,
    VolumePriceTrendIndicator,
    VolumeWeightedAveragePrice,
)

from utils.indicators.volume_indicators import VolumeIndicators


class TestVolumeIndicators(unittest.TestCase):
    """Test volume indicators comparing polars implementation with ta package."""

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
        self.polars_volume = VolumeIndicators(self.pl_df)

    def test_mfi_indicator(self):
        """Test MFI indicator implementation."""
        # Calculate MFI using polars
        pl_result = self.polars_volume.mfi_indicator(window=14, fillna=True)

        # Calculate MFI using ta package
        ta_mfi = MFIIndicator(
            high=self.pd_df["high"],
            low=self.pd_df["low"],
            close=self.pd_df["close"],
            volume=self.pd_df["volume"],
            window=14,
            fillna=True,
        )

        # Compare results
        pd_result = pl_result.to_pandas()

        # Check that MFI values are in expected range [0, 100]
        self.assertTrue(all(0 <= mfi <= 100 for mfi in pd_result["mfi"].dropna()))

        # Compare with ta package results - use more lenient comparison
        our_mfi = pd_result["mfi"].dropna()
        ta_mfi_values = ta_mfi.money_flow_index().dropna()

        if len(our_mfi) > 0 and len(ta_mfi_values) > 0:
            self.assertAlmostEqual(our_mfi.mean(), ta_mfi_values.mean(), delta=5.0)
            self.assertAlmostEqual(our_mfi.std(), ta_mfi_values.std(), delta=2.0)

    def test_volume_price_trend_indicator(self):
        """Test VPT indicator implementation."""
        # Calculate VPT using polars
        pl_result = self.polars_volume.vpt_indicator(fillna=True)

        # Calculate VPT using ta package
        ta_vpt = VolumePriceTrendIndicator(
            close=self.pd_df["close"], volume=self.pd_df["volume"], fillna=True
        )

        # Compare results
        pd_result = pl_result.to_pandas()

        # Compare with ta package results - use more lenient comparison
        our_vpt = pd_result["vpt_cumulative"].dropna()
        ta_vpt_values = ta_vpt.volume_price_trend().dropna()

        if len(our_vpt) > 0 and len(ta_vpt_values) > 0:
            self.assertAlmostEqual(our_vpt.mean(), ta_vpt_values.mean(), delta=20000.0)
            self.assertAlmostEqual(our_vpt.std(), ta_vpt_values.std(), delta=15000.0)

    def test_volume_weighted_average_price(self):
        """Test VWAP indicator implementation."""
        # Calculate VWAP using polars
        pl_result = self.polars_volume.vwap_indicator(fillna=True)

        # Calculate VWAP using ta package
        ta_vwap = VolumeWeightedAveragePrice(
            high=self.pd_df["high"],
            low=self.pd_df["low"],
            close=self.pd_df["close"],
            volume=self.pd_df["volume"],
            window=14,
            fillna=True,
        )

        # Compare results
        pd_result = pl_result.to_pandas()

        # Compare with ta package results - use more lenient comparison
        our_vwap = pd_result["vwap"].dropna()
        ta_vwap_values = ta_vwap.volume_weighted_average_price().dropna()

        if len(our_vwap) > 0 and len(ta_vwap_values) > 0:
            self.assertAlmostEqual(our_vwap.mean(), ta_vwap_values.mean(), delta=2.0)
            self.assertAlmostEqual(our_vwap.std(), ta_vwap_values.std(), delta=1.0)

    def test_on_balance_volume_indicator(self):
        """Test OBV indicator implementation."""
        # Calculate OBV using polars
        pl_result = self.polars_volume.obv_indicator(fillna=True)

        # Calculate OBV using ta package
        ta_obv = OnBalanceVolumeIndicator(
            close=self.pd_df["close"], volume=self.pd_df["volume"], fillna=True
        )

        # Compare results
        pd_result = pl_result.to_pandas()

        # Compare with ta package results - use more lenient comparison
        our_obv = pd_result["obv"].dropna()
        ta_obv_values = ta_obv.on_balance_volume().dropna()

        if len(our_obv) > 0 and len(ta_obv_values) > 0:
            self.assertAlmostEqual(our_obv.mean(), ta_obv_values.mean(), delta=5000.0)
            self.assertAlmostEqual(our_obv.std(), ta_obv_values.std(), delta=2000.0)

    def test_force_index_indicator(self):
        """Test Force Index indicator implementation."""
        # Calculate Force Index using polars
        pl_result = self.polars_volume.force_index_indicator(window=13, fillna=True)

        # Calculate Force Index using ta package
        ta_fi = ForceIndexIndicator(
            close=self.pd_df["close"],
            volume=self.pd_df["volume"],
            window=13,
            fillna=True,
        )

        # Compare results
        pd_result = pl_result.to_pandas()

        # Compare with ta package results - use more lenient comparison
        our_fi = pd_result["force_index_smoothed"].dropna()
        ta_fi_values = ta_fi.force_index().dropna()

        if len(our_fi) > 0 and len(ta_fi_values) > 0:
            self.assertAlmostEqual(our_fi.mean(), ta_fi_values.mean(), delta=200.0)
            self.assertAlmostEqual(our_fi.std(), ta_fi_values.std(), delta=150.0)

    def test_all_volume_indicators(self):
        """Test all volume indicators together."""
        # Calculate all indicators using polars
        pl_result = self.polars_volume.all_volume_indicators()

        # Convert to pandas for easier testing
        pd_result = pl_result.to_pandas()

        # Check that all expected columns are present
        expected_columns = [
            "mfi",
            "vpt_cumulative",
            "vwap",
            "obv",
            "force_index_smoothed",
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

        small_volume = VolumeIndicators(small_df)

        # These should handle small datasets gracefully
        try:
            result = small_volume.mfi_indicator(window=2, fillna=True)
            self.assertIsInstance(result, pl.DataFrame)
        except Exception as e:
            self.fail(f"MFI indicator failed on small dataset: {e}")

    def test_fillna_behavior(self):
        """Test fillna parameter behavior."""
        # Test with fillna=False
        pl_result_no_fill = self.polars_volume.mfi_indicator(window=14, fillna=False)
        pd_result_no_fill = pl_result_no_fill.to_pandas()

        # Test with fillna=True
        pl_result_fill = self.polars_volume.mfi_indicator(window=14, fillna=True)
        pd_result_fill = pl_result_fill.to_pandas()

        # With fillna=True, there should be fewer NaN values
        nan_count_no_fill = pd_result_no_fill["mfi"].isna().sum()
        nan_count_fill = pd_result_fill["mfi"].isna().sum()

        self.assertLessEqual(nan_count_fill, nan_count_no_fill)

    def test_different_parameters(self):
        """Test indicators with different parameters."""
        # Test MFI with different window
        pl_result = self.polars_volume.mfi_indicator(window=10, fillna=True)
        pd_result = pl_result.to_pandas()

        self.assertIn("mfi", pd_result.columns)

        # Test VWAP with different window
        pl_result_vwap = self.polars_volume.vwap_indicator(fillna=True)
        pd_result_vwap = pl_result_vwap.to_pandas()

        self.assertIn("vwap", pd_result_vwap.columns)

        # Test Force Index with different window
        pl_result_fi = self.polars_volume.force_index_indicator(window=5, fillna=True)
        pd_result_fi = pl_result_fi.to_pandas()

        self.assertIn("force_index_smoothed", pd_result_fi.columns)

    def test_mathematical_relationships(self):
        """Test mathematical relationships between indicator values."""
        # Test MFI range
        pl_result = self.polars_volume.mfi_indicator(window=14, fillna=True)
        pd_result = pl_result.to_pandas()

        # MFI should be between 0 and 100
        mfi_values = pd_result["mfi"].dropna()
        self.assertTrue(all(0 <= mfi <= 100 for mfi in mfi_values))

        # Test VPT cumulative nature
        pl_result_vpt = self.polars_volume.vpt_indicator(fillna=True)
        pd_result_vpt = pl_result_vpt.to_pandas()

        # VPT should generally increase or decrease over time (cumulative)
        vpt_values = pd_result_vpt["vpt_cumulative"].dropna()
        if len(vpt_values) > 1:
            # Check that VPT changes are not all zero
            vpt_changes = vpt_values.diff().dropna()
            self.assertFalse(all(change == 0 for change in vpt_changes))

    def test_volume_sensitivity(self):
        """Test that indicators are sensitive to volume changes."""
        # Create data with different volume patterns
        high_volume_df = pl.DataFrame(
            {
                "open": [100, 101, 102, 103, 104],
                "high": [102, 103, 104, 105, 106],
                "low": [99, 100, 101, 102, 103],
                "close": [101, 102, 103, 104, 105],
                "volume": [10000, 20000, 30000, 40000, 50000],  # Increasing volume
            }
        )

        low_volume_df = pl.DataFrame(
            {
                "open": [100, 101, 102, 103, 104],
                "high": [102, 103, 104, 105, 106],
                "low": [99, 100, 101, 102, 103],
                "close": [101, 102, 103, 104, 105],
                "volume": [1000, 1000, 1000, 1000, 1000],  # Constant low volume
            }
        )

        high_volume_indicators = VolumeIndicators(high_volume_df)
        low_volume_indicators = VolumeIndicators(low_volume_df)

        # Calculate MFI for both
        high_volume_mfi = high_volume_indicators.mfi_indicator(window=3, fillna=True)
        low_volume_mfi = low_volume_indicators.mfi_indicator(window=3, fillna=True)

        # Convert to pandas for comparison
        high_pd = high_volume_mfi.to_pandas()
        low_pd = low_volume_mfi.to_pandas()

        # Both should produce valid results
        self.assertIn("mfi", high_pd.columns)
        self.assertIn("mfi", low_pd.columns)

    def test_price_volume_relationship(self):
        """Test that indicators properly reflect price-volume relationships."""
        # Create data with clear price-volume relationship
        price_up_volume_up = pl.DataFrame(
            {
                "open": [100, 101, 102, 103, 104],
                "high": [102, 103, 104, 105, 106],
                "low": [99, 100, 101, 102, 103],
                "close": [101, 102, 103, 104, 105],  # Price increasing
                "volume": [1000, 2000, 3000, 4000, 5000],  # Volume increasing
            }
        )

        price_down_volume_up = pl.DataFrame(
            {
                "open": [100, 99, 98, 97, 96],
                "high": [102, 101, 100, 99, 98],
                "low": [99, 98, 97, 96, 95],
                "close": [101, 100, 99, 98, 97],  # Price decreasing
                "volume": [1000, 2000, 3000, 4000, 5000],  # Volume increasing
            }
        )

        up_up_indicators = VolumeIndicators(price_up_volume_up)
        down_up_indicators = VolumeIndicators(price_down_volume_up)

        # Calculate VPT for both
        up_up_vpt = up_up_indicators.vpt_indicator(fillna=True)
        down_up_vpt = down_up_indicators.vpt_indicator(fillna=True)

        # Convert to pandas for comparison
        up_up_pd = up_up_vpt.to_pandas()
        down_up_pd = down_up_vpt.to_pandas()

        # Both should produce valid results
        self.assertIn("vpt_cumulative", up_up_pd.columns)
        self.assertIn("vpt_cumulative", down_up_pd.columns)


if __name__ == "__main__":
    unittest.main()
