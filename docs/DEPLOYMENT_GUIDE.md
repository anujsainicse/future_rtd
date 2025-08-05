# Deployment Guide

Comprehensive guide for deploying the Cryptocurrency Perpetual Futures Arbitrage Tracking System in various environments.

## Overview

This guide covers deployment options from development to production, including Docker containerization, cloud deployment, and monitoring setup.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Production Configuration](#production-configuration)
5. [Monitoring & Logging](#monitoring--logging)
6. [Security Considerations](#security-considerations)
7. [Performance Tuning](#performance-tuning)
8. [Troubleshooting](#troubleshooting)

## Local Development

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Git** for version control
- **4GB+ RAM** recommended
- **Stable internet connection** for WebSocket connections

### Quick Setup

```bash
# Clone repository
git clone https://github.com/anujsainicse/future_rtd.git
cd future-spot

# Install dependencies and start
./run.sh
```

### Manual Setup

```bash
# Backend setup
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Frontend setup
cd frontend
npm install
cd ..

# Start backend
./start_backend.sh

# Start frontend (new terminal)
./start_frontend.sh
```

### Development Configuration

**Environment Variables:**
```bash
# .env file
DEBUG=true
LOG_LEVEL=debug
CORS_ORIGINS=http://localhost:3000
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_PORT=3000
```

## Docker Deployment

### Docker Compose (Recommended)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
      - LOG_LEVEL=info
      - CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
    volumes:
      - ./futures_symbols.txt:/app/futures_symbols.txt
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
    depends_on:
      - backend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
```

### Backend Dockerfile

Create `Dockerfile.backend`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

Create `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Expose port
EXPOSE 3000

# Start application
CMD ["npm", "start"]
```

### Docker Commands

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Scale backend instances
docker-compose up -d --scale backend=3

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

## Cloud Deployment

### AWS Deployment

#### EC2 Instance Setup

```bash
# Launch EC2 instance (t3.medium recommended)
# Security Group: Allow ports 22, 80, 443, 3000, 8000

# Connect to instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Install Docker
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Deploy application
git clone https://github.com/anujsainicse/future_rtd.git
cd future-spot
docker-compose up -d
```

#### ECS Deployment

Create `task-definition.json`:

```json
{
  "family": "crypto-arbitrage-system",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "your-account.dkr.ecr.region.amazonaws.com/crypto-arbitrage-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DEBUG",
          "value": "false"
        },
        {
          "name": "LOG_LEVEL",
          "value": "info"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/crypto-arbitrage",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "backend"
        }
      }
    }
  ]
}
```

### Google Cloud Platform

#### Cloud Run Deployment

```bash
# Build and push to Container Registry
docker build -t gcr.io/your-project/crypto-arbitrage-backend -f Dockerfile.backend .
docker push gcr.io/your-project/crypto-arbitrage-backend

# Deploy to Cloud Run
gcloud run deploy crypto-arbitrage-backend \
  --image gcr.io/your-project/crypto-arbitrage-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10
```

### DigitalOcean

#### App Platform Deployment

Create `.do/app.yaml`:

```yaml
name: crypto-arbitrage-system
services:
- name: backend
  source_dir: /
  dockerfile_path: Dockerfile.backend
  instance_count: 1
  instance_size_slug: basic-xxs
  http_port: 8000
  routes:
  - path: /api
  - path: /ws
  - path: /docs
  - path: /health
  env:
  - key: DEBUG
    value: "false"
  - key: LOG_LEVEL
    value: "info"

- name: frontend
  source_dir: /frontend
  dockerfile_path: Dockerfile
  instance_count: 1
  instance_size_slug: basic-xxs
  http_port: 3000
  routes:
  - path: /
  env:
  - key: NEXT_PUBLIC_API_URL
    value: "${backend.PUBLIC_URL}"
```

## Production Configuration

### Environment Variables

```bash
# Production .env
DEBUG=false
LOG_LEVEL=info
CORS_ORIGINS=https://yourdomain.com
API_HOST=0.0.0.0
API_PORT=8000

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (if implemented)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Redis (for caching)
REDIS_URL=redis://localhost:6379/0

# External APIs (if needed)
EXCHANGE_API_KEYS={"binance": "key1", "bybit": "key2"}
```

### Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=ws:10m rate=5r/s;

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # Backend API
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # WebSocket
        location /ws {
            limit_req zone=ws burst=10 nodelay;
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
        }

        # Health check
        location /health {
            proxy_pass http://backend;
            access_log off;
        }
    }
}
```

### SSL Certificate Setup

```bash
# Using Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring & Logging

### Application Logging

```python
# logging_config.py
import logging
import logging.handlers

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.handlers.RotatingFileHandler(
                'logs/app.log',
                maxBytes=10485760,  # 10MB
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )
```

### Prometheus Metrics

Add to `backend/main.py`:

```python
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)

