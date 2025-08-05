# 🚀 Crypto Futures Price Fetcher - Full Stack Application

A comprehensive real-time cryptocurrency futures price monitoring and arbitrage detection system with a modern web interface, inspired by CoinGlass's design.

## 📋 Project Overview

This full-stack application combines a Python-based price fetching engine with a modern React/Next.js frontend, connected through a FastAPI backend with WebSocket support for real-time data streaming.

### 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │  Price Engine   │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (Python)      │
│                 │    │                 │    │                 │
│ • React/TS      │    │ • REST APIs     │    │ • WebSocket     │
│ • Tailwind CSS  │    │ • WebSocket Hub │    │ • Multi-Exchange│
│ • Real-time UI  │    │ • Data Relay    │    │ • Arbitrage     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
  localhost:3000          localhost:8000           Price Feeds
```

## 🌟 Features

### 🔄 Real-Time Data Processing
- **Multi-Exchange Integration**: Binance Futures, Bybit, OKX
- **WebSocket Connections**: Sub-second price updates
- **Automatic Reconnection**: Robust connection management
- **Data Validation**: Price data integrity checks

### 💹 Arbitrage Detection
- **Real-Time Analysis**: Instant spread calculations
- **Profit Estimation**: Percentage-based opportunity ranking
- **Risk Assessment**: Low/Medium/High risk categorization
- **Alert System**: Push notifications for high-profit opportunities

### 🖥️ Modern Web Interface
- **Responsive Design**: Desktop and mobile optimized
- **Dark Theme**: Professional trading interface
- **Real-Time Updates**: Live price feeds without page refresh
- **Interactive Tables**: Sortable, filterable data presentation
- **Connection Monitoring**: Visual WebSocket status indicators

### 📊 Data Management
- **In-Memory Storage**: Optimized for high-frequency updates
- **Stale Data Cleanup**: Automatic removal of outdated prices
- **Event-Driven Architecture**: Publisher-subscriber pattern
- **RESTful APIs**: Standard HTTP endpoints for data access

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Internet connection** for exchange WebSocket feeds

### 1. Start the Price Engine & Backend
```bash
# Make script executable (first time only)
chmod +x start_backend.sh

# Start backend with price fetching
./start_backend.sh
```

This will:
- Install Python dependencies
- Start the price fetching engine
- Launch FastAPI backend on http://localhost:8000
- Begin collecting real-time price data

### 2. Start the Frontend
```bash
# In a new terminal
chmod +x start_frontend.sh
./start_frontend.sh
```

This will:
- Install Node.js dependencies
- Start Next.js development server on http://localhost:3000
- Open the dashboard in your browser

### 3. Access the Application
- **Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📁 Project Structure

```
crypto-futures-price-fetcher/
├── 🐍 Python Price Engine
│   ├── main.py                 # Main application
│   ├── src/
│   │   ├── price_manager.py    # Price storage & arbitrage
│   │   ├── exchanges/          # Exchange connectors
│   │   │   ├── base_exchange.py
│   │   │   ├── binance_exchange.py
│   │   │   ├── bybit_exchange.py
│   │   │   └── okx_exchange.py
│   │   └── utils/
│   │       └── input_parser.py # File parsing
│   └── requirements.txt
│
├── 🌐 FastAPI Backend
│   ├── main.py                 # FastAPI server
│   ├── requirements.txt
│   └── __init__.py
│
├── ⚛️ React Frontend
│   ├── components/
│   │   ├── Dashboard.tsx       # Main dashboard
│   │   ├── PriceTable.tsx      # Price monitoring
│   │   ├── ArbitrageTable.tsx  # Arbitrage opportunities
│   │   ├── ConnectionStatus.tsx # WebSocket status
│   │   └── MarketOverview.tsx  # Market statistics
│   ├── lib/
│   │   ├── api.ts             # REST API client
│   │   └── websocket.ts       # WebSocket client
│   ├── pages/
│   │   ├── _app.tsx           # App wrapper
│   │   └── index.tsx          # Home page
│   ├── styles/
│   │   └── globals.css        # Tailwind styles
│   ├── types/
│   │   └── index.ts           # TypeScript definitions
│   └── package.json
│
├── 📄 Configuration & Data
│   ├── symbols.csv            # Default symbol list
│   ├── examples/              # Sample input files
│   ├── start_backend.sh       # Backend startup script
│   ├── start_frontend.sh      # Frontend startup script
│   └── validate.py            # System validation
│
└── 📚 Documentation
    ├── README.md              # Python engine docs
    ├── FRONTEND_README.md     # Frontend docs
    └── FULL_STACK_README.md   # This file
