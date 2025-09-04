import React, { useState } from 'react';
import toast from 'react-hot-toast';
import { marketAPI } from '../../services/api';

const SymbolSearchTest = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);

    const testSymbolSearch = async () => {
        if (!searchQuery.trim()) {
            toast.error('Please enter a symbol to search');
            return;
        }

        setLoading(true);
        try {
            const response = await marketAPI.searchSymbols(searchQuery.trim());
            setResults(response || []);
            toast.success(`Found ${response?.length || 0} results for "${searchQuery}"`);
        } catch (error) {
            console.error('Symbol search failed:', error);
            toast.error('Symbol search failed: ' + (error.response?.data?.detail || error.message));
            setResults([]);
        } finally {
            setLoading(false);
        }
    };

    const handleSymbolSelect = (symbol) => {
        console.log('Selected symbol:', symbol);
        toast.success(`Selected: ${symbol.symbol} - ${symbol.longname || symbol.shortname}`);
    };

    return (
        <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-100 mb-4">Symbol Search Test</h3>
            <p className="text-sm text-gray-400 mb-4">
                Test the symbol search functionality that will be used in asset creation
            </p>

            <div className="space-y-4">
                <div className="flex space-x-2">
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Enter symbol (e.g., AAPL, MSFT, BTC)"
                        className="input-field flex-1"
                        onKeyPress={(e) => e.key === 'Enter' && testSymbolSearch()}
                    />
                    <button
                        onClick={testSymbolSearch}
                        disabled={loading || !searchQuery.trim()}
                        className="btn-primary"
                    >
                        {loading ? 'Searching...' : 'Search'}
                    </button>
                </div>

                {results.length > 0 && (
                    <div className="space-y-2">
                        <h4 className="text-md font-medium text-gray-200">Search Results:</h4>
                        <div className="max-h-64 overflow-y-auto space-y-2">
                            {results.slice(0, 10).map((result, index) => (
                                <div
                                    key={index}
                                    onClick={() => handleSymbolSelect(result)}
                                    className="p-3 bg-dark-800 border border-dark-600 rounded-lg cursor-pointer hover:bg-dark-700 transition-colors"
                                >
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <div className="font-mono text-sm text-gray-100">
                                                {result.symbol}
                                            </div>
                                            <div className="text-xs text-gray-400 truncate">
                                                {result.longname || result.shortname || result.name}
                                            </div>
                                        </div>
                                        <div className="text-right text-xs text-gray-500">
                                            <div>{result.exchDisp}</div>
                                            <div>{result.typeDisp}</div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {loading && (
                    <div className="flex items-center justify-center py-8">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
                        <span className="ml-2 text-gray-400">Searching...</span>
                    </div>
                )}
            </div>
        </div>
    );
};

export default SymbolSearchTest;
