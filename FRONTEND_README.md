# Crypto Futures Price Fetcher - Frontend

A modern, real-time dashboard for cryptocurrency futures price monitoring and arbitrage detection, inspired by CoinGlass's interface design.

## 🌟 Features

### Real-Time Data
- **Live Price Feeds**: WebSocket connections for instant price updates
- **Multi-Exchange Support**: Binance, Bybit, and OKX integration
- **Arbitrage Detection**: Real-time opportunity identification and alerts
- **Connection Monitoring**: Visual connection status with automatic reconnection

### User Interface
- **Responsive Design**: Optimized for desktop and mobile devices
- **Dark Theme**: Professional trading interface with modern styling
- **Interactive Tables**: Sortable columns with filtering capabilities
- **Real-Time Animations**: Price change indicators and flash effects
- **Toast Notifications**: Non-intrusive alerts for important events

### Data Visualization
- **Price Tables**: Comprehensive price comparison across exchanges
- **Arbitrage Tables**: Profit opportunity analysis with risk indicators
- **Market Overview**: Summary statistics and exchange status
- **Connection Status**: Real-time WebSocket connection monitoring

## 🚀 Quick Start

### Prerequisites
- Node.js 16.0 or higher
- npm or yarn package manager
- Backend API running on localhost:8000

### Installation

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Open browser:**
   Visit [http://localhost:3000](http://localhost:3000)

### Quick Start with Scripts

Use the provided startup script:
```bash
# Make executable (first time only)
chmod +x start_frontend.sh

# Start frontend
./start_frontend.sh
```

## 🏗️ Architecture

### Technology Stack
- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS with custom design system
- **State Management**: React hooks and context
- **Real-Time**: WebSocket with auto-reconnection
- **HTTP Client**: Axios for REST API calls
- **Animations**: Framer Motion
- **Notifications**: React Hot Toast
- **Icons**: Lucide React

### Project Structure
```
frontend/
├── components/          # React components
│   ├── Dashboard.tsx   # Main dashboard container
│   ├── PriceTable.tsx  # Price monitoring table
│   ├── ArbitrageTable.tsx # Arbitrage opportunities
│   ├── ConnectionStatus.tsx # WebSocket status
│   └── MarketOverview.tsx # Market statistics
├── lib/                # Utility libraries
│   ├── api.ts         # REST API client
│   └── websocket.ts   # WebSocket service
├── pages/             # Next.js pages
│   ├── _app.tsx       # App wrapper
│   └── index.tsx      # Home page
├── styles/            # CSS styles
│   └── globals.css    # Global styles and utilities
└── types/             # TypeScript definitions
    └── index.ts       # Type definitions
```

## 🎨 Design System

### Color Palette
- **Primary**: Blue (`#3b82f6`) - Interactive elements
- **Success**: Green (`#22c55e`) - Positive changes, profits
- **Danger**: Red (`#ef4444`) - Negative changes, risks
- **Warning**: Yellow (`#eab308`) - Alerts, moderate risks
- **Gray Scale**: Dark theme with multiple gray shades

### Exchange Branding
- **Binance**: Yellow accent (`#f59e0b`)
- **Bybit**: Orange accent (`#ea580c`)
- **OKX**: Blue accent (`#2563eb`)

### Typography
- **Headers**: Inter font family
- **Monospace**: For prices and numbers
- **Body**: Standard system fonts

## 📡 API Integration

### REST Endpoints
```typescript
// Get all prices
GET /api/prices

// Get symbol prices
GET /api/prices/{symbol}

// Get arbitrage opportunities
GET /api/arbitrage

// Get market summary
GET /api/summary

// Health check
GET /health
```

### WebSocket Events
```typescript
// Connection events
'connection-status' // Connection state changes

// Data events
'price_update'      // Real-time price updates
'arbitrage_opportunities' // New arbitrage alerts
'market_summary'    // Market statistics
'initial_prices'    // Initial data load
```

## 🔧 Configuration

### Environment Variables
Create a `.env.local` file:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

### API Configuration
The API base URL can be configured in `lib/api.ts`:
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

## 📊 Features Deep Dive

### Price Monitoring
- **Real-time Updates**: Sub-second price refreshes via WebSocket
- **Multi-Exchange View**: Side-by-side price comparison
- **Bid/Ask Spreads**: Detailed order book information
- **Historical Context**: Price change indicators
- **Search & Filter**: Find specific symbols or exchanges

### Arbitrage Detection
- **Profit Calculation**: Automatic spread analysis
- **Risk Assessment**: Low/Medium/High risk categorization
- **Sorting Options**: By profit, spread, or symbol
- **Alert System**: Toast notifications for high-profit opportunities
- **Filter Controls**: Minimum profit thresholds

### Connection Management
- **Auto-Reconnection**: Automatic WebSocket reconnection
- **Connection Status**: Visual indicators with last connected time
- **Error Handling**: Graceful error recovery and user feedback
- **Connection Health**: Monitoring connection quality

## 🎯 Performance Optimizations

### Frontend Optimizations
- **Code Splitting**: Automatic route-based code splitting
- **Image Optimization**: Next.js image optimization
- **Bundle Analysis**: Webpack bundle analyzer integration
- **Memoization**: React.memo for expensive components
- **Virtual Scrolling**: For large data tables (when needed)

### Real-Time Optimizations
- **Debounced Updates**: Prevent excessive re-renders
- **Selective Updates**: Only update changed data
- **Connection Pooling**: Efficient WebSocket management
- **Memory Management**: Cleanup intervals for stale data

## 🔍 Debugging

### Development Tools
```bash
# Enable verbose logging
localStorage.setItem('debug', 'websocket,api')

# View connection status
console.log(websocketService.getConnectionStatus())

# Monitor API calls
// Check Network tab in DevTools
```

### Common Issues

1. **WebSocket Connection Failed**
   - Ensure backend is running on port 8000
   - Check CORS settings
   - Verify WebSocket URL configuration

2. **API Calls Failing**
   - Confirm backend API is accessible
   - Check network connectivity
   - Verify API endpoint URLs

3. **Real-time Updates Not Working**
   - Check WebSocket connection status
   - Verify event listeners are properly attached
   - Confirm backend is emitting events

## 🚀 Deployment

### Production Build
```bash
# Build for production
npm run build

# Start production server
npm start
```

### Docker Deployment
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### Environment Setup
- Set `NODE_ENV=production`
- Configure API URLs for production backend
- Set up SSL certificates for HTTPS
- Configure CDN for static assets

## 📈 Monitoring

### Performance Metrics
- **First Contentful Paint (FCP)**
- **Largest Contentful Paint (LCP)**
- **Cumulative Layout Shift (CLS)**
- **WebSocket Connection Stability**
- **API Response Times**

### Error Tracking
- Implement error boundary components
- Monitor WebSocket connection errors
- Track API failure rates
- Log client-side errors

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make changes with proper TypeScript types
4. Test with both mock and real data
5. Submit pull request with description

### Code Standards
- Use TypeScript for all new code
- Follow ESLint configuration
- Use Prettier for code formatting
- Write meaningful commit messages
- Add JSDoc comments for complex functions

## 📄 License

MIT License - see LICENSE file for details