#!/bin/bash

echo "🔍 Checking backend server status..."
echo ""

# Check if port 8000 is in use
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Port 8000 is in use"
    echo "Process details:"
    lsof -i :8000
    echo ""
else
    echo "❌ Port 8000 is NOT in use - backend is not running!"
    echo ""
    echo "To start backend:"
    echo "  cd backend"
    echo "  source ../valuation_env/bin/activate"
    echo "  source ../.env"
    echo "  uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
    exit 1
fi

# Try to hit the health endpoint
echo "🏥 Testing backend health..."
response=$(curl -s -w "\n%{http_code}" http://localhost:8000/health 2>/dev/null)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo "✅ Backend is healthy!"
    echo "Response: $body"
else
    echo "⚠️  Backend responded with status: $http_code"
    echo "Response: $body"
fi

echo ""
echo "📋 Testing organizations endpoint..."
response=$(curl -s -w "\n%{http_code}" http://localhost:8000/api/admin/organizations 2>/dev/null)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo "✅ Organizations endpoint works!"
    echo "Response preview (first 200 chars):"
    echo "$body" | head -c 200
    echo "..."
else
    echo "❌ Organizations endpoint failed with status: $http_code"
    echo "Response: $body"
fi

echo ""
echo "🎯 Summary:"
if [ "$http_code" = "200" ]; then
    echo "✅ Backend is running and responding correctly"
    echo "   Frontend should be able to connect"
else
    echo "❌ Backend has issues - check logs for errors"
fi
