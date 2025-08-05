#!/bin/bash

echo "🛠️  Setting up Crypto Futures Price Fetcher..."

# Install Python dependencies
echo "📥 Installing Python dependencies..."
python -m pip install --user -r requirements.txt
python -m pip install --user -r backend/requirements.txt

# Create default symbols file if it doesn't exist
if [ ! -f "symbols.csv" ]; then
    echo "📄 Creating default symbols.csv..."
    cp examples/minimal.csv symbols.csv
fi

echo "✅ Python backend setup complete!"
echo ""

# Check if Node.js is available for frontend
if command -v node &> /dev/null; then
    echo "📦 Setting up frontend dependencies..."
    cd frontend
    npm install
    cd ..
    echo "✅ Frontend setup complete!"
    echo ""
    echo "🚀 Setup complete! You can now run:"
    echo "   Backend:  ./start_backend.sh"
    echo "   Frontend: ./start_frontend.sh"
else
    echo "⚠️  Node.js not found. Frontend setup skipped."
    echo "   Install Node.js from https://nodejs.org/"
    echo ""
    echo "🚀 Backend setup complete! You can run:"
    echo "   Backend only: ./start_backend.sh"
fi