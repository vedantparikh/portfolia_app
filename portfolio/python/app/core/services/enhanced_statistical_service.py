"""
Enhanced Statistical Service
Service for calculating indicators with user configurations and chart data generation.
"""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import polars as pl
from sqlalchemy.orm import Session

from app.core.schemas.statistical_indicators import (
    ChartDataRequest,
    ChartDataResponse,
    IndicatorCalculationRequest,
    IndicatorCalculationResponse,
    IndicatorConfiguration,
)
from app.core.services.analysis_configuration_service import AnalysisConfigurationService
from app.core.services.indicator_registry_service import IndicatorRegistryService
from app.core.services.market_data_service import MarketDataService


class EnhancedStatisticalService:
    """Enhanced service for statistical calculations with user configurations."""

    def __init__(self, db: Session):
        self.db = db
        self.indicator_registry = IndicatorRegistryService(db)
        self.configuration_service = AnalysisConfigurationService(db)
        self.market_data_service = MarketDataService()

    async def calculate_indicators(
        self, 
        request: IndicatorCalculationRequest
    ) -> IndicatorCalculationResponse:
        """Calculate indicators based on user configuration."""
        start_time = time.time()
        
        try:
            # Get market data
            market_data = await self.market_data_service.fetch_ticker_data(
                symbol=request.symbol,
                period=request.period,
                interval=request.interval
            )
            
            if market_data.empty:
                raise ValueError(f"No market data found for symbol {request.symbol}")
            
            # Get indicator configurations
            if request.configuration_id:
                config = self.configuration_service.get_configuration(
                    request.configuration_id, 
                    user_id=None  # Allow public configurations
                )
                if not config:
                    raise ValueError(f"Configuration {request.configuration_id} not found")
                indicator_configs = config.indicators
                configuration_name = config.name
            else:
                indicator_configs = request.indicators
                configuration_name = "Custom Configuration"
            
            # Validate all indicator configurations
            validation_errors = []
            for config in indicator_configs:
                errors = self.indicator_registry.validate_indicator_configuration(config)
                validation_errors.extend(errors)
            
            if validation_errors:
                raise ValueError(f"Validation errors: {[e.error_message for e in validation_errors]}")
            
            # Calculate indicators
            result_df, calculation_errors, performance_metrics = self.indicator_registry.calculate_indicators(
                market_data, indicator_configs
            )
            
            # Convert to response format
            data_records = result_df.to_dicts()
            
            # Extract indicator names that were applied
            applied_indicators = [config.indicator_name for config in indicator_configs if config.enabled]
            
            # Generate enhanced response data
            price_data = self._prepare_price_data(result_df)
            indicator_series = self._prepare_indicator_series(result_df, indicator_configs)
            volume_data = self._prepare_volume_data(result_df)
            metadata = self._prepare_metadata(
                request.symbol, request.period, request.interval, 
                result_df, len(applied_indicators), performance_metrics
            )
            
            # Increment usage count if using a saved configuration
            if request.configuration_id:
                self.configuration_service.increment_usage_count(request.configuration_id)
            
            return IndicatorCalculationResponse(
                symbol=request.symbol,
                period=request.period,
                interval=request.interval,
                start_date=market_data["Date"].min() if "Date" in market_data.columns else datetime.now(),
                end_date=market_data["Date"].max() if "Date" in market_data.columns else datetime.now(),
                configuration_name=configuration_name,
                data=data_records,
                indicators_applied=applied_indicators,
                total_records=len(data_records),
                price_data=price_data,
                indicator_series=indicator_series,
                volume_data=volume_data,
                metadata=metadata
            )
            
        except Exception as e:
            raise ValueError(f"Error calculating indicators: {str(e)}")

    async def generate_chart_data(
        self, 
        request: ChartDataRequest
    ) -> ChartDataResponse:
        """Generate chart data with indicators for visualization."""
        try:
            # Get market data
            market_data = await self.market_data_service.get_market_data(
                symbol=request.symbol,
                period=request.period,
                interval=request.interval
            )
            
            if market_data.is_empty():
                raise ValueError(f"No market data found for symbol {request.symbol}")
            
            # Get indicator configurations
            if request.configuration_id:
                config = self.configuration_service.get_configuration(
                    request.configuration_id, 
                    user_id=None
                )
                if not config:
                    raise ValueError(f"Configuration {request.configuration_id} not found")
                indicator_configs = config.indicators
                chart_settings = config.chart_settings or {}
            else:
                indicator_configs = request.indicators
                chart_settings = {}
            
            # Calculate indicators
            result_df, calculation_errors, performance_metrics = self.indicator_registry.calculate_indicators(
                market_data, indicator_configs
            )
            
            # Prepare chart data
            chart_data = self._prepare_chart_data(
                result_df, 
                indicator_configs, 
                request.chart_type,
                request.include_volume,
                chart_settings
            )
            
            # Prepare indicator data for chart
            indicator_data = self._prepare_indicator_data(result_df, indicator_configs)
            
            # Prepare volume data if requested
            volume_data = None
            if request.include_volume and "Volume" in result_df.columns:
                volume_data = self._prepare_volume_data(result_df)
            
            # Prepare metadata
            metadata = {
                "symbol": request.symbol,
                "period": request.period,
                "interval": request.interval,
                "chart_type": request.chart_type,
                "indicators_count": len([c for c in indicator_configs if c.enabled]),
                "data_points": len(result_df),
                "calculation_errors": len(calculation_errors),
                "performance_metrics": performance_metrics.dict() if performance_metrics else None
            }
            
            return ChartDataResponse(
                symbol=request.symbol,
                chart_type=request.chart_type,
                data=chart_data,
                indicators=indicator_data,
                volume_data=volume_data,
                metadata=metadata
            )
            
        except Exception as e:
            raise ValueError(f"Error generating chart data: {str(e)}")

    def _prepare_chart_data(
        self, 
        df: pl.DataFrame, 
        indicator_configs: List[IndicatorConfiguration],
        chart_type: str,
        include_volume: bool,
        chart_settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare chart data structure."""
        # Base chart data
        chart_data = {
            "type": chart_type,
            "data": []
        }
        
        # Prepare candlestick data
        if chart_type == "candlestick":
            candlestick_data = []
            for row in df.to_dicts():
                if all(col in row for col in ["Open", "High", "Low", "Close", "Date"]):
                    candlestick_data.append({
                        "x": row["Date"].isoformat() if isinstance(row["Date"], datetime) else str(row["Date"]),
                        "open": float(row["Open"]),
                        "high": float(row["High"]),
                        "low": float(row["Low"]),
                        "close": float(row["Close"])
                    })
            chart_data["data"] = candlestick_data
        
        # Prepare line chart data
        elif chart_type == "line":
            line_data = []
            for row in df.to_dicts():
                if "Close" in row and "Date" in row:
                    line_data.append({
                        "x": row["Date"].isoformat() if isinstance(row["Date"], datetime) else str(row["Date"]),
                        "y": float(row["Close"])
                    })
            chart_data["data"] = line_data
        
        # Add chart settings
        chart_data.update(chart_settings)
        
        return chart_data

    def _prepare_indicator_data(
        self, 
        df: pl.DataFrame, 
        indicator_configs: List[IndicatorConfiguration]
    ) -> List[Dict[str, Any]]:
        """Prepare indicator data for chart display."""
        indicator_data = []
        
        for config in indicator_configs:
            if not config.enabled:
                continue
                
            # Get indicator definition to find output columns
            indicator_def = self.indicator_registry.get_indicator_definition(config.indicator_name)
            if not indicator_def:
                continue
            
            # Prepare data for each output column
            for output_col in indicator_def.output_columns:
                if output_col in df.columns:
                    data_points = []
                    for row in df.to_dicts():
                        if output_col in row and row[output_col] is not None:
                            data_points.append({
                                "x": row["Date"].isoformat() if isinstance(row["Date"], datetime) else str(row["Date"]),
                                "y": float(row[output_col])
                            })
                    
                    if data_points:
                        indicator_data.append({
                            "name": config.display_name or f"{config.indicator_name}_{output_col}",
                            "indicator_name": config.indicator_name,
                            "output_column": output_col,
                            "data": data_points,
                            "color": config.color or "#000000",
                            "line_style": config.line_style or "solid",
                            "line_width": config.line_width or 1,
                            "y_axis": config.y_axis or "secondary"
                        })
        
        return indicator_data

    def _prepare_volume_data(self, df: pl.DataFrame) -> List[Dict[str, Any]]:
        """Prepare volume data for chart."""
        volume_data = []
        
        for row in df.to_dicts():
            if "Volume" in row and "Date" in row and row["Volume"] is not None:
                volume_data.append({
                    "x": row["Date"].isoformat() if isinstance(row["Date"], datetime) else str(row["Date"]),
                    "y": float(row["Volume"])
                })
        
        return volume_data

    def _prepare_price_data(self, df: pl.DataFrame) -> List[Dict[str, Any]]:
        """Prepare price data for candlestick charts."""
        price_data = []
        
        for row in df.to_dicts():
            if all(col in row for col in ["Open", "High", "Low", "Close", "Date"]):
                price_data.append({
                    "date": row["Date"].isoformat() if isinstance(row["Date"], datetime) else str(row["Date"]),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": float(row.get("Volume", 0)) if "Volume" in row else None,
                    "adjusted_close": float(row.get("Adj Close", row["Close"])) if "Adj Close" in row else None
                })
        
        return price_data

    def _prepare_indicator_series(self, df: pl.DataFrame, indicator_configs: List[IndicatorConfiguration]) -> List[Dict[str, Any]]:
        """Prepare indicator series data for charts."""
        indicator_series = []
        
        for config in indicator_configs:
            if not config.enabled or not config.id:
                continue
                
            # Get indicator definition to find output columns
            indicator_def = self.indicator_registry.get_indicator_definition(config.indicator_name)
            if not indicator_def:
                continue
            
            # Prepare data for each output column
            for output_col in indicator_def.output_columns:
                col_name = f"{output_col}_{config.id}"
                if col_name in df.columns:
                    data_points = []
                    for row in df.to_dicts():
                        if col_name in row and row[col_name] is not None:
                            data_points.append({
                                "date": row["Date"].isoformat() if isinstance(row["Date"], datetime) else str(row["Date"]),
                                "value": float(row[col_name]),
                                "formatted_value": f"{row[col_name]:.2f}",
                                "metadata": {"indicator_id": config.id, "parameter": output_col}
                            })
                    
                    if data_points:
                        indicator_series.append({
                            "id": f"{config.id}_{output_col}",
                            "indicator_name": config.indicator_name,
                            "display_name": f"{config.display_name or config.indicator_name} ({output_col})",
                            "data": data_points,
                            "color": config.color or "#000000",
                            "line_style": config.line_style or "solid",
                            "line_width": config.line_width or 1,
                            "y_axis": config.y_axis or "secondary",
                            "z_index": config.z_index or 0,
                            "opacity": config.opacity or 1.0,
                            "show_in_legend": config.show_in_legend,
                            "group": config.group,
                            "parameters": config.parameters
                        })
        
        return indicator_series

    def _prepare_volume_data(self, df: pl.DataFrame) -> List[Dict[str, Any]]:
        """Prepare volume data for charts."""
        volume_data = []
        
        for row in df.to_dicts():
            if "Volume" in row and "Date" in row and row["Volume"] is not None:
                volume_data.append({
                    "date": row["Date"].isoformat() if isinstance(row["Date"], datetime) else str(row["Date"]),
                    "volume": float(row["Volume"]),
                    "color": "#rgba(0,100,80,0.3)"
                })
        
        return volume_data

    def _prepare_metadata(
        self, 
        symbol: str, 
        period: str, 
        interval: str, 
        df: pl.DataFrame, 
        indicators_count: int,
        performance_metrics: Any
    ) -> Dict[str, Any]:
        """Prepare chart metadata."""
        return {
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "start_date": df["Date"].min().isoformat() if "Date" in df.columns else datetime.now().isoformat(),
            "end_date": df["Date"].max().isoformat() if "Date" in df.columns else datetime.now().isoformat(),
            "total_records": len(df),
            "indicators_count": indicators_count,
            "calculation_time_ms": performance_metrics.calculation_time_ms if performance_metrics else None,
            "data_source": "market_data",
            "last_updated": datetime.now().isoformat()
        }

    async def get_available_indicators(self) -> Dict[str, Any]:
        """Get all available indicators and their definitions."""
        indicators = self.indicator_registry.get_available_indicators()
        categories = self.indicator_registry.get_indicator_categories()
        statistics = self.indicator_registry.get_indicator_statistics()
        
        return {
            "indicators": [ind.dict() for ind in indicators],
            "categories": [cat.value for cat in categories],
            "statistics": statistics
        }

    async def get_predefined_templates(self) -> Dict[str, Any]:
        """Get predefined analysis templates."""
        templates = self.configuration_service.get_predefined_templates()
        return {name: template.dict() for name, template in templates.items()}

    async def create_configuration_from_template(
        self, 
        user_id: int, 
        template_name: str, 
        custom_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a configuration from a predefined template."""
        config = self.configuration_service.create_from_template(
            user_id, template_name, custom_name
        )
        return config.dict() if config else None

    async def validate_indicator_configuration(
        self, 
        config: IndicatorConfiguration
    ) -> List[Dict[str, Any]]:
        """Validate an indicator configuration."""
        errors = self.indicator_registry.validate_indicator_configuration(config)
        return [error.dict() for error in errors]

    async def get_configuration_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get statistics about user's configurations."""
        return self.configuration_service.get_configuration_statistics(user_id)

    async def search_configurations(
        self, 
        query: str, 
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Search configurations."""
        result = self.configuration_service.search_configurations(
            query, user_id, skip, limit
        )
        return result.dict()

    async def get_popular_configurations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get popular public configurations."""
        configs = self.configuration_service.get_popular_configurations(limit)
        return [config.dict() for config in configs]
