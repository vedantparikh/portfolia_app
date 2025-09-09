import {
    ArrowDownLeft,
    ArrowUpRight,
    Calculator,
    CircleDollarSign,
    Copy,
    Gift,
    GitBranch,
    Merge,
    Plus,
    Repeat,
    TrendingDown,
    TrendingUp,
    X,
    Zap
} from 'lucide-react';
import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { useAuth } from '../../contexts/AuthContext';
import { marketAPI } from '../../services/api';
import assetCache from '../../services/assetCache';
import { ClientSideAssetSearch } from '../shared';

const CreateTransactionModal = ({ portfolios, onClose, onCreate }) => {
    const { isAuthenticated } = useAuth();  // Get the authentication status
    const [formData, setFormData] = useState({  // State for form data
        portfolio_id: '',
        transaction_type: 'buy',
        asset_id: '',
        symbol: '',
        currency: 'USD',
        quantity: '',
        price: '',
        fees: '',
        notes: '',
        date: new Date().toISOString().split('T')[0],
        total_amount: '0',
    });
    const [loading, setLoading] = useState(false);  // Loading state
    const [selectedAsset, setSelectedAsset] = useState(null);
    const [isCreatingAsset, setIsCreatingAsset] = useState(false);
    const [fetchingPrice, setFetchingPrice] = useState(false);
    const [showAllTransactionTypes, setShowAllTransactionTypes] = useState(false);

    // Transaction types configuration
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
        return transactionTypes.find(type => type.value === formData.transaction_type) || transactionTypes[0];
    };

    // Get transaction types to display (common ones first, then all if expanded)
    const getDisplayedTransactionTypes = () => {
        const commonTypes = ['buy', 'sell', 'dividend'];

        if (!showAllTransactionTypes) {
            return transactionTypes.filter(type => commonTypes.includes(type.value));
        }

        return transactionTypes;
    };

    // Preload assets when the modal opens
    useEffect(() => {
        console.log('[CreateTransactionModal] Modal opened, preloading assets...');
        assetCache.preloadAssets();
    }, []);

    // Function to fetch current price for a symbol
    const fetchCurrentPrice = async (symbol) => {
        try {
            setFetchingPrice(true);
            console.log(`[CreateTransactionModal] Fetching price for symbol: ${symbol}`);

            const priceData = await marketAPI.getStockLatestData(symbol);
            console.log(`[CreateTransactionModal] Price data received:`, priceData);

            if (priceData && Array.isArray(priceData) && priceData.length > 0) {
                const latestData = priceData[0];
                const price = parseFloat(latestData.latest_price || latestData.Close || latestData.close || latestData.price);

                if (!isNaN(price)) {
                    console.log(`[CreateTransactionModal] Setting price: ${price} for ${symbol}`);
                    setFormData(prev => ({
                        ...prev,
                        price: price.toString()
                    }));
                    return price;
                }
            } else if (priceData && typeof priceData === 'object' && !Array.isArray(priceData)) {
                const price = parseFloat(priceData.latest_price || priceData.Close || priceData.close || priceData.price);

                if (!isNaN(price)) {
                    console.log(`[CreateTransactionModal] Setting price (object): ${price} for ${symbol}`);
                    setFormData(prev => ({
                        ...prev,
                        price: price.toString()
                    }));
                    return price;
                }
            }

            console.warn(`[CreateTransactionModal] No valid price found for ${symbol}`);
            return null;
        } catch (error) {
            console.error(`[CreateTransactionModal] Failed to fetch price for ${symbol}:`, error);
            return null;
        } finally {
            setFetchingPrice(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSymbolSelect = async (asset) => {
        console.log('[CreateTransactionModal] Asset selected:', asset);

        setSelectedAsset(asset);
        setFormData(prev => ({
            ...prev,
            symbol: asset.symbol,
            asset_id: asset.id
        }));

        // Automatically fetch current price for the selected asset
        if (asset.symbol) {
            await fetchCurrentPrice(asset.symbol);
        }
    };

    const handleSymbolChange = (value) => {
        setFormData(prev => ({
            ...prev,
            symbol: value,
            // Clear asset_id when manually typing since it might not match
            asset_id: ''
        }));

        // Clear selected asset when manually typing
        if (!value) {
            setSelectedAsset(null);
        } else {
            // Try to find the asset in cache if user typed a complete symbol
            const cachedAsset = assetCache.findAssetBySymbol(value);
            if (cachedAsset) {
                console.log('[CreateTransactionModal] Found asset in cache:', cachedAsset);
                setSelectedAsset(cachedAsset);
                setFormData(prev => ({
                    ...prev,
                    asset_id: cachedAsset.id
                }));
            }
        }
    };

    const handlePriceUpdate = (priceData) => {
        if (priceData && priceData.price) {
            setFormData(prev => ({
                ...prev,
                price: priceData.price.toString()
            }));
        }
    };

    const calculateTotal = () => {
        const quantity = parseFloat(formData.quantity) || 0;
        const price = parseFloat(formData.price) || 0;
        const fees = parseFloat(formData.fees) || 0;

        // Some transaction types don't involve monetary exchange
        const selectedType = getSelectedTransactionType();
        const monetaryTypes = ['buy', 'sell', 'dividend', 'fee', 'transfer_in', 'transfer_out'];

        if (!monetaryTypes.includes(selectedType.value)) {
            return fees; // Only fees for non-monetary transactions
        }

        return (quantity * price) + fees;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!formData.portfolio_id) {
            toast.error('Please select a portfolio');
            return;
        }

        if (!formData.symbol.trim()) {
            toast.error('Symbol is required');
            return;
        }

        // Try to find the asset in cache if asset_id is missing
        if (!formData.asset_id && formData.symbol) {
            const cachedAsset = assetCache.findAssetBySymbol(formData.symbol);
            if (cachedAsset) {
                console.log('[CreateTransactionModal] Found asset during validation:', cachedAsset);
                setFormData(prev => ({
                    ...prev,
                    asset_id: cachedAsset.id
                }));
                // Continue with the updated asset_id
                formData.asset_id = cachedAsset.id;
            } else {
                toast.error(`Asset "${formData.symbol}" not found. Please select an asset from the search results or add it first in the Assets section.`);
                return;
            }
        }

        if (!formData.asset_id) {
            toast.error('Please select an asset from the search results. If the asset doesn\'t exist, add it first in the Assets section.');
            return;
        }

        // Validation based on transaction type
        const selectedType = getSelectedTransactionType();
        const requiresQuantity = !['fee'].includes(selectedType.value);
        const requiresPrice = ['buy', 'sell', 'dividend', 'transfer_in', 'transfer_out'].includes(selectedType.value);

        if (requiresQuantity && (!formData.quantity || parseFloat(formData.quantity) <= 0)) {
            toast.error('Valid quantity is required');
            return;
        }

        if (requiresPrice && (!formData.price || parseFloat(formData.price) <= 0)) {
            toast.error('Valid price is required');
            return;
        }

        try {
            setLoading(true);

            const transactionData = {
                portfolio_id: parseInt(formData.portfolio_id),
                transaction_type: formData.transaction_type,
                asset_id: parseInt(formData.asset_id),
                currency: formData.currency,
                quantity: parseFloat(formData.quantity),
                price: parseFloat(formData.price),
                fees: parseFloat(formData.fees) || 0,
                notes: formData.notes.trim(),
                transaction_date: formData.date,
                total_amount: parseFloat(formData.total_amount)
            };

            // Calculate total_amount before sending
            transactionData.total_amount = calculateTotal();

            await onCreate(transactionData);
        } catch (error) {
            console.error('Error creating transaction:', error);
            // Don't show error toast here as it's handled in the parent component
        } finally {
            setLoading(false);
        }
    };

    const totalAmount = calculateTotal();

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-dark-900 rounded-xl border border-dark-700 w-full max-w-2xl max-h-[95vh] overflow-hidden flex flex-col">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-dark-700">
                    <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-primary-600/20 rounded-lg flex items-center justify-center">
                            {(() => {
                                const selectedType = getSelectedTransactionType();
                                const IconComponent = selectedType.icon;
                                const colorScheme = colorSchemes[selectedType.color];
                                return <IconComponent size={20} className={colorScheme.text} />;
                            })()}
                        </div>
                        <div>
                            <h2 className="text-xl font-bold text-gray-100">Create Transaction</h2>
                            <p className="text-sm text-gray-400">
                                Add a new {getSelectedTransactionType().label.toLowerCase()} transaction
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

                {/* Form */}
                <form onSubmit={handleSubmit} className="p-6 space-y-6 flex-1 overflow-y-auto">
                    {/* Authentication Status */}
                    {!isAuthenticated && (
                        <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-3">
                            <p className="text-red-400 text-sm">
                                ⚠️ You need to be logged in to add transactions.
                            </p>
                        </div>
                    )}
                    {/* Transaction Type */}
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
                                const isSelected = formData.transaction_type === type.value;

                                return (
                                    <button
                                        key={type.value}
                                        type="button"
                                        onClick={() => setFormData(prev => ({ ...prev, transaction_type: type.value }))}
                                        className={`p-3 rounded-lg border-2 transition-colors ${isSelected
                                            ? `${colorScheme.border} ${colorScheme.bg} ${colorScheme.text}`
                                            : `border-dark-600 bg-dark-800 text-gray-300 hover:border-dark-500 ${colorScheme.hover}`
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
                            value={formData.portfolio_id}
                            onChange={handleInputChange}
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

                    {/* Symbol */}
                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                            Asset Symbol *
                        </label>
                        <ClientSideAssetSearch
                            value={formData.symbol}
                            onChange={handleSymbolChange}
                            onSelect={handleSymbolSelect}
                            onPriceUpdate={handlePriceUpdate}
                            placeholder="Search your assets..."
                            disabled={loading}
                            showSuggestions={isAuthenticated}
                            preloadAssets={true}
                        />

                        {/* Selected Asset Info */}
                        {selectedAsset && (
                            <div className="mt-2 p-3 bg-dark-800 rounded-lg border border-dark-600">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-8 h-8 bg-primary-600/20 rounded-lg flex items-center justify-center">
                                            <TrendingUp size={16} className="text-primary-400" />
                                        </div>
                                        <div>
                                            <div className="font-mono text-sm font-medium text-gray-100">
                                                {selectedAsset.symbol}
                                            </div>
                                            <div className="text-xs text-gray-400">
                                                {selectedAsset.name}
                                            </div>
                                            <div className="text-xs text-gray-500">
                                                {selectedAsset.exchange} • {selectedAsset.asset_type}
                                            </div>
                                        </div>
                                    </div>
                                    <div className="text-xs text-gray-400">
                                        Your Asset
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Help Text */}
                        <div className="mt-2 text-xs text-gray-500">
                            If the asset doesn't exist, add it first in the Assets section.
                        </div>
                    </div>
                    {/* Quantity and Price */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {(() => {
                            const selectedType = getSelectedTransactionType();
                            const requiresQuantity = !['fee'].includes(selectedType.value);
                            const requiresPrice = ['buy', 'sell', 'dividend', 'transfer_in', 'transfer_out'].includes(selectedType.value);

                            return (
                                <>
                                    {requiresQuantity && (
                                        <div>
                                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                                {selectedType.value === 'split' ? 'Split Ratio' : 'Quantity'} *
                                            </label>
                                            <input
                                                type="number"
                                                name="quantity"
                                                value={formData.quantity}
                                                onChange={handleInputChange}
                                                placeholder={selectedType.value === 'split' ? "2" : "0.00"}
                                                min="0"
                                                step={selectedType.value === 'split' ? "1" : "0.000001"}
                                                className="input-field w-full"
                                                required
                                            />
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
                                                    value={formData.price}
                                                    onChange={handleInputChange}
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
                                        <div className="md:col-span-2">
                                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                                Fee Amount *
                                            </label>
                                            <input
                                                type="number"
                                                name="fees"
                                                value={formData.fees}
                                                onChange={handleInputChange}
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
                                                value={formData.fees}
                                                onChange={handleInputChange}
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
                                            value={formData.date}
                                            onChange={handleInputChange}
                                            className="input-field w-full"
                                        />
                                    </div>
                                </>
                            );
                        })()}
                    </div>

                    {/* Total Amount Display */}
                    <div className="bg-dark-800 rounded-lg p-4">
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
                                    return `${sign}$${totalAmount.toFixed(2)}`;
                                })()}
                            </span>
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                            {(() => {
                                const selectedType = getSelectedTransactionType();
                                const monetaryTypes = ['buy', 'sell', 'dividend', 'transfer_in', 'transfer_out'];

                                if (monetaryTypes.includes(selectedType.value)) {
                                    return `${formData.quantity || 0} × $${formData.price || 0} + $${formData.fees || 0} fees`;
                                } else {
                                    return `$${formData.fees || 0} fees only`;
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
                            value={formData.notes}
                            onChange={handleInputChange}
                            placeholder="Optional notes about this transaction..."
                            rows={3}
                            className="input-field w-full resize-none"
                        />
                    </div>
                </form>

                {/* Footer */}
                <div className="flex items-center justify-end space-x-3 p-6 border-t border-dark-700 flex-shrink-0">
                    <button
                        type="button"
                        onClick={onClose}
                        className="btn-secondary"
                        disabled={loading}
                    >
                        Cancel
                    </button>
                    <button
                        type="submit"
                        onClick={handleSubmit}
                        disabled={loading || !formData.portfolio_id || !formData.symbol || !formData.quantity || !formData.price}
                        className="btn-primary flex items-center space-x-2"
                    >
                        {loading ? (
                            <>
                                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                <span>Creating...</span>
                            </>
                        ) : (
                            <>
                                <Plus size={16} />
                                <span>Create Transaction</span>
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default CreateTransactionModal;
