import logging
from typing import Dict, Optional
from .base_exchange import BaseExchange

logger = logging.getLogger(__name__)

class OKXExchange(BaseExchange):
    def __init__(self):
        super().__init__('okx')
        # OKX doesn't use request IDs in its WebSocket API
    
    def get_websocket_url(self) -> str:
        return 'wss://ws.okx.com:8443/ws/v5/public'
    
    def get_subscribe_message(self, symbol: str) -> Dict:
        # Symbol is already in OKX format from configuration
        return {
            'op': 'subscribe',
            'args': [{
                'channel': 'books',
                'instId': symbol
            }]
        }
    
    def get_unsubscribe_message(self, symbol: str) -> Dict:
        # Symbol is already in OKX format from configuration
        return {
            'op': 'unsubscribe',
            'args': [{
                'channel': 'books',
                'instId': symbol
            }]
        }
    
    
    async def handle_message(self, message: Dict):
        # Handle subscription confirmation
        if message.get('event') == 'subscribe':
            inst_id = message.get('arg', {}).get('instId', 'unknown')
            logger.info(f"OKX subscription confirmed for {inst_id}")
            return
        
        # Handle errors
        if message.get('event') == 'error':
            error_msg = message.get('msg', 'Unknown OKX error')
            logger.error(f"OKX error: {error_msg}")
            self.emit('error', Exception(error_msg))
            return
        
        # Handle price data
        if message.get('arg') and message.get('data') and message['arg'].get('channel') == 'books':
            await self._handle_price_update(message)
    
    async def _handle_price_update(self, message: Dict):
        """Handle orderbook price updates."""
        data = message.get('data')
        if not data or len(data) == 0:
            return
        
        book_data = data[0]
        symbol = message['arg']['instId']
        
        # Get best bid and ask
        bids = book_data.get('bids', [])
        asks = book_data.get('asks', [])
        
        if not bids or not asks:
            return
        
        bid = float(bids[0][0])
        ask = float(asks[0][0])
        price = (bid + ask) / 2
        timestamp = int(book_data.get('ts', 0))
        
        # Use OKX symbol directly - mapping will handle display symbol conversion
        price_data = self.format_price_data(symbol, price, bid, ask, timestamp)
        self.emit('price_update', price_data)
    
    def get_ping_message(self) -> Optional[Dict]:
        # OKX uses simple ping string - convert to proper format
        return {'op': 'ping'}