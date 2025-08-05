# Cryptocurrency Perpetual Futures Arbitrage Tracking System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org)
[![WebSocket](https://img.shields.io/badge/WebSocket-Real--time-orange.svg)](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)

A **professional-grade, real-time cryptocurrency perpetual futures arbitrage tracking system** that monitors price differences across 11 major cryptocurrency exchanges and identifies profitable trading opportunities.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/anujsainicse/future_rtd.git
cd future-spot

# Install dependencies and start everything
./run.sh
```

**Access Points:**
- 🌐 **Web Dashboard**: http://localhost:3000
- 📊 **API Documentation**: http://localhost:8000/docs
- 🔌 **WebSocket**: ws://localhost:8000/ws

## ✨ Key Features

### 🎯 **Comprehensive Exchange Coverage**
- **11 Major Exchanges**: Binance, Bybit, OKX, KuCoin, Deribit, BitMEX, Gate.io, MEXC, Bitget, Phemex, CoinDCX
- **450+ Perpetual Futures Contracts** across all exchanges
- **Real-time WebSocket connections** with automatic reconnection

### 📈 **Advanced Arbitrage Detection**
- **Smart opportunity identification** with configurable thresholds
- **Rate-limited alerts** (5-minute cooldown per symbol)
- **Profit percentage calculations** with risk assessment
- **Real-time spread monitoring** across exchange pairs

### 🖥️ **Modern Web Dashboard**
- **Professional dark theme** optimized for trading
- **Real-time price updates** with visual indicators
- **Sortable and filterable tables** for all data
- **Connection status monitoring** with health indicators

### 🔧 **Developer-Friendly API**
- **RESTful API** with comprehensive endpoints
- **WebSocket streaming** for real-time data
- **Automatic OpenAPI documentation** at `/docs`
- **CORS support** for web applications

## 🏗️ Architecture

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Frontend Layer    │    │   Backend API       │    │   Price Engine      │
│   (React/Next.js)   │◄──►│   (FastAPI)         │◄──►│   (Python/AsyncIO)  │
│   Port: 3000        │    │   Port: 8000        │    │   WebSocket Clients │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

### Core Components

#### **Price Engine** (`src/`)
- **Real-time data collection** from 11 exchanges
- **Unified price management** with event-driven architecture
- **Automatic error handling** and reconnection logic

#### **Backend API** (`backend/`)
- **FastAPI server** with comprehensive REST endpoints
- **WebSocket hub** for real-time data streaming
- **Configuration management** with hot reload capability

#### **Frontend Dashboard** (`frontend/`)
- **React.js/Next.js** modern web application
- **TypeScript** for type safety and better development
- **Tailwind CSS** for professional styling

## 🔌 Exchange Coverage

| Exchange | Native Format | Connection Type | Status |
|----------|---------------|-----------------|--------|
| **Binance** | BTCUSDT | WebSocket | ✅ Active |
| **Bybit** | BTCUSDT | WebSocket | ✅ Active |
| **OKX** | BTC-USDT-SWAP | WebSocket | ✅ Active |
| **KuCoin** | XBTUSDTM | REST + WebSocket | ✅ Active |
| **Deribit** | BTC-PERPETUAL | JSON-RPC WebSocket | ✅ Active |
| **BitMEX** | XBTUSD | WebSocket | ✅ Active |
| **Gate.io** | BTC_USDT | WebSocket | ✅ Active |
| **MEXC** | BTC_USDT | WebSocket | ✅ Active |
| **Bitget** | BTCUSDT | WebSocket | ✅ Active |
| **Phemex** | BTCUSD | WebSocket | ✅ Active |
| **CoinDCX** | BTCUSDT | Socket.io | ✅ Active |

## 📊 API Documentation

### **REST Endpoints**

#### Health & System
```http
GET /health                           # System health check
GET /                                # API information
```

#### Price Data
```http
GET /api/prices                      # All current prices
GET /api/prices/{symbol}             # Prices for specific symbol
GET /api/best-prices/{symbol}        # Best bid/ask prices
GET /api/summary                     # Market summary statistics
```

#### Arbitrage Detection
```http
GET /api/arbitrage                   # All arbitrage opportunities
GET /api/arbitrage/{symbol}          # Opportunities for symbol
GET /api/spread/{symbol}/{ex1}/{ex2} # Spread between exchanges
GET /api/arbitrage/{symbol}/alert-status # Alert cooldown status
```

#### Configuration
```http
POST /api/reload-config              # Reload symbol configuration
```

### **WebSocket API**

**Endpoint:** `ws://localhost:8000/ws`

**Message Types:**
- `price_update` - Real-time price changes
- `arbitrage_opportunities` - Top arbitrage opportunities
- `market_summary` - System statistics
- `initial_prices` - Full price snapshot

## ⚙️ Configuration

### Symbol Configuration (`futures_symbols.txt`)

**Format:** `BASE_SYMBOL:EXCHANGE_NATIVE_SYMBOL:exchange_name`

```text
# Binance USDT-Margined Perpetual Futures
BTC:BTCUSDT:binance
ETH:ETHUSDT:binance
SOL:SOLUSDT:binance

# OKX USDT-Margined Perpetual Swaps  
BTC:BTC-USDT-SWAP:okx
ETH:ETH-USDT-SWAP:okx
SOL:SOL-USDT-SWAP:okx

# KuCoin USDT-Margined Perpetual Contracts
BTC:XBTUSDTM:kucoin
ETH:ETHUSDTM:kucoin
SOL:SOLUSDTM:kucoin
```

**Features:**
- ✅ **453 pre-configured mappings** across all exchanges
- ✅ **Hot reload capability** via API endpoint
- ✅ **Multiple format support** (TXT, CSV, JSON)
- ✅ **Automatic validation** against supported exchanges

## 🛠️ Installation & Setup

### **Prerequisites**
- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Git** for version control

### **Backend Setup**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start backend server
./start_backend.sh
# or manually:
cd backend && python main.py
```

### **Frontend Setup**
```bash
# Install Node.js dependencies
cd frontend && npm install

# Start development server
npm run dev
# or use the script:
./start_frontend.sh
```

### **Complete Setup**
```bash
# Start everything at once
./run.sh
```

## 📈 Performance Characteristics

### **Scalability**
- ⚡ **Sub-second latency** for price updates
- 🔄 **Concurrent WebSocket management** for 11+ exchanges
- 💾 **Memory-efficient** in-memory storage with cleanup
- 📊 **High-frequency updates** (100+ per second)

### **Reliability**
- 🔄 **Automatic reconnection** with exponential backoff
- 🏥 **Health monitoring** for all connections
- 🛡️ **Graceful error handling** without crashes
- 🧹 **Stale data cleanup** to prevent memory bloat

## 🔧 Development

### **Project Structure**
```
future-spot/
├── src/                     # Core price engine
│   ├── exchanges/           # Exchange implementations
│   ├── utils/              # Utility functions
│   └── price_manager.py    # Price management
├── backend/                # FastAPI server
│   └── main.py            # API endpoints
├── frontend/              # React.js dashboard
│   ├── components/        # React components
│   ├── pages/            # Next.js pages
│   └── lib/              # Utilities
├── futures_symbols.txt    # Symbol configuration
└── run.sh                # Quick start script
```

### **Adding New Exchanges**

1. **Create exchange class** in `src/exchanges/`
2. **Implement WebSocket connection** logic
3. **Add symbol normalization** methods
4. **Update configuration** files
5. **Test connection** and data flow

### **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and documentation
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- 📧 **Email**: [your-email@example.com]
- 🐛 **Issues**: [GitHub Issues](https://github.com/anujsainicse/future_rtd/issues)
- 📖 **Documentation**: See `/docs` folder for detailed guides

## 🎯 Roadmap

- [ ] **Portfolio tracking** integration
- [ ] **Advanced risk metrics** calculation  
- [ ] **Trading execution** capabilities
- [ ] **Machine learning** price prediction
- [ ] **Mobile application** development
- [ ] **Cloud deployment** templates

---

**Built with ❤️ for the cryptocurrency trading community**