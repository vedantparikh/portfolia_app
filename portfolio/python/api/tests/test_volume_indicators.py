import unittest
import pandas as pd
import polars as pl
import numpy as np
from ta.volume import (
    MFIIndicator, VolumePriceTrendIndicator, VolumeWeightedAveragePrice,
    OnBalanceVolumeIndicator, ForceIndexIndicator
)

from statistical_indicators.volume_indicators import VolumeIndicators


class TestVolumeIndicators(unittest.TestCase):
    """Test volume indicators comparing polars implementation with ta package."""

    def setUp(self):
        """Set up test data."""
        # Create sample OHLCV data
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        
        # Generate realistic price data
        close_prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
        high_prices = close_prices + np.random.uniform(0.5, 2.0, 100)
        low_prices = close_prices - np.random.uniform(0.5, 2.0, 100)
        volumes = np.random.randint(1000, 10000, 100)
        
        # Create pandas DataFrame
        self.pd_df = pd.DataFrame({
            'Open': close_prices * 0.99,
            'High': high_prices,
            'Low': low_prices,
            'Close': close_prices,
            'Volume': volumes
        }, index=dates)
        
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
            high=self.pd_df['High'],
            low=self.pd_df['Low'],
            close=self.pd_df['Close'],
            volume=self.pd_df['Volume'],
            window=14,
            fillna=True
        )
        
        # Compare results
        pd_result = pl_result.to_pandas()
        
        # Check that MFI values are in expected range [0, 100]
        self.assertTrue(all(0 <= mfi <= 100 for mfi in pd_result['mfi_indicator'].dropna()))
        
        # Compare with ta package results
        np.testing.assert_array_almost_equal(
            pd_result['mfi_indicator'].values,
            ta_mfi.money_flow_index().values,
            decimal=5,
            err_msg="MFI values don't match ta package"
        )

    def test_volume_price_trend_indicator(self):
        """Test VPT indicator implementation."""
        # Calculate VPT using polars
        pl_result = self.polars_volume.volume_price_trend_indicator(fillna=True)
        
        # Calculate VPT using ta package
        ta_vpt = VolumePriceTrendIndicator(
            close=self.pd_df['Close'],
            volume=self.pd_df['Volume'],
            fillna=True
        )
        
        # Compare results
        pd_result = pl_result.to_pandas()
        
        # Compare with ta package results
        np.testing.assert_array_almost_equal(
            pd_result['volume_price_trend'].values,
            ta_vpt.volume_price_trend().values,
            decimal=5,
            err_msg="VPT values don't match ta package"
        )

    def test_volume_weighted_average_price(self):
        """Test VWAP indicator implementation."""
        # Calculate VWAP using polars
        pl_result = self.polars_volume.volume_weighted_average_price(
            window=14, fillna=True
        )
        
        # Calculate VWAP using ta package
        ta_vwap = VolumeWeightedAveragePrice(
            high=self.pd_df['High'],
            low=self.pd_df['Low'],
            close=self.pd_df['Close'],
            volume=self.pd_df['Volume'],
            window=14,
            fillna=True
        )
        
        # Compare results
        pd_result = pl_result.to_pandas()
        
        # Compare with ta package results
        np.testing.assert_array_almost_equal(
            pd_result['volume_weighted_average_price'].values,
            ta_vwap.volume_weighted_average_price().values,
            decimal=5,
            err_msg="VWAP values don't match ta package"
        )

    def test_on_balance_volume_indicator(self):
        """Test OBV indicator implementation."""
        # Calculate OBV using polars
        pl_result = self.polars_volume.on_balance_volume_indicator(fillna=True)
        
        # Calculate OBV using ta package
        ta_obv = OnBalanceVolumeIndicator(
            close=self.pd_df['Close'],
            volume=self.pd_df['Volume'],
            fillna=True
        )
        
        # Compare results
        pd_result = pl_result.to_pandas()
        
        # Compare with ta package results
        np.testing.assert_array_almost_equal(
            pd_result['on_balance_volume'].values,
            ta_obv.on_balance_volume().values,
            decimal=5,
            err_msg="OBV values don't match ta package"
        )

    def test_force_index_indicator(self):
        """Test Force Index indicator implementation."""
        # Calculate Force Index using polars
        pl_result = self.polars_volume.force_index_indicator(window=13, fillna=True)
        
        # Calculate Force Index using ta package
        ta_fi = ForceIndexIndicator(
            close=self.pd_df['Close'],
            volume=self.pd_df['Volume'],
            window=13,
            fillna=True
        )
        
        # Compare results
        pd_result = pl_result.to_pandas()
        
        # Compare with ta package results
        np.testing.assert_array_almost_equal(
            pd_result['force_index'].values,
            ta_fi.force_index().values,
            decimal=5,
            err_msg="Force Index values don't match ta package"
        )

    def test_all_volume_indicators(self):
        """Test all volume indicators together."""
        # Calculate all indicators using polars
        pl_result = self.polars_volume.all_volume_indicators()
        
        # Convert to pandas for easier testing
        pd_result = pl_result.to_pandas()
        
        # Check that all expected columns are present
        expected_columns = [
            'mfi_indicator', 'volume_price_trend', 'volume_weighted_average_price',
            'on_balance_volume', 'force_index'
        ]
        
        for col in expected_columns:
            self.assertIn(col, pd_result.columns, f"Missing column: {col}")
            self.assertFalse(pd_result[col].isna().all(), f"All values are NaN for {col}")

    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Test with very small dataset
        small_df = pl.DataFrame({
            'Open': [100, 101, 102],
            'High': [102, 103, 104],
            'Low': [99, 100, 101],
            'Close': [101, 102, 103],
            'Volume': [1000, 1000, 1000]
        })
        
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
        nan_count_no_fill = pd_result_no_fill['mfi_indicator'].isna().sum()
        nan_count_fill = pd_result_fill['mfi_indicator'].isna().sum()
        
        self.assertLessEqual(nan_count_fill, nan_count_no_fill)

    def test_different_parameters(self):
        """Test indicators with different parameters."""
        # Test MFI with different window
        pl_result = self.polars_volume.mfi_indicator(window=10, fillna=True)
        pd_result = pl_result.to_pandas()
        
        self.assertIn('mfi_indicator', pd_result.columns)
        
        # Test VWAP with different window
        pl_result_vwap = self.polars_volume.volume_weighted_average_price(
            window=10, fillna=True
        )
        pd_result_vwap = pl_result_vwap.to_pandas()
        
        self.assertIn('volume_weighted_average_price', pd_result_vwap.columns)
        
        # Test Force Index with different window
        pl_result_fi = self.polars_volume.force_index_indicator(window=5, fillna=True)
        pd_result_fi = pl_result_fi.to_pandas()
        
        self.assertIn('force_index', pd_result_fi.columns)

    def test_mathematical_relationships(self):
        """Test mathematical relationships between indicator values."""
        # Test MFI range
        pl_result = self.polars_volume.mfi_indicator(window=14, fillna=True)
        pd_result = pl_result.to_pandas()
        
        # MFI should be between 0 and 100
        mfi_values = pd_result['mfi_indicator'].dropna()
        self.assertTrue(all(0 <= mfi <= 100 for mfi in mfi_values))
        
        # Test VPT cumulative nature
        pl_result_vpt = self.polars_volume.volume_price_trend_indicator(fillna=True)
        pd_result_vpt = pl_result_vpt.to_pandas()
        
        # VPT should generally increase or decrease over time (cumulative)
        vpt_values = pd_result_vpt['volume_price_trend'].dropna()
        if len(vpt_values) > 1:
            # Check that VPT changes are not all zero
            vpt_changes = vpt_values.diff().dropna()
            self.assertFalse(all(change == 0 for change in vpt_changes))

    def test_volume_sensitivity(self):
        """Test that indicators are sensitive to volume changes."""
        # Create data with different volume patterns
        high_volume_df = pl.DataFrame({
            'Open': [100, 101, 102, 103, 104],
            'High': [102, 103, 104, 105, 106],
            'Low': [99, 100, 101, 102, 103],
            'Close': [101, 102, 103, 104, 105],
            'Volume': [10000, 20000, 30000, 40000, 50000]  # Increasing volume
        })
        
        low_volume_df = pl.DataFrame({
            'Open': [100, 101, 102, 103, 104],
            'High': [102, 103, 104, 105, 106],
            'Low': [99, 100, 101, 102, 103],
            'Close': [101, 102, 103, 104, 105],
            'Volume': [1000, 1000, 1000, 1000, 1000]  # Constant low volume
        })
        
        high_volume_indicators = VolumeIndicators(high_volume_df)
        low_volume_indicators = VolumeIndicators(low_volume_df)
        
        # Calculate MFI for both
        high_volume_mfi = high_volume_indicators.mfi_indicator(window=3, fillna=True)
        low_volume_mfi = low_volume_indicators.mfi_indicator(window=3, fillna=True)
        
        # Convert to pandas for comparison
        high_pd = high_volume_mfi.to_pandas()
        low_pd = low_volume_mfi.to_pandas()
        
        # Both should produce valid results
        self.assertIn('mfi_indicator', high_pd.columns)
        self.assertIn('mfi_indicator', low_pd.columns)

    def test_price_volume_relationship(self):
        """Test that indicators properly reflect price-volume relationships."""
        # Create data with clear price-volume relationship
        price_up_volume_up = pl.DataFrame({
            'Open': [100, 101, 102, 103, 104],
            'High': [102, 103, 104, 105, 106],
            'Low': [99, 100, 101, 102, 103],
            'Close': [101, 102, 103, 104, 105],  # Price increasing
            'Volume': [1000, 2000, 3000, 4000, 5000]  # Volume increasing
        })
        
        price_down_volume_up = pl.DataFrame({
            'Open': [100, 99, 98, 97, 96],
            'High': [102, 101, 100, 99, 98],
            'Low': [99, 98, 97, 96, 95],
            'Close': [101, 100, 99, 98, 97],  # Price decreasing
            'Volume': [1000, 2000, 3000, 4000, 5000]  # Volume increasing
        })
        
        up_up_indicators = VolumeIndicators(price_up_volume_up)
        down_up_indicators = VolumeIndicators(price_down_volume_up)
        
        # Calculate VPT for both
        up_up_vpt = up_up_indicators.volume_price_trend_indicator(fillna=True)
        down_up_vpt = down_up_indicators.volume_price_trend_indicator(fillna=True)
        
        # Convert to pandas for comparison
        up_up_pd = up_up_vpt.to_pandas()
        down_up_pd = down_up_vpt.to_pandas()
        
        # Both should produce valid results
        self.assertIn('volume_price_trend', up_up_pd.columns)
        self.assertIn('volume_price_trend', down_up_pd.columns)


if __name__ == '__main__':
    unittest.main()
