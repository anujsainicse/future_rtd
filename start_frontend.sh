#!/bin/bash

echo "🎨 Starting Crypto Futures Price Fetcher Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    echo "   Download from: https://nodejs.org/"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

# Navigate to frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
else
    echo "🔧 Dependencies already installed"
fi

# Start the Next.js development server
echo "🌐 Starting Next.js frontend on http://localhost:3000"
echo "🔗 Make sure the backend is running on http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the frontend"
echo ""

npm run dev