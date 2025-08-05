import logging
from typing import Dict, Optional
from .base_exchange import BaseExchange

logger = logging.getLogger(__name__)

class MexcExchange(BaseExchange):
    def __init__(self):
        super().__init__('mexc')
        self.req_id = 1
    
    def get_websocket_url(self) -> str:
        return 'wss://contract.mexc.com/edge'
    
    def get_subscribe_message(self, symbol: str) -> Dict:
        # MEXC futures use different symbol format
        mexc_symbol = self._convert_to_mexc_symbol(symbol)
        
        message = {
            'method': 'sub.ticker',
            'param': {
                'symbol': mexc_symbol
            },
            'id': self.req_id
        }
        self.req_id += 1
        return message
    
    def get_unsubscribe_message(self, symbol: str) -> Dict:
        mexc_symbol = self._convert_to_mexc_symbol(symbol)
        
        message = {
            'method': 'unsub.ticker',
            'param': {
                'symbol': mexc_symbol
            },
            'id': self.req_id
        }
        self.req_id += 1
        return message
    
    def _convert_to_mexc_symbol(self, symbol: str) -> str:
        """Convert standard symbol to MEXC format."""
        # MEXC uses underscore format for futures contracts
        symbol_mappings = {
            'BTCUSDT': 'BTC_USDT',
            'ETHUSDT': 'ETH_USDT',
            'ADAUSDT': 'ADA_USDT',
            'BNBUSDT': 'BNB_USDT',
            'DOTUSDT': 'DOT_USDT',
            'LINKUSDT': 'LINK_USDT',
            'LTCUSDT': 'LTC_USDT',
            'XRPUSDT': 'XRP_USDT',
            'SOLUSDT': 'SOL_USDT',
            'AVAXUSDT': 'AVAX_USDT',
            'MATICUSDT': 'MATIC_USDT',
            'TRXUSDT': 'TRX_USDT'
        }
        
        if symbol in symbol_mappings:
            return symbol_mappings[symbol]
        else:
            # Convert XXXUSDT to XXX_USDT for other symbols
            return symbol.replace('USDT', '_USDT')
    
    def _convert_from_mexc_symbol(self, mexc_symbol: str) -> str:
        """Convert MEXC symbol back to standard format."""
        return mexc_symbol.replace('_USDT', 'USDT')
    
    async def handle_message(self, message: Dict):
        logger.debug(f"MEXC message: {message}")
        
        # Handle subscription confirmation
        if message.get('code') == 0 and 'id' in message:
            logger.info(f"MEXC subscription confirmed for request {message['id']}")
            return
        
        # Handle error responses - improved error handling
        code = message.get('code')
        if code is not None and code != 0:
            error_msg = message.get('msg', f'Unknown error with code {code}')
            logger.error(f"MEXC error: {error_msg}")
            return
        
        # Handle pong responses
        if message.get('channel') == 'pong':
            logger.debug('Received pong from MEXC')
            return
        
        # Handle ticker data
        if message.get('channel') == 'push.ticker' and 'data' in message:
            logger.debug(f"MEXC ticker data: {message['data']}")
            await self._handle_price_update(message)
        else:
            logger.debug(f"MEXC unknown message format: {message.keys()}")
    
    async def _handle_price_update(self, message: Dict):
        """Handle ticker price updates."""
        data = message.get('data')
        if not data:
            logger.debug("MEXC: No data in price update message")
            return
        
        try:
            # Get symbol and convert to standard format
            symbol_data = data.get('symbol')
            if not symbol_data:
                logger.debug(f"MEXC: Missing symbol in data: {data.keys()}")
                return
            
            symbol = self._convert_from_mexc_symbol(symbol_data)
            
            # Get price data - MEXC might use different field names
            last_price = data.get('lastPrice') or data.get('last')
            bid_price = data.get('bid1') or data.get('bidPrice')
            ask_price = data.get('ask1') or data.get('askPrice')
            timestamp = data.get('timestamp', 0)
            
            if not all([last_price, bid_price, ask_price]):
                logger.debug(f"MEXC {symbol_data}: Missing price data - last={last_price}, bid={bid_price}, ask={ask_price}")
                return
            
            # Convert to float with error handling
            price = float(last_price)
            bid = float(bid_price)
            ask = float(ask_price)
            timestamp = int(timestamp)
            
            if price <= 0 or bid <= 0 or ask <= 0:
                logger.debug(f"MEXC {symbol_data}: Invalid price values - price={price}, bid={bid}, ask={ask}")
                return
            
            price_data = self.format_price_data(symbol, price, bid, ask, timestamp)
            self.emit('price_update', price_data)
            
        except (ValueError, TypeError) as e:
            logger.error(f"Error processing MEXC price data: {e}, data: {data}")
        except Exception as e:
            logger.error(f"Unexpected error processing MEXC price data: {e}")
    
    def get_ping_message(self) -> Optional[Dict]:
        message = {
            'method': 'ping',
            'id': self.req_id
        }
        self.req_id += 1
        return message
    
    def normalize_symbol(self, symbol: str) -> str:
        """Convert standard symbol to MEXC format."""
        return self._convert_to_mexc_symbol(symbol)