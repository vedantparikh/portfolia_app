# Portfolia - Component Documentation

## Table of Contents

1. [Authentication Components](#authentication-components)
2. [Dashboard Components](#dashboard-components)
3. [Portfolio Components](#portfolio-components)
4. [Transaction Components](#transaction-components)
5. [Asset Components](#asset-components)
6. [Watchlist Components](#watchlist-components)
7. [Shared Components](#shared-components)

## Authentication Components

### Login Component (`src/components/auth/Login.jsx`)

**Purpose**: Handles user authentication
**Key Features**:

- Username and password input fields
- Form validation using react-hook-form
- Password visibility toggle
- Remember me checkbox
- Forgot password link
- Error handling and display

**Props**: None (uses context for authentication)
**State**:

- `showPassword`: Boolean for password visibility
- Form state managed by react-hook-form

**Key Functions**:

- `onSubmit`: Handles form submission and calls login API
- `setShowPassword`: Toggles password visibility

### Register Component (`src/components/auth/Register.jsx`)

**Purpose**: Handles new user registration
**Key Features**:

- First name, last name, email, username, password fields
- Password confirmation with validation
- Terms and conditions checkbox
- Form validation with error messages
- Password strength requirements

**Props**: None (uses context for registration)
**State**:

- `showPassword`: Boolean for password visibility
- `showConfirmPassword`: Boolean for confirm password visibility
- Form state managed by react-hook-form

### ProtectedRoute Component (`src/components/auth/ProtectedRoute.jsx`)

**Purpose**: Protects routes that require authentication
**Key Features**:

- Checks if user is authenticated
- Shows loading spinner while checking
- Redirects to login if not authenticated
- Renders children if authenticated

**Props**:

- `children`: React elements to render if authenticated

**State**: Uses AuthContext for authentication state

### EmailVerification Component (`src/components/auth/EmailVerification.jsx`)

**Purpose**: Handles email verification process
**Key Features**:

- Auto-verification from URL token
- Manual token entry form
- Resend verification email
- Success/error state handling
- Automatic redirect after verification

**Props**: None (uses URL parameters and context)

## Dashboard Components

### Dashboard Component (`src/components/dashboard/Dashboard.jsx`)

**Purpose**: Main dashboard showing portfolio overview and market insights
**Key Features**:

- Portfolio performance widgets
- Market insights section
- Recent transactions
- Quick action buttons
- Responsive design for mobile/desktop

**Props**: None (fetches data from APIs)
**State**:

- `portfolios`: Array of user portfolios
- `transactions`: Array of recent transactions
- `marketInsights`: Market data and trends
- `loading`: Boolean for loading state
- `isMobile`: Boolean for responsive design

**Key Functions**:

- `loadDashboardData`: Fetches all dashboard data
- `calculateMarketStats`: Calculates market statistics
- `getTotalPortfolioValue`: Calculates total portfolio value
- `handleRefresh`: Refreshes all data

### DashboardWidget Component (`src/components/dashboard/DashboardWidget.jsx`)

**Purpose**: Reusable widget for displaying metrics
**Key Features**:

- Configurable title, value, and change percentage
- Color-coded change indicators
- Icon support
- Trend indicators
- Status indicators

**Props**:

- `title`: Widget title
- `value`: Main value to display
- `change`: Change amount
- `changePercent`: Change percentage
- `icon`: Icon component
- `color`: Color theme
- `subtitle`: Optional subtitle
- `trend`: Trend direction
- `status`: Status indicator

### MarketInsights Component (`src/components/dashboard/MarketInsights.jsx`)

**Purpose**: Displays market trends and insights
**Key Features**:

- Market sentiment analysis
- Top gainers/losers
- Market statistics
- Real-time data updates

**Props**: None (fetches market data)
**State**:

- `insights`: Market insights data
- `loading`: Loading state

### PortfolioPerformance Component (`src/components/dashboard/PortfolioPerformance.jsx`)

**Purpose**: Shows portfolio performance charts and metrics
**Key Features**:

- Performance charts
- Portfolio comparison
- Historical data
- Performance metrics

**Props**:

- `portfolios`: Array of portfolios to analyze

## Portfolio Components

### Portfolio Component (`src/components/portfolio/Portfolio.jsx`)

**Purpose**: Main portfolio management page
**Key Features**:

- Portfolio grid/list view
- Create/edit/delete portfolios
- Portfolio statistics
- Search and filtering
- Responsive design

**Props**: None (manages its own state)
**State**:

- `portfolios`: Array of portfolios
- `selectedPortfolio`: Currently selected portfolio
- `viewMode`: Grid or list view
- `loading`: Loading state
- `isMobile`: Responsive state

**Key Functions**:

- `loadPortfolios`: Fetches user portfolios
- `handleCreatePortfolio`: Creates new portfolio
- `handleUpdatePortfolio`: Updates existing portfolio
- `handleDeletePortfolio`: Deletes portfolio
- `handleEditPortfolio`: Opens edit modal

### PortfolioCard Component (`src/components/portfolio/PortfolioCard.jsx`)

**Purpose**: Individual portfolio display card
**Key Features**:

- Portfolio information display
- Performance metrics
- Action buttons (edit/delete)
- Responsive design

**Props**:

- `portfolio`: Portfolio data object
- `stats`: Portfolio statistics
- `onEdit`: Edit callback function
- `onDelete`: Delete callback function

### PortfolioChart Component (`src/components/portfolio/PortfolioChart.jsx`)

**Purpose**: Displays portfolio performance charts
**Key Features**:

- Line charts for performance
- Bar charts for allocation
- Pie charts for distribution
- Interactive tooltips
- Multiple chart types

**Props**:

- `portfolio`: Portfolio data
- `stats`: Portfolio statistics

### CreatePortfolioModal Component (`src/components/portfolio/CreatePortfolioModal.jsx`)

**Purpose**: Modal for creating new portfolios
**Key Features**:

- Form for portfolio details
- Validation
- Submit handling
- Error display

**Props**:

- `onClose`: Close callback
- `onCreate`: Create callback

### EditPortfolioModal Component (`src/components/portfolio/EditPortfolioModal.jsx`)

**Purpose**: Modal for editing existing portfolios
**Key Features**:

- Pre-filled form with existing data
- Update handling
- Validation
- Error display

**Props**:

- `isOpen`: Modal visibility
- `onClose`: Close callback
- `portfolio`: Portfolio data to edit
- `onUpdate`: Update callback

## Transaction Components

### Transactions Component (`src/components/transactions/Transactions.jsx`)

**Purpose**: Main transactions management page
**Key Features**:

- Transaction list/grid view
- Create/edit/delete transactions
- Filtering and sorting
- Search functionality
- Statistics display

**Props**: None (manages its own state)
**State**:

- `transactions`: Array of transactions
- `portfolios`: Array of portfolios
- `filters`: Filter state
- `loading`: Loading state
- `isMobile`: Responsive state

**Key Functions**:

- `loadData`: Fetches transactions and portfolios
- `filterTransactions`: Applies filters to transactions
- `handleCreateTransaction`: Creates new transaction
- `handleUpdateTransaction`: Updates existing transaction
- `handleDeleteTransaction`: Deletes transaction

### TransactionCard Component (`src/components/transactions/TransactionCard.jsx`)

**Purpose**: Individual transaction display card
**Key Features**:

- Transaction details display
- Type indicators (buy/sell)
- Status indicators
- Action buttons
- Responsive design

**Props**:

- `transaction`: Transaction data object
- `onEdit`: Edit callback function
- `onDelete`: Delete callback function

### CreateTransactionModal Component (`src/components/transactions/CreateTransactionModal.jsx`)

**Purpose**: Modal for creating new transactions
**Key Features**:

- Transaction form
- Portfolio selection
- Symbol search
- Price and quantity inputs
- Validation

**Props**:

- `portfolios`: Array of portfolios
- `onClose`: Close callback
- `onCreate`: Create callback

### EditTransactionModal Component (`src/components/transactions/EditTransactionModal.jsx`)

**Purpose**: Modal for editing existing transactions
**Key Features**:

- Pre-filled form
- Update handling
- Validation
- Error display

**Props**:

- `isOpen`: Modal visibility
- `onClose`: Close callback
- `transaction`: Transaction data to edit
- `portfolios`: Array of portfolios
- `onUpdate`: Update callback

### TransactionFilters Component (`src/components/transactions/TransactionFilters.jsx`)

**Purpose**: Filtering and sorting controls for transactions
**Key Features**:

- Portfolio filter
- Date range filter
- Transaction type filter
- Sort options
- Clear filters

**Props**:

- `filters`: Current filter state
- `portfolios`: Array of portfolios
- `onFilterChange`: Filter change callback

## Asset Components

### Assets Component (`src/components/assets/Assets.jsx`)

**Purpose**: Main assets browsing page
**Key Features**:

- Asset grid/list view
- Search functionality
- Filtering options
- Market statistics
- Asset details modal

**Props**: None (manages its own state)
**State**:

- `assets`: Array of assets
- `filteredAssets`: Filtered assets
- `searchQuery`: Search term
- `filters`: Filter state
- `viewMode`: Grid or list view
- `loading`: Loading state

**Key Functions**:

- `loadAssets`: Fetches market assets
- `filterAssets`: Applies filters and search
- `handleAssetClick`: Opens asset details modal
- `handleRefresh`: Refreshes asset data

### AssetCard Component (`src/components/assets/AssetCard.jsx`)

**Purpose**: Individual asset display card
**Key Features**:

- Asset information display
- Price and change indicators
- Market cap and volume
- Performance indicators
- Click to view details

**Props**:

- `asset`: Asset data object
- `viewMode`: Grid or list view
- `onClick`: Click callback function

### AssetModal Component (`src/components/assets/AssetModal.jsx`)

**Purpose**: Detailed asset information modal
**Key Features**:

- Comprehensive asset details
- Price history charts
- Performance metrics
- Multiple tabs (overview, chart, details)
- Real-time data updates

**Props**:

- `asset`: Asset data object
- `onClose`: Close callback function

### AssetFilters Component (`src/components/assets/AssetFilters.jsx`)

**Purpose**: Filtering controls for assets
**Key Features**:

- Category filter
- Price range filter
- Change range filter
- Sort options
- Clear filters

**Props**:

- `filters`: Current filter state
- `onFilterChange`: Filter change callback

## Watchlist Components

### Watchlist Component (`src/components/watchlist/Watchlist.jsx`)

**Purpose**: Main watchlist management page
**Key Features**:

- Watchlist sidebar
- Watchlist content area
- Create/edit/delete watchlists
- Add/remove symbols
- Real-time price updates

**Props**: None (manages its own state)
**State**:

- `watchlists`: Array of watchlists
- `selectedWatchlist`: Currently selected watchlist
- `loading`: Loading state
- `isMobile`: Responsive state

**Key Functions**:

- `loadWatchlists`: Fetches user watchlists
- `handleCreateWatchlist`: Creates new watchlist
- `handleUpdateWatchlist`: Updates existing watchlist
- `handleDeleteWatchlist`: Deletes watchlist
- `handleAddSymbol`: Adds symbol to watchlist

### WatchlistSidebar Component (`src/components/watchlist/WatchlistSidebar.jsx`)

**Purpose**: Sidebar for watchlist navigation
**Key Features**:

- Watchlist list
- Search functionality
- Filter options
- Create watchlist button
- Watchlist management

**Props**:

- `watchlists`: Array of watchlists
- `selectedWatchlist`: Currently selected watchlist
- `onSelectWatchlist`: Selection callback
- `onCreateWatchlist`: Create callback
- `onUpdateWatchlist`: Update callback
- `onDeleteWatchlist`: Delete callback

### WatchlistContent Component (`src/components/watchlist/WatchlistContent.jsx`)

**Purpose**: Main content area for watchlist items
**Key Features**:

- Symbol list with prices
- Drag and drop reordering
- Edit/delete symbols
- Real-time price updates
- Performance indicators

**Props**:

- `watchlist`: Current watchlist data
- `onRemoveSymbol`: Remove symbol callback
- `onReorderItems`: Reorder callback
- `onUpdateWatchlist`: Update callback
- `onAddSymbol`: Add symbol callback

### AddSymbolModal Component (`src/components/watchlist/AddSymbolModal.jsx`)

**Purpose**: Modal for adding symbols to watchlist
**Key Features**:

- Symbol search
- Symbol selection
- Notes and target price
- Validation
- Submit handling

**Props**:

- `isOpen`: Modal visibility
- `onClose`: Close callback
- `onAdd`: Add symbol callback

### CreateWatchlistModal Component (`src/components/watchlist/CreateWatchlistModal.jsx`)

**Purpose**: Modal for creating new watchlists
**Key Features**:

- Watchlist name and description
- Privacy settings
- Validation
- Submit handling

**Props**:

- `isOpen`: Modal visibility
- `onClose`: Close callback
- `onCreate`: Create callback

## Shared Components

### Sidebar Component (`src/components/shared/Sidebar.jsx`)

**Purpose**: Main navigation sidebar
**Key Features**:

- Navigation menu
- User profile section
- Quick actions
- Search functionality
- Responsive design

**Props**:

- `currentView`: Current active view
- `portfolios`: Array of portfolios
- `selectedPortfolio`: Currently selected portfolio
- `onPortfolioChange`: Portfolio selection callback
- `onRefresh`: Refresh callback
- `onSearch`: Search callback
- `searchQuery`: Current search term
- `showFilters`: Filter visibility state
- `onToggleFilters`: Toggle filters callback
- `stats`: Statistics data
- `recentTransactions`: Recent transactions
- `onQuickAction`: Quick action callback
- `isMobile`: Mobile state
- `isOpen`: Sidebar visibility
- `onClose`: Close callback
- `onToggleSidebar`: Toggle sidebar callback

## Component Communication Patterns

### 1. Props Down, Events Up

- Parent components pass data down via props
- Child components communicate up via callback functions
- Example: PortfolioCard receives portfolio data and edit/delete callbacks

### 2. Context for Global State

- Authentication state shared via AuthContext
- Any component can access auth state using useAuth hook
- Example: All components can check if user is logged in

### 3. API Service Pattern

- Centralized API calls in services/api.js
- Components call API methods and handle responses
- Example: portfolioAPI.getPortfolios() used by Portfolio component

### 4. Modal Pattern

- Modals are controlled by parent components
- Modal visibility managed by state
- Callbacks handle modal actions
- Example: CreatePortfolioModal controlled by Portfolio component

### 5. Form Handling Pattern

- react-hook-form for form state management
- Validation rules defined in form configuration
- Error handling and display
- Example: Login component uses form validation

## Best Practices Demonstrated

### 1. Component Organization

- Feature-based folder structure
- Consistent naming conventions
- Single responsibility principle
- Reusable components

### 2. State Management

- Local state for component-specific data
- Context for global state
- Proper state updates and immutability
- Loading and error states

### 3. Error Handling

- Try-catch blocks for API calls
- User-friendly error messages
- Fallback UI for errors
- Toast notifications for feedback

### 4. Performance

- Conditional rendering
- Proper useEffect dependencies
- Memoization where appropriate
- Lazy loading for modals

### 5. Accessibility

- Semantic HTML elements
- Proper form labels
- Keyboard navigation
- Screen reader support

### 6. Responsive Design

- Mobile-first approach
- Flexible layouts
- Touch-friendly interfaces
- Adaptive components

This component documentation provides a comprehensive overview of all components in the Portfolia application, their purposes, features, and how they work together to create a complete portfolio management system.
