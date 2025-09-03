import {
    Activity,
    AlertTriangle,
    BarChart3,
    CheckCircle,
    Info,
    TrendingDown,
    TrendingUp
} from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { marketAPI } from '../../services/api';

const MarketInsights = () => {
    const [insights, setInsights] = useState({
        topGainers: [],
        topLosers: [],
        mostActive: [],
        marketSentiment: null,
        loading: true
    });

    useEffect(() => {
        loadMarketInsights();
    }, []);

    const loadMarketInsights = async () => {
        try {
            setInsights(prev => ({ ...prev, loading: true }));

            // Load market data
            const [allAssetsResponse, gainersResponse, losersResponse] = await Promise.allSettled([
                marketAPI.getAssets({ limit: 50, sort: 'market_cap' }),
                marketAPI.getAssets({ limit: 10, sort: 'price_change_percentage_24h', order: 'desc' }),
                marketAPI.getAssets({ limit: 10, sort: 'price_change_percentage_24h', order: 'asc' })
            ]);

            const allAssets = allAssetsResponse.status === 'fulfilled' ? allAssetsResponse.value.assets || [] : [];
            const topGainers = gainersResponse.status === 'fulfilled' ? gainersResponse.value.assets || [] : [];
            const topLosers = losersResponse.status === 'fulfilled' ? losersResponse.value.assets || [] : [];

            // Calculate market sentiment
            const positiveChanges = allAssets.filter(asset => (asset.price_change_percentage_24h || 0) > 0).length;
            const negativeChanges = allAssets.filter(asset => (asset.price_change_percentage_24h || 0) < 0).length;
            const totalAssets = allAssets.length;

            const sentiment = {
                bullish: positiveChanges,
                bearish: negativeChanges,
                neutral: totalAssets - positiveChanges - negativeChanges,
                ratio: totalAssets > 0 ? (positiveChanges / totalAssets) * 100 : 50
            };

            // Get most active by volume
            const mostActive = allAssets
                .sort((a, b) => (b.total_volume || 0) - (a.total_volume || 0))
                .slice(0, 5);

            setInsights({
                topGainers: topGainers.slice(0, 5),
                topLosers: topLosers.slice(0, 5),
                mostActive,
                marketSentiment: sentiment,
                loading: false
            });
        } catch (error) {
            console.error('Failed to load market insights:', error);
            setInsights(prev => ({ ...prev, loading: false }));
        }
    };

    const getSentimentColor = (ratio) => {
        if (ratio >= 60) return 'text-success-400';
        if (ratio <= 40) return 'text-danger-400';
        return 'text-warning-400';
    };

    const getSentimentIcon = (ratio) => {
        if (ratio >= 60) return <TrendingUp size={16} className="text-success-400" />;
        if (ratio <= 40) return <TrendingDown size={16} className="text-danger-400" />;
        return <BarChart3 size={16} className="text-warning-400" />;
    };

    const getSentimentText = (ratio) => {
        if (ratio >= 60) return 'Bullish';
        if (ratio <= 40) return 'Bearish';
        return 'Neutral';
    };

    if (insights.loading) {
        return (
            <div className="card p-6">
                <h3 className="text-lg font-semibold text-gray-100 mb-4">Market Insights</h3>
                <div className="flex items-center justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-400"></div>
                    <span className="ml-3 text-gray-400">Loading market data...</span>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Market Sentiment */}
            {insights.marketSentiment && (
                <div className="card p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold text-gray-100">Market Sentiment</h3>
                        <div className="flex items-center space-x-2">
                            {getSentimentIcon(insights.marketSentiment.ratio)}
                            <span className={`font-medium ${getSentimentColor(insights.marketSentiment.ratio)}`}>
                                {getSentimentText(insights.marketSentiment.ratio)}
                            </span>
                        </div>
                    </div>

                    <div className="space-y-3">
                        <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-400">Bullish</span>
                            <span className="text-sm font-medium text-success-400">
                                {insights.marketSentiment.bullish} ({insights.marketSentiment.ratio.toFixed(1)}%)
                            </span>
                        </div>
                        <div className="w-full bg-dark-700 rounded-full h-2">
                            <div
                                className="bg-success-400 h-2 rounded-full transition-all duration-300"
                                style={{ width: `${insights.marketSentiment.ratio}%` }}
                            />
                        </div>
                        <div className="flex items-center justify-between text-xs text-gray-500">
                            <span>Bearish: {insights.marketSentiment.bearish}</span>
                            <span>Neutral: {insights.marketSentiment.neutral}</span>
                        </div>
                    </div>
                </div>
            )}

            {/* Top Gainers & Losers */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Top Gainers */}
                <div className="card p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold text-gray-100">Top Gainers</h3>
                        <TrendingUp size={20} className="text-success-400" />
                    </div>

                    <div className="space-y-3">
                        {insights.topGainers.map((asset, index) => (
                            <div key={asset.id} className="flex items-center justify-between p-3 bg-dark-800 rounded-lg">
                                <div className="flex items-center space-x-3">
                                    <span className="text-sm font-medium text-gray-400">#{index + 1}</span>
                                    <div>
                                        <p className="text-sm font-medium text-gray-100">{asset.symbol}</p>
                                        <p className="text-xs text-gray-400">{asset.name}</p>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <p className="text-sm font-medium text-success-400">
                                        +{(asset.price_change_percentage_24h || 0).toFixed(2)}%
                                    </p>
                                    <p className="text-xs text-gray-400">
                                        ${asset.current_price?.toFixed(2) || 'N/A'}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Top Losers */}
                <div className="card p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold text-gray-100">Top Losers</h3>
                        <TrendingDown size={20} className="text-danger-400" />
                    </div>

                    <div className="space-y-3">
                        {insights.topLosers.map((asset, index) => (
                            <div key={asset.id} className="flex items-center justify-between p-3 bg-dark-800 rounded-lg">
                                <div className="flex items-center space-x-3">
                                    <span className="text-sm font-medium text-gray-400">#{index + 1}</span>
                                    <div>
                                        <p className="text-sm font-medium text-gray-100">{asset.symbol}</p>
                                        <p className="text-xs text-gray-400">{asset.name}</p>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <p className="text-sm font-medium text-danger-400">
                                        {(asset.price_change_percentage_24h || 0).toFixed(2)}%
                                    </p>
                                    <p className="text-xs text-gray-400">
                                        ${asset.current_price?.toFixed(2) || 'N/A'}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Most Active */}
            <div className="card p-6">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-100">Most Active</h3>
                    <Activity size={20} className="text-primary-400" />
                </div>

                <div className="space-y-3">
                    {insights.mostActive.map((asset, index) => (
                        <div key={asset.id} className="flex items-center justify-between p-3 bg-dark-800 rounded-lg">
                            <div className="flex items-center space-x-3">
                                <span className="text-sm font-medium text-gray-400">#{index + 1}</span>
                                <div>
                                    <p className="text-sm font-medium text-gray-100">{asset.symbol}</p>
                                    <p className="text-xs text-gray-400">{asset.name}</p>
                                </div>
                            </div>
                            <div className="text-right">
                                <p className="text-sm font-medium text-gray-100">
                                    ${((asset.total_volume || 0) / 1e6).toFixed(2)}M
                                </p>
                                <p className="text-xs text-gray-400">Volume</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Market Alerts */}
            <div className="card p-6">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-100">Market Alerts</h3>
                    <AlertTriangle size={20} className="text-warning-400" />
                </div>

                <div className="space-y-3">
                    <div className="flex items-start space-x-3 p-3 bg-warning-400/10 border border-warning-400/20 rounded-lg">
                        <AlertTriangle size={16} className="text-warning-400 mt-0.5" />
                        <div>
                            <p className="text-sm font-medium text-warning-400">High Volatility Detected</p>
                            <p className="text-xs text-gray-400 mt-1">
                                Market volatility is above normal levels. Consider adjusting your risk management strategy.
                            </p>
                        </div>
                    </div>

                    <div className="flex items-start space-x-3 p-3 bg-success-400/10 border border-success-400/20 rounded-lg">
                        <CheckCircle size={16} className="text-success-400 mt-0.5" />
                        <div>
                            <p className="text-sm font-medium text-success-400">Portfolio Performance</p>
                            <p className="text-xs text-gray-400 mt-1">
                                Your portfolio is outperforming the market by 2.3% this week.
                            </p>
                        </div>
                    </div>

                    <div className="flex items-start space-x-3 p-3 bg-primary-400/10 border border-primary-400/20 rounded-lg">
                        <Info size={16} className="text-primary-400 mt-0.5" />
                        <div>
                            <p className="text-sm font-medium text-primary-400">Market Update</p>
                            <p className="text-xs text-gray-400 mt-1">
                                New economic data released. Review your positions and consider rebalancing.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MarketInsights;
