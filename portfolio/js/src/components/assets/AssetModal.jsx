import {
    Activity,
    ArrowDownRight,
    ArrowUpRight,
    BarChart3,
    DollarSign,
    ExternalLink,
    Globe,
    RefreshCw,
    Save,
    TrendingDown,
    TrendingUp,
    X
} from 'lucide-react';
import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { marketAPI, portfolioAPI } from '../../services/api';
import { SymbolSearch } from '../shared';

const AssetModal = ({ asset, mode = 'view', onClose, onSave }) => {
    const [priceHistory, setPriceHistory] = useState([]);
    const [loading, setLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('overview');
    const [formData, setFormData] = useState({
        symbol: '',
        name: '',
        quantity: '',
        purchase_price: '',
        purchase_date: '',
        notes: '',
        currency: 'USD',
        portfolio_id: ''
    });
    const [isEditing, setIsEditing] = useState(false);
    const [portfolios, setPortfolios] = useState([]);

    useEffect(() => {
        if (asset) {
            loadPriceHistory();
            if (mode === 'edit' || mode === 'create') {
                setFormData({
                    symbol: asset.symbol || '',
                    name: asset.name || '',
                    quantity: asset.quantity || '',
                    purchase_price: asset.purchase_price || '',
                    purchase_date: asset.purchase_date || '',
                    notes: asset.notes || '',
                    currency: asset.currency || 'USD',
                    portfolio_id: asset.portfolio_id || ''
                });
                setIsEditing(true);
            }
        } else if (mode === 'create') {
            setIsEditing(true);
        }

        // Load portfolios for create/edit mode
        if (mode === 'create' || mode === 'edit') {
            loadPortfolios();
        }
    }, [asset, mode]);


    const loadPortfolios = async () => {
        try {
            const response = await portfolioAPI.getPortfolios();
            setPortfolios(response || []);
            // Set default portfolio if none selected
            if (response && response.length > 0 && !formData.portfolio_id) {
                setFormData(prev => ({ ...prev, portfolio_id: response[0].id }));
            }
        } catch (error) {
            console.error('Failed to load portfolios:', error);
            toast.error('Failed to load portfolios');
        }
    };

    const loadPriceHistory = async () => {
        if (!asset?.id) return;
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
            currency: 'USD' // Default currency, could be enhanced to detect from exchange
        }));
    };

    const handleSave = () => {
        if (!formData.symbol || !formData.quantity || !formData.purchase_price || !formData.portfolio_id) {
            toast.error('Please fill in all required fields');
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
            setFormData({
                symbol: asset?.symbol || '',
                name: asset?.name || '',
                quantity: asset?.quantity || '',
                purchase_price: asset?.purchase_price || '',
                purchase_date: asset?.purchase_date || '',
                notes: asset?.notes || ''
            });
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

    if (!asset && mode !== 'create') return null;

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
                )}

                {/* Tabs - Only show for view mode */}
                {mode === 'view' && asset && (
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
                )}

                {/* Content */}
                <div className="p-6 max-h-96 overflow-y-auto">
                    {isEditing ? (
                        /* Edit/Create Form */
                        <div className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {/* Symbol Search */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Symbol <span className="text-red-400">*</span>
                                    </label>
                                    <SymbolSearch
                                        value={formData.symbol}
                                        onChange={handleSymbolChange}
                                        onSelect={handleSymbolSelect}
                                        placeholder="e.g., AAPL, BTC"
                                        showSuggestions={true}
                                    />
                                </div>

                                {/* Asset Name */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Asset Name
                                    </label>
                                    <input
                                        type="text"
                                        name="name"
                                        value={formData.name}
                                        onChange={handleInputChange}
                                        placeholder="e.g., Apple Inc., Bitcoin"
                                        className="input-field w-full"
                                    />
                                </div>

                                {/* Portfolio Selector */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Portfolio <span className="text-red-400">*</span>
                                    </label>
                                    <select
                                        name="portfolio_id"
                                        value={formData.portfolio_id}
                                        onChange={handleInputChange}
                                        className="input-field w-full"
                                        required
                                    >
                                        <option value="">Select a portfolio</option>
                                        {portfolios.map((portfolio) => (
                                            <option key={portfolio.id} value={portfolio.id}>
                                                {portfolio.name} ({portfolio.currency})
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                {/* Currency */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Currency
                                    </label>
                                    <select
                                        name="currency"
                                        value={formData.currency}
                                        onChange={handleInputChange}
                                        className="input-field w-full"
                                    >
                                        <option value="USD">USD</option>
                                        <option value="EUR">EUR</option>
                                        <option value="GBP">GBP</option>
                                        <option value="JPY">JPY</option>
                                        <option value="CAD">CAD</option>
                                        <option value="AUD">AUD</option>
                                    </select>
                                </div>

                                {/* Quantity */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Quantity <span className="text-red-400">*</span>
                                    </label>
                                    <input
                                        type="number"
                                        name="quantity"
                                        value={formData.quantity}
                                        onChange={handleInputChange}
                                        placeholder="0.00"
                                        step="0.000001"
                                        min="0"
                                        className="input-field w-full"
                                        required
                                    />
                                </div>

                                {/* Purchase Price */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Purchase Price <span className="text-red-400">*</span>
                                    </label>
                                    <input
                                        type="number"
                                        name="purchase_price"
                                        value={formData.purchase_price}
                                        onChange={handleInputChange}
                                        placeholder="0.00"
                                        step="0.01"
                                        min="0"
                                        className="input-field w-full"
                                        required
                                    />
                                </div>

                                {/* Purchase Date */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Purchase Date
                                    </label>
                                    <input
                                        type="date"
                                        name="purchase_date"
                                        value={formData.purchase_date}
                                        onChange={handleInputChange}
                                        className="input-field w-full"
                                    />
                                </div>
                            </div>

                            {/* Notes */}
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Notes
                                </label>
                                <textarea
                                    name="notes"
                                    value={formData.notes}
                                    onChange={handleInputChange}
                                    placeholder="Additional notes about this asset..."
                                    rows={3}
                                    className="input-field w-full"
                                />
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
                                                    getChangeColor(((asset.current_price - asset.purchase_price) / asset.purchase_price) * 100) : 'text-gray-400'}`}>
                                                    {asset?.quantity && asset?.purchase_price && asset?.current_price ?
                                                        formatPrice((asset.current_price - asset.purchase_price) * asset.quantity) : 'N/A'}
                                                </p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-gray-400 mb-1">P&L Percentage</p>
                                                <p className={`text-xl font-semibold ${asset?.quantity && asset?.purchase_price && asset?.current_price ?
                                                    getChangeColor(((asset.current_price - asset.purchase_price) / asset.purchase_price) * 100) : 'text-gray-400'}`}>
                                                    {asset?.quantity && asset?.purchase_price && asset?.current_price ?
                                                        `${(((asset.current_price - asset.purchase_price) / asset.purchase_price) * 100).toFixed(2)}%` : 'N/A'}
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
                                                <p className="text-gray-100 font-medium">{asset?.symbol || 'N/A'}</p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-gray-400 mb-1">Name</p>
                                                <p className="text-gray-100 font-medium">{asset?.name || 'N/A'}</p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-gray-400 mb-1">Quantity</p>
                                                <p className="text-gray-100 font-medium">{asset?.quantity || 'N/A'}</p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-gray-400 mb-1">Purchase Price</p>
                                                <p className="text-gray-100 font-medium">{formatPrice(asset?.purchase_price)}</p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-gray-400 mb-1">Purchase Date</p>
                                                <p className="text-gray-100 font-medium">{asset?.purchase_date || 'N/A'}</p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-gray-400 mb-1">Current Price</p>
                                                <p className="text-gray-100 font-medium">{formatPrice(asset?.current_price)}</p>
                                            </div>
                                        </div>
                                        {asset?.notes && (
                                            <div className="mt-4">
                                                <p className="text-sm text-gray-400 mb-1">Notes</p>
                                                <p className="text-gray-100 font-medium">{asset.notes}</p>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between p-6 border-t border-dark-700">
                    <div className="flex items-center space-x-4">
                        {mode === 'view' && asset && (
                            <button className="btn-primary flex items-center space-x-2">
                                <ExternalLink size={16} />
                                <span>View on Exchange</span>
                            </button>
                        )}
                    </div>
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
