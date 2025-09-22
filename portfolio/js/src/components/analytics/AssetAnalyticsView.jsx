import {
  Activity,
  AlertTriangle,
  BarChart3,
  CheckCircle,
  Info,
  RefreshCw,
  Settings,
  Target,
  TrendingUp,
  XCircle,
} from "lucide-react";
import React, { useEffect, useState } from "react";
import { statisticalIndicatorsAPI } from "../../services/api";
import { formatPercentage } from "../../utils/formatters.jsx";
import EnhancedChart from "../shared/EnhancedChart";

const AssetAnalyticsView = ({
  asset,
  selectedConfiguration = null,
  onRefresh, // This prop is kept in case the parent needs to know about a refresh
  height = 500,
}) => {
  // FIX: Internal state for period, chart data, and analysis data
  const [period, setPeriod] = useState("30d"); // Default period
  const [chartData, setChartData] = useState([]); // Chart data is now internal state
  const [analysisData, setAnalysisData] = useState(null);
  
  const [indicatorConfigurations, setIndicatorConfigurations] = useState([]);
  const [selectedIndicators, setSelectedIndicators] = useState([
    "rsi_indicator",
    "macd_indicator",
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showAdvancedAnalysis, setShowAdvancedAnalysis] = useState(false);

  // FIX: Load configurations only once when asset changes
  useEffect(() => {
    if (asset?.symbol) {
      loadIndicatorConfigurations();
    }
  }, [asset?.symbol]);

  // FIX: Load analysis AND chart data when asset, period, or indicators change
  useEffect(() => {
    if (asset?.symbol) {
      loadData();
    }
  }, [asset?.symbol, period, selectedIndicators]);

  // FIX: Renamed to loadData, as it fetches both chart and analysis data
  const loadData = async () => {
    if (!asset?.symbol) return;

    try {
      setLoading(true);
      setError(null);

      // Use the available calculateIndicators endpoint
      const response = await statisticalIndicatorsAPI.calculateIndicators({
        symbol: asset.symbol,
        period: period, // FIX: Use period from state
        interval: "1d",
        indicators: selectedIndicators.map((indicatorName) => ({
          indicator_name: indicatorName,
          parameters: {},
          enabled: true,
        })),
      });

      // FIX: Set chart data from the response
      // Assuming 'response.data' contains the OHLCV array as per EnhancedChart fix
      setChartData(response.data || []); 

      // Transform the response to match expected format for analysis panels
      setAnalysisData({
        // 'indicator_series' is for overlays, 'indicators' might be for panels
        // Adjust as needed based on your actual API response structure
        indicators: response.indicator_series || [], 
        performance: {
          volatility: 0, 
          sharpe_ratio: 0,
          max_drawdown: 0,
          beta: 0,
        },
        // Assuming 'indicator_series' is for the chart, 
        // and another property (e.g., 'indicator_values') is for panels.
        // This part needs to match your API response.
        // For this example, we'll assume 'indicator_series' works for both.
        indicatorPanelData: response.indicator_series || {}, 
      });
    } catch (err) {
      console.error("Failed to load analysis data:", err);
      setError("Failed to load analysis data");
    } finally {
      setLoading(false);
    }
  };

  const loadIndicatorConfigurations = async () => {
    try {
      const configurations = await statisticalIndicatorsAPI.getConfigurations();
      setIndicatorConfigurations(configurations || []);
    } catch (err) {
      console.error("Failed to load indicator configurations:", err);
    }
  };

  // FIX: This handler updates the parent's state, triggering the useEffect
  const handlePeriodChange = (newPeriod) => {
    setPeriod(newPeriod);
  };

  const handleIndicatorChange = (newIndicators) => {
    setSelectedIndicators(newIndicators);
    // This will trigger the `loadData` useEffect
  };

  const handleRefresh = () => {
    loadData(); // FIX: Call the combined data-loading function
    if (onRefresh) {
      onRefresh();
    }
  };
  
  // ... (getSignalColor and getSignalIcon remain the same) ...
  const getSignalColor = (signal) => {
    switch (signal?.toLowerCase()) {
      case "buy":
      case "strong_buy":
        return "text-success-400";
      case "sell":
      case "strong_sell":
        return "text-danger-400";
      case "hold":
      case "neutral":
        return "text-warning-400";
      default:
        return "text-gray-400";
    }
  };

  const getSignalIcon = (signal) => {
    switch (signal?.toLowerCase()) {
      case "buy":
      case "strong_buy":
        return <CheckCircle className="w-4 h-4 text-success-400" />;
      case "sell":
      case "strong_sell":
        return <XCircle className="w-4 h-4 text-danger-400" />;
      case "hold":
      case "neutral":
        return <AlertTriangle className="w-4 h-4 text-warning-400" />;
      default:
        return <Info className="w-4 h-4 text-gray-400" />;
    }
  };

  if (loading && chartData.length === 0) { // Only show full-page loader on initial load
    return (
      <div className="flex items-center justify-center py-12">
        <RefreshCw className="w-8 h-8 text-primary-400 animate-spin" />
        <span className="ml-3 text-gray-400">Loading analysis...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="w-16 h-16 text-danger-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-300 mb-2">
          Analysis Error
        </h3>
        <p className="text-gray-500 mb-4">{error}</p>
        <button onClick={handleRefresh} className="btn-primary">
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-100">
            {asset?.symbol || "Asset"} Analysis
          </h2>
          <p className="text-gray-400">
            {asset?.name || "Asset Name"} - Technical Analysis & Indicators
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowAdvancedAnalysis(!showAdvancedAnalysis)}
            className="btn-outline flex items-center space-x-2"
          >
            <Settings size={16} />
            <span>Advanced</span>
          </button>
          <button
            onClick={handleRefresh}
            disabled={loading}
            className="btn-primary flex items-center space-x-2"
          >
            <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Enhanced Chart */}
      <div className="card p-6">
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-gray-100 mb-2 flex items-center">
            <BarChart3 className="w-5 h-5 mr-2 text-primary-400" />
            Price Chart with Indicators
          </h3>
          <p className="text-sm text-gray-400">
            Interactive chart with technical indicators and analysis tools
          </p>
        </div>

        <EnhancedChart
          data={chartData} // FIX: Pass data from state
          period={period} // FIX: Pass period from state
          onPeriodChange={handlePeriodChange} // FIX: Pass handler
          symbol={asset?.symbol}
          assetId={asset?.id}
          height={height}
          loading={loading} // Pass loading state to chart
          showIndicators={true}
          enableIndicatorConfig={true}
          defaultIndicators={selectedIndicators}
          onIndicatorsChange={handleIndicatorChange}
          // FIX: Pass the indicator data we fetched for the overlays
          indicatorOverlayData={analysisData?.indicators}
          showReturns={true}
          enableAnalysis={true}
          onRefresh={handleRefresh}
        />
      </div>

      {/* Analysis Summary */}
      {analysisData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Trading Signals */}
          {analysisData.signals && (
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-100 mb-4 flex items-center">
                <Target className="w-5 h-5 mr-2 text-primary-400" />
                Trading Signals
              </h3>
              {/* ... same as before ... */}
            </div>
          )}

          {/* Technical Indicators */}
          {/* FIX: Use 'analysisData.indicatorPanelData' or adjust key as needed */}
          {analysisData.indicatorPanelData && (
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-100 mb-4 flex items-center">
                <Activity className="w-5 h-5 mr-2 text-primary-400" />
                Technical Indicators
              </h3>

              <div className="space-y-4">
                {/* Note: This assumes your API returns an object of objects with 'value', 'overbought' etc.
                    EnhancedChart's overlay expects an object of *arrays*. 
                    Your 'calculateIndicators' API needs to provide both.
                */}
                {Object.entries(analysisData.indicatorPanelData).map(
                  ([indicator, data]) => (
                    // This assumes 'data' is an object { value, overbought, ... }
                    // If 'data' is an array [ { time, value }, ... ] this will fail
                    // You may need to adjust this based on your API response
                    <div key={indicator} className="p-3 bg-dark-800 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-gray-100">
                          {indicator}
                        </h4>
                        <span
                          className={`text-sm font-semibold ${
                            data.value > data.overbought // This line assumes data is not an array
                              ? "text-danger-400"
                              : data.value < data.oversold
                              ? "text-success-400"
                              : "text-gray-400"
                          }`}
                        >
                          {data.value?.toFixed(2) || "N/A"}
                        </span>
                      </div>
                      {/* ... same as before ... */}
                    </div>
                  )
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Performance Metrics */}
      {analysisData?.performance && (
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-100 mb-4 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-primary-400" />
            Performance Metrics
          </h3>
          {/* ... same as before ... */}
        </div>
      )}

      {/* Advanced Analysis */}
      {showAdvancedAnalysis && analysisData?.advanced && (
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-100 mb-4 flex items-center">
            <Settings className="w-5 h-5 mr-2 text-primary-400" />
            Advanced Analysis
          </h3>
           {/* ... same as before ... */}
        </div>
      )}

      {/* Indicator Configurations */}
      {indicatorConfigurations.length > 0 && (
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-100 mb-4 flex items-center">
            <Settings className="w-5 h-5 mr-2 text-primary-400" />
            Saved Indicator Configurations
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {indicatorConfigurations.map((config) => (
              <div key={config.id} className="p-4 bg-dark-800 rounded-lg">
                <h4 className="font-medium text-gray-100 mb-2">
                  {config.name}
                </h4>
                <p className="text-sm text-gray-400 mb-3">
                  {config.description}
                </p>

                <div className="flex flex-wrap gap-1 mb-3">
                  {config.indicators?.map((indicator) => (
                    <span
                      key={indicator}
                      className="px-2 py-1 bg-primary-600/20 text-primary-400 text-xs rounded-full"
                    >
                      {indicator}
                    </span>
                  ))}
                </div>

                <button
                  onClick={() => setSelectedIndicators(config.indicators || [])}
                  className="btn-outline w-full text-sm"
                >
                  Apply Configuration
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AssetAnalyticsView;