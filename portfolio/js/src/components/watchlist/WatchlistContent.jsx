import {
    AlertTriangle,
    Edit3,
    GripVertical,
    MoreVertical,
    Search,
    SortAsc,
    SortDesc,
    Trash2,
    X
} from 'lucide-react';
import React, {useState} from 'react';
import {DragDropContext, Draggable, Droppable} from 'react-beautiful-dnd';
import toast from 'react-hot-toast';
import {watchlistAPI} from '../../services/api';
import EditSymbolModal from './EditSymbolModal';

const WatchlistContent = ({watchlist, onRemoveSymbol, onReorderItems, onUpdateWatchlist}) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [sortBy, setSortBy] = useState('symbol');
    const [sortOrder, setSortOrder] = useState('asc');
    const [showEditModal, setShowEditModal] = useState(false);
    const [editingSymbol, setEditingSymbol] = useState(null);
    const [showDropdown, setShowDropdown] = useState(null);
    const [showNotesModal, setShowNotesModal] = useState(false);
    const [selectedNotes, setSelectedNotes] = useState(null);

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

    const handleUpdateSymbol = async (itemId, updateData) => {
        try {
            const updatedItem = await watchlistAPI.updateWatchlistItem(watchlist.id, itemId, updateData);
            if (onUpdateWatchlist) {
                onUpdateWatchlist(updatedItem);
            }
            toast.success('Symbol updated successfully');
        } catch (error) {
            console.error('Failed to update symbol:', error);
            const errorMessage = error.response?.data?.message || 'Failed to update symbol';
            toast.error(errorMessage);
        }
    };

    const handleShowNotes = (item) => {
        setSelectedNotes(item);
        setShowNotesModal(true);
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
        if (searchTerm) {
            items = items.filter(item =>
                item.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
                item.company_name?.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }
        items.sort((a, b) => {
            let aValue, bValue;
            switch (sortBy) {
                case 'symbol':
                    aValue = a.symbol;
                    bValue = b.symbol;
                    break;
                case 'price':
                    aValue = parseFloat(a.current_price || 0);
                    bValue = parseFloat(b.current_price || 0);
                    break;
                case 'change':
                    aValue = parseFloat(a.price_change_percent_since_added || 0);
                    bValue = parseFloat(b.price_change_percent_since_added || 0);
                    break;
                case 'added_price':
                    aValue = parseFloat(a.added_price || 0);
                    bValue = parseFloat(b.added_price || 0);
                    break;
                case 'added_date':
                    aValue = new Date(a.added_date || 0);
                    bValue = new Date(b.added_date || 0);
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

    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {month: 'short', day: 'numeric', year: 'numeric'});
    };

    const formatDateTime = (dateString) => {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'});
    };

    if (!watchlist) {
        return (
            <div className="flex-1 flex items-center justify-center">
                <div className="text-center">
                    <AlertTriangle size={48} className="mx-auto text-gray-600 mb-4"/>
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
                        <div className="relative">
                            <Search size={16}
                                    className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"/>
                            <input
                                type="text"
                                placeholder="Search symbols..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="pl-10 pr-4 py-2 bg-dark-800 border border-dark-600 rounded-lg text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent w-64"
                            />
                        </div>
                        <div className="flex items-center space-x-2">
                            <select
                                value={sortBy}
                                onChange={(e) => setSortBy(e.target.value)}
                                className="px-3 py-2 bg-dark-800 border border-dark-600 rounded-lg text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                            >
                                <option value="symbol">Symbol</option>
                                <option value="price">Current Price</option>
                                <option value="change">Change %</option>
                                <option value="added_price">Added Price</option>
                                <option value="added_date">Added Date</option>
                            </select>
                            <button
                                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                                className="p-2 rounded-lg bg-dark-800 border border-dark-600 text-gray-400 hover:bg-dark-700 transition-colors"
                            >
                                {sortOrder === 'asc' ? <SortAsc size={16}/> : <SortDesc size={16}/>}
                            </button>
                        </div>
                    </div>
                    <div className="text-sm text-gray-400">
                        {sortedItems.length} of {watchlist.items?.length || 0} symbols
                    </div>
                </div>
            </div>

            {/* Table Headers */}
            <div className="bg-dark-900/50 border-b border-dark-700 px-4 py-3">
                {/* 1. This parent flex container now justifies its direct children */}
                <div
                    className="flex items-center justify-between text-xs font-medium text-gray-400 uppercase tracking-wider">
                    {/* 2. The Symbol column is now the flexible one that will grow */}
                    <div className="flex items-center space-x-3 flex-1">
                        <div className="w-6 flex-shrink-0"></div>
                        {/* Drag handle space */}
                        <span>Symbol</span>
                    </div>
                    {/* 3. This container for the other columns NO LONGER has flex-1 */}
                    <div className="flex items-center space-x-6 text-right">
                        <div className="w-28 flex-shrink-0"><span>Added Price & Date</span></div>
                        <div className="w-28 flex-shrink-0"><span>Current Price & Last Updated</span></div>
                        <div className="w-24 flex-shrink-0"><span>Change Since Added</span></div>
                        <div className="w-20 flex-shrink-0"><span>Alerts</span></div>
                        <div className="w-24 flex-shrink-0"><span>Notes</span></div>
                        <div className="w-16 flex-shrink-0 text-center"><span>Actions</span></div>
                    </div>
                </div>
            </div>

            {/* Symbols Table */}
            <div className="flex-1 overflow-auto">
                {sortedItems.length === 0 ? (
                    <div className="flex items-center justify-center h-full">
                        <div className="text-center"><AlertTriangle size={48} className="mx-auto text-gray-600 mb-4"/>
                            <h3 className="text-lg font-medium text-gray-300 mb-2">No Symbols Found</h3><p
                                className="text-gray-400">{searchTerm ? 'Try adjusting your search terms' : 'Add some symbols to get started'}</p>
                        </div>
                    </div>
                ) : (
                    <DragDropContext onDragEnd={handleDragEnd}>
                        <Droppable droppableId="watchlist-items">
                            {(provided) => (
                                <div {...provided.droppableProps} ref={provided.innerRef}
                                     className="divide-y divide-dark-700">
                                    {sortedItems.map((item, index) => {
                                        const isPositive = parseFloat(item.price_change_percent_since_added || 0) > 0;
                                        const isNegative = parseFloat(item.price_change_percent_since_added || 0) < 0;
                                        return (
                                            <Draggable key={item.id} draggableId={item.id.toString()} index={index}>
                                                {(provided, snapshot) => (
                                                    <div ref={provided.innerRef} {...provided.draggableProps}
                                                         className={`group hover:bg-dark-800/50 transition-colors ${snapshot.isDragging ? 'bg-dark-800' : ''}`}>
                                                        {/* This parent now uses justify-between */}
                                                        <div className="flex items-center justify-between px-4 py-3">
                                                            {/* Symbol Info with Drag Handle - This is now the flexible column */}
                                                            <div className="flex items-center space-x-3 flex-1 min-w-0">
                                                                <div {...provided.dragHandleProps}
                                                                     className="text-gray-500 hover:text-gray-400 cursor-grab active:cursor-grabbing">
                                                                    <GripVertical size={16}/></div>
                                                                <div className="flex-1 min-w-0">
                                                                    <h4 className="text-sm font-medium text-gray-100">{item.symbol}</h4>
                                                                    <p className="text-xs text-gray-400 truncate">{item.company_name || 'Unknown Company'}</p>
                                                                </div>
                                                            </div>
                                                            {/* Price Data container - This NO LONGER has flex-1 */}
                                                            <div className="flex items-center space-x-6 text-sm">
                                                                <div className="text-right w-28 flex-shrink-0">
                                                                    <div
                                                                        className="text-gray-100 font-medium">${item.added_price || 'N/A'}</div>
                                                                    <div
                                                                        className="text-xs text-gray-400">Added {formatDate(item.added_date)}</div>
                                                                    <div className="text-xs text-gray-400">Added
                                                                        Days {item.days_since_added || 0}</div>
                                                                </div>
                                                                <div className="text-right w-28 flex-shrink-0">
                                                                    <div
                                                                        className="text-gray-100 font-medium">${item.current_price || '0.00'}</div>
                                                                    <div
                                                                        className="text-xs text-gray-400">Updated {formatDateTime(item.updated_at)}</div>
                                                                </div>
                                                                <div className="text-right w-24 flex-shrink-0">
                                                                    <div
                                                                        className={`font-medium ${getChangeColor(item.price_change_percent_since_added)}`}>{isPositive ? '+' : ''}{item.price_change_percent_since_added || '0.00'}%
                                                                    </div>
                                                                    <div
                                                                        className={`text-xs ${getChangeColor(item.price_change_since_added)}`}>{isPositive ? '+' : ''}{item.price_change_since_added || '0.00'}</div>
                                                                </div>
                                                                <div className="text-right w-20 flex-shrink-0">
                                                                    <div
                                                                        className="text-gray-100 font-medium">{item.alerts?.length || 0}</div>
                                                                    <div className="text-xs text-gray-400">Alerts</div>
                                                                </div>
                                                                <div className="text-right w-24 flex-shrink-0">
                                                                    <div
                                                                        className={`font-medium cursor-pointer transition-colors ${item.notes ? 'text-blue-400 hover:text-blue-300' : 'text-gray-500'}`}
                                                                        onClick={() => item.notes && handleShowNotes(item)}
                                                                        title={item.notes ? 'Click to view notes' : 'No notes'}>{item.notes ? 'Yes' : 'No'}</div>
                                                                    <div className="text-xs text-gray-400">Notes</div>
                                                                </div>
                                                                <div
                                                                    className="relative w-16 text-center flex-shrink-0">
                                                                    <button
                                                                        onClick={() => setShowDropdown(showDropdown === item.id ? null : item.id)}
                                                                        className="p-1 rounded hover:bg-dark-600 transition-colors opacity-0 group-hover:opacity-100">
                                                                        <MoreVertical size={14}
                                                                                      className="text-gray-400"/>
                                                                    </button>
                                                                    {showDropdown === item.id && (<div
                                                                        className="absolute right-0 top-8 w-48 bg-dark-800 border border-dark-600 rounded-lg shadow-lg z-10">
                                                                        <button onClick={() => handleEditSymbol(item)}
                                                                                className="w-full flex items-center space-x-2 px-3 py-2 text-sm text-gray-300 hover:bg-dark-700 transition-colors">
                                                                            <Edit3 size={14}/><span>Edit</span></button>
                                                                        <button
                                                                            onClick={() => handleDeleteSymbol(item.id)}
                                                                            className="w-full flex items-center space-x-2 px-3 py-2 text-sm text-red-400 hover:bg-red-500/10 transition-colors">
                                                                            <Trash2 size={14}/><span>Remove</span>
                                                                        </button>
                                                                    </div>)}
                                                                </div>
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

            <EditSymbolModal isOpen={showEditModal} onClose={() => {
                setShowEditModal(false);
                setEditingSymbol(null);
            }} symbol={editingSymbol} onUpdate={handleUpdateSymbol}/>

            {showNotesModal && selectedNotes && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-dark-900 border border-dark-700 rounded-lg w-full max-w-md mx-4">
                        <div className="flex items-center justify-between p-6 border-b border-dark-700"><h2
                            className="text-lg font-semibold text-gray-100">Notes for {selectedNotes.symbol}</h2>
                            <button onClick={() => {
                                setShowNotesModal(false);
                                setSelectedNotes(null);
                            }} className="p-2 rounded-lg hover:bg-dark-800 transition-colors"><X size={20}
                                                                                                 className="text-gray-400"/>
                            </button>
                        </div>
                        <div className="p-6">
                            <div className="bg-dark-800/50 border border-dark-600 rounded-lg p-4"><p
                                className="text-gray-100 whitespace-pre-wrap">{selectedNotes.notes || 'No notes available for this symbol.'}</p>
                            </div>
                            <div className="mt-4 text-center">
                                <button onClick={() => {
                                    setShowNotesModal(false);
                                    setSelectedNotes(null);
                                    setShowEditModal(true);
                                    setEditingSymbol(selectedNotes);
                                }}
                                        className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors">Edit
                                    Notes
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default WatchlistContent;