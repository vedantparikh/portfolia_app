import {
    Activity,
    ArrowDownRight,
    ArrowUpRight,
    BarChart3,
    DollarSign,
    ExternalLink,
    Globe,
    RefreshCw,
    TrendingDown,
    TrendingUp,
    X
} from 'lucide-react';
import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { marketAPI } from '../../services/api';

const AssetModal = ({ asset, onClose }) => {
    const [priceHistory, setPriceHistory] = useState([]);
    const [loading, setLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('overview');

    useEffect(() => {
        if (asset) {
            loadPriceHistory();
        }
    }, [asset]);

    const loadPriceHistory = async () => {
        try {
            setLoading(true);
            const response = await marketAPI.getAssetPrices(asset.id, {
                days: 7,
                interval: 'daily'
            });
            setPriceHistory(response.prices || []);
        } catch (error) {
            console.error('Failed to load price history:', error);
            toast.error('Failed to load price history');
        } finally {
            setLoading(false);
        }
    };

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
        if (change > 0) return <TrendingUp size={20} className="text-success-400" />;
        if (change < 0) return <TrendingDown size={20} className="text-danger-400" />;
        return null;
    };

    const getChangeArrow = (change) => {
        if (change > 0) return <ArrowUpRight size={16} className="text-success-400" />;
        if (change < 0) return <ArrowDownRight size={16} className="text-danger-400" />;
        return null;
    };

    const tabs = [
        { id: 'overview', label: 'Overview', icon: BarChart3 },
        { id: 'chart', label: 'Chart', icon: Activity },
        { id: 'details', label: 'Details', icon: Globe }
    ];

    if (!asset) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-dark-900 rounded-xl border border-dark-700 w-full max-w-4xl max-h-[90vh] overflow-hidden">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-dark-700">
                    <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-primary-600/20 rounded-lg flex items-center justify-center">
                            <BarChart3 size={24} className="text-primary-400" />
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold text-gray-100">{asset.symbol}</h2>
                            <p className="text-gray-400">{asset.name}</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 rounded-lg hover:bg-dark-800 transition-colors"
                    >
                        <X size={20} className="text-gray-400" />
                    </button>
                </div>

                {/* Price Section */}
                <div className="p-6 border-b border-dark-700">
                    <div className="flex items-center justify-between">
                        <div>
                            <div className="flex items-center space-x-3 mb-2">
                                <span className="text-3xl font-bold text-gray-100">
                                    {formatPrice(asset.current_price)}
                                </span>
                                <div className="flex items-center space-x-2">
                                    {getChangeIcon(asset.price_change_percentage_24h)}
                                    <span className={`text-lg font-medium ${getChangeColor(asset.price_change_percentage_24h)}`}>
                                        {asset.price_change_percentage_24h ? `${asset.price_change_percentage_24h.toFixed(2)}%` : 'N/A'}
                                    </span>
                                </div>
                            </div>
                            <div className="flex items-center space-x-4 text-sm text-gray-400">
                                <span>24h High: {formatPrice(asset.high_24h)}</span>
                                <span>24h Low: {formatPrice(asset.low_24h)}</span>
                            </div>
                        </div>
                        <button
                            onClick={loadPriceHistory}
                            disabled={loading}
                            className="btn-outline flex items-center space-x-2"
                        >
                            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
                            <span>Refresh</span>
                        </button>
                    </div>
                </div>

                {/* Tabs */}
                <div className="flex border-b border-dark-700">
                    {tabs.map((tab) => {
                        const Icon = tab.icon;
                        return (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`flex items-center space-x-2 px-6 py-4 text-sm font-medium transition-colors ${activeTab === tab.id
                                    ? 'text-primary-400 border-b-2 border-primary-400 bg-primary-600/10'
                                    : 'text-gray-400 hover:text-gray-300 hover:bg-dark-800/50'
                                    }`}
                            >
                                <Icon size={16} />
                                <span>{tab.label}</span>
                            </button>
                        );
                    })}
                </div>

                {/* Tab Content */}
                <div className="p-6 max-h-96 overflow-y-auto">
                    {activeTab === 'overview' && (
                        <div className="space-y-6">
                            {/* Key Metrics */}
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                <div className="card p-4">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-sm text-gray-400">Market Cap</span>
                                        <DollarSign size={16} className="text-gray-400" />
                                    </div>
                                    <p className="text-xl font-semibold text-gray-100">
                                        {formatMarketCap(asset.market_cap)}
                                    </p>
                                </div>

                                <div className="card p-4">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-sm text-gray-400">24h Volume</span>
                                        <Activity size={16} className="text-gray-400" />
                                    </div>
                                    <p className="text-xl font-semibold text-gray-100">
                                        {formatVolume(asset.total_volume)}
                                    </p>
                                </div>

                                <div className="card p-4">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-sm text-gray-400">Circulating Supply</span>
                                        <BarChart3 size={16} className="text-gray-400" />
                                    </div>
                                    <p className="text-xl font-semibold text-gray-100">
                                        {asset.circulating_supply ? `${(asset.circulating_supply / 1e6).toFixed(2)}M` : 'N/A'}
                                    </p>
                                </div>
                            </div>

                            {/* Price Performance */}
                            <div className="card p-6">
                                <h3 className="text-lg font-semibold text-gray-100 mb-4">Price Performance</h3>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    <div className="text-center">
                                        <p className="text-sm text-gray-400 mb-1">1h</p>
                                        <p className={`font-medium ${getChangeColor(asset.price_change_percentage_1h)}`}>
                                            {asset.price_change_percentage_1h ? `${asset.price_change_percentage_1h.toFixed(2)}%` : 'N/A'}
                                        </p>
                                    </div>
                                    <div className="text-center">
                                        <p className="text-sm text-gray-400 mb-1">24h</p>
                                        <p className={`font-medium ${getChangeColor(asset.price_change_percentage_24h)}`}>
                                            {asset.price_change_percentage_24h ? `${asset.price_change_percentage_24h.toFixed(2)}%` : 'N/A'}
                                        </p>
                                    </div>
                                    <div className="text-center">
                                        <p className="text-sm text-gray-400 mb-1">7d</p>
                                        <p className={`font-medium ${getChangeColor(asset.price_change_percentage_7d)}`}>
                                            {asset.price_change_percentage_7d ? `${asset.price_change_percentage_7d.toFixed(2)}%` : 'N/A'}
                                        </p>
                                    </div>
                                    <div className="text-center">
                                        <p className="text-sm text-gray-400 mb-1">30d</p>
                                        <p className={`font-medium ${getChangeColor(asset.price_change_percentage_30d)}`}>
                                            {asset.price_change_percentage_30d ? `${asset.price_change_percentage_30d.toFixed(2)}%` : 'N/A'}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'chart' && (
                        <div className="space-y-4">
                            <div className="card p-6">
                                <h3 className="text-lg font-semibold text-gray-100 mb-4">Price Chart (7 Days)</h3>
                                {loading ? (
                                    <div className="flex items-center justify-center h-64">
                                        <RefreshCw className="w-8 h-8 text-primary-400 animate-spin" />
                                    </div>
                                ) : priceHistory.length > 0 ? (
                                    <div className="h-64 flex items-end space-x-1">
                                        {priceHistory.map((price, index) => {
                                            const maxPrice = Math.max(...priceHistory.map(p => p.price));
                                            const minPrice = Math.min(...priceHistory.map(p => p.price));
                                            const height = ((price.price - minPrice) / (maxPrice - minPrice)) * 100;

                                            return (
                                                <div
                                                    key={index}
                                                    className="bg-primary-400 rounded-t flex-1"
                                                    style={{ height: `${height}%` }}
                                                    title={`${new Date(price.timestamp).toLocaleDateString()}: ${formatPrice(price.price)}`}
                                                />
                                            );
                                        })}
                                    </div>
                                ) : (
                                    <div className="flex items-center justify-center h-64 text-gray-400">
                                        <p>No price history available</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {activeTab === 'details' && (
                        <div className="space-y-4">
                            <div className="card p-6">
                                <h3 className="text-lg font-semibold text-gray-100 mb-4">Asset Details</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <p className="text-sm text-gray-400 mb-1">Symbol</p>
                                        <p className="text-gray-100 font-medium">{asset.symbol}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-gray-400 mb-1">Name</p>
                                        <p className="text-gray-100 font-medium">{asset.name}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-gray-400 mb-1">Category</p>
                                        <p className="text-gray-100 font-medium">{asset.category || 'N/A'}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-gray-400 mb-1">Total Supply</p>
                                        <p className="text-gray-100 font-medium">
                                            {asset.total_supply ? `${(asset.total_supply / 1e6).toFixed(2)}M` : 'N/A'}
                                        </p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-gray-400 mb-1">Max Supply</p>
                                        <p className="text-gray-100 font-medium">
                                            {asset.max_supply ? `${(asset.max_supply / 1e6).toFixed(2)}M` : 'N/A'}
                                        </p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-gray-400 mb-1">Market Cap Rank</p>
                                        <p className="text-gray-100 font-medium">{asset.market_cap_rank || 'N/A'}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between p-6 border-t border-dark-700">
                    <div className="flex items-center space-x-4">
                        <button className="btn-primary flex items-center space-x-2">
                            <ExternalLink size={16} />
                            <span>View on Exchange</span>
                        </button>
                    </div>
                    <div className="flex items-center space-x-3">
                        <button onClick={onClose} className="btn-secondary">
                            Close
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AssetModal;
