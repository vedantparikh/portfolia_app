import { Database, Search, TrendingUp } from 'lucide-react';
import React, { useEffect, useRef, useState } from 'react';
import { assetAPI, marketAPI } from '../../services/api';
import LoadingSpinner from './LoadingSpinner';

const ClientSideAssetSearch = ({
    value,
    onChange,
    onSelect,
    onPriceUpdate,
    placeholder = "Search assets...",
    disabled = false,
    showSuggestions = true
}) => {
    const [allAssets, setAllAssets] = useState([]);
    const [filteredAssets, setFilteredAssets] = useState([]);
    const [showSuggestionsDropdown, setShowSuggestionsDropdown] = useState(false);
    const [loading, setLoading] = useState(false);
    const [searching, setSearching] = useState(false);
    const [selectedAsset, setSelectedAsset] = useState(null);
    const inputRef = useRef(null);
    const dropdownRef = useRef(null);

    // Fetch all assets on component mount
    useEffect(() => {
        fetchAllAssets();
    }, []);

    // Filter assets based on search query
    useEffect(() => {
        if (value && value.length >= 2) {
            filterAssets(value);
        } else {
            setFilteredAssets([]);
        }
    }, [value, allAssets]);

    const fetchAllAssets = async () => {
        try {
            setLoading(true);
            const response = await assetAPI.getAssets({ limit: 1000 }); // Get all assets
            setAllAssets(response || []);
        } catch (error) {
            console.error('Failed to fetch assets:', error);
        } finally {
            setLoading(false);
        }
    };

    const filterAssets = (query) => {
        if (!query || query.length < 2) {
            setFilteredAssets([]);
            return;
        }

        const searchTerm = query.toLowerCase();
        const filtered = allAssets.filter(asset =>
            asset.symbol.toLowerCase().includes(searchTerm) ||
            (asset.name && asset.name.toLowerCase().includes(searchTerm))
        );

        // Limit to 10 results for better performance
        setFilteredAssets(filtered.slice(0, 10));
    };

    const fetchCurrentPrice = async (symbol) => {
        try {
            setSearching(true);
            const priceData = await marketAPI.getStockLatestData([symbol]);

            if (priceData && priceData.length > 0) {
                // Get the latest data point (first in the array)
                const latestData = priceData[0];
                if (onPriceUpdate) {
                    onPriceUpdate({
                        symbol: symbol,
                        price: parseFloat(latestData.Close),
                        currency: 'USD',
                        date: latestData.Date,
                        name: symbol,
                        exchange: 'NMS',
                        market_cap: null,
                        pe_ratio: null,
                        dividend_yield: null,
                        beta: null
                    });
                }
            }
        } catch (error) {
            console.error('Failed to fetch current price:', error);
        } finally {
            setSearching(false);
        }
    };

    // Handle input change
    const handleInputChange = (e) => {
        const query = e.target.value;
        onChange(query);
    };

    // Handle suggestion click
    const handleSuggestionClick = (asset) => {
        setSelectedAsset(asset);
        if (onSelect) {
            onSelect(asset);
        }
        setShowSuggestionsDropdown(false);

        // Fetch current price for the selected asset
        fetchCurrentPrice(asset.symbol);
    };

    // Handle input focus
    const handleFocus = () => {
        if (value && filteredAssets.length > 0) {
            setShowSuggestionsDropdown(true);
        }
    };

    // Handle input blur
    const handleBlur = () => {
        // Delay hiding to allow clicking on suggestions
        setTimeout(() => {
            setShowSuggestionsDropdown(false);
        }, 200);
    };

    // Handle key navigation
    const handleKeyDown = (e) => {
        if (!showSuggestionsDropdown || filteredAssets.length === 0) return;

        const currentIndex = filteredAssets.findIndex(asset => asset.symbol === value);

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                const nextIndex = currentIndex < filteredAssets.length - 1 ? currentIndex + 1 : 0;
                onChange(filteredAssets[nextIndex].symbol);
                break;
            case 'ArrowUp':
                e.preventDefault();
                const prevIndex = currentIndex > 0 ? currentIndex - 1 : filteredAssets.length - 1;
                onChange(filteredAssets[prevIndex].symbol);
                break;
            case 'Enter':
                e.preventDefault();
                if (currentIndex >= 0) {
                    handleSuggestionClick(filteredAssets[currentIndex]);
                }
                break;
            case 'Escape':
                setShowSuggestionsDropdown(false);
                break;
        }
    };

    // Get suggestion icon
    const getSuggestionIcon = (asset) => {
        return (
            <div className="w-8 h-8 bg-primary-600/20 rounded-lg flex items-center justify-center">
                <Database size={16} className="text-primary-400" />
            </div>
        );
    };

    // Get suggestion badge
    const getSuggestionBadge = (asset) => {
        return (
            <span className="text-xs px-2 py-1 bg-primary-600/20 text-primary-400 rounded">
                Your Asset
            </span>
        );
    };

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (
                dropdownRef.current &&
                !dropdownRef.current.contains(event.target) &&
                inputRef.current &&
                !inputRef.current.contains(event.target)
            ) {
                setShowSuggestionsDropdown(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    return (
        <div className="relative">
            {/* Input Field */}
            <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                    ref={inputRef}
                    type="text"
                    value={value}
                    onChange={handleInputChange}
                    onFocus={handleFocus}
                    onBlur={handleBlur}
                    onKeyDown={handleKeyDown}
                    placeholder={placeholder}
                    disabled={disabled}
                    className="input-field w-full pl-10 pr-4 py-3"
                />
                {searching && (
                    <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                        <LoadingSpinner size="sm" />
                    </div>
                )}
            </div>

            {/* Suggestions Dropdown */}
            {showSuggestionsDropdown && filteredAssets.length > 0 && (
                <div
                    ref={dropdownRef}
                    className="absolute z-50 w-full mt-1 bg-dark-800 border border-dark-600 rounded-lg shadow-lg max-h-80 overflow-y-auto"
                >
                    {filteredAssets.map((asset, index) => (
                        <div key={asset.id} className="border-b border-dark-700 last:border-b-0">
                            <button
                                type="button"
                                onClick={() => handleSuggestionClick(asset)}
                                className="w-full flex items-center space-x-3 px-4 py-3 text-left text-gray-300 hover:bg-dark-700 transition-colors"
                            >
                                {getSuggestionIcon(asset)}
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center space-x-2">
                                        <div className="font-mono text-sm font-medium">{asset.symbol}</div>
                                        {getSuggestionBadge(asset)}
                                    </div>
                                    <div className="text-xs text-gray-500 truncate">
                                        {asset.name}
                                    </div>
                                    <div className="text-xs text-gray-600">
                                        {asset.exchange} • {asset.asset_type}
                                    </div>
                                </div>
                            </button>
                        </div>
                    ))}
                </div>
            )}

            {/* No Results */}
            {showSuggestionsDropdown && filteredAssets.length === 0 && !searching && value && value.length >= 2 && (
                <div className="absolute z-50 w-full mt-1 bg-dark-800 border border-dark-600 rounded-lg shadow-lg">
                    <div className="px-4 py-6 text-center">
                        <Database size={32} className="mx-auto mb-3 text-gray-600" />
                        <p className="text-gray-400 text-sm mb-2">No assets found</p>
                        <p className="text-gray-500 text-xs">
                            Asset "{value}" doesn't exist. Please add it first in the Assets section.
                        </p>
                    </div>
                </div>
            )}

            {/* Loading State */}
            {loading && (
                <div className="absolute z-50 w-full mt-1 bg-dark-800 border border-dark-600 rounded-lg shadow-lg">
                    <div className="px-4 py-6 text-center">
                        <LoadingSpinner size="sm" className="mx-auto mb-3" />
                        <p className="text-gray-400 text-sm">Loading assets...</p>
                    </div>
                </div>
            )}

            {/* Selected Asset Info */}
            {selectedAsset && (
                <div className="mt-2 p-3 bg-dark-800 rounded-lg border border-dark-600">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                            <div className="w-8 h-8 bg-primary-600/20 rounded-lg flex items-center justify-center">
                                <TrendingUp size={16} className="text-primary-400" />
                            </div>
                            <div>
                                <div className="font-mono text-sm font-medium text-gray-100">
                                    {selectedAsset.symbol}
                                </div>
                                <div className="text-xs text-gray-400">
                                    {selectedAsset.name}
                                </div>
                                <div className="text-xs text-gray-500">
                                    {selectedAsset.exchange} • {selectedAsset.asset_type}
                                </div>
                            </div>
                        </div>
                        <div className="text-xs text-gray-400">
                            {searching ? 'Fetching price...' : 'Price updated'}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ClientSideAssetSearch;
