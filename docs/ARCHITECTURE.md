# System Architecture

Comprehensive architectural overview of the Cryptocurrency Perpetual Futures Arbitrage Tracking System.

## Overview

The system is built using a **three-tier architecture** with clear separation of concerns, enabling scalability, maintainability, and real-time performance for cryptocurrency arbitrage tracking across 11 major exchanges.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Web Browser  │  Mobile App  │  CLI Client  │  Third-party Apps  │  REST APIs  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                ┌───────▼───────┐
                                │  Load Balancer │ (Nginx/HAProxy)
                                │  SSL/TLS       │
                                └───────┬───────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                       PRESENTATION LAYER                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                    Frontend Application (React/Next.js)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │ Dashboard   │  │ Price       │  │ Arbitrage   │  │ Connection  │           │
│  │ Component   │  │ Monitor     │  │ Table       │  │ Status      │           │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘           │
│         │                 │                 │                 │               │
│         └─────────────────┼─────────────────┼─────────────────┘               │
│                           │                 │                                 │
│  ┌─────────────────────────┼─────────────────┼──────────────────────────────┐  │
│  │            WebSocket Client        │      HTTP Client                   │  │
│  └─────────────────────────┼─────────────────┼──────────────────────────────┘  │
└─────────────────────────────┼─────────────────┼─────────────────────────────────┘
                              │                 │
                              │           ┌─────▼─────┐
                              │           │    REST   │
                              │           │    API    │
                              │           └─────┬─────┘
                              │                 │
┌─────────────────────────────┼─────────────────┼─────────────────────────────────┐
│                        APPLICATION LAYER                                       │
├─────────────────────────────┼─────────────────┼─────────────────────────────────┤
│                    Backend API Server (FastAPI)                               │
│                             │                 │                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                    WebSocket Manager                                   │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │  │
│  │  │ Connection  │  │ Message     │  │ Broadcast   │  │ Client      │   │  │
│  │  │ Manager     │  │ Router      │  │ Handler     │  │ Registry    │   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │  │
│  └─────────────────────────┬───────────────────────────────────────────────┘  │
│                             │                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                      REST API Endpoints                                │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │  │
│  │  │ Price APIs  │  │ Arbitrage   │  │ Market      │  │ Config      │   │  │
│  │  │ /api/prices │  │ /api/arb    │  │ /api/summary│  │ /api/reload │   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │  │
│  └─────────────────────────┬───────────────────────────────────────────────┘  │
│                             │                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                   Business Logic Layer                                 │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │  │
│  │  │ Arbitrage   │  │ Price       │  │ Alert       │  │ Statistics  │   │  │
│  │  │ Calculator  │  │ Validator   │  │ Manager     │  │ Aggregator  │   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │  │
│  └─────────────────────────┬───────────────────────────────────────────────┘  │
└─────────────────────────────┼─────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼─────────────────────────────────────────────────┐
│                           DATA LAYER                                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                       Price Management Engine                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                         Price Manager                                   │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │  │
│  │  │ In-Memory   │  │ Event       │  │ Rate        │  │ Data        │   │  │
│  │  │ Store       │  │ System      │  │ Limiter     │  │ Validator   │   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │  │
│  └─────────────────────────┬───────────────────────────────────────────────┘  │
│                             │                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                    Exchange Orchestrator                               │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │  │
│  │  │ Connection  │  │ Symbol      │  │ Health      │  │ Failover    │   │  │
│  │  │ Pool        │  │ Mapper      │  │ Monitor     │  │ Manager     │   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │  │
│  └─────────────────────────┬───────────────────────────────────────────────┘  │
└─────────────────────────────┼─────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼─────────────────────────────────────────────────┐
│                      EXTERNAL INTEGRATION LAYER                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                          Exchange Adapters                                    │
│                                                                               │
│ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ │
│ │  Binance   │ │   Bybit    │ │    OKX     │ │  KuCoin    │ │  Deribit   │ │
│ │ WebSocket  │ │ WebSocket  │ │ WebSocket  │ │REST+WebSkt │ │JSON-RPC WS │ │
│ └────────────┘ └────────────┘ └────────────┘ └────────────┘ └────────────┘ │
│                                                                               │
│ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ │
│ │  BitMEX    │ │  Gate.io   │ │    MEXC    │ │  Bitget    │ │   Phemex   │ │
│ │ WebSocket  │ │ WebSocket  │ │ WebSocket  │ │ WebSocket  │ │ WebSocket  │ │
│ └────────────┘ └────────────┘ └────────────┘ └────────────┘ └────────────┘ │
│                                                                               │
│ ┌────────────┐                                                               │
│ │  CoinDCX   │                                                               │
│ │ Socket.io  │                                                               │
│ └────────────┘                                                               │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Presentation Layer

