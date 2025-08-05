#!/bin/bash

echo "🚀 Quick Start - Crypto Futures Dashboard"
echo "========================================"

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "uvicorn" 2>/dev/null
pkill -f "next dev" 2>/dev/null
sleep 2

# Create symbols file if needed
if [ ! -f "symbols.csv" ]; then
    cp examples/minimal.csv symbols.csv
    echo "📄 Created symbols.csv"
fi

# Start backend in background
echo "🌐 Starting backend on http://localhost:8000..."
cd backend
nohup python -c "import uvicorn; import main; uvicorn.run(main.app, host='0.0.0.0', port=8000, log_level='info')" > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 5

# Test backend health
echo "🔍 Testing backend connection..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running successfully!"
else
    echo "❌ Backend failed to start. Check backend.log"
    exit 1
fi

# Start frontend in background
echo "🎨 Starting frontend on http://localhost:3000..."
cd frontend
nohup npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
echo "⏳ Waiting for frontend to initialize..."
sleep 8

# Test frontend
echo "🔍 Testing frontend connection..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is running successfully!"
else
    echo "⚠️ Frontend may still be starting. Check frontend.log"
fi

echo ""
echo "🎉 Services Started Successfully!"
echo "📊 Dashboard: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "💡 Logs:"
echo "   Backend: tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "🛑 To stop: pkill -f 'uvicorn'; pkill -f 'next dev'"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"