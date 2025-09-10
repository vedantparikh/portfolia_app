import {
    Activity,
    ArrowDownLeft,
    ArrowUpRight,
    BarChart3,
    Calculator,
    CircleDollarSign,
    Copy,
    DollarSign,
    Edit,
    Gift,
    GitBranch,
    Globe,
    Merge,
    Plus,
    RefreshCw,
    Repeat,
    Save,
    TrendingDown,
    TrendingUp,
    X,
    Zap
} from 'lucide-react';
import React, { useEffect, useState } from 'react'; // Import useMemo
import toast from 'react-hot-toast';
import { marketAPI, portfolioAPI, transactionAPI } from '../../services/api';
import { Chart, SymbolSearch } from '../shared';


const AssetModal = ({ asset, mode = 'view', onClose, onSave }) => {
    const [priceHistory, setPriceHistory] = useState([]);
    const [loading, setLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('overview');
    const [chartPeriod, setChartPeriod] = useState('30d');
    const [formData, setFormData] = useState({
        symbol: '',
        name: '',
        asset_type: 'EQUITY',
        exchange: '',
        sector: '',
        industry: '',
        country: '',
        description: '',
        is_active: true
    });
    const [isEditing, setIsEditing] = useState(false);
    const [isChartFullscreen, setIsChartFullscreen] = useState(false);
    const [showTransactionForm, setShowTransactionForm] = useState(false);
    const [portfolios, setPortfolios] = useState([]);
    const [transactionFormData, setTransactionFormData] = useState({
        portfolio_id: '',
        transaction_type: 'buy',
        quantity: '',
        price: '',
        amount: '', // Optional amount field for UI calculation
        fees: '',
        notes: '',
        date: new Date().toISOString().split('T')[0]
    });
    const [transactionLoading, setTransactionLoading] = useState(false);
    const [fetchingPrice, setFetchingPrice] = useState(false);
    const [showAllTransactionTypes, setShowAllTransactionTypes] = useState(false);

    // Transaction types configuration (same as CreateTransactionModal)
    const transactionTypes = [
        {
            value: 'buy',
            label: 'Buy',
            description: 'Purchase assets',
            icon: TrendingUp,
            color: 'success',
            category: 'trading'
        },
        {
            value: 'sell',
            label: 'Sell',
            description: 'Sell assets',
            icon: TrendingDown,
            color: 'danger',
            category: 'trading'
        },
        {
            value: 'dividend',
            label: 'Dividend',
            description: 'Dividend payment',
            icon: CircleDollarSign,
            color: 'primary',
            category: 'income'
        },
        {
            value: 'split',
            label: 'Stock Split',
            description: 'Stock split event',
            icon: Copy,
            color: 'info',
            category: 'corporate'
        },
        {
            value: 'merger',
            label: 'Merger',
            description: 'Company merger',
            icon: Merge,
            color: 'warning',
            category: 'corporate'
        },
        {
            value: 'spin_off',
            label: 'Spin-off',
            description: 'Corporate spin-off',
            icon: GitBranch,
            color: 'info',
            category: 'corporate'
        },
        {
            value: 'rights_issue',
            label: 'Rights Issue',
            description: 'Rights offering',
            icon: Gift,
            color: 'primary',
            category: 'corporate'
        },
        {
            value: 'stock_option_exercise',
            label: 'Option Exercise',
            description: 'Stock option exercise',
            icon: Zap,
            color: 'warning',
            category: 'options'
        },
        {
            value: 'transfer_in',
            label: 'Transfer In',
            description: 'Asset transfer in',
            icon: ArrowDownLeft,
            color: 'success',
            category: 'transfer'
        },
        {
            value: 'transfer_out',
            label: 'Transfer Out',
            description: 'Asset transfer out',
            icon: ArrowUpRight,
            color: 'danger',
            category: 'transfer'
        },
        {
            value: 'fee',
            label: 'Fee',
            description: 'Management fee',
            icon: Calculator,
            color: 'gray',
            category: 'other'
        },
        {
            value: 'other',
            label: 'Other',
            description: 'Other transaction',
            icon: Repeat,
            color: 'gray',
            category: 'other'
        }
    ];

    // Color schemes for transaction types
    const colorSchemes = {
        success: {
            border: 'border-success-400',
            bg: 'bg-success-400/10',
            text: 'text-success-400',
            hover: 'hover:border-success-300'
        },
        danger: {
            border: 'border-danger-400',
            bg: 'bg-danger-400/10',
            text: 'text-danger-400',
            hover: 'hover:border-danger-300'
        },
        primary: {
            border: 'border-primary-400',
            bg: 'bg-primary-400/10',
            text: 'text-primary-400',
            hover: 'hover:border-primary-300'
        },
        warning: {
            border: 'border-warning-400',
            bg: 'bg-warning-400/10',
            text: 'text-warning-400',
            hover: 'hover:border-warning-300'
        },
        info: {
            border: 'border-info-400',
            bg: 'bg-info-400/10',
            text: 'text-info-400',
            hover: 'hover:border-info-300'
        },
        gray: {
            border: 'border-gray-400',
            bg: 'bg-gray-400/10',
            text: 'text-gray-400',
            hover: 'hover:border-gray-300'
        }
    };

    // Helper function to get the selected transaction type details
    const getSelectedTransactionType = () => {
        return transactionTypes.find(type => type.value === transactionFormData.transaction_type) || transactionTypes[0];
    };

    // Get transaction types to display (common ones first, then all if expanded)
    const getDisplayedTransactionTypes = () => {
        const commonTypes = ['buy', 'sell', 'dividend'];

        if (!showAllTransactionTypes) {
            return transactionTypes.filter(type => commonTypes.includes(type.value));
        }

        return transactionTypes;
    };

    // Helper function to format quantity with max 4 decimal places
    const formatQuantity = (quantity) => {
        if (!quantity) return '';
        const num = parseFloat(quantity);
        if (isNaN(num)) return '';
        return num.toFixed(4).replace(/\.?0+$/, '');
    };

    // **FIX:** The useState hook is now correctly at the top level, but it has been moved into the ChartComponent.
    // This is the best practice for encapsulating component-specific state.

    useEffect(() => {
        if (asset && mode === 'view') {
            loadPriceHistory();
        }
        if (mode === 'edit') {
            setFormData({
                ...asset,
                is_active: asset.is_active !== undefined ? asset.is_active : true
            });
            setIsEditing(true);
        } else if (mode === 'create') {
            setIsEditing(true);
        }
    }, [asset, mode]);

    // Load portfolios for transaction creation
    useEffect(() => {
        if (mode === 'create') {
            loadPortfolios();
        }
    }, [mode]);

    // Fetch current price when transaction form is shown and asset symbol is available
    useEffect(() => {
        if (showTransactionForm && formData.symbol && mode === 'create') {
            fetchCurrentPrice(formData.symbol);
        }
    }, [showTransactionForm, formData.symbol, mode]);

    const loadPortfolios = async () => {
        try {
            const response = await portfolioAPI.getPortfolios();
            setPortfolios(response || []);
        } catch (error) {
            console.error('Failed to load portfolios:', error);
            toast.error('Failed to load portfolios');
        }
    };

    const loadPriceHistory = async (period = chartPeriod) => {
        if (!asset?.id) {
            console.log('AssetModal: No asset ID available for price history');
            return;
        }

        try {
            setLoading(true);
            console.log('AssetModal: Loading price history for asset:', asset.id, 'period:', period);

            const response = await marketAPI.getAssetPrices(asset.id, {
                period: period,
                interval: '1d' // API only provides daily data
            });

            console.log('AssetModal: Price history response:', response);

            // Handle different response formats and transform data
            let priceData = [];
            if (response?.data) {
                priceData = Array.isArray(response.data) ? response.data : [];
            } else if (Array.isArray(response)) {
                priceData = response;
            }

            // Transform and validate price data for chart compatibility
            const transformedData = priceData.map(item => {
                // Handle different possible field names from API
                const date = item.date;
                const open = item.open;
                const high = item.high;
                const low = item.low;
                const close = item.close;
                const volume = item.volume;

                return {
                    date: date,
                    open: parseFloat(open) || 0,
                    high: parseFloat(high) || 0,
                    low: parseFloat(low) || 0,
                    close: parseFloat(close) || 0,
                    volume: parseFloat(volume) || 0
                };
            }).filter(item => {
                // Only include items with valid data
                return item.date && !isNaN(item.close) && item.close > 0;
            });

            console.log('AssetModal: Transformed price data:', transformedData.length, 'items');
            if (transformedData.length > 0) {
                console.log('AssetModal: Sample data item:', transformedData[0]);
            }

            setPriceHistory(transformedData);

        } catch (error) {
            console.error('AssetModal: Failed to load price history:', error);

            // Set empty array on error to prevent chart from showing "failed to load"
            setPriceHistory([]);

            // Only show toast error if it's not a 404 (asset might not have price data)
            if (error.response?.status !== 404) {
                toast.error('Failed to load price history');
            } else {
                console.log('AssetModal: No price data available for this asset');
            }
        } finally {
            setLoading(false);
        }
    };

    const handlePeriodChange = (newPeriod) => {
        setChartPeriod(newPeriod);
        loadPriceHistory(newPeriod);
    };

    const handleChartFullscreenToggle = (isFullscreen) => {
        setIsChartFullscreen(isFullscreen);
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSymbolChange = (value) => {
        setFormData(prev => ({ ...prev, symbol: value }));
    };

    const handleSymbolSelect = (suggestion) => {
        setFormData(prev => ({
            ...prev,
            symbol: suggestion.symbol,
            name: suggestion.long_name || suggestion.short_name || suggestion.name,
            exchange: suggestion.exchange,
            asset_type: suggestion.quote_type.toUpperCase(),
            sector: suggestion.sector,
            industry: suggestion.industry,
            country: suggestion.country,
        }));
    };

    const handleSave = async () => {
        if (!formData.symbol || !formData.name || !formData.asset_type) {
            toast.error('Please fill in all required fields (Symbol, Name, Asset Type)');
            return;
        }
        
        try {
            // Save the asset first
            const savedAsset = await onSave(formData);
            
            // If transaction form is shown and user wants to create a transaction
            if (showTransactionForm && savedAsset) {
                await handleCreateTransaction(savedAsset);
            } else {
                // Just close the modal if no transaction needed
                onClose();
            }
        } catch (error) {
            console.error('Failed to save asset:', error);
            toast.error('Failed to save asset');
        }
    };

    // Function to fetch current price for a symbol
    const fetchCurrentPrice = async (symbol) => {
        try {
            setFetchingPrice(true);
            console.log(`[AssetModal] Fetching price for symbol: ${symbol}`);

            const priceData = await marketAPI.getStockLatestData(symbol);
            console.log(`[AssetModal] Price data received:`, priceData);

            if (priceData && Array.isArray(priceData) && priceData.length > 0) {
                const latestData = priceData[0];
                const price = parseFloat(latestData.latest_price || latestData.Close || latestData.close || latestData.price);

                if (!isNaN(price)) {
                    console.log(`[AssetModal] Setting price: ${price} for ${symbol}`);
                    setTransactionFormData(prev => ({
                        ...prev,
                        price: price.toString()
                    }));
                    return price;
                }
            } else if (priceData && typeof priceData === 'object' && !Array.isArray(priceData)) {
                const price = parseFloat(priceData.latest_price || priceData.Close || priceData.close || priceData.price);

                if (!isNaN(price)) {
                    console.log(`[AssetModal] Setting price (object): ${price} for ${symbol}`);
                    setTransactionFormData(prev => ({
                        ...prev,
                        price: price.toString()
                    }));
                    return price;
                }
            }

            console.warn(`[AssetModal] No valid price found for ${symbol}`);
            return null;
        } catch (error) {
            console.error(`[AssetModal] Failed to fetch price for ${symbol}:`, error);
            return null;
        } finally {
            setFetchingPrice(false);
        }
    };

    const handleTransactionInputChange = (e) => {
        const { name, value } = e.target;

        // Handle amount/quantity/price calculations
        if (name === 'amount' || name === 'price') {
            const newFormData = { ...transactionFormData, [name]: value };

            // Auto-calculate quantity if both amount and price are present
            if (name === 'amount' && newFormData.price && parseFloat(newFormData.price) > 0) {
                const calculatedQuantity = parseFloat(value || 0) / parseFloat(newFormData.price);
                newFormData.quantity = calculatedQuantity > 0 ? calculatedQuantity.toFixed(6) : '';
            } else if (name === 'price' && newFormData.amount && parseFloat(value) > 0) {
                const calculatedQuantity = parseFloat(newFormData.amount) / parseFloat(value);
                newFormData.quantity = calculatedQuantity > 0 ? calculatedQuantity.toFixed(6) : '';
            }

            setTransactionFormData(newFormData);
        } else if (name === 'quantity') {
            // Clear amount when quantity is manually changed
            setTransactionFormData(prev => ({
                ...prev,
                [name]: value,
                amount: ''
            }));
        } else {
            setTransactionFormData(prev => ({
                ...prev,
                [name]: value
            }));
        }
    };

    const calculateTotal = () => {
        const quantity = parseFloat(transactionFormData.quantity) || 0;
        const price = parseFloat(transactionFormData.price) || 0;
        const fees = parseFloat(transactionFormData.fees) || 0;

        // Some transaction types don't involve monetary exchange
        const selectedType = getSelectedTransactionType();
        const monetaryTypes = ['buy', 'sell', 'dividend', 'fee', 'transfer_in', 'transfer_out'];

        if (!monetaryTypes.includes(selectedType.value)) {
            return fees; // Only fees for non-monetary transactions
        }

        return (quantity * price) + fees;
    };

    const handleCreateTransaction = async (savedAsset) => {
        if (!transactionFormData.portfolio_id) {
            toast.error('Please select a portfolio for the transaction');
            return;
        }

        // Validation based on transaction type
        const selectedType = getSelectedTransactionType();
        const requiresQuantity = !['fee'].includes(selectedType.value);
        const requiresPrice = ['buy', 'sell', 'dividend', 'transfer_in', 'transfer_out'].includes(selectedType.value);

        if (requiresQuantity && (!transactionFormData.quantity || parseFloat(transactionFormData.quantity) <= 0)) {
            toast.error('Valid quantity is required');
            return;
        }

        if (requiresPrice && (!transactionFormData.price || parseFloat(transactionFormData.price) <= 0)) {
            toast.error('Valid price is required');
            return;
        }

        try {
            setTransactionLoading(true);
            
            const transactionData = {
                portfolio_id: parseInt(transactionFormData.portfolio_id),
                transaction_type: transactionFormData.transaction_type,
                asset_id: savedAsset.id,
                currency: 'USD',
                quantity: parseFloat(transactionFormData.quantity),
                price: parseFloat(transactionFormData.price),
                fees: parseFloat(transactionFormData.fees) || 0,
                notes: transactionFormData.notes.trim(),
                transaction_date: transactionFormData.date,
                total_amount: calculateTotal()
            };

            await transactionAPI.createTransaction(transactionData);
            toast.success('Asset and transaction created successfully');
            onClose();
        } catch (error) {
            console.error('Failed to create transaction:', error);
            toast.error('Asset created but failed to create transaction');
        } finally {
            setTransactionLoading(false);
        }
    };

    const handleEdit = () => setIsEditing(true);

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
        if (numPrice < 0.01 && numPrice > 0) return `$${numPrice.toFixed(6)}`;
        if (numPrice < 1 && numPrice > 0) return `$${numPrice.toFixed(4)}`;
        return `$${numPrice.toFixed(2)}`;
    };

    const formatMarketCap = (marketCap) => {
        if (!marketCap) return 'N/A';
        if (marketCap >= 1e12) return `$${(marketCap / 1e12).toFixed(2)}T`;
        if (marketCap >= 1e9) return `$${(marketCap / 1e9).toFixed(2)}B`;
        if (marketCap >= 1e6) return `$${(marketCap / 1e6).toFixed(2)}M`;
        return `$${marketCap.toFixed(0)}`;
    };

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
                    <button onClick={onClose} className="p-2 rounded-lg hover:bg-dark-800 transition-colors">
                        <X size={20} className="text-gray-400" />
                    </button>
                </div>
                {/* Price Section */}
                {mode === 'view' && asset && (
                    <div className="flex-shrink-0 p-6 border-b border-dark-700">
                        <div className="flex items-center justify-between">
                            <div>
                                <div className="flex items-center space-x-3 mb-2">
                                    <span className="text-3xl font-bold text-gray-100">{formatPrice(asset.current_price)}</span>
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
                            <button onClick={loadPriceHistory} disabled={loading} className="btn-outline flex items-center space-x-2">
                                <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
                                <span>Refresh</span>
                            </button>
                        </div>
                    </div>
                )}
                {/* Tabs */}
                {mode === 'view' && asset && (
                    <div className="flex-shrink-0 flex border-b border-dark-700">
                        {tabs.map((tab) => (
                            <button key={tab.id} onClick={() => setActiveTab(tab.id)} className={`flex items-center space-x-2 px-6 py-4 text-sm font-medium transition-colors ${activeTab === tab.id ? 'text-primary-400 border-b-2 border-primary-400 bg-primary-600/10' : 'text-gray-400 hover:text-gray-300 hover:bg-dark-800/50'}`}>
                                <tab.icon size={16} />
                                <span>{tab.label}</span>
                            </button>
                        ))}
                    </div>
                )}
                {/* Content */}
                <div className="flex-grow p-6 overflow-y-auto">
                    {isEditing ? (
                        <div className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="md:col-span-2">
                                    <label className="block text-sm font-medium text-gray-300 mb-2">Symbol <span className="text-red-400">*</span></label>
                                    <SymbolSearch value={formData.symbol} onChange={handleSymbolChange} onSelect={handleSymbolSelect} placeholder="e.g., AAPL, BTC" />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">Asset Name <span className="text-red-400">*</span></label>
                                    <input type="text" name="name" value={formData.name} onChange={handleInputChange} placeholder="e.g., Apple Inc., Bitcoin" className="input-field w-full" required />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">Asset Type <span className="text-red-400">*</span></label>
                                    <select name="asset_type" value={formData.asset_type} onChange={handleInputChange} className="input-field w-full" required>
                                        <option value="EQUITY">Equity (Stock)</option>
                                        <option value="ETF">ETF</option>
                                        <option value="CRYPTOCURRENCY">Cryptocurrency</option>
                                        <option value="MUTUALFUND">Mutual Fund</option>
                                        <option value="COMMODITY">Commodity</option>
                                        <option value="INDEX">Index</option>
                                        <option value="CASH">Cash</option>
                                        <option value="BOND">Bond</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">Exchange <span className="text-gray-500">(Optional)</span></label>
                                    <input type="text" name="exchange" value={formData.exchange} onChange={handleInputChange} placeholder="e.g., NMS, NASDAQ, NYSE" className="input-field w-full" />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">Sector <span className="text-gray-500">(Optional)</span></label>
                                    <input type="text" name="sector" value={formData.sector} onChange={handleInputChange} placeholder="e.g., Technology, Healthcare" className="input-field w-full" />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">Industry <span className="text-gray-500">(Optional)</span></label>
                                    <input type="text" name="industry" value={formData.industry} onChange={handleInputChange} placeholder="e.g., Consumer Electronics, Software" className="input-field w-full" />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">Country <span className="text-gray-500">(Optional)</span></label>
                                    <input type="text" name="country" value={formData.country} onChange={handleInputChange} placeholder="e.g., United States, Canada" className="input-field w-full" />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">Description <span className="text-gray-500">(Optional)</span></label>
                                <textarea name="description" value={formData.description} onChange={handleInputChange} placeholder="Detailed description of the asset..." rows={3} className="input-field w-full" />
                            </div>
                            <div>
                                <label className="flex items-center space-x-3">
                                    <input type="checkbox" name="is_active" checked={formData.is_active} onChange={(e) => setFormData(prev => ({ ...prev, is_active: e.target.checked }))} className="w-4 h-4 text-primary-600 bg-gray-700 border-gray-600 rounded focus:ring-primary-500 focus:ring-2" />
                                    <span className="text-sm font-medium text-gray-300">Active Asset</span>
                                </label>
                            </div>

                            {/* Transaction Creation Option */}
                            {mode === 'create' && (
                                <div className="border-t border-dark-700 pt-6">
                                    <div className="flex items-center justify-between mb-4">
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-100">Create Transaction</h3>
                                            <p className="text-sm text-gray-400">Add a transaction for this asset after creating it</p>
                                        </div>
                                        <button
                                            type="button"
                                            onClick={() => setShowTransactionForm(!showTransactionForm)}
                                            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                                                showTransactionForm 
                                                    ? 'bg-primary-600 text-white' 
                                                    : 'bg-dark-700 text-gray-300 hover:bg-dark-600'
                                            }`}
                                        >
                                            <Plus size={16} />
                                            <span>{showTransactionForm ? 'Cancel Transaction' : 'Add Transaction'}</span>
                                        </button>
                                    </div>

                                    {showTransactionForm && (
                                        <div className="space-y-6 p-4 bg-dark-800 rounded-lg border border-dark-600">
                                            {/* Transaction Type Selection */}
                                            <div>
                                                <div className="flex items-center justify-between mb-3">
                                                    <label className="block text-sm font-medium text-gray-300">
                                                        Transaction Type
                                                    </label>
                                                    <button
                                                        type="button"
                                                        onClick={() => setShowAllTransactionTypes(!showAllTransactionTypes)}
                                                        className="text-xs text-primary-400 hover:text-primary-300 transition-colors"
                                                    >
                                                        {showAllTransactionTypes ? 'Show Less' : 'Show All Types'}
                                                    </button>
                                                </div>

                                                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                                                    {getDisplayedTransactionTypes().map((type) => {
                                                        const IconComponent = type.icon;
                                                        const colorScheme = colorSchemes[type.color];
                                                        const isSelected = transactionFormData.transaction_type === type.value;

                                                        return (
                                                            <button
                                                                key={type.value}
                                                                type="button"
                                                                onClick={() => setTransactionFormData(prev => ({ ...prev, transaction_type: type.value }))}
                                                                className={`p-3 rounded-lg border-2 transition-colors ${isSelected
                                                                    ? `${colorScheme.border} ${colorScheme.bg} ${colorScheme.text}`
                                                                    : `border-dark-600 bg-dark-700 text-gray-300 hover:border-dark-500 ${colorScheme.hover}`
                                                                    }`}
                                                            >
                                                                <div className="flex items-center space-x-3">
                                                                    <IconComponent size={18} className={isSelected ? colorScheme.text : 'text-gray-400'} />
                                                                    <div className="text-left flex-1">
                                                                        <div className="font-medium text-sm">{type.label}</div>
                                                                        <div className="text-xs opacity-75">{type.description}</div>
                                                                    </div>
                                                                </div>
                                                            </button>
                                                        );
                                                    })}
                                                </div>

                                                {/* Category indicator for selected type */}
                                                {(() => {
                                                    const selectedType = getSelectedTransactionType();
                                                    return (
                                                        <div className="mt-3 flex items-center space-x-2">
                                                            <span className="text-xs text-gray-500">Category:</span>
                                                            <span className={`text-xs px-2 py-1 rounded-full ${colorSchemes[selectedType.color].bg} ${colorSchemes[selectedType.color].text}`}>
                                                                {selectedType.category.charAt(0).toUpperCase() + selectedType.category.slice(1)}
                                                            </span>
                                                        </div>
                                                    );
                                                })()}
                                            </div>

                                            {/* Portfolio Selection */}
                                            <div>
                                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                                    Portfolio *
                                                </label>
                                                <select
                                                    name="portfolio_id"
                                                    value={transactionFormData.portfolio_id}
                                                    onChange={handleTransactionInputChange}
                                                    className="input-field w-full"
                                                    required
                                                >
                                                    <option value="">Select a portfolio</option>
                                                    {portfolios.map((portfolio) => (
                                                        <option key={portfolio.id} value={portfolio.id}>
                                                            {portfolio.name}
                                                        </option>
                                                    ))}
                                                </select>
                                            </div>

                                            {/* Amount, Quantity and Price */}
                                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                                {(() => {
                                                    const selectedType = getSelectedTransactionType();
                                                    const requiresQuantity = !['fee'].includes(selectedType.value);
                                                    const requiresPrice = ['buy', 'sell', 'dividend', 'transfer_in', 'transfer_out'].includes(selectedType.value);

                                                    return (
                                                        <>
                                                            {/* Amount field - optional helper for calculation */}
                                                            {requiresQuantity && requiresPrice && (
                                                                <div>
                                                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                                                        Total Amount
                                                                        <span className="text-xs text-gray-500 ml-1">(optional)</span>
                                                                    </label>
                                                                    <input
                                                                        type="number"
                                                                        name="amount"
                                                                        value={transactionFormData.amount}
                                                                        onChange={handleTransactionInputChange}
                                                                        placeholder="0.00"
                                                                        min="0"
                                                                        step="0.01"
                                                                        className="input-field w-full"
                                                                    />
                                                                    <div className="text-xs text-gray-500 mt-1">
                                                                        Auto-calculates quantity when price is set
                                                                    </div>
                                                                </div>
                                                            )}
                                                            {requiresQuantity && (
                                                                <div>
                                                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                                                        {selectedType.value === 'split' ? 'Split Ratio' : 'Quantity'} *
                                                                    </label>
                                                                    <input
                                                                        type="number"
                                                                        name="quantity"
                                                                        value={formatQuantity(transactionFormData.quantity)}
                                                                        onChange={handleTransactionInputChange}
                                                                        placeholder={selectedType.value === 'split' ? "2" : "0.0000"}
                                                                        min="0"
                                                                        step={selectedType.value === 'split' ? "1" : "0.000001"}
                                                                        className="input-field w-full"
                                                                        required
                                                                    />
                                                                    {transactionFormData.quantity && (
                                                                        <div className="text-xs text-gray-500 mt-1">
                                                                            Exact: {parseFloat(transactionFormData.quantity || 0).toFixed(6)}
                                                                        </div>
                                                                    )}
                                                                </div>
                                                            )}
                                                            {requiresPrice && (
                                                                <div>
                                                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                                                        {(() => {
                                                                            switch (selectedType.value) {
                                                                                case 'dividend': return 'Dividend per Share';
                                                                                case 'transfer_in':
                                                                                case 'transfer_out': return 'Transfer Price';
                                                                                default: return 'Price per Share';
                                                                            }
                                                                        })()} *
                                                                        {fetchingPrice && (
                                                                            <span className="ml-2 text-xs text-primary-400">
                                                                                (Fetching latest price...)
                                                                            </span>
                                                                        )}
                                                                    </label>
                                                                    <div className="relative">
                                                                        <input
                                                                            type="number"
                                                                            name="price"
                                                                            value={transactionFormData.price}
                                                                            onChange={handleTransactionInputChange}
                                                                            placeholder={fetchingPrice ? "Fetching..." : "0.00"}
                                                                            min="0"
                                                                            step="0.01"
                                                                            className="input-field w-full"
                                                                            required
                                                                            disabled={fetchingPrice}
                                                                        />
                                                                        {fetchingPrice && (
                                                                            <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                                                                                <div className="w-4 h-4 border-2 border-primary-400 border-t-transparent rounded-full animate-spin" />
                                                                            </div>
                                                                        )}
                                                                    </div>
                                                                </div>
                                                            )}
                                                            {/* Fee field always visible for all transaction types */}
                                                            {!requiresPrice && !requiresQuantity && (
                                                                <div className="md:col-span-3">
                                                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                                                        Fee Amount *
                                                                    </label>
                                                                    <input
                                                                        type="number"
                                                                        name="fees"
                                                                        value={transactionFormData.fees}
                                                                        onChange={handleTransactionInputChange}
                                                                        placeholder="0.00"
                                                                        min="0"
                                                                        step="0.01"
                                                                        className="input-field w-full"
                                                                        required
                                                                    />
                                                                </div>
                                                            )}
                                                        </>
                                                    );
                                                })()}
                                            </div>

                                            {/* Fees and Date */}
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                                {(() => {
                                                    const selectedType = getSelectedTransactionType();
                                                    const showFeesField = selectedType.value !== 'fee'; // Don't show separate fees field for fee transactions

                                                    return (
                                                        <>
                                                            {showFeesField && (
                                                                <div>
                                                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                                                        Additional Fees
                                                                    </label>
                                                                    <input
                                                                        type="number"
                                                                        name="fees"
                                                                        value={transactionFormData.fees}
                                                                        onChange={handleTransactionInputChange}
                                                                        placeholder="0.00"
                                                                        min="0"
                                                                        step="0.01"
                                                                        className="input-field w-full"
                                                                    />
                                                                </div>
                                                            )}
                                                            <div className={showFeesField ? '' : 'md:col-span-2'}>
                                                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                                                    Transaction Date
                                                                </label>
                                                                <input
                                                                    type="date"
                                                                    name="date"
                                                                    value={transactionFormData.date}
                                                                    onChange={handleTransactionInputChange}
                                                                    className="input-field w-full"
                                                                />
                                                            </div>
                                                        </>
                                                    );
                                                })()}
                                            </div>

                                            {/* Total Amount Display */}
                                            <div className="bg-dark-700 rounded-lg p-4">
                                                <div className="flex items-center justify-between">
                                                    <div className="flex items-center space-x-2">
                                                        <Calculator size={16} className="text-gray-400" />
                                                        <span className="text-sm font-medium text-gray-300">
                                                            {(() => {
                                                                const selectedType = getSelectedTransactionType();
                                                                switch (selectedType.value) {
                                                                    case 'buy': return 'Total Cost';
                                                                    case 'sell': return 'Total Proceeds';
                                                                    case 'dividend': return 'Dividend Amount';
                                                                    case 'fee': return 'Fee Amount';
                                                                    case 'transfer_in':
                                                                    case 'transfer_out': return 'Transfer Value';
                                                                    default: return 'Total Amount';
                                                                }
                                                            })()}
                                                        </span>
                                                    </div>
                                                    <span className={`text-xl font-bold ${(() => {
                                                        const selectedType = getSelectedTransactionType();
                                                        const colorScheme = colorSchemes[selectedType.color];
                                                        return colorScheme.text;
                                                    })()}`}>
                                                        {(() => {
                                                            const selectedType = getSelectedTransactionType();
                                                            const sign = ['buy', 'fee', 'transfer_out'].includes(selectedType.value) ? '-' : '+';
                                                            return `${sign}$${calculateTotal().toFixed(2)}`;
                                                        })()}
                                                    </span>
                                                </div>
                                                <div className="text-xs text-gray-500 mt-1">
                                                    {(() => {
                                                        const selectedType = getSelectedTransactionType();
                                                        const monetaryTypes = ['buy', 'sell', 'dividend', 'transfer_in', 'transfer_out'];

                                                        if (monetaryTypes.includes(selectedType.value)) {
                                                            return `${formatQuantity(transactionFormData.quantity) || 0} × $${transactionFormData.price || 0} + $${transactionFormData.fees || 0} fees`;
                                                        } else {
                                                            return `$${transactionFormData.fees || 0} fees only`;
                                                        }
                                                    })()}
                                                </div>
                                            </div>

                                            {/* Notes */}
                                            <div>
                                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                                    Notes
                                                </label>
                                                <textarea
                                                    name="notes"
                                                    value={transactionFormData.notes}
                                                    onChange={handleTransactionInputChange}
                                                    placeholder="Optional notes about this transaction..."
                                                    rows={3}
                                                    className="input-field w-full resize-none"
                                                />
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="space-y-6">
                            {activeTab === 'overview' && (
                                <div className="space-y-6">
                                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                        <div className="card p-4">
                                            <div className="flex items-center justify-between mb-2"><span className="text-sm text-gray-400">Quantity</span><BarChart3 size={16} className="text-gray-400" /></div>
                                            <p className="text-xl font-semibold text-gray-100">{asset?.quantity || 'N/A'}</p>
                                        </div>
                                        <div className="card p-4">
                                            <div className="flex items-center justify-between mb-2"><span className="text-sm text-gray-400">Purchase Price</span><DollarSign size={16} className="text-gray-400" /></div>
                                            <p className="text-xl font-semibold text-gray-100">{formatPrice(asset?.purchase_price)}</p>
                                        </div>
                                        <div className="card p-4">
                                            <div className="flex items-center justify-between mb-2"><span className="text-sm text-gray-400">Total Value</span><Activity size={16} className="text-gray-400" /></div>
                                            <p className="text-xl font-semibold text-gray-100">{asset?.quantity && asset?.current_price ? formatPrice(asset.quantity * asset.current_price) : 'N/A'}</p>
                                        </div>
                                    </div>
                                    <div className="card p-6">
                                        <h3 className="text-lg font-semibold text-gray-100 mb-4">Profit & Loss</h3>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div>
                                                <p className="text-sm text-gray-400 mb-1">Unrealized P&L</p>
                                                <p className={`text-xl font-semibold ${asset?.quantity && asset?.purchase_price && asset?.current_price ? getChangeColor((asset.current_price - asset.purchase_price) * asset.quantity) : 'text-gray-400'}`}>{asset?.quantity && asset?.purchase_price && asset?.current_price ? formatPrice((asset.current_price - asset.purchase_price) * asset.quantity) : 'N/A'}</p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-gray-400 mb-1">P&L Percentage</p>
                                                <p className={`text-xl font-semibold ${asset?.quantity && asset?.purchase_price && asset?.current_price ? getChangeColor((asset.current_price - asset.purchase_price)) : 'text-gray-400'}`}>{asset?.quantity && asset?.purchase_price && asset?.current_price && asset.purchase_price > 0 ? `${(((asset.current_price - asset.purchase_price) / asset.purchase_price) * 100).toFixed(2)}%` : 'N/A'}</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                            {activeTab === 'chart' && (
                                <div className="card p-6 relative">
                                    <Chart
                                        data={priceHistory}
                                        symbol={asset?.symbol}
                                        period={chartPeriod}
                                        onPeriodChange={handlePeriodChange}
                                        height={500}
                                        showVolume={true}
                                        loading={loading}
                                        onRefresh={() => loadPriceHistory()}
                                        showControls={true}
                                        showPeriodSelector={true}
                                        chartType="candlestick"
                                        theme="dark"
                                        enableFullscreen={true}
                                        onFullscreenToggle={handleChartFullscreenToggle}
                                    />
                                </div>
                            )}
                            {activeTab === 'analytics' && (
                                <div className="space-y-6">
                                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                                        {/* Analytics cards */}
                                    </div>
                                </div>
                            )}
                            {activeTab === 'details' && (
                                <div className="card p-6">
                                    {/* Details content */}
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
                                <button onClick={handleCancel} className="btn-secondary" disabled={transactionLoading}>Cancel</button>
                                <button 
                                    onClick={handleSave} 
                                    className="btn-primary flex items-center space-x-2" 
                                    disabled={transactionLoading}
                                >
                                    {transactionLoading ? (
                                        <>
                                            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                            <span>Creating...</span>
                                        </>
                                    ) : (
                                        <>
                                            <Save size={16} />
                                            <span>{mode === 'create' ? 'Create Asset' : 'Save Changes'}</span>
                                        </>
                                    )}
                                </button>
                            </>
                        ) : (
                            <>
                                {mode === 'view' && (<button onClick={handleEdit} className="btn-outline flex items-center space-x-2"><Edit size={16} /><span>Edit</span></button>)}
                                <button onClick={onClose} className="btn-secondary">Close</button>
                            </>
                        )}
                    </div>
                </div>
            </div>

            {/* Fullscreen Chart Overlay */}
            {isChartFullscreen && (
                <div className="fixed inset-0 z-[60] bg-dark-950 flex flex-col">
                    <div className="flex items-center justify-between p-4 border-b border-dark-700">
                        <h3 className="text-2xl font-semibold text-gray-100">
                            {asset?.symbol} - Price Chart
                        </h3>
                        <button
                            onClick={() => setIsChartFullscreen(false)}
                            className="p-2 text-gray-400 hover:text-gray-100 hover:bg-dark-700 rounded transition-colors"
                            title="Exit fullscreen"
                        >
                            <X size={24} />
                        </button>
                    </div>
                    <div className="flex-1 p-4">
                        <Chart
                            data={priceHistory}
                            symbol={asset?.symbol}
                            period={chartPeriod}
                            onPeriodChange={handlePeriodChange}
                            height={window.innerHeight - 120}
                            showVolume={true}
                            loading={loading}
                            onRefresh={() => loadPriceHistory()}
                            showControls={true}
                            showPeriodSelector={true}
                            chartType="candlestick"
                            theme="dark"
                            enableFullscreen={true}
                            onFullscreenToggle={handleChartFullscreenToggle}
                        />
                    </div>
                </div>
            )}
        </div>
    );
};

export default AssetModal;