#### Frontend Application (React/Next.js)
- **Technology Stack**: React 18, Next.js 14, TypeScript, Tailwind CSS
- **Architecture Pattern**: Component-based architecture with hooks
- **State Management**: React hooks + Context API for global state
- **Real-time Updates**: WebSocket client with automatic reconnection

**Key Components:**
```typescript
// Component hierarchy
├── pages/
│   ├── _app.tsx              // Application wrapper
│   └── index.tsx             // Main dashboard page
├── components/
│   ├── Dashboard.tsx         // Main dashboard layout
│   ├── PriceTable.tsx        // Real-time price display
│   ├── ArbitrageTable.tsx    // Arbitrage opportunities
│   ├── MarketOverview.tsx    // Market statistics
│   └── ConnectionStatus.tsx  // Exchange health monitoring
└── lib/
    ├── api.ts               // REST API client
    └── websocket.ts         // WebSocket client
```

#### WebSocket Client Architecture
```typescript
class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  
  connect(): Promise<void>
  disconnect(): void
  subscribe(messageHandler: MessageHandler): void
  send(message: any): void
  handleReconnection(): void
}
```

### 2. Application Layer

#### Backend API Server (FastAPI)
- **Framework**: FastAPI with async/await support
- **WebSocket Support**: Native WebSocket handling with connection management
- **API Documentation**: Automatic OpenAPI/Swagger documentation
- **CORS**: Configurable cross-origin resource sharing

**Core Modules:**
```python
# Application structure
backend/
├── main.py                   # FastAPI application and endpoints
├── models/                   # Pydantic data models
├── routers/                  # API route handlers
├── middleware/               # Custom middleware
└── services/                 # Business logic services
```

#### Request/Response Flow
```
Client Request → CORS Middleware → Rate Limiter → Route Handler → Business Logic → Data Layer → Response
```

#### WebSocket Manager
```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket)
    def disconnect(self, websocket: WebSocket)
    async def send_personal_message(self, message: str, websocket: WebSocket)
    async def broadcast(self, message: str)
```

### 3. Data Layer

#### Price Management Engine
The core data processing engine built with event-driven architecture:

```python
class PriceManager:
    def __init__(self):
        self.prices: Dict[str, Dict[str, Dict]] = {}  # symbol -> exchange -> data
        self.last_updated: Dict[str, float] = {}      # tracking timestamps
        self.event_callbacks: Dict[str, List] = {}    # event system
        self.last_arbitrage_alert: Dict[str, float] = {}  # rate limiting
    
    # Core methods
    def update_price(self, price_data: Dict)
    def check_arbitrage_opportunities(self, symbol: str) -> List[Dict]
    def get_best_prices(self, symbol: str) -> Dict
    def emit(self, event: str, data: Any)
```

#### Event-Driven Architecture
```python
# Event flow
Price Update → Price Manager → Event Emission → Multiple Subscribers
                                    ├── WebSocket Broadcaster
                                    ├── Arbitrage Calculator  
                                    ├── Statistics Aggregator
                                    └── Alert Manager
```

#### In-Memory Data Store
- **Storage**: Python dictionaries with optimized access patterns
- **Indexing**: Multi-dimensional indexing (symbol, exchange, timestamp)
- **Cleanup**: Automatic stale data removal with configurable TTL
- **Memory Management**: Garbage collection optimization for high-frequency updates

### 4. External Integration Layer

#### Exchange Adapter Pattern
All exchanges implement a common interface for unified handling:

```python
class BaseExchange(ABC):
    def __init__(self, name: str, ws_url: str)
    
    @abstractmethod
    async def connect(self) -> bool
    
    @abstractmethod
    async def subscribe(self, symbol: str) -> None
    
    @abstractmethod
    def parse_message(self, message: str) -> Dict
    
    @abstractmethod
    def normalize_symbol(self, symbol: str) -> str
```

#### Connection Management
```python
# Exchange connection lifecycle
Initialize → Authenticate (if needed) → Subscribe to Symbols → Listen for Messages
     ↓              ↓                        ↓                      ↓
Error Handler → Reconnect Logic →    Health Check    →    Message Parser
     ↓              ↓                        ↓                      ↓
   Logging    → Exponential Backoff → Connection Pool → Event Emission
```

## Data Flow Architecture

### 1. Real-time Price Updates

```
Exchange WebSocket → Message Parser → Symbol Normalizer → Price Manager → Event System
                                                               ↓
Frontend Client ← WebSocket Broadcast ← Connection Manager ← Event Handler
```

### 2. Arbitrage Detection Flow

```
Price Update → Arbitrage Calculator → Opportunity Detection → Rate Limiter → Alert System
                      ↓                        ↓                   ↓            ↓
             Compare All Exchanges → Calculate Spreads → Check Cooldown → Notify Clients
```

### 3. REST API Request Flow

