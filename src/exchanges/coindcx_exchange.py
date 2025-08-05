import logging
import asyncio
import socketio
import aiohttp
import json
from typing import Dict, Optional
from .base_exchange import BaseExchange

logger = logging.getLogger(__name__)

class CoindcxExchange(BaseExchange):
    def __init__(self):
        super().__init__('coindcx')
        self.sio = None
        self.connection_task = None
        self.target_symbols = set()  # Dynamic symbol tracking
        self.connected_to_socketio = False
        self.polling_task = None
        self.polling_interval = 2.0  # Poll every 2 seconds
        self.session = None
        self.use_rest_fallback = True  # Use REST API as primary method
    
    def get_websocket_url(self) -> str:
        # CoinDCX uses Socket.io, return the Socket.io endpoint
        return 'wss://stream.coindcx.com'
    
    def get_subscribe_message(self, symbol: str) -> Dict:
        # Socket.io subscription will be handled differently
        return {
            'channel': 'ticker',
            'symbol': symbol
        }
    
    def get_unsubscribe_message(self, symbol: str) -> Dict:
        # Socket.io unsubscription will be handled differently
        return {
            'channel': 'ticker',
            'symbol': symbol
        }
    
    def _convert_to_coindcx_symbol(self, symbol: str) -> str:
        """Convert standard symbol to CoinDCX format."""
        # CoinDCX uses standard symbols like BTCUSDT, ETHUSDT for crypto pairs
        # and BTCINR, ETHINR for INR pairs
        # No conversion needed as they match standard format
        return symbol.upper()
    
    def _convert_from_coindcx_symbol(self, coindcx_symbol: str) -> str:
        """Convert CoinDCX symbol back to standard format."""
        # CoinDCX uses standard symbols, so no conversion needed
        return coindcx_symbol.upper()
    
    async def connect(self):
        """Connect to CoinDCX using REST API polling or WebSocket fallback."""
        try:
            logger.info(f"Connecting to CoinDCX exchange...")
            
            # Create HTTP session for REST API calls
            self.session = aiohttp.ClientSession()
            
            if self.use_rest_fallback:
                # Use REST API polling approach
                logger.info("Using REST API polling for CoinDCX market data")
                self.is_connected = True
                
                # Start polling task
                self.polling_task = asyncio.create_task(self._polling_loop())
                
                logger.info(f"Connected to CoinDCX successfully")
                return True
            else:
                # Fallback to WebSocket approach
                return await self._connect_websocket()
            
        except Exception as e:
            logger.error(f"Failed to connect to CoinDCX: {e}")
            self.is_connected = False
            raise ConnectionError(f"CoinDCX connection failed: {e}")
    
    async def _connect_websocket(self):
        """Connect to CoinDCX WebSocket using Socket.io (fallback method)."""
        try:
            logger.info(f"Connecting to CoinDCX WebSocket: {self.get_websocket_url()}")
            
            # Create Socket.io client with specific configuration for CoinDCX
            self.sio = socketio.AsyncClient(
                logger=False,
                engineio_logger=False,
                reconnection=True,
                reconnection_attempts=5,
                reconnection_delay=1,
                reconnection_delay_max=5
            )
            
            # Set up event handlers
            self.sio.on('connect', self._on_socketio_connect)
            self.sio.on('disconnect', self._on_socketio_disconnect)
            self.sio.on('price_change', self._on_price_data)  # CoinDCX uses 'price_change' for LTP
            self.sio.on('ticker', self._on_ticker_data)  # Keep this as backup
            self.sio.on('error', self._on_socketio_error)
            self.sio.on('*', self._on_any_event)  # Catch all events
            
            # Connect to CoinDCX Socket.io server with specific transport
            await self.sio.connect(
                self.get_websocket_url(),
                transports=['websocket'],
                wait_timeout=10
            )
            
            # Mark as connected
            self.is_connected = True
            self.connected_to_socketio = True
            
            logger.info(f"Connected to CoinDCX WebSocket successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to CoinDCX WebSocket: {e}")
            self.is_connected = False
            self.connected_to_socketio = False
            raise ConnectionError(f"CoinDCX WebSocket connection failed: {e}")
    
    async def _on_socketio_connect(self):
        """Handle Socket.io connection event."""
        logger.info("CoinDCX Socket.io connected successfully")
        self.connected_to_socketio = True
        
        # Subscribe to symbols that were requested
        for symbol in self.target_symbols:
            await self._subscribe_to_symbol(symbol)
    
    async def _on_socketio_disconnect(self):
        """Handle Socket.io disconnection event."""
        logger.info("CoinDCX Socket.io disconnected")
        self.connected_to_socketio = False
    
    async def _on_socketio_error(self, data):
        """Handle Socket.io error events."""
        logger.error(f"CoinDCX Socket.io error: {data}")
        self.emit('error', Exception(f"CoinDCX Socket.io error: {data}"))
    
    async def _on_ticker_data(self, data):
        """Handle ticker data from Socket.io."""
        logger.debug(f"CoinDCX ticker data received: {data}")
        await self._handle_ticker_update(data)
    
    async def _on_price_data(self, data):
        """Handle price change data from Socket.io."""
        logger.debug(f"CoinDCX price change data received: {data}")
        await self._handle_ticker_update(data)
    
    async def _on_any_event(self, event, data):
        """Catch all events to understand CoinDCX's actual event structure."""
        logger.info(f"CoinDCX event '{event}' received with data: {data}")
        # Try to handle as ticker data if it looks like price information
        if isinstance(data, dict) and any(key in data for key in ['price', 'last_price', 'lastPrice', 'market', 'symbol']):
            await self._handle_ticker_update(data)
    
    async def _polling_loop(self):
        """Polling loop for REST API data."""
        while self.is_connected and not self.is_shutting_down:
            try:
                if self.target_symbols:
                    await self._fetch_ticker_data()
                await asyncio.sleep(self.polling_interval)
            except Exception as e:
                logger.error(f"Error in CoinDCX polling loop: {e}")
                await asyncio.sleep(self.polling_interval * 2)  # Backoff on error
    
    async def _fetch_ticker_data(self):
        """Fetch ticker data from CoinDCX REST API."""
        try:
            # CoinDCX ticker endpoint
            url = "https://public.coindcx.com/exchange/ticker"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    await self._process_ticker_response(data)
                else:
                    logger.warning(f"CoinDCX API returned status {response.status}")
                    
        except Exception as e:
            logger.error(f"Error fetching CoinDCX ticker data: {e}")
    
    async def _process_ticker_response(self, data):
        """Process ticker response from CoinDCX API."""
        try:
            if isinstance(data, list):
                # Process each ticker in the response
                for ticker in data:
                    if isinstance(ticker, dict):
                        market = ticker.get('market')
                        if market and market in self.target_symbols:
                            await self._handle_rest_ticker_update(ticker)
            elif isinstance(data, dict):
                # Single ticker response
                market = data.get('market')
                if market and market in self.target_symbols:
                    await self._handle_rest_ticker_update(data)
                    
        except Exception as e:
            logger.error(f"Error processing CoinDCX ticker response: {e}")
    
    async def _handle_rest_ticker_update(self, ticker_data):
        """Handle ticker data from REST API."""
        try:
            market = ticker_data.get('market')
            if not market:
                return
            
            symbol = self._convert_from_coindcx_symbol(market)
            
            # Extract price data from CoinDCX ticker format
            last_price = ticker_data.get('last_price') or ticker_data.get('lastPrice')
            bid_price = ticker_data.get('bid') or ticker_data.get('bidPrice')
            ask_price = ticker_data.get('ask') or ticker_data.get('askPrice')
            timestamp = ticker_data.get('timestamp', 0)
            
            # Convert timestamp to milliseconds if needed
            if timestamp and timestamp < 1e12:  # If it's in seconds
                timestamp = int(timestamp * 1000)
            else:
                timestamp = int(timestamp) if timestamp else 0
            
            logger.debug(f"CoinDCX REST {market}: price={last_price}, bid={bid_price}, ask={ask_price}")
            
            if last_price:
                # Convert to float with error handling
                price = float(last_price)
                bid = float(bid_price) if bid_price else price * 0.999  # Approximate bid
                ask = float(ask_price) if ask_price else price * 1.001  # Approximate ask
                
                if price > 0:
                    price_data = self.format_price_data(symbol, price, bid, ask, timestamp)
                    logger.debug(f"CoinDCX emitting price update for {symbol}: {price_data}")
                    self.emit('price_update', price_data)
                    
        except (ValueError, TypeError) as e:
            logger.error(f"Error parsing CoinDCX REST ticker data: {e}, data: {ticker_data}")
        except Exception as e:
            logger.error(f"Unexpected error processing CoinDCX REST ticker data: {e}")
    
    async def _subscribe_to_symbol(self, symbol: str):
        """Subscribe to a specific symbol via Socket.io."""
        if not self.connected_to_socketio or not self.sio:
            logger.warning(f"Cannot subscribe to {symbol}: Not connected to Socket.io")
            return
        
        try:
            coindcx_symbol = self._convert_to_coindcx_symbol(symbol)
            
            # CoinDCX subscription format - try the documented approach
            # Based on API docs, it might just need a simple subscription
            await self.sio.emit('subscribe', {
                'event': 'subscribe',
                'channel': ['all_tickers']  # Subscribe to all tickers first
            })
            logger.debug(f"Subscribed to all_tickers")
            
            # Also try symbol-specific subscription
            await self.sio.emit('subscribe', coindcx_symbol)
            logger.debug(f"Trying direct symbol subscription: {coindcx_symbol}")
            
            logger.info(f"Subscribed to CoinDCX price updates for {symbol} ({coindcx_symbol})")
            
        except Exception as e:
            logger.error(f"Failed to subscribe to CoinDCX symbol {symbol}: {e}")
    
    async def _unsubscribe_from_symbol(self, symbol: str):
        """Unsubscribe from a specific symbol via Socket.io."""
        if not self.connected_to_socketio or not self.sio:
            logger.warning(f"Cannot unsubscribe from {symbol}: Not connected to Socket.io")
            return
        
        try:
            coindcx_symbol = self._convert_to_coindcx_symbol(symbol)
            
            # Emit unsubscription request via Socket.io using CoinDCX format
            await self.sio.emit('unsubscribe', {
                'event': 'unsubscribe',
                'channel': [f'{coindcx_symbol}_price_change']
            })
            
            logger.info(f"Unsubscribed from CoinDCX price updates for {symbol} ({coindcx_symbol})")
            
        except Exception as e:
            logger.error(f"Failed to unsubscribe from CoinDCX symbol {symbol}: {e}")
    
    async def _handle_ticker_update(self, ticker_data):
        """Handle ticker price updates from Socket.io."""
        try:
            # CoinDCX ticker data structure may vary, adapt as needed
            if isinstance(ticker_data, dict):
                market = ticker_data.get('market') or ticker_data.get('symbol')
                if not market:
                    logger.debug(f"CoinDCX ticker missing market/symbol: {ticker_data}")
                    return
                
                # Only process symbols we're tracking
                if market not in self.target_symbols:
                    return
                
                symbol = self._convert_from_coindcx_symbol(market)
                
                # Get price data from CoinDCX ticker format
                last_price = ticker_data.get('last_price') or ticker_data.get('lastPrice') or ticker_data.get('price')
                bid_price = ticker_data.get('bid') or ticker_data.get('bidPrice')
                ask_price = ticker_data.get('ask') or ticker_data.get('askPrice')
                timestamp = ticker_data.get('timestamp', 0)
                
                # Convert timestamp to milliseconds if needed
                if timestamp and timestamp < 1e12:  # If it's in seconds
                    timestamp = int(timestamp * 1000)
                else:
                    timestamp = int(timestamp) if timestamp else 0
                
                logger.debug(f"CoinDCX {market}: price={last_price}, bid={bid_price}, ask={ask_price}")
                
                if not all([last_price, bid_price, ask_price]):
                    logger.debug(f"CoinDCX {market}: Missing price data - last_price={last_price}, bid={bid_price}, ask={ask_price}")
                    return
                
                # Convert to float with error handling
                price = float(last_price)
                bid = float(bid_price)
                ask = float(ask_price)
                
                if price <= 0 or bid <= 0 or ask <= 0:
                    logger.debug(f"CoinDCX {market}: Invalid price values - price={price}, bid={bid}, ask={ask}")
                    return
                
                price_data = self.format_price_data(symbol, price, bid, ask, timestamp)
                logger.debug(f"CoinDCX emitting price update for {symbol}: {price_data}")
                self.emit('price_update', price_data)
                
            else:
                logger.debug(f"CoinDCX received non-dict ticker data: {type(ticker_data)}")
                
        except (ValueError, TypeError) as e:
            logger.error(f"Error parsing CoinDCX ticker data: {e}, data: {ticker_data}")
        except Exception as e:
            logger.error(f"Unexpected error processing CoinDCX ticker data: {e}")
    
    async def handle_message(self, message):
        """Handle messages - not used for Socket.io since we use event handlers."""
        # Socket.io uses event handlers instead of message handling
        pass
    
    async def subscribe(self, symbol: str):
        """Subscribe to a symbol."""
        logger.info(f"WebSocket subscription requested for {symbol} on {self.name}")
        self.subscribed_symbols.add(symbol)
        self.target_symbols.add(symbol)
        
        # If already connected, subscribe immediately
        if self.connected_to_socketio:
            await self._subscribe_to_symbol(symbol)
    
    async def unsubscribe(self, symbol: str):
        """Unsubscribe from a symbol."""
        logger.info(f"WebSocket unsubscription requested for {symbol} on {self.name}")
        
        if symbol in self.subscribed_symbols:
            self.subscribed_symbols.remove(symbol)
        if symbol in self.target_symbols:
            self.target_symbols.remove(symbol)
        
        # If connected, unsubscribe from Socket.io
        if self.connected_to_socketio:
            await self._unsubscribe_from_symbol(symbol)
    
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
        
        # Close HTTP session
        if self.session and not self.session.closed:
            await self.session.close()
        
        # Disconnect from Socket.io if using WebSocket
        if self.sio and self.connected_to_socketio:
            try:
                await self.sio.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting from CoinDCX Socket.io: {e}")
        
        self.sio = None
        self.session = None
        self.polling_task = None
        self.is_connected = False
        self.connected_to_socketio = False
        self.subscribed_symbols.clear()
        self.target_symbols.clear()
        logger.info(f"Disconnected from {self.name}")
    
    def get_ping_message(self) -> Optional[Dict]:
        # Socket.io handles ping/pong automatically
        return None
    
    async def on_connect(self):
        """Override base class on_connect to avoid WebSocket ping setup."""
        # Socket.io handles keep-alive automatically, no need for manual ping
        pass
    
    def normalize_symbol(self, symbol: str) -> str:
        """Convert standard symbol to CoinDCX format."""
        return self._convert_to_coindcx_symbol(symbol)