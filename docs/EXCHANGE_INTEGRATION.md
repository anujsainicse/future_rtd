# Exchange Integration Guide

Complete guide for integrating cryptocurrency exchanges with the arbitrage tracking system.

## Overview

The system currently supports **11 major cryptocurrency exchanges**, each with specialized WebSocket implementations for real-time perpetual futures price tracking.

## Supported Exchanges

| Exchange | Status | Connection Type | Native Format | Rate Limits |
|----------|--------|-----------------|---------------|-------------|
| **Binance** | ✅ Active | WebSocket | BTCUSDT | 10 conn/IP |
| **Bybit** | ✅ Active | WebSocket | BTCUSDT | 100 conn/min |
| **OKX** | ✅ Active | WebSocket | BTC-USDT-SWAP | 240 conn/hour |
| **KuCoin** | ✅ Active | REST + WebSocket | XBTUSDTM | Token-based |
| **Deribit** | ✅ Active | JSON-RPC WebSocket | BTC-PERPETUAL | No limit |
| **BitMEX** | ✅ Active | WebSocket | XBTUSD | 20 conn/IP |
| **Gate.io** | ✅ Active | WebSocket | BTC_USDT | 100 conn/IP |
| **MEXC** | ✅ Active | WebSocket | BTC_USDT | No limit |
| **Bitget** | ✅ Active | WebSocket | BTCUSDT | 50 conn/IP |
| **Phemex** | ✅ Active | WebSocket | BTCUSD | 200 conn/IP |
| **CoinDCX** | ✅ Active | Socket.io | BTCUSDT | 10 conn/IP |

## Exchange Implementation Details

### 1. Binance (binance_exchange.py)

**WebSocket URL:** `wss://fstream.binance.com/ws`

**Connection Details:**
- **Protocol**: Native WebSocket with JSON messages
- **Subscription Format**: `{"method": "SUBSCRIBE", "params": ["btcusdt@bookTicker"], "id": 1}`
- **Message Format**: Book ticker with best bid/ask

**Key Features:**
- Automatic subscription confirmation handling
- Ping/pong heartbeat support
- Comprehensive error handling with reconnection

**Example Implementation:**
```python
class BinanceExchange(BaseExchange):
    def __init__(self):
        super().__init__("binance", "wss://fstream.binance.com/ws")
        self.request_id = 0
    
    async def subscribe(self, symbol: str):
        self.request_id += 1
        message = {
            "method": "SUBSCRIBE",
            "params": [f"{symbol.lower()}@bookTicker"],
            "id": self.request_id
        }
        await self.send_message(json.dumps(message))
```

### 2. Bybit (bybit_exchange.py)

**WebSocket URL:** `wss://stream.bybit.com/v5/public/linear`

**Connection Details:**
- **Protocol**: Native WebSocket with JSON-RPC
- **Subscription Format**: `{"op": "subscribe", "args": ["orderbook.1.BTCUSDT"], "req_id": "1"}`
- **Message Format**: Orderbook level 1 (best bid/ask)

**Key Features:**
- Request ID tracking for subscription confirmations
- Automatic topic parsing from messages
- Symbol normalization for unified display

**Rate Limiting:**
- 100 connections per minute per IP
- 500 operations per connection per second

### 3. OKX (okx_exchange.py)

**WebSocket URL:** `wss://ws.okx.com:8443/ws/v5/public`

**Connection Details:**
- **Protocol**: Native WebSocket with structured messages
- **Subscription Format**: `{"op": "subscribe", "args": [{"channel": "books5", "instId": "BTC-USDT-SWAP"}]}`
- **Message Format**: Order book with 5 levels (uses best bid/ask)

**Unique Features:**
- Institutional ID format (BTC-USDT-SWAP)
- Channel-based subscription model
- Comprehensive market data structure

### 4. KuCoin (kucoin_exchange.py)

**WebSocket URL:** Dynamic (token-based)

**Connection Details:**
- **Protocol**: REST API for token + WebSocket
- **Two-step Process**: 
  1. POST to `/api/v1/bullet-public` for token
  2. Connect to WebSocket with token
- **Subscription Format**: `{"type": "subscribe", "topic": "/contractMarket/tickerV2:XBTUSDTM"}`

**Implementation Flow:**
```python
async def connect(self):
    # Step 1: Get connection token
    token_data = await self.get_connection_token()
    
    # Step 2: Connect to WebSocket
    ws_url = f"{token_data['instanceServers'][0]['endpoint']}?token={token_data['token']}"
    self.websocket = await websockets.connect(ws_url)
```

### 5. Deribit (deribit_exchange.py)

**WebSocket URL:** `wss://www.deribit.com/ws/api/v2`

**Connection Details:**
- **Protocol**: JSON-RPC 2.0 over WebSocket
- **Subscription Format**: `{"method": "public/subscribe", "params": {"channels": ["book.BTC-PERPETUAL.raw"]}, "id": 1}`
- **Message Format**: Order book with comprehensive depth

