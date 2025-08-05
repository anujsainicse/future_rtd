# 🚀 Manual Startup Instructions

The WebSocket version issue has been fixed. Here's how to start the services manually:

## Step 1: Start Backend

```bash
# Terminal 1
cd backend
python -c "import uvicorn; import main; uvicorn.run(main.app, host='0.0.0.0', port=8000)"
```

## Step 2: Start Frontend (New Terminal)

```bash  
# Terminal 2
cd frontend
npm run dev
```

## Step 3: Access Application

- **Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Quick Test

Test if backend is working:
```bash
curl http://localhost:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "timestamp": "...",
  "price_fetcher_active": true,
  "websocket_connections": 0
}
```

## Alternative: Use Fixed Script

```bash
./run.sh
```

This should now work with the WebSocket fix.