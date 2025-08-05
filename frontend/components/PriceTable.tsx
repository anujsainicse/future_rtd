import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { 
  ArrowUpDown, 
  ArrowUp, 
  ArrowDown, 
  Search, 
  Filter,
  ExternalLink,
  TrendingUp,
  TrendingDown
} from 'lucide-react';
import { format } from 'date-fns';
import { AllPrices, SymbolPrices } from '@/types';

interface PriceTableProps {
  prices: AllPrices;
  onSymbolClick?: (symbol: string) => void;
}

interface PriceTableRow {
  symbol: string;
  exchanges: {
    [exchange: string]: {
      price: number;
      bid: number | null;
      ask: number | null;
      timestamp: number;
      change?: number;
    };
  };
  bestBid: number | null;
  bestAsk: number | null;
  spread: number | null;
  spreadPercentage: number | null;
}

const PriceTable: React.FC<PriceTableProps> = ({ prices, onSymbolClick }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'symbol' | 'price' | 'spread'>('symbol');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [selectedExchange, setSelectedExchange] = useState<string>('all');

  const exchanges = useMemo(() => {
    const exchangeSet = new Set<string>();
    Object.values(prices).forEach(symbolPrices => {
      Object.keys(symbolPrices).forEach(exchange => exchangeSet.add(exchange));
    });
    return Array.from(exchangeSet).sort();
  }, [prices]);

  const tableData = useMemo(() => {
    const rows: PriceTableRow[] = [];

    Object.entries(prices).forEach(([symbol, symbolPrices]) => {
      if (searchTerm && !symbol.toLowerCase().includes(searchTerm.toLowerCase())) {
        return;
      }

      const exchangeData: { [exchange: string]: any } = {};
      let bestBid: number | null = null;
      let bestAsk: number | null = null;

      Object.entries(symbolPrices).forEach(([exchange, priceData]) => {
        if (selectedExchange !== 'all' && exchange !== selectedExchange) {
          return;
        }

        exchangeData[exchange] = {
          ...priceData,
          change: 0 // TODO: Calculate price change from previous value
        };

        if (priceData.bid && (bestBid === null || priceData.bid > bestBid)) {
          bestBid = priceData.bid;
        }
        if (priceData.ask && (bestAsk === null || priceData.ask < bestAsk)) {
          bestAsk = priceData.ask;
        }
      });

      if (Object.keys(exchangeData).length === 0) return;

      const spread = bestBid && bestAsk ? bestAsk - bestBid : null;
      const spreadPercentage = spread && bestBid ? (spread / bestBid) * 100 : null;

      rows.push({
        symbol,
        exchanges: exchangeData,
        bestBid,
        bestAsk,
        spread,
        spreadPercentage
      });
    });

    // Sort data
    rows.sort((a, b) => {
      let aValue: any, bValue: any;

      switch (sortBy) {
        case 'symbol':
          aValue = a.symbol;
          bValue = b.symbol;
          break;
        case 'price':
          // Sort by average price across exchanges
          const aAvgPrice = Object.values(a.exchanges).reduce((sum, data) => sum + data.price, 0) / Object.keys(a.exchanges).length;
          const bAvgPrice = Object.values(b.exchanges).reduce((sum, data) => sum + data.price, 0) / Object.keys(b.exchanges).length;
          aValue = aAvgPrice;
          bValue = bAvgPrice;
          break;
        case 'spread':
          aValue = a.spreadPercentage || 0;
          bValue = b.spreadPercentage || 0;
          break;
        default:
          aValue = a.symbol;
          bValue = b.symbol;
      }

      if (sortOrder === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });

    return rows;
  }, [prices, searchTerm, sortBy, sortOrder, selectedExchange]);

  const handleSort = (column: 'symbol' | 'price' | 'spread') => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('asc');
    }
  };

  const getExchangeBadgeClass = (exchange: string) => {
    switch (exchange.toLowerCase()) {
      case 'binance':
        return 'exchange-binance';
      case 'bybit':
        return 'exchange-bybit';
      case 'okx':
        return 'exchange-okx';
      case 'kucoin':
        return 'exchange-kucoin';
      case 'deribit':
        return 'exchange-deribit';
      case 'bitget':
        return 'exchange-bitget';
      case 'gateio':
        return 'exchange-gateio';
      case 'mexc':
        return 'exchange-mexc';
      case 'bitmex':
        return 'exchange-bitmex';
      case 'phemex':
        return 'exchange-phemex';
      case 'coindcx':
        return 'exchange-coindcx';
      default:
        return 'exchange-badge bg-gray-700 text-gray-300';
    }
  };

  const formatPrice = (price: number) => {
    if (price >= 1000) {
      return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
    return price.toFixed(4);
  };

  const formatTimestamp = (timestamp: number) => {
    return format(new Date(timestamp), 'HH:mm:ss');
  };

  const SortIcon = ({ column }: { column: 'symbol' | 'price' | 'spread' }) => {
    if (sortBy !== column) {
      return <ArrowUpDown className="w-4 h-4 text-gray-500" />;
    }
    return sortOrder === 'asc' ? 
      <ArrowUp className="w-4 h-4 text-primary-400" /> : 
      <ArrowDown className="w-4 h-4 text-primary-400" />;
  };

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Real-Time Prices</h3>
          <div className="flex items-center space-x-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search symbols..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input pl-10 w-48"
              />
            </div>

            {/* Exchange Filter */}
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <select
                value={selectedExchange}
                onChange={(e) => setSelectedExchange(e.target.value)}
                className="select pl-10 w-40"
              >
                <option value="all">All Exchanges</option>
                {exchanges.map(exchange => (
                  <option key={exchange} value={exchange}>
                    {exchange.charAt(0).toUpperCase() + exchange.slice(1)}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="table">
          <thead>
            <tr>
              <th 
                className="cursor-pointer hover:bg-gray-700 transition-colors"
                onClick={() => handleSort('symbol')}
              >
                <div className="flex items-center space-x-2">
                  <span>Symbol</span>
                  <SortIcon column="symbol" />
                </div>
              </th>
              {exchanges.map(exchange => (
                <th key={exchange} className="text-center">
                  <div className={`${getExchangeBadgeClass(exchange)} inline-flex`}>
                    {exchange.toUpperCase()}
                  </div>
                </th>
              ))}
              <th 
                className="cursor-pointer hover:bg-gray-700 transition-colors text-center"
                onClick={() => handleSort('spread')}
              >
                <div className="flex items-center justify-center space-x-2">
                  <span>Spread</span>
                  <SortIcon column="spread" />
                </div>
              </th>
              <th className="text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            {tableData.map((row) => (
              <motion.tr
                key={row.symbol}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="hover:bg-gray-800/50 transition-colors"
              >
                <td>
                  <div className="flex items-center space-x-2">
                    <span className="font-semibold text-white">{row.symbol}</span>
                  </div>
                </td>
                
                {exchanges.map(exchange => {
                  const exchangeData = row.exchanges[exchange];
                  if (!exchangeData) {
                    return <td key={exchange} className="text-center text-gray-500">-</td>;
                  }

                  return (
                    <td key={exchange} className="text-center">
                      <div className="space-y-1">
                        <div className="font-mono text-sm font-semibold">
                          ${formatPrice(exchangeData.price)}
                        </div>
                        {exchangeData.bid && exchangeData.ask && (
                          <div className="text-xs text-gray-400">
                            {formatPrice(exchangeData.bid)} / {formatPrice(exchangeData.ask)}
                          </div>
                        )}
                        <div className="text-xs text-gray-500">
                          {formatTimestamp(exchangeData.timestamp)}
                        </div>
                      </div>
                    </td>
                  );
                })}

                <td className="text-center">
                  {row.spreadPercentage !== null ? (
                    <div className="space-y-1">
                      <div className={`font-semibold ${
                        row.spreadPercentage > 0.5 ? 'text-red-400' : 
                        row.spreadPercentage > 0.1 ? 'text-yellow-400' : 'text-green-400'
                      }`}>
                        {row.spreadPercentage.toFixed(3)}%
                      </div>
                      {row.spread && (
                        <div className="text-xs text-gray-400">
                          ${row.spread.toFixed(4)}
                        </div>
                      )}
                    </div>
                  ) : (
                    <span className="text-gray-500">-</span>
                  )}
                </td>

                <td className="text-center">
                  <button
                    onClick={() => onSymbolClick?.(row.symbol)}
                    className="btn-secondary btn text-xs py-1 px-2"
                  >
                    <ExternalLink className="w-3 h-3" />
                  </button>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>

        {tableData.length === 0 && (
          <div className="text-center py-12 text-gray-400">
            <Search className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No symbols found matching your criteria</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default PriceTable;