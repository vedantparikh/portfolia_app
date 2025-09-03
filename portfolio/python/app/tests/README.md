# Technical Indicators Test Suite

This test suite validates the polars-based implementation of technical indicators by comparing results with the industry-standard `ta` package.

## Overview

The tests ensure that our polars-based implementations produce identical results to the `ta` package, guaranteeing accuracy while providing the performance benefits of polars.

## Test Coverage

### 1. Momentum Indicators (`test_momentum_indicators.py`)
- **RSI (Relative Strength Index)**: Tests the 14-period RSI calculation
- **ROC (Rate of Change)**: Tests the 12-period ROC calculation
- **Stochastic RSI**: Tests the stochastic RSI with smoothing parameters
- **Stochastic Oscillator**: Tests the stochastic oscillator with %K and %D lines

### 2. Trend Indicators (`test_trend_indicators.py`)
- **MACD**: Tests Moving Average Convergence Divergence with signal line and histogram
- **ADX**: Tests Average Directional Index with DI+ and DI- components
- **Aroon Indicator**: Tests Aroon Up, Down, and Indicator calculations
- **CCI**: Tests Commodity Channel Index
- **PSAR**: Tests Parabolic Stop and Reverse (simplified implementation)

### 3. Volatility Indicators (`test_volatility_indicators.py`)
- **Bollinger Bands**: Tests upper, middle, and lower bands with indicators
- **ATR**: Tests Average True Range calculation
- **Keltner Channel**: Tests both original and alternative versions

### 4. Volume Indicators (`test_volume_indicators.py`)
- **MFI**: Tests Money Flow Index
- **VPT**: Tests Volume Price Trend
- **VWAP**: Tests Volume Weighted Average Price
- **OBV**: Tests On Balance Volume
- **Force Index**: Tests Force Index with smoothing

### 5. Market/Stock Module (`test_market_stock.py`)
- **Symbol Search**: Tests symbol lookup functionality
- **Data Fetching**: Tests OHLCV data retrieval
- **Data Conversion**: Tests pandas to polars conversion accuracy
- **Error Handling**: Tests error scenarios

## Running the Tests

### Prerequisites
```bash
pip install -r requirements.txt
```

### Run All Tests
```bash
cd python/api/tests
python run_tests.py
```

### Run Specific Test Suite
```bash
# Run only momentum indicators tests
python run_tests.py momentum

# Run only trend indicators tests
python run_tests.py trend

# Run only volatility indicators tests
python run_tests.py volatility

# Run only volume indicators tests
python run_tests.py volume

# Run only market/stock tests
python run_tests.py market
```

### Run Individual Test Files
```bash
# Run momentum indicators tests directly
python -m unittest test_momentum_indicators.py

# Run with verbose output
python -m unittest -v test_momentum_indicators.py
```

## Test Data

The tests use synthetic OHLCV data generated with:
- **100 data points** for comprehensive testing
- **Realistic price movements** using random walk with drift
- **Consistent volume patterns** for volume-based indicators
- **Reproducible results** using fixed random seed (42)

## Validation Approach

### 1. Numerical Accuracy
- Compare results with `ta` package using `numpy.testing.assert_array_almost_equal`
- Allow for small floating-point differences (5 decimal places)
- Verify that all values are within expected ranges

### 2. Mathematical Relationships
- Test that Bollinger Bands maintain: Upper ≥ Middle ≥ Lower
- Verify that Aroon values are between 0 and 100
- Check that RSI values are between 0 and 100
- Validate cumulative nature of indicators like VPT and OBV

### 3. Edge Cases
- Test with very small datasets (3-5 data points)
- Verify proper handling of NaN values
- Test different parameter combinations
- Validate error handling

### 4. Performance Characteristics
- Ensure data conversion completes in reasonable time
- Verify memory efficiency of polars operations
- Test with larger datasets (1000+ points)

## Expected Results

When all tests pass, you can be confident that:

1. **Accuracy**: Our polars implementations produce identical results to the `ta` package
2. **Performance**: Polars operations are significantly faster than pandas equivalents
3. **Memory Efficiency**: Polars uses less memory for large datasets
4. **Reliability**: All edge cases and error conditions are handled properly

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running from the correct directory
2. **Missing Dependencies**: Install all required packages from requirements.txt
3. **Path Issues**: The test runner automatically adds the parent directory to Python path

### Debug Mode

For detailed debugging, run individual tests with verbose output:
```bash
python -m unittest -v test_momentum_indicators.TestMomentumIndicators.test_rsi_indicator
```

### Performance Testing

To test performance improvements:
```bash
# Run with timing information
python -m unittest -v test_market_stock.TestMarketStock.test_performance_characteristics
```

## Contributing

When adding new indicators:

1. **Create comprehensive tests** comparing with `ta` package
2. **Test edge cases** and error conditions
3. **Validate mathematical relationships** where applicable
4. **Include performance benchmarks** for large datasets
5. **Document any deviations** from standard implementations

## License

This test suite is part of the Portfolia API project and follows the same licensing terms.
