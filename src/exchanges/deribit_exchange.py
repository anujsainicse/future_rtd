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
        # Symbol is already in Deribit format from configuration
        message = {
            'jsonrpc': '2.0',
            'id': self.req_id,
            'method': 'public/subscribe',
            'params': {
                'channels': [f'ticker.{symbol}.100ms']
            }
        }
        self.req_id += 1
        return message
    
    def get_unsubscribe_message(self, symbol: str) -> Dict:
        # Symbol is already in Deribit format from configuration
        message = {
            'jsonrpc': '2.0',
            'id': self.req_id,
            'method': 'public/unsubscribe',
            'params': {
                'channels': [f'ticker.{symbol}.100ms']
            }
        }
        self.req_id += 1
        return message
    
    
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
            
            # Use Deribit symbol directly - mapping will handle display symbol conversion
            symbol = instrument_name
            
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
        """Normalize symbol format - keep Deribit format for output."""
        return symbol.upper()