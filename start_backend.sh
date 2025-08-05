#!/bin/bash

echo "🚀 Starting Crypto Futures Price Fetcher Backend..."

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Install/update dependencies (using system Python since conda is already active)
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt 2>/dev/null || echo "⚠️  Some dependencies might already be installed"
pip install -r backend/requirements.txt 2>/dev/null || echo "⚠️  Some backend dependencies might already be installed"

# Check if symbols.csv exists
if [ ! -f "symbols.csv" ]; then
    echo "⚠️  symbols.csv not found. Using examples/minimal.csv"
    cp examples/minimal.csv symbols.csv
fi

# Start the FastAPI backend (which integrates the price fetcher)
echo "🌐 Starting FastAPI backend on http://localhost:8000"
echo "📊 API Documentation: http://localhost:8000/docs"
echo "🔌 WebSocket endpoint: ws://localhost:8000/ws"
echo ""
echo "This will start both the price fetcher AND the web API backend"
echo "Press Ctrl+C to stop the backend"
echo ""

cd backend
python main.py