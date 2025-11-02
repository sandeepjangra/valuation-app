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

# Stop Python backend server
echo "🔸 Stopping Python backend server..."
pkill -f "python.*main.py" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Python backend server stopped"
else
    echo "ℹ️  Python backend server was not running"
fi

# Additional cleanup - stop any other Python processes in the backend directory
echo "🔸 Cleaning up any remaining backend processes..."
pkill -f "uvicorn.*main:app" 2>/dev/null
pkill -f "python.*backend" 2>/dev/null

# Wait a moment for processes to terminate
sleep 2

# Check if any processes are still running
ANGULAR_RUNNING=$(ps aux | grep "ng serve" | grep -v grep | wc -l)
BACKEND_RUNNING=$(ps aux | grep "python.*main.py" | grep -v grep | wc -l)

echo ""
echo "📊 Server Status Check:"
echo "======================"

if [ $ANGULAR_RUNNING -eq 0 ]; then
    echo "✅ Angular frontend: Stopped"
else
    echo "⚠️  Angular frontend: Still running ($ANGULAR_RUNNING processes)"
fi

if [ $BACKEND_RUNNING -eq 0 ]; then
    echo "✅ Python backend: Stopped"
else
    echo "⚠️  Python backend: Still running ($BACKEND_RUNNING processes)"
fi

echo ""
echo "🎯 All development servers have been stopped!"
echo "📝 To start servers again, run: ./start-servers.sh"
echo ""