```

## 🔧 Configuration

### Symbol Configuration
Edit `symbols.csv` to customize which symbols to track:
```csv
exchange,symbol
binance,BTCUSDT
binance,ETHUSDT
bybit,BTCUSDT
okx,BTC-USDT
```

### Backend Configuration
Backend settings in `backend/main.py`:
- **WebSocket URL**: Change API endpoints
- **CORS Settings**: Configure allowed origins
- **Price Update Intervals**: Adjust refresh rates

### Frontend Configuration
Frontend settings in `frontend/next.config.js`:
- **API URLs**: Backend endpoint configuration
- **Proxy Settings**: API request routing

## 📡 API Reference

### REST Endpoints

#### Market Data
```http
GET /api/prices                    # Get all current prices
GET /api/prices/{symbol}           # Get prices for specific symbol
GET /api/summary                   # Get market summary statistics
GET /api/best-prices/{symbol}      # Get best bid/ask across exchanges
```

#### Arbitrage
```http
GET /api/arbitrage                 # Get all arbitrage opportunities
GET /api/arbitrage/{symbol}        # Get opportunities for specific symbol
GET /api/spread/{symbol}/{ex1}/{ex2} # Get spread between two exchanges
```

#### System
```http
GET /health                        # Health check and system status
```

### WebSocket Events

#### Client → Server
```javascript
// Connection established automatically
// Send any message for echo (debugging)
websocket.send("ping");
```

#### Server → Client
```javascript
// Market data updates
{
  "type": "price_update",
  "data": {
    "symbol": "BTCUSDT",
    "exchange": "binance", 
    "price": 50000.0,
    "bid": 49999.0,
    "ask": 50001.0,
    "timestamp": 1234567890
  }
}

// Arbitrage opportunities
{
  "type": "arbitrage_opportunities",
  "data": [
    {
      "symbol": "BTCUSDT",
      "buy_exchange": "binance",
      "sell_exchange": "bybit",
      "profit": 1.25
    }
  ]
}

// Market summary
{
  "type": "market_summary", 
  "data": {
    "total_symbols": 4,
    "total_exchanges": 3,
    "price_count": 12
  }
}
```

## 🎨 User Interface

### Dashboard Components

#### 📊 Market Overview
- **Symbol Count**: Number of tracked symbols
- **Exchange Status**: Connected exchanges with live indicators  
- **Arbitrage Alerts**: Active opportunities count
- **Best Profit**: Highest spread percentage

#### 💰 Price Monitor
- **Real-Time Prices**: Live price feeds from all exchanges
- **Bid/Ask Spreads**: Order book depth information
- **Search & Filter**: Find specific symbols or exchanges
- **Price Change**: Visual indicators for price movements

#### 🎯 Arbitrage Opportunities
- **Profit Ranking**: Sorted by potential profit percentage
- **Exchange Pairs**: Buy/sell exchange combinations
- **Risk Assessment**: Opportunity risk categorization
- **Real-Time Updates**: Instant opportunity detection

#### 🔗 Connection Status
- **WebSocket Status**: Live connection monitoring
- **Reconnection**: Automatic reconnection attempts
- **Error Handling**: Connection error notifications
- **Last Update**: Timestamp of latest data

### Design System

#### Color Palette
- **Primary Blue**: `#3b82f6` - Interactive elements
- **Success Green**: `#22c55e` - Profits, positive changes
- **Danger Red**: `#ef4444` - Losses, negative changes  
- **Warning Yellow**: `#eab308` - Alerts, moderate risks
- **Dark Theme**: Professional trading interface

#### Typography
- **Headings**: Inter font family
- **Monospace**: Prices and numerical data
- **Body Text**: System font stack

## 🚀 Deployment

### Production Deployment

#### Backend (FastAPI)
```bash
# Install production dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Start with production server
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Frontend (Next.js)
```bash
cd frontend
npm install
npm run build
npm start
```

#### Docker Deployment
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - NODE_ENV=production
      
  frontend:
    build: ./frontend  
    ports:
      - "3000:3000"
    depends_on:
      - backend
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
```

### Environment Variables

#### Backend
```bash
# Price fetcher settings
SYMBOLS_FILE=symbols.csv
RECONNECT_INTERVAL=5000
MAX_RECONNECT_ATTEMPTS=10

# API settings  
CORS_ORIGINS=["http://localhost:3000"]
API_PORT=8000
```

#### Frontend
```bash
# API configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws

# Feature flags
NEXT_PUBLIC_ENABLE_CHARTS=true
NEXT_PUBLIC_ENABLE_NOTIFICATIONS=true
```

## 🔍 Monitoring & Debugging

### Performance Monitoring
- **WebSocket Connection Health**: Connection uptime and stability
- **API Response Times**: REST endpoint performance
- **Price Update Frequency**: Real-time data freshness
- **Memory Usage**: Price data storage efficiency