# Custom metrics
from prometheus_client import Counter, Histogram, Gauge

exchange_connections = Gauge('exchange_connections_total', 'Number of exchange connections', ['exchange'])
price_updates = Counter('price_updates_total', 'Total price updates', ['exchange', 'symbol'])
arbitrage_opportunities = Counter('arbitrage_opportunities_total', 'Total arbitrage opportunities', ['symbol'])
websocket_connections = Gauge('websocket_connections_current', 'Current WebSocket connections')
```

### Health Checks

```python
@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "checks": {
            "database": check_database(),
            "exchanges": check_exchanges(),
            "memory": check_memory_usage(),
            "disk": check_disk_space()
        }
    }
    
    # Return 503 if any critical check fails
    if any(not check["healthy"] for check in health_status["checks"].values()):
        raise HTTPException(status_code=503, detail="Service unhealthy")
    
    return health_status
```

### Log Aggregation

#### ELK Stack Setup

```yaml
# docker-compose.yml addition
  elasticsearch:
    image: elasticsearch:7.15.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  logstash:
    image: logstash:7.15.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    depends_on:
      - elasticsearch

  kibana:
    image: kibana:7.15.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

## Security Considerations

### API Security

```python
# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/prices")
@limiter.limit("10/minute")
async def get_prices(request: Request):
    pass
```

### CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domains in production
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Input Validation

```python
from pydantic import BaseModel, validator

class ConfigReloadRequest(BaseModel):
    force: bool = False
    
    @validator('force')
    def validate_force(cls, v):
        return isinstance(v, bool)
```

## Performance Tuning

### Backend Optimization

```python
# Async optimization
import asyncio
import aiohttp

# Connection pooling
connector = aiohttp.TCPConnector(
    limit=100,
    limit_per_host=10,
    ttl_dns_cache=300,
    use_dns_cache=True
)

# Memory optimization
import gc
gc.set_threshold(700, 10, 10)  # Tune garbage collection
```

### Database Configuration

```sql
-- PostgreSQL optimization (if using database)
-- postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
```

### Frontend Optimization

```javascript
// next.config.js
const nextConfig = {
  experimental: {
    optimizeCss: true,
  },
  compress: true,
  poweredByHeader: false,
  generateEtags: false,
  httpAgentOptions: {
    keepAlive: true,
  },
}
```

## Troubleshooting

### Common Issues

#### High Memory Usage

```bash
# Monitor memory
docker stats

# Check for memory leaks
ps aux --sort=-%mem | head

# Restart containers
docker-compose restart backend
```

#### WebSocket Connection Issues

```bash
# Check WebSocket connectivity
wscat -c ws://localhost:8000/ws

# Test from outside
wscat -c wss://yourdomain.com/ws

# Check firewall
sudo ufw status
```

#### Exchange Connection Failures

```bash
# Check network connectivity
curl -I https://fstream.binance.com

# Test DNS resolution
nslookup fstream.binance.com

# Check logs
docker-compose logs backend | grep -i error
```

### Performance Monitoring

```bash
# System resources
htop
iotop
nethogs

# Application metrics
curl http://localhost:8000/metrics

# Container stats
docker stats --no-stream
```

### Backup and Recovery

```bash
# Backup configuration
tar -czf backup-$(date +%Y%m%d).tar.gz futures_symbols.txt logs/ docker-compose.yml

# Database backup (if applicable)
pg_dump dbname > backup.sql

# Restore configuration
tar -xzf backup-20240101.tar.gz
docker-compose up -d
```

## Scaling Considerations

### Horizontal Scaling

```yaml
# docker-compose.yml
  backend:
    deploy:
      replicas: 3
    # Load balancer needed
```

### Vertical Scaling

```yaml
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

This deployment guide provides comprehensive instructions for deploying the system in various environments, from local development to production cloud deployments.