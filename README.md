# Crypto Futures Price Fetcher

A Python application that fetches real-time cryptocurrency futures prices from multiple exchanges via WebSocket connections. Designed for arbitrage calculations and price monitoring across Binance, Bybit, and OKX.

## Features

- **Multi-Exchange Support**: Binance Futures, Bybit, and OKX
- **Real-time WebSocket Connections**: Live price feeds with automatic reconnection
- **Arbitrage Detection**: Automatic identification of price differences between exchanges
- **Flexible Input**: Support for CSV and JSON input files
- **Price Storage**: In-memory storage optimized for arbitrage calculations
- **Event-Driven Architecture**: Real-time price updates and arbitrage alerts
- **Graceful Shutdown**: Clean disconnection from all exchanges
- **Extensible Design**: Easy to add new exchanges

## Installation

1. Clone or download the project
2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

**Requirements**: Python 3.8+

## Usage

### Basic Usage

```bash
```

### Command Line Options

- `-i, --input <file>`: Input file path (CSV or JSON) - **Required**
- `-s, --summary-interval <seconds>`: Summary display interval in seconds (default: 30)
- `-v, --verbose`: Enable verbose logging
- `-h, --help`: Display help information

### Input File Formats

#### CSV Format

```csv
exchange,symbol
binance,BTCUSDT
binance,ETHUSDT
bybit,BTCUSDT
bybit,ETHUSDT
okx,BTC-USDT
okx,ETH-USDT
```

#### JSON Format

```json
[
  {"exchange": "binance", "symbol": "BTCUSDT"},
  {"exchange": "binance", "symbol": "ETHUSDT"},
  {"exchange": "bybit", "symbol": "BTCUSDT"},
  {"exchange": "bybit", "symbol": "ETHUSDT"},
  {"exchange": "okx", "symbol": "BTC-USDT"},
  {"exchange": "okx", "symbol": "ETH-USDT"}
]
```

## Supported Exchanges

### Binance Futures
- WebSocket: `wss://fstream.binance.com/ws`
- Symbol format: `BTCUSDT`, `ETHUSDT`
- Data: Book ticker (best bid/ask prices)

### Bybit
- WebSocket: `wss://stream.bybit.com/v5/public/linear`
- Symbol format: `BTCUSDT`, `ETHUSDT`
- Data: Order book level 1

### OKX
- WebSocket: `wss://ws.okx.com:8443/ws/v5/public`
- Symbol format: `BTC-USDT`, `ETH-USDT` (with hyphen)
- Data: Order book snapshot

## API Methods

When using the application programmatically:

```python
import asyncio
from main import CryptoFuturesPriceFetcher

async def main():
    fetcher = CryptoFuturesPriceFetcher()
    
    # Start the application (non-blocking for programmatic use)
    # Note: You'll need to handle this differently for programmatic access
    
    # Get API access
    api = fetcher.get_api()
    
    # Get all prices for a symbol
    btc_prices = api['get_prices_by_symbol']('BTCUSDT')
    print(btc_prices)
    # Output: {
    #   "binance": {"price": 50000.5, "bid": 50000.4, "ask": 50000.6, "timestamp": 1234567890},
    #   "bybit": {"price": 50010.2, "bid": 50010.1, "ask": 50010.3, "timestamp": 1234567891}
    # }
    
    # Get spread between two exchanges
    spread = api['get_spread']('BTCUSDT', 'binance', 'bybit')
    print(spread)
    
    # Get all prices
    all_prices = api['get_all_prices']()
    
    # Get best bid/ask across all exchanges
    best_prices = api['get_best_prices']('BTCUSDT')
    
    # Check arbitrage opportunities
    opportunities = api['check_arbitrage_opportunities']('BTCUSDT', 0.1)

# Run the async function
asyncio.run(main())
```

## Price Data Structure

The application stores prices in the following format:

```javascript
{
  "BTCUSDT": {
    "binance": { 
      price: 50000.5, 
      bid: 50000.4, 
      ask: 50000.6, 
      timestamp: 1234567890 
    },
    "bybit": { 
      price: 50010.2, 
      bid: 50010.1, 
      ask: 50010.3, 
      timestamp: 1234567891 
    },
    "okx": { 
      price: 50005.0, 
      bid: 50004.9, 
      ask: 50005.1, 
      timestamp: 1234567892 
    }
  }
}
```

## Events

The application emits the following events:

- `priceUpdate`: Fired when a price is updated from any exchange
- `arbitrageOpportunity`: Fired when arbitrage opportunities are detected

## Configuration

### Adding New Exchanges

1. Create a new exchange class extending `BaseExchange`:

```python
# src/exchanges/new_exchange.py
from .base_exchange import BaseExchange

class NewExchange(BaseExchange):
    def __init__(self):
        super().__init__('newexchange')
    
    def get_websocket_url(self) -> str:
        return 'wss://api.newexchange.com/ws'
    
    def get_subscribe_message(self, symbol: str) -> dict:
        return {'op': 'subscribe', 'channel': 'ticker', 'symbol': symbol}
    
    async def handle_message(self, message: dict):
        # Implement message handling logic
        pass
    
    # Implement other required methods...
```

2. Add the exchange to `main.py`:

```python
from src.exchanges.new_exchange import NewExchange

# Add to supported_exchanges and exchange_classes
self.supported_exchanges = ['binance', 'bybit', 'okx', 'newexchange']
self.exchange_classes = {
    # ... existing exchanges
    'newexchange': NewExchange
}
```

## Error Handling

- **Connection Failures**: Automatic reconnection with exponential backoff
- **Invalid Symbols**: Gracefully skipped with warnings
- **Exchange Errors**: Logged and handled without crashing
- **Stale Data**: Automatically cleaned up every minute

## Performance Considerations

- **Memory Usage**: Prices are stored in memory; monitor for high-volume scenarios
- **WebSocket Limits**: Each exchange has rate limits and connection limits
- **CPU Usage**: JSON parsing and event processing for high-frequency updates

## Troubleshooting

### Common Issues

1. **Connection Failures**
   - Check internet connection
   - Verify exchange WebSocket URLs are accessible
   - Some exchanges may block certain regions

2. **Symbol Format Errors**
   - Binance/Bybit: Use `BTCUSDT` format
   - OKX: Use `BTC-USDT` format (with hyphen)

3. **No Price Updates**
   - Verify symbols exist on the exchange
   - Check exchange-specific symbol formats
   - Monitor console for error messages

### Debug Mode

Enable detailed logging by using the verbose flag:

```bash
python main.py --input symbols.csv --verbose
```

## Examples

See the `examples/` directory for sample input files and usage patterns.

## Requirements

- Python >= 3.8
- Internet connection for WebSocket connections
- Valid cryptocurrency symbols supported by the exchanges

## License

MIT License