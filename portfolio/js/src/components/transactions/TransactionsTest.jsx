import React, { useState } from 'react';
import toast from 'react-hot-toast';
import { marketAPI, portfolioAPI, transactionAPI } from '../../services/api';

const TransactionsTest = () => {
    const [testResults, setTestResults] = useState({});
    const [loading, setLoading] = useState(false);

    const testTransactionsAPI = async () => {
        setLoading(true);
        const results = {};

        try {
            // Test 1: Get portfolios first
            console.log('Testing getPortfolios...');
            const portfoliosResponse = await portfolioAPI.getPortfolios();
            results.getPortfolios = {
                success: true,
                data: portfoliosResponse,
                message: 'Successfully fetched portfolios'
            };
            console.log('Portfolios response:', portfoliosResponse);
        } catch (error) {
            results.getPortfolios = {
                success: false,
                error: error.message,
                response: error.response?.data,
                status: error.response?.status,
                message: 'Failed to fetch portfolios'
            };
            console.error('Portfolios error:', error);
        }

        try {
            // Test 2: Get transactions
            console.log('Testing getTransactions...');
            const transactionsResponse = await transactionAPI.getTransactions({
                limit: 10,
                order_by: 'created_at',
                order: 'desc'
            });
            results.getTransactions = {
                success: true,
                data: transactionsResponse,
                message: 'Successfully fetched transactions'
            };
            console.log('Transactions response:', transactionsResponse);
        } catch (error) {
            results.getTransactions = {
                success: false,
                error: error.message,
                response: error.response?.data,
                status: error.response?.status,
                message: 'Failed to fetch transactions'
            };
            console.error('Transactions error:', error);
        }

        // Test 3: Get portfolio transactions (if we have portfolios)
        if (results.getPortfolios?.success && results.getPortfolios.data?.portfolios?.length > 0) {
            const firstPortfolio = results.getPortfolios.data.portfolios[0];
            try {
                console.log('Testing getPortfolioTransactions...');
                const portfolioTransactionsResponse = await transactionAPI.getPortfolioTransactions(firstPortfolio.id, {
                    limit: 10,
                    order_by: 'created_at',
                    order: 'desc'
                });
                results.getPortfolioTransactions = {
                    success: true,
                    data: portfolioTransactionsResponse,
                    message: 'Successfully fetched portfolio transactions'
                };
                console.log('Portfolio transactions response:', portfolioTransactionsResponse);
            } catch (error) {
                results.getPortfolioTransactions = {
                    success: false,
                    error: error.message,
                    response: error.response?.data,
                    status: error.response?.status,
                    message: 'Failed to fetch portfolio transactions'
                };
                console.error('Portfolio transactions error:', error);
            }
        }

        // Test 4: Get current price for a symbol
        try {
            console.log('Testing getCurrentPrice...');
            const priceResponse = await marketAPI.getCurrentPrice('AAPL');
            results.getCurrentPrice = {
                success: true,
                data: priceResponse,
                message: 'Successfully fetched current price for AAPL'
            };
            console.log('Current price response:', priceResponse);
        } catch (error) {
            results.getCurrentPrice = {
                success: false,
                error: error.message,
                response: error.response?.data,
                status: error.response?.status,
                message: 'Failed to fetch current price'
            };
            console.error('Current price error:', error);
        }

        // Test 5: Create a test transaction (if we have portfolios)
        if (results.getPortfolios?.success && results.getPortfolios.data?.portfolios?.length > 0) {
            const firstPortfolio = results.getPortfolios.data.portfolios[0];
            try {
                console.log('Testing createTransaction...');
                const testTransaction = {
                    portfolio_id: firstPortfolio.id,
                    transaction_type: 'buy',
                    asset_id: 'AAPL',
                    currency: 'USD',
                    quantity: 1,
                    price: 150.00,
                    fees: 0,
                    notes: 'Test transaction',
                    transaction_date: new Date().toISOString()
                };
                const createResponse = await transactionAPI.createTransaction(testTransaction);
                results.createTransaction = {
                    success: true,
                    data: createResponse,
                    message: 'Successfully created transaction'
                };
                console.log('Create transaction response:', createResponse);
            } catch (error) {
                results.createTransaction = {
                    success: false,
                    error: error.message,
                    response: error.response?.data,
                    status: error.response?.status,
                    message: 'Failed to create transaction'
                };
                console.error('Create transaction error:', error);
            }
        }

        // Test 6: Get transaction history
        try {
            console.log('Testing getTransactionHistory...');
            const historyResponse = await transactionAPI.getTransactionHistory({
                limit: 10,
                order_by: 'created_at',
                order: 'desc'
            });
            results.getTransactionHistory = {
                success: true,
                data: historyResponse,
                message: 'Successfully fetched transaction history'
            };
            console.log('Transaction history response:', historyResponse);
        } catch (error) {
            results.getTransactionHistory = {
                success: false,
                error: error.message,
                response: error.response?.data,
                status: error.response?.status,
                message: 'Failed to fetch transaction history'
            };
            console.error('Transaction history error:', error);
        }

        setTestResults(results);
        setLoading(false);
        toast.success('Transactions API tests completed. Check console for details.');
    };

    return (
        <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-100 mb-4">Transactions API Test</h3>
            <button
                onClick={testTransactionsAPI}
                disabled={loading}
                className="btn-primary mb-4"
            >
                {loading ? 'Testing...' : 'Test Transactions API'}
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

export default TransactionsTest;
