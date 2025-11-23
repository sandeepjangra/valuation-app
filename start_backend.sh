#!/bin/bash

# Start Backend Server Script
# This script properly starts the FastAPI backend with all required environment variables

cd /Users/sandeepjangra/Downloads/development/ValuationAppV1/backend

export MONGODB_URI="mongodb+srv://sandeepjangra:Sandeep123@cluster0.kghgh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

echo "🚀 Starting backend server..."
echo "📂 Directory: $(pwd)"
echo "🐍 Python: $(/Users/sandeepjangra/Downloads/development/ValuationAppV1/valuation_env/bin/python --version)"
echo ""

/Users/sandeepjangra/Downloads/development/ValuationAppV1/valuation_env/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
