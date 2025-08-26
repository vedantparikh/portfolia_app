# 🚀 Portfolia App - Local Development Startup Guide

Since Docker is not available on your system, this guide will help you run the application locally using the latest package versions.

## 📋 Prerequisites

- ✅ **Python 3.12+** (You have 3.12.1 - Perfect!)
- ✅ **Node.js 21+** (You have 21.7 - Perfect!)
- ✅ **npm 11+** (You have 11.5.2 - Perfect!)

## 🎯 Quick Start (Recommended)

### Option 1: Use the Startup Scripts (Easiest)

Open **3 separate terminal windows** and run:

**Terminal 1 - Backend API:**
```bash
./start_backend.sh
```

**Terminal 2 - Streamlit Dashboard:**
```bash
./start_streamlit.sh
```

**Terminal 3 - React Frontend:**
```bash
./start_frontend.sh
```

### Option 2: Manual Startup

**Backend API:**
```bash
cd python/api
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

**Streamlit Dashboard:**
```bash
cd python/streamlit
source venv/bin/activate
streamlit run main.py --server.port 8501 --server.address 0.0.0.0
```

**React Frontend:**
```bash
cd js
npm run dev
```

## 🌐 Access Your Services

Once all services are running, you can access:

- **🔌 FastAPI Backend**: http://localhost:8080
  - **API Documentation**: http://localhost:8080/docs
  - **Alternative Docs**: http://localhost:8080/redoc

- **📊 Streamlit Dashboard**: http://localhost:8501

- **⚛️ React Frontend**: http://localhost:3000

## 🧪 Test the Setup

### 1. Test FastAPI Backend
```bash
curl http://localhost:8080/api/market/symbols?name=AAPL
```

### 2. Test Streamlit Dashboard
- Open http://localhost:8501 in your browser
- Search for a stock symbol (e.g., "AAPL")
- View the interactive charts and indicators

### 3. Test React Frontend
- Open http://localhost:3000 in your browser
- You should see the React app (currently a template)

## 🔧 Troubleshooting

### Common Issues:

**Port Already in Use:**
```bash
# Find what's using the port
lsof -i :8080  # For backend
lsof -i :8501  # For Streamlit
lsof -i :3000  # For React

# Kill the process
kill -9 <PID>
```

**Python Virtual Environment Issues:**
```bash
# Recreate virtual environment
cd python/api
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Node.js Issues:**
```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
cd js
rm -rf node_modules package-lock.json
npm install
```

## 📱 Development Workflow

1. **Backend Changes**: FastAPI will auto-reload when you modify Python files
2. **Streamlit Changes**: Dashboard will auto-reload when you modify Python files
3. **Frontend Changes**: React will hot-reload when you modify JavaScript/JSX files

## 🎨 Available Features

### Backend API
- ✅ Stock symbol search
- ✅ Historical stock data
- ✅ Technical indicators (RSI, MACD, Bollinger Bands, etc.)
- ✅ Trading strategies (MACD, GFS)

### Streamlit Dashboard
- ✅ Interactive stock charts
- ✅ Real-time technical analysis
- ✅ Multi-timeframe RSI analysis
- ✅ Beautiful Plotly visualizations

### React Frontend
- ✅ Modern React 18 with hooks
- ✅ Vite build system (10x faster than CRA)
- ✅ ESLint configuration
- ✅ Ready for API integration

## 🚀 Next Steps

1. **Explore the API**: Visit http://localhost:8080/docs
2. **Try the Dashboard**: Search for stocks in Streamlit
3. **Develop Frontend**: Start building React components
4. **Add Features**: Implement new technical indicators
5. **Database Integration**: Add PostgreSQL when ready

## 📞 Need Help?

- Check the main README.md for project overview
- Review the API documentation at /docs
- Check terminal output for error messages
- Ensure all virtual environments are activated

---

**Happy Coding! 🎉**

Your Portfolia App is now running with the latest technology stack!