```
HTTP Request → FastAPI Router → Validation → Business Logic → Data Access → Response
                    ↓               ↓             ↓              ↓           ↓
               Route Handler → Pydantic Models → Service Layer → Price Manager → JSON Response
```

## Scalability Architecture

### Horizontal Scaling

```
Load Balancer (Nginx)
        ↓
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Frontend      │    │   Frontend      │
│   Instance 1    │    │   Instance 2    │    │   Instance 3    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        ↓                       ↓                       ↓
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Backend       │    │   Backend       │    │   Backend       │
│   Instance 1    │    │   Instance 2    │    │   Instance 3    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        ↓                       ↓                       ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Shared Data Layer                            │
│              (Redis/Database + Message Queue)                   │
└─────────────────────────────────────────────────────────────────┘
```

### Microservices Architecture (Future)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Price         │    │   Arbitrage     │    │   Alert         │
│   Service       │    │   Service       │    │   Service       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        ↓                       ↓                       ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Message Bus (Redis/RabbitMQ)                 │
└─────────────────────────────────────────────────────────────────┘
```

## Security Architecture

### Authentication & Authorization
```
Client Request → JWT Validation → Role Check → Rate Limiting → API Access
                      ↓               ↓             ↓             ↓
              Token Verification → Permission Check → Quota Check → Endpoint
```

### Data Security
- **Input Validation**: Pydantic models for request validation
- **Output Sanitization**: Structured JSON responses
- **Rate Limiting**: Per-IP and per-endpoint rate limiting
- **CORS**: Configurable cross-origin policies

### Network Security
```
Internet → SSL/TLS Termination → WAF → Load Balancer → Application Servers
              ↓                  ↓         ↓              ↓
        Certificate Mgmt → DDoS Protection → Health Checks → Service Mesh
```

## Monitoring Architecture

### Observability Stack
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Metrics      │    │      Logs       │    │     Traces      │
│  (Prometheus)   │    │  (ELK Stack)    │    │    (Jaeger)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        ↓                       ↓                       ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Visualization Layer                          │
│                  (Grafana + Kibana)                            │
└─────────────────────────────────────────────────────────────────┘
```

### Health Monitoring
```python
# Health check hierarchy
System Health
├── Application Health
│   ├── API Endpoint Health
│   ├── WebSocket Health
│   └── Service Health
├── Data Layer Health
│   ├── Price Manager Health
│   ├── Memory Usage
│   └── Event System Health
└── External Services Health
    ├── Exchange Connections
    ├── Network Connectivity
    └── Response Times
```

## Performance Architecture

### Caching Strategy
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Browser       │    │   CDN           │    │   Application   │
│   Cache         │    │   Cache         │    │   Cache         │
│   (Static)      │    │   (Static)      │    │   (Redis)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        ↓                       ↓                       ↓
┌─────────────────────────────────────────────────────────────────┐
│                    In-Memory Cache                              │
│                  (Price Manager)                               │
└─────────────────────────────────────────────────────────────────┘
```

### Async Processing
```python
# Async architecture
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   WebSocket     │    │   HTTP          │    │   Background    │
│   Event Loop    │    │   Event Loop    │    │   Tasks         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        ↓                       ↓                       ↓
┌─────────────────────────────────────────────────────────────────┐
│              Python AsyncIO Event Loop                         │
└─────────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

### Container Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                    Docker Compose                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │  Frontend   │  │   Backend   │  │    Nginx    │  │  Redis  │ │
│  │ Container   │  │ Container   │  │ Container   │  │Container│ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Cloud Architecture (AWS Example)
```
┌─────────────────────────────────────────────────────────────────┐
│                        AWS Cloud                               │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │   Route53   │  │     ALB     │  │     ECS     │  │   RDS   │ │
│  │    (DNS)    │  │(Load Bal.)  │  │ (Compute)   │  │  (DB)   │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │ CloudFront  │  │     S3      │  │ ElastiCache │  │ Lambda  │ │
│  │   (CDN)     │  │ (Storage)   │  │  (Cache)    │  │(Functions)│ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack Summary

### Backend Technologies
- **Language**: Python 3.8+
- **Framework**: FastAPI
- **WebSocket**: Native Python WebSockets
- **Async**: AsyncIO event loop
- **Validation**: Pydantic models
- **Documentation**: OpenAPI/Swagger

### Frontend Technologies  
- **Language**: TypeScript
- **Framework**: React 18 + Next.js 14
- **Styling**: Tailwind CSS
- **State**: React Hooks + Context
- **Build**: Next.js compiler
- **Deployment**: Static/SSG export

### Infrastructure Technologies
- **Containerization**: Docker + Docker Compose
- **Reverse Proxy**: Nginx
- **Caching**: Redis
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack
- **CI/CD**: GitHub Actions

This architecture provides a solid foundation for a high-performance, scalable cryptocurrency arbitrage tracking system with real-time capabilities and professional-grade reliability.