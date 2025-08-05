# API Reference - Crypto Futures Price Fetcher

## 📋 Table of Contents

1. [Authentication](#authentication)
2. [Base URL](#base-url)
3. [Response Format](#response-format)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [REST API Endpoints](#rest-api-endpoints)
7. [WebSocket API](#websocket-api)
8. [Data Models](#data-models)
9. [Code Examples](#code-examples)

---

## 🔐 Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

> **Note**: Authentication may be added in future versions for production deployments.

---

## 🌐 Base URL

- **Development**: `http://localhost:8000`
- **Production**: Configure based on your deployment

---

## 📊 Response Format

All API responses follow a consistent JSON format:

### Success Response
```json
{
  "data": { ... },
  "timestamp": "2023-12-01T12:00:00.000Z",
  "status": "success"
}
```

### Error Response
```json
{
  "error": "Error description",
  "code": "ERROR_CODE",
  "timestamp": "2023-12-01T12:00:00.000Z",
  "status": "error"
}
```

---

## ⚠️ Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| `200` | Success |
| `400` | Bad Request - Invalid parameters |
| `404` | Not Found - Resource not found |
| `500` | Internal Server Error |
| `503` | Service Unavailable - Exchange connections down |

### Error Codes

| Code | Description |
|------|-------------|
| `EXCHANGE_DOWN` | One or more exchanges are disconnected |
| `SYMBOL_NOT_FOUND` | Requested symbol not available |
| `INVALID_PARAMETERS` | Invalid request parameters |
| `RATE_LIMIT_EXCEEDED` | Too many requests |

---

## 🚦 Rate Limiting

Current rate limits (may be implemented in future versions):
- **REST API**: 100 requests per minute per IP
- **WebSocket**: 1 connection per IP

---

## 🔌 REST API Endpoints

### Health & Status

#### `GET /health`
Get system health status and connection information.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2023-12-01T12:00:00.000Z",
  "price_fetcher_active": true,
  "websocket_connections": 5,
  "exchange_status": {
    "binance": "connected",
    "bybit": "connected",
    "okx": "disconnected"
  }
}
```

#### `GET /`
Get API root information and version.

**Response:**
```json
{
  "message": "Crypto Futures Price API",
  "version": "1.0.0",
  "documentation": "/docs",
  "status": "running"
}
```

---

### Price Data Endpoints

#### `GET /api/prices`
Get all current prices from all exchanges.

**Response:**
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
    },
    "ETHUSDT": {
      "binance": {
        "price": 4125.30,
        "bid": 4125.20,
        "ask": 4125.40,
        "timestamp": 1638360000500
      }
    }
  },
  "timestamp": "2023-12-01T12:00:00.000Z"
}
```

#### `GET /api/prices/{symbol}`
Get prices for a specific symbol across all exchanges.

**Parameters:**
- `symbol` (path): Trading symbol (e.g., BTCUSDT, ETHUSDT)

**Example:** `GET /api/prices/BTCUSDT`

**Response:**
```json
{
  "symbol": "BTCUSDT",
  "prices": {
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
    },
    "okx": {
      "price": 43251.75,
      "bid": 43251.70,
      "ask": 43251.80,
      "timestamp": 1638360000750
    }
  },
  "timestamp": "2023-12-01T12:00:00.000Z"
}
```

#### `GET /api/best-prices/{symbol}`
Get the best bid and ask prices across all exchanges for a symbol.

**Parameters:**
- `symbol` (path): Trading symbol

**Example:** `GET /api/best-prices/BTCUSDT`

**Response:**
```json
{
  "symbol": "BTCUSDT",
  "best_bid": {
    "price": 43252.00,
    "exchange": "bybit",
    "timestamp": 1638360001000
  },
  "best_ask": {
    "price": 43250.60,
    "exchange": "binance",
    "timestamp": 1638360000000
  },
  "spread": 1.40,
  "spread_percentage": 0.0032,
  "timestamp": "2023-12-01T12:00:00.000Z"
}
```

#### `GET /api/summary`
Get market summary statistics.

**Response:**
```json
{
  "total_symbols": 15,
  "total_exchanges": 11,
  "symbols": ["BTCUSDT", "ETHUSDT", "BTC-PERPETUAL"],
  "exchanges": ["binance", "bybit", "okx", "deribit"],
  "price_count": 45,
  "last_update": 1638360001000,
  "uptime_seconds": 3600,
  "connections_active": 10
}
```

---

### Arbitrage Endpoints

#### `GET /api/arbitrage`
Get all current arbitrage opportunities across all symbols.

**Query Parameters:**
- `min_spread` (optional): Minimum spread percentage (default: 0.05)
- `limit` (optional): Maximum number of opportunities to return (default: 20)

**Example:** `GET /api/arbitrage?min_spread=0.1&limit=10`

**Response:**
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
      "profitable": true,
      "timestamp": 1638360001000
    },
    {
      "symbol": "ETHUSDT",
      "buy_exchange": "okx",
      "sell_exchange": "deribit",
      "buy_price": 4125.20,
      "sell_price": 4127.30,
      "spread": 2.10,
      "spread_percentage": 0.0051,
      "potential_profit": 0.0051,
      "profitable": true,
      "timestamp": 1638360001500
    }
  ],
  "total_opportunities": 15,
  "timestamp": "2023-12-01T12:00:00.000Z"
}
```

#### `GET /api/arbitrage/{symbol}`
Get arbitrage opportunities for a specific symbol.

**Parameters:**
- `symbol` (path): Trading symbol
- `min_spread` (query, optional): Minimum spread percentage (default: 0.1)

**Example:** `GET /api/arbitrage/BTCUSDT?min_spread=0.05`

**Response:**
```json
{
  "symbol": "BTCUSDT",
  "opportunities": [
    {
      "buy_exchange": "binance",
      "sell_exchange": "bybit",
      "buy_price": 43250.50,
      "sell_price": 43252.10,
      "spread": 1.60,
      "spread_percentage": 0.0037,
      "potential_profit": 0.0037,
      "profitable": true,
      "timestamp": 1638360001000
    }
  ],
  "timestamp": "2023-12-01T12:00:00.000Z"
}
```

#### `GET /api/spread/{symbol}/{exchange1}/{exchange2}`
Get spread between two specific exchanges for a symbol.

**Parameters:**
- `symbol` (path): Trading symbol
- `exchange1` (path): First exchange name
- `exchange2` (path): Second exchange name

**Example:** `GET /api/spread/BTCUSDT/binance/bybit`

**Response:**
```json
{
  "symbol": "BTCUSDT",
  "exchange1": "binance",
  "exchange2": "bybit",
  "price1": 43250.50,
  "price2": 43252.10,
  "spread": 1.60,
  "spread_percentage": 0.0037,
  "direction": "exchange2_higher",
  "arbitrage_direction": {
    "buy": "binance",
    "sell": "bybit"
  },
  "timestamp": "2023-12-01T12:00:00.000Z"
}
```

---

## 🔌 WebSocket API

### Connection
Connect to the WebSocket endpoint for real-time price updates and arbitrage notifications.

**Endpoint:** `ws://localhost:8000/ws`

### Message Types

#### 1. Initial Data
Upon connection, you'll receive initial market data:

```json
{
  "type": "market_summary",
  "data": {
    "total_symbols": 15,
    "total_exchanges": 11,
    "symbols": ["BTCUSDT", "ETHUSDT"],
    "exchanges": ["binance", "bybit", "okx"]
  }
}
```

```json
{
  "type": "initial_prices",
  "data": {
    "BTCUSDT": {
      "binance": {
        "price": 43250.50,
        "bid": 43250.40,
        "ask": 43250.60,
        "timestamp": 1638360000000
      }
    }
  }
}
```

#### 2. Price Updates
Real-time price updates as they occur:

```json
{
  "type": "price_update",
  "data": {
    "symbol": "BTCUSDT",
    "exchange": "binance",
    "price": 43251.20,
    "bid": 43251.10,
    "ask": 43251.30,
    "timestamp": 1638360002000
  }
}
```

#### 3. Arbitrage Opportunities
Real-time arbitrage opportunities (top 5):

```json
{
  "type": "arbitrage_opportunities",
  "data": [
    {
      "symbol": "BTCUSDT",
      "buy_exchange": "binance",
      "sell_exchange": "bybit",
      "buy_price": 43250.50,
      "sell_price": 43252.10,
      "spread": 1.60,
      "spread_percentage": 0.0037,
      "potential_profit": 0.0037
    }
  ]
}
```

### Client Example (JavaScript)

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = function(event) {
    console.log('Connected to WebSocket');
};

ws.onmessage = function(event) {
    const message = JSON.parse(event.data);
    
    switch(message.type) {
        case 'price_update':
            handlePriceUpdate(message.data);
            break;
        case 'arbitrage_opportunities':
            handleArbitrageOpportunities(message.data);
            break;
        case 'market_summary':
            handleMarketSummary(message.data);
            break;
    }
};

ws.onclose = function(event) {
    console.log('WebSocket connection closed');
    // Implement reconnection logic
};

ws.onerror = function(error) {
    console.error('WebSocket error:', error);
};
```

---

## 📊 Data Models

### Price Data Model
```typescript
interface PriceData {
  price: number;         // Last traded price or mid-price
  bid: number;          // Best bid price
  ask: number;          // Best ask price  
  timestamp: number;    // Unix timestamp in milliseconds
}
```

### Arbitrage Opportunity Model
```typescript
interface ArbitrageOpportunity {
  symbol: string;              // Trading symbol
  buy_exchange: string;        // Exchange to buy from (lower price)
  sell_exchange: string;       // Exchange to sell to (higher price)
  buy_price: number;          // Price on buy exchange
  sell_price: number;         // Price on sell exchange
  spread: number;             // Absolute price difference
  spread_percentage: number;   // Percentage spread
  potential_profit: number;    // Potential profit percentage
  profitable: boolean;        // Whether opportunity is profitable
  timestamp: number;          // Unix timestamp in milliseconds
}
```

### Market Summary Model
```typescript
interface MarketSummary {
  total_symbols: number;      // Total number of tracked symbols
  total_exchanges: number;    // Total number of connected exchanges
  symbols: string[];          // List of tracked symbols
  exchanges: string[];        // List of connected exchanges
  price_count: number;        // Total number of price points
  last_update: number;        // Last price update timestamp
  uptime_seconds?: number;    // Server uptime in seconds
  connections_active?: number; // Active WebSocket connections
}
```

### Exchange Status Model
```typescript
interface ExchangeStatus {
  [exchange: string]: 'connected' | 'disconnected' | 'connecting' | 'error';
}
```

---

## 💻 Code Examples

### Python Examples

#### 1. Basic Price Fetching
```python
import requests

# Get all prices
response = requests.get('http://localhost:8000/api/prices')
prices = response.json()

print(f"BTC Price on Binance: ${prices['prices']['BTCUSDT']['binance']['price']}")
```

#### 2. Arbitrage Monitoring
```python
import requests
import time

def monitor_arbitrage():
    while True:
        response = requests.get('http://localhost:8000/api/arbitrage?min_spread=0.1')
        opportunities = response.json()['opportunities']
        
        for opp in opportunities:
            print(f"Arbitrage: {opp['symbol']} - "
                  f"Buy on {opp['buy_exchange']} at {opp['buy_price']}, "
                  f"Sell on {opp['sell_exchange']} at {opp['sell_price']}, "
                  f"Profit: {opp['potential_profit']:.2%}")
        
        time.sleep(5)

monitor_arbitrage()
```

#### 3. WebSocket Client
```python
import asyncio
import websockets
import json

async def websocket_client():
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            
            if data['type'] == 'price_update':
                price_data = data['data']
                print(f"Price Update: {price_data['symbol']} on {price_data['exchange']} = ${price_data['price']}")
            
            elif data['type'] == 'arbitrage_opportunities':
                for opp in data['data']:
                    print(f"Arbitrage: {opp['symbol']} - {opp['spread_percentage']:.2%} profit")

asyncio.run(websocket_client())
```

### JavaScript Examples

#### 1. Fetch API Usage
```javascript
// Get prices for Bitcoin
async function getBitcoinPrices() {
    try {
        const response = await fetch('http://localhost:8000/api/prices/BTCUSDT');
        const data = await response.json();
        
        console.log('Bitcoin Prices:');
        Object.entries(data.prices).forEach(([exchange, priceData]) => {
            console.log(`${exchange}: $${priceData.price}`);
        });
    } catch (error) {
        console.error('Error fetching prices:', error);
    }
}

getBitcoinPrices();
```

#### 2. Real-time Price Display
```javascript
class PriceTracker {
    constructor() {
        this.ws = new WebSocket('ws://localhost:8000/ws');
        this.prices = {};
        this.setupWebSocket();
    }
    
    setupWebSocket() {
        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            
            if (message.type === 'price_update') {
                const { symbol, exchange, price } = message.data;
                
                if (!this.prices[symbol]) {
                    this.prices[symbol] = {};
                }
                
                this.prices[symbol][exchange] = price;
                this.updateDisplay(symbol, exchange, price);
            }
        };
        
        this.ws.onclose = () => {
            console.log('Connection closed, reconnecting...');
            setTimeout(() => this.reconnect(), 5000);
        };
    }
    
    updateDisplay(symbol, exchange, price) {
        const element = document.getElementById(`${symbol}-${exchange}`);
        if (element) {
            element.textContent = `$${price.toFixed(2)}`;
        }
    }
    
    reconnect() {
        this.ws = new WebSocket('ws://localhost:8000/ws');
        this.setupWebSocket();
    }
}

const tracker = new PriceTracker();
```

#### 3. Arbitrage Alert System
```javascript
class ArbitrageMonitor {
    constructor(minSpread = 0.001) {
        this.minSpread = minSpread;
        this.ws = new WebSocket('ws://localhost:8000/ws');
        this.setupWebSocket();
    }
    
    setupWebSocket() {
        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            
            if (message.type === 'arbitrage_opportunities') {
                message.data.forEach(opportunity => {
                    if (opportunity.spread_percentage >= this.minSpread) {
                        this.alertArbitrage(opportunity);
                    }
                });
            }
        };
    }
    
    alertArbitrage(opportunity) {
        const profit = (opportunity.spread_percentage * 100).toFixed(2);
        
        console.log(`🚨 ARBITRAGE ALERT 🚨`);
        console.log(`Symbol: ${opportunity.symbol}`);
        console.log(`Buy: ${opportunity.buy_exchange} at $${opportunity.buy_price}`);
        console.log(`Sell: ${opportunity.sell_exchange} at $${opportunity.sell_price}`);
        console.log(`Potential Profit: ${profit}%`);
        console.log('---');
        
        // Send browser notification
        if (Notification.permission === 'granted') {
            new Notification('Arbitrage Opportunity!', {
                body: `${opportunity.symbol}: ${profit}% profit potential`,
                icon: '/icon.png'
            });
        }
    }
}

