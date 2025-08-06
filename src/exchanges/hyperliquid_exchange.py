import logging
import json
from typing import Dict, Optional
from .base_exchange import BaseExchange

logger = logging.getLogger(__name__)

class HyperliquidExchange(BaseExchange):
    def __init__(self):
        super().__init__('hyperliquid')
        self.subscription_id = 1
    
    def get_websocket_url(self) -> str:
        return 'wss://api.hyperliquid.xyz/ws'
    
    def get_subscribe_message(self, symbol: str) -> Dict:
        """Subscribe to AllMids channel for price updates."""
        message = {
            "method": "subscribe",
            "subscription": {
                "type": "allMids"
            },
            "id": self.subscription_id
        }
        self.subscription_id += 1
        return message
    
    def get_unsubscribe_message(self, symbol: str) -> Dict:
        """Unsubscribe from AllMids channel."""
        message = {
            "method": "unsubscribe",
            "subscription": {
                "type": "allMids"
            },
            "id": self.subscription_id
        }
        self.subscription_id += 1
        return message
    
    async def handle_message(self, message: Dict):
        """Handle WebSocket messages from Hyperliquid."""
        logger.debug(f"Hyperliquid message: {message}")
        
        # Handle subscription confirmation
        if 'channel' in message and message.get('channel') == 'subscriptions':
            logger.info(f"Hyperliquid subscription confirmed: {message}")
            return
        
        # Handle AllMids price updates
        if 'channel' in message and message.get('channel') == 'allMids':
            await self._handle_price_update(message)
        else:
            logger.debug(f"Hyperliquid unknown message format: {message}")
    
    async def _handle_price_update(self, message: Dict):
        """Handle price updates from AllMids channel."""
        try:
            data = message.get('data', {})
            mids = data.get('mids', {})
            
            if not mids:
                return
            
            # Process each symbol's mid price
            for hyperliquid_symbol, mid_price_str in mids.items():
                if not mid_price_str:
                    continue
                
                # Convert Hyperliquid symbol to standard format
                symbol = self._convert_symbol_from_hyperliquid(hyperliquid_symbol)
                
                # Check if we're tracking this symbol
                if symbol not in self.subscribed_symbols:
                    continue
                
                try:
                    mid_price = float(mid_price_str)
                    if mid_price <= 0:
                        continue
                    
                    # Hyperliquid provides mid price, estimate bid/ask
                    spread_percent = 0.001  # 0.1% spread estimate
                    spread = mid_price * spread_percent
                    bid = mid_price - spread
                    ask = mid_price + spread
                    
                    # Use current timestamp since Hyperliquid doesn't provide timestamp in AllMids
                    import time
                    timestamp = int(time.time() * 1000)
                    
                    price_data = self.format_price_data(symbol, mid_price, bid, ask, timestamp)
                    logger.debug(f"Hyperliquid price update for {symbol}: ${mid_price:.6f}")
                    self.emit('price_update', price_data)
                    
                except (ValueError, TypeError) as e:
                    logger.debug(f"Error parsing Hyperliquid price for {hyperliquid_symbol}: {e}")
                    
        except Exception as e:
            logger.error(f"Error handling Hyperliquid price update: {e}")
    
    def _convert_symbol_from_hyperliquid(self, hyperliquid_symbol: str) -> str:
        """Convert Hyperliquid symbol format to standard format.
        
        Hyperliquid uses symbols like 'BTC', 'ETH', 'SOL' for perpetual futures.
        We need to convert them to standard format like 'BTC', 'ETH', 'SOL'.
        """
        # Hyperliquid typically uses simple symbols for perpetual futures
        # No conversion needed for most cases
        return hyperliquid_symbol.upper()
    
    def _convert_symbol_to_hyperliquid(self, symbol: str) -> str:
        """Convert standard symbol format to Hyperliquid format."""
        # Remove common suffixes that might not be used in Hyperliquid
        symbol = symbol.upper()
        
        # Remove USDT, PERP, etc. suffixes as Hyperliquid uses simple symbols
        for suffix in ['USDT', 'USD', 'PERP', 'PERPETUAL']:
            if symbol.endswith(suffix):
                symbol = symbol[:-len(suffix)]
                break
        
        return symbol
    
    async def subscribe(self, symbol: str):
        """Subscribe to a symbol."""
        logger.info(f"Subscribing to {symbol} on Hyperliquid")
        
        # Add to subscribed symbols
        self.subscribed_symbols.add(symbol)
        
        # For Hyperliquid, we subscribe to AllMids once and filter symbols locally
        # Only send subscription if this is the first symbol
        if len(self.subscribed_symbols) == 1:
            subscribe_msg = self.get_subscribe_message(symbol)
            if self.ws and not self.ws.closed:
                await self.ws.send(json.dumps(subscribe_msg))
                logger.debug(f"Sent Hyperliquid subscription: {subscribe_msg}")
    
    async def unsubscribe(self, symbol: str):
        """Unsubscribe from a symbol."""
        logger.info(f"Unsubscribing from {symbol} on Hyperliquid")
        
        if symbol in self.subscribed_symbols:
            self.subscribed_symbols.remove(symbol)
        
        # If no symbols left, unsubscribe from AllMids
        if len(self.subscribed_symbols) == 0:
            unsubscribe_msg = self.get_unsubscribe_message(symbol)
            if self.ws and not self.ws.closed:
                await self.ws.send(json.dumps(unsubscribe_msg))
                logger.debug(f"Sent Hyperliquid unsubscription: {unsubscribe_msg}")
    
    def get_ping_message(self) -> Optional[Dict]:
        """Hyperliquid WebSocket ping message."""
        return {
            "method": "ping",
            "id": self.subscription_id
        }
    
    def normalize_symbol(self, symbol: str) -> str:
        """Normalize symbol for Hyperliquid format."""
        return self._convert_symbol_to_hyperliquid(symbol)