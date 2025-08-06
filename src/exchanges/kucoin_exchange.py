import logging
import asyncio
import json
import urllib.request
import urllib.parse
from typing import Dict, Optional
from .base_exchange import BaseExchange

logger = logging.getLogger(__name__)

class KucoinExchange(BaseExchange):
    def __init__(self):
        super().__init__('kucoin')
        self.token = None
        self.endpoint = None
        self.req_id = 1
    
    async def get_websocket_token(self):
        """Get WebSocket token from KuCoin API using urllib."""
        try:
            # Run the synchronous urllib request in a thread pool
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, self._fetch_token_sync)
            
            if data and data.get('code') == '200000':
                token_data = data['data']
                self.token = token_data['token']
                instance_servers = token_data.get('instanceServers', [])
                if instance_servers:
                    self.endpoint = instance_servers[0]['endpoint']
                    logger.info(f"KuCoin WebSocket token obtained successfully")
                    return True
                else:
                    logger.error("KuCoin API returned no instance servers")
                    return False
            else:
                logger.error(f"KuCoin API error: {data.get('msg', 'Unknown error') if data else 'No response'}")
                return False
                
        except Exception as e:
            logger.error(f"Error getting KuCoin WebSocket token: {e}")
            return False
    
    def _fetch_token_sync(self):
        """Synchronous token fetch using urllib."""
        try:
            # Create POST request for KuCoin token
            url = 'https://api.kucoin.com/api/v1/bullet-public'
            data = urllib.parse.urlencode({}).encode('utf-8')
            
            request = urllib.request.Request(url, data=data, method='POST')
            request.add_header('Content-Type', 'application/x-www-form-urlencoded')
            
            with urllib.request.urlopen(request, timeout=10) as response:
                if response.status == 200:
                    response_data = response.read().decode('utf-8')
                    return json.loads(response_data)
                else:
                    logger.error(f"Failed to get KuCoin token. Status: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"HTTP error getting KuCoin token: {e}")
            return None
    
    def get_websocket_url(self) -> str:
        if not self.endpoint or not self.token:
            return f"wss://ws-api.kucoin.com/endpoint?token=placeholder"
        return f"{self.endpoint}?token={self.token}&[connectId=welcome]"
    
    async def connect(self):
        """Connect to KuCoin WebSocket with token authentication."""
        if not await self.get_websocket_token():
            logger.error("Failed to get KuCoin WebSocket token - cannot establish connection")
            raise ConnectionError("KuCoin WebSocket token authentication failed")
        
        logger.info(f"Connecting to KuCoin WebSocket: {self.get_websocket_url()}")
        return await super().connect()
    
    def get_subscribe_message(self, symbol: str) -> Dict:
        # Symbol is already in KuCoin format from configuration
        message = {
            'id': self.req_id,
            'type': 'subscribe',
            'topic': f'/contractMarket/ticker:{symbol}',
            'privateChannel': False,
            'response': True
        }
        self.req_id += 1
        return message
    
    def get_unsubscribe_message(self, symbol: str) -> Dict:
        # Symbol is already in KuCoin format from configuration
        message = {
            'id': self.req_id,
            'type': 'unsubscribe',
            'topic': f'/contractMarket/ticker:{symbol}',
            'privateChannel': False,
            'response': True
        }
        self.req_id += 1
        return message
    
    async def handle_message(self, message: Dict):
        # Add debug logging
        logger.debug(f"KuCoin message: {message}")
        
        # Handle subscription confirmation
        if message.get('type') == 'ack':
            logger.info(f"KuCoin subscription confirmed for request {message.get('id')}")
            return
        
        # Handle welcome message
        if message.get('type') == 'welcome':
            logger.info("KuCoin WebSocket connection established")
            return
        
        # Handle pong responses
        if message.get('type') == 'pong':
            logger.debug('Received pong from KuCoin')
            return
        
        # Handle price data
        if message.get('type') == 'message' and 'data' in message:
            logger.debug(f"KuCoin price data: {message['data']}")
            await self._handle_price_update(message)
        else:
            logger.debug(f"KuCoin unknown message format: {message.keys()}")
    
    async def _handle_price_update(self, message: Dict):
        """Handle ticker price updates."""
        data = message.get('data')
        if not data:
            return
        
        # Extract symbol from topic
        topic = message.get('topic', '')
        if not topic.startswith('/contractMarket/ticker:'):
            return
        
        kucoin_symbol = topic.split(':')[1]
        # Use KuCoin symbol directly - mapping will handle display symbol conversion
        symbol = kucoin_symbol
        
        # Get price data
        price = float(data.get('price', 0))
        bid = float(data.get('bestBidPrice', 0))
        ask = float(data.get('bestAskPrice', 0))
        timestamp = int(data.get('ts', 0)) // 1000000  # Convert from nanoseconds to milliseconds
        
        if price == 0 or bid == 0 or ask == 0:
            return
        
        price_data = self.format_price_data(symbol, price, bid, ask, timestamp)
        self.emit('price_update', price_data)
    
    def get_ping_message(self) -> Optional[Dict]:
        message = {
            'id': self.req_id,
            'type': 'ping'
        }
        self.req_id += 1
        return message
    
    def normalize_symbol(self, symbol: str) -> str:
        """Normalize symbol format - keep KuCoin format for output."""
        return symbol.upper()