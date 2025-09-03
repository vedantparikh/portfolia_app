import {
    AlertTriangle,
    CheckCircle,
    Clock,
    TrendingDown,
    TrendingUp
} from 'lucide-react';
import React from 'react';

const DashboardWidget = ({ title, value, change, changePercent, icon: Icon, color = 'primary', subtitle, trend, status }) => {
    const getColorClasses = (color) => {
        switch (color) {
            case 'success':
                return {
                    bg: 'bg-success-600/20',
                    icon: 'text-success-400',
                    text: 'text-success-400'
                };
            case 'danger':
                return {
                    bg: 'bg-danger-600/20',
                    icon: 'text-danger-400',
                    text: 'text-danger-400'
                };
            case 'warning':
                return {
                    bg: 'bg-warning-600/20',
                    icon: 'text-warning-400',
                    text: 'text-warning-400'
                };
            case 'info':
                return {
                    bg: 'bg-primary-600/20',
                    icon: 'text-primary-400',
                    text: 'text-primary-400'
                };
            default:
                return {
                    bg: 'bg-primary-600/20',
                    icon: 'text-primary-400',
                    text: 'text-primary-400'
                };
        }
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'success':
                return <CheckCircle size={16} className="text-success-400" />;
            case 'warning':
                return <AlertTriangle size={16} className="text-warning-400" />;
            case 'pending':
                return <Clock size={16} className="text-warning-400" />;
            default:
                return null;
        }
    };

    const getTrendIcon = (trend) => {
        if (trend === 'up') {
            return <TrendingUp size={16} className="text-success-400" />;
        } else if (trend === 'down') {
            return <TrendingDown size={16} className="text-danger-400" />;
        }
        return null;
    };

    const colors = getColorClasses(color);

    return (
        <div className="card p-6 hover:bg-dark-800/50 transition-colors">
            <div className="flex items-center justify-between mb-4">
                <div>
                    <p className="text-sm text-gray-400">{title}</p>
                    <p className="text-2xl font-bold text-gray-100">{value}</p>
                </div>
                <div className={`w-12 h-12 ${colors.bg} rounded-lg flex items-center justify-center`}>
                    <Icon size={24} className={colors.icon} />
                </div>
            </div>

            {change !== undefined && (
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        {getTrendIcon(trend)}
                        <span className={`text-sm font-medium ${change >= 0 ? 'text-success-400' : 'text-danger-400'}`}>
                            {change >= 0 ? '+' : ''}{change}
                        </span>
                        {changePercent !== undefined && (
                            <span className={`text-sm ${changePercent >= 0 ? 'text-success-400' : 'text-danger-400'}`}>
                                ({changePercent >= 0 ? '+' : ''}{changePercent.toFixed(2)}%)
                            </span>
                        )}
                    </div>
                    {status && (
                        <div className="flex items-center space-x-1">
                            {getStatusIcon(status)}
                            <span className="text-xs text-gray-400 capitalize">{status}</span>
                        </div>
                    )}
                </div>
            )}

            {subtitle && (
                <div className="mt-2">
                    <p className="text-xs text-gray-500">{subtitle}</p>
                </div>
            )}
        </div>
    );
};

export default DashboardWidget;
