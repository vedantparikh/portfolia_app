import React, { useState } from 'react';
import toast from 'react-hot-toast';
import { portfolioAPI } from '../../services/api';

const PortfolioTest = () => {
    const [testResults, setTestResults] = useState({});
    const [loading, setLoading] = useState(false);

    const testPortfolioAPI = async () => {
        setLoading(true);
        const results = {};

        try {
            // Test 1: Get portfolios
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
            // Test 2: Create a test portfolio
            console.log('Testing createPortfolio...');
            const testPortfolio = {
                name: 'Test Portfolio ' + Date.now(),
                description: 'Test portfolio for debugging',
                initial_cash: 1000,
                risk_tolerance: 'moderate'
            };
            const createResponse = await portfolioAPI.createPortfolio(testPortfolio);
            results.createPortfolio = {
                success: true,
                data: createResponse,
                message: 'Successfully created test portfolio'
            };
            console.log('Create response:', createResponse);

            // Test 3: Get portfolio summary if we have a portfolio ID
            if (createResponse.id || createResponse.portfolio?.id) {
                const portfolioId = createResponse.id || createResponse.portfolio.id;
                try {
                    console.log('Testing getPortfolioSummary...');
                    const summaryResponse = await portfolioAPI.getPortfolioSummary(portfolioId);
                    results.getPortfolioSummary = {
                        success: true,
                        data: summaryResponse,
                        message: 'Successfully fetched portfolio summary'
                    };
                    console.log('Summary response:', summaryResponse);
                } catch (summaryError) {
                    results.getPortfolioSummary = {
                        success: false,
                        error: summaryError.message,
                        response: summaryError.response?.data,
                        status: summaryError.response?.status,
                        message: 'Failed to fetch portfolio summary'
                    };
                    console.error('Summary error:', summaryError);
                }
            }
        } catch (error) {
            results.createPortfolio = {
                success: false,
                error: error.message,
                response: error.response?.data,
                status: error.response?.status,
                message: 'Failed to create test portfolio'
            };
            console.error('Create error:', error);
        }

        setTestResults(results);
        setLoading(false);
        toast.success('API tests completed. Check console for details.');
    };

    return (
        <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-100 mb-4">Portfolio API Test</h3>
            <button
                onClick={testPortfolioAPI}
                disabled={loading}
                className="btn-primary mb-4"
            >
                {loading ? 'Testing...' : 'Test Portfolio API'}
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

export default PortfolioTest;
