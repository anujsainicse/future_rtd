#!/bin/bash

echo "🔍 Diagnosing Crypto Futures Price Fetcher Setup..."
echo "=================================================="

# Check current directory
echo "📍 Current directory: $(pwd)"
echo ""

# Check file permissions
echo "📁 File permissions:"
ls -la *.sh 2>/dev/null || echo "No .sh files found in current directory"
echo ""

# Check Python
echo "🐍 Python check:"
if command -v python >/dev/null 2>&1; then
    echo "✅ Python found: $(python --version)"
    echo "📍 Python location: $(which python)"
else
    echo "❌ Python not found"
fi
echo ""

# Check Python modules
echo "📦 Python modules check:"
python -c "
import sys
modules = ['fastapi', 'uvicorn', 'websockets', 'pydantic']
for module in modules:
    try:
        __import__(module)
        print(f'✅ {module} installed')
    except ImportError:
        print(f'❌ {module} NOT installed')
"
echo ""

# Check Node.js
echo "🟢 Node.js check:"
if command -v node >/dev/null 2>&1; then
    echo "✅ Node.js found: $(node --version)"
    echo "📍 Node.js location: $(which node)"
else
    echo "❌ Node.js not found"
fi

if command -v npm >/dev/null 2>&1; then
    echo "✅ npm found: $(npm --version)"
else
    echo "❌ npm not found"
fi
echo ""

# Check project structure
echo "📂 Project structure:"
echo "Backend files:"
[ -d "backend" ] && echo "✅ backend/ directory exists" || echo "❌ backend/ directory missing"
[ -f "backend/main.py" ] && echo "✅ backend/main.py exists" || echo "❌ backend/main.py missing"

echo "Frontend files:"
[ -d "frontend" ] && echo "✅ frontend/ directory exists" || echo "❌ frontend/ directory missing"
[ -f "frontend/package.json" ] && echo "✅ frontend/package.json exists" || echo "❌ frontend/package.json missing"

echo "Config files:"
[ -f "symbols.csv" ] && echo "✅ symbols.csv exists" || echo "⚠️  symbols.csv missing (will be created)"
[ -f "examples/minimal.csv" ] && echo "✅ examples/minimal.csv exists" || echo "❌ examples/minimal.csv missing"
echo ""

# Test backend import
echo "🧪 Testing backend import:"
cd backend 2>/dev/null && python -c "
try:
    import main
    print('✅ Backend imports successfully')
except Exception as e:
    print(f'❌ Backend import error: {e}')
" && cd .. || echo "❌ Could not test backend (directory not found)"
echo ""

# Check ports
echo "🔌 Port availability:"
if command -v lsof >/dev/null 2>&1; then
    if lsof -i :8000 >/dev/null 2>&1; then
        echo "⚠️  Port 8000 is already in use:"
        lsof -i :8000
    else
        echo "✅ Port 8000 is available"
    fi
    
    if lsof -i :3000 >/dev/null 2>&1; then
        echo "⚠️  Port 3000 is already in use:"
        lsof -i :3000
    else
        echo "✅ Port 3000 is available"
    fi
else
    echo "⚠️  Cannot check port availability (lsof not available)"
fi
echo ""

echo "🎯 Diagnosis complete!"
echo ""
echo "💡 Common fixes:"
echo "   - Install Python modules: python -m pip install --user fastapi uvicorn websockets pydantic"
echo "   - Install Node.js from: https://nodejs.org/"
echo "   - Make scripts executable: chmod +x *.sh"
echo "   - Kill existing processes: pkill -f 'python.*main.py' && pkill -f 'npm.*dev'"