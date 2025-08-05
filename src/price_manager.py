import asyncio
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)

class PriceManager:
    def __init__(self):
        self.prices: Dict[str, Dict[str, Dict]] = {}
        self.last_updated: Dict[str, float] = {}  # symbol-exchange -> timestamp
        self.event_callbacks = {}
        self.stale_cleanup_task = None
    
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
    
    def update_price(self, price_data: Dict):
        """Update price for a symbol/exchange pair."""
        symbol = price_data['symbol']
        exchange = price_data['exchange']
        
        logger.debug(f"Price manager received update from {exchange} for {symbol}")
        
        if symbol not in self.prices:
            self.prices[symbol] = {}
        
        self.prices[symbol][exchange] = {
            'price': float(price_data['price']),
            'bid': float(price_data['bid']) if price_data['bid'] is not None else None,
            'ask': float(price_data['ask']) if price_data['ask'] is not None else None,
            'timestamp': price_data['timestamp']
        }
        
        self.last_updated[f"{symbol}-{exchange}"] = time.time()
        
        # Emit price update event
        self.emit('price_update', {
            'symbol': symbol,
            'exchange': exchange,
            'data': self.prices[symbol][exchange]
        })
        
        # Check for arbitrage opportunities
        opportunities = self.check_arbitrage_opportunities(symbol)
        if opportunities:
            self.emit('arbitrage_opportunity', opportunities)
    
    def get_prices_by_symbol(self, symbol: str) -> Optional[Dict[str, Dict]]:
        """Get all exchange prices for a symbol."""
        symbol = symbol.upper()
        return self.prices.get(symbol, {}).copy() if symbol in self.prices else None
    
    def get_spread(self, symbol: str, exchange1: str, exchange2: str) -> Optional[Dict]:
        """Calculate spread between two exchanges for a symbol."""
        prices = self.get_prices_by_symbol(symbol)
        if not prices or exchange1 not in prices or exchange2 not in prices:
            return None
        
        price1 = prices[exchange1]['price']
        price2 = prices[exchange2]['price']
        
        spread = abs(price1 - price2)
        min_price = min(price1, price2)
        spread_percentage = (spread / min_price) * 100 if min_price > 0 else 0
        
        return {
            'symbol': symbol,
            'exchanges': [exchange1, exchange2],
            'spread': spread,
            'spread_percentage': spread_percentage,
            'higher': exchange1 if price1 > price2 else exchange2,
            'lower': exchange1 if price1 < price2 else exchange2,
            'higher_price': max(price1, price2),
            'lower_price': min_price,
            'timestamp': max(prices[exchange1]['timestamp'], prices[exchange2]['timestamp'])
        }
    
    def get_all_prices(self) -> Dict[str, Dict[str, Dict]]:
        """Get all prices for all symbols."""
        return {symbol: exchanges.copy() for symbol, exchanges in self.prices.items()}
    
    def get_symbols(self) -> List[str]:
        """Get list of all symbols."""
        return list(self.prices.keys())
    
    def get_exchanges(self) -> List[str]:
        """Get list of all active exchanges."""
        exchanges = set()
        for symbol_data in self.prices.values():
            exchanges.update(symbol_data.keys())
        return list(exchanges)
    
    def get_best_prices(self, symbol: str) -> Optional[Dict]:
        """Get best bid/ask prices across all exchanges for a symbol."""
        prices = self.get_prices_by_symbol(symbol)
        if not prices:
            return None
        
        best_bid = None
        best_ask = None
        best_bid_exchange = None
        best_ask_exchange = None
        
        for exchange, data in prices.items():
            if data['bid'] is not None:
                if best_bid is None or data['bid'] > best_bid['price']:
                    best_bid = {
                        'price': data['bid'],
                        'exchange': exchange,
                        'timestamp': data['timestamp']
                    }
                    best_bid_exchange = exchange
            
            if data['ask'] is not None:
                if best_ask is None or data['ask'] < best_ask['price']:
                    best_ask = {
                        'price': data['ask'],
                        'exchange': exchange,
                        'timestamp': data['timestamp']
                    }
                    best_ask_exchange = exchange
        
        spread = None
        spread_percentage = None
        
        if best_bid and best_ask:
            spread = best_ask['price'] - best_bid['price']
            spread_percentage = (spread / best_bid['price']) * 100 if best_bid['price'] > 0 else 0
        
        return {
            'symbol': symbol,
            'best_bid': best_bid,
            'best_ask': best_ask,
            'spread': spread,
            'spread_percentage': spread_percentage
        }
    
    def check_arbitrage_opportunities(self, symbol: str, min_spread_percentage: float = 0.1) -> List[Dict]:
        """Check for arbitrage opportunities for a symbol."""
        prices = self.get_prices_by_symbol(symbol)
        if not prices or len(prices) < 2:
            return []
        
        exchanges = list(prices.keys())
        opportunities = []
        
        for i in range(len(exchanges)):
            for j in range(i + 1, len(exchanges)):
                spread = self.get_spread(symbol, exchanges[i], exchanges[j])
                if spread and spread['spread_percentage'] >= min_spread_percentage:
                    opportunities.append({
                        **spread,
                        'profitable': True,
                        'buy_exchange': spread['lower'],
                        'sell_exchange': spread['higher'],
                        'potential_profit': spread['spread_percentage']
                    })
        
        return sorted(opportunities, key=lambda x: x['potential_profit'], reverse=True)
    
    def get_market_summary(self) -> Dict:
        """Get market summary statistics."""
        symbols = self.get_symbols()
        exchanges = self.get_exchanges()
        
        price_count = sum(len(exchange_data) for exchange_data in self.prices.values())
        
        return {
            'total_symbols': len(symbols),
            'total_exchanges': len(exchanges),
            'symbols': symbols,
            'exchanges': exchanges,
            'last_update': time.time(),
            'price_count': price_count
        }
    
    def is_stale(self, symbol: str, exchange: str, max_age_seconds: float = 60.0) -> bool:
        """Check if price data is stale."""
        key = f"{symbol}-{exchange}"
        last_update = self.last_updated.get(key)
        
        if last_update is None:
            return True
        
        return (time.time() - last_update) > max_age_seconds
    
    def remove_stale_data(self, max_age_seconds: float = 300.0) -> int:
        """Remove stale price data."""
        now = time.time()
        stale_keys = []
        
        for key, timestamp in self.last_updated.items():
            if (now - timestamp) > max_age_seconds:
                stale_keys.append(key)
        
        removed_count = 0
        for key in stale_keys:
            symbol, exchange = key.split('-', 1)
            
            if symbol in self.prices and exchange in self.prices[symbol]:
                del self.prices[symbol][exchange]
                removed_count += 1
                
                # Remove symbol if no exchanges left
                if not self.prices[symbol]:
                    del self.prices[symbol]
            
            del self.last_updated[key]
        
        if removed_count > 0:
            logger.info(f"Removed {removed_count} stale price entries")
        
        return removed_count
    
    async def start_stale_data_cleanup(self, interval_seconds: float = 60.0, max_age_seconds: float = 300.0):
        """Start periodic stale data cleanup."""
        async def cleanup_loop():
            while True:
                try:
                    self.remove_stale_data(max_age_seconds)
                    await asyncio.sleep(interval_seconds)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in stale data cleanup: {e}")
                    await asyncio.sleep(interval_seconds)
        
        self.stale_cleanup_task = asyncio.create_task(cleanup_loop())
        return self.stale_cleanup_task
    
    async def stop_stale_data_cleanup(self):
        """Stop periodic stale data cleanup."""
        if self.stale_cleanup_task:
            self.stale_cleanup_task.cancel()
            try:
                await self.stale_cleanup_task
            except asyncio.CancelledError:
                pass
            self.stale_cleanup_task = None