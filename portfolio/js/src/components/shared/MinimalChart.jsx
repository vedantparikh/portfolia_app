import { createChart } from 'lightweight-charts';
import React, { useEffect, useRef } from 'react';

const MinimalChart = ({ data = [], height = 400 }) => {
    const chartContainerRef = useRef(null);
    const chartRef = useRef(null);

    useEffect(() => {
        if (!chartContainerRef.current) return;

        console.log('MinimalChart: Initializing chart');
        console.log('MinimalChart: Data length:', data.length);

        try {
            const chart = createChart(chartContainerRef.current, {
                width: chartContainerRef.current.clientWidth,
                height: height,
                layout: {
                    background: { color: '#1a1a1a' },
                    textColor: '#d1d4dc',
                },
                grid: {
                    vertLines: { color: '#2a2a2a' },
                    horzLines: { color: '#2a2a2a' },
                },
                crosshair: {
                    mode: 1,
                },
                rightPriceScale: {
                    borderColor: '#485c7b',
                },
                timeScale: {
                    borderColor: '#485c7b',
                    timeVisible: true,
                    secondsVisible: false,
                },
            });

            chartRef.current = chart;

            const candlestickSeries = chart.addCandlestickSeries({
                upColor: '#26a69a',
                downColor: '#ef5350',
                borderDownColor: '#ef5350',
                borderUpColor: '#26a69a',
                wickDownColor: '#ef5350',
                wickUpColor: '#26a69a',
            });

            // Process data
            if (data && data.length > 0) {
                const processedData = data
                    .filter(item => item && item.date && item.open && item.high && item.low && item.close)
                    .map(item => ({
                        time: new Date(item.date).getTime() / 1000,
                        open: parseFloat(item.open),
                        high: parseFloat(item.high),
                        low: parseFloat(item.low),
                        close: parseFloat(item.close)
                    }))
                    .filter(item => !isNaN(item.time) && !isNaN(item.open) && !isNaN(item.high) && !isNaN(item.low) && !isNaN(item.close))
                    .sort((a, b) => a.time - b.time);

                console.log('MinimalChart: Processed data length:', processedData.length);

                if (processedData.length > 0) {
                    candlestickSeries.setData(processedData);
                    console.log('MinimalChart: Data set successfully');
                } else {
                    console.warn('MinimalChart: No valid data to display');
                }
            }

            const handleResize = () => {
                if (chartContainerRef.current && chart) {
                    chart.applyOptions({
                        width: chartContainerRef.current.clientWidth,
                    });
                }
            };

            window.addEventListener('resize', handleResize);

            return () => {
                window.removeEventListener('resize', handleResize);
                if (chart) {
                    chart.remove();
                }
            };
        } catch (error) {
            console.error('MinimalChart: Error initializing chart:', error);
        }
    }, [height, data]);

    if (!data || data.length === 0) {
        return (
            <div className="flex items-center justify-center" style={{ height }}>
                <div className="text-gray-400">No data available</div>
            </div>
        );
    }

    return (
        <div className="w-full">
            <div
                ref={chartContainerRef}
                className="w-full"
                style={{ height }}
            />
        </div>
    );
};

export default MinimalChart;
