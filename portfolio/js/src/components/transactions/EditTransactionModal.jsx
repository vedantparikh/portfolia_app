import { Calculator, Edit, TrendingDown, TrendingUp, X } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { ClientSideAssetSearch } from '../shared';

const EditTransactionModal = ({ isOpen, onClose, transaction, portfolios, onUpdate }) => {
    const [formData, setFormData] = useState({
        portfolio_id: '',
        type: 'buy',
        symbol: '',
        asset_id: '',
        quantity: '',
        price: '',
        fees: '',
        notes: '',
        date: ''
    });
    const [loading, setLoading] = useState(false);
    const [selectedAsset, setSelectedAsset] = useState(null);

    useEffect(() => {
        if (transaction) {
            setFormData({
                portfolio_id: transaction.portfolio_id || '',
                type: transaction.type || 'buy',
                symbol: transaction.symbol || '',
                asset_id: transaction.asset_id || '',
                quantity: transaction.quantity || '',
                price: transaction.price || '',
                fees: transaction.fees || '',
                notes: transaction.notes || '',
                date: transaction.transaction_date ? transaction.transaction_date.split('T')[0] : new Date().toISOString().split('T')[0]
            });

            // Set selected asset if we have asset info
            if (transaction.asset_id && transaction.symbol) {
                setSelectedAsset({
                    id: transaction.asset_id,
                    symbol: transaction.symbol,
                    type: 'existing_asset'
                });
            }
        }
    }, [transaction]);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSymbolSelect = (asset) => {
        setSelectedAsset(asset);
        setFormData(prev => ({
            ...prev,
            symbol: asset.symbol,
            asset_id: asset.id
        }));
    };

    const handleSymbolChange = (value) => {
        setFormData(prev => ({
            ...prev,
            symbol: value
        }));
        // Clear selected asset when manually typing
        if (!value) {
            setSelectedAsset(null);
        }
    };

    const handlePriceUpdate = (priceData) => {
        if (priceData && priceData.price) {
            setFormData(prev => ({
                ...prev,
                price: priceData.price.toString()
            }));
            toast.success(`Current price for ${priceData.symbol}: $${priceData.price} (${priceData.currency})`);
        }
    };

    const calculateTotal = () => {
        const quantity = parseFloat(formData.quantity) || 0;
        const price = parseFloat(formData.price) || 0;
        const fees = parseFloat(formData.fees) || 0;
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

        if (!formData.asset_id) {
            toast.error('Please select an asset from the search results. If the asset doesn\'t exist, add it first in the Assets section.');
            return;
        }

        if (!formData.quantity || parseFloat(formData.quantity) <= 0) {
            toast.error('Valid quantity is required');
            return;
        }

        if (!formData.price || parseFloat(formData.price) <= 0) {
            toast.error('Valid price is required');
            return;
        }

        try {
            setLoading(true);

            const transactionData = {
                portfolio_id: parseInt(formData.portfolio_id),
                type: formData.type,
                asset_id: parseInt(formData.asset_id),
                quantity: parseFloat(formData.quantity),
                price: parseFloat(formData.price),
                fees: parseFloat(formData.fees) || 0,
                notes: formData.notes.trim(),
                transaction_date: formData.date
            };

            await onUpdate(transaction.id, transactionData);
            onClose();
        } catch (error) {
            console.error('Error updating transaction:', error);
        } finally {
            setLoading(false);
        }
    };

    const totalAmount = calculateTotal();

    if (!isOpen || !transaction) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-dark-900 rounded-xl border border-dark-700 w-full max-w-2xl max-h-[90vh] overflow-hidden">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-dark-700">
                    <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-primary-600/20 rounded-lg flex items-center justify-center">
                            {formData.type === 'buy' ? (
                                <TrendingUp size={20} className="text-success-400" />
                            ) : (
                                <TrendingDown size={20} className="text-danger-400" />
                            )}
                        </div>
                        <div>
                            <h2 className="text-xl font-bold text-gray-100">Edit Transaction</h2>
                            <p className="text-sm text-gray-400">Update transaction details</p>
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
                <form onSubmit={handleSubmit} className="p-6 space-y-6 max-h-[calc(90vh-140px)] overflow-y-auto">
                    {/* Transaction Type */}
                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-3">
                            Transaction Type
                        </label>
                        <div className="grid grid-cols-2 gap-3">
                            <button
                                type="button"
                                onClick={() => setFormData(prev => ({ ...prev, type: 'buy' }))}
                                className={`p-4 rounded-lg border-2 transition-colors ${formData.type === 'buy'
                                    ? 'border-success-400 bg-success-400/10 text-success-400'
                                    : 'border-dark-600 bg-dark-800 text-gray-300 hover:border-dark-500'
                                    }`}
                            >
                                <div className="flex items-center space-x-3">
                                    <TrendingUp size={20} />
                                    <div className="text-left">
                                        <div className="font-medium">Buy</div>
                                        <div className="text-xs opacity-75">Purchase assets</div>
                                    </div>
                                </div>
                            </button>
                            <button
                                type="button"
                                onClick={() => setFormData(prev => ({ ...prev, type: 'sell' }))}
                                className={`p-4 rounded-lg border-2 transition-colors ${formData.type === 'sell'
                                    ? 'border-danger-400 bg-danger-400/10 text-danger-400'
                                    : 'border-dark-600 bg-dark-800 text-gray-300 hover:border-dark-500'
                                    }`}
                            >
                                <div className="flex items-center space-x-3">
                                    <TrendingDown size={20} />
                                    <div className="text-left">
                                        <div className="font-medium">Sell</div>
                                        <div className="text-xs opacity-75">Sell assets</div>
                                    </div>
                                </div>
                            </button>
                        </div>
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
                            showSuggestions={true}
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
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                Quantity *
                            </label>
                            <input
                                type="number"
                                name="quantity"
                                value={formData.quantity}
                                onChange={handleInputChange}
                                placeholder="0.00"
                                min="0"
                                step="0.000001"
                                className="input-field w-full"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                Price per Share *
                            </label>
                            <input
                                type="number"
                                name="price"
                                value={formData.price}
                                onChange={handleInputChange}
                                placeholder="0.00"
                                min="0"
                                step="0.01"
                                className="input-field w-full"
                                required
                            />
                        </div>
                    </div>

                    {/* Fees and Date */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                Fees
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
                        <div>
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
                    </div>

                    {/* Total Amount Display */}
                    <div className="bg-dark-800 rounded-lg p-4">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                                <Calculator size={16} className="text-gray-400" />
                                <span className="text-sm font-medium text-gray-300">Total Amount</span>
                            </div>
                            <span className="text-xl font-bold text-gray-100">
                                {formData.type === 'buy' ? '-' : '+'}${totalAmount.toFixed(2)}
                            </span>
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                            {formData.quantity} × ${formData.price || 0} + ${formData.fees || 0} fees
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
                <div className="flex items-center justify-end space-x-3 p-6 border-t border-dark-700">
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
                                <span>Updating...</span>
                            </>
                        ) : (
                            <>
                                <Edit size={16} />
                                <span>Update Transaction</span>
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default EditTransactionModal;
