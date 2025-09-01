import {
    AlertTriangle,
    Edit3,
    GripVertical,
    MoreVertical,
    Search,
    SortAsc,
    SortDesc,
    Trash2
} from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { DragDropContext, Draggable, Droppable } from 'react-beautiful-dnd';
import { watchlistAPI } from '../../services/api';
import EditSymbolModal from './EditSymbolModal';

const WatchlistContent = ({ watchlist, onRemoveSymbol, onReorderItems }) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [sortBy, setSortBy] = useState('symbol');
    const [sortOrder, setSortOrder] = useState('asc');
    const [showEditModal, setShowEditModal] = useState(false);
    const [editingSymbol, setEditingSymbol] = useState(null);
    const [showDropdown, setShowDropdown] = useState(null);

    // Real-time data from API
    const [realTimeData, setRealTimeData] = useState({});

    useEffect(() => {
        if (watchlist?.items && watchlist.items.length > 0) {
            // Load real-time data for watchlist items
            loadRealTimeData();
        }
    }, [watchlist]);

    const loadRealTimeData = async () => {
        if (!watchlist?.id) return;
        
        try {
            const data = await watchlistAPI.getWatchlist(watchlist.id, true);
            if (data.items) {
                const priceData = {};
                data.items.forEach(item => {
                    priceData[item.symbol] = {
                        price: item.current_price?.toString() || '0.00',
                        change: item.day_change?.toString() || '0.00',
                        changePercent: item.day_change_percent?.toString() || '0.00',
                        volume: item.volume || 0,
                        marketCap: item.market_cap?.toString() || '0',
                        high: item.high?.toString() || '0.00',
                        low: item.low?.toString() || '0.00'
                    };
                });
                setRealTimeData(priceData);
            }
        } catch (error) {
            console.error('Failed to load real-time data:', error);
        }
    };

    // Refresh data periodically
    useEffect(() => {
        const interval = setInterval(() => {
            if (watchlist?.items && watchlist.items.length > 0) {
                loadRealTimeData();
            }
        }, 30000); // Refresh every 30 seconds

        return () => clearInterval(interval);
    }, [watchlist]);

    const handleEditSymbol = (symbol) => {
        setEditingSymbol(symbol);
        setShowEditModal(true);
        setShowDropdown(null);
    };

    const handleDeleteSymbol = (itemId) => {
        if (window.confirm('Are you sure you want to remove this symbol from the watchlist?')) {
            onRemoveSymbol(itemId);
        }
        setShowDropdown(null);
    };

    const handleDragEnd = (result) => {
        if (!result.destination || !watchlist?.items) return;

        const items = Array.from(watchlist.items);
        const [reorderedItem] = items.splice(result.source.index, 1);
        items.splice(result.destination.index, 0, reorderedItem);

        const itemIds = items.map(item => item.id);
        onReorderItems(itemIds);
    };

    const getSortedItems = () => {
        if (!watchlist?.items) return [];

        let items = [...watchlist.items];

        // Filter by search term
        if (searchTerm) {
            items = items.filter(item => 
                item.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
                item.company_name?.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }

        // Sort items
        items.sort((a, b) => {
            let aValue, bValue;

            switch (sortBy) {
                case 'symbol':
                    aValue = a.symbol;
                    bValue = b.symbol;
                    break;
                case 'price':
                    aValue = parseFloat(realTimeData[a.symbol]?.price || 0);
                    bValue = parseFloat(realTimeData[b.symbol]?.price || 0);
                    break;
                case 'change':
                    aValue = parseFloat(realTimeData[a.symbol]?.changePercent || 0);
                    bValue = parseFloat(realTimeData[b.symbol]?.changePercent || 0);
                    break;
                case 'volume':
                    aValue = realTimeData[a.symbol]?.volume || 0;
                    bValue = realTimeData[b.symbol]?.volume || 0;
                    break;
                default:
                    aValue = a.symbol;
                    bValue = b.symbol;
            }

            if (sortOrder === 'asc') {
                return aValue > bValue ? 1 : -1;
            } else {
                return aValue < bValue ? 1 : -1;
            }
        });

        return items;
    };

    const formatNumber = (num) => {
        if (num >= 1e9) return (num / 1e9).toFixed(1) + 'B';
        if (num >= 1e6) return (num / 1e6).toFixed(1) + 'M';
        if (num >= 1e3) return (num / 1e3).toFixed(1) + 'K';
        return num.toString();
    };

    const getChangeColor = (change) => {
        const changeNum = parseFloat(change);
        if (changeNum > 0) return 'text-success-400';
        if (changeNum < 0) return 'text-danger-400';
        return 'text-gray-400';
    };

    if (!watchlist) {
        return (
            <div className="flex-1 flex items-center justify-center">
                <div className="text-center">
                    <AlertTriangle size={48} className="mx-auto text-gray-600 mb-4" />
                    <h3 className="text-lg font-medium text-gray-300 mb-2">No Watchlist Selected</h3>
                    <p className="text-gray-400">Select a watchlist from the sidebar to view its symbols</p>
                </div>
            </div>
        );
    }

    const sortedItems = getSortedItems();

    return (
        <div className="flex-1 flex flex-col">
            {/* Toolbar */}
            <div className="p-4 border-b border-dark-700 bg-dark-900/50">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        {/* Search */}
                        <div className="relative">
                            <Search size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                            <input
                                type="text"
                                placeholder="Search symbols..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="pl-10 pr-4 py-2 bg-dark-800 border border-dark-600 rounded-lg text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent w-64"
                            />
                        </div>

                        {/* Sort */}
                        <div className="flex items-center space-x-2">
                            <select
                                value={sortBy}
                                onChange={(e) => setSortBy(e.target.value)}
                                className="px-3 py-2 bg-dark-800 border border-dark-600 rounded-lg text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                            >
                                <option value="symbol">Symbol</option>
                                <option value="price">Price</option>
                                <option value="change">Change %</option>
                                <option value="volume">Volume</option>
                            </select>
                            <button
                                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                                className="p-2 rounded-lg bg-dark-800 border border-dark-600 text-gray-400 hover:bg-dark-700 transition-colors"
                            >
                                {sortOrder === 'asc' ? <SortAsc size={16} /> : <SortDesc size={16} />}
                            </button>
                        </div>
                    </div>

                    <div className="text-sm text-gray-400">
                        {sortedItems.length} of {watchlist.items?.length || 0} symbols
                    </div>
                </div>
            </div>

            {/* Symbols Table */}
            <div className="flex-1 overflow-auto">
                {sortedItems.length === 0 ? (
                    <div className="flex items-center justify-center h-full">
                        <div className="text-center">
                            <AlertTriangle size={48} className="mx-auto text-gray-600 mb-4" />
                            <h3 className="text-lg font-medium text-gray-300 mb-2">No Symbols Found</h3>
                            <p className="text-gray-400">
                                {searchTerm ? 'Try adjusting your search terms' : 'Add some symbols to get started'}
                            </p>
                        </div>
                    </div>
                ) : (
                    <DragDropContext onDragEnd={handleDragEnd}>
                        <Droppable droppableId="watchlist-items">
                            {(provided) => (
                                <div
                                    {...provided.droppableProps}
                                    ref={provided.innerRef}
                                    className="divide-y divide-dark-700"
                                >
                                    {sortedItems.map((item, index) => {
                                        const data = realTimeData[item.symbol] || {};
                                        const isPositive = parseFloat(data.changePercent || 0) > 0;
                                        const isNegative = parseFloat(data.changePercent || 0) < 0;

                                        return (
                                            <Draggable key={item.id} draggableId={item.id.toString()} index={index}>
                                                {(provided, snapshot) => (
                                                    <div
                                                        ref={provided.innerRef}
                                                        {...provided.draggableProps}
                                                        className={`group hover:bg-dark-800/50 transition-colors ${
                                                            snapshot.isDragging ? 'bg-dark-800' : ''
                                                        }`}
                                                    >
                                                        <div className="flex items-center px-4 py-3">
                                                            {/* Drag Handle */}
                                                            <div
                                                                {...provided.dragHandleProps}
                                                                className="mr-3 text-gray-500 hover:text-gray-400 cursor-grab active:cursor-grabbing"
                                                            >
                                                                <GripVertical size={16} />
                                                            </div>

                                                            {/* Symbol Info */}
                                                            <div className="flex-1 min-w-0">
                                                                <div className="flex items-center space-x-3">
                                                                    <div>
                                                                        <h4 className="text-sm font-medium text-gray-100">
                                                                            {item.symbol}
                                                                        </h4>
                                                                        <p className="text-xs text-gray-400 truncate">
                                                                            {item.company_name || 'Unknown Company'}
                                                                        </p>
                                                                    </div>
                                                                </div>
                                                            </div>

                                                            {/* Price Data */}
                                                            <div className="flex items-center space-x-6 text-sm">
                                                                <div className="text-right">
                                                                    <div className="text-gray-100 font-medium">
                                                                        ${data.price || '0.00'}
                                                                    </div>
                                                                    <div className="text-xs text-gray-400">
                                                                        H: ${data.high || '0.00'} L: ${data.low || '0.00'}
                                                                    </div>
                                                                </div>

                                                                <div className="text-right">
                                                                    <div className={`font-medium ${getChangeColor(data.changePercent)}`}>
                                                                        {isPositive ? '+' : ''}{data.changePercent || '0.00'}%
                                                                    </div>
                                                                    <div className={`text-xs ${getChangeColor(data.change)}`}>
                                                                        {isPositive ? '+' : ''}{data.change || '0.00'}
                                                                    </div>
                                                                </div>

                                                                <div className="text-right w-20">
                                                                    <div className="text-gray-100 font-medium">
                                                                        {formatNumber(data.volume || 0)}
                                                                    </div>
                                                                    <div className="text-xs text-gray-400">
                                                                        Volume
                                                                    </div>
                                                                </div>

                                                                <div className="text-right w-20">
                                                                    <div className="text-gray-100 font-medium">
                                                                        {formatNumber(data.marketCap || 0)}
                                                                    </div>
                                                                    <div className="text-xs text-gray-400">
                                                                        Market Cap
                                                                    </div>
                                                                </div>
                                                            </div>

                                                            {/* Actions */}
                                                            <div className="relative ml-4">
                                                                <button
                                                                    onClick={() => setShowDropdown(showDropdown === item.id ? null : item.id)}
                                                                    className="p-1 rounded hover:bg-dark-600 transition-colors opacity-0 group-hover:opacity-100"
                                                                >
                                                                    <MoreVertical size={14} className="text-gray-400" />
                                                                </button>

                                                                {showDropdown === item.id && (
                                                                    <div className="absolute right-0 top-8 w-48 bg-dark-800 border border-dark-600 rounded-lg shadow-lg z-10">
                                                                        <button
                                                                            onClick={() => handleEditSymbol(item)}
                                                                            className="w-full flex items-center space-x-2 px-3 py-2 text-sm text-gray-300 hover:bg-dark-700 transition-colors"
                                                                        >
                                                                            <Edit3 size={14} />
                                                                            <span>Edit</span>
                                                                        </button>
                                                                        <button
                                                                            onClick={() => handleDeleteSymbol(item.id)}
                                                                            className="w-full flex items-center space-x-2 px-3 py-2 text-sm text-red-400 hover:bg-red-500/10 transition-colors"
                                                                        >
                                                                            <Trash2 size={14} />
                                                                            <span>Remove</span>
                                                                        </button>
                                                                    </div>
                                                                )}
                                                            </div>
                                                        </div>
                                                    </div>
                                                )}
                                            </Draggable>
                                        );
                                    })}
                                    {provided.placeholder}
                                </div>
                            )}
                        </Droppable>
                    </DragDropContext>
                )}
            </div>

            {/* Edit Symbol Modal */}
            <EditSymbolModal
                isOpen={showEditModal}
                onClose={() => {
                    setShowEditModal(false);
                    setEditingSymbol(null);
                }}
                symbol={editingSymbol}
                onUpdate={(itemId, updateData) => {
                    // Handle symbol update logic here
                    console.log('Update symbol:', itemId, updateData);
                }}
            />
        </div>
    );
};

export default WatchlistContent;
