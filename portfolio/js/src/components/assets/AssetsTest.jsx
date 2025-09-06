import React, { useState } from 'react';
import toast from 'react-hot-toast';
import { userAssetsAPI } from '../../services/api';

const AssetsTest = () => {
    const [testResults, setTestResults] = useState([]);
    const [loading, setLoading] = useState(false);

    const runTests = async () => {
        setLoading(true);
        setTestResults([]);
        const results = [];

        try {
            // Test 1: Get user assets
            results.push({ test: 'Get User Assets', status: 'running' });
            setTestResults([...results]);

            const assets = await userAssetsAPI.getUserAssets();
            results[results.length - 1] = {
                test: 'Get User Assets',
                status: 'success',
                message: `Found ${assets.assets?.length || 0} assets`
            };
            setTestResults([...results]);

            // Test 2: Create a test asset
            results.push({ test: 'Create Test Asset', status: 'running' });
            setTestResults([...results]);

            const testAsset = {
                symbol: 'TEST',
                name: 'Test Asset',
                quantity: 10,
                purchase_price: 100.50,
                purchase_date: '2024-01-01',
                notes: 'Test asset for API testing',
                currency: 'USD',
                portfolio_id: 1
            };

            const createdAsset = await userAssetsAPI.createUserAsset(testAsset);
            results[results.length - 1] = {
                test: 'Create Test Asset',
                status: 'success',
                message: `Created asset with ID: ${createdAsset.id}`
            };
            setTestResults([...results]);

            // Test 3: Update the test asset
            results.push({ test: 'Update Test Asset', status: 'running' });
            setTestResults([...results]);

            const updatedAsset = await userAssetsAPI.updateUserAsset(createdAsset.id, {
                ...testAsset,
                quantity: 15,
                notes: 'Updated test asset'
            });
            results[results.length - 1] = {
                test: 'Update Test Asset',
                status: 'success',
                message: `Updated asset quantity to ${updatedAsset.quantity}`
            };
            setTestResults([...results]);

            // Test 4: Get specific asset
            results.push({ test: 'Get Specific Asset', status: 'running' });
            setTestResults([...results]);

            const specificAsset = await userAssetsAPI.getUserAsset(createdAsset.id);
            results[results.length - 1] = {
                test: 'Get Specific Asset',
                status: 'success',
                message: `Retrieved asset: ${specificAsset.symbol}`
            };
            setTestResults([...results]);

            // Test 5: Delete the test asset
            results.push({ test: 'Delete Test Asset', status: 'running' });
            setTestResults([...results]);

            await userAssetsAPI.deleteUserAsset(createdAsset.id);
            results[results.length - 1] = {
                test: 'Delete Test Asset',
                status: 'success',
                message: 'Asset deleted successfully'
            };
            setTestResults([...results]);

            // Test 6: Get asset summary
            results.push({ test: 'Get Asset Summary', status: 'running' });
            setTestResults([...results]);

            const summary = await userAssetsAPI.getUserAssetSummary();
            results[results.length - 1] = {
                test: 'Get Asset Summary',
                status: 'success',
                message: `Summary retrieved: ${Object.keys(summary).length} metrics`
            };
            setTestResults([...results]);

            toast.success('All tests passed!');

        } catch (error) {
            const lastTest = results[results.length - 1];
            if (lastTest) {
                lastTest.status = 'error';
                lastTest.message = error.response?.data?.detail || error.message;
            }
            setTestResults([...results]);
            toast.error('Test failed: ' + (error.response?.data?.detail || error.message));
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'success': return 'text-green-400';
            case 'error': return 'text-red-400';
            case 'running': return 'text-yellow-400';
            default: return 'text-gray-400';
        }
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'success': return '✓';
            case 'error': return '✗';
            case 'running': return '⏳';
            default: return '○';
        }
    };

    return (
        <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-100 mb-4">Assets API Test Suite</h3>
            <p className="text-sm text-gray-400 mb-4">
                Test all CRUD operations for user assets
            </p>

            <button
                onClick={runTests}
                disabled={loading}
                className="btn-primary mb-4"
            >
                {loading ? 'Running Tests...' : 'Run Tests'}
            </button>

            {testResults.length > 0 && (
                <div className="space-y-2">
                    <h4 className="text-md font-medium text-gray-200 mb-2">Test Results:</h4>
                    {testResults.map((result, index) => (
                        <div key={index} className="flex items-center space-x-3 p-2 rounded-lg bg-dark-800">
                            <span className={`text-sm ${getStatusColor(result.status)}`}>
                                {getStatusIcon(result.status)}
                            </span>
                            <span className="text-sm text-gray-300 flex-1">{result.test}</span>
                            {result.message && (
                                <span className="text-xs text-gray-400">{result.message}</span>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default AssetsTest;