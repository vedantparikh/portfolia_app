import {
    Activity,
    ArrowLeft,
    BarChart3,
    DollarSign,
    PieChart,
    Plus,
    RefreshCw,
    TrendingDown,
    TrendingUp,
    Wallet
} from 'lucide-react';
import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { portfolioAPI, transactionAPI } from '../../services/api';
import CreatePortfolioModal from './CreatePortfolioModal';
import PortfolioCard from './PortfolioCard';
import PortfolioChart from './PortfolioChart';
import PortfolioDetail from './PortfolioDetail';

const Portfolio = () => {
    const [portfolios, setPortfolios] = useState([]);
    const [selectedPortfolio, setSelectedPortfolio] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [viewMode, setViewMode] = useState('overview'); // overview, detail, chart
    const [portfolioStats, setPortfolioStats] = useState(null);
    const [transactions, setTransactions] = useState([]);

    // Load portfolios on component mount
    useEffect(() => {
        loadPortfolios();
    }, []);

    // Load portfolio details when selected
    useEffect(() => {
        if (selectedPortfolio) {
            loadPortfolioDetails(selectedPortfolio.id);
        }
    }, [selectedPortfolio]);

    const loadPortfolios = async () => {
        try {
            setLoading(true);
            const response = await portfolioAPI.getPortfolios();
            setPortfolios(response.portfolios || []);

            // Select first portfolio by default
            if (response.portfolios && response.portfolios.length > 0) {
                setSelectedPortfolio(response.portfolios[0]);
            }
        } catch (error) {
            console.error('Failed to load portfolios:', error);
            toast.error('Failed to load portfolios');
        } finally {
            setLoading(false);
        }
    };

    const loadPortfolioDetails = async (portfolioId) => {
        try {
            // Load portfolio summary
            const summaryResponse = await portfolioAPI.getPortfolioSummary(portfolioId);
            setPortfolioStats(summaryResponse);

            // Load recent transactions
            const transactionsResponse = await transactionAPI.getPortfolioTransactions(portfolioId, {
                limit: 10,
                order_by: 'created_at',
                order: 'desc'
            });
            setTransactions(transactionsResponse.transactions || []);
        } catch (error) {
            console.error('Failed to load portfolio details:', error);
            toast.error('Failed to load portfolio details');
        }
    };

    const handleCreatePortfolio = async (portfolioData) => {
        try {
            const response = await portfolioAPI.createPortfolio(portfolioData);
            setPortfolios(prev => [...prev, response]);
            setSelectedPortfolio(response);
            setShowCreateModal(false);
            toast.success('Portfolio created successfully');
        } catch (error) {
            console.error('Failed to create portfolio:', error);
            toast.error('Failed to create portfolio');
        }
    };

    const handleDeletePortfolio = async (portfolioId) => {
        try {
            await portfolioAPI.deletePortfolio(portfolioId);
            setPortfolios(prev => prev.filter(p => p.id !== portfolioId));

            // If deleted portfolio was selected, select another one
            if (selectedPortfolio && selectedPortfolio.id === portfolioId) {
                const remainingPortfolios = portfolios.filter(p => p.id !== portfolioId);
                setSelectedPortfolio(remainingPortfolios.length > 0 ? remainingPortfolios[0] : null);
            }

            toast.success('Portfolio deleted successfully');
        } catch (error) {
            console.error('Failed to delete portfolio:', error);
            toast.error('Failed to delete portfolio');
        }
    };

    const handleRefresh = () => {
        loadPortfolios();
        if (selectedPortfolio) {
            loadPortfolioDetails(selectedPortfolio.id);
        }
        toast.success('Portfolio data refreshed');
    };

    const getTotalStats = () => {
        if (!portfolioStats) return null;

        const totalValue = portfolioStats.total_value || 0;
        const totalCost = portfolioStats.total_cost || 0;
        const totalGainLoss = totalValue - totalCost;
        const totalGainLossPercent = totalCost > 0 ? (totalGainLoss / totalCost) * 100 : 0;
        const dayChange = portfolioStats.day_change || 0;
        const dayChangePercent = totalValue > 0 ? (dayChange / totalValue) * 100 : 0;

        return {
            totalValue,
            totalCost,
            totalGainLoss,
            totalGainLossPercent,
            dayChange,
            dayChangePercent,
            totalHoldings: portfolioStats.total_holdings || 0,
            totalTransactions: portfolioStats.total_transactions || 0
        };
    };

    const stats = getTotalStats();

    if (loading) {
        return (
            <div className="min-h-screen gradient-bg flex items-center justify-center">
                <div className="text-center">
                    <RefreshCw className="w-8 h-8 text-primary-400 animate-spin mx-auto mb-4" />
                    <p className="text-gray-400">Loading portfolios...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen gradient-bg">
            <div className="max-w-7xl mx-auto p-6">
                {/* Header */}
                <div className="mb-8">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-4">
                            <a
                                href="/dashboard"
                                className="flex items-center space-x-2 text-gray-400 hover:text-gray-300 transition-colors"
                            >
                                <ArrowLeft size={20} />
                                <span>Back to Dashboard</span>
                            </a>
                        </div>
                        <div className="flex items-center space-x-3">
                            <button
                                onClick={handleRefresh}
                                className="btn-secondary flex items-center space-x-2"
                            >
                                <RefreshCw size={16} />
                                <span>Refresh</span>
                            </button>
                            <button
                                onClick={() => setShowCreateModal(true)}
                                className="btn-primary flex items-center space-x-2"
                            >
                                <Plus size={16} />
                                <span>New Portfolio</span>
                            </button>
                        </div>
                    </div>

                    <div className="mb-4">
                        <h1 className="text-3xl font-bold text-gray-100 mb-2">Portfolio</h1>
                        <p className="text-gray-400">Manage your investment portfolios</p>
                    </div>

                    {/* Portfolio Selector */}
                    {portfolios.length > 0 && (
                        <div className="flex items-center space-x-4 mb-6">
                            <label className="text-sm font-medium text-gray-300">Active Portfolio:</label>
                            <select
                                value={selectedPortfolio?.id || ''}
                                onChange={(e) => {
                                    const portfolio = portfolios.find(p => p.id === parseInt(e.target.value));
                                    setSelectedPortfolio(portfolio);
                                }}
                                className="input-field"
                            >
                                {portfolios.map((portfolio) => (
                                    <option key={portfolio.id} value={portfolio.id}>
                                        {portfolio.name}
                                    </option>
                                ))}
                            </select>
                        </div>
                    )}
                </div>

                {portfolios.length === 0 ? (
                    /* Empty State */
                    <div className="card p-12 text-center">
                        <Wallet className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                        <h3 className="text-xl font-semibold text-gray-300 mb-2">No portfolios yet</h3>
                        <p className="text-gray-500 mb-6">
                            Create your first portfolio to start tracking your investments
                        </p>
                        <button
                            onClick={() => setShowCreateModal(true)}
                            className="btn-primary flex items-center space-x-2 mx-auto"
                        >
                            <Plus size={16} />
                            <span>Create Portfolio</span>
                        </button>
                    </div>
                ) : (
                    <>
                        {/* Portfolio Stats */}
                        {stats && (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                                <div className="card p-6">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="text-sm text-gray-400">Total Value</p>
                                            <p className="text-2xl font-bold text-gray-100">
                                                ${stats.totalValue.toLocaleString()}
                                            </p>
                                        </div>
                                        <div className="w-12 h-12 bg-primary-600/20 rounded-lg flex items-center justify-center">
                                            <DollarSign size={24} className="text-primary-400" />
                                        </div>
                                    </div>
                                    <div className="mt-4 flex items-center text-sm">
                                        <span className={stats.totalGainLoss >= 0 ? 'text-success-400' : 'text-danger-400'}>
                                            {stats.totalGainLoss >= 0 ? '+' : ''}${stats.totalGainLoss.toLocaleString()}
                                        </span>
                                        <span className="text-gray-400 ml-2">
                                            ({stats.totalGainLossPercent.toFixed(2)}%)
                                        </span>
                                    </div>
                                </div>

                                <div className="card p-6">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="text-sm text-gray-400">Day Change</p>
                                            <p className={`text-2xl font-bold ${stats.dayChange >= 0 ? 'text-success-400' : 'text-danger-400'}`}>
                                                {stats.dayChange >= 0 ? '+' : ''}${stats.dayChange.toLocaleString()}
                                            </p>
                                        </div>
                                        <div className="w-12 h-12 bg-success-600/20 rounded-lg flex items-center justify-center">
                                            {stats.dayChange >= 0 ? (
                                                <TrendingUp size={24} className="text-success-400" />
                                            ) : (
                                                <TrendingDown size={24} className="text-danger-400" />
                                            )}
                                        </div>
                                    </div>
                                    <div className="mt-4 flex items-center text-sm">
                                        <span className={stats.dayChangePercent >= 0 ? 'text-success-400' : 'text-danger-400'}>
                                            {stats.dayChangePercent >= 0 ? '+' : ''}{stats.dayChangePercent.toFixed(2)}%
                                        </span>
                                        <span className="text-gray-400 ml-2">today</span>
                                    </div>
                                </div>

                                <div className="card p-6">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="text-sm text-gray-400">Holdings</p>
                                            <p className="text-2xl font-bold text-gray-100">{stats.totalHoldings}</p>
                                        </div>
                                        <div className="w-12 h-12 bg-warning-600/20 rounded-lg flex items-center justify-center">
                                            <BarChart3 size={24} className="text-warning-400" />
                                        </div>
                                    </div>
                                    <div className="mt-4 flex items-center text-sm">
                                        <span className="text-gray-400">Active positions</span>
                                    </div>
                                </div>

                                <div className="card p-6">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="text-sm text-gray-400">Transactions</p>
                                            <p className="text-2xl font-bold text-gray-100">{stats.totalTransactions}</p>
                                        </div>
                                        <div className="w-12 h-12 bg-gray-600/20 rounded-lg flex items-center justify-center">
                                            <Activity size={24} className="text-gray-400" />
                                        </div>
                                    </div>
                                    <div className="mt-4 flex items-center text-sm">
                                        <span className="text-gray-400">Total trades</span>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* View Mode Toggle */}
                        <div className="flex items-center justify-between mb-6">
                            <div className="flex items-center space-x-2">
                                <button
                                    onClick={() => setViewMode('overview')}
                                    className={`p-2 rounded-lg transition-colors ${viewMode === 'overview'
                                        ? 'bg-primary-600 text-white'
                                        : 'bg-dark-700 text-gray-400 hover:bg-dark-600'
                                        }`}
                                >
                                    <BarChart3 size={16} />
                                </button>
                                <button
                                    onClick={() => setViewMode('detail')}
                                    className={`p-2 rounded-lg transition-colors ${viewMode === 'detail'
                                        ? 'bg-primary-600 text-white'
                                        : 'bg-dark-700 text-gray-400 hover:bg-dark-600'
                                        }`}
                                >
                                    <PieChart size={16} />
                                </button>
                                <button
                                    onClick={() => setViewMode('chart')}
                                    className={`p-2 rounded-lg transition-colors ${viewMode === 'chart'
                                        ? 'bg-primary-600 text-white'
                                        : 'bg-dark-700 text-gray-400 hover:bg-dark-600'
                                        }`}
                                >
                                    <Activity size={16} />
                                </button>
                            </div>
                        </div>

                        {/* Portfolio Content */}
                        {selectedPortfolio && (
                            <div className="space-y-6">
                                {viewMode === 'overview' && (
                                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                        <PortfolioCard
                                            portfolio={selectedPortfolio}
                                            stats={stats}
                                            onDelete={handleDeletePortfolio}
                                        />
                                        <div className="card p-6">
                                            <h3 className="text-lg font-semibold text-gray-100 mb-4">Recent Transactions</h3>
                                            {transactions.length > 0 ? (
                                                <div className="space-y-3">
                                                    {transactions.slice(0, 5).map((transaction) => (
                                                        <div key={transaction.id} className="flex items-center justify-between p-3 bg-dark-800 rounded-lg">
                                                            <div>
                                                                <p className="text-sm font-medium text-gray-100">
                                                                    {transaction.type} {transaction.symbol}
                                                                </p>
                                                                <p className="text-xs text-gray-400">
                                                                    {new Date(transaction.created_at).toLocaleDateString()}
                                                                </p>
                                                            </div>
                                                            <div className="text-right">
                                                                <p className={`text-sm font-medium ${transaction.type === 'buy' ? 'text-success-400' : 'text-danger-400'
                                                                    }`}>
                                                                    {transaction.type === 'buy' ? '+' : '-'}${transaction.total_amount}
                                                                </p>
                                                                <p className="text-xs text-gray-400">
                                                                    {transaction.quantity} @ ${transaction.price}
                                                                </p>
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            ) : (
                                                <p className="text-gray-400 text-center py-8">No transactions yet</p>
                                            )}
                                        </div>
                                    </div>
                                )}

                                {viewMode === 'detail' && selectedPortfolio && (
                                    <PortfolioDetail
                                        portfolio={selectedPortfolio}
                                        stats={stats}
                                        transactions={transactions}
                                    />
                                )}

                                {viewMode === 'chart' && selectedPortfolio && (
                                    <PortfolioChart
                                        portfolio={selectedPortfolio}
                                        stats={stats}
                                    />
                                )}
                            </div>
                        )}
                    </>
                )}

                {/* Create Portfolio Modal */}
                {showCreateModal && (
                    <CreatePortfolioModal
                        onClose={() => setShowCreateModal(false)}
                        onCreate={handleCreatePortfolio}
                    />
                )}
            </div>
        </div>
    );
};

export default Portfolio;
