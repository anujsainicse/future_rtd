import logging
import asyncio
import aiohttp
from typing import Dict, Optional
from .base_exchange import BaseExchange

logger = logging.getLogger(__name__)

class CoindcxExchange(BaseExchange):
    def __init__(self):
        super().__init__('coindcx')
        self.req_id = 1
        self.api_url = 'https://api.coindcx.com/exchange/ticker'
        self.polling_task = None
        self.polling_interval = 5.0  # Poll every 5 seconds
        self.session = None
        self.target_symbols = set()  # Dynamic symbol tracking
    
    def get_websocket_url(self) -> str:
        # CoinDCX uses Socket.IO, not compatible with standard WebSocket
        # Return a dummy URL to avoid None issues, but override connect method
        return 'ws://localhost:9999'
    
    def get_subscribe_message(self, symbol: str) -> Dict:
        # Not used for REST API polling
        return {}
    
    def get_unsubscribe_message(self, symbol: str) -> Dict:
        # Not used for REST API polling
        return {}
    
    def _convert_to_coindcx_symbol(self, symbol: str) -> str:
        """Convert standard symbol to CoinDCX format."""
        # CoinDCX uses standard symbols like BTCUSDT, ETHUSDT
        return symbol
    
    def _convert_from_coindcx_symbol(self, coindcx_symbol: str) -> str:
        """Convert CoinDCX symbol back to standard format."""
        # CoinDCX uses standard symbols, so no conversion needed
        return coindcx_symbol
    
    async def on_connect(self):
        """Override on_connect to start REST API polling."""
        try:
            logger.info(f"Starting REST API polling for {self.name}...")
            
            # Create session for reuse
            self.session = aiohttp.ClientSession()
            
            # Start the polling task
            self.polling_task = asyncio.create_task(self._poll_api())
            logger.info(f"Started REST API polling for {self.name}")
            
        except Exception as e:
            logger.error(f"Failed to start polling for {self.name}: {e}")
            raise
    
    async def _poll_api(self):
        """Poll the CoinDCX REST API for ticker data."""
        while self.is_connected and not self.is_shutting_down:
            try:
                if not self.session:
                    logger.error("CoinDCX session not initialized")
                    break
                    
                async with self.session.get(self.api_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.debug(f"CoinDCX API returned {len(data)} tickers")
                        await self._process_ticker_data(data)
                    else:
                        logger.warning(f"CoinDCX API returned status {response.status}")
                
                await asyncio.sleep(self.polling_interval)
                
            except Exception as e:
                logger.error(f"Error polling CoinDCX API: {e}")
                await asyncio.sleep(self.polling_interval)
    
    async def _process_ticker_data(self, data: list):
        """Process ticker data from CoinDCX API."""
        if not isinstance(data, list):
            return
        
        # Use dynamically tracked symbols instead of hardcoded ones
        if not self.target_symbols:
            logger.debug("CoinDCX: No target symbols to track")
            return
        
        found_symbols = []
        for ticker in data:
            if not isinstance(ticker, dict):
                continue
                
            market = ticker.get('market')
            if market in self.target_symbols:
                found_symbols.append(market)
                await self._handle_ticker_update(ticker)
        
        if found_symbols:
            logger.debug(f"CoinDCX processed symbols: {found_symbols}")
        else:
            logger.debug(f"CoinDCX: No target symbols found in {len(data)} tickers. Looking for: {self.target_symbols}")
    
    async def _handle_ticker_update(self, ticker: Dict):
        """Handle ticker price updates from REST API."""
        market = ticker.get('market')
        if not market:
            logger.debug(f"CoinDCX ticker missing market: {ticker}")
            return
        
        symbol = self._convert_from_coindcx_symbol(market)
        
        # Get price data from CoinDCX ticker format
        last_price = ticker.get('last_price')
        bid_price = ticker.get('bid')
        ask_price = ticker.get('ask')
        timestamp = int(ticker.get('timestamp', 0)) * 1000  # Convert to milliseconds
        
        logger.debug(f"CoinDCX {market}: price={last_price}, bid={bid_price}, ask={ask_price}")
        
        if not all([last_price, bid_price, ask_price]):
            logger.debug(f"CoinDCX {market}: Missing price data - last_price={last_price}, bid={bid_price}, ask={ask_price}")
            return
        
        try:
            price = float(last_price)
            bid = float(bid_price)
            ask = float(ask_price)
            
            price_data = self.format_price_data(symbol, price, bid, ask, timestamp)
            logger.debug(f"CoinDCX emitting price update for {symbol}: {price_data}")
            self.emit('price_update', price_data)
            
        except (ValueError, TypeError) as e:
            logger.debug(f"Error parsing CoinDCX price data: {e}")
    
    async def handle_message(self, message):
        # Not used for REST API polling
        pass
    
    async def subscribe(self, symbol: str):
        """Override subscribe to track symbols for polling."""
        logger.info(f"Polling enabled for {symbol} on {self.name}")
        self.subscribed_symbols.add(symbol)
        self.target_symbols.add(symbol)
    
    async def disconnect(self):
        """Override disconnect to stop polling task."""
        self.is_shutting_down = True
        
        if self.polling_task:
            self.polling_task.cancel()
            self.polling_task = None
        
        # Properly close session
        if self.session:
            await self.session.close()
            self.session = None
        
        self.is_connected = False
        self.subscribed_symbols.clear()
        self.target_symbols.clear()
        logger.info(f"Disconnected from {self.name}")
    
    def get_ping_message(self) -> Optional[Dict]:
        # CoinDCX doesn't require custom ping messages
        return None
    
    def normalize_symbol(self, symbol: str) -> str:
        """Convert standard symbol to CoinDCX format."""
        return self._convert_to_coindcx_symbol(symbol)