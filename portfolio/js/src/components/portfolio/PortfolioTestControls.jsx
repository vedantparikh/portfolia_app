import React, { useState } from 'react';
import toast from 'react-hot-toast';
import { portfolioAPI } from '../../services/api';

const PortfolioTestControls = ({ onPortfolioUpdate }) => {
    const [testing, setTesting] = useState(false);
    const [testResults, setTestResults] = useState(null);

    const runPortfolioTests = async () => {
        setTesting(true);
        const results = {
            getPortfolios: { status: 'pending' },
            createPortfolio: { status: 'pending' },
            updatePortfolio: { status: 'pending' },
            deletePortfolio: { status: 'pending' }
        };

        try {
            // Test 1: Get Portfolios
            console.log('[Portfolio Test] Testing getPortfolios...');
            try {
                const portfoliosResponse = await portfolioAPI.getPortfolios();
                results.getPortfolios = {
                    status: 'success',
                    data: portfoliosResponse,
                    message: `Found ${Array.isArray(portfoliosResponse) ? portfoliosResponse.length : 'unknown'} portfolios`
                };
                toast.success('✅ Get portfolios test passed');
            } catch (error) {
                results.getPortfolios = {
                    status: 'error',
                    error: error.message,
                    message: 'Failed to fetch portfolios'
                };
                toast.error('❌ Get portfolios test failed');
            }

            // Test 2: Create Portfolio
            console.log('[Portfolio Test] Testing createPortfolio...');
            let createdPortfolioId = null;
            try {
                const testPortfolio = {
                    name: `Test Portfolio ${Date.now()}`,
                    description: 'Test portfolio created by automated test',
                    initial_cash: 10000,
                    risk_tolerance: 'moderate',
                    is_public: false
                };

                const createResponse = await portfolioAPI.createPortfolio(testPortfolio);
                createdPortfolioId = createResponse?.id || createResponse?.portfolio?.id;

                results.createPortfolio = {
                    status: 'success',
                    data: createResponse,
                    message: `Created portfolio with ID: ${createdPortfolioId}`
                };
                toast.success('✅ Create portfolio test passed');

                if (onPortfolioUpdate) {
                    onPortfolioUpdate();
                }

                // Test 3: Update Portfolio (only if create was successful)
                if (createdPortfolioId) {
                    console.log('[Portfolio Test] Testing updatePortfolio...');
                    try {
                        const updateData = {
                            name: `Updated Test Portfolio ${Date.now()}`,
                            description: 'Updated test portfolio',
                            target_return: 12.5
                        };

                        const updateResponse = await portfolioAPI.updatePortfolio(createdPortfolioId, updateData);
                        results.updatePortfolio = {
                            status: 'success',
                            data: updateResponse,
                            message: 'Successfully updated portfolio'
                        };
                        toast.success('✅ Update portfolio test passed');

                        if (onPortfolioUpdate) {
                            onPortfolioUpdate();
                        }
                    } catch (error) {
                        results.updatePortfolio = {
                            status: 'error',
                            error: error.message,
                            message: 'Failed to update portfolio'
                        };
                        toast.error('❌ Update portfolio test failed');
                    }

                    // Test 4: Delete Portfolio (only if create was successful)
                    console.log('[Portfolio Test] Testing deletePortfolio...');
                    try {
                        await portfolioAPI.deletePortfolio(createdPortfolioId);
                        results.deletePortfolio = {
                            status: 'success',
                            message: 'Successfully deleted test portfolio'
                        };
                        toast.success('✅ Delete portfolio test passed');

                        if (onPortfolioUpdate) {
                            onPortfolioUpdate();
                        }
                    } catch (error) {
                        results.deletePortfolio = {
                            status: 'error',
                            error: error.message,
                            message: 'Failed to delete portfolio'
                        };
                        toast.error('❌ Delete portfolio test failed');
                    }
                }
            } catch (error) {
                results.createPortfolio = {
                    status: 'error',
                    error: error.message,
                    message: 'Failed to create portfolio'
                };
                toast.error('❌ Create portfolio test failed');

                // Skip update and delete tests if create failed
                results.updatePortfolio = {
                    status: 'skipped',
                    message: 'Skipped due to create failure'
                };
                results.deletePortfolio = {
                    status: 'skipped',
                    message: 'Skipped due to create failure'
                };
            }

        } catch (error) {
            console.error('[Portfolio Test] Test suite error:', error);
            toast.error('Portfolio test suite encountered an error');
        } finally {
            setTestResults(results);
            setTesting(false);
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'success': return 'text-success-400';
            case 'error': return 'text-danger-400';
            case 'skipped': return 'text-warning-400';
            default: return 'text-gray-400';
        }
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'success': return '✅';
            case 'error': return '❌';
            case 'skipped': return '⏭️';
            case 'pending': return '⏳';
            default: return '⭕';
        }
    };

    return (
        <div className="card p-6 border-l-4 border-l-primary-400">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-100">Portfolio CRUD Test Suite</h3>
                <button
                    onClick={runPortfolioTests}
                    disabled={testing}
                    className="btn-primary flex items-center space-x-2"
                >
                    {testing ? (
                        <>
                            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                            <span>Testing...</span>
                        </>
                    ) : (
                        <span>Run Tests</span>
                    )}
                </button>
            </div>

            <p className="text-gray-400 text-sm mb-4">
                This will test Create, Read, Update, and Delete operations for portfolios.
            </p>

            {testResults && (
                <div className="space-y-3">
                    <h4 className="font-medium text-gray-200">Test Results:</h4>
                    {Object.entries(testResults).map(([test, result]) => (
                        <div key={test} className="flex items-center justify-between p-3 bg-dark-800 rounded-lg">
                            <div className="flex items-center space-x-3">
                                <span className="text-lg">{getStatusIcon(result.status)}</span>
                                <div>
                                    <div className="font-medium text-gray-100">
                                        {test.replace(/([A-Z])/g, ' $1').toLowerCase()}
                                    </div>
                                    <div className={`text-xs ${getStatusColor(result.status)}`}>
                                        {result.message}
                                    </div>
                                </div>
                            </div>
                            <div className={`text-sm font-medium ${getStatusColor(result.status)}`}>
                                {result.status.toUpperCase()}
                            </div>
                        </div>
                    ))}
                </div>
            )}

            <div className="mt-4 p-3 bg-dark-800 rounded-lg">
                <div className="text-xs text-gray-500">
                    <strong>Note:</strong> These tests use the actual API endpoints.
                    A test portfolio will be created and deleted during the process.
                    Make sure your backend server is running on http://localhost:8000
                </div>
            </div>
        </div>
    );
};

export default PortfolioTestControls;
