import {
    ArrowDownRight,
    ArrowUpRight,
    BarChart3,
    TrendingDown,
    TrendingUp
} from 'lucide-react';
import React from 'react';

const AssetCard = ({ asset, viewMode = 'grid', onClick }) => {
    const formatPrice = (price) => {
        if (price === null || price === undefined) return 'N/A';
        if (price < 0.01) return `$${price.toFixed(6)}`;
        if (price < 1) return `$${price.toFixed(4)}`;
        return `$${price.toFixed(2)}`;
    };

    const formatMarketCap = (marketCap) => {
        if (!marketCap) return 'N/A';
        if (marketCap >= 1e12) return `$${(marketCap / 1e12).toFixed(2)}T`;
        if (marketCap >= 1e9) return `$${(marketCap / 1e9).toFixed(2)}B`;
        if (marketCap >= 1e6) return `$${(marketCap / 1e6).toFixed(2)}M`;
        return `$${marketCap.toFixed(0)}`;
    };

    const formatVolume = (volume) => {
        if (!volume) return 'N/A';
        if (volume >= 1e9) return `$${(volume / 1e9).toFixed(2)}B`;
        if (volume >= 1e6) return `$${(volume / 1e6).toFixed(2)}M`;
        return `$${volume.toFixed(0)}`;
    };

    const getChangeColor = (change) => {
        if (change > 0) return 'text-success-400';
        if (change < 0) return 'text-danger-400';
        return 'text-gray-400';
    };

    const getChangeIcon = (change) => {
        if (change > 0) return <TrendingUp size={16} className="text-success-400" />;
        if (change < 0) return <TrendingDown size={16} className="text-danger-400" />;
        return null;
    };

    const getChangeArrow = (change) => {
        if (change > 0) return <ArrowUpRight size={14} className="text-success-400" />;
        if (change < 0) return <ArrowDownRight size={14} className="text-danger-400" />;
        return null;
    };

    if (viewMode === 'list') {
        return (
            <div
                className="card p-4 hover:bg-dark-800/50 transition-colors cursor-pointer"
                onClick={onClick}
            >
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-primary-600/20 rounded-lg flex items-center justify-center">
                            <BarChart3 size={24} className="text-primary-400" />
                        </div>
                        <div>
                            <h3 className="text-lg font-semibold text-gray-100">{asset.symbol}</h3>
                            <p className="text-sm text-gray-400 truncate max-w-48">{asset.name}</p>
                        </div>
                    </div>

                    <div className="flex items-center space-x-8">
                        <div className="text-right">
                            <p className="text-lg font-semibold text-gray-100">
                                {formatPrice(asset.current_price)}
                            </p>
                            <div className="flex items-center space-x-1">
                                {getChangeIcon(asset.price_change_percentage_24h)}
                                <span className={`text-sm ${getChangeColor(asset.price_change_percentage_24h)}`}>
                                    {asset.price_change_percentage_24h ? `${asset.price_change_percentage_24h.toFixed(2)}%` : 'N/A'}
                                </span>
                            </div>
                        </div>

                        <div className="text-right">
                            <p className="text-sm text-gray-400">Market Cap</p>
                            <p className="text-sm font-medium text-gray-100">
                                {formatMarketCap(asset.market_cap)}
                            </p>
                        </div>

                        <div className="text-right">
                            <p className="text-sm text-gray-400">Volume</p>
                            <p className="text-sm font-medium text-gray-100">
                                {formatVolume(asset.total_volume)}
                            </p>
                        </div>

                        <div className="flex items-center">
                            {getChangeArrow(asset.price_change_percentage_24h)}
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div
            className="card p-6 hover:bg-dark-800/50 transition-all duration-200 cursor-pointer group"
            onClick={onClick}
        >
            <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-primary-600/20 rounded-lg flex items-center justify-center group-hover:bg-primary-600/30 transition-colors">
                        <BarChart3 size={24} className="text-primary-400" />
                    </div>
                    <div>
                        <h3 className="text-lg font-semibold text-gray-100">{asset.symbol}</h3>
                        <p className="text-sm text-gray-400 truncate max-w-32">{asset.name}</p>
                    </div>
                </div>
                <div className="flex items-center">
                    {getChangeArrow(asset.price_change_percentage_24h)}
                </div>
            </div>

            <div className="space-y-3">
                <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Price</span>
                    <span className="text-xl font-bold text-gray-100">
                        {formatPrice(asset.current_price)}
                    </span>
                </div>

                <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">24h Change</span>
                    <div className="flex items-center space-x-1">
                        {getChangeIcon(asset.price_change_percentage_24h)}
                        <span className={`text-sm font-medium ${getChangeColor(asset.price_change_percentage_24h)}`}>
                            {asset.price_change_percentage_24h ? `${asset.price_change_percentage_24h.toFixed(2)}%` : 'N/A'}
                        </span>
                    </div>
                </div>

                <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Market Cap</span>
                    <span className="text-sm font-medium text-gray-100">
                        {formatMarketCap(asset.market_cap)}
                    </span>
                </div>

                <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Volume</span>
                    <span className="text-sm font-medium text-gray-100">
                        {formatVolume(asset.total_volume)}
                    </span>
                </div>
            </div>

            {/* Price change indicator bar */}
            <div className="mt-4 pt-4 border-t border-dark-700">
                <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                    <span>24h Performance</span>
                    <span>{asset.price_change_percentage_24h ? `${asset.price_change_percentage_24h.toFixed(2)}%` : 'N/A'}</span>
                </div>
                <div className="w-full bg-dark-700 rounded-full h-1.5">
                    <div
                        className={`h-1.5 rounded-full transition-all duration-300 ${asset.price_change_percentage_24h > 0
                            ? 'bg-success-400'
                            : asset.price_change_percentage_24h < 0
                                ? 'bg-danger-400'
                                : 'bg-gray-500'
                            }`}
                        style={{
                            width: `${Math.min(Math.abs(asset.price_change_percentage_24h || 0) * 2, 100)}%`
                        }}
                    />
                </div>
            </div>
        </div>
    );
};

export default AssetCard;
