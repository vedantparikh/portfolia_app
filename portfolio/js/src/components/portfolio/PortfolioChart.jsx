import {
    Activity,
    BarChart3,
    Download,
    PieChart,
    RefreshCw,
    TrendingUp
} from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { analyticsAPI, portfolioAPI } from '../../services/api';
import {
    formatCurrency,
    formatMetricValue,
    formatPercentage,
    getChangeColor
} from '../../utils/formatters.jsx';

const PortfolioChart = ({ portfolio, stats }) => {
    const [chartData, setChartData] = useState(null);
    const [allocationData, setAllocationData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [timeRange, setTimeRange] = useState('1mo');
    const [chartType, setChartType] = useState('line');

    const timeRanges = [
        { value: '1d', label: '1 Day', days: 1 },
        { value: '5d', label: '5 Days', days: 5 },
        { value: '1mo', label: '1 Month', days: 30 },
        { value: '3mo', label: '3 Months', days: 90 },
        { value: '6mo', label: '6 Months', days: 180 },
        { value: '1y', label: '1 Year', days: 365 },
        { value: 'ytd', label: 'YTD', days: 365 },
        { value: 'max', label: 'All Time', days: 9999 }
    ];

    const chartTypes = [
        { value: 'line', label: 'Line Chart', icon: TrendingUp },
        { value: 'bar', label: 'Bar Chart', icon: BarChart3 },
        { value: 'pie', label: 'Allocation', icon: PieChart }
    ];

    useEffect(() => {
        if (portfolio?.id) {
            loadChartData();
            loadAllocationData();
        }
    }, [portfolio, timeRange]);

    const loadChartData = async () => {
        if (!portfolio?.id) return;

        try {
            setLoading(true);
            console.log('[PortfolioChart] Loading chart data for portfolio:', portfolio.id, 'timeRange:', timeRange);

            // Get the current time range configuration
            const currentTimeRange = timeRanges.find(tr => tr.value === timeRange);
            const days = currentTimeRange?.days || 30;

            // Try to get performance history first
            try {
                const historyResponse = await analyticsAPI.getPortfolioPerformanceHistory(portfolio.id, days);
                console.log('[PortfolioChart] Performance history response:', historyResponse);

                if (historyResponse?.history && historyResponse.history.length > 0) {
                    // Process the history data for chart display
                    const processedData = processHistoryData(historyResponse.history);
                    setChartData(processedData);
                    return;
                }
            } catch (historyError) {
                console.warn('[PortfolioChart] Failed to load performance history:', historyError);
            }

            // If all API calls fail, use mock data
            console.log('[PortfolioChart] Using mock data as fallback');
            setChartData(generateMockData());

        } catch (error) {
            console.error('[PortfolioChart] Failed to load chart data:', error);
            setChartData(generateMockData());
        } finally {
            setLoading(false);
        }
    };

    const loadAllocationData = async () => {
        if (!portfolio?.id) return;

        try {
            console.log('[PortfolioChart] Loading allocation data for portfolio:', portfolio.id);

            // Try to get portfolio allocations
            try {
                const allocationsResponse = await analyticsAPI.getPortfolioAllocations(portfolio.id);
                console.log('[PortfolioChart] Allocations response:', allocationsResponse);

                if (allocationsResponse && allocationsResponse.length > 0) {
                    setAllocationData(allocationsResponse);
                    return;
                }
            } catch (allocationError) {
                console.warn('[PortfolioChart] Failed to load allocations:', allocationError);
            }

            // Fallback to portfolio holdings
            try {
                const holdingsResponse = await portfolioAPI.getPortfolioHoldings(portfolio.id);
                console.log('[PortfolioChart] Holdings response:', holdingsResponse);

                if (holdingsResponse && holdingsResponse.length > 0) {
                    // Convert holdings to allocation format
                    const totalValue = holdingsResponse.reduce((sum, holding) => sum + (parseFloat(holding.current_value) || 0), 0);
                    const allocations = holdingsResponse.map(holding => ({
                        asset_id: holding.asset_id,
                        asset_symbol: holding.symbol,
                        asset_name: holding.name,
                        current_percentage: totalValue > 0 ? ((parseFloat(holding.current_value) || 0) / totalValue) * 100 : 0,
                        current_value: parseFloat(holding.current_value) || 0
                    }));

                    setAllocationData(allocations);
                    return;
                }
            } catch (holdingsError) {
                console.warn('[PortfolioChart] Failed to load holdings:', holdingsError);
            }

            // Use mock allocation data as fallback
            setAllocationData(generateMockAllocationData());

        } catch (error) {
            console.error('[PortfolioChart] Failed to load allocation data:', error);
            setAllocationData(generateMockAllocationData());
        }
    };

    // Process performance history data for chart display
    const processHistoryData = (historyData) => {
        if (!historyData || historyData.length === 0) return null;

        const performanceData = historyData.map(item => ({
            date: item.snapshot_date?.split('T')[0] || new Date().toISOString().split('T')[0],
            value: parseFloat(item.total_value) || 0,
            benchmark: parseFloat(item.benchmark_return) || 0
        }));

        const firstValue = performanceData[0]?.value || 0;
        const lastValue = performanceData[performanceData.length - 1]?.value || 0;
        const totalReturn = firstValue > 0 ? ((lastValue - firstValue) / firstValue) * 100 : 0;

        return {
            performance_data: performanceData,
            total_return: totalReturn,
            benchmark_return: performanceData[performanceData.length - 1]?.benchmark || 0,
            volatility: parseFloat(historyData[historyData.length - 1]?.volatility) || 0,
            sharpe_ratio: parseFloat(historyData[historyData.length - 1]?.sharpe_ratio) || 0,
            max_drawdown: parseFloat(historyData[historyData.length - 1]?.max_drawdown) || 0
        };
    };

    // Process performance calculation data for chart display
    const processPerformanceData = (performanceData, period) => {
        if (!performanceData) return null;

        // For performance calculation, we'll generate a simple trend line
        const currentValue = parseFloat(performanceData.current_value) || stats?.totalValue || 100000;
        const totalReturn = performanceData.metrics?.cagr || performanceData.metrics?.total_return || 0;

        // Generate data points based on the period
        const currentTimeRange = timeRanges.find(tr => tr.value === timeRange);
        const days = currentTimeRange?.days || 30;
        const dataPoints = Math.min(days, 100); // Limit to 100 points for performance

        const data = [];
        const startValue = currentValue / (1 + totalReturn / 100);

        for (let i = 0; i < dataPoints; i++) {
            const date = new Date();
            date.setDate(date.getDate() - (dataPoints - i));

            const progress = i / (dataPoints - 1);
            const value = startValue * (1 + (totalReturn / 100) * progress);

            data.push({
                date: date.toISOString().split('T')[0],
                value: value,
                benchmark: startValue * (1 + (totalReturn * 0.8 / 100) * progress) // Slightly lower benchmark
            });
        }

        return {
            performance_data: data,
            total_return: totalReturn,
            benchmark_return: totalReturn * 0.8, // Slightly lower benchmark
            volatility: performanceData.metrics?.volatility || 0,
            sharpe_ratio: performanceData.metrics?.sharpe_ratio || 0,
            max_drawdown: performanceData.metrics?.max_drawdown || 0
        };
    };

    const generateMockData = () => {
        const currentTimeRange = timeRanges.find(tr => tr.value === timeRange);
        const days = currentTimeRange?.days || 30;

        const data = [];
        const startValue = stats?.totalValue || 100000;
        let currentValue = startValue;

        for (let i = 0; i < days; i++) {
            const date = new Date();
            date.setDate(date.getDate() - (days - i));

            // Simulate realistic price movements
            const change = (Math.random() - 0.5) * 0.05; // ±2.5% daily change
            currentValue *= (1 + change);

            data.push({
                date: date.toISOString().split('T')[0],
                value: currentValue,
                benchmark: startValue * (1 + (i * 0.0005)) // Slight upward trend for benchmark
            });
        }

        return {
            performance_data: data,
            total_return: ((currentValue - startValue) / startValue) * 100,
            benchmark_return: ((data[data.length - 1].benchmark - startValue) / startValue) * 100,
            volatility: Math.random() * 20 + 10, // 10-30% volatility
            sharpe_ratio: Math.random() * 2 + 0.5, // 0.5-2.5 Sharpe ratio
            max_drawdown: Math.random() * 15 + 5 // 5-20% max drawdown
        };
    };

    const generateMockAllocationData = () => {
        return [
            { asset_symbol: 'AAPL', asset_name: 'Apple Inc.', current_percentage: 25, current_value: 25000 },
            { asset_symbol: 'MSFT', asset_name: 'Microsoft Corp.', current_percentage: 20, current_value: 20000 },
            { asset_symbol: 'GOOGL', asset_name: 'Alphabet Inc.', current_percentage: 15, current_value: 15000 },
            { asset_symbol: 'TSLA', asset_name: 'Tesla Inc.', current_percentage: 10, current_value: 10000 },
            { asset_symbol: 'AMZN', asset_name: 'Amazon.com Inc.', current_percentage: 10, current_value: 10000 },
            { asset_symbol: 'CASH', asset_name: 'Cash', current_percentage: 20, current_value: 20000 }
        ];
    };

    const renderLineChart = () => {
        if (!chartData?.performance_data || chartData.performance_data.length === 0) {
            return (
                <div className="flex items-center justify-center h-80">
                    <div className="text-center">
                        <TrendingUp size={48} className="text-gray-500 mx-auto mb-4" />
                        <p className="text-gray-400">No performance data available</p>
                    </div>
                </div>
            );
        }

        const data = chartData.performance_data;
        const maxValue = Math.max(...data.map(d => Math.max(d.value || 0, d.benchmark || 0)));
        const minValue = Math.min(...data.map(d => Math.min(d.value || 0, d.benchmark || 0)));
        const range = maxValue - minValue || 1; // Avoid division by zero

        return (
            <div className="h-80 relative">
                <svg className="w-full h-full" viewBox="0 0 800 320">
                    {/* Grid lines */}
                    {[0, 0.25, 0.5, 0.75, 1].map((ratio, i) => (
                        <g key={i}>
                            <line
                                x1="50"
                                y1={50 + ratio * 240}
                                x2="750"
                                y2={50 + ratio * 240}
                                stroke="currentColor"
                                strokeWidth="1"
                                className="text-dark-700"
                            />
                            <text
                                x="40"
                                y={50 + ratio * 240 + 4}
                                textAnchor="end"
                                className="text-xs fill-gray-500"
                            >
                                {formatCurrency(maxValue - (range * ratio))}
                            </text>
                        </g>
                    ))}

                    {/* Portfolio line */}
                    <polyline
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        className="text-primary-400"
                        points={data.map((d, i) =>
                            `${50 + (i / (data.length - 1)) * 700},${50 + ((maxValue - d.value) / range) * 240}`
                        ).join(' ')}
                    />

                    {/* Benchmark line */}
                    <polyline
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeDasharray="5,5"
                        className="text-gray-500"
                        points={data.map((d, i) =>
                            `${50 + (i / (data.length - 1)) * 700},${50 + ((maxValue - d.benchmark) / range) * 240}`
                        ).join(' ')}
                    />

                    {/* Data points */}
                    {data.map((d, i) => (
                        <circle
                            key={i}
                            cx={50 + (i / (data.length - 1)) * 700}
                            cy={50 + ((maxValue - d.value) / range) * 240}
                            r="3"
                            fill="currentColor"
                            className="text-primary-400"
                        />
                    ))}
                </svg>

                {/* Legend */}
                <div className="absolute top-4 right-4 flex space-x-4">
                    <div className="flex items-center space-x-2">
                        <div className="w-4 h-0.5 bg-primary-400"></div>
                        <span className="text-xs text-gray-300">Portfolio</span>
                    </div>
                    <div className="flex items-center space-x-2">
                        <div className="w-4 h-0.5 bg-gray-500 border-dashed border-t border-gray-500"></div>
                        <span className="text-xs text-gray-300">Benchmark</span>
                    </div>
                </div>
            </div>
        );
    };

    const renderBarChart = () => {
        if (!chartData?.performance_data || chartData.performance_data.length === 0) {
            return (
                <div className="flex items-center justify-center h-80">
                    <div className="text-center">
                        <BarChart3 size={48} className="text-gray-500 mx-auto mb-4" />
                        <p className="text-gray-400">No performance data available</p>
                    </div>
                </div>
            );
        }

        const data = chartData.performance_data.slice(-30); // Last 30 data points
        const maxValue = Math.max(...data.map(d => d.value || 0)) || 1; // Avoid division by zero

        return (
            <div className="h-80 flex items-end space-x-1 px-4">
                {data.map((d, i) => {
                    const height = (d.value / maxValue) * 100;
                    return (
                        <div
                            key={i}
                            className="bg-primary-400 rounded-t flex-1 hover:bg-primary-300 transition-colors"
                            style={{ height: `${height}%` }}
                            title={`${d.date}: ${formatCurrency(d.value)}`}
                        />
                    );
                })}
            </div>
        );
    };

    const renderPieChart = () => {
        // Use real allocation data or fallback to mock data
        const allocations = allocationData || generateMockAllocationData();

        // Color palette for different assets
        const colors = [
            'bg-primary-400',
            'bg-success-400',
            'bg-warning-400',
            'bg-danger-400',
            'bg-info-400',
            'bg-purple-400',
            'bg-pink-400',
            'bg-indigo-400'
        ];

        // Process allocation data for pie chart
        const pieData = allocations.map((allocation, index) => ({
            name: allocation.asset_symbol || allocation.asset_name || `Asset ${index + 1}`,
            value: parseFloat(allocation.current_percentage) || 0,
            color: colors[index % colors.length],
            symbol: allocation.asset_symbol || '',
            value_amount: parseFloat(allocation.current_value) || 0
        })).filter(item => item.value > 0); // Only show assets with value

        if (pieData.length === 0) {
            return (
                <div className="h-80 flex items-center justify-center">
                    <div className="text-center">
                        <PieChart size={48} className="text-gray-500 mx-auto mb-4" />
                        <p className="text-gray-400">No allocation data available</p>
                    </div>
                </div>
            );
        }

        return (
            <div className="h-80 flex items-center justify-center">
                <div className="relative w-64 h-64">
                    {/* Simple pie chart representation */}
                    <div className="w-full h-full rounded-full border-8 border-dark-700 relative overflow-hidden">
                        {pieData.map((allocation, index) => {
                            const percentage = allocation.value;
                            const rotation = pieData.slice(0, index).reduce((sum, a) => sum + a.value, 0) * 3.6;

                            return (
                                <div
                                    key={index}
                                    className={`absolute inset-0 ${allocation.color} opacity-80`}
                                    style={{
                                        clipPath: `polygon(50% 50%, 50% 0%, ${50 + 50 * Math.cos((rotation - 90) * Math.PI / 180)}% ${50 + 50 * Math.sin((rotation - 90) * Math.PI / 180)}%)`
                                    }}
                                />
                            );
                        })}
                    </div>

                    {/* Center text */}
                    <div className="absolute inset-0 flex items-center justify-center">
                        <div className="text-center">
                            <div className="text-2xl font-bold text-gray-100">
                                {formatCurrency(stats?.totalValue || 0)}
                            </div>
                            <div className="text-sm text-gray-400">Total Value</div>
                        </div>
                    </div>
                </div>

                {/* Legend */}
                <div className="ml-8 space-y-2 max-h-64 overflow-y-auto">
                    {pieData.map((allocation, index) => (
                        <div key={index} className="flex items-center space-x-3">
                            <div className={`w-4 h-4 rounded ${allocation.color}`}></div>
                            <div className="flex-1 min-w-0">
                                <div className="text-sm text-gray-300 truncate">{allocation.name}</div>
                                {allocation.symbol && (
                                    <div className="text-xs text-gray-500">{allocation.symbol}</div>
                                )}
                            </div>
                            <div className="text-right">
                                <div className="text-sm font-medium text-gray-100">{allocation.value.toFixed(1)}%</div>
                                <div className="text-xs text-gray-500">{formatCurrency(allocation.value_amount)}</div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        );
    };

    const renderChart = () => {
        switch (chartType) {
            case 'line':
                return renderLineChart();
            case 'bar':
                return renderBarChart();
            case 'pie':
                return renderPieChart();
            default:
                return renderLineChart();
        }
    };

    return (
        <div className="space-y-6">
            {/* Chart Controls */}
            <div className="card p-6">
                <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-semibold text-gray-100">Portfolio Performance</h3>
                    <div className="flex items-center space-x-3">
                        <button
                            onClick={() => {
                                loadChartData();
                                loadAllocationData();
                            }}
                            disabled={loading}
                            className="btn-outline text-sm flex items-center space-x-2"
                        >
                            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
                            <span>Refresh</span>
                        </button>
                        <button className="btn-outline text-sm flex items-center space-x-2">
                            <Download size={16} />
                            <span>Export</span>
                        </button>
                    </div>
                </div>

                {/* Time Range Selector */}
                <div className="flex items-center space-x-2 mb-6">
                    <span className="text-sm text-gray-400">Time Range:</span>
                    {timeRanges.map((range) => (
                        <button
                            key={range.value}
                            onClick={() => setTimeRange(range.value)}
                            className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${timeRange === range.value
                                ? 'bg-primary-600 text-white'
                                : 'bg-dark-700 text-gray-300 hover:bg-dark-600'
                                }`}
                        >
                            {range.label}
                        </button>
                    ))}
                </div>

                {/* Chart Type Selector */}
                <div className="flex items-center space-x-2 mb-6">
                    <span className="text-sm text-gray-400">Chart Type:</span>
                    {chartTypes.map((type) => {
                        const Icon = type.icon;
                        return (
                            <button
                                key={type.value}
                                onClick={() => setChartType(type.value)}
                                className={`flex items-center space-x-2 px-3 py-1 rounded-lg text-sm font-medium transition-colors ${chartType === type.value
                                    ? 'bg-primary-600 text-white'
                                    : 'bg-dark-700 text-gray-300 hover:bg-dark-600'
                                    }`}
                            >
                                <Icon size={16} />
                                <span>{type.label}</span>
                            </button>
                        );
                    })}
                </div>

                {/* Chart */}
                <div className="bg-dark-800 rounded-lg p-4">
                    {loading ? (
                        <div className="flex items-center justify-center h-80">
                            <RefreshCw className="w-8 h-8 text-primary-400 animate-spin" />
                            <span className="ml-2 text-gray-400">Loading chart data...</span>
                        </div>
                    ) : chartData ? (
                        renderChart()
                    ) : (
                        <div className="flex items-center justify-center h-80">
                            <div className="text-center">
                                <BarChart3 size={48} className="text-gray-500 mx-auto mb-4" />
                                <p className="text-gray-400">No chart data available</p>
                                <button
                                    onClick={loadChartData}
                                    className="mt-2 text-primary-400 hover:text-primary-300 text-sm"
                                >
                                    Try again
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Performance Metrics */}
            {chartData && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <div className="card p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-400">Total Return</p>
                                <p className={`text-2xl font-bold ${getChangeColor(chartData.total_return || 0)}`}>
                                    {formatPercentage(chartData.total_return || 0)}
                                </p>
                            </div>
                            <div className="w-12 h-12 bg-primary-600/20 rounded-lg flex items-center justify-center">
                                <TrendingUp size={24} className="text-primary-400" />
                            </div>
                        </div>
                    </div>

                    <div className="card p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-400">Benchmark Return</p>
                                <p className={`text-2xl font-bold ${getChangeColor(chartData.benchmark_return || 0)}`}>
                                    {formatPercentage(chartData.benchmark_return || 0)}
                                </p>
                            </div>
                            <div className="w-12 h-12 bg-gray-600/20 rounded-lg flex items-center justify-center">
                                <BarChart3 size={24} className="text-gray-400" />
                            </div>
                        </div>
                    </div>

                    <div className="card p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-400">Volatility</p>
                                <p className="text-2xl font-bold text-gray-100">
                                    {formatPercentage(chartData.volatility || 0, { precision: 1 })}
                                </p>
                            </div>
                            <div className="w-12 h-12 bg-warning-600/20 rounded-lg flex items-center justify-center">
                                <Activity size={24} className="text-warning-400" />
                            </div>
                        </div>
                    </div>

                    <div className="card p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-400">Sharpe Ratio</p>
                                <p className="text-2xl font-bold text-gray-100">
                                    {formatMetricValue(chartData.sharpe_ratio || 0)}
                                </p>
                            </div>
                            <div className="w-12 h-12 bg-success-600/20 rounded-lg flex items-center justify-center">
                                <TrendingUp size={24} className="text-success-400" />
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default PortfolioChart;
