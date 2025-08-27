# Market Data Service

## Overview

The Market Data Service is a robust, reliable system for fetching, storing, and serving financial market data. It addresses the reliability issues with external APIs like yfinance by implementing a local data store with automatic fallback mechanisms.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Market Data   │    │   Data Service   │    │   Main API      │
│   Service       │    │   (Scheduler)    │    │                 │
│                 │    │                  │    │                 │
│ • Fetches data  │◄──►│ • Daily updates  │◄──►│ • Serves data   │
│ • Stores in DB  │    │ • Fallback logic │    │ • Uses local    │
│ • Handles errors│    │ • Data validation│    │   data first    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Key Features

### 1. **Reliable Data Fetching**
- **Retry Logic**: Automatic retry with exponential backoff
- **Multiple Data Sources**: yfinance as primary, local database as fallback
- **Error Handling**: Graceful degradation when external APIs fail

### 2. **Local Data Storage**
- **Daily Market Data**: OHLCV data stored locally
- **Ticker Information**: Company details and metadata
- **Data Logging**: Complete audit trail of all operations

### 3. **Automatic Updates**
- **Scheduled Updates**: Daily updates at market close + 2 hours
- **Batch Processing**: Efficient processing of multiple tickers
- **Failed Update Retry**: Automatic retry of failed updates every 6 hours

### 4. **Smart Fallback System**
- **Fresh Data Priority**: Always try to get latest data first
- **Local Data Backup**: Serve stored data when external APIs fail
- **Data Quality Monitoring**: Track data freshness and reliability

## Database Schema

