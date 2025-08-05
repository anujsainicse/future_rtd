from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import logging
import sys
import os
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel
import uvicorn

# Add parent directory to path to import our price fetcher
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the price fetcher components directly
from src.price_manager import PriceManager
from src.exchanges.binance_exchange import BinanceExchange
from src.exchanges.bybit_exchange import BybitExchange
from src.exchanges.okx_exchange import OKXExchange
from src.exchanges.kucoin_exchange import KucoinExchange
from src.exchanges.deribit_exchange import DeribitExchange
from src.exchanges.bitget_exchange import BitgetExchange
from src.exchanges.gateio_exchange import GateioExchange
from src.exchanges.mexc_exchange import MexcExchange
from src.exchanges.bitmex_exchange import BitmexExchange
from src.exchanges.phemex_exchange import PhemexExchange
from src.exchanges.coindcx_exchange import CoindcxExchange
from src.utils.input_parser import InputParser

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Crypto Futures Price API",
    description="Real-time cryptocurrency futures price tracking and arbitrage detection",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple price fetcher class for backend integration
class SimplePriceFetcher:
    def __init__(self):
        self.price_manager = PriceManager()
        self.exchanges = {}
        self.active_connections = set()
        self.supported_exchanges = ['binance', 'bybit', 'okx', 'kucoin', 'deribit', 'bitget', 'gateio', 'mexc', 'bitmex', 'phemex', 'coindcx']
        self.exchange_classes = {
            'binance': BinanceExchange,
            'bybit': BybitExchange,
            'okx': OKXExchange,
            'kucoin': KucoinExchange,
            'deribit': DeribitExchange,
            'bitget': BitgetExchange,
            'gateio': GateioExchange,
            'mexc': MexcExchange,
            'bitmex': BitmexExchange,
            'phemex': PhemexExchange,
            'coindcx': CoindcxExchange
        }
    
    async def initialize_exchanges(self, config_data):
        """Initialize exchanges from config."""
        exchange_config = config_data['exchanges']
        config_format = config_data.get('format', 'legacy')
        
        for exchange_name, symbols in exchange_config.items():
            if exchange_name not in self.exchange_classes:
                continue
                
            exchange_class = self.exchange_classes[exchange_name]
            exchange = exchange_class()
            self.exchanges[exchange_name] = exchange
            
            # Setup event handlers with symbol mapping support
            if config_format == 'symbol_ticker':
                exchange.on('price_update', lambda data, ex=exchange_name: self._handle_price_update_with_mapping(data, ex, config_data['pairs']))
            else:
                exchange.on('price_update', self.price_manager.update_price)
            
            try:
                await exchange.connect()
                self.active_connections.add(exchange_name)
                
                if config_format == 'symbol_ticker':
                    # symbols is a list of dicts with display_symbol and ticker
                    for symbol_data in symbols:
                        ticker = symbol_data['ticker']
                        await exchange.subscribe(ticker)
                        await asyncio.sleep(0.1)
                else:
                    # Legacy format - symbols is a list of strings
                    for symbol in symbols:
                        await exchange.subscribe(symbol)
                        await asyncio.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"Failed to connect to {exchange_name}: {e}")
    
    def _handle_price_update_with_mapping(self, data, exchange_name, pairs):
        """Handle price updates with ticker to display symbol mapping."""
        ticker = data['symbol']
        
        # Find the display symbol for this ticker and exchange
        display_symbol = None
        for pair in pairs:
            if pair['exchange'] == exchange_name and pair['ticker'] == ticker:
                display_symbol = pair['display_symbol']
                break
        
        if display_symbol:
            # Update the data with display symbol
            updated_data = data.copy()
            updated_data['symbol'] = display_symbol
            updated_data['ticker'] = ticker  # Keep original ticker for reference
            
            # Pass to price manager
            self.price_manager.update_price(updated_data)
        else:
            # Fallback to original symbol if no mapping found
            logger.warning(f"No display symbol mapping found for {ticker} on {exchange_name}")
            self.price_manager.update_price(data)
    
    def get_api(self):
        """Get API interface."""
        return {
            'get_all_prices': self.price_manager.get_all_prices,
            'get_prices_by_symbol': self.price_manager.get_prices_by_symbol,
            'get_spread': self.price_manager.get_spread,
            'get_market_summary': self.price_manager.get_market_summary,
            'get_best_prices': self.price_manager.get_best_prices,
            'check_arbitrage_opportunities': self.price_manager.check_arbitrage_opportunities,
            'get_arbitrage_alert_status': self.price_manager.get_arbitrage_alert_status
        }

# Global variables
price_fetcher: Optional[SimplePriceFetcher] = None
websocket_connections: List[WebSocket] = []

# Pydantic models
class PriceData(BaseModel):
    symbol: str
    exchange: str
    price: float
    bid: Optional[float]
    ask: Optional[float]
    timestamp: int

