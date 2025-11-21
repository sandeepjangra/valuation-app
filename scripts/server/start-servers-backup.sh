#!/bin/bash

# Valuation App - Start Both Servers Script
echo "🚀 Starting Valuation App Servers..."

# Kill any existing processes
echo "🔄 Cleaning up existing processes..."
pkill -f "ng serve"
pkill -f "python.*main.py"
lsof -ti:4200 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Wait a moment
sleep 2

# Start Backend Server
echo "🔧 Starting Backend Server (Port 8000)..."
cd /Users/sandeepjangra/Downloads/development/ValuationAppV1
source valuation_env/bin/activate
cd backend
nohup python main.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Start Frontend Server
echo "🎨 Starting Frontend Server (Port 4200)..."
cd /Users/sandeepjangra/Downloads/development/ValuationAppV1/valuation-frontend
nohup ng serve --host localhost --port 4200 > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Wait for frontend to start
sleep 5

# Test both servers
echo "🧪 Testing servers..."
if curl -s http://localhost:8000/api/common-fields > /dev/null; then
    echo "✅ Backend (8000): Running"
else
    echo "❌ Backend (8000): Failed"
fi

if curl -s http://localhost:4200 > /dev/null; then
    echo "✅ Frontend (4200): Running"
else
    echo "❌ Frontend (4200): Failed"
fi

echo ""
echo "🌟 Servers Status:"
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:4200"
echo "Report Form: http://localhost:4200/report-form?bankCode=SBI&bankName=State%20Bank%20of%20India&templateId=SBI_LAND_001&templateName=Land%20Property%20Valuation&propertyType=land"
echo ""
echo "📋 To stop servers:"
echo "  pkill -f 'ng serve'"
echo "  pkill -f 'python.*main.py'"
echo ""
echo "📋 To check logs:"
echo "  tail -f backend/backend.log"
echo "  tail -f valuation-frontend/frontend.log"