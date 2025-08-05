import logging
from typing import Dict, Optional
from .base_exchange import BaseExchange

logger = logging.getLogger(__name__)

class GateioExchange(BaseExchange):
    def __init__(self):
        super().__init__('gateio')
        self.req_id = 1
    
    def get_websocket_url(self) -> str:
        return 'wss://fx-ws.gateio.ws/v4/ws/usdt'
    
    def get_subscribe_message(self, symbol: str) -> Dict:
        # Gate.io futures use different symbol format
        gateio_symbol = self._convert_to_gateio_symbol(symbol)
        
        message = {
            'time': self.req_id,
            'channel': 'futures.tickers',
            'event': 'subscribe',
            'payload': [gateio_symbol]
        }
        self.req_id += 1
        return message
    
    def get_unsubscribe_message(self, symbol: str) -> Dict:
        gateio_symbol = self._convert_to_gateio_symbol(symbol)
        
        message = {
            'time': self.req_id,
            'channel': 'futures.tickers',
            'event': 'unsubscribe',
            'payload': [gateio_symbol]
        }
        self.req_id += 1
        return message
    
    def _convert_to_gateio_symbol(self, symbol: str) -> str:
        """Convert standard symbol to Gate.io format."""
        if symbol == 'BTCUSDT':
            return 'BTC_USDT'
        elif symbol == 'ETHUSDT':
            return 'ETH_USDT'
        else:
            # Convert XXXUSDT to XXX_USDT
            return symbol.replace('USDT', '_USDT')
    
    def _convert_from_gateio_symbol(self, gateio_symbol: str) -> str:
        """Convert Gate.io symbol back to standard format."""
        return gateio_symbol.replace('_USDT', 'USDT')
    
    async def handle_message(self, message):
        # Gate.io can send both dict and list messages
        if isinstance(message, list):
            logger.debug(f"Gate.io list message: {message[:2] if len(message) > 2 else message}")
            # Handle list messages - these are often heartbeat or subscription confirmations
            if len(message) >= 1:
                if message[0] == 'pong':
                    logger.debug("Gate.io pong received")
                elif len(message) >= 3 and message[0] == 'futures.tickers' and message[1] == 'update':
                    # This is ticker data in list format
                    await self._handle_list_price_update(message)
            return
        
        if not isinstance(message, dict):
            if isinstance(message, list):
                logger.debug(f"Gate.io list message: {message}")
                await self._handle_list_price_update(message)
                return
            else:
                logger.debug(f"Gate.io unknown message type: {type(message)}")
                return
            
        logger.debug(f"Gate.io message: {message}")
        
        # Handle subscription confirmation
        if message.get('event') == 'subscribe' and message.get('result', {}).get('status') == 'success':
            logger.info(f"Gate.io subscription confirmed for channel: {message.get('channel')}")
            return
        
        # Handle pong responses
        if message.get('event') == 'pong':
            logger.debug('Received pong from Gate.io')
            return
        
        # Handle error responses
        if message.get('event') == 'subscribe' and message.get('result', {}).get('status') == 'error':
            logger.error(f"Gate.io subscription error: {message.get('result')}")
            return
        
        # Handle ticker data updates
        if message.get('channel') == 'futures.tickers' and message.get('event') == 'update':
            logger.debug(f"Gate.io ticker data: {message.get('result')}")
            await self._handle_price_update(message)
        else:
            logger.debug(f"Gate.io unknown message format: {message.keys()}")
    
    async def _handle_price_update(self, message: Dict):
        """Handle ticker price updates."""
        result = message.get('result')
        if not result:
            return
        
        # GateIO result is a list of ticker objects
        if isinstance(result, list):
            for ticker_data in result:
                if isinstance(ticker_data, dict):
                    await self._process_ticker_data(ticker_data)
        else:
            await self._process_ticker_data(result)
    
    async def _handle_list_price_update(self, message: list):
        """Handle ticker price updates in list format."""
        if len(message) < 3:
            return
        
        # Gate.io list format: ['futures.tickers', 'update', data]
        data = message[2]
        if not isinstance(data, dict):
            return
        
        await self._process_ticker_data(data)
    
    async def _process_ticker_data(self, data: Dict):
        """Common method to process ticker data from either dict or list format."""
        # Get symbol and convert to standard format
        contract = data.get('contract')
        if not contract:
            logger.debug(f"Gate.io ticker data missing contract: {data.keys()}")
            return
        
        symbol = self._convert_from_gateio_symbol(contract)
        
        # Get price data - GateIO doesn't provide bid/ask in ticker, use last price
        last_price = data.get('last')
        mark_price = data.get('mark_price')
        
        if not last_price:
            logger.debug(f"Gate.io {contract}: Missing price data - last={last_price}")
            return
        
        try:
            price = float(last_price)
            # Use mark_price as both bid and ask since GateIO doesn't provide separate bid/ask in ticker
            mark = float(mark_price) if mark_price else price
            
            # Create small spread around mark price for bid/ask
            spread = price * 0.0001  # 0.01% spread
            bid = mark - spread/2
            ask = mark + spread/2
            
            # Improved timestamp parsing
            timestamp = self._parse_gateio_timestamp(data)
            
            logger.debug(f"Gate.io {symbol}: price={price}, bid={bid}, ask={ask}")
            price_data = self.format_price_data(symbol, price, bid, ask, timestamp)
            logger.debug(f"Gate.io emitting price update for {symbol}: {price_data}")
            self.emit('price_update', price_data)
            
        except (ValueError, TypeError) as e:
            logger.error(f"Error processing Gate.io price data for {contract}: {e}")
    
    def _parse_gateio_timestamp(self, data: Dict) -> int:
        """Parse Gate.io timestamp fields."""
        # Try different timestamp fields Gate.io might use
        timestamp_fields = ['change_utc', 'timestamp', 'time']
        
        for field in timestamp_fields:
            timestamp_value = data.get(field)
            if timestamp_value:
                try:
                    # If it's already in milliseconds, use as is
                    if isinstance(timestamp_value, (int, float)):
                        timestamp = int(timestamp_value)
                        # If it looks like seconds (Unix timestamp), convert to milliseconds
                        if timestamp < 1e12:  # Less than year 33658 in milliseconds
                            timestamp *= 1000
                        return timestamp
                    # If it's a string, try to parse it
                    elif isinstance(timestamp_value, str):
                        timestamp = int(float(timestamp_value)) * 1000
                        return timestamp
                except (ValueError, TypeError):
                    continue
        
        # Fallback to current time if no timestamp found
        import time
        return int(time.time() * 1000)
    
    def get_ping_message(self) -> Optional[Dict]:
        message = {
            'time': self.req_id,
            'channel': 'futures.ping',
            'event': 'ping'
        }
        self.req_id += 1
        return message
    
    def normalize_symbol(self, symbol: str) -> str:
        """Convert standard symbol to Gate.io format."""
        return self._convert_to_gateio_symbol(symbol)