import {
    BarChart3,
    Filter,
    PieChart,
    RefreshCw,
    Search,
    TrendingDown,
    TrendingUp
} from 'lucide-react';
import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { portfolioAPI } from '../../services/api';
import AssetCard from '../assets/AssetCard';
import AssetFilters from '../assets/AssetFilters';

const PortfolioAssets = ({ portfolio, onRefresh }) => {
    const [assets, setAssets] = useState([]);
    const [filteredAssets, setFilteredAssets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [showFilters, setShowFilters] = useState(false);
    const [viewMode, setViewMode] = useState('grid'); // grid or list
    const [filters, setFilters] = useState({
        category: 'all',
        priceRange: 'all',
        valueRange: 'all',
        changeRange: 'all',
        marketCapRange: 'all',
        rsiRange: 'all',
        sortBy: 'symbol',
        sortOrder: 'asc'
    });

    // Load portfolio assets when portfolio changes
    useEffect(() => {
        if (portfolio && portfolio.id) {
            loadPortfolioAssets();
        }
    }, [portfolio]);

    // Filter assets when search query or filters change
    useEffect(() => {
        filterAssets();
    }, [assets, searchQuery, filters]);

    const loadPortfolioAssets = async () => {
        if (!portfolio || !portfolio.id) return;

        try {
            setLoading(true);
            console.log('[PortfolioAssets] Loading assets for portfolio:', portfolio.id);
            
            // Get portfolio holdings which contain the assets
            const holdingsResponse = await portfolioAPI.getPortfolioHoldings(portfolio.id);
            console.log('[PortfolioAssets] Holdings response:', holdingsResponse);

            // Process holdings data to create asset objects
            let portfolioAssets = [];
            if (holdingsResponse && Array.isArray(holdingsResponse) && holdingsResponse.length > 0) {
                portfolioAssets = holdingsResponse.map(holding => ({
                    id: holding.asset_id,
                    symbol: holding.symbol,
                    name: holding.name,
                    asset_type: holding.asset_type || 'EQUITY',
                    quantity: holding.quantity,
                    purchase_price: holding.cost_basis,
                    current_price: holding.current_value / holding.quantity,
                    total_value: holding.current_value,
                    price_change_percentage_24h: holding.price_change_percentage_24h || 0,
                    market_cap: holding.market_cap,
                    volume_24h: holding.volume_24h,
                    rsi: holding.rsi,
                    volatility_20d: holding.volatility_20d,
                    purchase_date: holding.purchase_date,
                    // Calculate P&L
                    pnl: holding.unrealized_pnl,
                    pnl_percentage: holding.unrealized_pnl_percent
                }));
            }

            setAssets(portfolioAssets);
        } catch (error) {
            console.error('Failed to load portfolio assets:', error);
            toast.error('Failed to load portfolio assets');
            setAssets([]);
        } finally {
            setLoading(false);
        }
    };

    const filterAssets = () => {
        let filtered = [...assets];

        // Search filter
        if (searchQuery) {
            filtered = filtered.filter(asset =>
                asset.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
                asset.name.toLowerCase().includes(searchQuery.toLowerCase())
            );
        }

        // Category filter
        if (filters.category !== 'all') {
            filtered = filtered.filter(asset => {
                const categoryMap = {
                    'cryptocurrency': 'CRYPTOCURRENCY',
                    'stock': 'EQUITY',
                    'commodity': 'COMMODITY',
                    'forex': 'CASH',
                    'etf': 'ETF',
                    'bond': 'BOND',
                    'real_estate': 'REAL_ESTATE',
                    'mutual_fund': 'MUTUALFUND',
                    'index_fund': 'INDEX'
                };
                return asset.asset_type === categoryMap[filters.category];
            });
        }

        // Price range filter
        if (filters.priceRange !== 'all') {
            const [min, max] = filters.priceRange.split('-').map(Number);
            filtered = filtered.filter(asset => {
                const price = asset.current_price || 0;
                if (max) {
                    return price >= min && price <= max;
                } else {
                    return price >= min;
                }
            });
        }

        // Value range filter
        if (filters.valueRange !== 'all') {
            const [min, max] = filters.valueRange.split('-').map(Number);
            filtered = filtered.filter(asset => {
                const totalValue = asset.total_value || 0;
                if (max) {
                    return totalValue >= min && totalValue <= max;
                } else {
                    return totalValue >= min;
                }
            });
        }

        // Change range filter
        if (filters.changeRange !== 'all') {
            filtered = filtered.filter(asset => {
                const change = asset.price_change_percentage_24h || 0;
                switch (filters.changeRange) {
                    case 'positive':
                        return change > 0;
                    case 'negative':
                        return change < 0;
                    case 'stable':
                        return change >= -1 && change <= 1;
                    default:
                        return true;
                }
            });
        }

        // Market cap range filter
        if (filters.marketCapRange !== 'all') {
            filtered = filtered.filter(asset => {
                const marketCap = asset.market_cap || 0;
                switch (filters.marketCapRange) {
                    case '0-1e6':
                        return marketCap < 1e6;
                    case '1e6-1e9':
                        return marketCap >= 1e6 && marketCap < 1e9;
                    case '1e9-1e12':
                        return marketCap >= 1e9 && marketCap < 1e12;
                    case '1e12-':
                        return marketCap >= 1e12;
                    default:
                        return true;
                }
            });
        }

        // RSI range filter
        if (filters.rsiRange !== 'all') {
            filtered = filtered.filter(asset => {
                const rsi = asset.rsi;
                if (rsi === null || rsi === undefined) return false;
                switch (filters.rsiRange) {
                    case '0-30':
                        return rsi >= 0 && rsi <= 30;
                    case '30-70':
                        return rsi > 30 && rsi < 70;
                    case '70-100':
                        return rsi >= 70 && rsi <= 100;
                    default:
                        return true;
                }
            });
        }

        // Sort
        filtered.sort((a, b) => {
            let aValue, bValue;

            switch (filters.sortBy) {
                case 'symbol':
                    aValue = a.symbol || '';
                    bValue = b.symbol || '';
                    break;
                case 'name':
                    aValue = a.name || '';
                    bValue = b.name || '';
                    break;
                case 'quantity':
                    aValue = a.quantity || 0;
                    bValue = b.quantity || 0;
                    break;
                case 'purchase_price':
                    aValue = a.purchase_price || 0;
                    bValue = b.purchase_price || 0;
                    break;
                case 'current_price':
                    aValue = a.current_price || 0;
                    bValue = b.current_price || 0;
                    break;
                case 'total_value':
                    aValue = a.total_value || 0;
                    bValue = b.total_value || 0;
                    break;
                case 'purchase_date':
                    aValue = new Date(a.purchase_date || 0);
                    bValue = new Date(b.purchase_date || 0);
                    break;
                case 'market_cap':
                    aValue = a.market_cap || 0;
                    bValue = b.market_cap || 0;
                    break;
                case 'volume_24h':
                    aValue = a.volume_24h || 0;
                    bValue = b.volume_24h || 0;
                    break;
                case 'price_change_percentage_24h':
                    aValue = a.price_change_percentage_24h || 0;
                    bValue = b.price_change_percentage_24h || 0;
                    break;
                case 'rsi':
                    aValue = a.rsi || 0;
                    bValue = b.rsi || 0;
                    break;
                case 'volatility_20d':
                    aValue = a.volatility_20d || 0;
                    bValue = b.volatility_20d || 0;
                    break;
                default:
                    aValue = a.symbol || '';
                    bValue = b.symbol || '';
            }

            if (filters.sortBy === 'symbol' || filters.sortBy === 'name') {
                // String comparison
                if (filters.sortOrder === 'asc') {
                    return aValue.localeCompare(bValue);
                } else {
                    return bValue.localeCompare(aValue);
                }
            } else {
                // Numeric comparison
                if (filters.sortOrder === 'asc') {
                    return aValue - bValue;
                } else {
                    return bValue - aValue;
                }
            }
        });

        setFilteredAssets(filtered);
    };

    const handleRefresh = () => {
        loadPortfolioAssets();
        onRefresh && onRefresh();
        toast.success('Portfolio assets refreshed');
    };

    const handleFilterChange = (newFilters) => {
        setFilters(prev => ({ ...prev, ...newFilters }));
    };

    const getTotalStats = () => {
        const totalValue = filteredAssets.reduce((sum, asset) => {
            return sum + (asset.total_value || 0);
        }, 0);

        const totalInvested = filteredAssets.reduce((sum, asset) => {
            const invested = (asset.quantity || 0) * (asset.purchase_price || 0);
            return sum + invested;
        }, 0);

        const totalPnL = totalValue - totalInvested;
        const totalPnLPercentage = totalInvested > 0 ? (totalPnL / totalInvested) * 100 : 0;

        const positiveAssets = filteredAssets.filter(asset => {
            const pnl = asset.pnl_percentage || 0;
            return pnl > 0;
        }).length;

        const negativeAssets = filteredAssets.filter(asset => {
            const pnl = asset.pnl_percentage || 0;
            return pnl < 0;
        }).length;

        return {
            totalValue,
            totalInvested,
            totalPnL,
            totalPnLPercentage,
            positiveAssets,
            negativeAssets,
            totalAssets: filteredAssets.length
        };
    };

    const stats = getTotalStats();

    if (loading) {
        return (
            <div className="space-y-6">
                <div className="text-center py-12">
                    <RefreshCw className="w-8 h-8 text-primary-400 animate-spin mx-auto mb-4" />
                    <p className="text-gray-400">Loading portfolio assets...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-gray-100 mb-2">Portfolio Assets</h2>
                    <p className="text-gray-400">Assets in {portfolio?.name || 'this portfolio'}</p>
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
                        onClick={() => setShowFilters(!showFilters)}
                        className="btn-outline flex items-center space-x-2"
                    >
                        <Filter size={16} />
                        <span>Filters</span>
                    </button>
                </div>
            </div>

            {/* Search Bar */}
            <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                    type="text"
                    placeholder="Search assets by symbol or name..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="input-field w-full pl-10 pr-4 py-3"
                />
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="card p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-400">Total Assets</p>
                            <p className="text-2xl font-bold text-gray-100">{stats.totalAssets}</p>
                        </div>
                        <div className="w-12 h-12 bg-primary-600/20 rounded-lg flex items-center justify-center">
                            <BarChart3 size={24} className="text-primary-400" />
                        </div>
                    </div>
                </div>

                <div className="card p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-400">Total Value</p>
                            <p className="text-2xl font-bold text-gray-100">
                                ${(stats.totalValue / 1000).toFixed(2)}K
                            </p>
                        </div>
                        <div className="w-12 h-12 bg-success-600/20 rounded-lg flex items-center justify-center">
                            <TrendingUp size={24} className="text-success-400" />
                        </div>
                    </div>
                </div>

                <div className="card p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-400">Total Invested</p>
                            <p className="text-2xl font-bold text-gray-100">
                                ${(stats.totalInvested / 1000).toFixed(2)}K
                            </p>
                        </div>
                        <div className="w-12 h-12 bg-warning-600/20 rounded-lg flex items-center justify-center">
                            <BarChart3 size={24} className="text-warning-400" />
                        </div>
                    </div>
                </div>

                <div className="card p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-400">P&L</p>
                            <p className={`text-2xl font-bold ${stats.totalPnL >= 0 ? 'text-success-400' : 'text-danger-400'}`}>
                                ${(stats.totalPnL / 1000).toFixed(2)}K
                            </p>
                            <p className={`text-xs ${stats.totalPnLPercentage >= 0 ? 'text-success-400' : 'text-danger-400'}`}>
                                {stats.totalPnLPercentage.toFixed(2)}%
                            </p>
                        </div>
                        <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${stats.totalPnL >= 0 ? 'bg-success-600/20' : 'bg-danger-600/20'}`}>
                            {stats.totalPnL >= 0 ? <TrendingUp size={24} className="text-success-400" /> : <TrendingDown size={24} className="text-danger-400" />}
                        </div>
                    </div>
                </div>
            </div>

            {/* Filters */}
            {showFilters && (
                <div className="card p-6">
                    <AssetFilters
                        filters={filters}
                        onFilterChange={handleFilterChange}
                    />
                </div>
            )}

            {/* View Mode Toggle */}
            <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                    <button
                        onClick={() => setViewMode('grid')}
                        className={`p-2 rounded-lg transition-colors ${viewMode === 'grid'
                            ? 'bg-primary-600 text-white'
                            : 'bg-dark-700 text-gray-400 hover:bg-dark-600'
                            }`}
                    >
                        <BarChart3 size={16} />
                    </button>
                    <button
                        onClick={() => setViewMode('list')}
                        className={`p-2 rounded-lg transition-colors ${viewMode === 'list'
                            ? 'bg-primary-600 text-white'
                            : 'bg-dark-700 text-gray-400 hover:bg-dark-600'
                            }`}
                    >
                        <PieChart size={16} />
                    </button>
                </div>
                <p className="text-sm text-gray-400">
                    Showing {filteredAssets.length} of {assets.length} assets
                </p>
            </div>

            {/* Assets Grid/List */}
            {filteredAssets.length === 0 ? (
                <div className="card p-12 text-center">
                    <BarChart3 className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-gray-300 mb-2">No assets found</h3>
                    <p className="text-gray-500">
                        {searchQuery ? 'Try adjusting your search criteria' : 'No assets in this portfolio yet'}
                    </p>
                </div>
            ) : (
                <div className={
                    viewMode === 'grid'
                        ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6'
                        : 'space-y-4'
                }>
                    {filteredAssets.map((asset) => (
                        <AssetCard
                            key={asset.id}
                            asset={asset}
                            viewMode={viewMode}
                            onClick={() => {
                                // TODO: Implement asset detail view
                                toast.info('Asset detail view coming soon!');
                            }}
                            onEdit={() => {
                                // TODO: Implement edit asset functionality
                                toast.info('Edit asset functionality coming soon!');
                            }}
                            onDelete={() => {
                                // TODO: Implement delete asset functionality
                                toast.info('Delete asset functionality coming soon!');
                            }}
                            onAddToPortfolio={() => {
                                // Not applicable for portfolio assets
                                toast.info('Asset is already in this portfolio');
                            }}
                            onViewInPortfolio={() => {
                                // Not applicable for portfolio assets
                                toast.info('Asset is already in this portfolio');
                            }}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};

export default PortfolioAssets;
