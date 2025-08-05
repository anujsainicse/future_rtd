# Crypto Futures Price Fetcher - Complete Documentation

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [Installation & Setup](#installation--setup)
5. [Usage Guide](#usage-guide)
6. [API Documentation](#api-documentation)
7. [Exchange Integration](#exchange-integration)
8. [Development Guide](#development-guide)
9. [Troubleshooting](#troubleshooting)
10. [Contributing](#contributing)

---

## 🎯 Project Overview

The Crypto Futures Price Fetcher is a **high-performance, real-time cryptocurrency futures price tracking system** that connects to 11 major exchanges via WebSocket connections. It provides live price feeds, arbitrage detection, and a comprehensive API for cryptocurrency trading applications.

### Key Highlights
- **Real-time WebSocket connections** to 11 major exchanges
- **Arbitrage opportunity detection** with configurable thresholds
- **RESTful API** with FastAPI backend
- **React.js frontend** dashboard
- **Event-driven architecture** for optimal performance
- **Production-ready** with error handling and reconnection logic

---

## 🏗️ Architecture

### System Architecture Diagram

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API    │    │   Exchanges     │
│   (React.js)    │◄──►│   (FastAPI)      │◄──►│   (WebSocket)   │
│                 │    │                  │    │                 │
│ • Dashboard     │    │ • REST API       │    │ • Binance       │
│ • Real-time UI  │    │ • WebSocket      │    │ • Bybit         │
│ • Price Display │    │ • Price Manager  │    │ • OKX           │
│ • Arbitrage     │    │ • Event System   │    │ • KuCoin        │
└─────────────────┘    └──────────────────┘    │ • Deribit       │
                                               │ • BitMEX        │
                                               │ • Gate.io       │
                                               │ • MEXC          │
                                               │ • Bitget        │
                                               │ • Phemex        │
                                               │ • CoinDCX       │
                                               └─────────────────┘
```

### Core Components

#### 1. **Exchange Layer** (`src/exchanges/`)
- **Base Exchange** (`base_exchange.py`): Abstract base class for all exchanges
- **Exchange Implementations**: 11 specialized exchange connectors
- **WebSocket Management**: Connection handling, reconnection, ping/pong
- **Message Processing**: Real-time price data parsing and normalization

#### 2. **Price Management** (`src/price_manager.py`)
- **Price Storage**: In-memory price database with timestamp tracking
- **Arbitrage Detection**: Real-time spread calculation and opportunity identification
- **Event System**: Publisher-subscriber pattern for price updates
- **Data Validation**: Price data validation and filtering

#### 3. **Backend API** (`backend/main.py`)
- **FastAPI Server**: RESTful API with automatic documentation
- **WebSocket Server**: Real-time price streaming to clients
- **CORS Support**: Cross-origin resource sharing for frontend
- **Health Monitoring**: System health and connection status endpoints

#### 4. **Frontend Dashboard** (`frontend/`)
- **React.js Application**: Modern web interface
- **Real-time Updates**: WebSocket integration for live data
- **Price Tables**: Organized display of price data across exchanges
- **Arbitrage Dashboard**: Live arbitrage opportunities with profit calculations

---

## ✨ Features

### 🔄 Real-time Price Streaming
- **WebSocket connections** to all 11 exchanges
- **Sub-second latency** for price updates
- **Automatic reconnection** with exponential backoff
- **Connection monitoring** and health checks

### 💹 Multi-Exchange Support

| Exchange | Type | WebSocket URL | Symbols |
|----------|------|---------------|---------|
| **Binance** | Futures | `wss://fstream.binance.com/ws` | BTCUSDT, ETHUSDT, etc. |
| **Bybit** | Linear | `wss://stream.bybit.com/v5/public/linear` | BTCUSDT, ETHUSDT, etc. |
| **OKX** | Futures | `wss://ws.okx.com:8443/ws/v5/public` | BTC-USDT, ETH-USDT, etc. |
| **KuCoin** | Futures | Dynamic (token-based) | BTCUSDTM, ETHUSDTM, etc. |
| **Deribit** | Perpetual | `wss://www.deribit.com/ws/api/v2` | BTC-PERPETUAL, ETH-PERPETUAL |
| **BitMEX** | Perpetual | `wss://ws.bitmex.com/realtime` | XBTUSD, ETHUSD |
| **Gate.io** | Futures | `wss://fx-ws.gateio.ws/v4/ws/usdt` | BTC_USDT, ETH_USDT |
| **MEXC** | Futures | `wss://contract.mexc.com/edge` | BTC_USDT, ETH_USDT |
| **Bitget** | UMCBL | `wss://ws.bitget.com/mix/v1/stream` | BTCUSDT_UMCBL, etc. |
| **Phemex** | Perpetual | `wss://ws.phemex.com` | BTCUSD, ETHUSD |
| **CoinDCX** | Futures | `https://stream.coindcx.com` (Socket.io) | BTCUSDT, ETHUSDT |

### 🎯 Arbitrage Detection
- **Real-time spread calculation** between all exchange pairs
- **Configurable minimum spread** thresholds
- **Profit potential estimation** with percentage calculations
- **Top opportunities ranking** by profitability

### 🌐 Comprehensive API
- **RESTful endpoints** for price data and arbitrage opportunities
- **WebSocket streaming** for real-time updates
- **OpenAPI documentation** (Swagger UI)
- **CORS enabled** for web applications

### 📊 Web Dashboard
- **Modern React.js interface** with Tailwind CSS
- **Real-time price tables** with sorting and filtering
- **Arbitrage opportunities display** with profit calculations
- **Connection status monitoring** for all exchanges
- **Responsive design** for desktop and mobile

---

## 🚀 Installation & Setup

### Prerequisites
- **Python 3.8+** (recommended: Python 3.9+)
- **Node.js 16+** (for frontend)
- **npm or yarn** (for frontend dependencies)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd future-spot
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r backend/requirements.txt
   ```

3. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Run the application**
   ```bash
   ./run.sh
   ```

### Manual Setup

#### Backend Setup
```bash
# Install backend dependencies
pip install fastapi uvicorn websockets pydantic python-multipart
pip install python-socketio aiohttp  # For CoinDCX Socket.io

# Start backend server
cd backend
python main.py
```

#### Frontend Setup
```bash
# Install frontend dependencies
cd frontend
npm install

# Start development server
npm run dev
```

### Configuration Files

#### Symbol Configuration (`symbols.csv`)
```csv
exchange,symbol
binance,BTCUSDT
binance,ETHUSDT
bybit,BTCUSDT
bybit,ETHUSDT
okx,BTC-USDT
okx,ETH-USDT
```

#### Environment Variables
```bash
# Optional environment variables
PYTHON_ENV=development
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
```

---

## 📖 Usage Guide

### Starting the Application

#### Option 1: Automatic Start (Recommended)
```bash
./run.sh
```
This script:
- Installs missing dependencies
- Creates default symbol configuration
- Starts both backend and frontend
- Provides access URLs

#### Option 2: Manual Start
```bash
# Terminal 1 - Backend
cd backend && python main.py

# Terminal 2 - Frontend  
cd frontend && npm run dev
```

#### Option 3: Backend Only
```bash
./start_backend_only.sh
```

### Access Points
- **🌐 Web Dashboard**: http://localhost:3000
- **🔌 API Server**: http://localhost:8000
- **📚 API Documentation**: http://localhost:8000/docs
- **🔄 WebSocket**: ws://localhost:8000/ws

### Basic Usage Examples

#### 1. Get All Current Prices
```bash
curl http://localhost:8000/api/prices
```

#### 2. Get Prices for Specific Symbol
```bash
curl http://localhost:8000/api/prices/BTCUSDT
```

#### 3. Get Arbitrage Opportunities
```bash
curl http://localhost:8000/api/arbitrage
```

#### 4. WebSocket Connection (JavaScript)
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Price update:', data);
};
```

---

## 🔌 API Documentation

### REST API Endpoints

#### Health & Status
- **GET** `/health` - System health check
- **GET** `/` - API root information

#### Price Data
- **GET** `/api/prices` - Get all current prices
- **GET** `/api/prices/{symbol}` - Get prices for specific symbol
- **GET** `/api/best-prices/{symbol}` - Get best bid/ask across exchanges
- **GET** `/api/summary` - Get market summary statistics

#### Arbitrage
- **GET** `/api/arbitrage` - Get all arbitrage opportunities
- **GET** `/api/arbitrage/{symbol}` - Get arbitrage for specific symbol
- **GET** `/api/spread/{symbol}/{exchange1}/{exchange2}` - Get spread between exchanges

#### WebSocket
- **WS** `/ws` - Real-time price updates and arbitrage notifications

### Response Formats

#### Price Data Response
```json
{
  "prices": {
    "BTCUSDT": {
      "binance": {
        "price": 43250.50,
        "bid": 43250.40,
        "ask": 43250.60,
        "timestamp": 1638360000000
      },
      "bybit": {
        "price": 43252.10,
        "bid": 43252.00,
        "ask": 43252.20,
        "timestamp": 1638360001000
      }
    }
  },
  "timestamp": "2023-12-01T12:00:00Z"
}
```

#### Arbitrage Response
```json
{
  "opportunities": [
    {
      "symbol": "BTCUSDT",
      "buy_exchange": "binance",
      "sell_exchange": "bybit",
      "buy_price": 43250.50,
      "sell_price": 43252.10,
      "spread": 1.60,
      "spread_percentage": 0.0037,
      "potential_profit": 0.0037,
      "profitable": true
    }
  ],
  "timestamp": "2023-12-01T12:00:00Z"
}
```

#### WebSocket Message Types
```json
// Price Update
{
  "type": "price_update",
  "data": {
    "symbol": "BTCUSDT",
    "exchange": "binance",
    "price": 43250.50,
    "bid": 43250.40,
    "ask": 43250.60,
    "timestamp": 1638360000000
  }
}

// Arbitrage Opportunity
{
  "type": "arbitrage_opportunities",
  "data": [
    {
      "symbol": "BTCUSDT",
      "buy_exchange": "binance",
      "sell_exchange": "bybit",
      "spread_percentage": 0.0037
    }
  ]
}
```

---

## 🔗 Exchange Integration

### Supported Exchanges

#### 1. Binance Futures
- **Connection**: Direct WebSocket
- **Symbols**: Standard format (BTCUSDT, ETHUSDT)
- **Data**: BookTicker (best bid/ask)
- **Ping**: Automatic WebSocket ping/pong

#### 2. Bybit Linear
- **Connection**: Direct WebSocket  
- **Symbols**: Standard format (BTCUSDT, ETHUSDT)
- **Data**: OrderBook Level 1
- **Ping**: Custom ping with request ID

#### 3. OKX Futures
- **Connection**: Direct WebSocket
- **Symbols**: Hyphenated format (BTC-USDT, ETH-USDT)
- **Data**: Order book snapshot
- **Ping**: Simple ping message

#### 4. KuCoin Futures (Mixed Auth)
- **Connection**: REST auth + WebSocket data
- **Authentication**: Token-based via REST API
- **Symbols**: Margin format (BTCUSDTM, ETHUSDTM)
- **Data**: Ticker updates

#### 5. Deribit
- **Connection**: Direct WebSocket with JSON-RPC
- **Symbols**: Perpetual format (BTC-PERPETUAL, ETH-PERPETUAL)
- **Data**: Ticker with 100ms updates
- **Ping**: JSON-RPC test method

#### 6. BitMEX
- **Connection**: Direct WebSocket
- **Symbols**: Custom format (XBTUSD for Bitcoin, ETHUSD)
- **Data**: Quote + Trade data for accurate last price
- **Features**: Separate bid/ask and trade subscriptions

#### 7. Gate.io Futures
- **Connection**: Direct WebSocket
- **Symbols**: Underscore format (BTC_USDT, ETH_USDT)
- **Data**: Futures tickers
- **Message Format**: Handles both dict and list formats

#### 8. MEXC Futures
- **Connection**: Direct WebSocket
- **Symbols**: Underscore format (BTC_USDT, ETH_USDT)
- **Data**: Push ticker updates
- **Error Handling**: Code-based error responses

#### 9. Bitget UMCBL
- **Connection**: Direct WebSocket
- **Symbols**: UMCBL suffix (BTCUSDT_UMCBL, ETHUSDT_UMCBL)
- **Data**: Ticker channel with instType specification
- **Message Format**: Structured args format

#### 10. Phemex
- **Connection**: Direct WebSocket
- **Symbols**: USD format (BTCUSD, ETHUSD)
- **Data**: Order book with scaled prices
- **Scaling**: Symbol-specific price scaling (10000, 100000000)

#### 11. CoinDCX (Socket.io)
- **Connection**: Socket.io WebSocket
- **Library**: python-socketio
- **Symbols**: Standard format (BTCUSDT, ETHUSDT)
- **Data**: Real-time ticker events
- **Events**: subscribe/unsubscribe via Socket.io emit

### Adding New Exchanges

To add a new exchange, create a class inheriting from `BaseExchange`:

```python
# src/exchanges/new_exchange.py
from .base_exchange import BaseExchange

class NewExchange(BaseExchange):
    def __init__(self):
        super().__init__('newexchange')
        self.req_id = 1
    
    def get_websocket_url(self) -> str:
        return 'wss://api.newexchange.com/ws'
    
    def get_subscribe_message(self, symbol: str) -> dict:
        return {
            'op': 'subscribe',
            'args': [f'ticker.{symbol}']
        }
    
    async def handle_message(self, message: dict):
        # Implement message parsing logic
        pass
```

Then register in `backend/main.py`:
```python
from src.exchanges.new_exchange import NewExchange

# Add to supported exchanges
self.supported_exchanges.append('newexchange')
self.exchange_classes['newexchange'] = NewExchange
```

---

## 👨‍💻 Development Guide

### Project Structure

```
future-spot/
├── src/                          # Core application source
│   ├── exchanges/               # Exchange implementations
│   │   ├── base_exchange.py    # Abstract base class
│   │   ├── binance_exchange.py # Exchange-specific implementations
│   │   └── ...
│   ├── price_manager.py        # Price storage and arbitrage detection
│   └── utils/                  # Utility functions
│       └── input_parser.py     # Configuration file parsing
├── backend/                     # FastAPI backend server
│   ├── main.py                 # API server and WebSocket handling
│   └── requirements.txt        # Backend dependencies
├── frontend/                    # React.js web application
│   ├── components/             # React components
│   ├── lib/                    # Frontend utilities
│   ├── pages/                  # Next.js pages
│   └── package.json           # Frontend dependencies
├── examples/                    # Example configuration files
│   ├── minimal.csv            # Basic symbol configuration
│   └── symbols.json           # JSON format configuration
├── requirements.txt            # Core Python dependencies
└── documentation files        # Various documentation files
```

### Key Classes and Methods

#### BaseExchange Class
```python
class BaseExchange:
    async def connect(self) -> bool
    async def disconnect(self)
    async def subscribe(self, symbol: str)
    async def handle_message(self, message)
    def get_websocket_url(self) -> str
    def get_subscribe_message(self, symbol: str) -> dict
    def format_price_data(self, symbol, price, bid, ask, timestamp) -> dict
```

#### PriceManager Class
```python
class PriceManager:
    def update_price(self, data: dict)
    def get_all_prices(self) -> dict
    def get_prices_by_symbol(self, symbol: str) -> dict
    def check_arbitrage_opportunities(self, symbol: str, min_spread: float) -> list
    def get_best_prices(self, symbol: str) -> dict
```

### Development Workflow

#### 1. Setting up Development Environment
```bash
# Clone and setup
git clone <repository>
cd future-spot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Install frontend dependencies
cd frontend && npm install
```

#### 2. Running in Development Mode
```bash
# Backend with auto-reload
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend with hot reload
cd frontend  
npm run dev
```

#### 3. Testing
```bash
# Test backend endpoints
python test_backend.py

# Test specific exchange
python -c "from src.exchanges.binance_exchange import BinanceExchange; print('Import successful')"

# Validate configuration
python validate.py
```

#### 4. Debugging
```bash
# Enable debug mode
export LOG_LEVEL=DEBUG

# Run with debug script
./debug.sh

# Check logs
tail -f backend.log
tail -f frontend.log
```

### Code Style and Standards

#### Python Code Style
- **PEP 8** compliance
- **Type hints** for all function parameters and returns
- **Docstrings** for all classes and methods
- **Error handling** with proper logging
- **Async/await** for all I/O operations

#### JavaScript/TypeScript Code Style
- **ESLint** configuration
- **TypeScript** for type safety
- **Modern React** with hooks
- **Tailwind CSS** for styling

#### Exchange Implementation Guidelines
1. **Inherit from BaseExchange**
2. **Implement all required methods**
3. **Handle reconnection gracefully**
4. **Validate all incoming data**
5. **Use proper error logging**
6. **Follow symbol normalization patterns**

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Connection Failures
**Problem**: Exchange WebSocket connections fail
```
ERROR: Failed to connect to exchange: Connection refused
```

**Solutions**:
- Check internet connectivity
- Verify exchange WebSocket URLs are correct
- Check if exchange is blocking your IP/region
- Ensure firewall allows outbound WebSocket connections

#### 2. Symbol Format Errors
**Problem**: Symbols not found or price updates missing
```
DEBUG: No target symbols found in ticker data
```

**Solutions**:
- Verify symbol format for each exchange (BTCUSDT vs BTC-USDT vs BTC_USDT)
- Check if symbols exist on the exchange
- Update symbol mappings in exchange classes
- Validate `symbols.csv` configuration

#### 3. Dependency Issues
**Problem**: Import errors or missing modules
```
ModuleNotFoundError: No module named 'socketio'
```

**Solutions**:
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# For CoinDCX Socket.io
pip install 'python-socketio>=5.0.0'

# For async HTTP
pip install 'aiohttp>=3.8.0'
```

#### 4. Port Already in Use
**Problem**: Server fails to start
```
ERROR: [Errno 48] Address already in use
```

**Solutions**:
```bash
# Kill processes on port 8000
lsof -ti:8000 | xargs kill -9

# Kill processes on port 3000  
lsof -ti:3000 | xargs kill -9

# Or use different ports
uvicorn main:app --port 8001
```

#### 5. Frontend Build Issues
**Problem**: Frontend fails to start or build
```
npm ERR! Could not resolve dependency
```

**Solutions**:
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Update dependencies
npm update
```

### Performance Issues

#### 1. High Memory Usage
**Symptoms**: Memory usage grows over time
**Causes**: Price data accumulation, connection leaks
**Solutions**:
- Implement price data cleanup (remove old data)
- Monitor WebSocket connection lifecycle
- Use memory profiling tools

#### 2. Slow Price Updates
**Symptoms**: Delayed price updates, high latency
**Causes**: Network issues, exchange throttling, CPU bottlenecks
**Solutions**:
- Check network latency to exchanges
- Implement connection pooling
- Optimize message processing code
- Use performance monitoring

#### 3. High CPU Usage
**Symptoms**: High CPU utilization, slow response
**Causes**: Inefficient JSON parsing, too many concurrent connections
**Solutions**:
- Optimize message parsing logic
- Implement connection management
- Use async I/O properly
- Profile CPU usage

### Debugging Guide

#### 1. Enable Debug Logging
```python
# In your code
logging.basicConfig(level=logging.DEBUG)

# Or via environment
export LOG_LEVEL=DEBUG
```

#### 2. WebSocket Debugging
```python
# Enable websockets debug logging
import logging
logging.getLogger('websockets').setLevel(logging.DEBUG)
```

#### 3. Exchange-Specific Debugging
```python
# Test individual exchange
from src.exchanges.binance_exchange import BinanceExchange
import asyncio

async def test_exchange():
    exchange = BinanceExchange()
    await exchange.connect()
    await exchange.subscribe('BTCUSDT')
    # Monitor messages...

asyncio.run(test_exchange())
```

#### 4. API Testing
```bash
# Test health endpoint
curl -v http://localhost:8000/health

# Test price endpoint with verbose output
curl -v http://localhost:8000/api/prices/BTCUSDT

# Test WebSocket connection
wscat -c ws://localhost:8000/ws
```

---

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Install development dependencies
4. Make your changes with tests
5. Submit a pull request

### Contribution Guidelines

#### 1. Exchange Additions
- Follow the BaseExchange pattern
- Include comprehensive error handling
- Add symbol mapping documentation
- Test with real exchange data
- Update documentation

#### 2. Code Quality
- Maintain test coverage above 80%
- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Add docstrings for all public methods
- Include error handling and logging

#### 3. Documentation
- Update API documentation for changes
- Add examples for new features
- Update troubleshooting guide
- Include performance considerations

#### 4. Testing
- Unit tests for all new functionality
- Integration tests for exchange connections
- End-to-end tests for API endpoints
- Performance tests for high-load scenarios

### Reporting Issues
- Use GitHub Issues for bug reports
- Include system information (OS, Python version)
- Provide reproducible steps
- Include log files when relevant
- Tag issues appropriately (bug, enhancement, documentation)

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🚀 Roadmap

### Current Version Features
- ✅ 11 exchange integrations with WebSocket
- ✅ Real-time arbitrage detection
- ✅ FastAPI backend with comprehensive API
- ✅ React.js frontend dashboard
- ✅ Production-ready error handling

### Planned Features
- 🔄 **Database Integration**: PostgreSQL/MongoDB for historical data
- 🔄 **Advanced Analytics**: Machine learning for price prediction
- 🔄 **Alert System**: Email/SMS notifications for arbitrage opportunities  
- 🔄 **Mobile App**: React Native mobile application
- 🔄 **Options Trading**: Support for options contracts
- 🔄 **Portfolio Tracking**: Portfolio management and PnL tracking
- 🔄 **Risk Management**: Position sizing and risk assessment tools
- 🔄 **Backtesting**: Historical arbitrage opportunity analysis

### Performance Improvements
- 🔄 **Redis Caching**: High-performance price data caching
- 🔄 **Microservices**: Break down into specialized services
- 🔄 **Load Balancing**: Support for multiple backend instances
- 🔄 **CDN Integration**: Global content delivery for frontend

---

*For additional support or questions, please open an issue on GitHub or contact the development team.*