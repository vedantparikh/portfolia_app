import { Search, TrendingUp, X } from 'lucide-react';
import React, { useState } from 'react';

const AddSymbolModal = ({ isOpen, onClose, onAdd }) => {
    const [symbol, setSymbol] = useState('');
    const [loading, setLoading] = useState(false);
    const [suggestions, setSuggestions] = useState([]);
    const [showSuggestions, setShowSuggestions] = useState(false);

    // Mock popular symbols - in a real app, this would come from an API
    const popularSymbols = [
        'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
        'SPY', 'QQQ', 'IWM', 'VTI', 'VOO', 'ARKK', 'BTC', 'ETH'
    ];

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!symbol.trim()) {
            alert('Please enter a symbol');
            return;
        }

        setLoading(true);
        try {
            await onAdd(symbol.trim().toUpperCase());
            handleClose();
        } catch (error) {
            console.error('Failed to add symbol:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleClose = () => {
        setSymbol('');
        setLoading(false);
        setSuggestions([]);
        setShowSuggestions(false);
        onClose();
    };

    const handleSymbolChange = (value) => {
        setSymbol(value);
        
        if (value.trim()) {
            // Filter popular symbols based on input
            const filtered = popularSymbols.filter(s => 
                s.toLowerCase().includes(value.toLowerCase())
            );
            setSuggestions(filtered);
            setShowSuggestions(true);
        } else {
            setSuggestions([]);
            setShowSuggestions(false);
        }
    };

    const handleSuggestionClick = (suggestion) => {
        setSymbol(suggestion);
        setShowSuggestions(false);
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && suggestions.length > 0 && showSuggestions) {
            handleSuggestionClick(suggestions[0]);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-dark-900 border border-dark-700 rounded-lg w-full max-w-md mx-4">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-dark-700">
                    <h2 className="text-lg font-semibold text-gray-100">Add Symbol</h2>
                    <button
                        onClick={handleClose}
                        className="p-2 rounded-lg hover:bg-dark-800 transition-colors"
                    >
                        <X size={20} className="text-gray-400" />
                    </button>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit} className="p-6 space-y-6">
                    {/* Symbol Input */}
                    <div className="relative">
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                            Stock Symbol *
                        </label>
                        <div className="relative">
                            <input
                                type="text"
                                value={symbol}
                                onChange={(e) => handleSymbolChange(e.target.value)}
                                onKeyDown={handleKeyDown}
                                onFocus={() => symbol.trim() && setShowSuggestions(true)}
                                className="w-full pl-10 pr-4 py-3 bg-dark-800 border border-dark-600 rounded-lg text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-center text-lg font-mono"
                                placeholder="e.g., AAPL"
                                required
                                autoFocus
                            />
                            <Search size={20} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                        </div>

                        {/* Suggestions */}
                        {showSuggestions && suggestions.length > 0 && (
                            <div className="absolute top-full left-0 right-0 mt-1 bg-dark-800 border border-dark-600 rounded-lg shadow-lg z-10 max-h-48 overflow-y-auto">
                                {suggestions.map((suggestion, index) => (
                                    <button
                                        key={suggestion}
                                        type="button"
                                        onClick={() => handleSuggestionClick(suggestion)}
                                        className={`w-full px-4 py-2 text-left text-gray-100 hover:bg-dark-700 transition-colors ${
                                            index === 0 ? 'rounded-t-lg' : ''
                                        } ${index === suggestions.length - 1 ? 'rounded-b-lg' : ''}`}
                                    >
                                        <div className="flex items-center space-x-3">
                                            <TrendingUp size={16} className="text-primary-400" />
                                            <span className="font-mono">{suggestion}</span>
                                        </div>
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Popular Symbols */}
                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-3">
                            Popular Symbols
                        </label>
                        <div className="grid grid-cols-4 gap-2">
                            {popularSymbols.slice(0, 12).map((popSymbol) => (
                                <button
                                    key={popSymbol}
                                    type="button"
                                    onClick={() => handleSuggestionClick(popSymbol)}
                                    className="px-3 py-2 bg-dark-800 border border-dark-600 rounded-lg text-gray-300 hover:bg-dark-700 hover:border-primary-500 transition-colors text-sm font-mono"
                                >
                                    {popSymbol}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Info */}
                    <div className="bg-dark-800/50 border border-dark-600 rounded-lg p-4">
                        <div className="flex items-start space-x-3">
                            <TrendingUp size={16} className="text-primary-400 mt-0.5" />
                            <div className="text-sm text-gray-400">
                                <p className="font-medium text-gray-300 mb-1">Symbol Guidelines:</p>
                                <ul className="space-y-1 text-xs">
                                    <li>• Use standard stock symbols (e.g., AAPL, GOOGL)</li>
                                    <li>• For ETFs, use their ticker symbols (e.g., SPY, QQQ)</li>
                                    <li>• Cryptocurrencies are supported (e.g., BTC, ETH)</li>
                                    <li>• Symbols are case-insensitive</li>
                                </ul>
                            </div>
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center space-x-3 pt-4">
                        <button
                            type="button"
                            onClick={handleClose}
                            className="flex-1 px-4 py-2 border border-dark-600 text-gray-300 rounded-lg hover:bg-dark-800 transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={loading || !symbol.trim()}
                            className="flex-1 px-4 py-2 bg-primary-600 hover:bg-primary-700 disabled:bg-primary-600/50 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
                        >
                            {loading ? 'Adding...' : 'Add Symbol'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default AddSymbolModal;
