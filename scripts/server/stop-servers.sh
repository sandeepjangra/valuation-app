#!/bin/bash

# ValuationApp - Stop Development Servers Script
# This script stops both the Angular frontend and .NET backend development servers

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

# Stop .NET backend server - try all variations
echo "🔸 Stopping .NET backend server..."
STOPPED=0

# Try dotnet run
if pkill -f "dotnet run" 2>/dev/null; then
    echo "✅ .NET backend server stopped"
    STOPPED=1
fi

# Try ValuationApp.API process
if pkill -f "ValuationApp.API" 2>/dev/null; then
    echo "✅ ValuationApp.API process stopped"
    STOPPED=1
fi

# Try any dotnet process
if pkill -f "dotnet.*ValuationApp" 2>/dev/null; then
    echo "✅ .NET backend processes stopped"
    STOPPED=1
fi

if [ $STOPPED -eq 0 ]; then
    echo "ℹ️  .NET backend server was not running"
fi

# Also kill by port if needed
echo "🔸 Cleaning up ports..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "ℹ️  Port 8000 was already free"
lsof -ti:4200 | xargs kill -9 2>/dev/null || echo "ℹ️  Port 4200 was already free"

# Wait a moment for processes to terminate
sleep 2

# Check if any processes are still running
ANGULAR_RUNNING=$(ps aux | grep "ng serve" | grep -v grep | wc -l)
BACKEND_RUNNING=$(ps aux | grep -E "(dotnet run|ValuationApp.API)" | grep -v grep | wc -l)
PORT_8000_USED=$(lsof -ti:8000 2>/dev/null | wc -l)
PORT_4200_USED=$(lsof -ti:4200 2>/dev/null | wc -l)

echo ""
echo "📊 Server Status Check:"
echo "======================"

if [ $ANGULAR_RUNNING -eq 0 ] && [ $PORT_4200_USED -eq 0 ]; then
    echo "✅ Angular frontend: Stopped"
else
    echo "⚠️  Angular frontend: Still running (Processes: $ANGULAR_RUNNING, Port 4200: $PORT_4200_USED)"
fi

if [ $BACKEND_RUNNING -eq 0 ] && [ $PORT_8000_USED -eq 0 ]; then
    echo "✅ .NET backend: Stopped"
else
    echo "⚠️  .NET backend: Still running (Processes: $BACKEND_RUNNING, Port 8000: $PORT_8000_USED)"
fi

echo ""
echo "🎯 All development servers have been stopped!"
echo "📝 To start servers again, run: ./start.sh"
echo ""
