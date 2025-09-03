import { ArrowLeft, Bookmark, Plus, RefreshCw } from 'lucide-react';
import React, { useEffect, useRef, useState } from 'react';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import { watchlistAPI } from '../../services/api';
import AddSymbolModal from './AddSymbolModal';
import CreateWatchlistModal from './CreateWatchlistModal';
import WatchlistContent from './WatchlistContent';
import WatchlistSidebar from './WatchlistSidebar';

const Watchlist = () => {
    const navigate = useNavigate();
    const [watchlists, setWatchlists] = useState([]);
    const [selectedWatchlist, setSelectedWatchlist] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [showAddSymbolModal, setShowAddSymbolModal] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterType, setFilterType] = useState('all');
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(true);
    const [refreshInterval, setRefreshInterval] = useState(30000); // 30 seconds default
    
    // useRef to store the interval ID so we can clear it later
    const refreshIntervalRef = useRef(null);

    // Load watchlists on component mount
    useEffect(() => {
        loadWatchlists();
    }, []);

    // Set up automatic refresh when component mounts and selectedWatchlist changes
    useEffect(() => {
        // Clear any existing interval
        if (refreshIntervalRef.current) {
            clearInterval(refreshIntervalRef.current);
        }

        // Only start auto-refresh if we have a selected watchlist and auto-refresh is enabled
        if (selectedWatchlist && autoRefreshEnabled) {
            console.log(`[Watchlist] Starting auto-refresh every ${refreshInterval}ms for watchlist ${selectedWatchlist.id}`);
            
            refreshIntervalRef.current = setInterval(() => {
                refreshSelectedWatchlist();
            }, refreshInterval);
        }

        // Cleanup function - this runs when component unmounts or dependencies change
        return () => {
            if (refreshIntervalRef.current) {
                console.log('[Watchlist] Clearing auto-refresh interval');
                clearInterval(refreshIntervalRef.current);
            }
        };
    }, [selectedWatchlist, autoRefreshEnabled, refreshInterval]); // Dependencies: re-run when these change

    const loadWatchlists = async () => {
        try {
            setLoading(true);
            const data = await watchlistAPI.getWatchlists(true);
            setWatchlists(data);

            // Select the first watchlist or default watchlist
            if (data.length > 0) {
                const defaultWatchlist = data.find(w => w.is_default) || data[0];

                // Load the full watchlist with items
                try {
                    const fullWatchlist = await watchlistAPI.getWatchlist(defaultWatchlist.id, true);
                    setSelectedWatchlist(fullWatchlist);
                } catch (error) {
                    console.error('Failed to load watchlist items:', error);
                    // Fallback to the basic watchlist data
                    setSelectedWatchlist(defaultWatchlist);
                }
            }
        } catch (error) {
            console.error('Failed to load watchlists:', error);
            console.error('Error details:', error.response?.data);
            toast.error('Failed to load watchlists');
        } finally {
            setLoading(false);
        }
    };

    // Function to refresh the currently selected watchlist data
    const refreshSelectedWatchlist = async () => {
        if (!selectedWatchlist) return;

        try {
            console.log(`[Watchlist] Refreshing watchlist ${selectedWatchlist.id} with real-time data`);
            setIsRefreshing(true);
            
            // Fetch the latest data with real-time prices
            const updatedWatchlist = await watchlistAPI.getWatchlist(selectedWatchlist.id, true);
            setSelectedWatchlist(updatedWatchlist);
            
            console.log('[Watchlist] Watchlist data refreshed successfully');
        } catch (error) {
            console.error('Failed to refresh watchlist data:', error);
            // Don't show toast for background refresh failures to avoid spam
            if (!autoRefreshEnabled) {
                toast.error('Failed to refresh watchlist data');
            }
        } finally {
            setIsRefreshing(false);
        }
    };

    // Manual refresh function (called when user clicks refresh button)
    const handleManualRefresh = async () => {
        await refreshSelectedWatchlist();
        toast.success('Watchlist data refreshed');
    };

    const handleCreateWatchlist = async (watchlistData) => {
        try {
            console.log('Creating watchlist with data:', watchlistData);
            const newWatchlist = await watchlistAPI.createWatchlist(watchlistData);
            console.log('Watchlist created successfully:', newWatchlist);
            setWatchlists(prev => [...prev, newWatchlist]);
            setSelectedWatchlist(newWatchlist);
            setShowCreateModal(false);
            toast.success('Watchlist created successfully');
        } catch (error) {
            console.error('Failed to create watchlist:', error);
            console.error('Error details:', error.response?.data);
            toast.error('Failed to create watchlist');
        }
    };

    const handleUpdateWatchlist = async (watchlistId, updateData) => {
        try {
            const updatedWatchlist = await watchlistAPI.updateWatchlist(watchlistId, updateData);
            setWatchlists(prev =>
                prev.map(w => w.id === watchlistId ? updatedWatchlist : w)
            );
            if (selectedWatchlist?.id === watchlistId) {
                setSelectedWatchlist(updatedWatchlist);
            }
            toast.success('Watchlist updated successfully');
        } catch (error) {
            console.error('Failed to update watchlist:', error);
            toast.error('Failed to update watchlist');
        }
    };

    const handleDeleteWatchlist = async (watchlistId) => {
        try {
            await watchlistAPI.deleteWatchlist(watchlistId);
            setWatchlists(prev => prev.filter(w => w.id !== watchlistId));

            // If deleted watchlist was selected, select another one
            if (selectedWatchlist?.id === watchlistId) {
                const remainingWatchlists = watchlists.filter(w => w.id !== watchlistId);
                if (remainingWatchlists.length > 0) {
                    setSelectedWatchlist(remainingWatchlists[0]);
                } else {
                    setSelectedWatchlist(null);
                }
            }
            toast.success('Watchlist deleted successfully');
        } catch (error) {
            console.error('Failed to delete watchlist:', error);
            toast.error('Failed to delete watchlist');
        }
    };

    const handleAddSymbol = async (symbolData) => {
        if (!selectedWatchlist) {
            const error = new Error('Please select a watchlist first');
            throw error;
        }

        try {
            // Extract symbol string for display purposes
            const symbolString = typeof symbolData === 'string' ? symbolData : symbolData.symbol || symbolData.name;
            symbolData.company_name = symbolData.shortname || symbolData.name;

            // Pass the complete symbol data to the API
            const newItem = await watchlistAPI.addItemToWatchlist(selectedWatchlist.id, symbolData);

            // Update the selected watchlist with the new item
            setSelectedWatchlist(prev => ({
                ...prev,
                items: [...(prev.items || []), newItem]
            }));

            setShowAddSymbolModal(false);
            toast.success(`${symbolString} added to watchlist`);
        } catch (error) {
            console.error('Failed to add symbol:', error);

            // Provide more specific error messages
            let errorMessage = 'Failed to add symbol to watchlist';

            if (error.response?.status === 400) {
                errorMessage = error.response.data?.message || 'Invalid symbol or symbol already exists';
            } else if (error.response?.status === 404) {
                errorMessage = 'Watchlist not found';
            } else if (error.response?.status === 401) {
                errorMessage = 'Please log in again';
            } else if (error.response?.status >= 500) {
                errorMessage = 'Server error. Please try again later';
            } else if (error.message === 'Please select a watchlist first') {
                errorMessage = error.message;
            }

            toast.error(errorMessage);
            throw error; // Re-throw to let the modal handle it
        }
    };

    const handleRemoveSymbol = async (itemId) => {
        if (!selectedWatchlist) return;

        try {
            await watchlistAPI.removeItemFromWatchlist(selectedWatchlist.id, itemId);

            // Update the selected watchlist by removing the item
            setSelectedWatchlist(prev => ({
                ...prev,
                items: prev.items.filter(item => item.id !== itemId)
            }));

            toast.success('Symbol removed from watchlist');
        } catch (error) {
            console.error('Failed to remove symbol:', error);
            toast.error('Failed to remove symbol from watchlist');
        }
    };

    const handleReorderItems = async (itemIds) => {
        if (!selectedWatchlist) return;

        try {
            await watchlistAPI.reorderWatchlistItems(selectedWatchlist.id, itemIds);

            // Update the selected watchlist with reordered items
            const reorderedItems = itemIds.map(id =>
                selectedWatchlist.items.find(item => item.id === id)
            ).filter(Boolean);

            setSelectedWatchlist(prev => ({
                ...prev,
                items: reorderedItems
            }));
        } catch (error) {
            console.error('Failed to reorder items:', error);
            toast.error('Failed to reorder watchlist items');
        }
    };

    const handleSelectWatchlist = async (watchlist) => {
        try {
            // Load the full watchlist with items
            const fullWatchlist = await watchlistAPI.getWatchlist(watchlist.id, true);
            setSelectedWatchlist(fullWatchlist);
        } catch (error) {
            console.error('Failed to load watchlist items:', error);
            // Fallback to the basic watchlist data
            setSelectedWatchlist(watchlist);
            toast.error('Failed to load watchlist items');
        }
    };

    const handleUpdateWatchlistItem = (updatedItem) => {
        // Update the selected watchlist with the updated item
        setSelectedWatchlist(prev => ({
            ...prev,
            items: prev.items.map(item =>
                item.id === updatedItem.id ? updatedItem : item
            )
        }));
    };

    const filteredWatchlists = watchlists.filter(watchlist => {
        const matchesSearch = watchlist.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            watchlist.description?.toLowerCase().includes(searchTerm.toLowerCase());

        if (filterType === 'all') return matchesSearch;
        if (filterType === 'default') return matchesSearch && watchlist.is_default;
        if (filterType === 'public') return matchesSearch && watchlist.is_public;
        if (filterType === 'private') return matchesSearch && !watchlist.is_public;

        return matchesSearch;
    });

    if (loading) {
        return (
            <div className="min-h-screen gradient-bg flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
                    <p className="text-gray-400">Loading watchlists...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen gradient-bg flex">
            {/* Watchlist Sidebar */}
            <WatchlistSidebar
                watchlists={filteredWatchlists}
                selectedWatchlist={selectedWatchlist}
                onSelectWatchlist={handleSelectWatchlist}
                onCreateWatchlist={() => setShowCreateModal(true)}
                onUpdateWatchlist={handleUpdateWatchlist}
                onDeleteWatchlist={handleDeleteWatchlist}
                searchTerm={searchTerm}
                onSearchChange={setSearchTerm}
                filterType={filterType}
                onFilterChange={setFilterType}
            />

            {/* Main Content */}
            <div className="flex-1 flex flex-col">
                {/* Header */}
                <header className="bg-dark-900/80 backdrop-blur-sm border-b border-dark-700 px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                            <button
                                onClick={() => navigate('/dashboard')}
                                className="flex items-center space-x-2 px-3 py-2 text-gray-400 hover:text-gray-100 hover:bg-dark-800 rounded-lg transition-colors"
                            >
                                <ArrowLeft size={20} />
                                <span>Back to Dashboard</span>
                            </button>
                            <div className="w-px h-6 bg-dark-600"></div>
                            <Bookmark size={24} className="text-primary-400" />
                            <div>
                                <h1 className="text-xl font-semibold text-gray-100">Watchlists</h1>
                                <p className="text-sm text-gray-400">
                                    {selectedWatchlist ? `${selectedWatchlist.name} • ${selectedWatchlist.items?.length || 0} symbols` : 'Select a watchlist'}
                                </p>
                            </div>
                        </div>

                        <div className="flex items-center space-x-3">
                            {selectedWatchlist && (
                                <>
                                    {/* Auto-refresh toggle */}
                                    <div className="flex items-center space-x-2">
                                        <label className="flex items-center space-x-2 text-sm text-gray-400">
                                            <input
                                                type="checkbox"
                                                checked={autoRefreshEnabled}
                                                onChange={(e) => setAutoRefreshEnabled(e.target.checked)}
                                                className="rounded border-dark-600 bg-dark-800 text-primary-600 focus:ring-primary-500"
                                            />
                                            <span>Auto-refresh</span>
                                        </label>
                                        
                                        {/* Refresh interval selector */}
                                        {autoRefreshEnabled && (
                                            <select
                                                value={refreshInterval}
                                                onChange={(e) => setRefreshInterval(Number(e.target.value))}
                                                className="px-2 py-1 bg-dark-800 border border-dark-600 rounded text-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                                            >
                                                <option value={10000}>10s</option>
                                                <option value={30000}>30s</option>
                                                <option value={60000}>1m</option>
                                                <option value={300000}>5m</option>
                                            </select>
                                        )}
                                    </div>

                                    {/* Manual refresh button */}
                                    <button
                                        onClick={handleManualRefresh}
                                        disabled={isRefreshing}
                                        className="flex items-center space-x-2 px-3 py-2 bg-dark-800 hover:bg-dark-700 text-gray-300 rounded-lg transition-colors disabled:opacity-50"
                                        title="Refresh watchlist data"
                                    >
                                        <RefreshCw 
                                            size={16} 
                                            className={isRefreshing ? 'animate-spin' : ''} 
                                        />
                                        <span>{isRefreshing ? 'Refreshing...' : 'Refresh'}</span>
                                    </button>

                                    {/* Add Symbol button */}
                                    <button
                                        onClick={() => setShowAddSymbolModal(true)}
                                        className="flex items-center space-x-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
                                    >
                                        <Plus size={16} />
                                        <span>Add Symbol</span>
                                    </button>
                                </>
                            )}
                        </div>
                    </div>
                </header>

                {/* Watchlist Content */}
                <WatchlistContent
                    watchlist={selectedWatchlist}
                    onRemoveSymbol={handleRemoveSymbol}
                    onReorderItems={handleReorderItems}
                    onUpdateWatchlist={handleUpdateWatchlistItem}
                />
            </div>

            {/* Modals */}
            <CreateWatchlistModal
                isOpen={showCreateModal}
                onClose={() => setShowCreateModal(false)}
                onCreate={handleCreateWatchlist}
            />

            <AddSymbolModal
                isOpen={showAddSymbolModal}
                onClose={() => setShowAddSymbolModal(false)}
                onAdd={handleAddSymbol}
            />
        </div>
    );
};

export default Watchlist;
