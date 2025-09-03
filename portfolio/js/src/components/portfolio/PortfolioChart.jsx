import {
    Activity,
    BarChart3,
    Download,
    PieChart,
    RefreshCw,
    TrendingUp
} from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { analyticsAPI } from '../../services/api';

const PortfolioChart = ({ portfolio, stats }) => {
    const [chartData, setChartData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [timeRange, setTimeRange] = useState('1M');
    const [chartType, setChartType] = useState('line');

    const timeRanges = [
        { value: '1D', label: '1 Day' },
        { value: '1W', label: '1 Week' },
        { value: '1M', label: '1 Month' },
        { value: '3M', label: '3 Months' },
        { value: '6M', label: '6 Months' },
        { value: '1Y', label: '1 Year' },
        { value: 'ALL', label: 'All Time' }
    ];

    const chartTypes = [
        { value: 'line', label: 'Line Chart', icon: TrendingUp },
        { value: 'bar', label: 'Bar Chart', icon: BarChart3 },
        { value: 'pie', label: 'Allocation', icon: PieChart }
    ];

    useEffect(() => {
        loadChartData();
    }, [portfolio, timeRange]);

    const loadChartData = async () => {
        try {
            setLoading(true);
            const response = await analyticsAPI.getPortfolioPerformance(portfolio.id, {
                time_range: timeRange,
                include_benchmark: true
            });
            setChartData(response);
        } catch (error) {
            console.error('Failed to load chart data:', error);
            // Use mock data for demonstration
            setChartData(generateMockData());
        } finally {
            setLoading(false);
        }
    };

    const generateMockData = () => {
        const days = timeRange === '1D' ? 1 :
            timeRange === '1W' ? 7 :
                timeRange === '1M' ? 30 :
                    timeRange === '3M' ? 90 :
                        timeRange === '6M' ? 180 :
                            timeRange === '1Y' ? 365 : 730;

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

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount);
    };

    const formatPercentage = (value) => {
        return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
    };

    const getChangeColor = (value) => {
        if (value > 0) return 'text-success-400';
        if (value < 0) return 'text-danger-400';
        return 'text-gray-400';
    };

    const renderLineChart = () => {
        if (!chartData?.performance_data) return null;

        const data = chartData.performance_data;
        const maxValue = Math.max(...data.map(d => Math.max(d.value, d.benchmark)));
        const minValue = Math.min(...data.map(d => Math.min(d.value, d.benchmark)));
        const range = maxValue - minValue;

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
        if (!chartData?.performance_data) return null;

        const data = chartData.performance_data.slice(-30); // Last 30 data points
        const maxValue = Math.max(...data.map(d => d.value));

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
        // Mock allocation data
        const allocations = [
            { name: 'Stocks', value: 60, color: 'bg-primary-400' },
            { name: 'Bonds', value: 25, color: 'bg-success-400' },
            { name: 'Cash', value: 10, color: 'bg-warning-400' },
            { name: 'Other', value: 5, color: 'bg-danger-400' }
        ];

        return (
            <div className="h-80 flex items-center justify-center">
                <div className="relative w-64 h-64">
                    {/* Simple pie chart representation */}
                    <div className="w-full h-full rounded-full border-8 border-dark-700 relative overflow-hidden">
                        {allocations.map((allocation, index) => {
                            const percentage = allocation.value;
                            const rotation = allocations.slice(0, index).reduce((sum, a) => sum + a.value, 0) * 3.6;

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
                <div className="ml-8 space-y-2">
                    {allocations.map((allocation, index) => (
                        <div key={index} className="flex items-center space-x-3">
                            <div className={`w-4 h-4 rounded ${allocation.color}`}></div>
                            <span className="text-sm text-gray-300">{allocation.name}</span>
                            <span className="text-sm font-medium text-gray-100">{allocation.value}%</span>
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
                            onClick={loadChartData}
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
                        </div>
                    ) : (
                        renderChart()
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
                                <p className={`text-2xl font-bold ${getChangeColor(chartData.total_return)}`}>
                                    {formatPercentage(chartData.total_return)}
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
                                <p className={`text-2xl font-bold ${getChangeColor(chartData.benchmark_return)}`}>
                                    {formatPercentage(chartData.benchmark_return)}
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
                                    {chartData.volatility.toFixed(1)}%
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
                                    {chartData.sharpe_ratio.toFixed(2)}
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