// Request notification permission
Notification.requestPermission();

// Start monitoring
const monitor = new ArbitrageMonitor(0.005); // 0.5% minimum spread
```

### cURL Examples

#### 1. Basic API Testing
```bash
# Health check
curl -X GET "http://localhost:8000/health"

# Get all prices
curl -X GET "http://localhost:8000/api/prices"

# Get Bitcoin prices
curl -X GET "http://localhost:8000/api/prices/BTCUSDT"

# Get arbitrage opportunities with minimum 0.1% spread
curl -X GET "http://localhost:8000/api/arbitrage?min_spread=0.001"

# Get spread between Binance and Bybit for Bitcoin
curl -X GET "http://localhost:8000/api/spread/BTCUSDT/binance/bybit"
```

#### 2. JSON Pretty Printing
```bash
# Get prices with formatted JSON output
curl -s "http://localhost:8000/api/prices/BTCUSDT" | python -m json.tool

# Get arbitrage opportunities with jq formatting
curl -s "http://localhost:8000/api/arbitrage" | jq '.opportunities[] | select(.spread_percentage > 0.001)'
```

---

## 🔄 Changelog

### v1.0.0 (Current)
- Initial API release
- 11 exchange integrations
- Real-time WebSocket streaming
- Arbitrage detection
- Full REST API

### Planned v1.1.0
- Authentication system
- Rate limiting
- Historical data endpoints
- Advanced filtering options
- Batch operations

---

*For additional support or questions about the API, please refer to the main documentation or open an issue on GitHub.*