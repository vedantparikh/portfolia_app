# Portfolia API Endpoint Structure

## Overview

The Portfolia API provides a comprehensive set of endpoints for portfolio management, market data access, and financial analytics. All endpoints follow RESTful principles and return structured JSON responses with proper HTTP status codes.

## 🏗️ API Structure

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
All endpoints (except health checks) require JWT authentication:
```http
Authorization: Bearer <jwt_token>
```

## 📊 Core Endpoint Categories

### 1. **Authentication Endpoints** - `/auth`

#### User Registration & Login
```http
POST /auth/register          # Register new user
POST /auth/login            # User login
POST /auth/logout           # User logout
POST /auth/refresh          # Refresh JWT token
```

#### Password Management
```http
POST /auth/forgot-password   # Request password reset
POST /auth/reset-password    # Reset password with token
POST /auth/change-password   # Change password (authenticated)
```

#### Email Verification
```http
POST /auth/verify-email      # Verify email with token
POST /auth/resend-verification # Resend verification email
```

### 2. **Portfolio Endpoints** - `/portfolios`

#### Portfolio Management
```http
GET    /portfolios                    # Get user portfolios
POST   /portfolios                    # Create new portfolio
GET    /portfolios/{id}               # Get specific portfolio
PUT    /portfolios/{id}               # Update portfolio
DELETE /portfolios/{id}               # Delete portfolio
```

#### Portfolio Assets
```http
GET    /portfolios/{id}/assets        # Get portfolio assets
POST   /portfolios/{id}/assets        # Add asset to portfolio
PUT    /portfolios/{id}/assets/{asset_id}  # Update portfolio asset
DELETE /portfolios/{id}/assets/{asset_id}  # Remove asset from portfolio
```

#### Portfolio Transactions
```http
GET    /portfolios/{id}/transactions  # Get portfolio transactions
POST   /portfolios/{id}/transactions  # Add new transaction
PUT    /portfolios/{id}/transactions/{tx_id}  # Update transaction
DELETE /portfolios/{id}/transactions/{tx_id}  # Delete transaction
```

#### Portfolio Analytics
```http
GET /portfolios/{id}/summary          # Portfolio summary with metrics
GET /portfolios/{id}/performance      # Performance history
GET /portfolios/{id}/holdings         # Current holdings with details
```

### 3. **Market Data Endpoints** - `/market-data`

#### Real-time Data
```http
GET /market-data/ticker/{symbol}                    # Historical data
GET /market-data/ticker/{symbol}/price              # Current price
GET /market-data/ticker/{symbol}/info               # Company information
GET /market-data/prices/bulk?symbols=AAPL,GOOGL    # Bulk prices
```

#### Market Information
```http
GET /market-data/market-status           # Market status & hours
GET /market-data/supported-periods       # Supported data periods
GET /market-data/supported-intervals     # Supported data intervals
```

### 4. **Asset Management** - `/assets`

#### Asset Operations
```http
GET    /assets                 # Search/list assets
POST   /assets                 # Create new asset
GET    /assets/{id}            # Get asset details
PUT    /assets/{id}            # Update asset
DELETE /assets/{id}            # Delete asset
GET    /assets/{id}/prices     # Get asset price history
```

#### Asset Search & Discovery
```http
GET /assets/search              # Advanced asset search
GET /assets/popular             # Popular assets
GET /assets/breakdown/sectors   # Sector breakdown
GET /assets/breakdown/types     # Asset type breakdown
GET /assets/breakdown/exchanges # Exchange breakdown
GET /assets/suggestions         # Search suggestions
```

### 5. **Watchlist Endpoints** - `/watchlists`

#### Watchlist Management
```http
GET    /watchlists                    # Get user watchlists
POST   /watchlists                    # Create watchlist
GET    /watchlists/{id}               # Get watchlist with items
PUT    /watchlists/{id}               # Update watchlist
DELETE /watchlists/{id}               # Delete watchlist
```

