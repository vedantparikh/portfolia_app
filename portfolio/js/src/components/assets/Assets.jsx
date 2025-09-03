import {
    Activity,
    ArrowLeft,
    BarChart3,
    DollarSign,
    Filter,
    PieChart,
    RefreshCw,
    Search,
    TrendingDown,
    TrendingUp
} from 'lucide-react';
import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { marketAPI } from '../../services/api';
import AssetCard from './AssetCard';
import AssetFilters from './AssetFilters';
import AssetModal from './AssetModal';

const Assets = () => {
    const [assets, setAssets] = useState([]);
    const [filteredAssets, setFilteredAssets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedAsset, setSelectedAsset] = useState(null);
    const [showModal, setShowModal] = useState(false);
    const [showFilters, setShowFilters] = useState(false);
    const [viewMode, setViewMode] = useState('grid'); // grid or list
    const [filters, setFilters] = useState({
        category: 'all',
        priceRange: 'all',
        changeRange: 'all',
        sortBy: 'market_cap',
        sortOrder: 'desc'
    });

    // Load assets on component mount
    useEffect(() => {
        loadAssets();
    }, []);

    // Filter assets when search query or filters change
    useEffect(() => {
        filterAssets();
    }, [assets, searchQuery, filters]);

    const loadAssets = async () => {
        try {
            setLoading(true);
            const response = await marketAPI.getAssets({
                limit: 100,
                include_prices: true
            });
            setAssets(response.assets || []);
        } catch (error) {
            console.error('Failed to load assets:', error);
            toast.error('Failed to load assets');
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
            filtered = filtered.filter(asset => asset.category === filters.category);
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

        // Sort
        filtered.sort((a, b) => {
            let aValue, bValue;

            switch (filters.sortBy) {
                case 'market_cap':
                    aValue = a.market_cap || 0;
                    bValue = b.market_cap || 0;
                    break;
                case 'price':
                    aValue = a.current_price || 0;
                    bValue = b.current_price || 0;
                    break;
                case 'change':
                    aValue = a.price_change_percentage_24h || 0;
                    bValue = b.price_change_percentage_24h || 0;
                    break;
                case 'volume':
                    aValue = a.total_volume || 0;
                    bValue = b.total_volume || 0;
                    break;
                default:
                    aValue = a.market_cap || 0;
                    bValue = b.market_cap || 0;
            }

            if (filters.sortOrder === 'asc') {
                return aValue - bValue;
            } else {
                return bValue - aValue;
            }
        });

        setFilteredAssets(filtered);
    };

    const handleAssetClick = (asset) => {
        setSelectedAsset(asset);
        setShowModal(true);
    };

    const handleRefresh = () => {
        loadAssets();
        toast.success('Assets refreshed');
    };

    const handleFilterChange = (newFilters) => {
        setFilters(prev => ({ ...prev, ...newFilters }));
    };

    const getTotalStats = () => {
        const totalMarketCap = filteredAssets.reduce((sum, asset) => sum + (asset.market_cap || 0), 0);
        const totalVolume = filteredAssets.reduce((sum, asset) => sum + (asset.total_volume || 0), 0);
        const positiveChanges = filteredAssets.filter(asset => (asset.price_change_percentage_24h || 0) > 0).length;
        const negativeChanges = filteredAssets.filter(asset => (asset.price_change_percentage_24h || 0) < 0).length;

        return {
            totalMarketCap,
            totalVolume,
            positiveChanges,
            negativeChanges,
            totalAssets: filteredAssets.length
        };
    };

    const stats = getTotalStats();

    if (loading) {
        return (
            <div className="min-h-screen gradient-bg flex items-center justify-center">
                <div className="text-center">
                    <RefreshCw className="w-8 h-8 text-primary-400 animate-spin mx-auto mb-4" />
                    <p className="text-gray-400">Loading assets...</p>
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
                                onClick={() => setShowFilters(!showFilters)}
                                className="btn-outline flex items-center space-x-2"
                            >
                                <Filter size={16} />
                                <span>Filters</span>
                            </button>
                        </div>
                    </div>

                    <div className="mb-4">
                        <h1 className="text-3xl font-bold text-gray-100 mb-2">Assets</h1>
                        <p className="text-gray-400">Explore and analyze market assets</p>
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
                </div>

                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
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
                                <p className="text-sm text-gray-400">Market Cap</p>
                                <p className="text-2xl font-bold text-gray-100">
                                    ${(stats.totalMarketCap / 1e12).toFixed(2)}T
                                </p>
                            </div>
                            <div className="w-12 h-12 bg-success-600/20 rounded-lg flex items-center justify-center">
                                <DollarSign size={24} className="text-success-400" />
                            </div>
                        </div>
                    </div>

                    <div className="card p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-400">24h Volume</p>
                                <p className="text-2xl font-bold text-gray-100">
                                    ${(stats.totalVolume / 1e9).toFixed(2)}B
                                </p>
                            </div>
                            <div className="w-12 h-12 bg-warning-600/20 rounded-lg flex items-center justify-center">
                                <Activity size={24} className="text-warning-400" />
                            </div>
                        </div>
                    </div>

                    <div className="card p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-400">Gainers</p>
                                <p className="text-2xl font-bold text-success-400">{stats.positiveChanges}</p>
                            </div>
                            <div className="w-12 h-12 bg-success-600/20 rounded-lg flex items-center justify-center">
                                <TrendingUp size={24} className="text-success-400" />
                            </div>
                        </div>
                    </div>

                    <div className="card p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-400">Losers</p>
                                <p className="text-2xl font-bold text-danger-400">{stats.negativeChanges}</p>
                            </div>
                            <div className="w-12 h-12 bg-danger-600/20 rounded-lg flex items-center justify-center">
                                <TrendingDown size={24} className="text-danger-400" />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Filters */}
                {showFilters && (
                    <div className="card p-6 mb-8">
                        <AssetFilters
                            filters={filters}
                            onFilterChange={handleFilterChange}
                        />
                    </div>
                )}

                {/* View Mode Toggle */}
                <div className="flex items-center justify-between mb-6">
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
                            {searchQuery ? 'Try adjusting your search criteria' : 'No assets available at the moment'}
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
                                onClick={() => handleAssetClick(asset)}
                            />
                        ))}
                    </div>
                )}

                {/* Asset Modal */}
                {showModal && selectedAsset && (
                    <AssetModal
                        asset={selectedAsset}
                        onClose={() => {
                            setShowModal(false);
                            setSelectedAsset(null);
                        }}
                    />
                )}
            </div>
        </div>
    );
};

export default Assets;
