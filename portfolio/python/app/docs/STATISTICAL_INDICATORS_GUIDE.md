# Statistical Indicators Configuration Guide

This guide explains how to use the enhanced statistical indicators system that allows users to define custom parameters and create multiple analysis configurations.

## Overview

The enhanced statistical indicators system provides:

1. **User-configurable parameters** for all indicators
2. **Multiple analysis configurations** that can be saved and reused
3. **Predefined templates** for common analysis scenarios
4. **Chart data generation** for visualization
5. **Dynamic indicator execution** based on user configurations
6. **Multiple instances** of the same indicator with different parameters
7. **React UI integration** with optimized chart data structures

## 🆕 **New Features - Multiple Indicator Instances & React UI Support**

### **Multiple Instances of Same Indicator**

You can now use multiple instances of the same indicator with different parameters in a single configuration:

```python
# Example: Multiple RSI instances with different periods
indicators = [
    {
        "id": "rsi_14",
        "indicator_name": "rsi_indicator",
        "parameters": {"window": 14, "fillna": False},
        "display_name": "RSI (14)",
        "color": "#FF6B6B",
        "y_axis": "secondary",
        "group": "momentum",
        "z_index": 3
    },
    {
        "id": "rsi_21",
        "indicator_name": "rsi_indicator",
        "parameters": {"window": 21, "fillna": False},
        "display_name": "RSI (21)",
        "color": "#FF9F43",
        "y_axis": "secondary",
        "group": "momentum",
        "z_index": 2,
        "line_style": "dashed"
    }
]
```

### **React UI Integration**

The API now provides React-optimized chart data:

```python
# Get React chart data
response = requests.get("/api/v1/statistical-indicators/chart-data/react", params={
    "symbol": "AAPL",
    "period": "6mo",
    "configuration_id": 1
})

react_data = response.json()
# Contains: price_data, indicator_series, volume_data, config, metadata
```

### **Enhanced Response Schemas**

All API responses now include comprehensive schemas for React components:

- **`PriceDataPoint`**: Individual price data points
- **`IndicatorSeries`**: Complete indicator series with styling
- **`VolumeDataPoint`**: Volume data for subplots
- **`ChartMetadata`**: Chart configuration and metadata
- **`ReactChartData`**: Complete React-optimized chart structure

## Available Indicators

The system includes indicators from four categories:

### Momentum Indicators

- **RSI (Relative Strength Index)**: Measures overbought/oversold conditions
- **ROC (Rate of Change)**: Measures price momentum
- **Stochastic RSI**: Combines RSI and Stochastic oscillator
- **Stochastic Oscillator**: Measures momentum using high/low/close prices

### Trend Indicators

- **MACD**: Moving Average Convergence Divergence
- **ADX**: Average Directional Index
- **Aroon**: Identifies trend changes
- **PSAR**: Parabolic Stop and Reverse
- **CCI**: Commodity Channel Index

### Volatility Indicators

- **Bollinger Bands**: Price volatility bands
- **ATR**: Average True Range
- **Keltner Channels**: Volatility-based channels

### Volume Indicators

- **MFI**: Money Flow Index
- **VPT**: Volume Price Trend
- **VWAP**: Volume Weighted Average Price
- **OBV**: On-Balance Volume
- **Force Index**: Price and volume momentum

## API Endpoints

### Get Available Indicators

```http
GET /api/v1/statistical-indicators/indicators
```

Query Parameters:

- `category` (optional): Filter by category (momentum, trend, volatility, volume)
- `search` (optional): Search by name or description

Response:

```json
{
  "indicators": [
    {
      "name": "rsi_indicator",
      "category": "momentum",
      "description": "Relative Strength Index indicator",
      "parameters": [
        {
          "name": "window",
          "type": "integer",
          "default_value": 14,
          "min_value": 1,
          "max_value": 200,
          "description": "N -Period",
          "required": true
        },
        {
          "name": "fillna",
          "type": "boolean",
          "default_value": false,
          "description": "If True, fill NaN values",
          "required": true
        }
      ],
      "output_columns": ["RSI"],
      "required_columns": ["Close"],
      "class_name": "MomentumIndicators",
      "method_name": "rsi_indicator"
    }
  ],
  "categories": ["momentum", "trend", "volatility", "volume"],
  "total_indicators": 16
}
```

### Calculate Indicators

```http
POST /api/v1/statistical-indicators/calculate
```

