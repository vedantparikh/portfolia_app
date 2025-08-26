import unittest
import pandas as pd
import polars as pl
import numpy as np
from unittest.mock import patch, MagicMock

from market.stock import get_symbols, get_symbol_df, get_symbol_data


class TestMarketStock(unittest.TestCase):
    """Test market stock functions."""

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
        self.sample_df = pd.DataFrame({
            'Open': close_prices * 0.99,
            'High': high_prices,
            'Low': low_prices,
            'Close': close_prices,
            'Volume': volumes,
            'Dividends': np.random.uniform(0, 1, 100)
        }, index=dates)

    @patch('market.stock.yq')
    def test_get_symbols(self, mock_yq):
        """Test get_symbols function."""
        # Mock the yahooquery response
        mock_response = {
            'quotes': [
                {'symbol': 'AAPL', 'quoteType': 'EQUITY'},
                {'symbol': 'GOOGL', 'quoteType': 'EQUITY'},
                {'symbol': 'MSFT', 'quoteType': 'EQUITY'}
            ]
        }
        mock_yq.search.return_value = mock_response
        
        # Test the function
        result = get_symbols('AAPL')
        
        # Verify the result
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].symbol, 'AAPL')
        self.assertEqual(result[0].quoteType, 'EQUITY')
        self.assertEqual(result[1].symbol, 'GOOGL')
        self.assertEqual(result[1].quoteType, 'EQUITY')
        
        # Verify yahooquery was called
        mock_yq.search.assert_called_once_with('AAPL')

    @patch('market.stock.yq')
    def test_get_symbols_no_results(self, mock_yq):
        """Test get_symbols function with no results."""
        # Mock empty response
        mock_response = {'quotes': []}
        mock_yq.search.return_value = mock_response
        
        # Test the function
        result = get_symbols('INVALID')
        
        # Verify the result
        self.assertEqual(result, 'No Symbol Found')

    @patch('market.stock.yf')
    def test_get_symbol_df(self, mock_yf):
        """Test get_symbol_df function."""
        # Mock yfinance Ticker
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = self.sample_df
        mock_yf.Ticker.return_value = mock_ticker
        
        # Test the function
        result = get_symbol_df('AAPL', period='1y', interval='1d')
        
        # Verify the result is a polars DataFrame
        self.assertIsInstance(result, pl.DataFrame)
        
        # Verify it has the expected columns
        expected_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Datetime']
        for col in expected_columns:
            self.assertIn(col, result.columns)
        
        # Verify yfinance was called correctly
        mock_yf.Ticker.assert_called_once_with('AAPL')
        mock_ticker.history.assert_called_once_with(period='1y', interval='1d')

    @patch('market.stock.yf')
    def test_get_symbol_df_default_parameters(self, mock_yf):
        """Test get_symbol_df function with default parameters."""
        # Mock yfinance Ticker
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = self.sample_df
        mock_yf.Ticker.return_value = mock_ticker
        
        # Test the function with default parameters
        result = get_symbol_df('AAPL')
        
        # Verify the result
        self.assertIsInstance(result, pl.DataFrame)
        
        # Verify yfinance was called with default parameters
        mock_ticker.history.assert_called_once_with(period='max', interval='1d')

    @patch('market.stock.get_symbol_df')
    def test_get_symbol_data(self, mock_get_symbol_df):
        """Test get_symbol_data function."""
        # Mock the get_symbol_df function to return our sample data
        mock_get_symbol_df.return_value = pl.from_pandas(self.sample_df)
        
        # Test the function
        result = get_symbol_data('AAPL', period='1y', interval='1d')
        
        # Verify the result is a list
        self.assertIsInstance(result, list)
        
        # Verify it has the expected length
        self.assertEqual(len(result), 100)
        
        # Verify the first item has the expected structure
        first_item = result[0]
        self.assertIsInstance(first_item.id, pd.Timestamp)
        self.assertIsInstance(first_item.open, float)
        self.assertIsInstance(first_item.close, float)
        self.assertIsInstance(first_item.low, float)
        self.assertIsInstance(first_item.high, float)
        self.assertIsInstance(first_item.volume, int)
        self.assertIsInstance(first_item.dividends, float)
        
        # Verify get_symbol_df was called
        mock_get_symbol_df.assert_called_once_with(name='AAPL', period='1y', interval='1d')

    @patch('market.stock.get_symbol_df')
    def test_get_symbol_data_default_parameters(self, mock_get_symbol_df):
        """Test get_symbol_data function with default parameters."""
        # Mock the get_symbol_df function
        mock_get_symbol_df.return_value = pl.from_pandas(self.sample_df)
        
        # Test the function with default parameters
        result = get_symbol_data('AAPL')
        
        # Verify the result
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 100)
        
        # Verify get_symbol_df was called with default parameters
        mock_get_symbol_df.assert_called_once_with(name='AAPL', period='max', interval='1d')

    def test_data_conversion_accuracy(self):
        """Test that data conversion from pandas to polars is accurate."""
        # Test with a simple DataFrame
        simple_df = pd.DataFrame({
            'Open': [100.0, 101.0, 102.0],
            'High': [102.0, 103.0, 104.0],
            'Low': [99.0, 100.0, 101.0],
            'Close': [101.0, 102.0, 103.0],
            'Volume': [1000, 2000, 3000],
            'Dividends': [0.0, 0.5, 0.0]
        }, index=pd.date_range('2023-01-01', periods=3, freq='D'))
        
        # Convert to polars
        pl_df = pl.from_pandas(simple_df)
        
        # Verify the conversion preserved the data
        self.assertEqual(len(pl_df), 3)
        self.assertEqual(pl_df['Open'].to_list(), [100.0, 101.0, 102.0])
        self.assertEqual(pl_df['High'].to_list(), [102.0, 103.0, 104.0])
        self.assertEqual(pl_df['Low'].to_list(), [99.0, 100.0, 101.0])
        self.assertEqual(pl_df['Close'].to_list(), [101.0, 102.0, 103.0])
        self.assertEqual(pl_df['Volume'].to_list(), [1000, 2000, 3000])
        self.assertEqual(pl_df['Dividends'].to_list(), [0.0, 0.5, 0.0])

    def test_error_handling(self):
        """Test error handling in the functions."""
        # Test with invalid symbol
        with self.assertRaises(Exception):
            # This should raise an exception when yfinance tries to fetch data
            get_symbol_df('INVALID_SYMBOL_12345', period='1d', interval='1d')

    def test_data_types(self):
        """Test that the returned data has correct types."""
        # Mock the functions to return test data
        with patch('market.stock.yf') as mock_yf:
            mock_ticker = MagicMock()
            mock_ticker.history.return_value = self.sample_df
            mock_yf.Ticker.return_value = mock_ticker
            
            result_df = get_symbol_df('AAPL')
            
            # Verify data types
            self.assertIsInstance(result_df, pl.DataFrame)
            
            # Check numeric columns
            numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends']
            for col in numeric_columns:
                if col in result_df.columns:
                    # Check that the column contains numeric data
                    sample_values = result_df[col].head(5).to_list()
                    for val in sample_values:
                        if val is not None:
                            self.assertIsInstance(val, (int, float))

    def test_performance_characteristics(self):
        """Test basic performance characteristics."""
        # Create a larger dataset
        large_df = pd.DataFrame({
            'Open': np.random.uniform(100, 200, 1000),
            'High': np.random.uniform(100, 200, 1000),
            'Low': np.random.uniform(100, 200, 1000),
            'Close': np.random.uniform(100, 200, 1000),
            'Volume': np.random.randint(1000, 10000, 1000),
            'Dividends': np.random.uniform(0, 1, 1000)
        }, index=pd.date_range('2023-01-01', periods=1000, freq='D'))
        
        # Test conversion performance
        import time
        start_time = time.time()
        pl_df = pl.from_pandas(large_df)
        conversion_time = time.time() - start_time
        
        # Verify the conversion completed in reasonable time (< 1 second)
        self.assertLess(conversion_time, 1.0, "Data conversion took too long")
        
        # Verify the result
        self.assertEqual(len(pl_df), 1000)
        self.assertEqual(len(pl_df.columns), 6)


if __name__ == '__main__':
    unittest.main()
