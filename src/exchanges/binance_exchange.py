import logging
from typing import Dict, Optional
from .base_exchange import BaseExchange

logger = logging.getLogger(__name__)

class BinanceExchange(BaseExchange):
    def __init__(self):
        super().__init__('binance')
        self.stream_id = 1
    
    def get_websocket_url(self) -> str:
        return 'wss://fstream.binance.com/ws'
    
    def get_subscribe_message(self, symbol: str) -> Dict:
        stream_name = f"{symbol.lower()}@bookTicker"
        message = {
            'method': 'SUBSCRIBE',
            'params': [stream_name],
            'id': self.stream_id
        }
        self.stream_id += 1
        return message
    
    def get_unsubscribe_message(self, symbol: str) -> Dict:
        stream_name = f"{symbol.lower()}@bookTicker"
        message = {
            'method': 'UNSUBSCRIBE',
            'params': [stream_name],
            'id': self.stream_id
        }
        self.stream_id += 1
        return message
    
    async def handle_message(self, message: Dict):
        # Add debug logging
        logger.debug(f"Binance message: {message}")
        
        # Handle subscription confirmation
        if 'result' in message and message.get('result') is None and 'id' in message:
            logger.info(f"Binance subscription confirmed for request {message['id']}")
            return
        
        # Handle errors
        if 'error' in message:
            error_msg = message['error'].get('msg', 'Unknown Binance error')
            logger.error(f"Binance error: {error_msg}")
            self.emit('error', Exception(error_msg))
            return
        
        # Handle price data - Binance sends bookTicker data directly
        if message.get('e') == 'bookTicker':
            logger.debug(f"Binance price data: {message}")
            await self._handle_price_update(message)
        elif 'stream' in message and 'data' in message:
            logger.debug(f"Binance stream price data: {message['data']}")
            await self._handle_price_update(message['data'])
        else:
            logger.debug(f"Binance unknown message format: {message.keys()}")
    
    async def _handle_price_update(self, data: Dict):
        """Handle book ticker price updates."""
        if not all(key in data for key in ['s', 'b', 'a']):
            return
        
        symbol = data['s']
        bid = float(data['b'])
        ask = float(data['a'])
        price = (bid + ask) / 2
        timestamp = int(data.get('T', 0))  # Transaction time
        
        price_data = self.format_price_data(symbol, price, bid, ask, timestamp)
        self.emit('price_update', price_data)
    
    def get_ping_message(self) -> Optional[Dict]:
        return None  # Binance handles ping/pong automatically