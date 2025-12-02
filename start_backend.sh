#!/bin/bash

# Start Backend Server Script
# This script properly starts the FastAPI backend with all required environment variables

cd /Users/sandeepjangra/Downloads/development/ValuationAppV1/backend

# Use the correct MongoDB connection string
export MONGODB_URI="mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster"

echo "🚀 Starting backend server..."
echo "📂 Directory: $(pwd)"
echo "🐍 Python: $(/Users/sandeepjangra/Downloads/development/ValuationAppV1/valuation_env/bin/python --version)"
echo ""

/Users/sandeepjangra/Downloads/development/ValuationAppV1/valuation_env/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
