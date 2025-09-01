import { Search, TrendingUp, X } from 'lucide-react';
import React, { useEffect, useRef, useState } from 'react';
import toast from 'react-hot-toast';
import { useAuth } from '../../contexts/AuthContext';
import { authUtils, marketAPI } from '../../services/api';

const AddSymbolModal = ({ isOpen, onClose, onAdd }) => {
    const { isAuthenticated } = useAuth();
    const [symbol, setSymbol] = useState('');
    const [loading, setLoading] = useState(false);
    const [suggestions, setSuggestions] = useState([]);
    const [showSuggestions, setShowSuggestions] = useState(false);
    const [error, setError] = useState('');
    const [searching, setSearching] = useState(false);
    const debounceTimeoutRef = useRef(null);

    // Popular symbols for quick access
    const popularSymbols = [
        'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
        'SPY', 'QQQ', 'IWM', 'VTI', 'VOO', 'ARKK', 'BTC', 'ETH'
    ];

    // Cleanup debounce timeout on unmount
    useEffect(() => {
        return () => {
            if (debounceTimeoutRef.current) {
                clearTimeout(debounceTimeoutRef.current);
            }
        };
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!symbol.trim()) {
            setError('Please enter a symbol');
            return;
        }

        // Validate symbol format (basic validation)
        const symbolRegex = /^[A-Z]{1,5}$/;
        if (!symbolRegex.test(symbol.trim().toUpperCase())) {
            setError('Please enter a valid stock symbol (1-5 uppercase letters)');
            return;
        }

        setLoading(true);
        setError('');
        
        try {
            // For manual form submission, create a basic symbol object
            const symbolData = {
                symbol: symbol.trim().toUpperCase(),
                name: symbol.trim().toUpperCase() // Use symbol as name if no company name available
            };
            
            await onAdd(symbolData);
            handleClose();
            toast.success(`Added ${symbol.trim().toUpperCase()} to watchlist`);
        } catch (error) {
            console.error('Failed to add symbol:', error);
            const errorMessage = error.response?.data?.message || error.message || 'Failed to add symbol';
            setError(errorMessage);
            toast.error(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    const handleClose = () => {
        // Clear debounce timeout
        if (debounceTimeoutRef.current) {
            clearTimeout(debounceTimeoutRef.current);
        }
        
        setSymbol('');
        setLoading(false);
        setSuggestions([]);
        setShowSuggestions(false);
        setError('');
        onClose();
    };

    const handleSymbolChange = (value) => {
        setSymbol(value);
        setError(''); // Clear error when user types
        
        // Clear existing timeout
        if (debounceTimeoutRef.current) {
            clearTimeout(debounceTimeoutRef.current);
        }
        
        // Set new timeout for debounced search
        debounceTimeoutRef.current = setTimeout(async () => {
            await performSearch(value);
        }, 400);
        
        // For immediate feedback, show popular symbols for short inputs
        if (value.trim().length === 1) {
            const filtered = popularSymbols.filter(s => 
                s.toLowerCase().includes(value.toLowerCase())
            );
            setSuggestions(filtered);
            setShowSuggestions(true);
        } else if (!value.trim()) {
            setSuggestions([]);
            setShowSuggestions(false);
        }
    };

    const performSearch = async (value) => {
        if (value.trim().length < 2) {
            if (value.trim()) {
                // For single character, just filter popular symbols
                const filtered = popularSymbols.filter(s => 
                    s.toLowerCase().includes(value.toLowerCase())
                );
                setSuggestions(filtered);
                setShowSuggestions(true);
            } else {
                setSuggestions([]);
                setShowSuggestions(false);
            }
            return;
        }

        setSearching(true);
        try {
            // Check authentication before making API call
            if (!authUtils.isAuthenticated()) {
                console.warn('[AddSymbolModal] User not authenticated for symbol search');
                toast.error('Please log in to search for symbols');
                setError('Authentication required');
                setSuggestions([]);
                setShowSuggestions(false);
                return;
            }

            const results = await marketAPI.searchSymbols(value.trim());
            setSuggestions(results);
            setShowSuggestions(true);
        } catch (error) {
            console.error('Failed to search symbols:', error);
            
            // Handle authentication errors
            if (error.response?.status === 401) {
                toast.error('Session expired. Please log in again.');
                setError('Authentication required');
                setSuggestions([]);
                setShowSuggestions(false);
            } else {
                // Fallback to popular symbols if API fails
                const filtered = popularSymbols.filter(s => 
                    s.toLowerCase().includes(value.toLowerCase())
                );
                setSuggestions(filtered);
                setShowSuggestions(true);
                toast.error('Search failed. Using popular symbols instead.');
            }
        } finally {
            setSearching(false);
        }
    };

    const handleSuggestionClick = async (suggestion) => {
        const symbolValue = typeof suggestion === 'string' ? suggestion : suggestion.symbol || suggestion.name;
        setSymbol(symbolValue);
        setShowSuggestions(false);
        setError('');
        
        // Automatically add the symbol to watchlist when clicked
        try {
            // Pass the complete suggestion object to preserve all symbol information
            await onAdd(suggestion);
            handleClose();
            toast.success(`Added ${symbolValue} to watchlist`);
        } catch (error) {
            console.error('Failed to add symbol:', error);
            const errorMessage = error.response?.data?.message || error.message || 'Failed to add symbol';
            setError(errorMessage);
            toast.error(errorMessage);
        }
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
                    {/* Authentication Status */}
                    {!isAuthenticated && (
                        <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-3">
                            <p className="text-red-400 text-sm">
                                ⚠️ You need to be logged in to search for symbols. Popular symbols are still available.
                            </p>
                        </div>
                    )}
                    
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
                                disabled={loading}
                            />
                            <Search size={20} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                        </div>

                        {/* Error Message */}
                        {error && (
                            <p className="mt-2 text-sm text-red-400">{error}</p>
                        )}

                        {/* Suggestions */}
                        {showSuggestions && suggestions.length > 0 && (
                            <div className="absolute top-full left-0 right-0 mt-1 bg-dark-800 border border-dark-600 rounded-lg shadow-lg z-10 max-h-48 overflow-y-auto">
                                {searching && (
                                    <div className="px-4 py-3 text-gray-400 text-sm flex items-center space-x-2">
                                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-500"></div>
                                        <span>Searching...</span>
                                    </div>
                                )}
                                {suggestions.map((suggestion, index) => (
                                    <button
                                        key={index}
                                        type="button"
                                        onClick={() => handleSuggestionClick(suggestion)}
                                        className="w-full flex items-center space-x-3 px-4 py-3 text-left text-gray-300 hover:bg-dark-700 transition-colors"
                                    >
                                        <TrendingUp size={16} className="text-primary-400" />
                                        <span className="font-mono">
                                            {typeof suggestion === 'string' ? suggestion : suggestion.symbol || suggestion.name}
                                        </span>
                                        {typeof suggestion === 'object' && suggestion.name && (
                                            <span className="text-sm text-gray-500 truncate">
                                                {suggestion.name}
                                            </span>
                                        )}
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
                            {popularSymbols.slice(0, 8).map((popSymbol) => (
                                <button
                                    key={popSymbol}
                                    type="button"
                                    onClick={() => handleSuggestionClick(popSymbol)}
                                    className="px-3 py-2 text-sm bg-dark-800 border border-dark-600 rounded-lg text-gray-300 hover:bg-dark-700 hover:border-primary-500 transition-colors font-mono"
                                >
                                    {popSymbol}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex items-center justify-end space-x-3 pt-4">
                        <button
                            type="button"
                            onClick={handleClose}
                            className="px-4 py-2 text-gray-400 hover:text-gray-300 transition-colors"
                            disabled={loading}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={loading || !symbol.trim()}
                            className="px-6 py-2 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center space-x-2"
                        >
                            {loading ? (
                                <>
                                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                    <span>Adding...</span>
                                </>
                            ) : (
                                <span>Add Symbol</span>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default AddSymbolModal;
