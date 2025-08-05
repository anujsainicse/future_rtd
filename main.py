#!/usr/bin/env python3

import asyncio
import logging
import signal
import sys
import time
from pathlib import Path
from typing import Dict, List, Set

import click

from src.utils.input_parser import InputParser
from src.price_manager import PriceManager
from src.exchanges.binance_exchange import BinanceExchange
from src.exchanges.bybit_exchange import BybitExchange
from src.exchanges.okx_exchange import OKXExchange

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class CryptoFuturesPriceFetcher:
    def __init__(self):
        self.price_manager = PriceManager()
        self.exchanges = {}
        self.active_connections = set()
        self.is_shutting_down = False
        self.stale_cleanup_task = None
        
        self.supported_exchanges = ['binance', 'bybit', 'okx']
        self.exchange_classes = {
            'binance': BinanceExchange,
            'bybit': BybitExchange,
            'okx': OKXExchange
        }
        
        self._setup_event_handlers()
        self._setup_graceful_shutdown()
    
    def _setup_event_handlers(self):
        """Setup event handlers for price updates and arbitrage detection."""
        def on_price_update(data):
            symbol = data['symbol']
            exchange = data['exchange']
            price_data = data['data']
            timestamp_str = time.strftime('%H:%M:%S', time.localtime(price_data['timestamp'] / 1000))
            
            logger.info(f"[{exchange.upper()}] {symbol}: ${price_data['price']:.4f} ({timestamp_str})")
        
        def on_arbitrage_opportunity(opportunities):
            if opportunities:
                best = opportunities[0]
                logger.info(f"🚀 ARBITRAGE: {best['symbol']} - "
                          f"Buy on {best['buy_exchange']} (${best['lower_price']:.4f}) → "
                          f"Sell on {best['sell_exchange']} (${best['higher_price']:.4f}) | "
                          f"Profit: {best['potential_profit']:.2f}%")
        
        self.price_manager.on('price_update', on_price_update)
        self.price_manager.on('arbitrage_opportunity', on_arbitrage_opportunity)
    
    def _setup_graceful_shutdown(self):
        """Setup graceful shutdown handlers."""
        def signal_handler(signum, frame):
            logger.info(f"\n🛑 Received signal {signum}, shutting down gracefully...")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def load_input_file(self, file_path: str) -> Dict[str, List[str]]:
        """Load and parse input file."""
        try:
            logger.info(f"Loading input file: {file_path}")
            parsed_data = await InputParser.parse_file(file_path)
            
            valid_exchanges = InputParser.validate_exchange_support(
                parsed_data['exchanges'],
                self.supported_exchanges
            )
            
            total_pairs = sum(len(symbols) for symbols in valid_exchanges.values())
            logger.info(f"Loaded {total_pairs} symbol pairs across {len(valid_exchanges)} exchanges")
            
            return valid_exchanges
            
        except Exception as e:
            logger.error(f"Failed to load input file: {e}")
            sys.exit(1)
    
    async def initialize_exchanges(self, exchange_config: Dict[str, List[str]]):
        """Initialize and connect to exchanges."""
        tasks = []
        
        for exchange_name, symbols in exchange_config.items():
            if exchange_name not in self.exchange_classes:
                logger.warning(f"Exchange {exchange_name} not supported, skipping")
                continue
            
            exchange_class = self.exchange_classes[exchange_name]
            exchange = exchange_class()
            
            self.exchanges[exchange_name] = exchange
            
            # Setup event handlers
            exchange.on('price_update', self.price_manager.update_price)
            exchange.on('error', lambda error, ex=exchange_name: logger.error(f"Exchange {ex} error: {error}"))
            exchange.on('max_reconnect_attempts_reached', 
                       lambda ex=exchange_name: self._handle_exchange_failure(ex))
            
            tasks.append(self._connect_to_exchange(exchange, symbols))
        
        # Connect to all exchanges concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                exchange_name = list(exchange_config.keys())[i]
                logger.error(f"Failed to initialize {exchange_name}: {result}")
    
    async def _connect_to_exchange(self, exchange, symbols: List[str]):
        """Connect to an exchange and subscribe to symbols."""
        try:
            await exchange.connect()
            self.active_connections.add(exchange.name)
            
            # Subscribe to symbols with small delays to avoid rate limits
            for symbol in symbols:
                try:
                    await exchange.subscribe(symbol)
                    await asyncio.sleep(0.1)  # Small delay between subscriptions
                except Exception as e:
                    logger.error(f"Failed to subscribe to {symbol} on {exchange.name}: {e}")
            
        except Exception as e:
            logger.error(f"Failed to connect to {exchange.name}: {e}")
            raise
    
    def _handle_exchange_failure(self, exchange_name: str):
        """Handle exchange connection failure."""
        logger.error(f"Exchange {exchange_name} reached max reconnection attempts")
        self.active_connections.discard(exchange_name)
    
    async def start_stale_cleanup(self):
        """Start periodic stale data cleanup."""
        self.stale_cleanup_task = await self.price_manager.start_stale_data_cleanup(60.0, 300.0)
    
    async def start_periodic_summary(self, interval: int = 30):
        """Start periodic market summary."""
        async def summary_loop():
            while not self.is_shutting_down:
                try:
                    summary = self.price_manager.get_market_summary()
                    logger.info(f"📊 Summary: {summary['total_symbols']} symbols, "
                              f"{summary['price_count']} prices from {summary['total_exchanges']} exchanges")
                    await asyncio.sleep(interval)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in summary loop: {e}")
                    await asyncio.sleep(interval)
        
        return asyncio.create_task(summary_loop())
    
    async def run(self, input_file: str, summary_interval: int = 30):
        """Run the price fetcher."""
        logger.info("🚀 Starting Crypto Futures Price Fetcher...")
        
        # Load input file
        exchange_config = await self.load_input_file(input_file)
        
        if not exchange_config:
            logger.error("No supported exchanges found in input file")
            sys.exit(1)
        
        # Initialize exchanges
        await self.initialize_exchanges(exchange_config)
        
        if not self.active_connections:
            logger.error("No active exchange connections established")
            sys.exit(1)
        
        # Start background tasks
        await self.start_stale_cleanup()
        summary_task = await self.start_periodic_summary(summary_interval)
        
        logger.info(f"✅ Connected to {len(self.active_connections)} exchanges")
        logger.info("Monitoring prices... Press Ctrl+C to exit")
        
        try:
            # Keep the application running
            while not self.is_shutting_down:
                await asyncio.sleep(1)
        finally:
            summary_task.cancel()
            await self.shutdown()
    
    async def shutdown(self):
        """Gracefully shutdown all connections."""
        if self.is_shutting_down:
            return
        
        self.is_shutting_down = True
        logger.info("Shutting down...")
        
        # Stop background tasks
        if self.stale_cleanup_task:
            await self.price_manager.stop_stale_data_cleanup()
        
        # Disconnect from all exchanges
        disconnect_tasks = []
        for exchange in self.exchanges.values():
            disconnect_tasks.append(exchange.disconnect())
        
        if disconnect_tasks:
            await asyncio.gather(*disconnect_tasks, return_exceptions=True)
        
        logger.info("✅ Shutdown complete")
    
    def get_api(self):
        """Get API interface for programmatic access."""
        return {
            'get_prices_by_symbol': self.price_manager.get_prices_by_symbol,
            'get_spread': self.price_manager.get_spread,
            'get_all_prices': self.price_manager.get_all_prices,
            'get_best_prices': self.price_manager.get_best_prices,
            'get_market_summary': self.price_manager.get_market_summary,
            'check_arbitrage_opportunities': self.price_manager.check_arbitrage_opportunities
        }

@click.command()
@click.option('-i', '--input', 'input_file', required=True, 
              help='Input file path (CSV or JSON)')
@click.option('-s', '--summary-interval', default=30, 
              help='Summary display interval in seconds (default: 30)')
@click.option('-v', '--verbose', is_flag=True, 
              help='Enable verbose logging')
def main(input_file: str, summary_interval: int, verbose: bool):
    """WebSocket-based Crypto Futures Price Fetcher."""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Resolve input file path
    input_path = Path(input_file).resolve()
    
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        sys.exit(1)
    
    # Create and run fetcher
    fetcher = CryptoFuturesPriceFetcher()
    
    try:
        asyncio.run(fetcher.run(str(input_path), summary_interval))
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=verbose)
        sys.exit(1)

if __name__ == '__main__':
    main()