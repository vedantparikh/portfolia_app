import { Database, Search } from 'lucide-react';
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { marketAPI } from '../../services/api';
import assetCache from '../../services/assetCache';
import LoadingSpinner from './LoadingSpinner';

const ClientSideAssetSearch = ({
    value,
    onChange,
    onSelect,
    onPriceUpdate,
    placeholder = "Search assets...",
    disabled = false,
    showSuggestions = true,
    preloadAssets = false
}) => {
    const [filteredAssets, setFilteredAssets] = useState([]);
    const [showSuggestionsDropdown, setShowSuggestionsDropdown] = useState(false);
    const [loading, setLoading] = useState(false);
    const [searching, setSearching] = useState(false);
    const inputRef = useRef(null);
    const dropdownRef = useRef(null);
    const debounceTimeoutRef = useRef(null);

    // Subscribe to asset cache updates and preload if needed
    useEffect(() => {
        // Subscribe to cache updates
        const unsubscribe = assetCache.subscribe(({ isLoading: cacheLoading }) => {
            setLoading(cacheLoading);
        });

        // Preload assets if requested or if this is a transaction-related component
        if (preloadAssets) {
            assetCache.preloadAssets();
        }

        return () => {
            unsubscribe();
            if (debounceTimeoutRef.current) {
                clearTimeout(debounceTimeoutRef.current);
            }
        };
    }, [preloadAssets]);

    // Debounced filter function using asset cache
    const debouncedFilter = useCallback((query) => {
        if (debounceTimeoutRef.current) {
            clearTimeout(debounceTimeoutRef.current);
        }

        debounceTimeoutRef.current = setTimeout(() => {
            if (query && query.length >= 2) {
                const filtered = assetCache.filterAssets(query, 8);
                setFilteredAssets(filtered);
            } else {
                setFilteredAssets([]);
            }
        }, 200); // Reduced debounce time since filtering is now in-memory
    }, []);

    // Filter assets based on search query with debouncing
    useEffect(() => {
        debouncedFilter(value);
    }, [value, debouncedFilter]);

    const fetchCurrentPrice = useCallback(async (symbol) => {
        try {
            setSearching(true);
            console.log(`[ClientSideAssetSearch] Fetching price for symbol: ${symbol}`);

            // Use the stock-latest-data endpoint with symbols as query parameter
            const priceData = await marketAPI.getStockLatestData(symbol);

            console.log(`[ClientSideAssetSearch] Price data received:`, priceData);

            if (priceData && Array.isArray(priceData) && priceData.length > 0) {
                // Get the latest data point (first in the array)
                const latestData = priceData[0];
                const price = parseFloat(latestData.latest_price || latestData.Close || latestData.close || latestData.price);

                if (onPriceUpdate && !isNaN(price)) {
                    console.log(`[ClientSideAssetSearch] Updating price: ${price} for ${symbol}`);
                    onPriceUpdate({
                        symbol: symbol,
                        price: price,
                        currency: latestData.currency || 'USD',
                        date: latestData.latest_date || latestData.Date || latestData.date,
                        name: latestData.name || symbol,
                        exchange: latestData.exchange || latestData.Exchange || 'NMS',
                        market_cap: latestData.market_cap || latestData.MarketCap || null,
                        pe_ratio: latestData.pe_ratio || latestData.PE || null,
                        dividend_yield: latestData.dividend_yield || latestData.DividendYield || null,
                        beta: latestData.beta || latestData.Beta || null
                    });
                } else {
                    console.warn(`[ClientSideAssetSearch] Invalid price data for ${symbol}:`, latestData);
                }
            } else if (priceData && typeof priceData === 'object' && !Array.isArray(priceData)) {
                // Handle single object response
                const price = parseFloat(priceData.latest_price || priceData.Close || priceData.close || priceData.price);

                if (onPriceUpdate && !isNaN(price)) {
                    console.log(`[ClientSideAssetSearch] Updating price (object): ${price} for ${symbol}`);
                    onPriceUpdate({
                        symbol: symbol,
                        price: price,
                        currency: priceData.currency || 'USD',
                        date: priceData.latest_date || priceData.Date || priceData.date,
                        name: priceData.name || symbol,
                        exchange: priceData.exchange || priceData.Exchange || 'NMS',
                        market_cap: priceData.market_cap || priceData.MarketCap || null,
                        pe_ratio: priceData.pe_ratio || priceData.PE || null,
                        dividend_yield: priceData.dividend_yield || priceData.DividendYield || null,
                        beta: priceData.beta || priceData.Beta || null
                    });
                }
            } else {
                console.warn(`[ClientSideAssetSearch] No valid price data found for ${symbol}`);
            }
        } catch (error) {
            console.error(`[ClientSideAssetSearch] Failed to fetch current price for ${symbol}:`, error);
        } finally {
            setSearching(false);
        }
    }, [onPriceUpdate]);

    // Handle input change
    const handleInputChange = (e) => {
        const query = e.target.value;
        onChange(query);
    };

    // Handle suggestion click
    const handleSuggestionClick = useCallback((asset) => {
        if (onSelect) {
            onSelect(asset);
        }
        setShowSuggestionsDropdown(false);

        // Fetch current price for the selected asset
        fetchCurrentPrice(asset.symbol);
    }, [onSelect, fetchCurrentPrice]);

    // Handle input focus
    const handleFocus = useCallback(() => {
        if (value && filteredAssets.length > 0) {
            setShowSuggestionsDropdown(true);
        }
    }, [value, filteredAssets.length]);

    // Handle input blur
    const handleBlur = useCallback(() => {
        // Delay hiding to allow clicking on suggestions
        setTimeout(() => {
            setShowSuggestionsDropdown(false);
        }, 200);
    }, []);

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

    // Memoized suggestion icon
    const getSuggestionIcon = useMemo(() => (
        <div className="w-8 h-8 bg-primary-600/20 rounded-lg flex items-center justify-center">
            <Database size={16} className="text-primary-400" />
        </div>
    ), []);

    // Memoized suggestion badge
    const getSuggestionBadge = useMemo(() => (
        <span className="text-xs px-2 py-1 bg-primary-600/20 text-primary-400 rounded">
            Your Asset
        </span>
    ), []);

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
                                {getSuggestionIcon}
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center space-x-2">
                                        <div className="font-mono text-sm font-medium">{asset.symbol}</div>
                                        {getSuggestionBadge}
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

        </div>
    );
};

export default ClientSideAssetSearch;
