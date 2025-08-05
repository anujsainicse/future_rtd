import logging
from typing import Dict, Optional
from .base_exchange import BaseExchange

logger = logging.getLogger(__name__)

class PhemexExchange(BaseExchange):
    def __init__(self):
        super().__init__('phemex')
        self.req_id = 1
        # Phemex scale factors for different symbols
        self.scale_factors = {
            'BTCUSD': 10000,  # 4 decimal places
            'ETHUSD': 10000,  # 4 decimal places
            'XRPUSD': 100000000,  # 8 decimal places
            'ADAUSD': 100000000,  # 8 decimal places
        }
    
    def get_websocket_url(self) -> str:
        return 'wss://ws.phemex.com'
    
    def get_subscribe_message(self, symbol: str) -> Dict:
        # Phemex uses different symbol format
        phemex_symbol = self._convert_to_phemex_symbol(symbol)
        
        message = {
            'id': self.req_id,
            'method': 'book.subscribe',
            'params': [phemex_symbol]
        }
        self.req_id += 1
        return message
    
    def get_unsubscribe_message(self, symbol: str) -> Dict:
        phemex_symbol = self._convert_to_phemex_symbol(symbol)
        
        message = {
            'id': self.req_id,
            'method': 'book.unsubscribe',
            'params': [phemex_symbol]
        }
        self.req_id += 1
        return message
    
    def _convert_to_phemex_symbol(self, symbol: str) -> str:
        """Convert standard symbol to Phemex format."""
        if symbol == 'BTCUSDT':
            return 'BTCUSD'  # Phemex perpetual contracts
        elif symbol == 'ETHUSDT':
            return 'ETHUSD'
        else:
            # Convert XXXUSDT to XXXUSD
            return symbol.replace('USDT', 'USD')
    
    def _convert_from_phemex_symbol(self, phemex_symbol: str) -> str:
        """Convert Phemex symbol back to standard format."""
        if phemex_symbol == 'BTCUSD':
            return 'BTCUSDT'
        elif phemex_symbol == 'ETHUSD':
            return 'ETHUSDT'
        else:
            # Convert XXXUSD to XXXUSDT
            return phemex_symbol.replace('USD', 'USDT')
    
    async def handle_message(self, message):
        if not isinstance(message, dict):
            logger.debug(f"Phemex non-dict message: {type(message)} - {str(message)[:100]}")
            # Handle string messages that might be JSON
            if isinstance(message, str):
                try:
                    import json
                    parsed_message = json.loads(message)
                    await self.handle_message(parsed_message)
                    return
                except json.JSONDecodeError as e:
                    logger.debug(f"Failed to parse Phemex string message as JSON: {e}")
                    return
            return
            
        logger.debug(f"Phemex message: {message}")
        
        # Handle subscription confirmation
        if message.get('id') and message.get('result', {}).get('status') == 'success':
            logger.info(f"Phemex subscription confirmed for request {message['id']}")
            return
        
        # Handle error responses
        if message.get('error'):
            logger.error(f"Phemex error: {message['error']}")
            return
        
        # Handle book data updates
        if message.get('method') == 'book.update' and 'params' in message:
            logger.debug(f"Phemex book data: {message['params']}")
            await self._handle_price_update(message)
        else:
            logger.debug(f"Phemex unknown message format: {message.keys()}")
    
    async def _handle_price_update(self, message: Dict):
        """Handle order book price updates."""
        params = message.get('params')
        if not params or len(params) < 2:
            return
        
        phemex_symbol = params[0]
        book_data = params[1]
        
        # Get symbol and convert to standard format
        symbol = self._convert_from_phemex_symbol(phemex_symbol)
        
        # Get price data from book
        bids = book_data.get('bids', [])
        asks = book_data.get('asks', [])
        
        if not bids or not asks:
            return
        
        # Get symbol-specific scale factor
        scale = self.scale_factors.get(phemex_symbol, 10000)  # Default to 10000
        
        try:
            # Get best bid and ask (prices are scaled integers)
            best_bid_raw = bids[0][0] if bids[0] and len(bids[0]) > 0 else 0
            best_ask_raw = asks[0][0] if asks[0] and len(asks[0]) > 0 else 0
            
            if best_bid_raw == 0 or best_ask_raw == 0:
                logger.debug(f"Phemex {phemex_symbol}: Missing bid or ask data")
                return
            
            # Scale down to actual prices
            best_bid = float(best_bid_raw) / scale
            best_ask = float(best_ask_raw) / scale
            
            # Use mid price as the last price
            price = (best_bid + best_ask) / 2
            timestamp = int(book_data.get('timestamp', 0))
            
            logger.debug(f"Phemex {phemex_symbol}: price={price:.8f}, bid={best_bid:.8f}, ask={best_ask:.8f}, scale={scale}")
            
            price_data = self.format_price_data(symbol, price, best_bid, best_ask, timestamp)
            self.emit('price_update', price_data)
            
        except (ValueError, TypeError, IndexError) as e:
            logger.error(f"Error processing Phemex price data for {phemex_symbol}: {e}")
            logger.debug(f"Raw bids: {bids[:3] if bids else []}, Raw asks: {asks[:3] if asks else []}")
    
    def get_ping_message(self) -> Optional[Dict]:
        message = {
            'id': self.req_id,
            'method': 'server.ping',
            'params': []
        }
        self.req_id += 1
        return message
    
    def normalize_symbol(self, symbol: str) -> str:
        """Convert standard symbol to Phemex format."""
        return self._convert_to_phemex_symbol(symbol)