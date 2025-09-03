# Watchlist Feature

A comprehensive watchlist management system inspired by TradingView, providing full CRUD operations for watchlists and watchlist items.

## Features

### Watchlist Management

- ✅ Create new watchlists with custom names, descriptions, and colors
- ✅ Edit existing watchlists (name, description, color, privacy settings)
- ✅ Delete watchlists with confirmation
- ✅ Set default watchlist
- ✅ Public/private watchlist visibility
- ✅ Search and filter watchlists
- ✅ Color-coded watchlists for easy identification

### Symbol Management

- ✅ Add symbols to watchlists with autocomplete suggestions
- ✅ Remove symbols from watchlists
- ✅ Edit symbol details (notes, price alerts)
- ✅ Drag and drop reordering of symbols
- ✅ Search and sort symbols within watchlists
- ✅ Real-time price data simulation (mock data)

### Price Alerts

- ✅ Set high and low price alerts for symbols
- ✅ Visual indicators for alert status
- ✅ Alert notifications (email and in-app)

### UI/UX Features

- ✅ TradingView-inspired dark theme
- ✅ Responsive design for desktop and mobile
- ✅ Real-time data updates
- ✅ Drag and drop functionality
- ✅ Modal dialogs for all operations
- ✅ Toast notifications for user feedback
- ✅ Loading states and error handling

## Components

### Main Components

- `Watchlist.jsx` - Main container component
- `WatchlistSidebar.jsx` - Sidebar with watchlist list and management
- `WatchlistContent.jsx` - Main content area with symbol table

### Modal Components

- `CreateWatchlistModal.jsx` - Create new watchlists
- `EditWatchlistModal.jsx` - Edit existing watchlists
- `AddSymbolModal.jsx` - Add symbols to watchlists
- `EditSymbolModal.jsx` - Edit symbol details and alerts

## API Integration

The watchlist feature integrates with the backend API through the `watchlistAPI` service:

```javascript
import { watchlistAPI } from "../../services/api";

// Get all watchlists
const watchlists = await watchlistAPI.getWatchlists();

// Create new watchlist
const newWatchlist = await watchlistAPI.createWatchlist({
  name: "My Watchlist",
  description: "Description",
  is_default: false,
  is_public: false,
  color: "#3B82F6",
});

// Add symbol to watchlist
const newItem = await watchlistAPI.addItemToWatchlist(watchlistId, {
  symbol: "AAPL",
});
```

## Usage

1. **Access Watchlist**: Navigate to `/watchlist` in the application
2. **Create Watchlist**: Click the "+" button in the sidebar
3. **Add Symbols**: Select a watchlist and click "Add Symbol"
4. **Manage Symbols**: Use the dropdown menu on each symbol for edit/remove options
5. **Reorder Symbols**: Drag and drop symbols to reorder them
6. **Set Alerts**: Edit a symbol to set price alerts

## Styling

The watchlist uses Tailwind CSS with a custom dark theme that matches the TradingView aesthetic:

- Dark backgrounds (`bg-dark-900`, `bg-dark-800`)
- Primary accent colors (`text-primary-400`, `bg-primary-600`)
- Success/danger colors for price changes
- Consistent spacing and typography

## Dependencies

- `react-beautiful-dnd` - Drag and drop functionality
- `lucide-react` - Icons
- `react-hot-toast` - Toast notifications
- `axios` - API calls

## Future Enhancements

- Real-time WebSocket integration for live price data
- Chart integration for symbol analysis
- Bulk import/export of watchlists
- Advanced filtering and sorting options
- Watchlist sharing and collaboration
- Mobile-optimized touch interactions
