"""
Indicator Registry Service
Service for managing and executing statistical indicators dynamically.
"""

import inspect
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Type

import polars as pl
from sqlalchemy.orm import Session

from app.core.schemas.statistical_indicators import (
    IndicatorCalculationError,
    IndicatorCategory,
    IndicatorConfiguration,
    IndicatorDefinition,
    IndicatorParameter,
    IndicatorParameterType,
    IndicatorPerformanceMetrics,
    IndicatorValidationError,
)
from app.utils.indicators.momentum_indicators import MomentumIndicators
from app.utils.indicators.trend_indicators import TrendIndicators
from app.utils.indicators.volatility_indicators import VolatilityIndicators
from app.utils.indicators.volume_indicators import VolumeIndicators


class IndicatorRegistryService:
    """Service for managing and executing statistical indicators."""

    def __init__(self, db: Session):
        self.db = db
        self._indicator_registry: Dict[str, IndicatorDefinition] = {}
        self._indicator_classes: Dict[str, Type] = {}
        self._initialize_registry()

    def _initialize_registry(self) -> None:
        """Initialize the indicator registry with all available indicators."""
        # Register momentum indicators
        self._register_indicator_class(MomentumIndicators, "momentum")
        
        # Register trend indicators
        self._register_indicator_class(TrendIndicators, "trend")
        
        # Register volatility indicators
        self._register_indicator_class(VolatilityIndicators, "volatility")
        
        # Register volume indicators
        self._register_indicator_class(VolumeIndicators, "volume")

    def _register_indicator_class(self, indicator_class: Type, category: str) -> None:
        """Register an indicator class and its methods."""
        class_name = indicator_class.__name__
        self._indicator_classes[class_name] = indicator_class
        
        # Get all methods that end with '_indicator'
        methods = [method for method in dir(indicator_class) 
                  if method.endswith('_indicator') and not method.startswith('_')]
        
        for method_name in methods:
            method = getattr(indicator_class, method_name)
            if not callable(method):
                continue
                
            # Get method signature
            sig = inspect.signature(method)
            
            # Extract parameters
            parameters = []
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                    
                # Determine parameter type
                param_type = IndicatorParameterType.INTEGER
                if param.annotation == bool:
                    param_type = IndicatorParameterType.BOOLEAN
                elif param.annotation == float:
                    param_type = IndicatorParameterType.FLOAT
                elif param.annotation == str:
                    param_type = IndicatorParameterType.STRING
                
                # Get default value
                default_value = param.default if param.default != inspect.Parameter.empty else None
                
                # Determine if required
                required = param.default == inspect.Parameter.empty
                
                # Create parameter definition
                param_def = IndicatorParameter(
                    name=param_name,
                    type=param_type,
                    default_value=default_value,
                    description=f"Parameter {param_name} for {method_name}",
                    required=required
                )
                
                # Add min/max values for common parameters
                if param_name in ['window', 'window_slow', 'window_fast', 'window_sign', 'smooth1', 'smooth2', 'smooth_window']:
                    param_def.min_value = 1
                    param_def.max_value = 200
                elif param_name in ['window_dev', 'multiplier']:
                    param_def.min_value = 0.1
                    param_def.max_value = 10.0
                elif param_name in ['step', 'max_step']:
                    param_def.min_value = 0.001
                    param_def.max_value = 1.0
                elif param_name == 'constant':
                    param_def.min_value = 0.001
                    param_def.max_value = 1.0
                
                parameters.append(param_def)
            
            # Determine required columns based on method name and class
            required_columns = self._get_required_columns(method_name, category)
            
            # Create indicator definition
            indicator_def = IndicatorDefinition(
                name=method_name,
                category=IndicatorCategory(category),
                description=f"{method_name.replace('_', ' ').title()} indicator",
                parameters=parameters,
                output_columns=self._get_output_columns(method_name),
                required_columns=required_columns,
                class_name=class_name,
                method_name=method_name
            )
            
            self._indicator_registry[method_name] = indicator_def

    def _get_required_columns(self, method_name: str, category: str) -> List[str]:
        """Get required columns for an indicator method."""
        base_columns = ["Close"]
        
        if category in ["volatility", "trend"]:
            base_columns.extend(["High", "Low"])
        
        if category == "volume":
            base_columns.append("Volume")
        
        # Specific indicators that need additional columns
        if method_name in ["stoch_oscillator_indicator", "stoch_rsi_indicator"]:
            base_columns.extend(["High", "Low"])
        
        return list(set(base_columns))

    def _get_output_columns(self, method_name: str) -> List[str]:
        """Get output columns for an indicator method."""
        # This is a simplified mapping - in practice, you'd inspect the actual method
        output_mapping = {
            "rsi_indicator": ["RSI"],
            "roc_indicator": ["ROC"],
            "stoch_rsi_indicator": ["stoch_rsi", "stoch_rsi_k", "stoch_rsi_d"],
            "stoch_oscillator_indicator": ["stoch", "stoch_signal"],
            "macd_indicator": ["MACD", "Signal", "Histogram"],
            "adx_indicator": ["ADX", "ADX_pos", "ADX_neg"],
            "aroon_indicator": ["aroon_up", "aroon_down", "aroon_indicator"],
            "psar_indicator": ["psar", "psar_down", "psar_down_indicator", "psar_up", "psar_up_indicator"],
            "cci_indicator": ["CCI"],
            "bollinger_bands_indicator": ["bb_bbm", "bb_bbh", "bb_bbl", "bb_bbhi", "bb_bbli"],
            "average_true_range_indicator": ["average_true_range"],
            "keltner_channel_indicator": ["keltner_channel_mband", "keltner_channel_hband", "keltner_channel_lband", "keltner_channel_pband", "keltner_channel_wband", "keltner_channel_hband_indicator", "keltner_channel_lband_indicator"],
            "mfi_indicator": ["MFI"],
            "vpt_indicator": ["VPT"],
            "vwap_indicator": ["VWAP"],
            "obv_indicator": ["OBV"],
            "force_index_indicator": ["Force_Index"]
        }
        
        return output_mapping.get(method_name, [])

    def get_available_indicators(self) -> List[IndicatorDefinition]:
        """Get all available indicators."""
        return list(self._indicator_registry.values())

    def get_indicators_by_category(self, category: IndicatorCategory) -> List[IndicatorDefinition]:
        """Get indicators by category."""
        return [ind for ind in self._indicator_registry.values() if ind.category == category]

    def get_indicator_definition(self, indicator_name: str) -> Optional[IndicatorDefinition]:
        """Get definition for a specific indicator."""
        return self._indicator_registry.get(indicator_name)

    def validate_indicator_configuration(self, config: IndicatorConfiguration) -> List[IndicatorValidationError]:
        """Validate an indicator configuration."""
        errors = []
        
        # Check if indicator exists
        indicator_def = self.get_indicator_definition(config.indicator_name)
        if not indicator_def:
            errors.append(IndicatorValidationError(
                indicator_name=config.indicator_name,
                parameter_name="indicator_name",
                error_message=f"Indicator '{config.indicator_name}' not found",
                provided_value=config.indicator_name,
                expected_type="valid indicator name"
            ))
            return errors
        
        # Validate parameters
        for param_name, param_value in config.parameters.items():
            param_def = next((p for p in indicator_def.parameters if p.name == param_name), None)
            if not param_def:
                errors.append(IndicatorValidationError(
                    indicator_name=config.indicator_name,
                    parameter_name=param_name,
                    error_message=f"Unknown parameter '{param_name}'",
                    provided_value=param_value,
                    expected_type="valid parameter name"
                ))
                continue
            
            # Type validation
            if param_def.type == IndicatorParameterType.INTEGER:
                if not isinstance(param_value, int):
                    errors.append(IndicatorValidationError(
                        indicator_name=config.indicator_name,
                        parameter_name=param_name,
                        error_message=f"Parameter '{param_name}' must be an integer",
                        provided_value=param_value,
                        expected_type="integer"
                    ))
                elif param_def.min_value is not None and param_value < param_def.min_value:
                    errors.append(IndicatorValidationError(
                        indicator_name=config.indicator_name,
                        parameter_name=param_name,
                        error_message=f"Parameter '{param_name}' must be >= {param_def.min_value}",
                        provided_value=param_value,
                        expected_type=f"integer >= {param_def.min_value}"
                    ))
                elif param_def.max_value is not None and param_value > param_def.max_value:
                    errors.append(IndicatorValidationError(
                        indicator_name=config.indicator_name,
                        parameter_name=param_name,
                        error_message=f"Parameter '{param_name}' must be <= {param_def.max_value}",
                        provided_value=param_value,
                        expected_type=f"integer <= {param_def.max_value}"
                    ))
            
            elif param_def.type == IndicatorParameterType.FLOAT:
                if not isinstance(param_value, (int, float)):
                    errors.append(IndicatorValidationError(
                        indicator_name=config.indicator_name,
                        parameter_name=param_name,
                        error_message=f"Parameter '{param_name}' must be a number",
                        provided_value=param_value,
                        expected_type="float"
                    ))
                elif param_def.min_value is not None and param_value < param_def.min_value:
                    errors.append(IndicatorValidationError(
                        indicator_name=config.indicator_name,
                        parameter_name=param_name,
                        error_message=f"Parameter '{param_name}' must be >= {param_def.min_value}",
                        provided_value=param_value,
                        expected_type=f"float >= {param_def.min_value}"
                    ))
                elif param_def.max_value is not None and param_value > param_def.max_value:
                    errors.append(IndicatorValidationError(
                        indicator_name=config.indicator_name,
                        parameter_name=param_name,
                        error_message=f"Parameter '{param_name}' must be <= {param_def.max_value}",
                        provided_value=param_value,
                        expected_type=f"float <= {param_def.max_value}"
                    ))
            
            elif param_def.type == IndicatorParameterType.BOOLEAN:
                if not isinstance(param_value, bool):
                    errors.append(IndicatorValidationError(
                        indicator_name=config.indicator_name,
                        parameter_name=param_name,
                        error_message=f"Parameter '{param_name}' must be a boolean",
                        provided_value=param_value,
                        expected_type="boolean"
                    ))
        
        # Check for missing required parameters
        for param_def in indicator_def.parameters:
            if param_def.required and param_def.name not in config.parameters:
                errors.append(IndicatorValidationError(
                    indicator_name=config.indicator_name,
                    parameter_name=param_def.name,
                    error_message=f"Required parameter '{param_def.name}' is missing",
                    provided_value=None,
                    expected_type=param_def.type.value
                ))
        
        return errors

    def calculate_indicators(
        self, 
        data: pl.DataFrame, 
        configurations: List[IndicatorConfiguration]
    ) -> Tuple[pl.DataFrame, List[IndicatorCalculationError], IndicatorPerformanceMetrics]:
        """Calculate indicators based on configurations."""
        start_time = time.time()
        errors = []
        result_df = data.copy()
        
        # Generate unique IDs for indicators that don't have them
        for i, config in enumerate(configurations):
            if not config.id:
                config.id = f"{config.indicator_name}_{i}_{hash(str(config.parameters))}"
        
        # Group indicators by class for efficient processing
        indicators_by_class = {}
        for config in configurations:
            if not config.enabled:
                continue
                
            indicator_def = self.get_indicator_definition(config.indicator_name)
            if not indicator_def:
                errors.append(IndicatorCalculationError(
                    symbol="unknown",
                    indicator_name=config.indicator_name,
                    error_message=f"Indicator '{config.indicator_name}' not found",
                    error_type="IndicatorNotFound",
                    timestamp=datetime.now()
                ))
                continue
            
            class_name = indicator_def.class_name
            if class_name not in indicators_by_class:
                indicators_by_class[class_name] = []
            indicators_by_class[class_name].append((config, indicator_def))
        
        # Process each indicator class
        for class_name, indicator_configs in indicators_by_class.items():
            try:
                indicator_class = self._indicator_classes[class_name]
                indicator_instance = indicator_class(result_df)
                
                for config, indicator_def in indicator_configs:
                    try:
                        method = getattr(indicator_instance, indicator_def.method_name)
                        temp_df = method(**config.parameters)
                        
                        # Rename columns to include the indicator ID for multiple instances
                        if config.id:
                            output_columns = indicator_def.output_columns
                            for col in output_columns:
                                if col in temp_df.columns:
                                    new_col_name = f"{col}_{config.id}"
                                    temp_df = temp_df.rename({col: new_col_name})
                        
                        # Merge the results back to the main dataframe
                        for col in temp_df.columns:
                            if col not in result_df.columns:
                                result_df = result_df.with_columns([temp_df[col].alias(col)])
                            else:
                                # Update existing column
                                result_df = result_df.with_columns([temp_df[col].alias(col)])
                        
                    except Exception as e:
                        errors.append(IndicatorCalculationError(
                            symbol="unknown",
                            indicator_name=config.indicator_name,
                            error_message=str(e),
                            error_type=type(e).__name__,
                            timestamp=datetime.now()
                        ))
                        
            except Exception as e:
                for config, _ in indicator_configs:
                    errors.append(IndicatorCalculationError(
                        symbol="unknown",
                        indicator_name=config.indicator_name,
                        error_message=f"Failed to initialize {class_name}: {str(e)}",
                        error_type=type(e).__name__,
                        timestamp=datetime.now()
                    ))
        
        # Calculate performance metrics
        end_time = time.time()
        calculation_time_ms = (end_time - start_time) * 1000
        
        # Estimate memory usage (simplified)
        memory_usage_mb = result_df.estimated_size() / (1024 * 1024) if hasattr(result_df, 'estimated_size') else 0
        
        performance_metrics = IndicatorPerformanceMetrics(
            calculation_time_ms=calculation_time_ms,
            memory_usage_mb=memory_usage_mb,
            data_points_processed=len(result_df),
            indicators_calculated=len([c for c in configurations if c.enabled]),
            success_rate=1.0 - (len(errors) / max(len(configurations), 1))
        )
        
        return result_df, errors, performance_metrics

    def get_indicator_categories(self) -> List[IndicatorCategory]:
        """Get all available indicator categories."""
        return list(IndicatorCategory)

    def search_indicators(self, query: str) -> List[IndicatorDefinition]:
        """Search indicators by name or description."""
        query_lower = query.lower()
        results = []
        
        for indicator in self._indicator_registry.values():
            if (query_lower in indicator.name.lower() or 
                query_lower in indicator.description.lower()):
                results.append(indicator)
        
        return results

    def get_indicator_statistics(self) -> Dict[str, Any]:
        """Get statistics about available indicators."""
        total_indicators = len(self._indicator_registry)
        categories = {}
        
        for indicator in self._indicator_registry.values():
            category = indicator.category.value
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
        
        return {
            "total_indicators": total_indicators,
            "categories": categories,
            "indicators_with_parameters": len([i for i in self._indicator_registry.values() if i.parameters]),
            "indicators_requiring_volume": len([i for i in self._indicator_registry.values() if "Volume" in i.required_columns]),
            "indicators_requiring_high_low": len([i for i in self._indicator_registry.values() if "High" in i.required_columns and "Low" in i.required_columns])
        }
