import logging
from typing import Dict, Optional
from .base_exchange import BaseExchange

logger = logging.getLogger(__name__)

class BybitExchange(BaseExchange):
    def __init__(self):
        super().__init__('bybit')
        self.req_id = 1
    
    def get_websocket_url(self) -> str:
        return 'wss://stream.bybit.com/v5/public/linear'
    
    def get_subscribe_message(self, symbol: str) -> Dict:
        message = {
            'op': 'subscribe',
            'args': [f'orderbook.1.{symbol}'],
            'req_id': self.req_id
        }
        self.req_id += 1
        return message
    
    def get_unsubscribe_message(self, symbol: str) -> Dict:
        message = {
            'op': 'unsubscribe',
            'args': [f'orderbook.1.{symbol}'],
            'req_id': self.req_id
        }
        self.req_id += 1
        return message
    
    async def handle_message(self, message: Dict):
        # Handle subscription confirmation
        if 'success' in message and message.get('req_id'):
            logger.info(f"Bybit subscription confirmed for request {message['req_id']}")
            return
        
        # Handle pong responses
        if message.get('op') == 'pong':
            logger.debug('Received pong from Bybit')
            return
        
        # Handle price data
        if 'topic' in message and 'data' in message:
            await self._handle_price_update(message)
    
    async def _handle_price_update(self, message: Dict):
        """Handle orderbook price updates."""
        data = message.get('data')
        if not data or not data.get('b') or not data.get('a'):
            return
        
        # Extract symbol from topic (e.g., "orderbook.1.BTCUSDT")
        topic_parts = message['topic'].split('.')
        if len(topic_parts) < 3:
            return
        
        symbol = topic_parts[2]
        
        # Get best bid and ask
        bids = data.get('b', [])
        asks = data.get('a', [])
        
        if not bids or not asks:
            return
        
        bid = float(bids[0][0])
        ask = float(asks[0][0])
        price = (bid + ask) / 2
        timestamp = int(message.get('ts', 0))
        
        price_data = self.format_price_data(symbol, price, bid, ask, timestamp)
        self.emit('price_update', price_data)
    
    def get_ping_message(self) -> Optional[Dict]:
        message = {
            'op': 'ping',
            'req_id': self.req_id
        }
        self.req_id += 1
        return message