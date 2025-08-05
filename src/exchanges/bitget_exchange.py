import logging
from typing import Dict, Optional
from .base_exchange import BaseExchange

logger = logging.getLogger(__name__)

class BitgetExchange(BaseExchange):
    def __init__(self):
        super().__init__('bitget')
        self.req_id = 1
    
    def get_websocket_url(self) -> str:
        return 'wss://ws.bitget.com/v2/ws/public'
    
    def get_subscribe_message(self, symbol: str) -> Dict:
        # Bitget futures use USDT-FUTURES instType with standard symbol format
        
        message = {
            'op': 'subscribe',
            'args': [
                {
                    'instType': 'USDT-FUTURES',
                    'channel': 'ticker',
                    'instId': symbol
                }
            ]
        }
        return message
    
    def get_unsubscribe_message(self, symbol: str) -> Dict:
        
        message = {
            'op': 'unsubscribe',
            'args': [
                {
                    'instType': 'USDT-FUTURES',
                    'channel': 'ticker',
                    'instId': symbol
                }
            ]
        }
        return message
    
    def _convert_to_bitget_symbol(self, symbol: str) -> str:
        """Convert standard symbol to Bitget format."""
        # Bitget futures perpetuals use UMCBL suffix
        # Handle common symbol mappings
        symbol_mappings = {
            'BTCUSDT': 'BTCUSDT_UMCBL',
            'ETHUSDT': 'ETHUSDT_UMCBL',
            'ADAUSDT': 'ADAUSDT_UMCBL',
            'BNBUSDT': 'BNBUSDT_UMCBL',
            'DOTUSDT': 'DOTUSDT_UMCBL',
            'LINKUSDT': 'LINKUSDT_UMCBL',
            'LTCUSDT': 'LTCUSDT_UMCBL',
            'XRPUSDT': 'XRPUSDT_UMCBL',
            'SOLUSDT': 'SOLUSDT_UMCBL',
            'AVAXUSDT': 'AVAXUSDT_UMCBL'
        }
        
        return symbol_mappings.get(symbol, f"{symbol}_UMCBL")
    
    def _convert_from_bitget_symbol(self, bitget_symbol: str) -> str:
        """Convert Bitget symbol back to standard format."""
        return bitget_symbol.replace('_UMCBL', '')
    
    async def handle_message(self, message):
        if not isinstance(message, dict):
            logger.debug(f"Bitget non-dict message: {type(message)}")
            return
            
        logger.debug(f"Bitget message: {message}")
        
        # Handle subscription confirmation
        if message.get('event') == 'subscribe':
            logger.info(f"Bitget subscription confirmed: {message.get('arg')}")
            return
        
        # Handle pong responses
        if message.get('event') == 'pong':
            logger.debug('Received pong from Bitget')
            return
        
        # Handle error responses
        if message.get('event') == 'error':
            logger.error(f"Bitget error: {message}")
            return
        
        # Handle ticker data - check for both old and new format
        if 'data' in message:
            arg = message.get('arg', {})
            if isinstance(arg, dict) and arg.get('channel') == 'ticker':
                logger.debug(f"Bitget ticker data: {message['data']}")
                await self._handle_price_update(message)
            elif isinstance(arg, str) and 'ticker' in arg:
                logger.debug(f"Bitget ticker data (string format): {message['data']}")
                await self._handle_price_update(message)
        else:
            logger.debug(f"Bitget unknown message format: {message.keys()}")
    
    async def _handle_price_update(self, message: Dict):
        """Handle ticker price updates."""
        data_list = message.get('data', [])
        if not data_list:
            logger.debug("Bitget: No data in price update message")
            return
        
        for data in data_list:
            try:
                # Get instrument ID - now uses standard symbol format
                inst_id = data.get('instId')
                if not inst_id:
                    logger.debug(f"Bitget: Missing instId in data: {data.keys()}")
                    continue
                
                symbol = inst_id  # No conversion needed anymore
                
                # Get price data - Bitget uses specific field names
                last_price = data.get('lastPr')
                bid_price = data.get('bidPr')
                ask_price = data.get('askPr')
                timestamp = data.get('ts', 0)
                
                if not all([last_price, bid_price, ask_price]):
                    logger.debug(f"Bitget {inst_id}: Missing price data - last={last_price}, bid={bid_price}, ask={ask_price}")
                    continue
                
                # Convert to float with error handling
                price = float(last_price)
                bid = float(bid_price)
                ask = float(ask_price)
                timestamp = int(timestamp)
                
                if price <= 0 or bid <= 0 or ask <= 0:
                    logger.debug(f"Bitget {inst_id}: Invalid price values - price={price}, bid={bid}, ask={ask}")
                    continue
                
                logger.debug(f"Bitget {symbol}: price={price}, bid={bid}, ask={ask}")
                price_data = self.format_price_data(symbol, price, bid, ask, timestamp)
                logger.debug(f"Bitget emitting price update for {symbol}: {price_data}")
                self.emit('price_update', price_data)
                
            except (ValueError, TypeError) as e:
                logger.error(f"Error processing Bitget price data: {e}, data: {data}")
            except Exception as e:
                logger.error(f"Unexpected error processing Bitget price data: {e}")
    
    def get_ping_message(self) -> Optional[Dict]:
        # Bitget doesn't use ping, let the base class handle it with websocket ping
        return None
    
    def normalize_symbol(self, symbol: str) -> str:
        """Bitget now uses standard symbol format."""
        return symbol.upper()