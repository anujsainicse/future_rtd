import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { 
  ArrowUpDown, 
  ArrowUp, 
  ArrowDown, 
  TrendingUp,
  DollarSign,
  Clock,
  ExternalLink,
  AlertTriangle
} from 'lucide-react';
import { format } from 'date-fns';
import { ArbitrageOpportunity } from '@/types';

interface ArbitrageTableProps {
  opportunities: ArbitrageOpportunity[];
  onOpportunityClick?: (opportunity: ArbitrageOpportunity) => void;
}

const ArbitrageTable: React.FC<ArbitrageTableProps> = ({ 
  opportunities, 
  onOpportunityClick 
}) => {
  const [sortBy, setSortBy] = useState<'profit' | 'spread' | 'symbol' | 'timestamp'>('profit');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [minProfitFilter, setMinProfitFilter] = useState<number>(0.1);

  const filteredOpportunities = useMemo(() => {
    return opportunities
      .filter(opp => opp.potential_profit >= minProfitFilter)
      .sort((a, b) => {
        let aValue: any, bValue: any;

        switch (sortBy) {
          case 'profit':
            aValue = a.potential_profit;
            bValue = b.potential_profit;
            break;
          case 'spread':
            aValue = a.spread;
            bValue = b.spread;
            break;
          case 'symbol':
            aValue = a.symbol;
            bValue = b.symbol;
            break;
          case 'timestamp':
            aValue = a.timestamp;
            bValue = b.timestamp;
            break;
          default:
            aValue = a.potential_profit;
            bValue = b.potential_profit;
        }

        if (sortOrder === 'asc') {
          return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
        } else {
          return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
        }
      });
  }, [opportunities, sortBy, sortOrder, minProfitFilter]);

  const handleSort = (column: 'profit' | 'spread' | 'symbol' | 'timestamp') => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder(column === 'profit' ? 'desc' : 'asc');
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
      default:
        return 'exchange-badge bg-gray-700 text-gray-300';
    }
  };

  const getProfitColorClass = (profit: number) => {
    if (profit >= 2.0) return 'text-green-400';
    if (profit >= 1.0) return 'text-green-500';
    if (profit >= 0.5) return 'text-yellow-400';
    return 'text-gray-300';
  };

  const getRiskLevel = (profit: number) => {
    if (profit >= 2.0) return { level: 'High', color: 'text-green-400' };
    if (profit >= 1.0) return { level: 'Medium', color: 'text-yellow-400' };
    return { level: 'Low', color: 'text-gray-400' };
  };

  const formatPrice = (price: number) => {
    if (price >= 1000) {
      return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
    return price.toFixed(4);
  };

  const formatTimestamp = (timestamp: number) => {
    if (!timestamp || isNaN(timestamp)) {
      return '--:--:--';
    }
    
    const date = new Date(timestamp);
    if (isNaN(date.getTime())) {
      return '--:--:--';
    }
    
    return format(date, 'HH:mm:ss');
  };

  const SortIcon = ({ column }: { column: 'profit' | 'spread' | 'symbol' | 'timestamp' }) => {
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
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-5 h-5 text-green-400" />
            <h3 className="text-lg font-semibold">Arbitrage Opportunities</h3>
            <span className="text-sm text-gray-400">
              ({filteredOpportunities.length} opportunities)
            </span>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <label className="text-sm text-gray-400">Min Profit:</label>
              <select
                value={minProfitFilter}
                onChange={(e) => setMinProfitFilter(Number(e.target.value))}
                className="select w-24"
              >
                <option value={0}>0%</option>
                <option value={0.1}>0.1%</option>
                <option value={0.5}>0.5%</option>
                <option value={1.0}>1.0%</option>
                <option value={2.0}>2.0%</option>
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
              <th>Buy Exchange</th>
              <th>Sell Exchange</th>
              <th className="text-right">Buy Price</th>
              <th className="text-right">Sell Price</th>
              <th 
                className="cursor-pointer hover:bg-gray-700 transition-colors text-right"
                onClick={() => handleSort('spread')}
              >
                <div className="flex items-center justify-end space-x-2">
                  <span>Spread</span>
                  <SortIcon column="spread" />
                </div>
              </th>
              <th 
                className="cursor-pointer hover:bg-gray-700 transition-colors text-right"
                onClick={() => handleSort('profit')}
              >
                <div className="flex items-center justify-end space-x-2">
                  <span>Profit %</span>
                  <SortIcon column="profit" />
                </div>
              </th>
              <th className="text-center">Risk</th>
              <th 
                className="cursor-pointer hover:bg-gray-700 transition-colors text-center"
                onClick={() => handleSort('timestamp')}
              >
                <div className="flex items-center justify-center space-x-2">
                  <Clock className="w-4 h-4" />
                  <SortIcon column="timestamp" />
                </div>
              </th>
              <th className="text-center">Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredOpportunities.map((opportunity, index) => {
              const riskLevel = getRiskLevel(opportunity.potential_profit);
              
              return (
                <motion.tr
                  key={`${opportunity.symbol}-${opportunity.buy_exchange}-${opportunity.sell_exchange}-${index}`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="hover:bg-gray-800/50 transition-colors"
                >
                  <td>
                    <div className="flex items-center space-x-2">
                      <span className="font-semibold text-white">{opportunity.symbol}</span>
                      {opportunity.potential_profit >= 2.0 && (
                        <AlertTriangle className="w-4 h-4 text-yellow-400" title="High profit opportunity" />
                      )}
                    </div>
                  </td>

                  <td>
                    <span className={getExchangeBadgeClass(opportunity.buy_exchange)}>
                      {opportunity.buy_exchange.toUpperCase()}
                    </span>
                  </td>

                  <td>
                    <span className={getExchangeBadgeClass(opportunity.sell_exchange)}>
                      {opportunity.sell_exchange.toUpperCase()}
                    </span>
                  </td>

                  <td className="text-right font-mono">
                    <span className="text-green-400">
                      ${formatPrice(opportunity.buy_price || opportunity.lower_price)}
                    </span>
                  </td>

                  <td className="text-right font-mono">
                    <span className="text-red-400">
                      ${formatPrice(opportunity.sell_price || opportunity.higher_price)}
                    </span>
                  </td>

                  <td className="text-right font-mono">
                    <div className="space-y-1">
                      <div className="text-gray-300">
                        ${opportunity.spread.toFixed(4)}
                      </div>
                      <div className="text-xs text-gray-500">
                        {opportunity.spread_percentage.toFixed(3)}%
                      </div>
                    </div>
                  </td>

                  <td className="text-right">
                    <div className={`font-bold text-lg ${getProfitColorClass(opportunity.potential_profit)}`}>
                      {opportunity.potential_profit.toFixed(2)}%
                    </div>
                  </td>

                  <td className="text-center">
                    <span className={`text-xs font-medium ${riskLevel.color}`}>
                      {riskLevel.level}
                    </span>
                  </td>

                  <td className="text-center text-xs text-gray-400">
                    {formatTimestamp(opportunity.timestamp)}
                  </td>

                  <td className="text-center">
                    <button
                      onClick={() => onOpportunityClick?.(opportunity)}
                      className="btn-primary btn text-xs py-1 px-2"
                    >
                      <ExternalLink className="w-3 h-3" />
                    </button>
                  </td>
                </motion.tr>
              );
            })}
          </tbody>
        </table>

        {filteredOpportunities.length === 0 && (
          <div className="text-center py-12 text-gray-400">
            <TrendingUp className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No arbitrage opportunities found</p>
            <p className="text-sm mt-2">
              Try lowering the minimum profit filter or wait for market conditions to change
            </p>
          </div>
        )}
      </div>

      {/* Summary Footer */}
      {filteredOpportunities.length > 0 && (
        <div className="px-6 py-4 bg-gray-800/50 border-t border-gray-800">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center space-x-6">
              <div className="text-gray-400">
                Total Opportunities: <span className="text-white font-semibold">{filteredOpportunities.length}</span>
              </div>
              <div className="text-gray-400">
                Best Profit: <span className={`font-semibold ${getProfitColorClass(filteredOpportunities[0]?.potential_profit || 0)}`}>
                  {filteredOpportunities[0]?.potential_profit.toFixed(2)}%
                </span>
              </div>
              <div className="text-gray-400">
                Avg Profit: <span className="text-white font-semibold">
                  {(filteredOpportunities.reduce((sum, opp) => sum + opp.potential_profit, 0) / filteredOpportunities.length).toFixed(2)}%
                </span>
              </div>
            </div>
            <div className="text-xs text-gray-500">
              Updated continuously via WebSocket
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ArbitrageTable;