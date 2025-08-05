import React from 'react';
import { motion } from 'framer-motion';
import { 
  DollarSign, 
  Building, 
  TrendingUp, 
  Target,
  Activity,
  Clock,
  BarChart3,
  Zap
} from 'lucide-react';
import { MarketSummary } from '@/types';

interface MarketOverviewProps {
  symbolCount: number;
  exchangeCount: number;
  arbitrageOpportunities: number;
  bestProfit: number;
  marketSummary: MarketSummary | null;
}

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ElementType;
  color: string;
  trend?: 'up' | 'down' | 'neutral';
  delay?: number;
}

const StatCard: React.FC<StatCardProps> = ({ 
  title, 
  value, 
  subtitle, 
  icon: Icon, 
  color, 
  trend,
  delay = 0 
}) => {
  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-3 h-3 text-green-400" />;
      case 'down':
        return <TrendingUp className="w-3 h-3 text-red-400 rotate-180" />;
      default:
        return null;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className="card hover:shadow-glow transition-all duration-300"
    >
      <div className="card-body">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-sm text-gray-400 mb-1">{title}</p>
            <div className="flex items-end space-x-2">
              <p className="text-2xl font-bold text-white">{value}</p>
              {getTrendIcon()}
            </div>
            {subtitle && (
              <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
            )}
          </div>
          <div className={`p-2 rounded-lg ${color}`}>
            <Icon className="w-5 h-5" />
          </div>
        </div>
      </div>
    </motion.div>
  );
};

const MarketOverview: React.FC<MarketOverviewProps> = ({
  symbolCount,
  exchangeCount,
  arbitrageOpportunities,
  bestProfit,
  marketSummary
}) => {
  const formatProfit = (profit: number) => {
    return profit > 0 ? `${profit.toFixed(2)}%` : '-';
  };

  const getProfitColor = (profit: number) => {
    if (profit >= 2.0) return 'bg-green-900/20 text-green-400';
    if (profit >= 1.0) return 'bg-yellow-900/20 text-yellow-400';
    return 'bg-gray-800/20 text-gray-400';
  };

  const getArbitrageColor = (count: number) => {
    if (count >= 5) return 'bg-green-900/20 text-green-400';
    if (count >= 1) return 'bg-yellow-900/20 text-yellow-400';
    return 'bg-gray-800/20 text-gray-400';
  };

  const getLastUpdateTime = () => {
    if (!marketSummary) return '';
    return new Date(marketSummary.last_update * 1000).toLocaleTimeString();
  };

  const stats = [
    {
      title: 'Active Symbols',
      value: symbolCount,
      subtitle: 'Tracked symbols',
      icon: DollarSign,
      color: 'bg-blue-900/20 text-blue-400',
      delay: 0
    },
    {
      title: 'Connected Exchanges',
      value: exchangeCount,
      subtitle: 'Real-time feeds',
      icon: Building,
      color: 'bg-purple-900/20 text-purple-400',
      delay: 0.1
    },
    {
      title: 'Arbitrage Opportunities',
      value: arbitrageOpportunities,
      subtitle: 'Active opportunities',
      icon: Target,
      color: getArbitrageColor(arbitrageOpportunities),
      trend: arbitrageOpportunities > 0 ? 'up' : 'neutral',
      delay: 0.2
    },
    {
      title: 'Best Profit',
      value: formatProfit(bestProfit),
      subtitle: 'Highest spread',
      icon: TrendingUp,
      color: getProfitColor(bestProfit),
      trend: bestProfit > 1 ? 'up' : 'neutral',  
      delay: 0.3
    }
  ];

  return (
    <div className="space-y-6">
      {/* Main Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <StatCard
            key={stat.title}
            title={stat.title}
            value={stat.value}
            subtitle={stat.subtitle}
            icon={stat.icon}
            color={stat.color}
            trend={stat.trend}
            delay={stat.delay}
          />
        ))}
      </div>

      {/* Detailed Market Info */}
      {marketSummary && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card"
        >
          <div className="card-header">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Activity className="w-5 h-5 text-primary-400" />
                <h3 className="text-lg font-semibold">Market Activity</h3>
              </div>
              <div className="flex items-center space-x-2 text-sm text-gray-400">
                <Clock className="w-4 h-4" />
                <span>Last update: {getLastUpdateTime()}</span>
              </div>
            </div>
          </div>
          
          <div className="card-body">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-3">
                <h4 className="text-sm font-medium text-gray-400 uppercase tracking-wider">
                  Price Feeds
                </h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-300">Total Price Points:</span>
                    <span className="font-semibold text-white">{marketSummary.price_count}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-300">Active Symbols:</span>
                    <span className="font-semibold text-white">{marketSummary.total_symbols}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-300">Connected Exchanges:</span>
                    <span className="font-semibold text-white">{marketSummary.total_exchanges}</span>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <h4 className="text-sm font-medium text-gray-400 uppercase tracking-wider">
                  Tracked Symbols
                </h4>
                <div className="flex flex-wrap gap-1">
                  {marketSummary.symbols.slice(0, 8).map(symbol => (
                    <span 
                      key={symbol}
                      className="px-2 py-1 bg-gray-800 text-gray-300 text-xs rounded"
                    >
                      {symbol}
                    </span>
                  ))}
                  {marketSummary.symbols.length > 8 && (
                    <span className="px-2 py-1 bg-gray-700 text-gray-400 text-xs rounded">
                      +{marketSummary.symbols.length - 8} more
                    </span>
                  )}
                </div>
              </div>

              <div className="space-y-3">
                <h4 className="text-sm font-medium text-gray-400 uppercase tracking-wider">
                  Exchanges
                </h4>
                <div className="space-y-2">
                  {marketSummary.exchanges.map(exchange => (
                    <div key={exchange} className="flex items-center justify-between">
                      <span className={`px-2 py-1 rounded text-xs font-medium uppercase ${
                        exchange === 'binance' ? 'bg-yellow-900/20 text-yellow-300' :
                        exchange === 'bybit' ? 'bg-orange-900/20 text-orange-300' :
                        exchange === 'okx' ? 'bg-blue-900/20 text-blue-300' :
                        'bg-gray-800/20 text-gray-300'
                      }`}>
                        {exchange}
                      </span>
                      <div className="flex items-center space-x-1">
                        <Zap className="w-3 h-3 text-green-400" />
                        <span className="text-xs text-green-400">Live</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default MarketOverview;