### TickerInfo Table
```sql
CREATE TABLE ticker_info (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255),
    company_name VARCHAR(500),
    sector VARCHAR(100),
    industry VARCHAR(100),
    exchange VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### MarketData Table
```sql
CREATE TABLE market_data (
    id SERIAL PRIMARY KEY,
    ticker_id INTEGER REFERENCES ticker_info(id),
    date DATE NOT NULL,
    open_price DECIMAL NOT NULL,
    high_price DECIMAL NOT NULL,
    low_price DECIMAL NOT NULL,
    close_price DECIMAL NOT NULL,
    volume INTEGER NOT NULL,
    adjusted_close DECIMAL NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(ticker_id, date)
);
```

### DataUpdateLog Table
```sql
CREATE TABLE data_update_log (
    id SERIAL PRIMARY KEY,
    ticker_symbol VARCHAR(20) NOT NULL,
    operation VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    records_processed INTEGER DEFAULT 0,
    error_message VARCHAR(1000),
    execution_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## API Endpoints

### Market Data Endpoints

#### 1. **Get Ticker Data with Fallback**
```http
GET /api/v1/market-data/ticker/{symbol}
```
- **Description**: Get market data with automatic fallback to local data
- **Parameters**:
  - `symbol`: Stock symbol (e.g., AAPL)
  - `period`: Data period (1y, 2y, max, etc.)
  - `interval`: Data interval (1d, 1h, etc.)
  - `use_fallback`: Enable/disable fallback (default: true)

#### 2. **Get Local Ticker Data**
```http
GET /api/v1/market-data/ticker/{symbol}/local
```
- **Description**: Get data from local database only
- **Parameters**:
  - `symbol`: Stock symbol
  - `start_date`: Start date for range
  - `end_date`: End date for range
  - `limit`: Maximum records to return

#### 3. **Update Ticker Data**
```http
POST /api/v1/market-data/ticker/{symbol}/update
```
- **Description**: Manually update data for a specific ticker
- **Parameters**:
  - `symbol`: Stock symbol
  - `force_update`: Force update even if data is recent

#### 4. **Get Data Quality Info**
```http
GET /api/v1/market-data/ticker/{symbol}/quality
```
- **Description**: Get information about data freshness and quality

#### 5. **Update All Tickers**
```http
POST /api/v1/market-data/update/all
```
- **Description**: Update data for all active tickers
- **Parameters**:
  - `tickers`: Optional list of specific tickers

#### 6. **Get Active Tickers**
```http
GET /api/v1/market-data/tickers/active
```
- **Description**: Get list of all active tickers

#### 7. **Get Service Status**
```http
GET /api/v1/market-data/status
```
- **Description**: Get service health and recent operations

#### 8. **Scheduler Control**
```http
POST /api/v1/market-data/scheduler/start
POST /api/v1/market-data/scheduler/stop
```
- **Description**: Start/stop the automatic data scheduler

### Stock Endpoints (Updated)

#### 1. **Get Stock Data with Fallback**
```http
GET /api/v1/stock/symbol-data
```
- **Description**: Get stock data using the new fallback service
- **Parameters**:
  - `name`: Stock symbol
  - `period`: Data period
  - `interval`: Data interval
  - `use_fallback`: Enable fallback (default: true)

#### 2. **Get Local Stock Data**
```http
GET /api/v1/stock/symbol-data/local
```
- **Description**: Get stock data from local database only

## Configuration

### Environment Variables
```bash
# Database
POSTGRES_DB=portfolia
POSTGRES_USER=portfolia_user
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# API Settings
API_PORT=8000
DEBUG=True
```

### Scheduler Configuration
```python
class DataScheduler:
    def __init__(self):
        self.update_interval_hours = 24      # Daily updates
        self.batch_size = 10                 # Process 10 tickers at once
        self.retry_failed_after_hours = 6    # Retry failed updates every 6 hours
```

## Usage Examples

### 1. **Basic Data Retrieval**
```python
from services.market_data_service import market_data_service

# Get data with fallback
data = await market_data_service.get_data_with_fallback("AAPL", "1y", "1d")

# Get local data only
local_data = await market_data_service.get_market_data("AAPL")
```

### 2. **Manual Updates**
```python
from services.data_scheduler import data_scheduler

# Update specific tickers
results = await data_scheduler.manual_update(["AAPL", "GOOGL", "MSFT"])

# Update all tickers
all_results = await data_scheduler.manual_update()
```

### 3. **Data Quality Monitoring**
```python
# Check data freshness
quality = await market_data_service.get_data_quality_info("AAPL")
print(f"Data age: {quality['data_age_days']} days")
print(f"Is fresh: {quality['is_fresh']}")
```

## Deployment

### Docker Compose
```yaml
data-service:
  build: 
    context: ./python/api
    dockerfile: Dockerfile
  command: ["python", "start_data_service.py"]
  depends_on:
    postgres:
      condition: service_healthy
    redis:
      condition: service_healthy
  volumes:
    - ./python/api/app:/app/app:delegated
    - ./python/api/models:/app/models:delegated
    - ./python/api/services:/app/services:delegated
```

### Standalone Service
```bash
# Start the data service
python start_data_service.py

# Or as a background process
nohup python start_data_service.py > data_service.log 2>&1 &
```

## Monitoring and Logging

### Log Levels
- **INFO**: Normal operations, successful updates
- **WARNING**: Non-critical issues, retries
- **ERROR**: Failed operations, database errors

### Key Metrics
- **Update Success Rate**: Percentage of successful updates
- **Data Freshness**: Age of latest data for each ticker
- **API Response Times**: Performance of external API calls
- **Error Rates**: Frequency of different types of failures

### Health Checks
- **Database Connectivity**: PostgreSQL connection status
- **Service Status**: Scheduler running state
- **Data Quality**: Freshness of stored data
- **Recent Operations**: Last 24 hours of activity

## Troubleshooting

### Common Issues

#### 1. **External API Failures**
- **Symptom**: High error rates in update logs
- **Solution**: Check network connectivity, API rate limits
- **Fallback**: Service automatically uses local data

#### 2. **Database Connection Issues**
- **Symptom**: Service fails to start or update
- **Solution**: Verify PostgreSQL is running, check credentials
- **Monitoring**: Health checks will detect connection issues

#### 3. **Data Staleness**
- **Symptom**: Old data being served
- **Solution**: Check scheduler status, manually trigger updates
- **Prevention**: Monitor data quality endpoints

### Debug Commands
```bash
# Check service status
curl http://localhost:8000/api/v1/market-data/status

# Check data quality for a ticker
curl http://localhost:8000/api/v1/market-data/ticker/AAPL/quality

# Manually trigger update
curl -X POST "http://localhost:8000/api/v1/market-data/ticker/AAPL/update"

# View recent logs
docker logs data-service --tail 100
```

## Performance Considerations

### 1. **Batch Processing**
- Process multiple tickers simultaneously
- Configurable batch size for optimal performance
- Rate limiting to avoid overwhelming external APIs

### 2. **Database Optimization**
- Indexed queries for fast data retrieval
- Composite indexes for common query patterns
- Efficient upsert operations for data updates

### 3. **Caching Strategy**
- Redis for session and temporary data
- Local database for persistent market data
- Smart fallback to minimize external API calls

## Future Enhancements

### 1. **Additional Data Sources**
- Alpha Vantage API integration
- IEX Cloud data feeds
- Polygon.io real-time data

### 2. **Advanced Analytics**
- Technical indicators calculation
- Pattern recognition algorithms
- Risk assessment metrics

### 3. **Real-time Updates**
- WebSocket connections for live data
- Push notifications for price alerts
- Streaming data processing

### 4. **Machine Learning**
- Predictive models for price movements
- Anomaly detection in market data
- Automated trading signals

## Conclusion

The Market Data Service provides a robust, reliable foundation for financial data operations. By implementing local storage with intelligent fallback mechanisms, it ensures data availability even when external APIs are unreliable. The automatic scheduling and monitoring capabilities make it suitable for production environments requiring consistent market data access.
