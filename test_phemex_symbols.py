#!/usr/bin/env python3

import asyncio
import websockets
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_phemex_symbols():
    """Test different symbol variations on Phemex."""
    uri = "wss://ws.phemex.com"
    
    # Test different possible ETH symbols
    symbols_to_test = [
        'ETHUSD',
        'ETHUSDT', 
        'ETH-USD',
        'ETH-USDT',
        'ETHUSDP',  # Sometimes perpetual contracts have P suffix
        'ETHUSDT.P'
    ]
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info(f"Connected to Phemex WebSocket: {uri}")
            
            # Subscribe to each symbol
            for i, symbol in enumerate(symbols_to_test):
                message = {
                    'id': i + 10,
                    'method': 'orderbook.subscribe',
                    'params': [symbol, 20]
                }
                
                logger.info(f"Testing symbol: {symbol}")
                await websocket.send(json.dumps(message))
                await asyncio.sleep(0.5)  # Wait a bit between subscriptions
            
            # Listen for responses
            message_count = 0
            while message_count < 20:  # Listen for responses
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                    message = json.loads(response)
                    
                    message_count += 1
                    
                    # Look for subscription confirmations or errors
                    if message.get('id') and message.get('id') >= 10:
                        symbol_index = message['id'] - 10
                        tested_symbol = symbols_to_test[symbol_index] if symbol_index < len(symbols_to_test) else 'unknown'
                        
                        if message.get('error'):
                            logger.error(f"❌ {tested_symbol}: {message['error']}")
                        elif message.get('result'):
                            if message['result'].get('status') == 'success':
                                logger.info(f"✅ {tested_symbol}: Subscription successful")
                            else:
                                logger.info(f"⚠️  {tested_symbol}: {message['result']}")
                    
                    # Look for actual orderbook data
                    if 'book' in message and 'symbol' in message:
                        symbol = message['symbol']
                        logger.info(f"📊 Received orderbook data for: {symbol}")
                        
                        if symbol == 'ETHUSD':
                            logger.info("🎉 ETHUSD data confirmed!")
                            break
                            
                except asyncio.TimeoutError:
                    logger.warning("Timeout waiting for message")
                    break
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
    except Exception as e:
        logger.error(f"Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(test_phemex_symbols())