class ArbitrageOpportunity(BaseModel):
    symbol: str
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    spread: float
    spread_percentage: float
    potential_profit: float

class MarketSummary(BaseModel):
    total_symbols: int
    total_exchanges: int
    symbols: List[str]
    exchanges: List[str]
    price_count: int
    last_update: float

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending message to websocket: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to websocket: {e}")
                disconnected.append(connection)
        
        # Remove disconnected websockets
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    """Initialize the price fetcher on startup."""
    global price_fetcher
    
    logger.info("Starting up FastAPI server...")
    
    # Initialize price fetcher
    price_fetcher = SimplePriceFetcher()
    
    # Set up event handlers for real-time updates
    def on_price_update(data):
        asyncio.create_task(broadcast_price_update(data))
    
    def on_arbitrage_opportunity(opportunities):
        if opportunities:
            asyncio.create_task(broadcast_arbitrage_opportunities(opportunities))
    
    price_fetcher.price_manager.on('price_update', on_price_update)
    price_fetcher.price_manager.on('arbitrage_opportunity', on_arbitrage_opportunity)
    
    # Start the price fetcher in the background
    asyncio.create_task(start_price_fetcher())
    
    logger.info("FastAPI server startup complete")

async def start_price_fetcher():
    """Start the price fetcher with default symbols."""
    try:
        # Load symbols configuration - try new format first, fallback to CSV
        futures_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'futures_symbols.txt')
        symbols_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'symbols.csv')
        
        config_file = futures_file if os.path.exists(futures_file) else symbols_file
        logger.info(f"Loading configuration from: {config_file}")
        
        parsed_data = await InputParser.parse_file(config_file)
        valid_exchanges = InputParser.validate_exchange_support(
            parsed_data['exchanges'], 
            price_fetcher.supported_exchanges
        )
        
        # Create config data structure
        config_data = {
            'exchanges': valid_exchanges,
            'format': parsed_data.get('format', 'legacy'),
            'pairs': parsed_data.get('pairs', [])
        }
        
        # Initialize exchanges
        await price_fetcher.initialize_exchanges(config_data)
        logger.info(f"Started price fetcher with {len(valid_exchanges)} exchanges using {parsed_data.get('format', 'legacy')} format")
        
    except Exception as e:
        logger.error(f"Error starting price fetcher: {e}")

async def broadcast_price_update(data):
    """Broadcast price updates to all connected WebSocket clients."""
    message = {
        "type": "price_update",
        "data": {
            "symbol": data["symbol"],
            "exchange": data["exchange"],
            "price": data["data"]["price"],
            "bid": data["data"]["bid"],
            "ask": data["data"]["ask"],
            "timestamp": data["data"]["timestamp"]
        }
    }
    await manager.broadcast(json.dumps(message))

async def broadcast_arbitrage_opportunities(opportunities):
    """Broadcast arbitrage opportunities to all connected WebSocket clients."""
    message = {
        "type": "arbitrage_opportunities",
        "data": [
            {
                "symbol": opp["symbol"],
                "buy_exchange": opp["buy_exchange"],
                "sell_exchange": opp["sell_exchange"],
                "buy_price": opp["lower_price"],
                "sell_price": opp["higher_price"],
                "spread": opp["spread"],
                "spread_percentage": opp["spread_percentage"],
                "potential_profit": opp["potential_profit"]
            }
            for opp in opportunities[:5]  # Send top 5 opportunities
        ]
    }
    await manager.broadcast(json.dumps(message))

# REST API endpoints
@app.get("/")
async def root():
    return {"message": "Crypto Futures Price API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "price_fetcher_active": price_fetcher is not None,
        "websocket_connections": len(manager.active_connections)
    }

@app.get("/api/prices", response_model=Dict)
async def get_all_prices():
    """Get all current prices."""
    if not price_fetcher:
        return {"error": "Price fetcher not initialized"}
    
    api = price_fetcher.get_api()
    prices = api['get_all_prices']()
    return {"prices": prices, "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/prices/{symbol}")
