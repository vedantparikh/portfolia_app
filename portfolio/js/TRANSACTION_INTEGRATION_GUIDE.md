# Transaction Integration Guide

## Overview

This guide explains the enhanced transaction system that integrates asset search and creation functionality. The system allows users to search for both existing assets and external market symbols, create new assets from search results, and properly reference assets in transactions.

## Key Features

### 1. Enhanced Symbol Search (`EnhancedSymbolSearch.jsx`)

The enhanced symbol search component provides:

- **Dual Search Capability**: Searches both existing user assets and external market symbols
- **Real-time Suggestions**: Shows live search results as you type
- **Asset Creation**: Allows creating new assets directly from symbol search results
- **Visual Distinction**: Clearly shows whether a result is an existing asset or a market symbol
- **Price Integration**: Fetches current prices when symbols are selected

#### Usage Example:

```jsx
<EnhancedSymbolSearch
  value={symbol}
  onChange={handleSymbolChange}
  onSelect={handleSymbolSelect}
  onPriceUpdate={handlePriceUpdate}
  placeholder="e.g., AAPL, BTC"
  showSuggestions={true}
/>
```

### 2. Updated Transaction Forms

Both `CreateTransactionModal.jsx` and `EditTransactionModal.jsx` now include:

- **Asset Validation**: Ensures proper asset selection before transaction creation
- **Asset Information Display**: Shows selected asset details
- **Proper Asset References**: Uses asset IDs instead of symbols for database references

### 3. API Integration

The system uses several API endpoints:

#### Asset Management (`assetAPI`)

- `getAssets()` - Get all assets
- `createAsset()` - Create new asset
- `searchAssets()` - Search assets by query
- `getAsset()` - Get specific asset
- `updateAsset()` - Update asset
- `deleteAsset()` - Delete asset

#### Market Data (`marketAPI`)

- `searchSymbols()` - Search external symbols
- `getCurrentPrice()` - Get current price for symbol
- `getStockLatestData()` - Get latest market data

#### Transaction Management (`transactionAPI`)

- `createTransaction()` - Create transaction with asset_id reference
- `updateTransaction()` - Update transaction
- `getTransactions()` - Get user transactions

## Data Flow

### 1. Asset Search and Selection

```
User types symbol → EnhancedSymbolSearch →
├── Search existing assets (assetAPI.searchAssets)
├── Search market symbols (marketAPI.searchSymbols)
└── Display combined results with creation options
```

### 2. Asset Creation

```
User clicks "Add" on market symbol →
assetAPI.createAsset() →
Asset created in database →
Symbol search results updated →
Asset selected for transaction
```

### 3. Transaction Creation

```
User fills form →
Validation (asset_id must be valid) →
transactionAPI.createTransaction() →
Transaction created with proper asset reference
```

## Database Schema

### Assets Table

```sql
CREATE TABLE assets (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    name VARCHAR(255) NOT NULL,
    asset_type VARCHAR(50) NOT NULL,
    exchange VARCHAR(50),
    sector VARCHAR(100),
    industry VARCHAR(100),
    country VARCHAR(100),
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Transactions Table

```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(id),
    asset_id INTEGER REFERENCES assets(id),  -- Proper foreign key reference
    transaction_type VARCHAR(20) NOT NULL,
    quantity DECIMAL(20,8) NOT NULL,
    price DECIMAL(20,8) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    transaction_date TIMESTAMP NOT NULL,
    fees DECIMAL(20,8) DEFAULT 0,
    total_amount DECIMAL(20,8),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Component Architecture

```
Transactions.jsx
├── CreateTransactionModal.jsx
│   └── EnhancedSymbolSearch.jsx
├── EditTransactionModal.jsx
│   └── EnhancedSymbolSearch.jsx
└── TransactionIntegrationTest.jsx
```

## Error Handling

The system includes comprehensive error handling:

1. **Asset Search Errors**: Graceful fallback when search fails
2. **Asset Creation Errors**: User feedback for creation failures
3. **Transaction Validation**: Prevents invalid transactions
4. **API Error Handling**: Proper error messages and fallbacks

## Testing

The `TransactionIntegrationTest.jsx` component provides comprehensive testing:

- Asset search functionality
- Symbol search from market data
- Asset creation from symbol search results
- Transaction creation with proper asset references
- Transaction retrieval and validation

## Usage Instructions

### For Developers

1. **Import the Enhanced Symbol Search**:

   ```jsx
   import { EnhancedSymbolSearch } from "../shared";
   ```

2. **Handle Asset Selection**:

   ```jsx
   const handleSymbolSelect = (suggestion) => {
     setSelectedAsset(suggestion);
     setFormData((prev) => ({
       ...prev,
       symbol: suggestion.symbol,
       asset_id: suggestion.id || suggestion.symbol,
     }));
   };
   ```

3. **Validate Asset Selection**:
   ```jsx
   if (!formData.asset_id || formData.asset_id === formData.symbol) {
     toast.error(
       "Please select an asset from the search results or create a new one"
     );
     return;
   }
   ```

### For Users

1. **Creating a Transaction**:

   - Select a portfolio
   - Type a symbol in the search field
   - Choose from existing assets or market symbols
   - If using a market symbol, click "Add" to create the asset
   - Fill in transaction details
   - Submit the transaction

2. **Editing a Transaction**:
   - Click edit on any transaction
   - Modify the symbol using the enhanced search
   - Update other transaction details
   - Save changes

## Benefits

1. **Improved User Experience**: Seamless asset search and creation
2. **Data Integrity**: Proper foreign key relationships
3. **Flexibility**: Support for both existing and new assets
4. **Real-time Data**: Live price updates and market data
5. **Comprehensive Testing**: Built-in integration tests

## Future Enhancements

1. **Bulk Asset Creation**: Create multiple assets at once
2. **Asset Categories**: Organize assets by type or sector
3. **Price Alerts**: Set up alerts for asset price changes
4. **Portfolio Integration**: Better integration with portfolio management
5. **Advanced Search**: Filter by exchange, sector, or other criteria

## Troubleshooting

### Common Issues

1. **Asset Not Found**: Ensure the symbol exists in the market data
2. **Creation Failed**: Check API permissions and data validation
3. **Transaction Error**: Verify asset_id is properly set
4. **Search Not Working**: Check API connectivity and authentication

### Debug Mode

Enable debug mode by adding `console.log` statements in the components or use the built-in integration test component to verify functionality.
