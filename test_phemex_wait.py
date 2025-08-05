#!/usr/bin/env python3

import asyncio
import websockets
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_phemex_wait():
    """Test with longer wait to see if ETHUSD data arrives."""
    uri = "wss://ws.phemex.com"
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info(f"Connected to Phemex WebSocket: {uri}")
            
            # Subscribe to ETHUSD
            eth_message = {
                'id': 100,
                'method': 'orderbook.subscribe',
                'params': ['ETHUSD', 20]
            }
            
            logger.info("Subscribing to ETHUSD...")
            await websocket.send(json.dumps(eth_message))
            
            # Wait for longer to see if any ETHUSD data comes through
            start_time = asyncio.get_event_loop().time()
            eth_data_received = False
            
            while (asyncio.get_event_loop().time() - start_time) < 60:  # Wait up to 60 seconds
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    message = json.loads(response)
                    
                    # Check for subscription confirmation
                    if message.get('id') == 100:
                        if message.get('error'):
                            logger.error(f"ETHUSD subscription error: {message['error']}")
                            break
                        elif message.get('result'):
                            logger.info(f"ETHUSD subscription confirmed: {message['result']}")
                    
                    # Check for orderbook data
                    if 'book' in message and 'symbol' in message:
                        symbol = message['symbol']
                        if symbol == 'ETHUSD':
                            logger.info(f"🎉 ETHUSD orderbook data received!")
                            logger.info(f"ETHUSD data: {json.dumps(message, indent=2)}")
                            eth_data_received = True
                            break
                        else:
                            logger.info(f"Received data for other symbol: {symbol}")
                    
                except asyncio.TimeoutError:
                    logger.info("Still waiting for ETHUSD data...")
                    continue
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
            if not eth_data_received:
                logger.warning("❌ No ETHUSD orderbook data received after 60 seconds")
                logger.warning("This suggests ETHUSD may not be actively traded on Phemex")
                    
    except Exception as e:
        logger.error(f"Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(test_phemex_wait())