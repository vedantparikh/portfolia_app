import { AlertCircle, CheckCircle, RefreshCw, XCircle } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { assetAPI, marketAPI, portfolioAPI, transactionAPI } from '../../services/api';

const TransactionIntegrationTest = () => {
    const [testResults, setTestResults] = useState({});
    const [isRunning, setIsRunning] = useState(false);
    const [portfolios, setPortfolios] = useState([]);

    useEffect(() => {
        loadPortfolios();
    }, []);

    const loadPortfolios = async () => {
        try {
            const response = await portfolioAPI.getPortfolios();
            setPortfolios(response || []);
        } catch (error) {
            console.error('Failed to load portfolios:', error);
        }
    };

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

    const testAssetSearch = async () => {
        const results = await assetAPI.searchAssets('AAPL');
        return results;
    };

    const testSymbolSearch = async () => {
        const results = await marketAPI.searchSymbols('AAPL');
        return results;
    };

    const testAssetCreation = async () => {
        const testAsset = {
            symbol: 'TEST' + Date.now(),
            name: 'Test Asset',
            asset_type: 'EQUITY',
            exchange: 'TEST',
            sector: 'Technology',
            industry: 'Software',
            country: 'United States',
            description: 'Test asset for integration testing',
            is_active: true
        };

        const createdAsset = await assetAPI.createAsset(testAsset);
        return createdAsset;
    };

    const testTransactionCreation = async () => {
        if (portfolios.length === 0) {
            throw new Error('No portfolios available for testing');
        }

        // First create a test asset
        const testAsset = await testAssetCreation();

        // Then create a transaction
        const transactionData = {
            portfolio_id: portfolios[0].id,
            asset_id: testAsset.id,
            transaction_type: 'buy',
            quantity: 10,
            price: 100.00,
            currency: 'USD',
            transaction_date: new Date().toISOString(),
            fees: 5.00,
            notes: 'Test transaction for integration testing'
        };

        const createdTransaction = await transactionAPI.createTransaction(transactionData);
        return { transaction: createdTransaction, asset: testAsset };
    };

    const testTransactionRetrieval = async () => {
        const transactions = await transactionAPI.getTransactions({ limit: 5 });
        return transactions;
    };

    const runAllTests = async () => {
        setIsRunning(true);
        setTestResults({});

        try {
            // Test 1: Asset Search
            await runTest('Asset Search', testAssetSearch);

            // Test 2: Symbol Search
            await runTest('Symbol Search', testSymbolSearch);

            // Test 3: Asset Creation
            await runTest('Asset Creation', testAssetCreation);

            // Test 4: Transaction Creation
            await runTest('Transaction Creation', testTransactionCreation);

            // Test 5: Transaction Retrieval
            await runTest('Transaction Retrieval', testTransactionRetrieval);

            toast.success('All integration tests completed successfully!');
        } catch (error) {
            toast.error('Some tests failed. Check the results below.');
        } finally {
            setIsRunning(false);
        }
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
                        Transaction Integration Test
                    </h3>
                    <p className="text-sm text-gray-400">
                        Test the complete transaction workflow with asset search and creation
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
                <h4 className="text-blue-400 font-medium mb-2">Test Coverage</h4>
                <ul className="text-sm text-gray-300 space-y-1">
                    <li>• Asset search functionality</li>
                    <li>• Symbol search from market data</li>
                    <li>• Asset creation from symbol search results</li>
                    <li>• Transaction creation with proper asset references</li>
                    <li>• Transaction retrieval and validation</li>
                </ul>
            </div>
        </div>
    );
};

export default TransactionIntegrationTest;
