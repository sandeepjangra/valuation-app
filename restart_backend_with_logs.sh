#!/bin/bash

echo "🔄 Restarting backend with detailed logging..."

# Kill existing backend processes
pkill -f "uvicorn.*backend.main"
sleep 2

# Create logs directory if it doesn't exist
mkdir -p logs

# Clear previous log
> logs/backend.log

# Verify .env file exists and MongoDB URI is configured
if [ ! -f ".env" ]; then
    echo "❌ .env file not found! Please create .env file with MongoDB configuration."
    echo "💡 You can copy from .env.example and update the values."
    exit 1
fi

if ! grep -q "MONGODB_URI=mongodb" .env; then
    echo "⚠️  Warning: MONGODB_URI not properly configured in .env file"
    echo "💡 Please ensure MONGODB_URI is set to a valid MongoDB connection string"
fi

# Start backend with logging
cd /Users/sandeepjangra/Downloads/development/ValuationAppV1
echo "🚀 Starting backend server..."
/Users/sandeepjangra/Downloads/development/ValuationAppV1/valuation_env/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --log-level info 2>&1 | tee logs/backend.log &

# Wait for startup
sleep 3

# Test if backend is running
if curl -s "http://localhost:8000/api/admin/collections-status" > /dev/null; then
    echo "✅ Backend is running and responding"
    echo "📋 Logs are being written to logs/backend.log"
    echo "🔍 To monitor logs: tail -f logs/backend.log"
else
    echo "❌ Backend failed to start properly"
fi