import axios from 'axios';
import { AllPrices, ArbitrageOpportunity, MarketSummary } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const apiService = {
  // Health check
  async getHealth() {
    const response = await api.get('/health');
    return response.data;
  },

  // Get all prices
  async getAllPrices(): Promise<{ prices: AllPrices; timestamp: string }> {
    const response = await api.get('/api/prices');
    return response.data;
  },

  // Get prices for a specific symbol
  async getSymbolPrices(symbol: string) {
    const response = await api.get(`/api/prices/${symbol}`);
    return response.data;
  },

  // Get spread between two exchanges
  async getSpread(symbol: string, exchange1: string, exchange2: string) {
    const response = await api.get(`/api/spread/${symbol}/${exchange1}/${exchange2}`);
    return response.data;
  },

  // Get all arbitrage opportunities
  async getArbitrageOpportunities(): Promise<{ opportunities: ArbitrageOpportunity[]; timestamp: string }> {
    const response = await api.get('/api/arbitrage');
    return response.data;
  },

  // Get arbitrage opportunities for a specific symbol
  async getSymbolArbitrage(symbol: string, minSpread: number = 0.1) {
    const response = await api.get(`/api/arbitrage/${symbol}?min_spread=${minSpread}`);
    return response.data;
  },

  // Get market summary
  async getMarketSummary(): Promise<MarketSummary> {
    const response = await api.get('/api/summary');
    return response.data;
  },

  // Get best prices for a symbol
  async getBestPrices(symbol: string) {
    const response = await api.get(`/api/best-prices/${symbol}`);
    return response.data;
  },
};

export default apiService;