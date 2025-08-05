# Developer Guide - Crypto Futures Price Fetcher

## 📋 Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Project Architecture](#project-architecture)
3. [Exchange Integration](#exchange-integration)
4. [Testing](#testing)
5. [Debugging](#debugging)
6. [Code Style Guidelines](#code-style-guidelines)
7. [Deployment](#deployment)
8. [Contributing](#contributing)

---

## 🛠️ Development Environment Setup

### Prerequisites

#### Required Software
- **Python 3.8+** (recommended: Python 3.9+)
- **Node.js 16+** (for frontend development)
- **Git** (for version control)
- **VS Code** (recommended IDE with extensions)

#### Recommended VS Code Extensions
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.flake8",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next"
  ]
}
```

### Initial Setup

#### 1. Clone and Environment Setup
```bash
# Clone the repository
git clone <repository-url>
cd future-spot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Install development dependencies
pip install pytest pytest-asyncio black flake8 mypy
```

#### 2. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Install development dependencies
npm install --save-dev @types/node @types/react eslint prettier

# Return to project root
cd ..
```

#### 3. Environment Configuration
```bash
# Create environment file (optional)
cat > .env << EOF
PYTHON_ENV=development
LOG_LEVEL=DEBUG
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_PORT=3000
EOF
```

### Development Scripts

Create development helper scripts:

#### `dev-backend.sh`
```bash
#!/bin/bash
# Development backend startup script

export PYTHON_ENV=development
export LOG_LEVEL=DEBUG

cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### `dev-frontend.sh`
```bash
#!/bin/bash
# Development frontend startup script

cd frontend
npm run dev
```

#### `test-all.sh`
```bash
#!/bin/bash
# Run all tests

echo "Running Python tests..."
python -m pytest tests/ -v

echo "Running TypeScript checks..."
cd frontend
npm run type-check

echo "Running ESLint..."
npm run lint

echo "All tests completed!"
```

---

## 🏗️ Project Architecture

### Directory Structure
```
future-spot/
├── src/                          # Core Python source code
│   ├── exchanges/               # Exchange implementations
│   │   ├── __init__.py
│   │   ├── base_exchange.py    # Abstract base class
│   │   ├── binance_exchange.py # Exchange implementations
│   │   └── ...
│   ├── price_manager.py        # Price storage and arbitrage
│   └── utils/
│       ├── __init__.py
│       └── input_parser.py     # Configuration parsing
├── backend/                     # FastAPI backend server
│   ├── __init__.py
│   ├── main.py                 # API server
│   └── requirements.txt
├── frontend/                    # React.js frontend
│   ├── components/             # React components
│   ├── lib/                    # Utilities
│   ├── pages/                  # Next.js pages
│   └── ...
├── tests/                      # Test files
│   ├── test_exchanges.py
│   ├── test_price_manager.py
│   └── ...
├── examples/                   # Example configurations
├── docs/                       # Documentation
└── scripts/                    # Development scripts
```

### Core Components

#### 1. Exchange Layer (`src/exchanges/`)

**BaseExchange Class** - Abstract base for all exchanges:
```python
from abc import ABC, abstractmethod
from typing import Dict, Optional
import asyncio
import websockets
import json
import logging

class BaseExchange(ABC):
    def __init__(self, name: str):
        self.name = name
        self.websocket = None
        self.is_connected = False
        self.subscribed_symbols = set()
        self.event_handlers = {}
        
    @abstractmethod
    def get_websocket_url(self) -> str:
        """Return the WebSocket URL for this exchange."""
        pass
        
    @abstractmethod
    def get_subscribe_message(self, symbol: str) -> Dict:
        """Return subscription message for a symbol."""
        pass
        
    @abstractmethod
    async def handle_message(self, message: Dict):
        """Handle incoming WebSocket messages."""
        pass
```

**Exchange Implementation Pattern**:
```python
class ExampleExchange(BaseExchange):
    def __init__(self):
        super().__init__('example')
        self.req_id = 1
        
    def get_websocket_url(self) -> str:
        return 'wss://api.example.com/ws'
        
    def get_subscribe_message(self, symbol: str) -> Dict:
        message = {
            'op': 'subscribe',
            'args': [f'ticker.{symbol}'],
            'id': self.req_id
        }
        self.req_id += 1
        return message
        
    async def handle_message(self, message: Dict):
        if message.get('channel') == 'ticker':
            await self._handle_ticker_update(message)
            
    async def _handle_ticker_update(self, message: Dict):
        # Extract price data
        symbol = message['data']['symbol']
        price = float(message['data']['price'])
        bid = float(message['data']['bid'])
        ask = float(message['data']['ask'])
        timestamp = int(message['data']['timestamp'])
        
        # Format and emit price data
        price_data = self.format_price_data(symbol, price, bid, ask, timestamp)
        self.emit('price_update', price_data)
```

#### 2. Price Manager (`src/price_manager.py`)

**Core Functions**:
```python
class PriceManager:
    def __init__(self):
        self.prices = {}  # symbol -> exchange -> price_data
        self.event_handlers = {}
        self.last_cleanup = time.time()
        
    def update_price(self, data: Dict):
        """Update price data from exchange."""
        symbol = data['symbol']
        exchange = data['exchange']
        price_info = data['data']
        
        # Update internal storage
        if symbol not in self.prices:
            self.prices[symbol] = {}
        self.prices[symbol][exchange] = price_info
        
        # Emit events
        self.emit('price_update', data)
        self._check_arbitrage_opportunities(symbol)
        
    def _check_arbitrage_opportunities(self, symbol: str):
        """Check for arbitrage opportunities for a symbol."""
        if symbol not in self.prices:
            return
            
        exchanges = list(self.prices[symbol].keys())
        opportunities = []
        
        for i, exchange1 in enumerate(exchanges):
            for exchange2 in exchanges[i+1:]:
                opp = self._calculate_spread(symbol, exchange1, exchange2)
                if opp and opp['profitable']:
                    opportunities.append(opp)
                    
        if opportunities:
            self.emit('arbitrage_opportunity', opportunities)
```

#### 3. Backend API (`backend/main.py`)

**FastAPI Structure**:
```python
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI(
    title="Crypto Futures Price API",
    description="Real-time price tracking and arbitrage detection",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Price fetcher instance
price_fetcher = None

@app.on_event("startup")
async def startup_event():
    global price_fetcher
    # Initialize price fetcher
    price_fetcher = SimplePriceFetcher()
    # Start background task
    asyncio.create_task(start_price_fetcher())

@app.get("/api/prices")
async def get_all_prices():
    if not price_fetcher:
        return {"error": "Price fetcher not initialized"}
    
    api = price_fetcher.get_api()
    prices = api['get_all_prices']()
    return {"prices": prices}
```

---

## 🔗 Exchange Integration

### Adding a New Exchange

Follow these steps to add support for a new exchange:

#### 1. Create Exchange Class
```python
# src/exchanges/newexchange_exchange.py
import logging
from typing import Dict, Optional
from .base_exchange import BaseExchange

logger = logging.getLogger(__name__)

class NewExchangeExchange(BaseExchange):
    def __init__(self):
        super().__init__('newexchange')
        self.req_id = 1
        
    def get_websocket_url(self) -> str:
        return 'wss://api.newexchange.com/ws/v1'
        
    def get_subscribe_message(self, symbol: str) -> Dict:
        # Convert symbol to exchange format
        exchange_symbol = self._convert_to_exchange_symbol(symbol)
        
        message = {
            'op': 'subscribe',
            'channel': 'ticker',
            'symbol': exchange_symbol,
            'id': self.req_id
        }
        self.req_id += 1
        return message
        
    def get_unsubscribe_message(self, symbol: str) -> Dict:
        exchange_symbol = self._convert_to_exchange_symbol(symbol)
        
        message = {
            'op': 'unsubscribe',
            'channel': 'ticker',
            'symbol': exchange_symbol,
            'id': self.req_id
        }
        self.req_id += 1
        return message
        
    def _convert_to_exchange_symbol(self, symbol: str) -> str:
        """Convert standard symbol to exchange format."""
        # Example: BTCUSDT -> BTC/USDT
        if symbol.endswith('USDT'):
            base = symbol[:-4]
            return f"{base}/USDT"
        return symbol
        
    def _convert_from_exchange_symbol(self, exchange_symbol: str) -> str:
        """Convert exchange symbol back to standard format."""
        # Example: BTC/USDT -> BTCUSDT
        return exchange_symbol.replace('/', '')
        
    async def handle_message(self, message: Dict):
        logger.debug(f"NewExchange message: {message}")
        
        # Handle subscription confirmation
        if message.get('type') == 'subscribed':
            logger.info(f"NewExchange subscription confirmed: {message.get('symbol')}")
            return
            
        # Handle ticker data
        if message.get('type') == 'ticker':
            await self._handle_ticker_update(message)
            
    async def _handle_ticker_update(self, message: Dict):
        """Handle ticker price updates."""
        try:
            # Extract data from message
            exchange_symbol = message.get('symbol')
            if not exchange_symbol:
                return
                
            symbol = self._convert_from_exchange_symbol(exchange_symbol)
            
            # Get price data
            price = float(message.get('price', 0))
            bid = float(message.get('bid', 0))
            ask = float(message.get('ask', 0))
            timestamp = int(message.get('timestamp', 0))
            
            # Validate data
            if not all([price, bid, ask]):
                logger.debug(f"NewExchange {symbol}: Missing price data")
                return
                
            # Format and emit
            price_data = self.format_price_data(symbol, price, bid, ask, timestamp)
            self.emit('price_update', price_data)
            
        except (ValueError, TypeError) as e:
            logger.error(f"Error processing NewExchange ticker: {e}")
            
    def get_ping_message(self) -> Optional[Dict]:
        message = {
            'op': 'ping',
            'id': self.req_id
        }
        self.req_id += 1
        return message
```

#### 2. Register Exchange
```python
# backend/main.py
from src.exchanges.newexchange_exchange import NewExchangeExchange

class SimplePriceFetcher:
    def __init__(self):
        # Add to supported exchanges
        self.supported_exchanges = [
            'binance', 'bybit', 'okx', 'newexchange'  # Add here
        ]
        
        # Add to exchange classes
        self.exchange_classes = {
            'binance': BinanceExchange,
            'bybit': BybitExchange,
            'okx': OKXExchange,
            'newexchange': NewExchangeExchange  # Add here
        }
```

#### 3. Add Tests
```python
# tests/test_newexchange.py
import pytest
import asyncio
from src.exchanges.newexchange_exchange import NewExchangeExchange

class TestNewExchangeExchange:
    def setup_method(self):
        self.exchange = NewExchangeExchange()
        
    def test_websocket_url(self):
        url = self.exchange.get_websocket_url()
        assert url == 'wss://api.newexchange.com/ws/v1'
        
    def test_symbol_conversion(self):
        # Test conversion to exchange format
        result = self.exchange._convert_to_exchange_symbol('BTCUSDT')
        assert result == 'BTC/USDT'
        
        # Test conversion from exchange format
        result = self.exchange._convert_from_exchange_symbol('BTC/USDT')
        assert result == 'BTCUSDT'
        
    def test_subscribe_message(self):
        message = self.exchange.get_subscribe_message('BTCUSDT')
        expected = {
            'op': 'subscribe',
            'channel': 'ticker',
            'symbol': 'BTC/USDT',
            'id': 1
        }
        assert message == expected
        
    @pytest.mark.asyncio
    async def test_message_handling(self):
        # Mock ticker message
        ticker_message = {
            'type': 'ticker',
            'symbol': 'BTC/USDT',
            'price': '43250.50',
            'bid': '43250.40',
            'ask': '43250.60',
            'timestamp': 1638360000000
        }
        
        # Set up event handler
        price_updates = []
        def on_price_update(data):
            price_updates.append(data)
        
        self.exchange.on('price_update', on_price_update)
        
        # Handle message
        await self.exchange.handle_message(ticker_message)
        
        # Verify price update was emitted
        assert len(price_updates) == 1
        assert price_updates[0]['symbol'] == 'BTCUSDT'
        assert price_updates[0]['data']['price'] == 43250.50
```

#### 4. Add to Configuration
```csv
# examples/symbols.csv
exchange,symbol
binance,BTCUSDT
bybit,BTCUSDT
newexchange,BTCUSDT
```

---

## 🧪 Testing

### Testing Framework Setup

#### Install Testing Dependencies
```bash
pip install pytest pytest-asyncio pytest-mock pytest-cov
```

#### Test Configuration (`pytest.ini`)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts = 
    --verbose
    --tb=short
    --cov=src
    --cov-report=html
    --cov-report=term-missing
```

### Test Categories

#### 1. Unit Tests
Test individual components in isolation:

```python
# tests/test_price_manager.py
import pytest
from src.price_manager import PriceManager

class TestPriceManager:
    def setup_method(self):
        self.price_manager = PriceManager()
        
    def test_update_price(self):
        price_data = {
            'symbol': 'BTCUSDT',
            'exchange': 'binance',
            'data': {
                'price': 43250.50,
                'bid': 43250.40,
                'ask': 43250.60,
                'timestamp': 1638360000000
            }
        }
        
        self.price_manager.update_price(price_data)
        
        # Verify price was stored
        prices = self.price_manager.get_prices_by_symbol('BTCUSDT')
        assert 'binance' in prices
        assert prices['binance']['price'] == 43250.50
        
    def test_arbitrage_detection(self):
        # Add prices from two exchanges
        self.price_manager.update_price({
            'symbol': 'BTCUSDT',
            'exchange': 'binance',
            'data': {'price': 43250.50, 'bid': 43250.40, 'ask': 43250.60, 'timestamp': 1638360000000}
        })
        
        self.price_manager.update_price({
            'symbol': 'BTCUSDT',
            'exchange': 'bybit', 
            'data': {'price': 43252.10, 'bid': 43252.00, 'ask': 43252.20, 'timestamp': 1638360001000}
        })
        
        # Check for arbitrage opportunities
        opportunities = self.price_manager.check_arbitrage_opportunities('BTCUSDT', 0.001)
        
        assert len(opportunities) > 0
        assert opportunities[0]['symbol'] == 'BTCUSDT'
        assert opportunities[0]['spread'] > 0
```

#### 2. Integration Tests
Test component interactions:

```python
# tests/test_integration.py
import pytest
import asyncio
from unittest.mock import Mock, patch
from backend.main import SimplePriceFetcher

class TestIntegration:
    @pytest.mark.asyncio
    async def test_price_fetcher_startup(self):
        """Test that price fetcher starts and connects to exchanges."""
        price_fetcher = SimplePriceFetcher()
        
        # Mock exchange configuration
        exchange_config = {
            'binance': ['BTCUSDT'],
            'bybit': ['BTCUSDT']
        }
        
        with patch('src.exchanges.binance_exchange.BinanceExchange') as MockBinance:
            mock_binance = Mock()
            mock_binance.connect.return_value = asyncio.coroutine(lambda: True)()
            mock_binance.subscribe.return_value = asyncio.coroutine(lambda: None)()
            MockBinance.return_value = mock_binance
            
            await price_fetcher.initialize_exchanges(exchange_config)
            
            # Verify exchange was initialized
            assert len(price_fetcher.exchanges) == 1
            mock_binance.connect.assert_called_once()
            mock_binance.subscribe.assert_called_with('BTCUSDT')
```

#### 3. API Tests
Test FastAPI endpoints:

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app

class TestAPI:
    def setup_method(self):
        self.client = TestClient(app)
        
    def test_health_endpoint(self):
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        
    def test_prices_endpoint(self):
        response = self.client.get("/api/prices")
        assert response.status_code == 200
        data = response.json()
        assert "prices" in data
        
    def test_arbitrage_endpoint(self):
        response = self.client.get("/api/arbitrage")
        assert response.status_code == 200
        data = response.json()
        assert "opportunities" in data
```

#### 4. Exchange Tests
Test exchange-specific functionality:

```python
# tests/test_exchanges.py
import pytest
from unittest.mock import Mock, patch
from src.exchanges.binance_exchange import BinanceExchange

class TestBinanceExchange:
    def setup_method(self):
        self.exchange = BinanceExchange()
        
    def test_websocket_url(self):
        url = self.exchange.get_websocket_url()
        assert url == 'wss://fstream.binance.com/ws'
        
    def test_subscribe_message(self):
        message = self.exchange.get_subscribe_message('BTCUSDT')
        assert message['method'] == 'SUBSCRIBE'
        assert 'btcusdt@bookTicker' in message['params']
        
    @pytest.mark.asyncio
    async def test_price_update_handling(self):
        # Mock price update message
        price_message = {
            'e': 'bookTicker',
            's': 'BTCUSDT',
            'b': '43250.40',
            'B': '10.5',
            'a': '43250.60',
            'A': '15.2',
            'T': 1638360000000,
            'E': 1638360000000
        }
        
        # Track emitted events
        price_updates = []
        def on_price_update(data):
            price_updates.append(data)
            
        self.exchange.on('price_update', on_price_update)
        
        await self.exchange.handle_message(price_message)
        
        assert len(price_updates) == 1
        assert price_updates[0]['symbol'] == 'BTCUSDT'
        assert price_updates[0]['data']['bid'] == 43250.40
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_price_manager.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_exchanges.py::TestBinanceExchange::test_subscribe_message

# Run async tests only
pytest -m asyncio

# Run with verbose output
pytest -v -s
```

---

## 🐛 Debugging

### Logging Configuration

#### Set Up Structured Logging
```python
# src/utils/logger.py
import logging
import sys
from datetime import datetime

def setup_logging(level=logging.INFO):
    """Configure application logging."""
    
    # Custom formatter
    class CustomFormatter(logging.Formatter):
        def format(self, record):
            timestamp = datetime.fromtimestamp(record.created).isoformat()
            return f"[{timestamp}] {record.levelname:8} {record.name:20} | {record.getMessage()}"
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(CustomFormatter())
    
    # File handler
    file_handler = logging.FileHandler('app.log')
    file_handler.setFormatter(CustomFormatter())
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Suppress noisy libraries
    logging.getLogger('websockets').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
```

#### Debug Configuration
```python
# debug_config.py
import logging
import os

def setup_debug_environment():
    """Configure environment for debugging."""
    
    # Set debug environment variables
    os.environ['PYTHON_ENV'] = 'development'
    os.environ['LOG_LEVEL'] = 'DEBUG'
    
    # Enable all debug logging
    loggers = [
        'src.exchanges',
        'src.price_manager',
        'backend.main',
        'websockets',
        'asyncio'
    ]
    
    for logger_name in loggers:
        logging.getLogger(logger_name).setLevel(logging.DEBUG)
```

### Debugging Tools

#### 1. WebSocket Message Inspector
```python
# debug/websocket_inspector.py
import asyncio
import websockets
import json
from datetime import datetime

async def inspect_exchange_websocket(url, subscribe_message):
    """Connect to exchange WebSocket and log all messages."""
    
    print(f"Connecting to {url}")
    
    async with websockets.connect(url) as websocket:
        # Send subscription
        await websocket.send(json.dumps(subscribe_message))
        print(f"Sent: {subscribe_message}")
        
        # Listen for messages
        try:
            while True:
                message = await websocket.recv()
                timestamp = datetime.now().isoformat()
                print(f"[{timestamp}] Received: {message}")
                
        except KeyboardInterrupt:
            print("Inspection stopped")

# Usage
if __name__ == "__main__":
    url = "wss://fstream.binance.com/ws"
    subscribe_msg = {
        "method": "SUBSCRIBE",
        "params": ["btcusdt@bookTicker"],
        "id": 1
    }
    
    asyncio.run(inspect_exchange_websocket(url, subscribe_msg))
```

#### 2. Price Data Analyzer
```python
# debug/price_analyzer.py
import json
from collections import defaultdict, deque
from datetime import datetime, timedelta

class PriceAnalyzer:
    def __init__(self, window_minutes=5):
        self.prices = defaultdict(lambda: defaultdict(deque))
        self.window = timedelta(minutes=window_minutes)
        
    def add_price(self, exchange, symbol, price, timestamp):
        """Add price data point."""
        self.prices[symbol][exchange].append({
            'price': price,
            'timestamp': timestamp
        })
        
        # Clean old data
        self._clean_old_data(symbol, exchange)
        
    def _clean_old_data(self, symbol, exchange):
        """Remove data older than window."""
        cutoff = datetime.now() - self.window
        cutoff_ts = cutoff.timestamp() * 1000
        
        while (self.prices[symbol][exchange] and 
               self.prices[symbol][exchange][0]['timestamp'] < cutoff_ts):
            self.prices[symbol][exchange].popleft()
            
    def get_statistics(self, symbol):
        """Get price statistics for symbol."""
        stats = {}
        
        for exchange, price_data in self.prices[symbol].items():
            if not price_data:
                continue
                
            prices = [p['price'] for p in price_data]
            stats[exchange] = {
                'count': len(prices),
                'min': min(prices),
                'max': max(prices),
                'avg': sum(prices) / len(prices),
                'latest': prices[-1],
                'volatility': self._calculate_volatility(prices)
            }
            
        return stats
        
    def _calculate_volatility(self, prices):
        """Calculate price volatility."""
        if len(prices) < 2:
            return 0
            
        avg = sum(prices) / len(prices)
        variance = sum((p - avg) ** 2 for p in prices) / len(prices)
        return variance ** 0.5
        
    def find_anomalies(self, symbol, threshold=0.01):
        """Find price anomalies (>1% deviation from average)."""
        anomalies = []
        stats = self.get_statistics(symbol)
        
        if len(stats) < 2:
            return anomalies
            
        avg_price = sum(s['avg'] for s in stats.values()) / len(stats)
        
        for exchange, stat in stats.items():
            deviation = abs(stat['latest'] - avg_price) / avg_price
            if deviation > threshold:
                anomalies.append({
                    'exchange': exchange,
                    'price': stat['latest'],
                    'deviation': deviation,
                    'expected': avg_price
                })
                
        return anomalies

# Usage
analyzer = PriceAnalyzer()

# Add price data points
analyzer.add_price('binance', 'BTCUSDT', 43250.50, 1638360000000)
analyzer.add_price('bybit', 'BTCUSDT', 43252.10, 1638360001000)

# Get statistics
stats = analyzer.get_statistics('BTCUSDT')
print(json.dumps(stats, indent=2))

# Find anomalies
anomalies = analyzer.find_anomalies('BTCUSDT')
for anomaly in anomalies:
    print(f"Anomaly: {anomaly['exchange']} price {anomaly['price']} "
          f"deviates {anomaly['deviation']:.2%} from expected {anomaly['expected']}")
```

#### 3. Connection Monitor
```python
# debug/connection_monitor.py
import asyncio
import time
from collections import defaultdict

class ConnectionMonitor:
    def __init__(self):
        self.connections = {}
        self.stats = defaultdict(lambda: {
            'connects': 0,
            'disconnects': 0,
            'messages': 0,
            'errors': 0,
            'last_message': None,
            'uptime': 0
        })
        
    def on_connect(self, exchange):
        """Record connection event."""
        self.connections[exchange] = {
            'connected_at': time.time(),
            'status': 'connected'
        }
        self.stats[exchange]['connects'] += 1
        print(f"✅ {exchange} connected")
        
    def on_disconnect(self, exchange):
        """Record disconnection event."""
        if exchange in self.connections:
            uptime = time.time() - self.connections[exchange]['connected_at']
            self.stats[exchange]['uptime'] += uptime
            self.connections[exchange]['status'] = 'disconnected'
            
        self.stats[exchange]['disconnects'] += 1
        print(f"❌ {exchange} disconnected")
        
    def on_message(self, exchange):
        """Record message received."""
        self.stats[exchange]['messages'] += 1
        self.stats[exchange]['last_message'] = time.time()
        
    def on_error(self, exchange, error):
        """Record error event."""
        self.stats[exchange]['errors'] += 1
        print(f"🔥 {exchange} error: {error}")
        
    def get_status_report(self):
        """Generate status report."""
        report = {}
        
        for exchange, stats in self.stats.items():
            connection = self.connections.get(exchange, {})
            current_uptime = 0
            
            if connection.get('status') == 'connected':
                current_uptime = time.time() - connection['connected_at']
                
            total_uptime = stats['uptime'] + current_uptime
            
            report[exchange] = {
                'status': connection.get('status', 'unknown'),
                'total_uptime': total_uptime,
                'connects': stats['connects'],
                'disconnects': stats['disconnects'],
                'messages': stats['messages'],
                'errors': stats['errors'],
                'last_message_ago': time.time() - stats['last_message'] if stats['last_message'] else None,
                'reliability': stats['connects'] / max(stats['connects'] + stats['errors'], 1)
            }
            
        return report

# Usage
monitor = ConnectionMonitor()

# Simulate events
monitor.on_connect('binance')
monitor.on_message('binance')
monitor.on_error('binance', 'Connection timeout')
monitor.on_disconnect('binance')

# Get report
report = monitor.get_status_report()
print(json.dumps(report, indent=2))
```

---

## 📝 Code Style Guidelines

### Python Style Guide

#### 1. PEP 8 Compliance
```python
# Good
def calculate_arbitrage_opportunity(symbol: str, min_spread: float) -> List[Dict]:
    """Calculate arbitrage opportunities for a symbol."""
    opportunities = []
    
    if not symbol or min_spread < 0:
        return opportunities
        
    # Implementation here
    return opportunities

# Bad
def calc_arb_opp(sym,min_spr):
    opps=[]
    if not sym or min_spr<0:return opps
    return opps
```

#### 2. Type Hints
```python
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass

@dataclass
class PriceData:
    price: float
    bid: float
    ask: float
    timestamp: int
    volume: Optional[float] = None

def process_price_update(
    symbol: str,
    exchange: str,
    data: PriceData
) -> Optional[Dict[str, Any]]:
    """Process price update with proper type hints."""
    if not data.price or data.price <= 0:
        return None
        
    return {
        'symbol': symbol,
        'exchange': exchange,
        'price': data.price,
        'spread': data.ask - data.bid
    }
```

#### 3. Documentation Standards
```python
class ExchangeConnector:
    """
    Manages WebSocket connections to cryptocurrency exchanges.
    
    This class handles connection lifecycle, message processing,
    and error recovery for exchange WebSocket connections.
    
    Attributes:
        name: Exchange name identifier
        websocket: Active WebSocket connection
        subscribed_symbols: Set of currently subscribed symbols
    
    Example:
        >>> connector = ExchangeConnector('binance')
        >>> await connector.connect()
        >>> await connector.subscribe('BTCUSDT')
    """
    
    def __init__(self, name: str) -> None:
        """
        Initialize exchange connector.
        
        Args:
            name: Exchange name (e.g., 'binance', 'bybit')
            
        Raises:
            ValueError: If name is empty or invalid
        """
        if not name or not isinstance(name, str):
            raise ValueError("Exchange name must be a non-empty string")
            
        self.name = name.lower()
        self.websocket = None
        self.subscribed_symbols = set()
    
    async def subscribe(self, symbol: str) -> bool:
        """
        Subscribe to real-time price updates for a symbol.
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            
        Returns:
            True if subscription successful, False otherwise
            
        Raises:
            ConnectionError: If WebSocket is not connected
            ValueError: If symbol format is invalid
        """
        # Implementation here
        pass
```

#### 4. Error Handling
```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class ExchangeError(Exception):
    """Base exception for exchange-related errors."""
    pass

class ConnectionError(ExchangeError):
    """Raised when connection to exchange fails."""
    pass

class SubscriptionError(ExchangeError):
    """Raised when symbol subscription fails."""
    pass

async def safe_subscribe(exchange, symbol: str) -> bool:
    """
    Safely subscribe to symbol with comprehensive error handling.
    
    Args:
        exchange: Exchange instance
        symbol: Symbol to subscribe to
        
    Returns:
        True if successful, False otherwise
    """
    try:
        await exchange.subscribe(symbol)
        logger.info(f"Successfully subscribed to {symbol} on {exchange.name}")
        return True
        
    except ConnectionError as e:
        logger.error(f"Connection error subscribing to {symbol}: {e}")
        # Attempt reconnection
        try:
            await exchange.reconnect()
            await exchange.subscribe(symbol)
            return True
        except Exception as retry_error:
            logger.error(f"Retry failed: {retry_error}")
            return False
            
    except SubscriptionError as e:
        logger.error(f"Subscription error for {symbol}: {e}")
        return False
        
    except Exception as e:
        logger.error(f"Unexpected error subscribing to {symbol}: {e}")
        return False
```

### JavaScript/TypeScript Style

#### 1. TypeScript Interfaces
```typescript
// types/index.ts
export interface PriceData {
  price: number;
  bid: number;
  ask: number;
  timestamp: number;
  volume?: number;
}

export interface ArbitrageOpportunity {
  symbol: string;
  buyExchange: string;
  sellExchange: string;
  buyPrice: number;
  sellPrice: number;
  spread: number;
  spreadPercentage: number;
  potentialProfit: number;
  profitable: boolean;
  timestamp: number;
}

export interface ExchangeStatus {
  [exchange: string]: 'connected' | 'disconnected' | 'connecting' | 'error';
}
```

#### 2. React Component Standards
```typescript
// components/PriceTable.tsx
import React, { useState, useEffect } from 'react';
import { PriceData } from '../types';

interface PriceTableProps {
  prices: Record<string, Record<string, PriceData>>;
  onSymbolSelect?: (symbol: string) => void;
}

export const PriceTable: React.FC<PriceTableProps> = ({
  prices,
  onSymbolSelect
}) => {
  const [sortBy, setSortBy] = useState<'symbol' | 'price'>('symbol');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  const sortedSymbols = React.useMemo(() => {
    return Object.keys(prices).sort((a, b) => {
      if (sortBy === 'symbol') {
        return sortOrder === 'asc' ? a.localeCompare(b) : b.localeCompare(a);
      }
      
      // Sort by price (using first available exchange)
      const priceA = Object.values(prices[a])[0]?.price || 0;
      const priceB = Object.values(prices[b])[0]?.price || 0;
      
      return sortOrder === 'asc' ? priceA - priceB : priceB - priceA;
    });
  }, [prices, sortBy, sortOrder]);

  const handleSort = (column: 'symbol' | 'price') => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('asc');
    }
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white border border-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th 
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
              onClick={() => handleSort('symbol')}
            >
              Symbol {sortBy === 'symbol' && (sortOrder === 'asc' ? '↑' : '↓')}
            </th>
            {/* More columns */}
          </tr>
        </thead>
        <tbody>
          {sortedSymbols.map((symbol) => (
            <tr
              key={symbol}
              className="hover:bg-gray-50 cursor-pointer"
              onClick={() => onSymbolSelect?.(symbol)}
            >
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {symbol}
              </td>
              {/* More cells */}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
```

### Configuration Files

#### 1. ESLint Configuration (`.eslintrc.js`)
```javascript
module.exports = {
  extends: [
    'next/core-web-vitals',
    '@typescript-eslint/recommended',
  ],
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint'],
  rules: {
    '@typescript-eslint/no-unused-vars': 'error',
    '@typescript-eslint/explicit-function-return-type': 'warn',
    'prefer-const': 'error',
    'no-var': 'error',
  },
};
```

#### 2. Prettier Configuration (`.prettierrc`)
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false
}
```

---

## 🚀 Deployment

### Production Deployment

#### 1. Environment Preparation
```bash
# Create production environment file
cat > .env.production << EOF
PYTHON_ENV=production
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=https://your-domain.com
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://localhost:6379/0
EOF
```

#### 2. Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy application code
COPY src/ ./src/
COPY backend/ ./backend/
COPY examples/ ./examples/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Expose port
EXPOSE 8000

# Start application
CMD ["python", "backend/main.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHON_ENV=production
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped
      
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
```

#### 3. Kubernetes Deployment
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crypto-price-fetcher
spec:
  replicas: 3
  selector:
    matchLabels:
      app: crypto-price-fetcher
  template:
    metadata:
      labels:
        app: crypto-price-fetcher
    spec:
      containers:
      - name: backend
        image: crypto-price-fetcher:latest
        ports:
        - containerPort: 8000
        env:
        - name: PYTHON_ENV
          value: "production"
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: crypto-price-fetcher-service
spec:
  selector:
    app: crypto-price-fetcher
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Monitoring and Observability

#### 1. Health Checks
```python
# backend/health.py
from fastapi import APIRouter
from typing import Dict, Any
import psutil
import time

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Comprehensive health check endpoint."""
    
    # System metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    # Application metrics
    active_connections = len(price_fetcher.exchanges) if price_fetcher else 0
    
    # Health status
    status = "healthy"
    if cpu_percent > 90:
        status = "degraded"
    if memory.percent > 90:
        status = "critical"
        
    return {
        "status": status,
        "timestamp": time.time(),
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": psutil.disk_usage('/').percent
        },
        "application": {
            "active_exchanges": active_connections,
            "price_fetcher_active": price_fetcher is not None,
            "websocket_connections": len(manager.active_connections)
        }
    }
```

#### 2. Metrics Collection
```python
# backend/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time

# Metrics
price_updates_total = Counter('price_updates_total', 'Total price updates', ['exchange'])
arbitrage_opportunities_total = Counter('arbitrage_opportunities_total', 'Total arbitrage opportunities')
websocket_connections_active = Gauge('websocket_connections_active', 'Active WebSocket connections')
api_request_duration = Histogram('api_request_duration_seconds', 'API request duration')

class MetricsCollector:
    def __init__(self):
        self.start_time = time.time()
        
    def record_price_update(self, exchange: str):
        price_updates_total.labels(exchange=exchange).inc()
        
    def record_arbitrage_opportunity(self):
        arbitrage_opportunities_total.inc()
        
    def update_websocket_connections(self, count: int):
        websocket_connections_active.set(count)
        
    def time_api_request(self):
        return api_request_duration.time()

metrics = MetricsCollector()

@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type="text/plain")
```

---

## 🤝 Contributing

### Contribution Workflow

#### 1. Development Setup
```bash
# Fork and clone repository
git clone https://github.com/yourusername/future-spot.git
cd future-spot

# Create feature branch
git checkout -b feature/your-feature-name

# Install dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt
cd frontend && npm install

# Install development tools
pip install black flake8 mypy pytest pytest-cov
```

#### 2. Code Quality Checks
```bash
# Run code formatting
black src/ backend/
black --check src/ backend/  # Check without formatting

# Run linting
flake8 src/ backend/

# Run type checking
mypy src/ backend/

# Run tests
pytest --cov=src --cov=backend

# Frontend checks
cd frontend
npm run lint
npm run type-check
```

#### 3. Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3.9
        
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
        
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
        
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.2.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

#### 4. Pull Request Template
```markdown
<!-- .github/pull_request_template.md -->
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review of code completed
- [ ] Code is commented where necessary
- [ ] Documentation updated
- [ ] Tests added for new functionality
```

### Code Review Guidelines

#### 1. Review Checklist
- **Functionality**: Does the code work as intended?
- **Performance**: Are there any performance implications?
- **Security**: Are there any security vulnerabilities?
- **Maintainability**: Is the code readable and maintainable?
- **Testing**: Are there adequate tests?
- **Documentation**: Is documentation updated?

#### 2. Exchange Integration Review
- **Connection Handling**: Proper WebSocket lifecycle management
- **Error Recovery**: Graceful handling of connection failures
- **Message Processing**: Correct parsing of exchange-specific messages
- **Symbol Normalization**: Proper symbol format conversion
- **Rate Limiting**: Respect for exchange rate limits

---

*This developer guide is continuously updated. For the latest information, check the repository documentation.*