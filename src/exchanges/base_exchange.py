import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Optional, Set, Any
import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException

logger = logging.getLogger(__name__)

class BaseExchange(ABC):
    def __init__(self, name: str):
        self.name = name
        self.ws = None
        self.is_connected = False
        self.reconnect_interval = 5.0
        self.max_reconnect_attempts = 10
        self.reconnect_attempts = 0
        self.subscribed_symbols: Set[str] = set()
        self.ping_task = None
        self.listen_task = None
        self.event_callbacks = {}
        self.is_shutting_down = False
    
    def on(self, event: str, callback):
        """Register event callback."""
        if event not in self.event_callbacks:
            self.event_callbacks[event] = []
        self.event_callbacks[event].append(callback)
    
    def emit(self, event: str, data: Any):
        """Emit event to registered callbacks."""
        if event in self.event_callbacks:
            for callback in self.event_callbacks[event]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        asyncio.create_task(callback(data))
                    else:
                        callback(data)
                except Exception as e:
                    logger.error(f"Error in event callback for {event}: {e}")
    
    async def connect(self):
        """Connect to the WebSocket endpoint."""
        try:
            ws_url = self.get_websocket_url()
            logger.info(f"Connecting to {self.name}...")
            
            # Skip WebSocket connection for exchanges that don't use standard WebSocket
            if ws_url.startswith('ws://localhost:') and ':9999' in ws_url:
                logger.info(f"Skipping WebSocket connection for {self.name} (uses custom connection)")
                self.is_connected = True
                await self.on_connect()
                return
            
            self.ws = await websockets.connect(
                ws_url,
                ping_interval=30,
                ping_timeout=10,
                close_timeout=10
            )
            
            self.is_connected = True
            self.reconnect_attempts = 0
            logger.info(f"Connected to {self.name}")
            
            await self.on_connect()
            
            # Start listening for messages
            self.listen_task = asyncio.create_task(self._listen_messages())
            
        except Exception as e:
            logger.error(f"Failed to connect to {self.name}: {e}")
            raise
    
    async def _listen_messages(self):
        """Listen for incoming WebSocket messages."""
        try:
            async for message in self.ws:
                if self.is_shutting_down:
                    break
                    
                try:
                    # Handle string messages (parse JSON)
                    if isinstance(message, str):
                        try:
                            data = json.loads(message)
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse JSON message from {self.name}: {e}")
                            continue
                    # Handle binary messages
                    elif isinstance(message, bytes):
                        try:
                            data = json.loads(message.decode('utf-8'))
                        except (json.JSONDecodeError, UnicodeDecodeError) as e:
                            logger.error(f"Failed to parse binary message from {self.name}: {e}")
                            continue
                    # Message is already parsed (shouldn't happen but handle gracefully)
                    else:
                        data = message
                    
                    # Only call handle_message if we have valid data
                    if data is not None:
                        await self.handle_message(data)
                    else:
                        logger.debug(f"Received None message from {self.name}")
                        
                except Exception as e:
                    logger.debug(f"Message handling issue from {self.name}: {e}")
                    # Only log as error if it's not a known message format issue
                    if "has no attribute 'get'" not in str(e):
                        logger.error(f"Error handling message from {self.name}: {e}")
                    
        except ConnectionClosed:
            logger.warning(f"Connection closed for {self.name}")
            await self._handle_disconnect()
        except WebSocketException as e:
            logger.error(f"WebSocket error for {self.name}: {e}")
            await self._handle_disconnect()
        except Exception as e:
            logger.error(f"Unexpected error in message listener for {self.name}: {e}")
            await self._handle_disconnect()
    
    async def _handle_disconnect(self):
        """Handle WebSocket disconnection."""
        self.is_connected = False
        
        if self.ping_task:
            self.ping_task.cancel()
            self.ping_task = None
        
        if not self.is_shutting_down and self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            logger.info(f"Attempting to reconnect to {self.name} ({self.reconnect_attempts}/{self.max_reconnect_attempts})")
            
            await asyncio.sleep(self.reconnect_interval)
            
            try:
                await self.connect()
                # Re-subscribe to all symbols
                for symbol in self.subscribed_symbols.copy():
                    await self.subscribe(symbol)
            except Exception as e:
                logger.error(f"Reconnection failed for {self.name}: {e}")
        else:
            if not self.is_shutting_down:
                logger.error(f"Max reconnection attempts reached for {self.name}")
                self.emit('max_reconnect_attempts_reached', self.name)
    
    async def subscribe(self, symbol: str):
        """Subscribe to a symbol's price updates."""
        if not self.is_connected:
            raise ConnectionError(f"Not connected to {self.name}")
        
        self.subscribed_symbols.add(symbol)
        subscribe_message = self.get_subscribe_message(symbol)
        
        await self.ws.send(json.dumps(subscribe_message))
        logger.info(f"Subscribed to {symbol} on {self.name}")
    
    async def unsubscribe(self, symbol: str):
        """Unsubscribe from a symbol's price updates."""
        if not self.is_connected:
            return
        
        self.subscribed_symbols.discard(symbol)
        unsubscribe_message = self.get_unsubscribe_message(symbol)
        
        await self.ws.send(json.dumps(unsubscribe_message))
        logger.info(f"Unsubscribed from {symbol} on {self.name}")
    
    async def start_ping(self):
        """Start periodic ping messages."""
        async def ping_loop():
            while self.is_connected and not self.is_shutting_down:
                try:
                    ping_message = self.get_ping_message()
                    if ping_message:
                        await self.ws.send(json.dumps(ping_message))
                    else:
                        await self.ws.ping()
                    
                    await asyncio.sleep(30)
                except Exception as e:
                    logger.error(f"Error sending ping to {self.name}: {e}")
                    break
        
        self.ping_task = asyncio.create_task(ping_loop())
    
    async def disconnect(self):
        """Disconnect from the WebSocket."""
        self.is_shutting_down = True
        
        if self.ping_task:
            self.ping_task.cancel()
            self.ping_task = None
        
        if self.listen_task:
            self.listen_task.cancel()
            self.listen_task = None
        
        if self.ws and not self.ws.closed:
            await self.ws.close()
        
        self.is_connected = False
        self.subscribed_symbols.clear()
        logger.info(f"Disconnected from {self.name}")
    
    def normalize_symbol(self, symbol: str) -> str:
        """Normalize symbol format."""
        return symbol.upper()
    
    def format_price_data(self, symbol: str, price: float, bid: Optional[float], ask: Optional[float], timestamp: Optional[int] = None) -> Dict:
        """Format price data for emission."""
        return {
            'exchange': self.name,
            'symbol': self.normalize_symbol(symbol),
            'price': float(price),
            'bid': float(bid) if bid is not None else None,
            'ask': float(ask) if ask is not None else None,
            'timestamp': timestamp or int(time.time() * 1000)
        }
    
    # Abstract methods that must be implemented by subclasses
    @abstractmethod
    def get_websocket_url(self) -> str:
        """Return the WebSocket URL for this exchange."""
        pass
    
    @abstractmethod
    def get_subscribe_message(self, symbol: str) -> Dict:
        """Return the subscription message for a symbol."""
        pass
    
    @abstractmethod
    def get_unsubscribe_message(self, symbol: str) -> Dict:
        """Return the unsubscription message for a symbol."""
        pass
    
    @abstractmethod
    async def handle_message(self, message):
        """Handle incoming WebSocket messages. Message can be Dict, list, or other types."""
        pass
    
    async def on_connect(self):
        """Called after successful connection. Override in subclasses if needed."""
        await self.start_ping()
    
    def get_ping_message(self) -> Optional[Dict]:
        """Return ping message. Override in subclasses if needed."""
        return None