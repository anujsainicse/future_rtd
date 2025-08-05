# API Reference

Complete API reference for the Cryptocurrency Perpetual Futures Arbitrage Tracking System.

## Base URL

- **Development**: `http://localhost:8000`
- **WebSocket**: `ws://localhost:8000/ws`

## Authentication

Currently, the API does not require authentication. For production deployments, consider implementing appropriate authentication mechanisms.

## REST API Endpoints

### Health & System

#### `GET /health`

Returns system health information and connection status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T12:00:00.000Z",
  "price_fetcher_active": true,
  "websocket_connections": 3
}
```

#### `GET /`

Returns basic API information.

**Response:**
```json
{
  "message": "Crypto Futures Price API",
  "status": "running"
}
```

### Price Data

#### `GET /api/prices`

Get current prices for all symbols across all exchanges.

**Response:**
```json
{
  "prices": {
    "BTC": {
      "binance": {
        "price": 43500.25,
        "bid": 43500.00,
        "ask": 43500.50,
        "timestamp": 1704110400000
      },
      "bybit": {
        "price": 43505.75,
        "bid": 43505.50,
        "ask": 43506.00,
        "timestamp": 1704110401000
      }
    }
  },
  "timestamp": "2025-01-01T12:00:00.000Z"
}
```

#### `GET /api/prices/{symbol}`

Get prices for a specific symbol across all exchanges.

**Parameters:**
- `symbol` (string, required): Symbol to query (e.g., "BTC", "ETH")

**Response:**
```json
{
  "symbol": "BTC",
  "prices": {
    "binance": {
      "price": 43500.25,
      "bid": 43500.00,
      "ask": 43500.50,
      "timestamp": 1704110400000
    },
    "bybit": {
      "price": 43505.75,
      "bid": 43505.50,
      "ask": 43506.00,
      "timestamp": 1704110401000
    }
  },
  "timestamp": "2025-01-01T12:00:00.000Z"
}
```

**Error Response:**
```json
{
  "error": "No prices found for symbol BTC"
}
```

#### `GET /api/best-prices/{symbol}`

Get best bid and ask prices across all exchanges for a symbol.

**Parameters:**
- `symbol` (string, required): Symbol to query

**Response:**
```json
{
  "symbol": "BTC",
  "best_bid": {
    "price": 43505.50,
    "exchange": "bybit",
    "timestamp": 1704110401000
  },
  "best_ask": {
    "price": 43500.50,
    "exchange": "binance",
    "timestamp": 1704110400000
  },
  "spread": -5.00,
  "spread_percentage": -0.011
}
```

#### `GET /api/summary`

Get market summary statistics.

**Response:**
```json
{
  "total_symbols": 53,
  "total_exchanges": 11,
  "symbols": ["BTC", "ETH", "SOL", "..."],
  "exchanges": ["binance", "bybit", "okx", "..."],
  "price_count": 158,
  "last_update": 1704110400.123
}
```

### Arbitrage Detection

#### `GET /api/arbitrage`

Get all current arbitrage opportunities with minimum 0.05% spread.

**Response:**
```json
{
  "opportunities": [
    {
      "symbol": "BTC",
      "exchanges": ["binance", "okx"],
      "spread": 25.75,
      "spread_percentage": 0.059,
      "higher": "okx",
      "lower": "binance",
      "higher_price": 43525.75,
      "lower_price": 43500.00,
      "profitable": true,
      "buy_exchange": "binance",
      "sell_exchange": "okx",
      "potential_profit": 0.059,
      "timestamp": 1704110401000
    }
  ],
  "timestamp": "2025-01-01T12:00:00.000Z"
}
```

#### `GET /api/arbitrage/{symbol}`

Get arbitrage opportunities for a specific symbol.

**Parameters:**
- `symbol` (string, required): Symbol to analyze
- `min_spread` (float, optional): Minimum spread percentage (default: 0.1)

**Query Example:**
```
GET /api/arbitrage/BTC?min_spread=0.05
```

**Response:**
```json
{
  "symbol": "BTC",
  "opportunities": [
    {
      "symbol": "BTC",
      "exchanges": ["binance", "okx"],
      "spread": 25.75,
      "spread_percentage": 0.059,
      "higher": "okx",
      "lower": "binance",
      "higher_price": 43525.75,
      "lower_price": 43500.00,
      "profitable": true,
      "buy_exchange": "binance",
      "sell_exchange": "okx",
      "potential_profit": 0.059,
      "timestamp": 1704110401000
    }
  ],
  "timestamp": "2025-01-01T12:00:00.000Z"
}
```

#### `GET /api/spread/{symbol}/{exchange1}/{exchange2}`

Get spread information between two specific exchanges for a symbol.

**Parameters:**
- `symbol` (string, required): Symbol to analyze
- `exchange1` (string, required): First exchange name
- `exchange2` (string, required): Second exchange name

**Response:**
```json
{
  "symbol": "BTC",
  "exchanges": ["binance", "okx"],
  "spread": 25.75,
  "spread_percentage": 0.059,
  "higher": "okx",
  "lower": "binance",
  "higher_price": 43525.75,
  "lower_price": 43500.00,
  "timestamp": 1704110401000
}
```

#### `GET /api/arbitrage/{symbol}/alert-status`

Get arbitrage alert status and cooldown information for a symbol.

**Parameters:**
- `symbol` (string, required): Symbol to check

**Response:**
```json
{
  "symbol": "BTC",
  "can_send_alert": false,
  "last_alert_time": 1704110100.123,
  "seconds_since_last_alert": 180.5,
  "seconds_until_next_alert": 119.5,
  "cooldown_seconds": 300,
  "timestamp": "2025-01-01T12:00:00.000Z"
}
```

### Configuration Management

#### `POST /api/reload-config`

Reload the symbol configuration from `futures_symbols.txt` without restarting the server.

**Response (Success):**
```json
{
  "status": "success",
  "message": "Configuration reloaded with 11 exchanges",
  "exchanges": ["binance", "bybit", "okx", "kucoin", "deribit", "bitget", "gateio", "mexc", "bitmex", "phemex", "coindcx"],
  "total_symbols": 453,
  "timestamp": "2025-01-01T12:00:00.000Z"
}
```

**Response (Error):**
```json
{
  "error": "Failed to reload configuration: Invalid file format"
}
```

## WebSocket API

### Connection

**Endpoint:** `ws://localhost:8000/ws`