### Debug Tools
```javascript
// Frontend debugging
localStorage.setItem('debug', 'websocket,api');

// Check WebSocket status
console.log(websocketService.getConnectionStatus());

// Monitor price updates
websocketService.on('price_update', console.log);
```

### Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# Frontend health  
curl http://localhost:3000/api/health

# WebSocket connection test
wscat -c ws://localhost:8000/ws
```

## 🛠️ Development

### Adding New Exchanges

#### 1. Create Exchange Connector
```python
# src/exchanges/new_exchange.py
from .base_exchange import BaseExchange

class NewExchange(BaseExchange):
    def __init__(self):
        super().__init__('newexchange')
    
    def get_websocket_url(self) -> str:
        return 'wss://api.newexchange.com/ws'
    
    def get_subscribe_message(self, symbol: str) -> dict:
        return {'op': 'subscribe', 'symbol': symbol}
    
    async def handle_message(self, message: dict):
        # Parse exchange-specific message format
        # Emit price_update events
        pass
```

#### 2. Register Exchange
```python
# main.py
from src.exchanges.new_exchange import NewExchange

self.supported_exchanges = ['binance', 'bybit', 'okx', 'newexchange']
self.exchange_classes = {
    # ... existing exchanges
    'newexchange': NewExchange
}
```

#### 3. Add Frontend Styling
```css
/* frontend/styles/globals.css */
.exchange-newexchange {
  @apply exchange-badge bg-purple-900 text-purple-300;
}
```

### Adding New Features

#### Backend Routes
```python
# backend/main.py
@app.get("/api/new-feature")
async def new_feature():
    return {"feature": "data"}
```

#### Frontend Components
```typescript
// frontend/components/NewFeature.tsx
import React from 'react';

const NewFeature: React.FC = () => {
  return <div>New Feature</div>;
};

export default NewFeature;
```

## 🐛 Troubleshooting

### Common Issues

#### WebSocket Connection Failed
```bash
# Check backend is running
curl http://localhost:8000/health

# Verify WebSocket endpoint
wscat -c ws://localhost:8000/ws

# Check firewall/proxy settings
```

#### No Price Updates
```bash
# Verify exchange connections
tail -f backend.log | grep "Connected to"

# Check symbol format
# Binance/Bybit: BTCUSDT
# OKX: BTC-USDT

# Validate input file
python validate.py
```

#### Frontend Not Loading
```bash
# Check Node.js version
node --version  # Should be 16+

# Clear dependencies
rm -rf frontend/node_modules
cd frontend && npm install

# Check API connectivity  
curl http://localhost:8000/api/summary
```

#### High Memory Usage
```python
# Adjust cleanup intervals
# In PriceManager
await self.start_stale_data_cleanup(
    interval_seconds=30,    # More frequent cleanup
    max_age_seconds=120     # Shorter data retention
)
```

## 📈 Performance Optimization

### Backend Optimizations
- **Connection Pooling**: Reuse WebSocket connections
- **Data Compression**: Minimize WebSocket message size
- **Memory Management**: Regular cleanup of stale data
- **Caching**: Redis for frequently accessed data

### Frontend Optimizations  
- **Code Splitting**: Lazy load components
- **Memoization**: Prevent unnecessary re-renders
- **Virtual Scrolling**: Handle large data tables
- **Service Workers**: Cache static assets

## 🔒 Security Considerations

### API Security
- **Rate Limiting**: Prevent API abuse
- **Input Validation**: Sanitize all user inputs
- **CORS Configuration**: Restrict allowed origins
- **Authentication**: JWT tokens for protected endpoints

### WebSocket Security
- **Origin Validation**: Verify WebSocket origins
- **Message Validation**: Sanitize incoming messages
- **Connection Limits**: Prevent connection exhaustion
- **SSL/TLS**: Secure WebSocket connections (WSS)

## 📝 License

MIT License - Feel free to use this project for personal or commercial purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🆘 Support

### Documentation
- **Python Engine**: See `README.md`
- **Frontend**: See `FRONTEND_README.md`
- **API Documentation**: http://localhost:8000/docs

### Community
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Wiki**: Community-maintained documentation

---

## 🎉 Success!

You now have a complete real-time cryptocurrency futures price monitoring and arbitrage detection system with:

✅ **Python Price Engine** - Multi-exchange WebSocket connections  
✅ **FastAPI Backend** - RESTful APIs and WebSocket hub  
✅ **React Frontend** - Modern, responsive dashboard  
✅ **Real-Time Updates** - Sub-second price feeds  
✅ **Arbitrage Detection** - Automated opportunity identification  
✅ **Professional UI** - CoinGlass-inspired design  

**Start trading smarter with real-time market intelligence!** 🚀📈