import React, { useState } from 'react';
import toast from 'react-hot-toast';
import { marketAPI } from '../../services/api';

const AssetsTest = () => {
    const [testResults, setTestResults] = useState({});
    const [loading, setLoading] = useState(false);

    const testAssetsAPI = async () => {
        setLoading(true);
        const results = {};

        try {
            // Test 1: Get assets
            console.log('Testing getAssets...');
            const assetsResponse = await marketAPI.getAssets({
                limit: 10,
                include_prices: true
            });
            results.getAssets = {
                success: true,
                data: assetsResponse,
                message: 'Successfully fetched assets'
            };
            console.log('Assets response:', assetsResponse);
        } catch (error) {
            results.getAssets = {
                success: false,
                error: error.message,
                response: error.response?.data,
                status: error.response?.status,
                message: 'Failed to fetch assets'
            };
            console.error('Assets error:', error);
        }

        try {
            // Test 2: Search assets
            console.log('Testing searchAssets...');
            const searchResponse = await marketAPI.searchAssets('AAPL');
            results.searchAssets = {
                success: true,
                data: searchResponse,
                message: 'Successfully searched assets'
            };
            console.log('Search response:', searchResponse);
        } catch (error) {
            results.searchAssets = {
                success: false,
                error: error.message,
                response: error.response?.data,
                status: error.response?.status,
                message: 'Failed to search assets'
            };
            console.error('Search error:', error);
        }

        try {
            // Test 3: Search stock symbols
            console.log('Testing searchSymbols...');
            const symbolsResponse = await marketAPI.searchSymbols('Apple');
            results.searchSymbols = {
                success: true,
                data: symbolsResponse,
                message: 'Successfully searched symbols'
            };
            console.log('Symbols response:', symbolsResponse);
        } catch (error) {
            results.searchSymbols = {
                success: false,
                error: error.message,
                response: error.response?.data,
                status: error.response?.status,
                message: 'Failed to search symbols'
            };
            console.error('Symbols error:', error);
        }

        // Test 4: Get asset prices (if we have an asset)
        if (results.getAssets?.success && results.getAssets.data?.assets?.length > 0) {
            const firstAsset = results.getAssets.data.assets[0];
            try {
                console.log('Testing getAssetPrices...');
                const pricesResponse = await marketAPI.getAssetPrices(firstAsset.id, {
                    days: 7
                });
                results.getAssetPrices = {
                    success: true,
                    data: pricesResponse,
                    message: 'Successfully fetched asset prices'
                };
                console.log('Prices response:', pricesResponse);
            } catch (error) {
                results.getAssetPrices = {
                    success: false,
                    error: error.message,
                    response: error.response?.data,
                    status: error.response?.status,
                    message: 'Failed to fetch asset prices'
                };
                console.error('Prices error:', error);
            }
        }

        setTestResults(results);
        setLoading(false);
        toast.success('Assets API tests completed. Check console for details.');
    };

    return (
        <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-100 mb-4">Assets API Test</h3>
            <button
                onClick={testAssetsAPI}
                disabled={loading}
                className="btn-primary mb-4"
            >
                {loading ? 'Testing...' : 'Test Assets API'}
            </button>

            {Object.keys(testResults).length > 0 && (
                <div className="space-y-4">
                    {Object.entries(testResults).map(([test, result]) => (
                        <div key={test} className="p-4 bg-dark-800 rounded-lg">
                            <h4 className="font-medium text-gray-100 mb-2">{test}</h4>
                            <div className={`text-sm ${result.success ? 'text-success-400' : 'text-danger-400'}`}>
                                {result.message}
                            </div>
                            {result.error && (
                                <div className="text-xs text-gray-400 mt-1">
                                    Error: {result.error}
                                </div>
                            )}
                            {result.status && (
                                <div className="text-xs text-gray-400">
                                    Status: {result.status}
                                </div>
                            )}
                            {result.response && (
                                <div className="text-xs text-gray-400 mt-1">
                                    Response: {JSON.stringify(result.response, null, 2)}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default AssetsTest;
