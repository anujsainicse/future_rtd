import logging
from typing import Dict, Optional
from .base_exchange import BaseExchange

logger = logging.getLogger(__name__)

class BitmexExchange(BaseExchange):
    def __init__(self):
        super().__init__('bitmex')
        self.req_id = 1
        # Store last prices from trade data
        self.last_prices = {}
    
    def get_websocket_url(self) -> str:
        return 'wss://ws.bitmex.com/realtime'
    
    def get_subscribe_message(self, symbol: str) -> Dict:
        # BitMEX uses different symbol format
        bitmex_symbol = self._convert_to_bitmex_symbol(symbol)
        
        message = {
            'op': 'subscribe',
            # Subscribe to both quote (bid/ask) and trade (last price) data
            'args': [f'quote:{bitmex_symbol}', f'trade:{bitmex_symbol}']
        }
        return message
    
    def get_unsubscribe_message(self, symbol: str) -> Dict:
        bitmex_symbol = self._convert_to_bitmex_symbol(symbol)
        
        message = {
            'op': 'unsubscribe',
            'args': [f'quote:{bitmex_symbol}', f'trade:{bitmex_symbol}']
        }
        return message
    
    def _convert_to_bitmex_symbol(self, symbol: str) -> str:
        """Convert standard symbol to BitMEX format."""
        if symbol == 'BTCUSDT':
            return 'XBTUSD'  # BitMEX uses XBT for Bitcoin
        elif symbol == 'ETHUSDT':
            return 'ETHUSD'
        else:
            # For other symbols, assume USD format
            base = symbol.replace('USDT', '')
            return f'{base}USD'
    
    def _convert_from_bitmex_symbol(self, bitmex_symbol: str) -> str:
        """Convert BitMEX symbol back to standard format."""
        if bitmex_symbol == 'XBTUSD':
            return 'BTCUSDT'
        elif bitmex_symbol == 'ETHUSD':
            return 'ETHUSDT'
        else:
            # Convert XXXUSD to XXXUSDT
            return bitmex_symbol.replace('USD', 'USDT')
    
    async def handle_message(self, message: Dict):
        logger.debug(f"BitMEX message: {message}")
        
        # Handle subscription confirmation
        if message.get('success') is True and 'subscribe' in message:
            logger.info(f"BitMEX subscription confirmed: {message.get('subscribe')}")
            return
        
        # Handle error responses
        if message.get('error'):
            logger.error(f"BitMEX error: {message['error']}")
            return
        
        # Handle info messages
        if message.get('info'):
            logger.info(f"BitMEX info: {message['info']}")
            return
        
        # Handle quote data (bid/ask)
        if message.get('table') == 'quote' and 'data' in message:
            logger.debug(f"BitMEX quote data: {message['data']}")
            await self._handle_quote_update(message)
        # Handle trade data (last price)
        elif message.get('table') == 'trade' and 'data' in message:
            logger.debug(f"BitMEX trade data: {message['data']}")
            await self._handle_trade_update(message)
        else:
            logger.debug(f"BitMEX unknown message format: {message.keys()}")
    
    async def _handle_quote_update(self, message: Dict):
        """Handle quote (bid/ask) price updates."""
        data_list = message.get('data', [])
        if not data_list:
            return
        
        for data in data_list:
            # Get symbol and convert to standard format
            bitmex_symbol = data.get('symbol')
            if not bitmex_symbol:
                continue
            
            symbol = self._convert_from_bitmex_symbol(bitmex_symbol)
            
            # Get price data
            bid_price = data.get('bidPrice')
            ask_price = data.get('askPrice')
            timestamp_str = data.get('timestamp')
            
            if not all([bid_price, ask_price]):
                continue
            
            bid = float(bid_price)
            ask = float(ask_price)
            
            # Use last traded price if available, otherwise mid price
            last_price = self.last_prices.get(bitmex_symbol)
            price = float(last_price) if last_price else (bid + ask) / 2
            
            # Parse timestamp
            timestamp = self._parse_timestamp(timestamp_str)
            
            price_data = self.format_price_data(symbol, price, bid, ask, timestamp)
            self.emit('price_update', price_data)
    
    async def _handle_trade_update(self, message: Dict):
        """Handle trade (last price) updates."""
        data_list = message.get('data', [])
        if not data_list:
            return
        
        for data in data_list:
            bitmex_symbol = data.get('symbol')
            if not bitmex_symbol:
                continue
            
            # Store the last traded price
            price = data.get('price')
            if price:
                self.last_prices[bitmex_symbol] = price
                logger.debug(f"BitMEX {bitmex_symbol}: Updated last price to {price}")
    
    def _parse_timestamp(self, timestamp_str: str) -> int:
        """Parse BitMEX timestamp string to milliseconds."""
        if not timestamp_str:
            return 0
        
        try:
            from datetime import datetime
            # BitMEX timestamps are in ISO format with Z suffix
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return int(dt.timestamp() * 1000)
        except Exception as e:
            logger.debug(f"Failed to parse BitMEX timestamp {timestamp_str}: {e}")
            return 0
    
    def get_ping_message(self) -> Optional[Dict]:
        return {'op': 'ping'}
    
    def normalize_symbol(self, symbol: str) -> str:
        """Convert standard symbol to BitMEX format."""
        return self._convert_to_bitmex_symbol(symbol)