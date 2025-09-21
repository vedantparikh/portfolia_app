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
    XCircle
} from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { statisticalIndicatorsAPI } from '../../services/api';
import { formatPercentage } from '../../utils/formatters.jsx';
import EnhancedChart from '../shared/EnhancedChart';

const AssetAnalyticsView = ({
    asset,
    chartData = [],
    selectedConfiguration = null,
    onRefresh,
    height = 500
}) => {
    const [analysisData, setAnalysisData] = useState(null);
    const [indicatorConfigurations, setIndicatorConfigurations] = useState([]);
    const [selectedIndicators, setSelectedIndicators] = useState(['SMA', 'EMA', 'RSI', 'MACD']);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [showAdvancedAnalysis, setShowAdvancedAnalysis] = useState(false);

    useEffect(() => {
        if (asset?.symbol) {
            loadAnalysisData();
            loadIndicatorConfigurations();
        }
    }, [asset?.symbol]);

    const loadAnalysisData = async () => {
        if (!asset?.symbol) return;

        try {
            setLoading(true);
            setError(null);

            // Use the available calculateIndicators endpoint
            const response = await statisticalIndicatorsAPI.calculateIndicators({
                symbol: asset.symbol,
                period: '1y',
                interval: '1d',
                indicators: selectedIndicators.map(indicatorName => ({
                    indicator_name: indicatorName,
                    parameters: {},
                    enabled: true
                }))
            });

            // Transform the response to match expected format
            setAnalysisData({
                indicators: response.indicator_series || [],
                performance: {
                    volatility: 0, // Will be calculated from data
                    sharpe_ratio: 0,
                    max_drawdown: 0,
                    beta: 0
                }
            });
        } catch (err) {
            console.error('Failed to load analysis data:', err);
            setError('Failed to load analysis data');
        } finally {
            setLoading(false);
        }
    };

    const loadIndicatorConfigurations = async () => {
        try {
            const configurations = await statisticalIndicatorsAPI.getConfigurations();
            setIndicatorConfigurations(configurations || []);
        } catch (err) {
            console.error('Failed to load indicator configurations:', err);
        }
    };

    const handleIndicatorChange = (newIndicators) => {
        setSelectedIndicators(newIndicators);
    };

    const handleRefresh = () => {
        loadAnalysisData();
        if (onRefresh) {
            onRefresh();
        }
    };

    const getSignalColor = (signal) => {
        switch (signal?.toLowerCase()) {
            case 'buy':
            case 'strong_buy':
                return 'text-success-400';
            case 'sell':
            case 'strong_sell':
                return 'text-danger-400';
            case 'hold':
            case 'neutral':
                return 'text-warning-400';
            default:
                return 'text-gray-400';
        }
    };

    const getSignalIcon = (signal) => {
        switch (signal?.toLowerCase()) {
            case 'buy':
            case 'strong_buy':
                return <CheckCircle className="w-4 h-4 text-success-400" />;
            case 'sell':
            case 'strong_sell':
                return <XCircle className="w-4 h-4 text-danger-400" />;
            case 'hold':
            case 'neutral':
                return <AlertTriangle className="w-4 h-4 text-warning-400" />;
            default:
                return <Info className="w-4 h-4 text-gray-400" />;
        }
    };

    if (loading) {
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
                <h3 className="text-lg font-semibold text-gray-300 mb-2">Analysis Error</h3>
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
                        {asset?.symbol || 'Asset'} Analysis
                    </h2>
                    <p className="text-gray-400">
                        {asset?.name || 'Asset Name'} - Technical Analysis & Indicators
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
                        <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
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
                    data={chartData}
                    symbol={asset?.symbol}
                    assetId={asset?.id}
                    height={height}
                    showIndicators={true}
                    enableIndicatorConfig={true}
                    defaultIndicators={selectedIndicators}
                    onIndicatorsChange={handleIndicatorChange}
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

                            <div className="space-y-4">
                                {Object.entries(analysisData.signals).map(([indicator, signal]) => (
                                    <div key={indicator} className="flex items-center justify-between p-3 bg-dark-800 rounded-lg">
                                        <div className="flex items-center space-x-3">
                                            {getSignalIcon(signal.signal)}
                                            <div>
                                                <p className="font-medium text-gray-100">{indicator}</p>
                                                <p className="text-sm text-gray-400">
                                                    Strength: {signal.strength || 'N/A'}
                                                </p>
                                            </div>
                                        </div>
                                        <div className="text-right">
                                            <p className={`font-semibold ${getSignalColor(signal.signal)}`}>
                                                {signal.signal || 'N/A'}
                                            </p>
                                            <p className="text-xs text-gray-500">
                                                {signal.confidence ? `${signal.confidence}%` : 'N/A'}
                                            </p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Technical Indicators */}
                    {analysisData.indicators && (
                        <div className="card p-6">
                            <h3 className="text-lg font-semibold text-gray-100 mb-4 flex items-center">
                                <Activity className="w-5 h-5 mr-2 text-primary-400" />
                                Technical Indicators
                            </h3>

                            <div className="space-y-4">
                                {Object.entries(analysisData.indicators).map(([indicator, data]) => (
                                    <div key={indicator} className="p-3 bg-dark-800 rounded-lg">
                                        <div className="flex items-center justify-between mb-2">
                                            <h4 className="font-medium text-gray-100">{indicator}</h4>
                                            <span className={`text-sm font-semibold ${data.value > data.overbought ? 'text-danger-400' :
                                                data.value < data.oversold ? 'text-success-400' :
                                                    'text-gray-400'
                                                }`}>
                                                {data.value?.toFixed(2) || 'N/A'}
                                            </span>
                                        </div>

                                        {data.overbought && data.oversold && (
                                            <div className="w-full bg-dark-700 rounded-full h-2 mb-2">
                                                <div
                                                    className="bg-primary-400 h-2 rounded-full transition-all duration-300"
                                                    style={{
                                                        width: `${Math.min(100, Math.max(0,
                                                            ((data.value - data.oversold) / (data.overbought - data.oversold)) * 100
                                                        ))}%`
                                                    }}
                                                />
                                            </div>
                                        )}

                                        <div className="flex justify-between text-xs text-gray-400">
                                            <span>Oversold: {data.oversold || 'N/A'}</span>
                                            <span>Overbought: {data.overbought || 'N/A'}</span>
                                        </div>
                                    </div>
                                ))}
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

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        <div className="text-center">
                            <p className="text-sm text-gray-400">Volatility</p>
                            <p className="text-2xl font-bold text-gray-100">
                                {formatPercentage(analysisData.performance.volatility || 0)}
                            </p>
                        </div>

                        <div className="text-center">
                            <p className="text-sm text-gray-400">Sharpe Ratio</p>
                            <p className="text-2xl font-bold text-gray-100">
                                {analysisData.performance.sharpe_ratio?.toFixed(2) || 'N/A'}
                            </p>
                        </div>

                        <div className="text-center">
                            <p className="text-sm text-gray-400">Max Drawdown</p>
                            <p className="text-2xl font-bold text-danger-400">
                                {formatPercentage(analysisData.performance.max_drawdown || 0)}
                            </p>
                        </div>

                        <div className="text-center">
                            <p className="text-sm text-gray-400">Beta</p>
                            <p className="text-2xl font-bold text-gray-100">
                                {analysisData.performance.beta?.toFixed(2) || 'N/A'}
                            </p>
                        </div>
                    </div>
                </div>
            )}

            {/* Advanced Analysis */}
            {showAdvancedAnalysis && analysisData?.advanced && (
                <div className="card p-6">
                    <h3 className="text-lg font-semibold text-gray-100 mb-4 flex items-center">
                        <Settings className="w-5 h-5 mr-2 text-primary-400" />
                        Advanced Analysis
                    </h3>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Momentum Analysis */}
                        {analysisData.advanced.momentum && (
                            <div>
                                <h4 className="font-medium text-gray-100 mb-3">Momentum Analysis</h4>
                                <div className="space-y-2">
                                    {Object.entries(analysisData.advanced.momentum).map(([key, value]) => (
                                        <div key={key} className="flex justify-between">
                                            <span className="text-sm text-gray-400 capitalize">
                                                {key.replace('_', ' ')}
                                            </span>
                                            <span className="text-sm font-medium text-gray-100">
                                                {typeof value === 'number' ? value.toFixed(2) : value}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Volatility Analysis */}
                        {analysisData.advanced.volatility && (
                            <div>
                                <h4 className="font-medium text-gray-100 mb-3">Volatility Analysis</h4>
                                <div className="space-y-2">
                                    {Object.entries(analysisData.advanced.volatility).map(([key, value]) => (
                                        <div key={key} className="flex justify-between">
                                            <span className="text-sm text-gray-400 capitalize">
                                                {key.replace('_', ' ')}
                                            </span>
                                            <span className="text-sm font-medium text-gray-100">
                                                {typeof value === 'number' ? value.toFixed(2) : value}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
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
                                <h4 className="font-medium text-gray-100 mb-2">{config.name}</h4>
                                <p className="text-sm text-gray-400 mb-3">{config.description}</p>

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
