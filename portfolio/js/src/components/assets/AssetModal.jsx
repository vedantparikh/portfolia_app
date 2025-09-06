import {
    Activity,
    BarChart3,
    DollarSign,
    Edit,
    Globe,
    RefreshCw,
    Save,
    TrendingDown,
    TrendingUp,
    X
} from 'lucide-react';
import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { marketAPI } from '../../services/api';
import { SymbolSearch } from '../shared';

const AssetModal = ({ asset, mode = 'view', onClose, onSave }) => {
    const [priceHistory, setPriceHistory] = useState([]);
    const [loading, setLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('overview');
    const [formData, setFormData] = useState({
        symbol: '',
        name: '',
        asset_type: 'EQUITY',
        // Optional fields
        exchange: '',
        sector: '',
        industry: '',
        country: '',
        description: '',
        is_active: true
    });
    const [isEditing, setIsEditing] = useState(false);

    useEffect(() => {
        if (asset) {
            loadPriceHistory();
            // In view mode, we don't need to set isEditing, but we do for edit/create
            if (mode === 'edit') {
                setFormData({
                    ...asset, // Pre-fill with all asset data
                    is_active: asset.is_active !== undefined ? asset.is_active : true
                });
                setIsEditing(true);
            }
        } else if (mode === 'create') {
            setIsEditing(true);
        }
    }, [asset, mode]);

    const loadPriceHistory = async () => {
        if (!asset?.id) return;
        try {
            setLoading(true);
            const response = await marketAPI.getAssetPrices(asset.id, {
                period: '30d',
                interval: '1d'
            });
            setPriceHistory(response.prices || []);
        } catch (error) {
            console.error('Failed to load price history:', error);
            toast.error('Failed to load price history');
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSymbolChange = (value) => {
        setFormData(prev => ({
            ...prev,
            symbol: value
        }));
    };

    const handleSymbolSelect = (suggestion) => {
        setFormData(prev => ({
            ...prev,
            symbol: suggestion.symbol,
            name: suggestion.longname || suggestion.shortname || suggestion.name,
            exchange: suggestion.exchange,
            asset_type: suggestion.quoteType.toUpperCase(),
        }));
    };

    const handleSave = () => {
        if (!formData.symbol || !formData.name || !formData.asset_type) {
            toast.error('Please fill in all required fields (Symbol, Name, Asset Type)');
            return;
        }
        onSave && onSave(formData);
    };

    const handleEdit = () => {
        setIsEditing(true);
    };

    const handleCancel = () => {
        if (mode === 'create') {
            onClose();
        } else {
            setIsEditing(false);
            setFormData({ ...asset, is_active: asset.is_active !== undefined ? asset.is_active : true });
        }
    };

    const formatPrice = (price) => {
        if (price === null || price === undefined) return 'N/A';
        const numPrice = Number(price);
        if (isNaN(numPrice)) return 'N/A';
        if (numPrice < 0.01) return `$${numPrice.toFixed(6)}`;
        if (numPrice < 1) return `$${numPrice.toFixed(4)}`;
        return `$${numPrice.toFixed(2)}`;
    };

    const formatMarketCap = (marketCap) => {
        if (!marketCap) return 'N/A';
        if (marketCap >= 1e12) return `$${(marketCap / 1e12).toFixed(2)}T`;
        if (marketCap >= 1e9) return `$${(marketCap / 1e9).toFixed(2)}B`;
        if (marketCap >= 1e6) return `$${(marketCap / 1e6).toFixed(2)}M`;
        return `$${marketCap.toFixed(0)}`;
    };
    
    // FIX 2: Added the missing 'formatPercentage' function
    const formatPercentage = (value) => {
        if (value === null || value === undefined) return 'N/A';
        const numValue = Number(value);
        if (isNaN(numValue)) return 'N/A';
        return `${(numValue * 100).toFixed(2)}%`;
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
    const tabs = [
        { id: 'overview', label: 'Overview', icon: BarChart3 },
        { id: 'chart', label: 'Chart', icon: Activity },
        { id: 'details', label: 'Details', icon: Globe },
        { id: 'analytics', label: 'Analytics', icon: TrendingUp }
    ];

    if (!asset && mode !== 'create') return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-dark-900 rounded-xl border border-dark-700 w-full max-w-4xl max-h-[90vh] flex flex-col">
                {/* Header */}
                <div className="flex-shrink-0 flex items-center justify-between p-6 border-b border-dark-700">
                    <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-primary-600/20 rounded-lg flex items-center justify-center">
                            <BarChart3 size={24} className="text-primary-400" />
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold text-gray-100">
                                {mode === 'create' ? 'Add New Asset' : asset?.symbol || 'Asset'}
                            </h2>
                            <p className="text-gray-400">
                                {mode === 'create' ? 'Create a new asset entry' : asset?.name || 'Asset Details'}
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 rounded-lg hover:bg-dark-800 transition-colors"
                    >
                        <X size={20} className="text-gray-400" />
                    </button>
                </div>

                {/* Price Section - Only show for view mode */}
                {mode === 'view' && asset && (
                    <div className="flex-shrink-0 p-6 border-b border-dark-700">
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
                )}

                {/* Tabs - Only show for view mode */}
                {mode === 'view' && asset && (
                    <div className="flex-shrink-0 flex border-b border-dark-700">
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
                )}

                {/* Content */}
                <div className="flex-grow p-6 overflow-y-auto">
                    {isEditing ? (
                        /* Edit/Create Form */
                        <div className="space-y-6">
                            {/* FIX 3: Encapsulated all form fields in a single grid container */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {/* Symbol Search */}
                                <div className="md:col-span-2">
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Symbol <span className="text-red-400">*</span>
                                    </label>
                                    <SymbolSearch
                                        value={formData.symbol}
                                        onChange={handleSymbolChange}
                                        onSelect={handleSymbolSelect}
                                        placeholder="e.g., AAPL, BTC"
                                    />
                                </div>

                                {/* Asset Name - Required */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Asset Name <span className="text-red-400">*</span>
                                    </label>
                                    <input
                                        type="text"
                                        name="name"
                                        value={formData.name}
                                        onChange={handleInputChange}
                                        placeholder="e.g., Apple Inc., Bitcoin"
                                        className="input-field w-full"
                                        required
                                    />
                                </div>

                                {/* Asset Type */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Asset Type <span className="text-red-400">*</span>
                                    </label>
                                    <select
                                        name="asset_type"
                                        value={formData.asset_type}
                                        onChange={handleInputChange}
                                        className="input-field w-full"
                                        required
                                    >
                                        <option value="EQUITY">Equity (Stock)</option>
                                        <option value="ETF">ETF</option>
                                        <option value="CRYPTOCURRENCY">Cryptocurrency</option>
                                        <option value="MUTUALFUND">Mutual Fund</option>
                                        <option value="COMMODITY">Commodity</option>
                                        <option value="INDEX">Index</option>
                                        <option value="CASH">Cash</option>
                                        <option value="BOND">Bond</option>
                                        <option value="REAL_ESTATE">Real Estate</option>
                                        <option value="FUTURE">Future</option>
                                        <option value="OPTION">Option</option>
                                        <option value="WARRANT">Warrant</option>
                                        <option value="OTHER">Other</option>
                                    </select>
                                </div>
                                
                                {/* Exchange */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Exchange <span className="text-gray-500">(Optional)</span>
                                    </label>
                                    <input
                                        type="text"
                                        name="exchange"
                                        value={formData.exchange}
                                        onChange={handleInputChange}
                                        placeholder="e.g., NMS, NASDAQ, NYSE"
                                        className="input-field w-full"
                                    />
                                </div>

                                {/* Sector */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Sector <span className="text-gray-500">(Optional)</span>
                                    </label>
                                    <input
                                        type="text"
                                        name="sector"
                                        value={formData.sector}
                                        onChange={handleInputChange}
                                        placeholder="e.g., Technology, Healthcare"
                                        className="input-field w-full"
                                    />
                                </div>

                                {/* Industry */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Industry <span className="text-gray-500">(Optional)</span>
                                    </label>
                                    <input
                                        type="text"
                                        name="industry"
                                        value={formData.industry}
                                        onChange={handleInputChange}
                                        placeholder="e.g., Consumer Electronics, Software"
                                        className="input-field w-full"
                                    />
                                </div>

                                {/* Country */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Country <span className="text-gray-500">(Optional)</span>
                                    </label>
                                    <input
                                        type="text"
                                        name="country"
                                        value={formData.country}
                                        onChange={handleInputChange}
                                        placeholder="e.g., United States, Canada"
                                        className="input-field w-full"
                                    />
                                </div>
                            </div>

                            {/* Description */}
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Description <span className="text-gray-500">(Optional)</span>
                                </label>
                                <textarea
                                    name="description"
                                    value={formData.description}
                                    onChange={handleInputChange}
                                    placeholder="Detailed description of the asset..."
                                    rows={3}
                                    className="input-field w-full"
                                />
                            </div>

                            {/* Is Active */}
                            <div>
                                <label className="flex items-center space-x-3">
                                    <input
                                        type="checkbox"
                                        name="is_active"
                                        checked={formData.is_active}
                                        onChange={(e) => setFormData(prev => ({ ...prev, is_active: e.target.checked }))}
                                        className="w-4 h-4 text-primary-600 bg-gray-700 border-gray-600 rounded focus:ring-primary-500 focus:ring-2"
                                    />
                                    <span className="text-sm font-medium text-gray-300">
                                        Active Asset
                                    </span>
                                </label>
                            </div>
                        </div>
                    ) : (
                        /* View Mode Content */
                        <div className="space-y-6">
                            {activeTab === 'overview' && (
                                <div className="space-y-6">
                                    {/* Key Metrics */}
                                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                        <div className="card p-4">
                                            <div className="flex items-center justify-between mb-2">
                                                <span className="text-sm text-gray-400">Quantity</span>
                                                <BarChart3 size={16} className="text-gray-400" />
                                            </div>
                                            <p className="text-xl font-semibold text-gray-100">
                                                {asset?.quantity || 'N/A'}
                                            </p>
                                        </div>

                                        <div className="card p-4">
                                            <div className="flex items-center justify-between mb-2">
                                                <span className="text-sm text-gray-400">Purchase Price</span>
                                                <DollarSign size={16} className="text-gray-400" />
                                            </div>
                                            <p className="text-xl font-semibold text-gray-100">
                                                {formatPrice(asset?.purchase_price)}
                                            </p>
                                        </div>

                                        <div className="card p-4">
                                            <div className="flex items-center justify-between mb-2">
                                                <span className="text-sm text-gray-400">Total Value</span>
                                                <Activity size={16} className="text-gray-400" />
                                            </div>
                                            <p className="text-xl font-semibold text-gray-100">
                                                {asset?.quantity && asset?.current_price ?
                                                    formatPrice(asset.quantity * asset.current_price) : 'N/A'}
                                            </p>
                                        </div>
                                    </div>

                                    {/* P&L Performance */}
                                    <div className="card p-6">
                                        <h3 className="text-lg font-semibold text-gray-100 mb-4">Profit & Loss</h3>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div>
                                                <p className="text-sm text-gray-400 mb-1">Unrealized P&L</p>
                                                <p className={`text-xl font-semibold ${asset?.quantity && asset?.purchase_price && asset?.current_price ?
                                                    getChangeColor((asset.current_price - asset.purchase_price) * asset.quantity) : 'text-gray-400'}`}>
                                                    {asset?.quantity && asset?.purchase_price && asset?.current_price ?
                                                        formatPrice((asset.current_price - asset.purchase_price) * asset.quantity) : 'N/A'}
                                                </p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-gray-400 mb-1">P&L Percentage</p>
                                                <p className={`text-xl font-semibold ${asset?.quantity && asset?.purchase_price && asset?.current_price ?
                                                    getChangeColor((asset.current_price - asset.purchase_price)) : 'text-gray-400'}`}>
                                                    {asset?.quantity && asset?.purchase_price && asset?.current_price && asset.purchase_price > 0 ?
                                                        `${(((asset.current_price - asset.purchase_price) / asset.purchase_price) * 100).toFixed(2)}%` : 'N/A'}
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                            
                            {activeTab === 'chart' && (
                                <div className="card p-6">
                                    <h3 className="text-lg font-semibold text-gray-100 mb-4">Price Chart (30 Days)</h3>
                                    {loading ? (
                                        <div className="flex items-center justify-center h-64">
                                            <RefreshCw className="w-8 h-8 text-primary-400 animate-spin" />
                                        </div>
                                    ) : priceHistory.length > 0 ? (
                                        <div className="h-64 flex items-end space-x-1">
                                            {(() => {
                                                const maxPrice = Math.max(...priceHistory.map(p => p.price));
                                                const minPrice = Math.min(...priceHistory.map(p => p.price));
                                                const range = maxPrice - minPrice;
                                                return priceHistory.map((price, index) => {
                                                    const height = range > 0 ? ((price.price - minPrice) / range) * 100 : 50;
                                                    return (
                                                        <div
                                                            key={index}
                                                            className="bg-primary-500 hover:bg-primary-400 transition-colors rounded-t flex-1"
                                                            style={{ height: `${height}%`, minHeight: '2px' }}
                                                            title={`${new Date(price.timestamp).toLocaleDateString()}: ${formatPrice(price.price)}`}
                                                        />
                                                    );
                                                });
                                            })()}
                                        </div>
                                    ) : (
                                        <div className="flex items-center justify-center h-64 text-gray-400">
                                            <p>No price history available</p>
                                        </div>
                                    )}
                                </div>
                            )}

                             {activeTab === 'analytics' && (
                                <div className="space-y-6">
                                    {/* Performance Metrics */}
                                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                                        <div className="card p-4">
                                            <div className="flex items-center justify-between mb-2">
                                                <span className="text-sm text-gray-400">RSI (14)</span>
                                                <Activity size={16} className="text-gray-400" />
                                            </div>
                                            <p className={`text-xl font-semibold ${asset?.rsi > 70 ? 'text-danger-400' : asset?.rsi < 30 ? 'text-success-400' : 'text-gray-100'}`}>
                                                {asset?.rsi ? asset.rsi.toFixed(1) : 'N/A'}
                                            </p>
                                        </div>

                                        <div className="card p-4">
                                            <div className="flex items-center justify-between mb-2">
                                                <span className="text-sm text-gray-400">Beta</span>
                                                <TrendingDown size={16} className="text-gray-400" />
                                            </div>
                                            <p className="text-xl font-semibold text-gray-100">
                                                {asset?.beta ? asset.beta.toFixed(2) : 'N/A'}
                                            </p>
                                        </div>

                                        <div className="card p-4">
                                            <div className="flex items-center justify-between mb-2">
                                                <span className="text-sm text-gray-400">Sharpe Ratio</span>
                                                <DollarSign size={16} className="text-gray-400" />
                                            </div>
                                            <p className="text-xl font-semibold text-gray-100">
                                                {asset?.sharpe_ratio ? asset.sharpe_ratio.toFixed(2) : 'N/A'}
                                            </p>
                                        </div>

                                        <div className="card p-4">
                                            <div className="flex items-center justify-between mb-2">
                                                <span className="text-sm text-gray-400">Market Cap</span>
                                                <Globe size={16} className="text-gray-400" />
                                            </div>
                                            <p className="text-xl font-semibold text-gray-100">
                                                {formatMarketCap(asset?.market_cap)}
                                            </p>
                                        </div>
                                    </div>

                                    {/* Returns Performance */}
                                    <div className="card p-6">
                                        <h3 className="text-lg font-semibold text-gray-100 mb-4">Returns Performance</h3>
                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                            <div className="text-center">
                                                <p className="text-sm text-gray-400 mb-1">1 Month</p>
                                                <p className={`text-lg font-semibold ${getChangeColor(asset?.total_return_1m)}`}>
                                                    {formatPercentage(asset?.total_return_1m)}
                                                </p>
                                            </div>
                                            <div className="text-center">
                                                <p className="text-sm text-gray-400 mb-1">3 Months</p>
                                                <p className={`text-lg font-semibold ${getChangeColor(asset?.total_return_3m)}`}>
                                                    {formatPercentage(asset?.total_return_3m)}
                                                </p>
                                            </div>
                                            <div className="text-center">
                                                <p className="text-sm text-gray-400 mb-1">1 Year</p>
                                                <p className={`text-lg font-semibold ${getChangeColor(asset?.total_return_1y)}`}>
                                                    {formatPercentage(asset?.total_return_1y)}
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {activeTab === 'details' && (
                                <div className="card p-6">
                                    <h3 className="text-lg font-semibold text-gray-100 mb-4">Asset Details</h3>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                                        {[
                                            { label: 'Symbol', value: asset?.symbol },
                                            { label: 'Name', value: asset?.name },
                                            { label: 'Asset Type', value: asset?.asset_type },
                                            { label: 'Exchange', value: asset?.exchange },
                                            { label: 'ISIN', value: asset?.isin },
                                            { label: 'CUSIP', value: asset?.cusip },
                                            { label: 'Sector', value: asset?.sector },
                                            { label: 'Industry', value: asset?.industry },
                                            { label: 'Country', value: asset?.country }
                                        ].map(item => (
                                            <div key={item.label}>
                                                <p className="text-gray-400 mb-1">{item.label}</p>
                                                <p className="text-gray-100 font-medium">{item.value || 'N/A'}</p>
                                            </div>
                                        ))}
                                    </div>
                                    {asset?.description && (
                                        <div className="mt-4 text-sm">
                                            <p className="text-gray-400 mb-1">Description</p>
                                            <p className="text-gray-200 font-medium whitespace-pre-wrap">{asset.description}</p>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="flex-shrink-0 flex items-center justify-end p-6 border-t border-dark-700">
                    <div className="flex items-center space-x-3">
                        {isEditing ? (
                            <>
                                <button onClick={handleCancel} className="btn-secondary">
                                    Cancel
                                </button>
                                <button onClick={handleSave} className="btn-primary flex items-center space-x-2">
                                    <Save size={16} />
                                    <span>{mode === 'create' ? 'Create Asset' : 'Save Changes'}</span>
                                </button>
                            </>
                        ) : (
                            <>
                                {mode === 'view' && (
                                    <button onClick={handleEdit} className="btn-outline flex items-center space-x-2">
                                        <Edit size={16} />
                                        <span>Edit</span>
                                    </button>
                                )}
                                <button onClick={onClose} className="btn-secondary">
                                    Close
                                </button>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AssetModal;