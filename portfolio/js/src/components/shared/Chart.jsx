import {
    createChart,
    CandlestickSeries,
    LineSeries,
    AreaSeries,
    HistogramSeries
} from 'lightweight-charts';
import { BarChart3, RefreshCw } from 'lucide-react';
import React, { useEffect, useMemo, useRef } from 'react';

const Chart = ({
    data = [],
    symbol = '',
    period = '30d',
    onPeriodChange,
    height = 400,
    showVolume = true,
    loading = false,
    onRefresh,
    showControls = true,
    showPeriodSelector = true,
    chartType = 'candlestick',
    theme = 'dark',
    className = '',
}) => {
    const chartContainerRef = useRef(null);

    const { candlestickData, volumeData } = useMemo(() => {
        if (!data || data.length === 0) {
            return { candlestickData: [], volumeData: [] };
        }
        const sortedData = [...data].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

        const cData = sortedData.map(item => ({
            time: new Date(item.date).getTime() / 1000,
            open: item.open,
            high: item.high,
            low: item.low,
            close: item.close,
        }));

        const vData = sortedData.map(item => ({
            time: new Date(item.date).getTime() / 1000,
            value: item.volume,
            color: item.close >= item.open ? 'rgba(38, 166, 154, 0.5)' : 'rgba(239, 83, 80, 0.5)',
        }));

        return { candlestickData: cData, volumeData: vData };
    }, [data]);

    useEffect(() => {
        if (!chartContainerRef.current || chartContainerRef.current.clientWidth === 0 || candlestickData.length === 0) {
            return;
        }

        const chart = createChart(chartContainerRef.current, {
            width: chartContainerRef.current.clientWidth,
            height: height,
            layout: {
                background: { color: theme === 'dark' ? '#1a1a1a' : '#ffffff' },
                textColor: theme === 'dark' ? '#d1d4dc' : '#191919',
            },
            grid: {
                vertLines: { color: theme === 'dark' ? '#2a2a2a' : '#e1e3e6' },
                horzLines: { color: theme === 'dark' ? '#2a2a2a' : '#e1e3e6' },
            },
            crosshair: { mode: 1 },
            rightPriceScale: { borderColor: theme === 'dark' ? '#485c7b' : '#cccccc' },
            timeScale: {
                borderColor: theme === 'dark' ? '#485c7b' : '#cccccc',
                timeVisible: true,
                secondsVisible: false,
            },
        });

        if (!chart) {
            console.error('Failed to create chart');
            return;
        }

        let priceSeries;

        if (chartType === 'candlestick') {
            try {
                priceSeries = chart.addSeries(CandlestickSeries, {
                    upColor: '#26a69a',
                    downColor: '#ef5350',
                    borderDownColor: '#ef5350',
                    borderUpColor: '#26a69a',
                    wickDownColor: '#ef5350',
                    wickUpColor: '#26a69a',
                });
                priceSeries.setData(candlestickData);
            } catch (error) {
                console.error('Error adding candlestick series:', error);
                return;
            }
        } else if (chartType === 'line' || chartType === 'area') {
            const lineData = candlestickData.map(d => ({ time: d.time, value: d.close }));
            if (chartType === 'area') {
                priceSeries = chart.addSeries(AreaSeries, {
                    topColor: 'rgba(33, 150, 243, 0.3)',
                    bottomColor: 'rgba(33, 150, 243, 0.0)',
                    lineColor: '#2196F3',
                    lineWidth: 2,
                });
            } else {
                priceSeries = chart.addSeries(LineSeries, { color: '#2196F3', lineWidth: 2 });
            }
            priceSeries.setData(lineData);
        }

        if (showVolume) {
            const volumeSeries = chart.addSeries(HistogramSeries, {
                priceFormat: { type: 'volume' },
                priceScaleId: '',
                scaleMargins: { top: 0.8, bottom: 0 },
            });
            volumeSeries.setData(volumeData);
        }

        chart.timeScale().fitContent();

        const handleResize = () => {
            if (chartContainerRef.current) {
                chart.applyOptions({ width: chartContainerRef.current.clientWidth });
            }
        };
        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            chart.remove();
        };

    }, [candlestickData, volumeData, theme, height, showVolume, chartType]);


    const periods = [
        { value: '30d', label: '30 Days' },
        { value: '3mo', label: '3 Months' },
        { value: '6mo', label: '6 Months' },
        { value: 'ytd', label: 'YTD' },
        { value: '1y', label: '1 Year' },
        { value: '5y', label: '5 Years' },
        { value: 'max', label: 'All' }
    ];

    if (loading) {
        return (
            <div className={`flex items-center justify-center ${className}`} style={{ height }}>
                <div className="flex flex-col items-center space-y-2">
                    <RefreshCw className="w-8 h-8 text-primary-400 animate-spin" />
                    <p className="text-gray-400">Loading chart data...</p>
                </div>
            </div>
        );
    }

    return (
        <div className={`relative ${className}`}>
            {showControls && (
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-2">
                        {showPeriodSelector && periods.map(periodOption => (
                            <button
                                key={periodOption.value}
                                onClick={() => onPeriodChange(periodOption.value)}
                                className={`px-3 py-1 text-xs rounded-md transition-colors ${period === periodOption.value
                                    ? 'bg-primary-600 text-white font-semibold'
                                    : 'bg-dark-800 text-gray-400 hover:bg-dark-700'
                                    }`}
                            >
                                {periodOption.label}
                            </button>
                        ))}
                    </div>
                    {onRefresh && (
                        <button
                            onClick={onRefresh}
                            className="p-2 text-gray-400 hover:text-gray-100 hover:bg-dark-700 rounded"
                            title="Refresh data"
                        >
                            <RefreshCw size={16} />
                        </button>
                    )}
                </div>
            )}

            <div ref={chartContainerRef} style={{ height: `${height}px`, width: '100%' }} />

            {(!data || data.length === 0) && !loading && (
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none" style={{ height }}>
                    <div className="flex flex-col items-center space-y-2">
                        <BarChart3 className="w-8 h-8 text-gray-500" />
                        <p className="text-gray-500">No chart data available for this period.</p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Chart;