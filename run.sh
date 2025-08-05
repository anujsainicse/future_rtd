#!/bin/bash

# Simple startup script for Crypto Futures Price Fetcher
echo "🚀 Starting Crypto Futures Price Fetcher..."

# Install dependencies if needed
echo "📦 Installing dependencies..."
python -m pip install --user fastapi uvicorn websockets pydantic python-multipart 2>/dev/null

# Create symbols file if it doesn't exist
if [ ! -f "symbols.csv" ]; then
    cp examples/minimal.csv symbols.csv
    echo "📄 Created symbols.csv from examples/minimal.csv"
fi

# Function to cleanup on exit
cleanup() {
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}
trap cleanup INT TERM

# Start backend
echo "🔧 Starting backend..."
cd backend && python main.py &
BACKEND_PID=$!
cd ..

# Start frontend (if Node.js is available)
if command -v npm >/dev/null 2>&1; then
    echo "🎨 Starting frontend..."
    cd frontend
    [ ! -d "node_modules" ] && npm install
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    echo "✅ Services started!"
    echo "📊 Dashboard: http://localhost:3000"
    echo "🔌 API: http://localhost:8000"
    echo ""
    echo "Press Ctrl+C to stop"
    
    # Wait for processes
    wait $BACKEND_PID $FRONTEND_PID
else
    echo "⚠️  Node.js not found. Starting backend only."
    echo "🔌 API: http://localhost:8000"
    echo "Press Ctrl+C to stop"
    wait $BACKEND_PID
fi