import React, { useState } from 'react';
import toast from 'react-hot-toast';
import { authAPI, marketAPI, portfolioAPI, transactionAPI } from '../services/api';

const ComprehensiveTest = () => {
    const [testResults, setTestResults] = useState({});
    const [loading, setLoading] = useState(false);
    const [currentTest, setCurrentTest] = useState('');

    const runAllTests = async () => {
        setLoading(true);
        const results = {};

        // Test 1: Authentication
        setCurrentTest('Testing Authentication...');
        try {
            console.log('Testing authentication...');
            const authResponse = await authAPI.getCurrentUser();
            results.authentication = {
                success: true,
                data: authResponse,
                message: 'Authentication successful'
            };
            console.log('Auth response:', authResponse);
        } catch (error) {
            results.authentication = {
                success: false,
                error: error.message,
                response: error.response?.data,
                status: error.response?.status,
                message: 'Authentication failed - Please login first'
            };
            console.error('Auth error:', error);
        }

        // Test 2: Portfolio API
        setCurrentTest('Testing Portfolio API...');
        try {
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

        // Test 3: Create Portfolio
        setCurrentTest('Testing Portfolio Creation...');
        try {
            console.log('Testing createPortfolio...');
            const testPortfolio = {
                name: 'Test Portfolio ' + Date.now(),
                description: 'Test portfolio for comprehensive testing',
                initial_cash: 1000,
                risk_tolerance: 'moderate'
            };
            const createResponse = await portfolioAPI.createPortfolio(testPortfolio);
            results.createPortfolio = {
                success: true,
                data: createResponse,
                message: 'Successfully created test portfolio'
            };
            console.log('Create portfolio response:', createResponse);
        } catch (error) {
            results.createPortfolio = {
                success: false,
                error: error.message,
                response: error.response?.data,
                status: error.response?.status,
                message: 'Failed to create portfolio'
            };
            console.error('Create portfolio error:', error);
        }

        // Test 4: Assets API
        setCurrentTest('Testing Assets API...');
        try {
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

        // Test 5: Search Assets
        setCurrentTest('Testing Asset Search...');
        try {
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

        // Test 6: Transactions API
        setCurrentTest('Testing Transactions API...');
        try {
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

        // Test 7: Create Transaction (if we have portfolios)
        if (results.getPortfolios?.success && results.getPortfolios.data?.portfolios?.length > 0) {
            setCurrentTest('Testing Transaction Creation...');
            const firstPortfolio = results.getPortfolios.data.portfolios[0];
            try {
                console.log('Testing createBuyTransaction...');
                const testTransaction = {
                    portfolio_id: firstPortfolio.id,
                    symbol: 'AAPL',
                    quantity: 1,
                    price: 150.00,
                    transaction_date: new Date().toISOString()
                };
                const createTransactionResponse = await transactionAPI.createBuyTransaction(testTransaction);
                results.createTransaction = {
                    success: true,
                    data: createTransactionResponse,
                    message: 'Successfully created test transaction'
                };
                console.log('Create transaction response:', createTransactionResponse);
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

        // Test 8: Portfolio Summary (if we have portfolios)
        if (results.getPortfolios?.success && results.getPortfolios.data?.portfolios?.length > 0) {
            setCurrentTest('Testing Portfolio Summary...');
            const firstPortfolio = results.getPortfolios.data.portfolios[0];
            try {
                console.log('Testing getPortfolioSummary...');
                const summaryResponse = await portfolioAPI.getPortfolioSummary(firstPortfolio.id);
                results.getPortfolioSummary = {
                    success: true,
                    data: summaryResponse,
                    message: 'Successfully fetched portfolio summary'
                };
                console.log('Portfolio summary response:', summaryResponse);
            } catch (error) {
                results.getPortfolioSummary = {
                    success: false,
                    error: error.message,
                    response: error.response?.data,
                    status: error.response?.status,
                    message: 'Failed to fetch portfolio summary'
                };
                console.error('Portfolio summary error:', error);
            }
        }

        setTestResults(results);
        setLoading(false);
        setCurrentTest('');
        toast.success('Comprehensive tests completed. Check console for details.');
    };

    const getSuccessCount = () => {
        return Object.values(testResults).filter(result => result.success).length;
    };

    const getTotalCount = () => {
        return Object.keys(testResults).length;
    };

    const getEndpointIssues = () => {
        return Object.entries(testResults)
            .filter(([_, result]) => !result.success)
            .map(([test, result]) => ({
                test,
                error: result.error,
                status: result.status,
                response: result.response
            }));
    };

    return (
        <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-100 mb-4">Comprehensive API Test</h3>

            <div className="mb-4">
                <button
                    onClick={runAllTests}
                    disabled={loading}
                    className="btn-primary mb-4"
                >
                    {loading ? 'Testing...' : 'Run All Tests'}
                </button>

                {loading && currentTest && (
                    <div className="text-sm text-gray-400 mb-4">
                        {currentTest}
                    </div>
                )}
            </div>

            {Object.keys(testResults).length > 0 && (
                <div className="space-y-4">
                    {/* Summary */}
                    <div className="p-4 bg-dark-800 rounded-lg">
                        <h4 className="font-medium text-gray-100 mb-2">Test Summary</h4>
                        <div className="text-sm">
                            <div className="flex items-center space-x-4">
                                <span className={`font-medium ${getSuccessCount() === getTotalCount() ? 'text-success-400' : 'text-warning-400'}`}>
                                    {getSuccessCount()}/{getTotalCount()} tests passed
                                </span>
                                <span className="text-gray-400">
                                    {getTotalCount() - getSuccessCount()} failed
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Endpoint Issues */}
                    {getEndpointIssues().length > 0 && (
                        <div className="p-4 bg-danger-900/20 border border-danger-700 rounded-lg">
                            <h4 className="font-medium text-danger-400 mb-2">Endpoint Issues Found</h4>
                            <div className="space-y-2">
                                {getEndpointIssues().map((issue, index) => (
                                    <div key={index} className="text-sm">
                                        <div className="font-medium text-gray-100">{issue.test}</div>
                                        <div className="text-danger-400">Error: {issue.error}</div>
                                        {issue.status && (
                                            <div className="text-gray-400">Status: {issue.status}</div>
                                        )}
                                        {issue.response && (
                                            <div className="text-gray-400">
                                                Response: {JSON.stringify(issue.response, null, 2)}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Individual Test Results */}
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

export default ComprehensiveTest;
