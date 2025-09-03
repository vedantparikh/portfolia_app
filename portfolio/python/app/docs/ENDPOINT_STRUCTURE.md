# Stock Data Endpoint Structure

## Overview

The Portfolia API now provides **three distinct endpoints** for retrieving stock data, giving users clear control over data sources and performance characteristics.

## Endpoint Comparison

### 1. **Fresh Data Endpoint** - `/api/v1/stock/symbol-data/fresh`

- **Purpose**: Fetch live, real-time data from yfinance API
- **Data Source**: External yfinance API
- **Response Time**: Slower (depends on external API)
- **Data Freshness**: Always current
- **Use Case**: When you need the most up-to-date market information
- **Storage**: Automatically stores fresh data locally for future use

**Example Request:**

```bash
GET /api/v1/stock/symbol-data/fresh?name=AAPL&period=max&interval=1d
```

**Response:**

```json
{
  "symbol": "AAPL",
  "period": "max",
  "interval": "1d",
  "source": "yfinance_fresh",
  "data_points": 1250,
  "data": [...]
}
```

### 2. **Local Data Endpoint** - `/api/v1/stock/symbol-data/local`

- **Purpose**: Retrieve data from local database only
- **Data Source**: Local PostgreSQL database
- **Response Time**: Fast (no external API calls)
- **Data Freshness**: Depends on last update (may be hours/days old)
- **Use Case**: When you need fast responses and can tolerate slightly older data
- **Storage**: No external API calls, no data updates

**Example Request:**

```bash
GET /api/v1/stock/symbol-data/local?name=AAPL&start_date=2024-01-01&end_date=2024-12-31&limit=100
```

**Response:**

```json
{
  "symbol": "AAPL",
  "source": "local_database",
  "data_points": 100,
  "data": [...]
}
```

### 3. **Intelligent Endpoint** - `/api/v1/stock/symbol-data`

- **Purpose**: Smart data source selection based on data freshness
- **Data Source**: Intelligent choice between local and external
- **Response Time**: Variable (fast for fresh local data, slower for stale data)
- **Data Freshness**: Optimized for best user experience
- **Use Case**: Default choice for most applications
- **Storage**: Automatically updates local data when needed

**Logic:**

1. If local data is fresh (< 24 hours old) → Return local data (fast)
2. If local data is stale → Fetch fresh data from yfinance
3. If yfinance fails → Fall back to local data (even if stale)
4. Always store fresh data locally for future use

**Example Request:**

```bash
GET /api/v1/stock/symbol-data?name=AAPL&period=max&interval=1d
```

**Response Examples:**

**Fresh Local Data:**

```json
{
  "symbol": "AAPL",
  "period": "max",
  "interval": "1d",
  "source": "local_database_fresh",
  "data_points": 1250,
  "data": [...],
  "data_age_hours": 2
}
```

**Fresh External Data:**

```json
{
  "symbol": "AAPL",
  "period": "max",
  "interval": "1d",
  "source": "yfinance_fresh",
  "data_points": 1250,
  "data": [...]
}
```

**Stale Local Data (Fallback):**

```json
{
  "symbol": "AAPL",
  "period": "max",
  "interval": "1d",
  "source": "local_database_stale",
  "data_points": 1250,
  "data": [...],
  "data_age_hours": 48,
  "warning": "Using stale local data - fresh data unavailable"
}
```

## Market Data Router Endpoints

The market data router also provides similar endpoints for consistency:

- **`/api/v1/market-data/ticker/{symbol}/fresh`** - Fresh yfinance data
- **`/api/v1/market-data/ticker/{symbol}/local`** - Local database data
- **`/api/v1/market-data/ticker/{symbol}`** - Intelligent selection

## When to Use Each Endpoint

### Use **Fresh Data Endpoint** when:

- You need real-time market information
- Building trading applications
- Data freshness is critical
- You can tolerate longer response times

### Use **Local Data Endpoint** when:

- You need fast response times
- Building dashboards or analytics
- Data freshness is not critical
- You want to avoid external API rate limits

### Use **Intelligent Endpoint** when:

- You want the best of both worlds
- Building general-purpose applications
- You're unsure which endpoint to use
- You want automatic optimization

## Performance Characteristics

| Endpoint    | Response Time       | Data Freshness        | External API Calls | Local Storage       |
| ----------- | ------------------- | --------------------- | ------------------ | ------------------- |
| `/fresh`    | Slow (2-5s)         | Always current        | Yes                | Updates local DB    |
| `/local`    | Fast (<100ms)       | Variable (hours/days) | No                 | No updates          |
| `/` (smart) | Variable (100ms-5s) | Optimized             | Conditional        | Updates when needed |

## Error Handling

All endpoints provide consistent error handling:

- **404**: No data available for the symbol
- **500**: Internal server error
- **400**: Invalid parameters (dates, etc.)

## Data Storage Strategy

- **Fresh data** is automatically stored locally for future use
- **Local data** serves as a reliable fallback
- **Data quality** is continuously monitored
- **Automatic updates** run daily to keep local data fresh

## Best Practices

1. **For real-time trading**: Use `/fresh` endpoints
2. **For dashboards**: Use `/local` endpoints
3. **For general applications**: Use the intelligent endpoints
4. **Monitor data age**: Check the `data_age_hours` field
5. **Handle warnings**: Check for `warning` fields in responses

## Migration from Old Endpoints

If you were using the old fallback endpoints:

- **Old behavior**: Automatic fallback with single endpoint
- **New behavior**: Explicit endpoint selection with intelligent defaults
- **Backward compatibility**: The main endpoints still provide fallback logic
- **Performance improvement**: Faster responses when fresh local data is available
