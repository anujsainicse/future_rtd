#!/usr/bin/env python3

import os
import sys

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test imports
try:
    print("🧪 Testing imports...")
    from src.price_manager import PriceManager
    print("✅ PriceManager imported")
    
    from src.exchanges.binance_exchange import BinanceExchange
    from src.exchanges.bybit_exchange import BybitExchange  
    from src.exchanges.okx_exchange import OKXExchange
    print("✅ Exchange classes imported")
    
    from src.utils.input_parser import InputParser
    print("✅ InputParser imported")
    
    print("✅ All core components working!")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test backend
try:
    print("🌐 Testing backend...")
    os.chdir('backend')
    
    # Import backend modules
    import main
    print("✅ Backend main module imported")
    
    # Test FastAPI app creation
    app = main.app
    print("✅ FastAPI app created")
    
    print("🎉 Backend is ready!")
    print("🚀 Starting backend server...")
    
    # Start the server
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    
except Exception as e:
    print(f"❌ Backend error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)