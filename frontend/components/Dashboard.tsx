import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Wifi, 
  WifiOff, 
  RefreshCw,
  AlertTriangle,
  DollarSign,
  BarChart3,
  Clock
} from 'lucide-react';
import toast from 'react-hot-toast';

import { websocketService } from '@/lib/websocket';
import { apiService } from '@/lib/api';
import { 
  AllPrices, 
  ArbitrageOpportunity, 
  MarketSummary, 
  ConnectionStatus,
  PriceUpdateMessage 
} from '@/types';

import PriceTable from './PriceTable';
import ArbitrageTable from './ArbitrageTable';
import ConnectionStatusComponent from './ConnectionStatus';
import MarketOverview from './MarketOverview';

const Dashboard: React.FC = () => {
  const [prices, setPrices] = useState<AllPrices>({});
  const [arbitrageOpportunities, setArbitrageOpportunities] = useState<ArbitrageOpportunity[]>([]);
  const [marketSummary, setMarketSummary] = useState<MarketSummary | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({
    connected: false,
    connecting: false,
    error: null,
    lastConnected: null
  });
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'prices' | 'arbitrage' | 'charts'>('prices');
  const [lastUpdateTime, setLastUpdateTime] = useState<Date>(new Date());

  useEffect(() => {
    initializeData();
    setupWebSocket();

    return () => {
      websocketService.disconnect();
    };
  }, []);

  const initializeData = async () => {
    try {
      setLoading(true);
      
      // Load initial data
      const [pricesData, arbitrageData, summaryData] = await Promise.all([
        apiService.getAllPrices(),
        apiService.getArbitrageOpportunities(),
        apiService.getMarketSummary()
      ]);

      setPrices(pricesData.prices);
      setArbitrageOpportunities(arbitrageData.opportunities);
      setMarketSummary(summaryData);
      setLastUpdateTime(new Date());
      
      toast.success('Data loaded successfully');
    } catch (error) {
      console.error('Error loading initial data:', error);
      toast.error('Failed to load initial data');
    } finally {
      setLoading(false);
    }
  };

  const setupWebSocket = () => {
    // Connection status listener
    websocketService.on('connection-status', (status: ConnectionStatus) => {
      setConnectionStatus(status);
      
      if (status.connected) {
        toast.success('Connected to real-time data feed');
      } else if (status.error) {
        toast.error(`Connection error: ${status.error}`);
      }
    });

    // Price update listener
    websocketService.on('price_update', (data: PriceUpdateMessage['data']) => {
      setPrices(prevPrices => {
        const newPrices = { ...prevPrices };
        
        if (!newPrices[data.symbol]) {
          newPrices[data.symbol] = {};
        }
        
        newPrices[data.symbol][data.exchange] = {
          price: data.price,
          bid: data.bid,
          ask: data.ask,
          timestamp: data.timestamp
        };
        
        return newPrices;
      });
      
      setLastUpdateTime(new Date());
    });

    // Arbitrage opportunities listener
    websocketService.on('arbitrage_opportunities', (opportunities: ArbitrageOpportunity[]) => {
      setArbitrageOpportunities(opportunities);
      
      if (opportunities.length > 0) {
        const bestOpportunity = opportunities[0];
        if (bestOpportunity.potential_profit > 1.0) { // Only show significant opportunities
          toast.success(
            `Arbitrage Alert: ${bestOpportunity.symbol} - ${bestOpportunity.potential_profit.toFixed(2)}% profit`,
            { duration: 5000 }
          );
        }
      }
    });

    // Market summary listener
    websocketService.on('market_summary', (summary: MarketSummary) => {
      setMarketSummary(summary);
    });

    // Initial prices listener
    websocketService.on('initial_prices', (initialPrices: AllPrices) => {
      setPrices(initialPrices);
      setLastUpdateTime(new Date());
    });

    // Connect to WebSocket
    websocketService.connect();
  };

  const refreshData = async () => {
    toast.promise(
      initializeData(),
      {
        loading: 'Refreshing data...',
        success: 'Data refreshed successfully',
        error: 'Failed to refresh data'
      }
    );
  };

  const getSymbolCount = () => Object.keys(prices).length;
  const getExchangeCount = () => {
    const exchanges = new Set<string>();
    Object.values(prices).forEach(symbolPrices => {
      Object.keys(symbolPrices).forEach(exchange => exchanges.add(exchange));
    });
    return exchanges.size;
  };

  const getTotalArbitrageOpportunities = () => arbitrageOpportunities.length;
  const getBestArbitrageProfit = () => {
    if (arbitrageOpportunities.length === 0) return 0;
    return Math.max(...arbitrageOpportunities.map(opp => opp.potential_profit));
  };

  const tabs = [
    { id: 'prices' as const, label: 'Price Monitor', icon: DollarSign },
    { id: 'arbitrage' as const, label: 'Arbitrage', icon: TrendingUp },
    { id: 'charts' as const, label: 'Charts', icon: BarChart3 },
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin text-primary-500 mx-auto mb-4" />
          <p className="text-gray-400">Loading market data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <header className="bg-gray-900 border-b border-gray-800 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Activity className="w-8 h-8 text-primary-500" />
              <h1 className="text-2xl font-bold text-gradient">
                Crypto Futures Monitor
              </h1>
            </div>
            <ConnectionStatusComponent status={connectionStatus} />
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-400">
              <Clock className="w-4 h-4 inline mr-1" />
              Last update: {lastUpdateTime.toLocaleTimeString()}
            </div>
            <button
              onClick={refreshData}
              className="btn-secondary flex items-center space-x-2"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Refresh</span>
            </button>
          </div>
        </div>
      </header>

      {/* Market Overview */}
      <div className="px-6 py-6">
        <MarketOverview
          symbolCount={getSymbolCount()}
          exchangeCount={getExchangeCount()}
          arbitrageOpportunities={getTotalArbitrageOpportunities()}
          bestProfit={getBestArbitrageProfit()}
          marketSummary={marketSummary}
        />
      </div>

      {/* Navigation Tabs */}
      <div className="px-6">
        <div className="flex space-x-1 bg-gray-800 rounded-lg p-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-md font-medium transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'bg-primary-600 text-white shadow-glow'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Content */}
      <div className="px-6 py-6">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {activeTab === 'prices' && (
            <PriceTable 
              prices={prices} 
              onSymbolClick={(symbol) => console.log('Symbol clicked:', symbol)} 
            />
          )}
          
          {activeTab === 'arbitrage' && (
            <ArbitrageTable 
              opportunities={arbitrageOpportunities}
              onOpportunityClick={(opportunity) => console.log('Opportunity clicked:', opportunity)}
            />
          )}
          
          {activeTab === 'charts' && (
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold">Price Charts</h3>
              </div>
              <div className="card-body">
                <div className="flex items-center justify-center h-64 text-gray-400">
                  <div className="text-center">
                    <BarChart3 className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>Chart visualization coming soon...</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default Dashboard;