#### Watchlist Items
```http
POST   /watchlists/{id}/items         # Add item to watchlist
PUT    /watchlists/{id}/items/{item_id}  # Update watchlist item
DELETE /watchlists/{id}/items/{item_id}  # Remove item from watchlist
POST   /watchlists/{id}/reorder       # Reorder watchlist items
POST   /watchlists/{id}/bulk-add      # Add multiple symbols
```

#### Watchlist Features
```http
GET /watchlists/public          # Get public watchlists
GET /watchlists/stats           # Watchlist statistics
```

**Real-time Data Parameter:**
```http
GET /watchlists/{id}?include_real_time_data=true
```

### 6. **Analytics Endpoints** - `/analytics`

#### Portfolio Analytics
```http
POST /analytics/portfolios/{id}/performance/snapshot    # Create performance snapshot
POST /analytics/assets/{id}/metrics                     # Calculate asset metrics
GET  /analytics/portfolios/{id}/allocations/analysis    # Allocation analysis
POST /analytics/portfolios/{id}/risk/calculate          # Risk calculation
GET  /analytics/portfolios/{id}/performance/comparison  # Performance comparison
GET  /analytics/portfolios/{id}/summary                 # Analytics summary
```

#### Advanced Analytics
```http
GET /analytics/portfolios/{id}/allocations      # Portfolio allocations
GET /analytics/portfolios/{id}/benchmarks       # Benchmark comparisons
GET /analytics/portfolios/{id}/rebalancing      # Rebalancing recommendations
```

### 7. **Dashboard Endpoints** - `/dashboard`

#### Dashboard Data
```http
GET /dashboard/overview         # Dashboard overview
GET /dashboard/performance      # Performance metrics
GET /dashboard/alerts          # Active alerts
GET /dashboard/recent-activity # Recent activity
```

### 8. **Statistical Indicators** - `/statistical-indicators`

#### Technical Analysis
```http
GET /statistical-indicators/momentum/{symbol}     # Momentum indicators
GET /statistical-indicators/trend/{symbol}        # Trend indicators
GET /statistical-indicators/volatility/{symbol}   # Volatility indicators
GET /statistical-indicators/volume/{symbol}       # Volume indicators
```

### 9. **Transactions** - `/transactions`

#### Transaction Management
```http
GET    /transactions            # Get user transactions
POST   /transactions            # Create transaction
GET    /transactions/{id}       # Get transaction details
PUT    /transactions/{id}       # Update transaction
DELETE /transactions/{id}       # Delete transaction
```

### 10. **Health & Utility** - `/health`

#### System Health
```http
GET /health                     # API health check
GET /health/detailed            # Detailed health status
GET /health/database            # Database connectivity
GET /health/external-services   # External service status
```

## 📋 Request/Response Patterns

### Standard Request Headers
```http
Content-Type: application/json
Authorization: Bearer <jwt_token>
Accept: application/json
```

### Standard Response Format
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully",
  "timestamp": "2024-09-11T15:30:00Z"
}
```

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": { ... }
  },
  "timestamp": "2024-09-11T15:30:00Z"
}
```

### Pagination Format
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

## 🔧 Query Parameters

### Common Parameters

#### Pagination
```http
?page=1&limit=20&sort=created_at&order=desc
```

#### Filtering
```http
?start_date=2024-01-01&end_date=2024-12-31&status=active
```

#### Market Data
```http
?period=1y&interval=1d&include_dividends=true
```

#### Real-time Features
```http
?include_real_time_data=true&refresh_cache=false
```

## 📊 Response Models

### Portfolio Response
```json
{
  "id": 1,
  "name": "My Portfolio",
  "description": "Investment portfolio",
  "currency": "USD",
  "is_active": true,
  "is_public": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-09-11T15:30:00Z"
}
```

