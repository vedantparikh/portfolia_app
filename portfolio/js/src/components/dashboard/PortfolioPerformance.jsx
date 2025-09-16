import {
    BarChart3,
    Calendar,
    DollarSign,
    RefreshCw,
    Target,
    TrendingUp,
    TrendingDown
} from 'lucide-react';
import React, { useEffect, useState } from 'react';
import {
    formatCurrency,
    formatPercentage,
    getChangeColor,
    getChangeIcon
} from '../../utils/formatters.jsx';

const PortfolioPerformance = ({ portfolios }) => {
    const [performance, setPerformance] = useState({
        totalValue: 0,
        totalCost: 0,
        totalGainLoss: 0,
        totalGainLossPercent: 0,
        dayChange: 0,
        dayChangePercent: 0,
        bestPerformer: null,
        worstPerformer: null,
        loading: true
    });

    useEffect(() => {
        if (portfolios && portfolios.length > 0) {
            calculatePerformance();
        }
    }, [portfolios]);

    const calculatePerformance = async () => {
        try {
            setPerformance(prev => ({ ...prev, loading: true }));

            let totalValue = 0;
            let totalCost = 0;
            let totalDayChange = 0;
            let portfolioPerformances = [];

            // Calculate performance for each portfolio
            for (const portfolio of portfolios) {
                if (portfolio.stats) {
                    const value = portfolio.stats.total_value || 0;
                    const cost = portfolio.stats.total_cost || 0;
                    const dayChange = portfolio.stats.day_change || 0;

                    totalValue += value;
                    totalCost += cost;
                    totalDayChange += dayChange;

                    const gainLoss = value - cost;
                    const gainLossPercent = cost > 0 ? (gainLoss / cost) * 100 : 0;

                    portfolioPerformances.push({
                        ...portfolio,
                        gainLoss,
                        gainLossPercent
                    });
                }
            }

            const totalGainLoss = totalValue - totalCost;
            const totalGainLossPercent = totalCost > 0 ? (totalGainLoss / totalCost) * 100 : 0;
            const dayChangePercent = totalValue > 0 ? (totalDayChange / totalValue) * 100 : 0;

            // Find best and worst performers
            const sortedPerformances = portfolioPerformances.sort((a, b) => b.gainLossPercent - a.gainLossPercent);
            const bestPerformer = sortedPerformances.length > 0 ? sortedPerformances[0] : null;
            const worstPerformer = sortedPerformances.length > 0 ? sortedPerformances[sortedPerformances.length - 1] : null;

            setPerformance({
                totalValue,
                totalCost,
                totalGainLoss,
                totalGainLossPercent,
                dayChange: totalDayChange,
                dayChangePercent,
                bestPerformer,
                worstPerformer,
                loading: false
            });
        } catch (error) {
            console.error('Failed to calculate performance:', error);
            setPerformance(prev => ({ ...prev, loading: false }));
        }
    };


    if (performance.loading) {
        return (
            <div className="card p-6">
                <h3 className="text-lg font-semibold text-gray-100 mb-4">Portfolio Performance</h3>
                <div className="flex items-center justify-center py-8">
                    <RefreshCw className="w-8 h-8 text-primary-400 animate-spin" />
                    <span className="ml-3 text-gray-400">Calculating performance...</span>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Overall Performance */}
            <div className="card p-6">
                <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-semibold text-gray-100">Overall Performance</h3>
                    <button
                        onClick={calculatePerformance}
                        className="p-2 rounded-lg hover:bg-dark-800 transition-colors"
                    >
                        <RefreshCw size={16} className="text-gray-400" />
                    </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-gray-400">Total Value</span>
                            <DollarSign size={16} className="text-gray-400" />
                        </div>
                        <p className="text-2xl font-bold text-gray-100">{formatCurrency(performance.totalValue)}</p>
                    </div>

                    <div>
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-gray-400">Total Gain/Loss</span>
                            {getChangeIcon(performance.totalGainLoss)}
                        </div>
                        <p className={`text-2xl font-bold ${getChangeColor(performance.totalGainLoss)}`}>
                            {formatCurrency(performance.totalGainLoss)}
                        </p>
                    </div>

                    <div>
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-gray-400">Total Return</span>
                            {getChangeIcon(performance.totalGainLossPercent)}
                        </div>
                        <p className={`text-2xl font-bold ${getChangeColor(performance.totalGainLossPercent)}`}>
                            {formatPercentage(performance.totalGainLossPercent)}
                        </p>
                    </div>

                    <div>
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-gray-400">Day Change</span>
                            {getChangeIcon(performance.dayChange)}
                        </div>
                        <p className={`text-2xl font-bold ${getChangeColor(performance.dayChange)}`}>
                            {formatCurrency(performance.dayChange)}
                        </p>
                    </div>
                </div>
            </div>

            {/* Portfolio Breakdown */}
            <div className="card p-6">
                <h3 className="text-lg font-semibold text-gray-100 mb-4">Portfolio Breakdown</h3>

                <div className="space-y-4">
                    {portfolios.map((portfolio) => {
                        const value = portfolio.stats?.total_value || 0;
                        const cost = portfolio.stats?.total_cost || 0;
                        const gainLoss = value - cost;
                        const gainLossPercent = cost > 0 ? (gainLoss / cost) * 100 : 0;
                        const percentage = performance.totalValue > 0 ? (value / performance.totalValue) * 100 : 0;

                        return (
                            <div key={portfolio.id} className="space-y-2">
                                <div className="flex items-center justify-between">
                                    <span className="text-sm font-medium text-gray-100">{portfolio.name}</span>
                                    <div className="text-right">
                                        <span className="text-sm font-medium text-gray-100">{formatCurrency(value)}</span>
                                        <span className={`text-xs ml-2 ${getChangeColor(gainLossPercent)}`}>
                                            {formatPercentage(gainLossPercent)}
                                        </span>
                                    </div>
                                </div>
                                <div className="w-full bg-dark-700 rounded-full h-2">
                                    <div
                                        className="bg-primary-400 h-2 rounded-full transition-all duration-300"
                                        style={{ width: `${percentage}%` }}
                                    />
                                </div>
                                <div className="flex items-center justify-between text-xs text-gray-500">
                                    <span>{percentage.toFixed(1)}% of total</span>
                                    <span>{formatCurrency(gainLoss)} gain/loss</span>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Best & Worst Performers */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Best Performer */}
                {performance.bestPerformer && (
                    <div className="card p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-gray-100">Best Performer</h3>
                            <TrendingUp size={20} className="text-success-400" />
                        </div>

                        <div className="space-y-3">
                            <div>
                                <p className="text-sm font-medium text-gray-100">{performance.bestPerformer.name}</p>
                                <p className="text-xs text-gray-400">{performance.bestPerformer.description || 'No description'}</p>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-gray-400">Return</span>
                                <span className={`text-lg font-bold ${getChangeColor(performance.bestPerformer.gainLossPercent)}`}>
                                    {formatPercentage(performance.bestPerformer.gainLossPercent)}
                                </span>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-gray-400">Value</span>
                                <span className="text-sm font-medium text-gray-100">
                                    {formatCurrency(performance.bestPerformer.stats?.total_value || 0)}
                                </span>
                            </div>
                        </div>
                    </div>
                )}

                {/* Worst Performer */}
                {performance.worstPerformer && performance.worstPerformer.id !== performance.bestPerformer?.id && (
                    <div className="card p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-gray-100">Worst Performer</h3>
                            <TrendingDown size={20} className="text-danger-400" />
                        </div>

                        <div className="space-y-3">
                            <div>
                                <p className="text-sm font-medium text-gray-100">{performance.worstPerformer.name}</p>
                                <p className="text-xs text-gray-400">{performance.worstPerformer.description || 'No description'}</p>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-gray-400">Return</span>
                                <span className={`text-lg font-bold ${getChangeColor(performance.worstPerformer.gainLossPercent)}`}>
                                    {formatPercentage(performance.worstPerformer.gainLossPercent)}
                                </span>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-gray-400">Value</span>
                                <span className="text-sm font-medium text-gray-100">
                                    {formatCurrency(performance.worstPerformer.stats?.total_value || 0)}
                                </span>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Performance Insights */}
            <div className="card p-6">
                <h3 className="text-lg font-semibold text-gray-100 mb-4">Performance Insights</h3>

                <div className="space-y-4">
                    <div className="flex items-start space-x-3 p-3 bg-dark-800 rounded-lg">
                        <BarChart3 size={16} className="text-primary-400 mt-1" />
                        <div>
                            <p className="text-sm font-medium text-gray-100">Diversification</p>
                            <p className="text-xs text-gray-400 mt-1">
                                You have {portfolios.length} portfolio{portfolios.length !== 1 ? 's' : ''} with good diversification across different assets.
                            </p>
                        </div>
                    </div>

                    <div className="flex items-start space-x-3 p-3 bg-dark-800 rounded-lg">
                        <Target size={16} className="text-success-400 mt-1" />
                        <div>
                            <p className="text-sm font-medium text-gray-100">Risk Management</p>
                            <p className="text-xs text-gray-400 mt-1">
                                {performance.totalGainLossPercent >= 0 ? 'Your portfolio is performing well' : 'Consider reviewing your investment strategy'}
                                with a {formatPercentage(performance.totalGainLossPercent)} total return.
                            </p>
                        </div>
                    </div>

                    <div className="flex items-start space-x-3 p-3 bg-dark-800 rounded-lg">
                        <Calendar size={16} className="text-warning-400 mt-1" />
                        <div>
                            <p className="text-sm font-medium text-gray-100">Daily Performance</p>
                            <p className="text-xs text-gray-400 mt-1">
                                Today's change: {formatCurrency(performance.dayChange)} ({formatPercentage(performance.dayChangePercent)})
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PortfolioPerformance;
