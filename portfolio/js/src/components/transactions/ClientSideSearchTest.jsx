import { AlertCircle, CheckCircle, Database, RefreshCw, TrendingUp, XCircle } from 'lucide-react';
import React, { useState } from 'react';
import toast from 'react-hot-toast';
import { assetAPI, marketAPI } from '../../services/api';
import { ClientSideAssetSearch } from '../shared';

const ClientSideSearchTest = () => {
    const [testResults, setTestResults] = useState({});
    const [isRunning, setIsRunning] = useState(false);
    const [selectedAsset, setSelectedAsset] = useState(null);
    const [searchValue, setSearchValue] = useState('');
    const [priceData, setPriceData] = useState(null);

    const runTest = async (testName, testFunction) => {
        try {
            const result = await testFunction();
            setTestResults(prev => ({
                ...prev,
                [testName]: { status: 'success', result, error: null }
            }));
            return result;
        } catch (error) {
            setTestResults(prev => ({
                ...prev,
                [testName]: { status: 'error', result: null, error: error.message }
            }));
            throw error;
        }
    };

    const testAssetFetching = async () => {
        const assets = await assetAPI.getAssets({ limit: 100 });
        return { count: assets.length, sample: assets.slice(0, 3) };
    };

    const testPriceFetching = async () => {
        if (!selectedAsset) {
            throw new Error('No asset selected for price testing');
        }

        const priceData = await marketAPI.getStockLatestData([selectedAsset.symbol]);
        return priceData;
    };

    const testSearchFunctionality = async () => {
        // This test simulates the search functionality
        const assets = await assetAPI.getAssets({ limit: 100 });
        const searchTerm = 'AAPL'; // Test with a common symbol

        const filtered = assets.filter(asset =>
            asset.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
            (asset.name && asset.name.toLowerCase().includes(searchTerm.toLowerCase()))
        );

        return {
            searchTerm,
            totalAssets: assets.length,
            filteredCount: filtered.length,
            results: filtered.slice(0, 5)
        };
    };

    const runAllTests = async () => {
        setIsRunning(true);
        setTestResults({});

        try {
            // Test 1: Asset Fetching
            await runTest('Asset Fetching', testAssetFetching);

            // Test 2: Search Functionality
            await runTest('Search Functionality', testSearchFunctionality);

            // Test 3: Price Fetching (if asset is selected)
            if (selectedAsset) {
                await runTest('Price Fetching', testPriceFetching);
            }

            toast.success('All client-side search tests completed successfully!');
        } catch (error) {
            toast.error('Some tests failed. Check the results below.');
        } finally {
            setIsRunning(false);
        }
    };

    const handleAssetSelect = (asset) => {
        setSelectedAsset(asset);
        setPriceData(null);
    };

    const handlePriceUpdate = (price) => {
        setPriceData(price);
        toast.success(`Price updated for ${price.symbol}: $${price.price} (${price.currency})`);
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'success':
                return <CheckCircle size={16} className="text-green-400" />;
            case 'error':
                return <XCircle size={16} className="text-red-400" />;
            default:
                return <AlertCircle size={16} className="text-yellow-400" />;
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'success':
                return 'text-green-400';
            case 'error':
                return 'text-red-400';
            default:
                return 'text-yellow-400';
        }
    };

    return (
        <div className="card p-6">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h3 className="text-lg font-semibold text-gray-100 mb-2">
                        Client-Side Asset Search Test
                    </h3>
                    <p className="text-sm text-gray-400">
                        Test the new client-side search with local filtering and price fetching
                    </p>
                </div>
                <button
                    onClick={runAllTests}
                    disabled={isRunning}
                    className="btn-primary flex items-center space-x-2"
                >
                    {isRunning ? (
                        <RefreshCw size={16} className="animate-spin" />
                    ) : (
                        <RefreshCw size={16} />
                    )}
                    <span>{isRunning ? 'Running Tests...' : 'Run Tests'}</span>
                </button>
            </div>

            {/* Interactive Search Test */}
            <div className="mb-6 p-4 bg-dark-800 rounded-lg">
                <h4 className="text-gray-300 font-medium mb-3">Interactive Search Test</h4>
                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                            Search Assets
                        </label>
                        <ClientSideAssetSearch
                            value={searchValue}
                            onChange={setSearchValue}
                            onSelect={handleAssetSelect}
                            onPriceUpdate={handlePriceUpdate}
                            placeholder="Type to search assets..."
                            showSuggestions={true}
                        />
                    </div>

                    {selectedAsset && (
                        <div className="p-3 bg-dark-700 rounded-lg">
                            <div className="flex items-center space-x-3">
                                <div className="w-8 h-8 bg-primary-600/20 rounded-lg flex items-center justify-center">
                                    <Database size={16} className="text-primary-400" />
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

                            {priceData && (
                                <div className="mt-3 pt-3 border-t border-dark-600">
                                    <div className="space-y-2">
                                        <div className="flex items-center space-x-2">
                                            <TrendingUp size={16} className="text-green-400" />
                                            <span className="text-sm text-gray-300">
                                                Current Price: <span className="text-green-400 font-medium">${priceData.price}</span>
                                            </span>
                                            <span className="text-xs text-gray-500">
                                                ({priceData.currency})
                                            </span>
                                        </div>
                                        <div className="grid grid-cols-2 gap-2 text-xs text-gray-400">
                                            {priceData.market_cap && (
                                                <div>Market Cap: ${(priceData.market_cap / 1000000000).toFixed(2)}B</div>
                                            )}
                                            {priceData.pe_ratio && (
                                                <div>P/E Ratio: {priceData.pe_ratio}</div>
                                            )}
                                            {priceData.dividend_yield && (
                                                <div>Dividend Yield: {priceData.dividend_yield}</div>
                                            )}
                                            {priceData.beta && (
                                                <div>Beta: {priceData.beta}</div>
                                            )}
                                        </div>
                                        <div className="text-xs text-gray-500">
                                            Last Updated: {new Date(priceData.date).toLocaleString()}
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>

            {/* Test Results */}
            <div className="space-y-4">
                {Object.entries(testResults).map(([testName, result]) => (
                    <div key={testName} className="flex items-start space-x-3 p-4 bg-dark-800 rounded-lg">
                        <div className="flex-shrink-0 mt-0.5">
                            {getStatusIcon(result.status)}
                        </div>
                        <div className="flex-1 min-w-0">
                            <div className="flex items-center space-x-2 mb-2">
                                <h4 className={`font-medium ${getStatusColor(result.status)}`}>
                                    {testName}
                                </h4>
                                <span className={`text-xs px-2 py-1 rounded ${result.status === 'success' ? 'bg-green-600/20 text-green-400' : result.status === 'error' ? 'bg-red-600/20 text-red-400' : 'bg-yellow-600/20 text-yellow-400'}`}>
                                    {result.status}
                                </span>
                            </div>

                            {result.error && (
                                <div className="text-sm text-red-400 mb-2">
                                    Error: {result.error}
                                </div>
                            )}

                            {result.result && (
                                <div className="text-sm text-gray-300">
                                    <details className="cursor-pointer">
                                        <summary className="hover:text-gray-100">
                                            View Result Details
                                        </summary>
                                        <pre className="mt-2 p-3 bg-dark-900 rounded text-xs overflow-x-auto">
                                            {JSON.stringify(result.result, null, 2)}
                                        </pre>
                                    </details>
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {Object.keys(testResults).length === 0 && (
                    <div className="text-center py-8 text-gray-400">
                        <AlertCircle size={32} className="mx-auto mb-3 text-gray-600" />
                        <p>No tests have been run yet. Click "Run Tests" to start.</p>
                    </div>
                )}
            </div>

            <div className="mt-6 p-4 bg-blue-600/10 border border-blue-500/30 rounded-lg">
                <h4 className="text-blue-400 font-medium mb-2">Client-Side Search Features</h4>
                <ul className="text-sm text-gray-300 space-y-1">
                    <li>• Fetches all assets on component mount</li>
                    <li>• Filters assets locally by symbol and name</li>
                    <li>• Shows real-time search results as you type</li>
                    <li>• Fetches current price when asset is selected</li>
                    <li>• No server requests for search (faster performance)</li>
                    <li>• Keyboard navigation support</li>
                </ul>
            </div>
        </div>
    );
};

export default ClientSideSearchTest;