Request Body:

```json
{
  "symbol": "AAPL",
  "period": "1y",
  "interval": "1d",
  "indicators": [
    {
      "indicator_name": "rsi_indicator",
      "parameters": {
        "window": 14,
        "fillna": false
      },
      "enabled": true,
      "display_name": "RSI (14)",
      "color": "#FF6B6B",
      "y_axis": "secondary"
    },
    {
      "indicator_name": "macd_indicator",
      "parameters": {
        "window_slow": 26,
        "window_fast": 12,
        "window_sign": 9,
        "fillna": false
      },
      "enabled": true,
      "display_name": "MACD",
      "color": "#4ECDC4",
      "y_axis": "secondary"
    }
  ]
}
```

Response:

```json
{
  "symbol": "AAPL",
  "period": "1y",
  "interval": "1d",
  "start_date": "2023-01-01T00:00:00",
  "end_date": "2024-01-01T00:00:00",
  "configuration_name": "Custom Configuration",
  "data": [
    {
      "Date": "2023-01-01",
      "Open": 130.28,
      "High": 130.9,
      "Low": 124.17,
      "Close": 125.07,
      "Volume": 112117500,
      "RSI": 45.23,
      "MACD": 0.12,
      "Signal": 0.08,
      "Histogram": 0.04
    }
  ],
  "indicators_applied": ["rsi_indicator", "macd_indicator"],
  "total_records": 252
}
```

### Generate Chart Data

```http
POST /api/v1/statistical-indicators/chart-data
```

Request Body:

```json
{
  "symbol": "AAPL",
  "period": "6mo",
  "interval": "1d",
  "chart_type": "candlestick",
  "include_volume": true,
  "indicators": [
    {
      "indicator_name": "bollinger_bands_indicator",
      "parameters": {
        "window": 20,
        "window_dev": 2,
        "fillna": false
      },
      "enabled": true,
      "display_name": "Bollinger Bands",
      "color": "#45B7D1",
      "y_axis": "primary"
    }
  ]
}
```

### Analysis Configurations

#### Create Configuration

```http
POST /api/v1/statistical-indicators/configurations
```

Request Body:

```json
{
  "name": "My Custom Analysis",
  "description": "Custom technical analysis setup",
  "indicators": [
    {
      "indicator_name": "rsi_indicator",
      "parameters": { "window": 14, "fillna": false },
      "enabled": true,
      "display_name": "RSI (14)",
      "color": "#FF6B6B",
      "y_axis": "secondary"
    },
    {
      "indicator_name": "macd_indicator",
      "parameters": {
        "window_slow": 26,
        "window_fast": 12,
        "window_sign": 9,
        "fillna": false
      },
      "enabled": true,
      "display_name": "MACD",
      "color": "#4ECDC4",
      "y_axis": "secondary"
    }
  ],
  "chart_settings": {
    "height": 600,
    "show_legend": true
  },
  "is_public": false,
  "tags": ["custom", "momentum", "trend"]
}
```

#### Get Configurations

```http
GET /api/v1/statistical-indicators/configurations?user_only=true&skip=0&limit=10
```

#### Use Configuration

```http
POST /api/v1/statistical-indicators/calculate
```

Request Body:

```json
{
  "symbol": "AAPL",
  "period": "1y",
  "interval": "1d",
  "configuration_id": 123
}
```

### Predefined Templates

#### Get Templates

```http
GET /api/v1/statistical-indicators/templates
```

#### Create from Template

```http
POST /api/v1/statistical-indicators/templates/basic_technical_analysis/create
```

Request Body:

```json
{
  "custom_name": "My Basic Analysis"
}
```

## Usage Examples

### Example 1: Basic RSI Analysis

```python
import requests

# Get RSI for AAPL
response = requests.post("http://localhost:8000/api/v1/statistical-indicators/calculate", json={
    "symbol": "AAPL",
    "period": "6mo",
    "interval": "1d",
    "indicators": [
        {
            "indicator_name": "rsi_indicator",
            "parameters": {"window": 14, "fillna": false},
            "enabled": True,
            "display_name": "RSI (14)",
            "color": "#FF6B6B",
            "y_axis": "secondary"
        }
    ]
})

data = response.json()
print(f"RSI values: {[row['RSI'] for row in data['data'][-5:]]}")
```

### Example 2: Advanced Momentum Analysis

