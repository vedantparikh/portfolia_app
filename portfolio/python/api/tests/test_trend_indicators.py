import unittest
import pandas as pd
import polars as pl
import numpy as np
from ta.trend import (
    MACD, ADXIndicator, AroonIndicator, PSARIndicator, CCIIndicator
)

from statistical_indicators.trend_indicators import TrendIndicators


class TestTrendIndicators(unittest.TestCase):
    """Test trend indicators comparing polars implementation with ta package."""

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
        self.polars_trend = TrendIndicators(self.pl_df)

    def test_macd_indicator(self):
        """Test MACD indicator implementation."""
        # Calculate MACD using polars
        pl_result = self.polars_trend.macd_indicator(
            window_slow=26, window_fast=12, window_sign=9, fillna=True
        )
        
        # Calculate MACD using ta package
        ta_macd = MACD(
            close=self.pd_df['Close'],
            window_slow=26,
            window_fast=12,
            window_sign=9,
            fillna=True
        )
        
        # Compare results
        pd_result = pl_result.to_pandas()
        
        # Compare with ta package results
        np.testing.assert_array_almost_equal(
            pd_result['MACD'].values,
            ta_macd.macd().values,
            decimal=5,
            err_msg="MACD values don't match ta package"
        )
        
        np.testing.assert_array_almost_equal(
            pd_result['Signal'].values,
            ta_macd.macd_signal().values,
            decimal=5,
            err_msg="MACD Signal values don't match ta package"
        )
        
        np.testing.assert_array_almost_equal(
            pd_result['Histogram'].values,
            ta_macd.macd_diff().values,
            decimal=5,
            err_msg="MACD Histogram values don't match ta package"
        )

    def test_adx_indicator(self):
        """Test ADX indicator implementation."""
        # Calculate ADX using polars
        pl_result = self.polars_trend.adx_indicator(window=14, fillna=True)
        
        # Calculate ADX using ta package
        ta_adx = ADXIndicator(
            high=self.pd_df['High'],
            low=self.pd_df['Low'],
            close=self.pd_df['Close'],
            window=14,
            fillna=True
        )
        
        # Compare results
        pd_result = pl_result.to_pandas()
        
        # Check that ADX values are in expected range [0, 100]
        self.assertTrue(all(0 <= adx <= 100 for adx in pd_result['ADX'].dropna()))
        
        # Compare with ta package results
        np.testing.assert_array_almost_equal(
            pd_result['ADX'].values,
            ta_adx.adx().values,
            decimal=5,
            err_msg="ADX values don't match ta package"
        )
        
        np.testing.assert_array_almost_equal(
            pd_result['ADX_pos'].values,
            ta_adx.adx_pos().values,
            decimal=5,
            err_msg="ADX+ values don't match ta package"
        )
        
        np.testing.assert_array_almost_equal(
            pd_result['ADX_neg'].values,
            ta_adx.adx_neg().values,
            decimal=5,
            err_msg="ADX- values don't match ta package"
        )

    def test_aroon_indicator(self):
        """Test Aroon indicator implementation."""
        # Calculate Aroon using polars
        pl_result = self.polars_trend.aroon_indicator(window=25, fillna=True)
        
        # Calculate Aroon using ta package
        ta_aroon = AroonIndicator(
            close=self.pd_df['Close'],
            window=25,
            fillna=True
        )
        
        # Compare results
        pd_result = pl_result.to_pandas()
        
        # Check that Aroon values are in expected range [0, 100]
        self.assertTrue(all(0 <= aroon <= 100 for aroon in pd_result['aroon_up'].dropna()))
        self.assertTrue(all(0 <= aroon <= 100 for aroon in pd_result['aroon_down'].dropna()))
        self.assertTrue(all(-100 <= aroon <= 100 for aroon in pd_result['aroon_indicator'].dropna()))
        
        # Compare with ta package results
        np.testing.assert_array_almost_equal(
            pd_result['aroon_up'].values,
            ta_aroon.aroon_up().values,
            decimal=5,
            err_msg="Aroon Up values don't match ta package"
        )
        
        np.testing.assert_array_almost_equal(
            pd_result['aroon_down'].values,
            ta_aroon.aroon_down().values,
            decimal=5,
            err_msg="Aroon Down values don't match ta package"
        )
        
        np.testing.assert_array_almost_equal(
            pd_result['aroon_indicator'].values,
            ta_aroon.aroon_indicator().values,
            decimal=5,
            err_msg="Aroon Indicator values don't match ta package"
        )

    def test_cci_indicator(self):
        """Test CCI indicator implementation."""
        # Calculate CCI using polars
        pl_result = self.polars_trend.cci_indicator(window=20, constant=0.015, fillna=True)
        
        # Calculate CCI using ta package
        ta_cci = CCIIndicator(
            high=self.pd_df['High'],
            low=self.pd_df['Low'],
            close=self.pd_df['Close'],
            window=20,
            constant=0.015,
            fillna=True
        )
        
        # Compare results
        pd_result = pl_result.to_pandas()
        
        # Compare with ta package results
        np.testing.assert_array_almost_equal(
            pd_result['CCI'].values,
            ta_cci.cci().values,
            decimal=5,
            err_msg="CCI values don't match ta package"
        )

    def test_all_trend_indicators(self):
        """Test all trend indicators together."""
        # Calculate all indicators using polars
        pl_result = self.polars_trend.all_trend_indicators()
        
        # Convert to pandas for easier testing
        pd_result = pl_result.to_pandas()
        
        # Check that all expected columns are present
        expected_columns = ['MACD', 'Signal', 'Histogram', 'aroon_down', 'aroon_up', 
                          'aroon_indicator', 'ADX', 'ADX_neg', 'ADX_pos', 'psar', 
                          'psar_down', 'psar_down_indicator', 'psar_up', 'psar_up_indicator']
        
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
        
        small_trend = TrendIndicators(small_df)
        
        # These should handle small datasets gracefully
        try:
            result = small_trend.macd_indicator(window_slow=3, window_fast=2, window_sign=2, fillna=True)
            self.assertIsInstance(result, pl.DataFrame)
        except Exception as e:
            self.fail(f"MACD indicator failed on small dataset: {e}")

    def test_fillna_behavior(self):
        """Test fillna parameter behavior."""
        # Test with fillna=False
        pl_result_no_fill = self.polars_trend.macd_indicator(
            window_slow=26, window_fast=12, window_sign=9, fillna=False
        )
        pd_result_no_fill = pl_result_no_fill.to_pandas()
        
        # Test with fillna=True
        pl_result_fill = self.polars_trend.macd_indicator(
            window_slow=26, window_fast=12, window_sign=9, fillna=True
        )
        pd_result_fill = pl_result_fill.to_pandas()
        
        # With fillna=True, there should be fewer NaN values
        nan_count_no_fill = pd_result_no_fill['MACD'].isna().sum()
        nan_count_fill = pd_result_fill['MACD'].isna().sum()
        
        self.assertLessEqual(nan_count_fill, nan_count_no_fill)

    def test_different_windows(self):
        """Test indicators with different window sizes."""
        # Test MACD with different parameters
        pl_result = self.polars_trend.macd_indicator(
            window_slow=20, window_fast=10, window_sign=5, fillna=True
        )
        pd_result = pl_result.to_pandas()
        
        # All columns should be present
        self.assertIn('MACD', pd_result.columns)
        self.assertIn('Signal', pd_result.columns)
        self.assertIn('Histogram', pd_result.columns)
        
        # Test ADX with different window
        pl_result_adx = self.polars_trend.adx_indicator(window=10, fillna=True)
        pd_result_adx = pl_result_adx.to_pandas()
        
        self.assertIn('ADX', pd_result_adx.columns)
        self.assertIn('ADX_pos', pd_result_adx.columns)
        self.assertIn('ADX_neg', pd_result_adx.columns)


if __name__ == '__main__':
    unittest.main()
