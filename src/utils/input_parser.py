import json
import csv
import os
from pathlib import Path
from typing import Dict, List, Tuple, Set
import logging

logger = logging.getLogger(__name__)

class InputParser:
    @staticmethod
    async def parse_file(file_path: str) -> Dict:
        """Parse input file (CSV or JSON) and return exchange/symbol configuration."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Input file not found: {file_path}")
        
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.csv':
            return await InputParser._parse_csv(file_path)
        elif file_extension == '.json':
            return await InputParser._parse_json(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}. Supported formats: .csv, .json")
    
    @staticmethod
    async def _parse_csv(file_path: str) -> Dict:
        """Parse CSV file format."""
        results = []
        exchange_symbols: Dict[str, Set[str]] = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row_num, row in enumerate(reader, start=2):
                    exchange = row.get('exchange', '').strip().lower()
                    symbol = row.get('symbol', '').strip().upper()
                    
                    if not exchange or not symbol:
                        logger.warning(f"Skipping invalid row {row_num}: {row}")
                        continue
                    
                    if exchange not in exchange_symbols:
                        exchange_symbols[exchange] = set()
                    
                    exchange_symbols[exchange].add(symbol)
                    results.append({'exchange': exchange, 'symbol': symbol})
            
            # Convert sets to lists for JSON serialization
            grouped_data = {exchange: list(symbols) for exchange, symbols in exchange_symbols.items()}
            
            return {'exchanges': grouped_data, 'pairs': results}
            
        except Exception as e:
            raise ValueError(f"Failed to parse CSV file: {str(e)}")
    
    @staticmethod
    async def _parse_json(file_path: str) -> Dict:
        """Parse JSON file format."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            if not isinstance(data, list):
                raise ValueError('JSON file must contain an array of exchange/symbol pairs')
            
            results = []
            exchange_symbols: Dict[str, Set[str]] = {}
            
            for item in data:
                exchange = item.get('exchange', '').strip().lower()
                symbol = item.get('symbol', '').strip().upper()
                
                if not exchange or not symbol:
                    logger.warning(f"Skipping invalid entry: {item}")
                    continue
                
                if exchange not in exchange_symbols:
                    exchange_symbols[exchange] = set()
                
                exchange_symbols[exchange].add(symbol)
                results.append({'exchange': exchange, 'symbol': symbol})
            
            # Convert sets to lists
            grouped_data = {exchange: list(symbols) for exchange, symbols in exchange_symbols.items()}
            
            return {'exchanges': grouped_data, 'pairs': results}
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to parse JSON file: {str(e)}")
    
    @staticmethod
    def validate_exchange_support(exchanges: Dict[str, List[str]], supported_exchanges: List[str]) -> Dict[str, List[str]]:
        """Filter exchanges to only include supported ones."""
        unsupported = [ex for ex in exchanges.keys() if ex not in supported_exchanges]
        
        if unsupported:
            logger.warning(f"Unsupported exchanges will be ignored: {', '.join(unsupported)}")
            logger.warning(f"Supported exchanges: {', '.join(supported_exchanges)}")
        
        filtered = {ex: symbols for ex, symbols in exchanges.items() if ex in supported_exchanges}
        return filtered