```python
# Create a comprehensive momentum analysis
indicators = [
    {
        "indicator_name": "rsi_indicator",
        "parameters": {"window": 14, "fillna": False},
        "enabled": True,
        "display_name": "RSI (14)",
        "color": "#FF6B6B",
        "y_axis": "secondary"
    },
    {
        "indicator_name": "stoch_rsi_indicator",
        "parameters": {"window": 14, "smooth1": 3, "smooth2": 3, "fillna": False},
        "enabled": True,
        "display_name": "Stochastic RSI",
        "color": "#FF9F43",
        "y_axis": "secondary"
    },
    {
        "indicator_name": "roc_indicator",
        "parameters": {"window": 12, "fillna": False},
        "enabled": True,
        "display_name": "Rate of Change",
        "color": "#5F27CD",
        "y_axis": "secondary"
    }
]

response = requests.post("http://localhost:8000/api/v1/statistical-indicators/calculate", json={
    "symbol": "AAPL",
    "period": "1y",
    "interval": "1d",
    "indicators": indicators
})
```

### Example 3: Save and Reuse Configuration

```python
# Create a configuration
config_response = requests.post("http://localhost:8000/api/v1/statistical-indicators/configurations", json={
    "name": "Momentum Analysis",
    "description": "Comprehensive momentum indicators",
    "indicators": indicators,
    "is_public": False,
    "tags": ["momentum", "custom"]
})

config_id = config_response.json()["id"]

# Use the configuration
response = requests.post("http://localhost:8000/api/v1/statistical-indicators/calculate", json={
    "symbol": "AAPL",
    "period": "1y",
    "interval": "1d",
    "configuration_id": config_id
})
```

### Example 4: Generate Chart Data

```python
# Generate Plotly chart data
chart_response = requests.get("http://localhost:8000/api/v1/statistical-indicators/chart-data/plotly", params={
    "symbol": "AAPL",
    "period": "6mo",
    "interval": "1d",
    "configuration_id": config_id,
    "chart_type": "candlestick"
})

chart_data = chart_response.json()
# Use with Plotly for visualization
```

## Parameter Reference

### Common Parameters

Most indicators share these common parameters:

- `window`: Period for calculation (integer, 1-200)
- `fillna`: Whether to fill NaN values (boolean)

### Indicator-Specific Parameters

#### RSI

- `window`: Period (default: 14)

#### MACD

- `window_slow`: Slow period (default: 26)
- `window_fast`: Fast period (default: 12)
- `window_sign`: Signal period (default: 9)

#### Bollinger Bands

- `window`: Period (default: 20)
- `window_dev`: Standard deviation multiplier (default: 2)

#### Stochastic RSI

- `window`: Period (default: 14)
- `smooth1`: First smoothing period (default: 3)
- `smooth2`: Second smoothing period (default: 3)

#### Keltner Channels

- `window`: Period (default: 20)
- `window_atr`: ATR period (default: 10)
- `multiplier`: Channel width multiplier (default: 2)
- `original_version`: Use original version (default: true)

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad Request (validation errors)
- `404`: Not Found (configuration not found)
- `429`: Rate Limit Exceeded
- `500`: Internal Server Error

Error responses include detailed error messages:

```json
{
  "detail": "Validation errors: ['Parameter 'window' must be >= 1', 'Unknown parameter 'invalid_param'']"
}
```

## Rate Limiting

- Unauthenticated users: 10 requests per hour
- Authenticated users: No rate limiting
- Rate limits apply to calculation and chart generation endpoints

## Best Practices

1. **Use configurations** for frequently used indicator combinations
2. **Validate parameters** before sending requests
3. **Cache results** for better performance
4. **Use appropriate timeframes** based on your analysis needs
5. **Combine indicators** from different categories for comprehensive analysis

## Performance Considerations

- Indicator calculations are optimized for large datasets
- Use appropriate `period` and `interval` values
- Consider using saved configurations to reduce API calls
- Chart data generation includes performance metrics

## Troubleshooting

### Common Issues

1. **"Indicator not found"**: Check the indicator name spelling
2. **"Validation errors"**: Verify parameter types and ranges
3. **"No market data found"**: Check symbol validity and date ranges
4. **"Configuration not found"**: Ensure configuration exists and is accessible

### Debug Tips

1. Use the validation endpoint to check configurations
2. Check the available indicators endpoint for correct names
3. Verify parameter ranges using the indicator definitions
4. Test with simple configurations first
