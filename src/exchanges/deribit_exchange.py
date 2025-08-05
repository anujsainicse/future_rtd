import logging
from typing import Dict, Optional
from .base_exchange import BaseExchange

logger = logging.getLogger(__name__)

class DeribitExchange(BaseExchange):
    def __init__(self):
        super().__init__('deribit')
        self.req_id = 1
    
    def get_websocket_url(self) -> str:
        return 'wss://www.deribit.com/ws/api/v2'
    
    def get_subscribe_message(self, symbol: str) -> Dict:
        # Deribit uses different symbol format for perpetual futures
        deribit_symbol = self._convert_to_deribit_symbol(symbol)
        
        message = {
            'jsonrpc': '2.0',
            'id': self.req_id,
            'method': 'public/subscribe',
            'params': {
                'channels': [f'ticker.{deribit_symbol}.100ms']
            }
        }
        self.req_id += 1
        return message
    
    def get_unsubscribe_message(self, symbol: str) -> Dict:
        deribit_symbol = self._convert_to_deribit_symbol(symbol)
        
        message = {
            'jsonrpc': '2.0',
            'id': self.req_id,
            'method': 'public/unsubscribe',
            'params': {
                'channels': [f'ticker.{deribit_symbol}.100ms']
            }
        }
        self.req_id += 1
        return message
    
    def _convert_to_deribit_symbol(self, symbol: str) -> str:
        """Convert standard symbol to Deribit format."""
        # Deribit only supports certain perpetual contracts
        symbol_mappings = {
            'BTCUSDT': 'BTC-PERPETUAL',
            'ETHUSDT': 'ETH-PERPETUAL',
            'SOLUSDT': 'SOL-PERPETUAL',
            'ADAUSDT': 'ADA-PERPETUAL',
            'DOTUSDT': 'DOT-PERPETUAL',
            'LINKUSDT': 'LINK-PERPETUAL',
            'LTCUSDT': 'LTC-PERPETUAL',
            'XRPUSDT': 'XRP-PERPETUAL',
            'AVAXUSDT': 'AVAX-PERPETUAL',
            'MATICUSDT': 'MATIC-PERPETUAL'
        }
        
        if symbol in symbol_mappings:
            return symbol_mappings[symbol]
        else:
            # For unsupported symbols, assume perpetual format but warn
            base = symbol.replace('USDT', '')
            logger.warning(f"Deribit symbol {symbol} not in known mappings, using {base}-PERPETUAL")
            return f'{base}-PERPETUAL'
    
    def _convert_from_deribit_symbol(self, deribit_symbol: str) -> str:
        """Convert Deribit symbol back to standard format."""
        # Reverse mapping from Deribit to standard format
        reverse_mappings = {
            'BTC-PERPETUAL': 'BTCUSDT',
            'ETH-PERPETUAL': 'ETHUSDT',
            'SOL-PERPETUAL': 'SOLUSDT',
            'ADA-PERPETUAL': 'ADAUSDT',
            'DOT-PERPETUAL': 'DOTUSDT',
            'LINK-PERPETUAL': 'LINKUSDT',
            'LTC-PERPETUAL': 'LTCUSDT',
            'XRP-PERPETUAL': 'XRPUSDT',
            'AVAX-PERPETUAL': 'AVAXUSDT',
            'MATIC-PERPETUAL': 'MATICUSDT'
        }
        
        if deribit_symbol in reverse_mappings:
            return reverse_mappings[deribit_symbol]
        else:
            # Fallback: Extract base currency and append USDT
            try:
                base = deribit_symbol.split('-')[0]
                return f'{base}USDT'
            except (IndexError, AttributeError):
                logger.error(f"Failed to parse Deribit symbol: {deribit_symbol}")
                return deribit_symbol  # Return as-is if parsing fails
    
    async def handle_message(self, message: Dict):
        # Add debug logging
        logger.debug(f"Deribit message: {message}")
        
        # Handle subscription confirmation
        if 'result' in message and message.get('id'):
            logger.info(f"Deribit subscription confirmed for request {message['id']}")
            return
        
        # Handle error responses
        if 'error' in message:
            logger.error(f"Deribit error: {message['error']}")
            return
        
        # Handle price data notifications
        if 'method' in message and message['method'] == 'subscription':
            logger.debug(f"Deribit price data: {message['params']}")
            await self._handle_price_update(message)
        else:
            logger.debug(f"Deribit unknown message format: {message.keys()}")
    
    async def _handle_price_update(self, message: Dict):
        """Handle ticker price updates."""
        params = message.get('params')
        if not params:
            logger.debug("Deribit: No params in price update message")
            return
        
        data = params.get('data')
        if not data:
            logger.debug("Deribit: No data in params")
            return
        
        try:
            # Get instrument name and convert to standard symbol
            instrument_name = data.get('instrument_name')
            if not instrument_name:
                logger.debug(f"Deribit: Missing instrument_name in data: {data.keys()}")
                return
            
            symbol = self._convert_from_deribit_symbol(instrument_name)
            
            # Get price data
            last_price = data.get('last_price')
            best_bid_price = data.get('best_bid_price')
            best_ask_price = data.get('best_ask_price')
            timestamp = data.get('timestamp', 0)
            
            if not all([last_price, best_bid_price, best_ask_price]):
                logger.debug(f"Deribit {instrument_name}: Missing price data - last={last_price}, bid={best_bid_price}, ask={best_ask_price}")
                return
            
            # Convert to float with error handling
            price = float(last_price)
            bid = float(best_bid_price)
            ask = float(best_ask_price)
            timestamp = int(timestamp)
            
            if price <= 0 or bid <= 0 or ask <= 0:
                logger.debug(f"Deribit {instrument_name}: Invalid price values - price={price}, bid={bid}, ask={ask}")
                return
            
            price_data = self.format_price_data(symbol, price, bid, ask, timestamp)
            self.emit('price_update', price_data)
            
        except (ValueError, TypeError) as e:
            logger.error(f"Error processing Deribit price data: {e}, data: {data}")
        except Exception as e:
            logger.error(f"Unexpected error processing Deribit price data: {e}")
    
    def get_ping_message(self) -> Optional[Dict]:
        # Deribit uses test request for keepalive
        message = {
            'jsonrpc': '2.0',
            'id': self.req_id,
            'method': 'public/test'
        }
        self.req_id += 1
        return message
    
    def normalize_symbol(self, symbol: str) -> str:
        """Convert standard symbol to Deribit format."""
        return self._convert_to_deribit_symbol(symbol)