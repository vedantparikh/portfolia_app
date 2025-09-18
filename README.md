# Portfolia App - Financial Portfolio Analysis Platform

A comprehensive financial portfolio analysis application built with modern technologies and the latest package versions.

## 🚀 Latest Technology Stack

### Backend (Python)
- **Python**: 3.12.2 (Latest stable)
- **FastAPI**: 0.109.2 (Latest stable)
- **Uvicorn**: 0.27.1 (Latest stable)
- **Pandas**: 2.2.0 (Latest stable)
- **NumPy**: 1.26.4 (Latest stable)
- **Technical Analysis**: ta 0.11.0 (Latest stable)
- **Yahoo Finance**: yfinance 0.2.36 (Latest stable)

### Frontend (React)
- **React**: 18.2.0 (Latest stable)
- **Node.js**: 21.7 (Latest LTS)
- **Build Tool**: Vite 7.1.3 (Latest stable)
- **Package Manager**: npm 11.5.2 (Latest stable)

### Database & Infrastructure
- **PostgreSQL**: 16.2 (Latest stable)
- **Docker**: Latest stable
- **Docker Compose**: 3.8

## 🏗️ Architecture

The application follows a microservices architecture with three main components:

1. **FastAPI Backend** (`/python/api/`)
   - RESTful API for financial data
   - Technical indicators calculation
   - Trading strategy algorithms
   - Market data integration

2. **React Frontend** (`/js/`)
   - Modern web interface
   - Real-time data updates
   - Responsive design

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.12+ (for local development)
- Node.js 21+ (for local development)

### Using Docker (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd portfolia_app/portfolio

# Start all services
docker-compose up --build

# Access the services:
# - React App: http://localhost:3000
# - FastAPI: http://localhost:8080
# - PostgreSQL: localhost:5432
```

### Local Development

#### Backend Setup
```bash
cd python/api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

#### Frontend Setup
```bash
cd js
npm install
npm run dev
```

## 📊 Features

### Market Data
- Real-time stock data from Yahoo Finance
- Historical OHLCV data
- Symbol search and validation

### Technical Indicators
- **Momentum**: RSI, ROC, Stochastic RSI, Stochastic Oscillator
- **Trend**: MACD, ADX, Aroon, Parabolic SAR, CCI
- **Volatility**: Bollinger Bands, ATR, Keltner Channels
- **Volume**: MFI, VPT, VWAP, OBV, Force Index

### Trading Strategies
- **MACD Strategy**: Trend-following with EMA confirmation
- **GFS Strategy**: Multi-timeframe RSI analysis

### Visualization
- Interactive Plotly charts
- Candlestick patterns
- Technical indicator overlays
- Real-time data updates

## 🔧 API Endpoints

### Market Data
- `GET /api/market/symbols?name={symbol}` - Search for stock symbols
- `GET /api/market/symbol-data?name={symbol}&period={period}&interval={interval}` - Get historical data

### Technical Indicators
- `GET /api/statistical-indicators/momentum-rsi-indicator` - RSI calculation
- Additional endpoints for other indicators (in development)

## 📁 Project Structure

```
portfolia_app/
├── portfolio/
│   ├── python/
│   │   ├── api/                    # FastAPI backend
│   │   │   ├── market/            # Stock data endpoints
│   │   │   ├── statistical_indicators/  # Technical indicators
│   │   │   └── trading_strategy/  # Trading algorithms
│   │   
│   ├── js/                        # React frontend (Vite)
│   ├── docker-compose.yml         # Multi-service orchestration
│   └── README.md                  # This file
```

## 🛠️ Development

### Code Quality
- **Python**: Pre-commit hooks, type hints
- **JavaScript**: ESLint configuration
- **API**: OpenAPI/Swagger documentation

### Testing
- Backend: pytest (to be implemented)
- Frontend: Vitest (to be implemented)

### Database
- PostgreSQL with SQLAlchemy ORM
- Database migrations (to be implemented)

## 🔮 Roadmap

- [ ] Complete API endpoints for all technical indicators
- [ ] User authentication and portfolio management
- [ ] Real-time data streaming
- [ ] Backtesting framework
- [ ] Mobile-responsive design
- [ ] Performance optimization
- [ ] Comprehensive test coverage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the API endpoints

---

**Note**: This project uses the latest stable versions of all packages as of January 2024. Regular updates are recommended to maintain security and performance.
