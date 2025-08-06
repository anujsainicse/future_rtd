import logging
import json
from typing import Dict, Optional, Set
from .base_exchange import BaseExchange

logger = logging.getLogger(__name__)

class DydxExchange(BaseExchange):
    def __init__(self):
        super().__init__('dydx')
        self.subscribed_markets: Set[str] = set()
    
    def get_websocket_url(self) -> str:
        return 'wss://indexer.dydx.trade/v4/ws'
    
    def get_subscribe_message(self, symbol: str) -> Dict:
        """Subscribe to v4_markets channel for market data."""
        dydx_symbol = self._convert_symbol_to_dydx(symbol)
        message = {
            "type": "subscribe",
            "channel": "v4_markets",
            "id": dydx_symbol
        }
        return message
    
    def get_unsubscribe_message(self, symbol: str) -> Dict:
        """Unsubscribe from v4_markets channel."""
        dydx_symbol = self._convert_symbol_to_dydx(symbol)
        message = {
            "type": "unsubscribe", 
            "channel": "v4_markets",
            "id": dydx_symbol
        }
        return message
    
    async def handle_message(self, message: Dict):
        """Handle WebSocket messages from dYdX."""
        logger.debug(f"dYdX message: {message}")
        
        # Handle subscription confirmation
        if message.get('type') == 'subscribed':
            channel = message.get('channel')
            market_id = message.get('id')
            logger.info(f"dYdX subscription confirmed for {channel}:{market_id}")
            return
        
        # Handle connection type messages
        if message.get('type') == 'connected':
            logger.info("dYdX WebSocket connected")
            return
        
        # Handle channel data messages
        if message.get('type') == 'channel_data':
            channel = message.get('channel')
            if channel == 'v4_markets':
                await self._handle_market_data(message)
        else:
            logger.debug(f"dYdX unknown message type: {message.get('type')}")
    
    async def _handle_market_data(self, message: Dict):
        """Handle market data from v4_markets channel."""
        try:
            contents = message.get('contents', {})
            markets = contents.get('markets', {})
            
            if not markets:
                return
            
            # Process each market's data
            for dydx_market_id, market_data in markets.items():
                # Convert dYdX market ID to standard symbol
                symbol = self._convert_symbol_from_dydx(dydx_market_id)
                
                # Check if we're tracking this symbol
                if symbol not in self.subscribed_symbols:
                    continue
                
                try:
                    # Extract price information from market data
                    oracle_price_str = market_data.get('oraclePrice')
                    if not oracle_price_str:
                        continue
                    
                    price = float(oracle_price_str)
                    if price <= 0:
                        continue
                    
                    # dYdX doesn't provide bid/ask in market data, estimate from oracle price
                    spread_percent = 0.001  # 0.1% spread estimate
                    spread = price * spread_percent
                    bid = price - spread
                    ask = price + spread
                    
                    # Use current timestamp since dYdX market data doesn't include timestamp
                    import time
                    timestamp = int(time.time() * 1000)
                    
                    price_data = self.format_price_data(symbol, price, bid, ask, timestamp)
                    logger.debug(f"dYdX price update for {symbol}: ${price:.6f}")
                    self.emit('price_update', price_data)
                    
                except (ValueError, TypeError) as e:
                    logger.debug(f"Error parsing dYdX market data for {dydx_market_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error handling dYdX market data: {e}")
    
    def _convert_symbol_from_dydx(self, dydx_symbol: str) -> str:
        """Convert dYdX market ID to standard symbol format.
        
        dYdX uses market IDs like 'BTC-USD', 'ETH-USD', 'SOL-USD' for perpetual futures.
        Convert them to standard format like 'BTC', 'ETH', 'SOL'.
        """
        # Remove -USD suffix as dYdX perpetuals are USD-settled
        if dydx_symbol.endswith('-USD'):
            return dydx_symbol[:-4].upper()
        
        return dydx_symbol.upper()
    
    def _convert_symbol_to_dydx(self, symbol: str) -> str:
        """Convert standard symbol format to dYdX market ID format."""
        # Remove common suffixes
        symbol = symbol.upper()
        
        # Remove USDT, PERP, etc. suffixes as dYdX uses different format
        for suffix in ['USDT', 'USD', 'PERP', 'PERPETUAL']:
            if symbol.endswith(suffix):
                symbol = symbol[:-len(suffix)]
                break
        
        # dYdX uses format like BTC-USD for perpetual futures
        return f"{symbol}-USD"
    
    async def subscribe(self, symbol: str):
        """Subscribe to a symbol."""
        logger.info(f"Subscribing to {symbol} on dYdX")
        
        # Convert to dYdX format
        dydx_symbol = self._convert_symbol_to_dydx(symbol)
        
        # Add to subscribed symbols
        self.subscribed_symbols.add(symbol)
        self.subscribed_markets.add(dydx_symbol)
        
        # Send subscription message
        subscribe_msg = self.get_subscribe_message(symbol)
        if self.ws and not self.ws.closed:
            await self.ws.send(json.dumps(subscribe_msg))
            logger.debug(f"Sent dYdX subscription: {subscribe_msg}")
    
    async def unsubscribe(self, symbol: str):
        """Unsubscribe from a symbol."""
        logger.info(f"Unsubscribing from {symbol} on dYdX")
        
        dydx_symbol = self._convert_symbol_to_dydx(symbol)
        
        if symbol in self.subscribed_symbols:
            self.subscribed_symbols.remove(symbol)
        if dydx_symbol in self.subscribed_markets:
            self.subscribed_markets.remove(dydx_symbol)
        
        # Send unsubscription message
        unsubscribe_msg = self.get_unsubscribe_message(symbol)
        if self.ws and not self.ws.closed:
            await self.ws.send(json.dumps(unsubscribe_msg))
            logger.debug(f"Sent dYdX unsubscription: {unsubscribe_msg}")
    
    def get_ping_message(self) -> Optional[Dict]:
        """dYdX WebSocket ping message."""
        return {
            "type": "ping"
        }
    
    def normalize_symbol(self, symbol: str) -> str:
        """Normalize symbol for dYdX format."""
        return self._convert_symbol_to_dydx(symbol)