**Unique Features:**
- Professional derivatives focus (BTC-PERPETUAL, ETH-PERPETUAL)
- JSON-RPC 2.0 protocol compliance
- USD-margined contracts (not USDT)

### 6. BitMEX (bitmex_exchange.py)

**WebSocket URL:** `wss://ws.bitmex.com/realtime`

**Connection Details:**
- **Protocol**: Native WebSocket with topic-based subscriptions
- **Subscription Format**: `{"op": "subscribe", "args": ["orderBookL2_25:XBTUSD"]}`
- **Message Format**: Order book Level 2 data

**Key Features:**
- Partial and update message handling
- Symbol ID mapping (XBTUSD for BTC perpetual)
- Comprehensive order book management

### 7. Gate.io (gateio_exchange.py)

**WebSocket URL:** `wss://fx-ws.gateio.ws/v4/ws/usdt`

**Connection Details:**
- **Protocol**: Native WebSocket with channel subscriptions
- **Subscription Format**: `{"method": "futures.book_ticker", "params": ["BTC_USDT"], "id": 1}`
- **Message Format**: Book ticker with timestamp

**Rate Limiting:**
- 100 connections per IP
- Authentication required for private channels

### 8. MEXC (mexc_exchange.py)

**WebSocket URL:** `wss://contract.mexc.com/edge`

**Connection Details:**
- **Protocol**: Native WebSocket with method-based subscriptions
- **Subscription Format**: `{"method": "sub.ticker", "param": {"symbol": "BTC_USDT"}}`
- **Message Format**: Ticker data with comprehensive statistics

### 9. Bitget (bitget_exchange.py)

**WebSocket URL:** `wss://ws.bitget.com/mix/v1/stream`

**Connection Details:**
- **Protocol**: Native WebSocket with operation-based messages
- **Subscription Format**: `{"op": "subscribe", "args": [{"instType": "USDT-FUTURES", "channel": "books5", "instId": "BTCUSDT"}]}`
- **Message Format**: Order book with 5 levels

**Key Features:**
- InstType classification (USDT-FUTURES for perpetual contracts)
- Comprehensive subscription management
- Real-time order book updates

### 10. Phemex (phemex_exchange.py)

**WebSocket URL:** `wss://ws.phemex.com`

**Connection Details:**
- **Protocol**: Native WebSocket with ID-based subscriptions
- **Subscription Format**: `{"method": "book.subscribe", "params": ["BTCUSD"], "id": 1}`
- **Message Format**: Order book with bid/ask arrays

**Unique Features:**
- USD-margined perpetual contracts
- Custom ETH perpetual format (cETHUSD)
- Professional trading focus

**Special Symbol Handling:**
```python
def normalize_symbol(self, symbol: str) -> str:
    if symbol.startswith('c') and symbol.endswith('USD'):
        return symbol  # Keep original case for perpetual contracts like cETHUSD
    return symbol.upper()
```

### 11. CoinDCX (coindcx_exchange.py)

**WebSocket URL:** `https://stream.coindcx.com`

**Connection Details:**
- **Protocol**: Socket.io over HTTPS
- **Subscription Format**: `socket.emit('join', {'channelName': 'B-BTC_USDT'})`
- **Message Format**: Real-time price updates

**Key Features:**
- Socket.io implementation (not native WebSocket)
- Indian exchange with USDT perpetual contracts
- Real-time price streaming

## Adding New Exchanges

### Step 1: Create Exchange Class

Create a new file in `src/exchanges/` following the naming convention:

```python
# src/exchanges/new_exchange.py
import json
import logging
from .base_exchange import BaseExchange

logger = logging.getLogger(__name__)

class NewExchange(BaseExchange):
    def __init__(self):
        super().__init__("newexchange", "wss://api.newexchange.com/ws")
    
    async def subscribe(self, symbol: str):
        message = {
            "method": "subscribe",
            "params": {"symbol": symbol}
        }
        await self.send_message(json.dumps(message))
    
    def parse_message(self, message: str) -> dict:
        try:
            data = json.loads(message)
            
            # Parse exchange-specific message format
            if 'ticker' in data:
                return {
                    'symbol': self.normalize_symbol(data['symbol']),
                    'exchange': self.name,
                    'price': float(data['price']),
                    'bid': float(data['bid']) if data.get('bid') else None,
                    'ask': float(data['ask']) if data.get('ask') else None,
                    'timestamp': int(data.get('timestamp', 0))
                }
        except Exception as e:
            logger.error(f"Error parsing {self.name} message: {e}")
            return None
    
    def normalize_symbol(self, symbol: str) -> str:
        # Convert exchange-specific symbol to unified format
        # Example: BTCUSDT -> BTC
        return symbol.replace('USDT', '').upper()
```

### Step 2: Update Main Application

Add the new exchange to the main application:

