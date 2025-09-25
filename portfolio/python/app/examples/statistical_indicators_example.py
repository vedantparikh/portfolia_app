#!/usr/bin/env python3
"""
Statistical Indicators Example
Demonstrates how to use the enhanced statistical indicators API.
"""

from typing import Any, Dict, List

import requests

# API base URL
BASE_URL = "http://localhost:8000/api/v1/statistical-indicators"

class StatisticalIndicatorsClient:
    """Client for interacting with the statistical indicators API."""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_available_indicators(self, category: str = None, search: str = None) -> Dict[str, Any]:
        """Get available indicators."""
        params = {}
        if category:
            params["category"] = category
        if search:
            params["search"] = search
        
        response = self.session.get(f"{self.base_url}/indicators", params=params)
        response.raise_for_status()
        return response.json()
    
    def calculate_indicators(
        self, 
        symbol: str, 
        indicators: List[Dict[str, Any]], 
        period: str = "6mo",
        interval: str = "1d"
    ) -> Dict[str, Any]:
        """Calculate indicators for a symbol."""
        data = {
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "indicators": indicators
        }
        
        response = self.session.post(f"{self.base_url}/calculate", json=data)
        response.raise_for_status()
        return response.json()
    
    def calculate_with_configuration(
        self, 
        symbol: str, 
        configuration_id: int,
        period: str = "6mo",
        interval: str = "1d"
    ) -> Dict[str, Any]:
        """Calculate indicators using a saved configuration."""
        data = {
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "configuration_id": configuration_id
        }
        
        response = self.session.post(f"{self.base_url}/calculate", json=data)
        response.raise_for_status()
        return response.json()
    
    def generate_chart_data(
        self, 
        symbol: str, 
        indicators: List[Dict[str, Any]], 
        chart_type: str = "candlestick",
        period: str = "6mo",
        interval: str = "1d"
    ) -> Dict[str, Any]:
        """Generate chart data."""
        data = {
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "chart_type": chart_type,
            "include_volume": True,
            "indicators": indicators
        }
        
        response = self.session.post(f"{self.base_url}/chart-data", json=data)
        response.raise_for_status()
        return response.json()
    
    def create_configuration(
        self, 
        name: str, 
        indicators: List[Dict[str, Any]], 
        description: str = None,
        is_public: bool = False,
        tags: List[str] = None
    ) -> Dict[str, Any]:
        """Create a new analysis configuration."""
        data = {
            "name": name,
            "description": description,
            "indicators": indicators,
            "is_public": is_public,
            "tags": tags or []
        }
        
        response = self.session.post(f"{self.base_url}/configurations", json=data)
        response.raise_for_status()
        return response.json()
    
    def get_configurations(self, user_only: bool = False, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """Get analysis configurations."""
        params = {
            "user_only": user_only,
            "skip": skip,
            "limit": limit
        }
        
        response = self.session.get(f"{self.base_url}/configurations", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_templates(self) -> Dict[str, Any]:
        """Get predefined templates."""
        response = self.session.get(f"{self.base_url}/templates")
        response.raise_for_status()
        return response.json()
    
    def create_from_template(self, template_name: str, custom_name: str = None) -> Dict[str, Any]:
        """Create configuration from template."""
        data = {}
        if custom_name:
            data["custom_name"] = custom_name
        
        response = self.session.post(f"{self.base_url}/templates/{template_name}/create", json=data)
        response.raise_for_status()
        return response.json()
    
    def validate_configuration(self, indicator_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate an indicator configuration."""
        response = self.session.post(f"{self.base_url}/validate", json=indicator_config)
        response.raise_for_status()
        return response.json()


def example_basic_rsi_analysis():
    """Example: Basic RSI analysis for AAPL."""
    print("=== Basic RSI Analysis ===")
    
    client = StatisticalIndicatorsClient()
    
    # Define RSI indicator
    rsi_config = {
        "indicator_name": "rsi_indicator",
        "parameters": {
            "window": 14,
            "fillna": False
        },
        "enabled": True,
        "display_name": "RSI (14)",
        "color": "#FF6B6B",
        "y_axis": "secondary"
    }
    
    # Calculate RSI
    result = client.calculate_indicators("AAPL", [rsi_config], period="3mo")
    
    print(f"Symbol: {result['symbol']}")
    print(f"Period: {result['period']}")
    print(f"Total records: {result['total_records']}")
    print(f"Indicators applied: {result['indicators_applied']}")
    
    # Show last 5 RSI values
    print("\nLast 5 RSI values:")
    for row in result['data'][-5:]:
        print(f"Date: {row['Date']}, RSI: {row['RSI']:.2f}")


def example_advanced_momentum_analysis():
    """Example: Advanced momentum analysis with multiple indicators."""
    print("\n=== Advanced Momentum Analysis ===")
    
    client = StatisticalIndicatorsClient()
    
    # Define multiple momentum indicators
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
    
    # Calculate indicators
    result = client.calculate_indicators("AAPL", indicators, period="6mo")
    
    print(f"Symbol: {result['symbol']}")
    print(f"Indicators applied: {result['indicators_applied']}")
    
    # Show latest values
    latest = result['data'][-1]
    print(f"\nLatest values for {latest['Date']}:")
    print(f"RSI: {latest['RSI']:.2f}")
    print(f"Stochastic RSI: {latest['stoch_rsi']:.2f}")
    print(f"Rate of Change: {latest['ROC']:.2f}")


def example_multiple_instances_analysis():
    """Example: Multiple instances of the same indicator with different parameters."""
    print("\n=== Multiple Instances Analysis ===")
    
    client = StatisticalIndicatorsClient()
    
    # Define multiple instances of RSI with different periods
    indicators = [
        {
            "id": "rsi_14",
            "indicator_name": "rsi_indicator",
            "parameters": {"window": 14, "fillna": False},
            "enabled": True,
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
            "enabled": True,
            "display_name": "RSI (21)",
            "color": "#FF9F43",
            "y_axis": "secondary",
            "group": "momentum",
            "z_index": 2,
            "line_style": "dashed"
        },
        {
            "id": "rsi_30",
            "indicator_name": "rsi_indicator",
            "parameters": {"window": 30, "fillna": False},
            "enabled": True,
            "display_name": "RSI (30)",
            "color": "#5F27CD",
            "y_axis": "secondary",
            "group": "momentum",
            "z_index": 1,
            "line_style": "dotted"
        },
        # Multiple Bollinger Bands
        {
            "id": "bb_20_2",
            "indicator_name": "bollinger_bands_indicator",
            "parameters": {"window": 20, "window_dev": 2, "fillna": False},
            "enabled": True,
            "display_name": "BB (20,2)",
            "color": "#45B7D1",
            "y_axis": "primary",
            "group": "volatility",
            "z_index": 1
        },
        {
            "id": "bb_50_2.5",
            "indicator_name": "bollinger_bands_indicator",
            "parameters": {"window": 50, "window_dev": 2.5, "fillna": False},
            "enabled": True,
            "display_name": "BB (50,2.5)",
            "color": "#FF6B6B",
            "y_axis": "primary",
            "group": "volatility",
            "z_index": 0,
            "opacity": 0.7
        }
    ]
    
    # Calculate indicators
    result = client.calculate_indicators("AAPL", indicators, period="3mo")
    
    print(f"Symbol: {result['symbol']}")
    print(f"Indicators applied: {result['indicators_applied']}")
    print(f"Total records: {result['total_records']}")
    
    # Show React chart data structure
    if 'react_chart_data' in result:
        react_data = result['react_chart_data']
        print("\nReact Chart Data:")
        print(f"Chart type: {react_data['chart_type']}")
        print(f"Price data points: {len(react_data['price_data'])}")
        print(f"Indicator series: {len(react_data['indicator_series'])}")
        print(f"Volume data points: {len(react_data['volume_data']) if react_data['volume_data'] else 0}")
        
        # Show indicator series details
        print("\nIndicator Series:")
        for series in react_data['indicator_series']:
            print(f"- {series['display_name']}: {len(series['data'])} points, color: {series['color']}")
    
    # Show latest values for each RSI instance
    latest = result['data'][-1]
    print(f"\nLatest values for {latest['Date']}:")
    if 'RSI_rsi_14' in latest:
        print(f"RSI (14): {latest['RSI_rsi_14']:.2f}")
    if 'RSI_rsi_21' in latest:
        print(f"RSI (21): {latest['RSI_rsi_21']:.2f}")
    if 'RSI_rsi_30' in latest:
        print(f"RSI (30): {latest['RSI_rsi_30']:.2f}")


def example_configuration_management():
    """Example: Create and use analysis configurations."""
    print("\n=== Configuration Management ===")
    
    client = StatisticalIndicatorsClient()
    
    # Define a custom configuration
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
            "indicator_name": "macd_indicator",
            "parameters": {
                "window_slow": 26,
                "window_fast": 12,
                "window_sign": 9,
                "fillna": False
            },
            "enabled": True,
            "display_name": "MACD",
            "color": "#4ECDC4",
            "y_axis": "secondary"
        },
        {
            "indicator_name": "bollinger_bands_indicator",
            "parameters": {"window": 20, "window_dev": 2, "fillna": False},
            "enabled": True,
            "display_name": "Bollinger Bands",
            "color": "#45B7D1",
            "y_axis": "primary"
        }
    ]
    
    # Create configuration
    config = client.create_configuration(
        name="My Custom Analysis",
        description="RSI, MACD, and Bollinger Bands analysis",
        indicators=indicators,
        is_public=False,
        tags=["custom", "momentum", "trend", "volatility"]
    )
    
    print(f"Created configuration: {config['name']} (ID: {config['id']})")
    
    # Use the configuration
    result = client.calculate_with_configuration("AAPL", config['id'], period="3mo")
    
    print(f"Using configuration: {result['configuration_name']}")
    print(f"Indicators applied: {result['indicators_applied']}")


def example_template_usage():
    """Example: Using predefined templates."""
    print("\n=== Template Usage ===")
    
    client = StatisticalIndicatorsClient()
    
    # Get available templates
    templates = client.get_templates()
    print("Available templates:")
    for name, template in templates.items():
        print(f"- {name}: {template['description']}")
    
    # Create from template
    config = client.create_from_template("basic_technical_analysis", "My Basic Analysis")
    print(f"\nCreated from template: {config['name']} (ID: {config['id']})")
    
    # Use the template configuration
    result = client.calculate_with_configuration("AAPL", config['id'], period="1mo")
    print(f"Using template configuration: {result['configuration_name']}")


def example_chart_data_generation():
    """Example: Generate chart data for visualization."""
    print("\n=== Chart Data Generation ===")
    
    client = StatisticalIndicatorsClient()
    
    # Define indicators for chart
    indicators = [
        {
            "indicator_name": "bollinger_bands_indicator",
            "parameters": {"window": 20, "window_dev": 2, "fillna": False},
            "enabled": True,
            "display_name": "Bollinger Bands",
            "color": "#45B7D1",
            "y_axis": "primary"
        },
        {
            "indicator_name": "rsi_indicator",
            "parameters": {"window": 14, "fillna": False},
            "enabled": True,
            "display_name": "RSI (14)",
            "color": "#FF6B6B",
            "y_axis": "secondary"
        }
    ]
    
    # Generate chart data
    chart_data = client.generate_chart_data("AAPL", indicators, chart_type="candlestick", period="3mo")
    
    print(f"Chart type: {chart_data['chart_type']}")
    print(f"Data points: {len(chart_data['data']['data'])}")
    print(f"Indicators: {len(chart_data['indicators'])}")
    print(f"Volume data: {'Yes' if chart_data['volume_data'] else 'No'}")


def example_validation():
    """Example: Validate indicator configurations."""
    print("\n=== Configuration Validation ===")
    
    client = StatisticalIndicatorsClient()
    
    # Valid configuration
    valid_config = {
        "indicator_name": "rsi_indicator",
        "parameters": {"window": 14, "fillna": False},
        "enabled": True
    }
    
    errors = client.validate_configuration(valid_config)
    print(f"Valid configuration errors: {len(errors)}")
    
    # Invalid configuration
    invalid_config = {
        "indicator_name": "rsi_indicator",
        "parameters": {"window": -1, "fillna": "invalid"},  # Invalid values
        "enabled": True
    }
    
    errors = client.validate_configuration(invalid_config)
    print(f"Invalid configuration errors: {len(errors)}")
    for error in errors:
        print(f"- {error['parameter_name']}: {error['error_message']}")


def main():
    """Run all examples."""
    try:
        example_basic_rsi_analysis()
        example_advanced_momentum_analysis()
        example_multiple_instances_analysis()
        example_configuration_management()
        example_template_usage()
        example_chart_data_generation()
        example_validation()
        
        print("\n=== All examples completed successfully! ===")
        
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