### Message Types

#### Connection Response

Upon connection, the client receives initial data:

```json
{
  "type": "market_summary",
  "data": {
    "total_symbols": 53,
    "total_exchanges": 11,
    "symbols": ["BTC", "ETH", "..."],
    "exchanges": ["binance", "bybit", "..."],
    "price_count": 158,
    "last_update": 1704110400.123
  }
}
```

```json
{
  "type": "initial_prices",
  "data": {
    "BTC": {
      "binance": {
        "price": 43500.25,
        "bid": 43500.00,
        "ask": 43500.50,
        "timestamp": 1704110400000
      }
    }
  }
}
```

#### Real-time Updates

**Price Update:**
```json
{
  "type": "price_update",
  "data": {
    "symbol": "BTC",
    "exchange": "binance",
    "price": 43501.75,
    "bid": 43501.50,
    "ask": 43502.00,
    "timestamp": 1704110410000
  }
}
```

**Arbitrage Opportunities:**
```json
{
  "type": "arbitrage_opportunities",
  "data": [
    {
      "symbol": "BTC",
      "buy_exchange": "binance",
      "sell_exchange": "okx",
      "buy_price": 43500.00,
      "sell_price": 43525.75,
      "spread": 25.75,
      "spread_percentage": 0.059,
      "potential_profit": 0.059
    }
  ]
}
```

## Error Handling

### HTTP Status Codes

- **200**: Success
- **400**: Bad Request - Invalid parameters
- **404**: Not Found - Resource doesn't exist
- **500**: Internal Server Error

### Error Response Format

```json
{
  "error": "Description of the error",
  "details": "Additional error details (optional)",
  "timestamp": "2025-01-01T12:00:00.000Z"
}
```

## Rate Limiting

### Arbitrage Alerts

- **Cooldown Period**: 5 minutes per symbol
- **Purpose**: Prevent alert spam for the same arbitrage opportunity
- **Status Check**: Use `/api/arbitrage/{symbol}/alert-status` to check cooldown

### WebSocket Connections

- **Max Connections**: No hard limit (memory-based)
- **Automatic Cleanup**: Stale connections are automatically removed
- **Reconnection**: Supported with exponential backoff

## Data Models

### Price Data
```typescript
interface PriceData {
  symbol: string;
  exchange: string;
  price: number;
  bid: number | null;
  ask: number | null;
  timestamp: number;
}
```

### Arbitrage Opportunity
```typescript
interface ArbitrageOpportunity {
  symbol: string;
  exchanges: [string, string];
  spread: number;
  spread_percentage: number;
  higher: string;
  lower: string;
  higher_price: number;
  lower_price: number;
  profitable: boolean;
  buy_exchange: string;
  sell_exchange: string;
  potential_profit: number;
  timestamp: number;
}
```

### Market Summary
```typescript
interface MarketSummary {
  total_symbols: number;
  total_exchanges: number;
  symbols: string[];
  exchanges: string[];
  price_count: number;
  last_update: number;
}
```

## Interactive API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation powered by FastAPI and Swagger UI.

## SDK Examples

### Python
```python
import requests

# Get all prices
response = requests.get('http://localhost:8000/api/prices')
prices = response.json()

# Get arbitrage opportunities
response = requests.get('http://localhost:8000/api/arbitrage')
opportunities = response.json()
```

### JavaScript
```javascript
// Fetch prices
const response = await fetch('http://localhost:8000/api/prices');
const prices = await response.json();

// WebSocket connection
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

### cURL
```bash
# Get market summary
curl http://localhost:8000/api/summary

# Get BTC arbitrage opportunities
curl http://localhost:8000/api/arbitrage/BTC

# Reload configuration
curl -X POST http://localhost:8000/api/reload-config
```