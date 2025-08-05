#!/usr/bin/env python3

import asyncio
import websockets
import json
import logging
import sys
sys.path.append('src')

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_phemex_direct():
    """Test Phemex WebSocket connection directly."""
    uri = "wss://ws.phemex.com"
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info(f"Connected to Phemex WebSocket: {uri}")
            
            # Subscribe to BTCUSD (should work)
            btc_message = {
                'id': 1,
                'method': 'orderbook.subscribe',
                'params': ['BTCUSD', 20]
            }
            
            # Subscribe to ETHUSD (test this)
            eth_message = {
                'id': 2,
                'method': 'orderbook.subscribe',
                'params': ['ETHUSD', 20]
            }
            
            logger.info(f"Sending BTC subscription: {btc_message}")
            await websocket.send(json.dumps(btc_message))
            
            logger.info(f"Sending ETH subscription: {eth_message}")
            await websocket.send(json.dumps(eth_message))
            
            # Listen for responses
            message_count = 0
            while message_count < 20:  # Listen for 20 messages
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    message = json.loads(response)
                    
                    message_count += 1
                    logger.info(f"Message {message_count}: {json.dumps(message, indent=2)}")
                    
                    # Look for subscription confirmations or errors
                    if message.get('id') in [1, 2]:
                        logger.info(f"Subscription response for ID {message['id']}: {message}")
                    
                    # Look for orderbook data
                    if 'book' in message and 'symbol' in message:
                        symbol = message['symbol']
                        logger.info(f"Orderbook data received for {symbol}")
                        
                        if symbol == 'ETHUSD':
                            logger.info("✅ ETHUSD data received!")
                            logger.info(f"ETHUSD orderbook: {message}")
                            
                    
                except asyncio.TimeoutError:
                    logger.warning("Timeout waiting for message")
                    break
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
    except Exception as e:
        logger.error(f"Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(test_phemex_direct())