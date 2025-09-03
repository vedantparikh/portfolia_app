import {
    BarChart3,
    Calendar,
    Edit,
    Settings,
    Trash2,
    TrendingDown,
    TrendingUp
} from 'lucide-react';
import React from 'react';

const PortfolioCard = ({ portfolio, stats, onEdit, onDelete }) => {
    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount);
    };

    const formatPercentage = (value) => {
        return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
    };

    const getChangeColor = (value) => {
        if (value > 0) return 'text-success-400';
        if (value < 0) return 'text-danger-400';
        return 'text-gray-400';
    };

    const getChangeIcon = (value) => {
        if (value > 0) return <TrendingUp size={16} className="text-success-400" />;
        if (value < 0) return <TrendingDown size={16} className="text-danger-400" />;
        return null;
    };

    const handleDelete = () => {
        if (window.confirm(`Are you sure you want to delete "${portfolio.name}"? This action cannot be undone.`)) {
            onDelete(portfolio.id);
        }
    };

    return (
        <div className="card p-6">
            <div className="flex items-start justify-between mb-6">
                <div>
                    <h3 className="text-xl font-semibold text-gray-100 mb-1">{portfolio.name}</h3>
                    <p className="text-sm text-gray-400">{portfolio.description || 'No description'}</p>
                </div>
                <div className="flex items-center space-x-2">
                    <button
                        onClick={() => onEdit && onEdit(portfolio)}
                        className="p-2 rounded-lg hover:bg-dark-800 transition-colors"
                        title="Edit portfolio"
                    >
                        <Edit size={16} className="text-gray-400" />
                    </button>
                    <button className="p-2 rounded-lg hover:bg-dark-800 transition-colors">
                        <Settings size={16} className="text-gray-400" />
                    </button>
                    <button
                        onClick={handleDelete}
                        className="p-2 rounded-lg hover:bg-danger-600/20 transition-colors"
                        title="Delete portfolio"
                    >
                        <Trash2 size={16} className="text-danger-400" />
                    </button>
                </div>
            </div>

            {/* Portfolio Stats */}
            <div className="space-y-4">
                <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Total Value</span>
                    <span className="text-2xl font-bold text-gray-100">
                        {formatCurrency(stats?.totalValue || 0)}
                    </span>
                </div>

                <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Total Gain/Loss</span>
                    <div className="flex items-center space-x-2">
                        {getChangeIcon(stats?.totalGainLoss || 0)}
                        <span className={`text-lg font-semibold ${getChangeColor(stats?.totalGainLoss || 0)}`}>
                            {formatCurrency(stats?.totalGainLoss || 0)}
                        </span>
                    </div>
                </div>

                <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Total Return</span>
                    <span className={`text-sm font-medium ${getChangeColor(stats?.totalGainLossPercent || 0)}`}>
                        {formatPercentage(stats?.totalGainLossPercent || 0)}
                    </span>
                </div>

                <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Day Change</span>
                    <div className="flex items-center space-x-2">
                        {getChangeIcon(stats?.dayChange || 0)}
                        <span className={`text-sm font-medium ${getChangeColor(stats?.dayChange || 0)}`}>
                            {formatCurrency(stats?.dayChange || 0)}
                        </span>
                    </div>
                </div>

                <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Day Return</span>
                    <span className={`text-sm font-medium ${getChangeColor(stats?.dayChangePercent || 0)}`}>
                        {formatPercentage(stats?.dayChangePercent || 0)}
                    </span>
                </div>
            </div>

            {/* Performance Bar */}
            <div className="mt-6 pt-6 border-t border-dark-700">
                <div className="flex items-center justify-between text-xs text-gray-500 mb-2">
                    <span>Performance</span>
                    <span>{formatPercentage(stats?.totalGainLossPercent || 0)}</span>
                </div>
                <div className="w-full bg-dark-700 rounded-full h-2">
                    <div
                        className={`h-2 rounded-full transition-all duration-300 ${(stats?.totalGainLossPercent || 0) > 0
                            ? 'bg-success-400'
                            : (stats?.totalGainLossPercent || 0) < 0
                                ? 'bg-danger-400'
                                : 'bg-gray-500'
                            }`}
                        style={{
                            width: `${Math.min(Math.abs(stats?.totalGainLossPercent || 0) * 2, 100)}%`
                        }}
                    />
                </div>
            </div>

            {/* Portfolio Info */}
            <div className="mt-6 pt-6 border-t border-dark-700">
                <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="flex items-center space-x-2">
                        <BarChart3 size={16} className="text-gray-400" />
                        <span className="text-gray-400">Holdings:</span>
                        <span className="text-gray-100 font-medium">{stats?.totalHoldings || 0}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                        <Calendar size={16} className="text-gray-400" />
                        <span className="text-gray-400">Created:</span>
                        <span className="text-gray-100 font-medium">
                            {new Date(portfolio.created_at).toLocaleDateString()}
                        </span>
                    </div>
                </div>
            </div>

            {/* Quick Actions */}
            <div className="mt-6 pt-6 border-t border-dark-700">
                <div className="flex space-x-3">
                    <button className="flex-1 btn-primary text-sm py-2">
                        Add Position
                    </button>
                    <button className="flex-1 btn-outline text-sm py-2">
                        View Details
                    </button>
                </div>
            </div>
        </div>
    );
};

export default PortfolioCard;