```python
# main.py or backend/main.py
from src.exchanges.new_exchange import NewExchange

# Add to exchange classes mapping
self.exchange_classes = {
    'binance': BinanceExchange,
    'bybit': BybitExchange,
    # ... existing exchanges
    'newexchange': NewExchange,  # Add new exchange
}

# Add to supported exchanges list
self.supported_exchanges = [
    'binance', 'bybit', 'okx', 'kucoin', 'deribit', 
    'bitget', 'gateio', 'mexc', 'bitmex', 'phemex', 
    'coindcx', 'newexchange'  # Add new exchange
]
```

### Step 3: Update Configuration

Add symbols for the new exchange in `futures_symbols.txt`:

```text
# New Exchange - USDT-Margined Perpetual Futures
BTC:BTCUSDT:newexchange
ETH:ETHUSDT:newexchange
SOL:SOLUSDT:newexchange
```

### Step 4: Test Integration

1. **Unit Testing**: Test WebSocket connection and message parsing
2. **Integration Testing**: Verify data flow through the system
3. **Performance Testing**: Monitor resource usage and latency

## Base Exchange Interface

All exchanges inherit from `BaseExchange` which provides:

### Core Methods

```python
class BaseExchange:
    async def connect(self) -> bool
    async def disconnect(self) -> None
    async def subscribe(self, symbol: str) -> None
    async def send_message(self, message: str) -> None
    def parse_message(self, message: str) -> dict
    def normalize_symbol(self, symbol: str) -> str
    def on(self, event: str, callback) -> None
    def emit(self, event: str, data) -> None
```

### Event System

- **price_update**: Emitted when new price data is received
- **connection_status**: Emitted on connection state changes
- **error**: Emitted when errors occur

### Error Handling

- **Automatic Reconnection**: Exponential backoff with max attempts
- **Message Validation**: Comprehensive error checking
- **Logging**: Detailed logging for debugging

## Symbol Normalization

Each exchange uses different symbol formats. The system normalizes these to a unified format:

### Example Mappings

| Exchange | Native Symbol | Normalized Symbol |
|----------|---------------|-------------------|
| Binance | BTCUSDT | BTC |
| OKX | BTC-USDT-SWAP | BTC |
| KuCoin | XBTUSDTM | BTC |
| Deribit | BTC-PERPETUAL | BTC |
| BitMEX | XBTUSD | BTC |

### Implementation

```python
def normalize_symbol(self, symbol: str) -> str:
    """Convert exchange-specific symbol to unified format."""
    # Remove common suffixes and prefixes
    symbol = symbol.upper()
    
    # Exchange-specific normalization
    if self.name == 'okx':
        return symbol.split('-')[0]  # BTC-USDT-SWAP -> BTC
    elif self.name == 'kucoin':
        return symbol.replace('USDTM', '').replace('XBT', 'BTC')
    elif self.name == 'deribit':
        return symbol.split('-')[0]  # BTC-PERPETUAL -> BTC
    
    # Default normalization
    return symbol.replace('USDT', '').replace('USD', '')
```

## WebSocket Connection Management

### Connection Lifecycle

1. **Initialize**: Create WebSocket connection
2. **Authenticate**: If required by exchange
3. **Subscribe**: Subscribe to symbol streams
4. **Listen**: Handle incoming messages
5. **Reconnect**: On connection loss
6. **Cleanup**: Proper resource cleanup

### Health Monitoring

```python
async def health_check(self):
    """Check connection health and reconnect if needed."""
    if not self.websocket or self.websocket.closed:
        logger.warning(f"{self.name} connection lost, reconnecting...")
        await self.connect()
        
        # Re-subscribe to all symbols
        for symbol in self.subscribed_symbols:
            await self.subscribe(symbol)
```

## Rate Limiting and Best Practices

### Connection Limits

- **Respect Exchange Limits**: Each exchange has different connection limits
- **Connection Pooling**: Reuse connections when possible
- **Graceful Degradation**: Handle rate limit errors gracefully

### Message Handling

- **Async Processing**: Use async/await for non-blocking operations
- **Error Isolation**: Don't let one exchange failure affect others
- **Performance Monitoring**: Track message processing times

### Production Considerations

- **Authentication**: Implement API key management for private data
- **Load Balancing**: Distribute connections across multiple IPs
- **Monitoring**: Comprehensive logging and alerting
- **Backup Connections**: Redundant connections for critical exchanges

## Troubleshooting

### Common Issues

1. **Connection Failures**
   - Check network connectivity
   - Verify WebSocket URL
   - Review exchange-specific requirements

2. **Authentication Errors**
   - Validate API credentials
   - Check IP whitelist settings
   - Verify timestamp synchronization

3. **Message Parsing Errors**
   - Review exchange API documentation
   - Check message format changes
   - Validate JSON structure

4. **Rate Limiting**
   - Implement exponential backoff
   - Monitor connection counts
   - Use connection pooling

### Debug Logging

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This will show detailed WebSocket messages and connection events for all exchanges.