async def get_symbol_prices(symbol: str):
    """Get prices for a specific symbol."""
    if not price_fetcher:
        return {"error": "Price fetcher not initialized"}
    
    api = price_fetcher.get_api()
    prices = api['get_prices_by_symbol'](symbol.upper())
    
    if not prices:
        return {"error": f"No prices found for symbol {symbol}"}
    
    return {
        "symbol": symbol.upper(),
        "prices": prices,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/spread/{symbol}/{exchange1}/{exchange2}")
async def get_spread(symbol: str, exchange1: str, exchange2: str):
    """Get spread between two exchanges for a symbol."""
    if not price_fetcher:
        return {"error": "Price fetcher not initialized"}
    
    api = price_fetcher.get_api()
    spread = api['get_spread'](symbol.upper(), exchange1.lower(), exchange2.lower())
    
    if not spread:
        return {"error": f"No spread data found for {symbol} between {exchange1} and {exchange2}"}
    
    return spread

@app.get("/api/arbitrage")
async def get_arbitrage_opportunities():
    """Get current arbitrage opportunities."""
    if not price_fetcher:
        return {"error": "Price fetcher not initialized"}
    
    api = price_fetcher.get_api()
    all_opportunities = []
    
    # Get opportunities for each symbol
    symbols = api['get_market_summary']()['symbols']
    for symbol in symbols:
        opportunities = api['check_arbitrage_opportunities'](symbol, 0.05)  # 0.05% minimum spread
        all_opportunities.extend(opportunities)
    
    # Sort by potential profit
    all_opportunities.sort(key=lambda x: x['potential_profit'], reverse=True)
    
    return {
        "opportunities": all_opportunities[:20],  # Top 20 opportunities
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/arbitrage/{symbol}")
async def get_symbol_arbitrage(symbol: str, min_spread: float = 0.1):
    """Get arbitrage opportunities for a specific symbol."""
    if not price_fetcher:
        return {"error": "Price fetcher not initialized"}
    
    api = price_fetcher.get_api()
    opportunities = api['check_arbitrage_opportunities'](symbol.upper(), min_spread)
    
    return {
        "symbol": symbol.upper(),
        "opportunities": opportunities,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/arbitrage/{symbol}/alert-status")
async def get_arbitrage_alert_status(symbol: str):
    """Get arbitrage alert status for a specific symbol."""
    if not price_fetcher:
        return {"error": "Price fetcher not initialized"}
    
    api = price_fetcher.get_api()
    status = api['get_arbitrage_alert_status'](symbol.upper())
    
    return {
        **status,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/summary", response_model=MarketSummary)
async def get_market_summary():
    """Get market summary statistics."""
    if not price_fetcher:
        return {"error": "Price fetcher not initialized"}
    
    api = price_fetcher.get_api()
    summary = api['get_market_summary']()
    
    return MarketSummary(**summary)

@app.get("/api/best-prices/{symbol}")
async def get_best_prices(symbol: str):
    """Get best bid/ask prices across all exchanges for a symbol."""
    if not price_fetcher:
        return {"error": "Price fetcher not initialized"}
    
    api = price_fetcher.get_api()
    best_prices = api['get_best_prices'](symbol.upper())
    
    if not best_prices:
        return {"error": f"No price data found for symbol {symbol}"}
    
    return best_prices

@app.post("/api/reload-config")
async def reload_configuration():
    """Reload the futures_symbols.txt configuration file."""
    global price_fetcher
    
    if not price_fetcher:
        return {"error": "Price fetcher not initialized"}
    
    try:
        # Disconnect all existing exchanges
        for exchange in price_fetcher.exchanges.values():
            try:
                await exchange.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting exchange: {e}")
        
        # Clear existing data
        price_fetcher.exchanges.clear()
        price_fetcher.active_connections.clear()
        
        # Reload configuration and reinitialize
        futures_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'futures_symbols.txt')
        symbols_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'symbols.csv')
        
        config_file = futures_file if os.path.exists(futures_file) else symbols_file
        logger.info(f"Reloading configuration from: {config_file}")
        
        parsed_data = await InputParser.parse_file(config_file)
        valid_exchanges = InputParser.validate_exchange_support(
            parsed_data['exchanges'], 
            price_fetcher.supported_exchanges
        )
        
        config_data = {
            'exchanges': valid_exchanges,
            'format': parsed_data.get('format', 'legacy'),
            'pairs': parsed_data.get('pairs', [])
        }
        
        # Initialize exchanges with new config
        await price_fetcher.initialize_exchanges(config_data)
        
        return {
            "status": "success",
            "message": f"Configuration reloaded with {len(valid_exchanges)} exchanges",
            "exchanges": list(valid_exchanges.keys()),
            "total_symbols": sum(len(symbols) for symbols in valid_exchanges.values()),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error reloading configuration: {e}")
        return {"error": f"Failed to reload configuration: {str(e)}"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time price updates."""
    await manager.connect(websocket)
    
    try:
        # Send initial data
        if price_fetcher:
            api = price_fetcher.get_api()
            
            # Send current market summary
            summary = api['get_market_summary']()
            await websocket.send_text(json.dumps({
                "type": "market_summary",
                "data": summary
            }))
            
            # Send current prices
            prices = api['get_all_prices']()
            await websocket.send_text(json.dumps({
                "type": "initial_prices",
                "data": prices
            }))
        
        # Keep connection alive
        while True:
            data = await websocket.receive_text()
            # Echo back any received messages (for debugging)
            await websocket.send_text(f"Echo: {data}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )