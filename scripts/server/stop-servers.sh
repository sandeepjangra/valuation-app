#!/bin/bash

# ValuationApp - Stop Development Servers Script
# This script stops both the Angular frontend and Python backend development servers

echo "🛑 Stopping ValuationApp Development Servers..."
echo "=================================================="

# Stop Angular development server
echo "🔸 Stopping Angular frontend server..."
pkill -f "ng serve" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Angular server stopped"
else
    echo "ℹ️  Angular server was not running"
fi

# Stop Python backend server - try all variations
echo "🔸 Stopping Python backend server..."
STOPPED=0

# Try uvicorn first (most common)
if pkill -f "uvicorn.*main:app" 2>/dev/null; then
    echo "✅ Uvicorn backend server stopped"
    STOPPED=1
fi

# Try python main.py
if pkill -f "python.*main.py" 2>/dev/null; then
    echo "✅ Python main.py stopped"
    STOPPED=1
fi

# Try any Python process in backend directory
if pkill -f "python.*backend" 2>/dev/null; then
    echo "✅ Python backend processes stopped"
    STOPPED=1
fi

if [ $STOPPED -eq 0 ]; then
    echo "ℹ️  Python backend server was not running"
fi

# Also kill by port if needed
echo "🔸 Cleaning up port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "ℹ️  Port 8000 was already free"

# Wait a moment for processes to terminate
sleep 2

# Check if any processes are still running
ANGULAR_RUNNING=$(ps aux | grep "ng serve" | grep -v grep | wc -l)
BACKEND_RUNNING=$(ps aux | grep -E "(uvicorn|python.*main\.py)" | grep -v grep | wc -l)
PORT_8000_USED=$(lsof -ti:8000 2>/dev/null | wc -l)

echo ""
echo "📊 Server Status Check:"
echo "======================"

if [ $ANGULAR_RUNNING -eq 0 ]; then
    echo "✅ Angular frontend: Stopped"
else
    echo "⚠️  Angular frontend: Still running ($ANGULAR_RUNNING processes)"
fi

if [ $BACKEND_RUNNING -eq 0 ] && [ $PORT_8000_USED -eq 0 ]; then
    echo "✅ Python backend: Stopped"
else
    echo "⚠️  Python backend: Still running (Processes: $BACKEND_RUNNING, Port 8000: $PORT_8000_USED)"
fi

echo ""
echo "🎯 All development servers have been stopped!"
echo "📝 To start servers again, run: ./start-servers.sh or ./scripts/server/start-servers.sh"
echo ""