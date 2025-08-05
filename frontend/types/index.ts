export interface PriceData {
  price: number;
  bid: number | null;
  ask: number | null;
  timestamp: number;
}

export interface SymbolPrices {
  [exchange: string]: PriceData;
}

export interface AllPrices {
  [symbol: string]: SymbolPrices;
}

export interface ArbitrageOpportunity {
  symbol: string;
  buy_exchange: string;
  sell_exchange: string;
  buy_price: number;
  sell_price: number;
  spread: number;
  spread_percentage: number;
  potential_profit: number;
  profitable: boolean;
  higher: string;
  lower: string;
  higher_price: number;
  lower_price: number;
  timestamp: number;
}

export interface MarketSummary {
  total_symbols: number;
  total_exchanges: number;
  symbols: string[];
  exchanges: string[];
  price_count: number;
  last_update: number;
}

export interface WebSocketMessage {
  type: 'price_update' | 'arbitrage_opportunities' | 'market_summary' | 'initial_prices';
  data: any;
}

export interface PriceUpdateMessage {
  type: 'price_update';
  data: {
    symbol: string;
    exchange: string;
    price: number;
    bid: number | null;
    ask: number | null;
    timestamp: number;
  };
}

export interface ConnectionStatus {
  connected: boolean;
  connecting: boolean;
  error: string | null;
  lastConnected: Date | null;
}

export interface ExchangeInfo {
  name: string;
  displayName: string;
  color: string;
  status: 'online' | 'offline' | 'error';
}

export interface FilterOptions {
  exchange?: string;
  symbol?: string;
  minSpread?: number;
  sortBy?: 'symbol' | 'spread' | 'profit' | 'timestamp';
  sortOrder?: 'asc' | 'desc';
}

export interface TableColumn {
  key: string;
  label: string;
  sortable?: boolean;
  render?: (value: any, row: any) => React.ReactNode;
}