### Asset Response
```json
{
  "id": 1,
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "asset_type": "EQUITY",
  "currency": "USD",
  "exchange": "NASDAQ",
  "sector": "Technology",
  "industry": "Consumer Electronics",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Market Data Response
```json
{
  "symbol": "AAPL",
  "period": "1y",
  "interval": "1d",
  "data_points": 252,
  "data": [
    {
      "date": "2024-01-01T00:00:00Z",
      "open": 150.00,
      "high": 155.00,
      "low": 148.00,
      "close": 152.00,
      "volume": 50000000,
      "dividends": 0.0,
      "stock_splits": 0.0
    }
  ]
}
```

### Watchlist Response
```json
{
  "id": 1,
  "name": "Tech Stocks",
  "description": "Technology companies",
  "is_public": false,
  "color": "#FF5733",
  "sort_order": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-09-11T15:30:00Z",
  "item_count": 5,
  "total_gain_loss": 1250.50,
  "total_gain_loss_percent": 8.5,
  "items": [...]
}
```

## 🚀 Performance Features

### Caching
- **Market Data**: 5-minute TTL for prices, 1-hour for company info
- **Portfolio Data**: Real-time calculations with smart caching
- **User Sessions**: Redis-based session management

### Real-time Updates
- **Live Pricing**: Direct yfinance integration
- **Portfolio Valuations**: Real-time P&L calculations
- **Watchlist Updates**: Live price monitoring

### Batch Operations
- **Bulk Price Fetching**: Multiple symbols in single request
- **Batch Transactions**: Multiple transaction operations
- **Bulk Watchlist Updates**: Add multiple symbols at once

## 🔒 Security Features

### Authentication
- **JWT Tokens**: Secure token-based authentication
- **Token Refresh**: Automatic token renewal
- **Session Management**: Secure session handling

### Authorization
- **User Isolation**: Users can only access their own data
- **Portfolio Ownership**: Strict ownership validation
- **Admin Endpoints**: Separate admin-only endpoints

### Data Validation
- **Pydantic Schemas**: Runtime data validation
- **Input Sanitization**: SQL injection prevention
- **Rate Limiting**: API abuse prevention

## 📈 Analytics Features

### Portfolio Analytics
- **Performance Metrics**: Returns, volatility, Sharpe ratio
- **Risk Analysis**: VaR, beta, correlation analysis
- **Allocation Analysis**: Drift detection, rebalancing recommendations

### Technical Indicators
- **Momentum**: RSI, MACD, Stochastic
- **Trend**: Moving averages, trend lines
- **Volatility**: Bollinger bands, ATR
- **Volume**: Volume indicators, OBV

### Benchmarking
- **Index Comparison**: Compare against market indices
- **Peer Analysis**: Compare with similar portfolios
- **Custom Benchmarks**: User-defined benchmarks

## 🛠️ Development Features

### API Documentation
- **OpenAPI/Swagger**: Interactive API documentation
- **Schema Validation**: Automatic request/response validation
- **Type Safety**: Full TypeScript-like type checking

### Testing
- **Unit Tests**: Comprehensive test coverage
- **Integration Tests**: End-to-end API testing
- **Performance Tests**: Load and stress testing

### Monitoring
- **Health Checks**: System health monitoring
- **Logging**: Comprehensive request/response logging
- **Metrics**: Performance and usage metrics

## 🔄 Migration Notes

### From Previous Version
- **Removed Local Market Data**: All market data now fetched from yfinance
- **Enhanced Schemas**: All endpoints now use proper response models
- **Real-time Features**: Live data integration across all services
- **Improved Analytics**: Enhanced portfolio and risk analytics

### Breaking Changes
- **Market Data Endpoints**: Updated to use yfinance directly
- **Response Formats**: All responses now use structured schemas
- **Authentication**: Enhanced JWT token handling

This endpoint structure provides a comprehensive, modern API for portfolio management with real-time market data integration and advanced analytics capabilities.