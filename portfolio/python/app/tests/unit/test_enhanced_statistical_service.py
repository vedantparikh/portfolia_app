"""
Tests for Enhanced Statistical Service
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.core.schemas.statistical_indicators import (
    ChartDataRequest,
    IndicatorCalculationRequest,
    IndicatorConfiguration,
)
from app.core.services.enhanced_statistical_service import EnhancedStatisticalService


@pytest.fixture
def mock_db():
    """Mock database session."""
    return Mock()


@pytest.fixture
def service(mock_db):
    """Enhanced statistical service instance."""
    return EnhancedStatisticalService(mock_db)


@pytest.fixture
def sample_indicators():
    """Sample indicator configurations."""
    return [
        IndicatorConfiguration(
            indicator_name="rsi_indicator",
            parameters={"window": 14, "fillna": False},
            enabled=True,
            display_name="RSI (14)",
            color="#FF6B6B",
            y_axis="secondary"
        ),
        IndicatorConfiguration(
            indicator_name="macd_indicator",
            parameters={
                "window_slow": 26,
                "window_fast": 12,
                "window_sign": 9,
                "fillna": False
            },
            enabled=True,
            display_name="MACD",
            color="#4ECDC4",
            y_axis="secondary"
        )
    ]


@pytest.fixture
def sample_request(sample_indicators):
    """Sample calculation request."""
    return IndicatorCalculationRequest(
        symbol="AAPL",
        period="6mo",
        interval="1d",
        indicators=sample_indicators
    )


@pytest.fixture
def sample_chart_request(sample_indicators):
    """Sample chart data request."""
    return ChartDataRequest(
        symbol="AAPL",
        period="6mo",
        interval="1d",
        indicators=sample_indicators,
        chart_type="candlestick",
        include_volume=True
    )


class TestEnhancedStatisticalService:
    """Test cases for Enhanced Statistical Service."""

    @pytest.mark.asyncio
    async def test_get_available_indicators(self, service):
        """Test getting available indicators."""
        with patch.object(service.indicator_registry, 'get_available_indicators') as mock_get:
            mock_get.return_value = {
                "indicators": [
                    {
                        "name": "rsi_indicator",
                        "category": "momentum",
                        "description": "RSI indicator",
                        "parameters": [],
                        "output_columns": ["RSI"],
                        "required_columns": ["Close"],
                        "class_name": "MomentumIndicators",
                        "method_name": "rsi_indicator"
                    }
                ],
                "categories": ["momentum", "trend", "volatility", "volume"],
                "statistics": {"total_indicators": 16}
            }
            
            result = await service.get_available_indicators()
            
            assert "indicators" in result
            assert "categories" in result
            assert "statistics" in result
            assert len(result["indicators"]) == 1
            assert result["indicators"][0]["name"] == "rsi_indicator"

    @pytest.mark.asyncio
    async def test_calculate_indicators_success(self, service, sample_request):
        """Test successful indicator calculation."""
        # Mock market data service
        mock_market_data = Mock()
        mock_market_data.is_empty.return_value = False
        mock_market_data.columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
        mock_market_data.__getitem__.side_effect = lambda key: Mock(min=lambda: datetime.now(), max=lambda: datetime.now())
        
        with patch.object(service.market_data_service, 'get_market_data', new_callable=AsyncMock) as mock_get_data:
            mock_get_data.return_value = mock_market_data
            
            # Mock indicator registry
            with patch.object(service.indicator_registry, 'validate_indicator_configuration') as mock_validate:
                mock_validate.return_value = []
                
                with patch.object(service.indicator_registry, 'calculate_indicators') as mock_calculate:
                    mock_result_df = Mock()
                    mock_result_df.to_dicts.return_value = [
                        {
                            "Date": "2023-01-01",
                            "Close": 150.0,
                            "RSI": 50.0,
                            "MACD": 0.1
                        }
                    ]
                    mock_calculate.return_value = (mock_result_df, [], Mock())
                    
                    result = await service.calculate_indicators(sample_request)
                    
                    assert result.symbol == "AAPL"
                    assert result.period == "6mo"
                    assert result.interval == "1d"
                    assert len(result.data) == 1
                    assert result.indicators_applied == ["rsi_indicator", "macd_indicator"]

    @pytest.mark.asyncio
    async def test_calculate_indicators_validation_error(self, service, sample_request):
        """Test indicator calculation with validation errors."""
        # Mock market data service
        mock_market_data = Mock()
        mock_market_data.is_empty.return_value = False
        
        with patch.object(service.market_data_service, 'get_market_data', new_callable=AsyncMock) as mock_get_data:
            mock_get_data.return_value = mock_market_data
            
            # Mock validation errors
            with patch.object(service.indicator_registry, 'validate_indicator_configuration') as mock_validate:
                from app.core.schemas.statistical_indicators import (
                    IndicatorValidationError,
                )
                mock_validate.return_value = [
                    IndicatorValidationError(
                        indicator_name="rsi_indicator",
                        parameter_name="window",
                        error_message="Invalid window value",
                        provided_value=-1,
                        expected_type="integer"
                    )
                ]
                
                with pytest.raises(ValueError, match="Validation errors"):
                    await service.calculate_indicators(sample_request)

    @pytest.mark.asyncio
    async def test_calculate_indicators_no_data(self, service, sample_request):
        """Test indicator calculation with no market data."""
        # Mock empty market data
        mock_market_data = Mock()
        mock_market_data.is_empty.return_value = True
        
        with patch.object(service.market_data_service, 'get_market_data', new_callable=AsyncMock) as mock_get_data:
            mock_get_data.return_value = mock_market_data
            
            with pytest.raises(ValueError, match="No market data found"):
                await service.calculate_indicators(sample_request)

    @pytest.mark.asyncio
    async def test_generate_chart_data_success(self, service, sample_chart_request):
        """Test successful chart data generation."""
        # Mock market data service
        mock_market_data = Mock()
        mock_market_data.is_empty.return_value = False
        mock_market_data.columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
        mock_market_data.__getitem__.side_effect = lambda key: Mock(min=lambda: datetime.now(), max=lambda: datetime.now())
        
        with patch.object(service.market_data_service, 'get_market_data', new_callable=AsyncMock) as mock_get_data:
            mock_get_data.return_value = mock_market_data
            
            # Mock indicator registry
            with patch.object(service.indicator_registry, 'validate_indicator_configuration') as mock_validate:
                mock_validate.return_value = []
                
                with patch.object(service.indicator_registry, 'calculate_indicators') as mock_calculate:
                    mock_result_df = Mock()
                    mock_result_df.to_dicts.return_value = [
                        {
                            "Date": "2023-01-01",
                            "Open": 150.0,
                            "High": 155.0,
                            "Low": 145.0,
                            "Close": 152.0,
                            "Volume": 1000000,
                            "RSI": 50.0,
                            "MACD": 0.1
                        }
                    ]
                    mock_calculate.return_value = (mock_result_df, [], Mock())
                    
                    result = await service.generate_chart_data(sample_chart_request)
                    
                    assert result.symbol == "AAPL"
                    assert result.chart_type == "candlestick"
                    assert "data" in result.data
                    assert len(result.indicators) > 0

    @pytest.mark.asyncio
    async def test_get_predefined_templates(self, service):
        """Test getting predefined templates."""
        with patch.object(service.configuration_service, 'get_predefined_templates') as mock_get:
            mock_templates = {
                "basic_technical_analysis": {
                    "name": "Basic Technical Analysis",
                    "description": "Essential indicators",
                    "indicators": []
                }
            }
            mock_get.return_value = mock_templates
            
            result = await service.get_predefined_templates()
            
            assert "basic_technical_analysis" in result
            assert result["basic_technical_analysis"]["name"] == "Basic Technical Analysis"

    @pytest.mark.asyncio
    async def test_validate_indicator_configuration(self, service):
        """Test indicator configuration validation."""
        config = IndicatorConfiguration(
            indicator_name="rsi_indicator",
            parameters={"window": 14, "fillna": False},
            enabled=True
        )
        
        with patch.object(service.indicator_registry, 'validate_indicator_configuration') as mock_validate:
            mock_validate.return_value = []
            
            errors = await service.validate_indicator_configuration(config)
            
            assert errors == []
            mock_validate.assert_called_once_with(config)

    @pytest.mark.asyncio
    async def test_create_configuration_from_template(self, service):
        """Test creating configuration from template."""
        with patch.object(service.configuration_service, 'create_from_template') as mock_create:
            mock_config = Mock()
            mock_config.dict.return_value = {"id": 1, "name": "Test Config"}
            mock_create.return_value = mock_config
            
            result = await service.create_configuration_from_template(1, "test_template", "Custom Name")
            
            assert result == {"id": 1, "name": "Test Config"}
            mock_create.assert_called_once_with(1, "test_template", "Custom Name")

    def test_prepare_chart_data_candlestick(self, service):
        """Test preparing candlestick chart data."""
        # Mock DataFrame
        mock_df = Mock()
        mock_df.to_dicts.return_value = [
            {
                "Date": datetime(2023, 1, 1),
                "Open": 150.0,
                "High": 155.0,
                "Low": 145.0,
                "Close": 152.0
            }
        ]
        
        indicators = [
            IndicatorConfiguration(
                indicator_name="rsi_indicator",
                parameters={"window": 14, "fillna": False},
                enabled=True
            )
        ]
        
        result = service._prepare_chart_data(mock_df, indicators, "candlestick", True, {})
        
        assert result["type"] == "candlestick"
        assert len(result["data"]) == 1
        assert result["data"][0]["open"] == 150.0
        assert result["data"][0]["close"] == 152.0

    def test_prepare_chart_data_line(self, service):
        """Test preparing line chart data."""
        # Mock DataFrame
        mock_df = Mock()
        mock_df.to_dicts.return_value = [
            {
                "Date": datetime(2023, 1, 1),
                "Close": 152.0
            }
        ]
        
        indicators = []
        
        result = service._prepare_chart_data(mock_df, indicators, "line", False, {})
        
        assert result["type"] == "line"
        assert len(result["data"]) == 1
        assert result["data"][0]["y"] == 152.0

    def test_prepare_indicator_data(self, service):
        """Test preparing indicator data for chart."""
        # Mock DataFrame
        mock_df = Mock()
        mock_df.to_dicts.return_value = [
            {
                "Date": datetime(2023, 1, 1),
                "RSI": 50.0
            }
        ]
        
        indicators = [
            IndicatorConfiguration(
                indicator_name="rsi_indicator",
                parameters={"window": 14, "fillna": False},
                enabled=True,
                display_name="RSI (14)",
                color="#FF6B6B",
                y_axis="secondary"
            )
        ]
        
        # Mock indicator definition
        with patch.object(service.indicator_registry, 'get_indicator_definition') as mock_get_def:
            mock_def = Mock()
            mock_def.output_columns = ["RSI"]
            mock_get_def.return_value = mock_def
            
            result = service._prepare_indicator_data(mock_df, indicators)
            
            assert len(result) == 1
            assert result[0]["name"] == "RSI (14)"
            assert result[0]["indicator_name"] == "rsi_indicator"
            assert result[0]["color"] == "#FF6B6B"
            assert result[0]["y_axis"] == "secondary"

    def test_prepare_volume_data(self, service):
        """Test preparing volume data for chart."""
        # Mock DataFrame
        mock_df = Mock()
        mock_df.to_dicts.return_value = [
            {
                "Date": datetime(2023, 1, 1),
                "Volume": 1000000
            }
        ]
        
        result = service._prepare_volume_data(mock_df)
        
        assert len(result) == 1
        assert result[0]["y"] == 1000000
