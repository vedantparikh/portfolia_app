import {
    AreaSeries,
    CandlestickSeries,
    HistogramSeries,
    LineSeries,
    createChart
} from 'lightweight-charts';
import { BarChart3, Maximize2, Minimize2, RefreshCw } from 'lucide-react';
import React, { useEffect, useMemo, useRef, useState } from 'react';

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
    enableFullscreen = false,
    onFullscreenToggle,
}) => {
    const chartContainerRef = useRef(null);
    const [isFullscreen, setIsFullscreen] = useState(false);

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
            volume: item.volume,
        }));

        const vData = sortedData.map(item => ({
            time: new Date(item.date).getTime() / 1000,
            value: item.volume,
            color: item.close >= item.open ? 'rgba(34, 197, 94, 0.5)' : 'rgba(239, 68, 68, 0.5)',
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
                background: { color: theme === 'dark' ? '#020617' : '#ffffff' },
                textColor: theme === 'dark' ? '#f1f5f9' : '#191919',
            },
            grid: {
                vertLines: { color: theme === 'dark' ? '#334155' : '#e1e3e6' },
                horzLines: { color: theme === 'dark' ? '#334155' : '#e1e3e6' },
            },
            crosshair: {
                mode: 1,
                vertLine: {
                    color: theme === 'dark' ? '#475569' : '#cccccc',
                    width: 1,
                    style: 2,
                },
                horzLine: {
                    color: theme === 'dark' ? '#475569' : '#cccccc',
                    width: 1,
                    style: 2,
                },
            },
            rightPriceScale: {
                borderColor: theme === 'dark' ? '#475569' : '#cccccc',
                textColor: theme === 'dark' ? '#cbd5e1' : '#191919',
            },
            timeScale: {
                borderColor: theme === 'dark' ? '#475569' : '#cccccc',
                timeVisible: true,
                secondsVisible: false,
                textColor: theme === 'dark' ? '#cbd5e1' : '#191919',
            },
        });

        if (!chart) {
            console.error('Failed to create chart');
            return;
        }

        let priceSeries;

        if (chartType === 'candlestick') {
            priceSeries = chart.addSeries(CandlestickSeries, {
                upColor: '#22c55e',
                downColor: '#ef4444',
                borderDownColor: '#dc2626',
                borderUpColor: '#16a34a',
                wickDownColor: '#dc2626',
                wickUpColor: '#16a34a',
            });
            priceSeries.setData(candlestickData);
        } else if (chartType === 'line' || chartType === 'area') {
            const lineData = candlestickData.map(d => ({ time: d.time, value: d.close }));
            if (chartType === 'area') {
                priceSeries = chart.addSeries(AreaSeries, {
                    topColor: 'rgba(14, 165, 233, 0.3)',
                    bottomColor: 'rgba(14, 165, 233, 0.0)',
                    lineColor: '#0ea5e9',
                    lineWidth: 2,
                });
            } else {
                priceSeries = chart.addSeries(LineSeries, {
                    color: '#0ea5e9',
                    lineWidth: 2
                });
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

        const tooltip = document.createElement('div');
        tooltip.className = 'absolute bg-dark-800 border border-dark-600 rounded-lg p-3 shadow-xl z-50 pointer-events-none opacity-0 transition-opacity duration-200';
        tooltip.style.fontSize = '12px';
        tooltip.style.fontFamily = 'Inter, system-ui, sans-serif';
        chartContainerRef.current.appendChild(tooltip);

        const updateTooltip = (param) => {
            if (!param.point || !param.time || !chartContainerRef.current) {
                tooltip.style.opacity = '0';
                return;
            }

            const data = param.seriesData.get(priceSeries);
            if (!data) {
                tooltip.style.opacity = '0';
                return;
            }

            const date = new Date(data.time * 1000).toLocaleDateString();
            const time = new Date(data.time * 1000).toLocaleTimeString();
            let tooltipContent = '';
            if (chartType === 'candlestick') {
                tooltipContent = `
                    <div class="text-gray-100 font-semibold mb-2">${symbol || 'Asset'} - ${date}</div>
                    <div class="space-y-1 text-xs">
                        <div class="flex justify-between"><span class="text-gray-400">Open:</span><span class="text-gray-200">$${data.open?.toFixed(2) || 'N/A'}</span></div>
                        <div class="flex justify-between"><span class="text-gray-400">High:</span><span class="text-success-400">$${data.high?.toFixed(2) || 'N/A'}</span></div>
                        <div class="flex justify-between"><span class="text-gray-400">Low:</span><span class="text-danger-400">$${data.low?.toFixed(2) || 'N/A'}</span></div>
                        <div class="flex justify-between"><span class="text-gray-400">Close:</span><span class="text-gray-200">$${data.close?.toFixed(2) || 'N/A'}</span></div>
                        <div class="flex justify-between"><span class="text-gray-400">Volume:</span><span class="text-gray-200">${data.volume || 'N/A'}</span></div>
                        <div class="flex justify-between"><span class="text-gray-400">Change:</span><span class="${data.close >= data.open ? 'text-success-400' : 'text-danger-400'}">${data.close && data.open ? ((data.close - data.open) / data.open * 100).toFixed(2) + '%' : 'N/A'}</span></div>
                    </div>
                `;
            } else {
                tooltipContent = `
                    <div class="text-gray-100 font-semibold mb-2">${symbol || 'Asset'} - ${date}</div>
                    <div class="space-y-1 text-xs">
                        <div class="flex justify-between"><span class="text-gray-400">Time:</span><span class="text-gray-200">${time}</span></div>
                        <div class="flex justify-between"><span class="text-gray-400">Price:</span><span class="text-primary-400">$${data.value?.toFixed(2) || 'N/A'}</span></div>
                    </div>
                `;
            }
            tooltip.innerHTML = tooltipContent;

            const container = chartContainerRef.current;
            const tooltipWidth = tooltip.offsetWidth;
            const tooltipHeight = tooltip.offsetHeight;
            const margin = 15;

            let left = param.point.x + margin;

            if (left + tooltipWidth > container.clientWidth) {
                left = param.point.x - tooltipWidth - margin;
            }

            let top = param.point.y - tooltipHeight - margin;

            if (top < 0) {
                top = param.point.y + margin;
            }

            tooltip.style.left = `${left}px`;
            tooltip.style.top = `${top}px`;
            tooltip.style.opacity = '1';
        };

        chart.subscribeCrosshairMove(updateTooltip);

        const handleResize = () => {
            if (chartContainerRef.current) {
                chart.applyOptions({ width: chartContainerRef.current.clientWidth });
            }
        };
        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            if (tooltip && tooltip.parentNode) {
                tooltip.parentNode.removeChild(tooltip);
            }
            chart.remove();
        };

    }, [candlestickData, volumeData, theme, height, showVolume, chartType, symbol]);

    const handleFullscreenToggle = () => {
        const newFullscreenState = !isFullscreen;
        setIsFullscreen(newFullscreenState);
        if (onFullscreenToggle) {
            onFullscreenToggle(newFullscreenState);
        }
    };

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
                    <div className="flex items-center space-x-2">
                        {enableFullscreen && (
                            <button
                                onClick={handleFullscreenToggle}
                                className="p-2 text-gray-400 hover:text-gray-100 hover:bg-dark-700 rounded transition-colors"
                                title={isFullscreen ? "Exit fullscreen" : "Enter fullscreen"}
                            >
                                {isFullscreen ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
                            </button>
                        )}
                        {onRefresh && (
                            <button
                                onClick={onRefresh}
                                className="p-2 text-gray-400 hover:text-gray-100 hover:bg-dark-700 rounded transition-colors"
                                title="Refresh data"
                            >
                                <RefreshCw size={16} />
                            </button>
                        )}
                    </div>
                </div>
            )}

            <div
                ref={chartContainerRef}
                style={{
                    height: `${height}px`,
                    width: '100%',
                    position: 'relative'
                }}
                className="bg-dark-950 rounded-lg border border-dark-700 overflow-hidden"
            />

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