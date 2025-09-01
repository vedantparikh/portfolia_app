import { ArrowLeft, Bookmark, Plus } from 'lucide-react';
import React, { useEffect, useState } from 'react';
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

    // Load watchlists on component mount
    useEffect(() => {
        loadWatchlists();
    }, []);

    const loadWatchlists = async () => {
        try {
            setLoading(true);
            const data = await watchlistAPI.getWatchlists(true);
            setWatchlists(data);
            
            // Select the first watchlist or default watchlist
            if (data.length > 0) {
                const defaultWatchlist = data.find(w => w.is_default) || data[0];
                setSelectedWatchlist(defaultWatchlist);
            }
        } catch (error) {
            console.error('Failed to load watchlists:', error);
            console.error('Error details:', error.response?.data);
            toast.error('Failed to load watchlists');
        } finally {
            setLoading(false);
        }
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

    const handleAddSymbol = async (symbol) => {
        if (!selectedWatchlist) {
            const error = new Error('Please select a watchlist first');
            throw error;
        }

        try {
            const newItem = await watchlistAPI.addItemToWatchlist(selectedWatchlist.id, { symbol });
            
            // Update the selected watchlist with the new item
            setSelectedWatchlist(prev => ({
                ...prev,
                items: [...(prev.items || []), newItem]
            }));
            
            setShowAddSymbolModal(false);
            toast.success(`${symbol} added to watchlist`);
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
                onSelectWatchlist={setSelectedWatchlist}
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
                                <button
                                    onClick={() => setShowAddSymbolModal(true)}
                                    className="flex items-center space-x-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
                                >
                                    <Plus size={16} />
                                    <span>Add Symbol</span>
                                </button>
                            )}
                        </div>
                    </div>
                </header>

                {/* Watchlist Content */}
                <WatchlistContent
                    watchlist={selectedWatchlist}
                    onRemoveSymbol={handleRemoveSymbol}
                    onReorderItems={handleReorderItems}
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
