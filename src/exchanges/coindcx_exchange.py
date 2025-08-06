import logging
import asyncio
import json
import urllib.request
import urllib.parse
import time
from typing import Dict, Optional, Set
from .base_exchange import BaseExchange

logger = logging.getLogger(__name__)

class CoindcxExchange(BaseExchange):
    def __init__(self):
        super().__init__('coindcx')
        self.target_symbols: Set[str] = set()
        self.polling_task = None
        self.polling_interval = 3.0  # Poll every 3 seconds
        self.last_prices = {}  # Cache last prices to detect changes
        self.api_url = "https://public.coindcx.com/exchange/ticker"
    
    def get_websocket_url(self) -> str:
        # CoinDCX will use REST polling instead of WebSocket
        return "https://public.coindcx.com"
    
    def get_subscribe_message(self, symbol: str) -> Dict:
        # Not used in REST approach
        return {'symbol': symbol}
    
    def get_unsubscribe_message(self, symbol: str) -> Dict:
        # Not used in REST approach
        return {'symbol': symbol}
    
    async def connect(self):
        """Connect to CoinDCX using REST API polling."""
        try:
            logger.info(f"Connecting to CoinDCX exchange using REST API...")
            
            # Test the REST API first
            if await self._test_rest_api():
                self.is_connected = True
                # Start polling task
                self.polling_task = asyncio.create_task(self._polling_loop())
                logger.info(f"Connected to CoinDCX successfully")
                return True
            else:
                raise ConnectionError("CoinDCX REST API test failed")
                
        except Exception as e:
            logger.error(f"Failed to connect to CoinDCX: {e}")
            self.is_connected = False
            raise ConnectionError(f"CoinDCX connection failed: {e}")
    
    async def _test_rest_api(self):
        """Test the CoinDCX REST API connection."""
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, self._fetch_tickers_sync)
            
            if data and isinstance(data, list) and len(data) > 0:
                logger.debug(f"CoinDCX API test successful, got {len(data)} tickers")
                return True
            else:
                logger.warning("CoinDCX API returned empty or invalid data")
                return False
                
        except Exception as e:
            logger.error(f"CoinDCX API test failed: {e}")
            return False
    
    def _fetch_tickers_sync(self):
        """Synchronous ticker fetch using urllib."""
        try:
            request = urllib.request.Request(self.api_url)
            request.add_header('User-Agent', 'Mozilla/5.0 (compatible; CryptoBot/1.0)')
            
            with urllib.request.urlopen(request, timeout=10) as response:
                if response.status == 200:
                    response_data = response.read().decode('utf-8')
                    return json.loads(response_data)
                else:
                    logger.error(f"CoinDCX API returned status: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"HTTP error fetching CoinDCX tickers: {e}")
            return None
    
    async def _polling_loop(self):
        """Polling loop for REST API data."""
        while self.is_connected and not self.is_shutting_down:
            try:
                if self.target_symbols:
                    await self._fetch_and_process_tickers()
                await asyncio.sleep(self.polling_interval)
            except Exception as e:
                logger.error(f"Error in CoinDCX polling loop: {e}")
                await asyncio.sleep(self.polling_interval * 2)  # Backoff on error
    
    async def _fetch_and_process_tickers(self):
        """Fetch and process ticker data from CoinDCX REST API."""
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, self._fetch_tickers_sync)
            
            if data and isinstance(data, list):
                await self._process_ticker_response(data)
            else:
                logger.debug("No valid ticker data received from CoinDCX")
                
        except Exception as e:
            logger.error(f"Error fetching CoinDCX ticker data: {e}")
    
    async def _process_ticker_response(self, data):
        """Process ticker response from CoinDCX API."""
        try:
            for ticker in data:
                if isinstance(ticker, dict):
                    market = ticker.get('market')
                    if market and market in self.target_symbols:
                        await self._handle_ticker_update(ticker)
                        
        except Exception as e:
            logger.error(f"Error processing CoinDCX ticker response: {e}")
    
    async def _handle_ticker_update(self, ticker_data):
        """Handle ticker data updates."""
        try:
            market = ticker_data.get('market')
            if not market:
                return
            
            symbol = market  # CoinDCX uses standard format
            
            # Extract price data
            last_price = ticker_data.get('last_price')
            bid_price = ticker_data.get('bid')
            ask_price = ticker_data.get('ask')
            timestamp = ticker_data.get('timestamp', int(time.time() * 1000))
            
            # Convert timestamp to milliseconds if needed
            if timestamp and timestamp < 1e12:
                timestamp = int(timestamp * 1000)
            
            if last_price:
                try:
                    price = float(last_price)
                    bid = float(bid_price) if bid_price else price * 0.999
                    ask = float(ask_price) if ask_price else price * 1.001
                    
                    if price > 0:
                        # Only emit if price changed significantly
                        cache_key = f"{symbol}_price"
                        last_price_cached = self.last_prices.get(cache_key, 0)
                        
                        price_change = abs(price - last_price_cached) / last_price_cached if last_price_cached > 0 else 1
                        if price_change > 0.0001:  # 0.01% change threshold
                            self.last_prices[cache_key] = price
                            
                            price_data = self.format_price_data(symbol, price, bid, ask, timestamp)
                            logger.debug(f"CoinDCX price update for {symbol}: ${price:.6f}")
                            self.emit('price_update', price_data)
                            
                except (ValueError, TypeError) as e:
                    logger.debug(f"Error parsing CoinDCX price data for {market}: {e}")
                    
        except Exception as e:
            logger.error(f"Error handling CoinDCX ticker update: {e}")
    
    async def handle_message(self, message):
        """Handle messages - not used for REST API approach."""
        pass
    
    async def subscribe(self, symbol: str):
        """Subscribe to a symbol."""
        logger.info(f"Subscribing to {symbol} on CoinDCX (REST polling)")
        self.subscribed_symbols.add(symbol)
        self.target_symbols.add(symbol)
    
    async def unsubscribe(self, symbol: str):
        """Unsubscribe from a symbol."""
        logger.info(f"Unsubscribing from {symbol} on CoinDCX")
        
        if symbol in self.subscribed_symbols:
            self.subscribed_symbols.remove(symbol)
        if symbol in self.target_symbols:
            self.target_symbols.remove(symbol)
    
    async def disconnect(self):
        """Disconnect from CoinDCX."""
        logger.info(f"Disconnecting from {self.name}")
        self.is_shutting_down = True
        
        # Stop polling task
        if self.polling_task and not self.polling_task.done():
            self.polling_task.cancel()
            try:
                await self.polling_task
            except asyncio.CancelledError:
                pass
        
        self.polling_task = None
        self.is_connected = False
        self.subscribed_symbols.clear()
        self.target_symbols.clear()
        logger.info(f"Disconnected from {self.name}")
    
    def get_ping_message(self) -> Optional[Dict]:
        # REST API doesn't need ping
        return None
    
    def normalize_symbol(self, symbol: str) -> str:
        """Convert standard symbol to CoinDCX format."""
        return symbol.upper()