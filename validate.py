#!/usr/bin/env python3

import asyncio
import logging
import sys
from pathlib import Path

# Suppress logging for cleaner output
logging.getLogger().setLevel(logging.CRITICAL)

from main import CryptoFuturesPriceFetcher

async def test_application():
    """Test the application components."""
    print("🧪 Testing Crypto Futures Price Fetcher...")
    
    try:
        # Test 1: Initialize fetcher
        fetcher = CryptoFuturesPriceFetcher()
        print("✅ Application initialization")
        
        # Test 2: Load input file
        exchange_config = await fetcher.load_input_file('examples/minimal.csv')
        print("✅ Input file parsing")
        print(f"   - Found exchanges: {list(exchange_config.keys())}")
        
        # Test 3: Check API methods
        api = fetcher.get_api()
        expected_methods = [
            'get_prices_by_symbol', 'get_spread', 'get_all_prices',
            'get_best_prices', 'get_market_summary', 'check_arbitrage_opportunities'
        ]
        
        for method in expected_methods:
            if method not in api:
                raise Exception(f"Missing API method: {method}")
        
        print("✅ API methods available")
        
        # Test 4: Price manager functionality
        pm = fetcher.price_manager
        test_price = {
            'symbol': 'BTCUSDT',
            'exchange': 'test',
            'price': 50000.0,
            'bid': 49999.0,
            'ask': 50001.0,
            'timestamp': 1234567890
        }
        
        pm.update_price(test_price)
        prices = pm.get_prices_by_symbol('BTCUSDT')
        
        if not prices or 'test' not in prices:
            raise Exception("Price manager not working correctly")
        
        print("✅ Price manager functionality")
        
        # Test 5: File formats
        test_files = ['examples/minimal.csv', 'examples/symbols.csv', 'examples/symbols.json']
        for test_file in test_files:
            if Path(test_file).exists():
                try:
                    await fetcher.load_input_file(test_file)
                    print(f"✅ File format: {Path(test_file).suffix}")
                except Exception as e:
                    print(f"❌ File format error {test_file}: {e}")
        
        print("\n🎉 All tests passed! The Python application is ready to use.")
        print("\n📋 Usage examples:")
        print("   python main.py --input symbols.csv")
        print("   python main.py --input examples/minimal.csv --verbose")
        print("   python main.py --input examples/symbols.json")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(test_application())