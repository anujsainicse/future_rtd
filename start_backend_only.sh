#!/bin/bash

echo "🔧 Starting Backend Only..."

# Kill any existing processes
pkill -f "python.*main.py" 2>/dev/null

# Create symbols file if needed
if [ ! -f "symbols.csv" ]; then
    cp examples/minimal.csv symbols.csv
    echo "📄 Created symbols.csv"
fi

# Start backend
echo "🌐 Starting backend on http://localhost:8000..."
cd backend

# Start with direct uvicorn command to avoid startup issues
python -c "
import uvicorn
import main

if __name__ == '__main__':
    uvicorn.run(main.app, host='0.0.0.0', port=8000, log_level='info')
"