"""
Chart Data Service
Service for generating chart data with various visualization formats.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import polars as pl
from sqlalchemy.orm import Session

from app.core.schemas.statistical_indicators import (
    ChartDataRequest,
    ChartDataResponse,
    IndicatorConfiguration,
)
from app.core.services.enhanced_statistical_service import EnhancedStatisticalService


class ChartDataService:
    """Service for generating chart data with indicators."""

    def __init__(self, db: Session):
        self.db = db
        self.statistical_service = EnhancedStatisticalService(db)

    async def generate_chart_data(
        self, 
        request: ChartDataRequest
    ) -> ChartDataResponse:
        """Generate comprehensive chart data for visualization."""
        return await self.statistical_service.generate_chart_data(request)

    async def generate_plotly_chart_data(
        self, 
        request: ChartDataRequest
    ) -> Dict[str, Any]:
        """Generate Plotly-compatible chart data."""
        chart_response = await self.generate_chart_data(request)
        
        # Convert to Plotly format
        plotly_data = self._convert_to_plotly_format(chart_response)
        
        return plotly_data

    async def generate_highcharts_data(
        self, 
        request: ChartDataRequest
    ) -> Dict[str, Any]:
        """Generate Highcharts-compatible chart data."""
        chart_response = await self.generate_chart_data(request)
        
        # Convert to Highcharts format
        highcharts_data = self._convert_to_highcharts_format(chart_response)
        
        return highcharts_data

    async def generate_candlestick_chart(
        self, 
        symbol: str,
        period: str = "max",
        interval: str = "1d",
        configuration_id: Optional[int] = None,
        indicators: Optional[List[IndicatorConfiguration]] = None
    ) -> Dict[str, Any]:
        """Generate a candlestick chart with indicators."""
        request = ChartDataRequest(
            symbol=symbol,
            period=period,
            interval=interval,
            configuration_id=configuration_id,
            indicators=indicators,
            chart_type="candlestick",
            include_volume=True
        )
        
        return await self.generate_plotly_chart_data(request)

    async def generate_line_chart(
        self, 
        symbol: str,
        period: str = "max",
        interval: str = "1d",
        configuration_id: Optional[int] = None,
        indicators: Optional[List[IndicatorConfiguration]] = None
    ) -> Dict[str, Any]:
        """Generate a line chart with indicators."""
        request = ChartDataRequest(
            symbol=symbol,
            period=period,
            interval=interval,
            configuration_id=configuration_id,
            indicators=indicators,
            chart_type="line",
            include_volume=True
        )
        
        return await self.generate_plotly_chart_data(request)

    def _convert_to_plotly_format(self, chart_response: ChartDataResponse) -> Dict[str, Any]:
        """Convert chart response to Plotly format."""
        # Main candlestick trace
        main_trace = {
            "type": "candlestick",
            "x": [point["x"] for point in chart_response.data["data"]],
            "open": [point["open"] for point in chart_response.data["data"]],
            "high": [point["high"] for point in chart_response.data["data"]],
            "low": [point["low"] for point in chart_response.data["data"]],
            "close": [point["close"] for point in chart_response.data["data"]],
            "name": chart_response.symbol,
            "yaxis": "y"
        }
        
        # Indicator traces
        indicator_traces = []
        for indicator in chart_response.indicators:
            trace = {
                "type": "scatter",
                "mode": "lines",
                "x": [point["x"] for point in indicator["data"]],
                "y": [point["y"] for point in indicator["data"]],
                "name": indicator["name"],
                "line": {
                    "color": indicator["color"],
                    "dash": indicator["line_style"],
                    "width": indicator["line_width"]
                },
                "yaxis": "y2" if indicator["y_axis"] == "secondary" else "y"
            }
            indicator_traces.append(trace)
        
        # Volume trace
        volume_trace = None
        if chart_response.volume_data:
            volume_trace = {
                "type": "bar",
                "x": [point["x"] for point in chart_response.volume_data],
                "y": [point["y"] for point in chart_response.volume_data],
                "name": "Volume",
                "yaxis": "y3",
                "marker": {"color": "rgba(0,100,80,0.3)"}
            }
        
        # Combine all traces
        data = [main_trace] + indicator_traces
        if volume_trace:
            data.append(volume_trace)
        
        # Layout configuration
        layout = {
            "title": f"{chart_response.symbol} - Technical Analysis",
            "xaxis": {
                "type": "date",
                "rangeslider": {"visible": False}
            },
            "yaxis": {
                "title": "Price",
                "side": "right"
            },
            "yaxis2": {
                "title": "Indicators",
                "side": "right",
                "overlaying": "y"
            },
            "yaxis3": {
                "title": "Volume",
                "side": "right",
                "overlaying": "y",
                "position": 0.95
            },
            "legend": {
                "x": 0,
                "y": 1,
                "xanchor": "left"
            },
            "margin": {"r": 50, "t": 50, "b": 50, "l": 50},
            "height": 600
        }
        
        return {
            "data": data,
            "layout": layout,
            "config": {
                "displayModeBar": True,
                "displaylogo": False,
                "modeBarButtonsToRemove": ["pan2d", "lasso2d", "select2d"]
            }
        }

    def _convert_to_highcharts_format(self, chart_response: ChartDataResponse) -> Dict[str, Any]:
        """Convert chart response to Highcharts format."""
        # Main candlestick series
        ohlc_data = []
        for point in chart_response.data["data"]:
            ohlc_data.append([
                int(datetime.fromisoformat(point["x"].replace("Z", "+00:00")).timestamp() * 1000),
                point["open"],
                point["high"],
                point["low"],
                point["close"]
            ])
        
        # Indicator series
        indicator_series = []
        for indicator in chart_response.indicators:
            series_data = []
            for point in indicator["data"]:
                series_data.append([
                    int(datetime.fromisoformat(point["x"].replace("Z", "+00:00")).timestamp() * 1000),
                    point["y"]
                ])
            
            series = {
                "type": "line",
                "name": indicator["name"],
                "data": series_data,
                "color": indicator["color"],
                "dashStyle": indicator["line_style"],
                "lineWidth": indicator["line_width"],
                "yAxis": 1 if indicator["y_axis"] == "secondary" else 0
            }
            indicator_series.append(series)
        
        # Volume series
        volume_series = None
        if chart_response.volume_data:
            volume_data = []
            for point in chart_response.volume_data:
                volume_data.append([
                    int(datetime.fromisoformat(point["x"].replace("Z", "+00:00")).timestamp() * 1000),
                    point["y"]
                ])
            
            volume_series = {
                "type": "column",
                "name": "Volume",
                "data": volume_data,
                "yAxis": 2,
                "color": "rgba(0,100,80,0.3)"
            }
        
        # Chart configuration
        chart_config = {
            "chart": {
                "type": "candlestick",
                "height": 600
            },
            "title": {
                "text": f"{chart_response.symbol} - Technical Analysis"
            },
            "xAxis": {
                "type": "datetime"
            },
            "yAxis": [
                {
                    "title": {"text": "Price"},
                    "height": "60%"
                },
                {
                    "title": {"text": "Indicators"},
                    "top": "60%",
                    "height": "20%",
                    "offset": 0
                },
                {
                    "title": {"text": "Volume"},
                    "top": "80%",
                    "height": "20%",
                    "offset": 0
                }
            ],
            "series": [
                {
                    "type": "candlestick",
                    "name": chart_response.symbol,
                    "data": ohlc_data
                }
            ] + indicator_series + ([volume_series] if volume_series else []),
            "legend": {
                "enabled": True
            },
            "plotOptions": {
                "candlestick": {
                    "color": "red",
                    "upColor": "green"
                }
            }
        }
        
        return chart_config

    def _generate_react_chart_data(
        self, 
        df: pl.DataFrame, 
        indicator_configs: List[IndicatorConfiguration], 
        chart_type: str,
        include_volume: bool,
        chart_settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate React-optimized chart data."""
        from app.core.schemas.statistical_indicators import (
            ChartMetadata,
            IndicatorDataPoint,
            IndicatorSeries,
            PriceDataPoint,
            ReactChartConfig,
            ReactChartData,
            VolumeDataPoint,
        )

        # Prepare price data
        price_data = []
        for row in df.to_dicts():
            if all(col in row for col in ["Open", "High", "Low", "Close", "Date"]):
                price_data.append(PriceDataPoint(
                    date=row["Date"].isoformat() if isinstance(row["Date"], datetime) else str(row["Date"]),
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=float(row.get("Volume", 0)) if "Volume" in row else None,
                    adjusted_close=float(row.get("Adj Close", row["Close"])) if "Adj Close" in row else None
                ))
        
        # Prepare indicator series
        indicator_series = []
        for config in indicator_configs:
            if not config.enabled or not config.id:
                continue
                
            # Get indicator definition
            indicator_def = self.statistical_service.indicator_registry.get_indicator_definition(config.indicator_name)
            if not indicator_def:
                continue
            
            # Prepare data for each output column
            for output_col in indicator_def.output_columns:
                col_name = f"{output_col}_{config.id}"
                if col_name in df.columns:
                    data_points = []
                    for row in df.to_dicts():
                        if col_name in row and row[col_name] is not None:
                            data_points.append(IndicatorDataPoint(
                                date=row["Date"].isoformat() if isinstance(row["Date"], datetime) else str(row["Date"]),
                                value=float(row[col_name]),
                                formatted_value=f"{row[col_name]:.2f}",
                                metadata={"indicator_id": config.id, "parameter": output_col}
                            ))
                    
                    if data_points:
                        indicator_series.append(IndicatorSeries(
                            id=f"{config.id}_{output_col}",
                            indicator_name=config.indicator_name,
                            display_name=f"{config.display_name or config.indicator_name} ({output_col})",
                            data=data_points,
                            color=config.color or "#000000",
                            line_style=config.line_style or "solid",
                            line_width=config.line_width or 1,
                            y_axis=config.y_axis or "secondary",
                            z_index=config.z_index or 0,
                            opacity=config.opacity or 1.0,
                            show_in_legend=config.show_in_legend,
                            group=config.group,
                            parameters=config.parameters
                        ))
        
        # Prepare volume data
        volume_data = None
        if include_volume and "Volume" in df.columns:
            volume_data = []
            for row in df.to_dicts():
                if "Volume" in row and "Date" in row and row["Volume"] is not None:
                    volume_data.append(VolumeDataPoint(
                        date=row["Date"].isoformat() if isinstance(row["Date"], datetime) else str(row["Date"]),
                        volume=float(row["Volume"]),
                        color="#rgba(0,100,80,0.3)"
                    ))
        
        # Prepare chart configuration
        config = ReactChartConfig(
            height=chart_settings.get("height", 600),
            width=chart_settings.get("width"),
            show_legend=chart_settings.get("show_legend", True),
            show_grid=chart_settings.get("show_grid", True),
            show_crosshair=chart_settings.get("show_crosshair", True),
            theme=chart_settings.get("theme", "light"),
            animation=chart_settings.get("animation", True),
            responsive=chart_settings.get("responsive", True)
        )
        
        # Prepare metadata
        metadata = ChartMetadata(
            symbol="",  # Will be set by caller
            period="",  # Will be set by caller
            interval="",  # Will be set by caller
            start_date=df["Date"].min().isoformat() if "Date" in df.columns else datetime.now().isoformat(),
            end_date=df["Date"].max().isoformat() if "Date" in df.columns else datetime.now().isoformat(),
            total_records=len(df),
            indicators_count=len([c for c in indicator_configs if c.enabled]),
            calculation_time_ms=None,  # Will be set by caller
            data_source="market_data",
            last_updated=datetime.now().isoformat()
        )
        
        return ReactChartData(
            chart_type=chart_type,
            price_data=price_data,
            indicator_series=indicator_series,
            volume_data=volume_data,
            config=config,
            metadata=metadata
        )

    def _generate_plotly_config(
        self, 
        df: pl.DataFrame, 
        indicator_configs: List[IndicatorConfiguration], 
        chart_type: str
    ) -> Dict[str, Any]:
        """Generate Plotly configuration for React components."""
        return {
            "displayModeBar": True,
            "displaylogo": False,
            "modeBarButtonsToRemove": ["pan2d", "lasso2d", "select2d"],
            "responsive": True,
            "toImageButtonOptions": {
                "format": "png",
                "filename": "chart",
                "height": 600,
                "width": 800,
                "scale": 1
            }
        }

    def _generate_highcharts_config(
        self, 
        df: pl.DataFrame, 
        indicator_configs: List[IndicatorConfiguration], 
        chart_type: str
    ) -> Dict[str, Any]:
        """Generate Highcharts configuration for React components."""
        return {
            "chart": {
                "type": chart_type,
                "height": 600,
                "backgroundColor": "transparent"
            },
            "title": {
                "text": None
            },
            "credits": {
                "enabled": False
            },
            "exporting": {
                "enabled": True
            },
            "tooltip": {
                "shared": True,
                "crosshairs": True
            },
            "legend": {
                "enabled": True,
                "align": "center",
                "verticalAlign": "top"
            }
        }

    async def generate_indicator_comparison_chart(
        self,
        symbol: str,
        indicators: List[IndicatorConfiguration],
        period: str = "max",
        interval: str = "1d"
    ) -> Dict[str, Any]:
        """Generate a chart comparing multiple indicators."""
        request = ChartDataRequest(
            symbol=symbol,
            period=period,
            interval=interval,
            indicators=indicators,
            chart_type="line",
            include_volume=False
        )
        
        chart_response = await self.generate_chart_data(request)
        
        # Create comparison chart
        comparison_data = []
        for indicator in chart_response.indicators:
            comparison_data.append({
                "type": "scatter",
                "mode": "lines",
                "x": [point["x"] for point in indicator["data"]],
                "y": [point["y"] for point in indicator["data"]],
                "name": indicator["name"],
                "line": {
                    "color": indicator["color"],
                    "dash": indicator["line_style"],
                    "width": indicator["line_width"]
                }
            })
        
        layout = {
            "title": f"{symbol} - Indicator Comparison",
            "xaxis": {"title": "Date"},
            "yaxis": {"title": "Value"},
            "legend": {"x": 0, "y": 1},
            "height": 500
        }
        
        return {
            "data": comparison_data,
            "layout": layout
        }

    async def generate_heatmap_data(
        self,
        symbols: List[str],
        indicator_name: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> Dict[str, Any]:
        """Generate heatmap data for multiple symbols and one indicator."""
        heatmap_data = []
        
        for symbol in symbols:
            try:
                request = ChartDataRequest(
                    symbol=symbol,
                    period=period,
                    interval=interval,
                    indicators=[IndicatorConfiguration(
                        indicator_name=indicator_name,
                        parameters={},
                        enabled=True
                    )],
                    chart_type="line",
                    include_volume=False
                )
                
                chart_response = await self.generate_chart_data(request)
                
                # Get the latest value for the indicator
                if chart_response.indicators:
                    latest_value = chart_response.indicators[0]["data"][-1]["y"]
                    heatmap_data.append({
                        "symbol": symbol,
                        "value": latest_value,
                        "date": chart_response.indicators[0]["data"][-1]["x"]
                    })
                    
            except Exception:
                # Skip symbols that fail
                continue
        
        return {
            "indicator": indicator_name,
            "data": heatmap_data,
            "period": period,
            "interval": interval
        }
