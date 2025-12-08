#!/bin/bash

# Valuation App Authentication System Quick Start
# This script helps you set up and start the authentication system

set -e

echo "🚀 Valuation App Authentication System Setup"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "backend" ]; then
    print_error "Please run this script from the ValuationAppV1 root directory"
    exit 1
fi

print_info "Checking prerequisites..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    print_error "Python 3.8+ is required. Found: $python_version"
    exit 1
fi

print_status "Python version check passed: $python_version"

# Check if virtual environment exists
if [ ! -d "valuation_env" ]; then
    print_info "Creating Python virtual environment..."
    python3 -m venv valuation_env
    print_status "Virtual environment created"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source valuation_env/bin/activate
print_status "Virtual environment activated"

# Install/update dependencies
print_info "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
print_status "Dependencies installed"

# Check environment configuration
if [ ! -f "backend/.env" ]; then
    print_warning "Environment file not found. Creating from template..."
    cp backend/.env.example backend/.env
    print_info "Please edit backend/.env with your AWS Cognito and MongoDB configuration"
    print_info "Required variables:"
    echo "  - COGNITO_USER_POOL_ID"
    echo "  - COGNITO_CLIENT_ID"
    echo "  - MONGODB_URI"
    echo "  - AWS_REGION"
    echo ""
    read -p "Press Enter after configuring the .env file..."
fi

# Check if MongoDB is accessible
print_info "Checking MongoDB connection..."
cd backend
if python3 -c "
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from database.multi_db_manager import MultiDatabaseManager
import asyncio

async def test_connection():
    try:
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        print('MongoDB connection successful')
        await db_manager.disconnect()
        return True
    except Exception as e:
        print(f'MongoDB connection failed: {e}')
        return False

result = asyncio.run(test_connection())
sys.exit(0 if result else 1)
" 2>/dev/null; then
    print_status "MongoDB connection successful"
else
    print_error "MongoDB connection failed. Please check your MONGODB_URI in .env"
    exit 1
fi

cd ..

# Check AWS credentials
print_info "Checking AWS configuration..."
if [ -z "$AWS_ACCESS_KEY_ID" ] && [ -z "$AWS_PROFILE" ]; then
    print_warning "AWS credentials not configured"
    print_info "Please configure AWS credentials using one of these methods:"
    echo "  1. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables"
    echo "  2. Configure AWS CLI: aws configure"
    echo "  3. Use IAM roles (for EC2/Lambda deployment)"
    echo ""
    read -p "Press Enter after configuring AWS credentials..."
fi

# Run authentication system setup
print_info "Setting up authentication system..."
cd scripts
if python3 setup_auth_system.py; then
    print_status "Authentication system setup completed"
else
    print_error "Authentication system setup failed"
    exit 1
fi

cd ..

# Start the backend server
print_info "Starting backend server..."
cd backend

# Kill any existing server on port 8000
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    print_warning "Killing existing server on port 8000..."
    kill -9 $(lsof -Pi :8000 -sTCP:LISTEN -t) 2>/dev/null || true
    sleep 2
fi

# Start server in background
nohup python3 main.py > ../logs/backend_server.log 2>&1 &
server_pid=$!
echo $server_pid > ../.server.pid

# Wait for server to start
print_info "Waiting for server to start..."
sleep 5

# Check if server is running
if curl -s http://localhost:8000/api/health > /dev/null; then
    print_status "Backend server started successfully on http://localhost:8000"
else
    print_error "Backend server failed to start"
    exit 1
fi

cd ..

# Check if frontend exists and start it
if [ -d "valuation-frontend" ]; then
    print_info "Starting frontend development server..."
    cd valuation-frontend
    
    # Install npm dependencies if needed
    if [ ! -d "node_modules" ]; then
        print_info "Installing npm dependencies..."
        npm install
    fi
    
    # Start Angular development server
    print_info "Starting Angular development server..."
    npm start &
    frontend_pid=$!
    echo $frontend_pid > ../.frontend.pid
    
    print_status "Frontend server starting on http://localhost:4200"
    cd ..
fi

echo ""
echo "🎉 Authentication System Setup Complete!"
echo "========================================"
echo ""
print_status "Backend API: http://localhost:8000"
if [ -d "valuation-frontend" ]; then
    print_status "Frontend App: http://localhost:4200"
fi
echo ""
echo "📋 Test Credentials:"
echo "-------------------"
echo "System Admin:"
echo "  Email: admin@system.com"
echo "  Password: Admin123!"
echo ""
echo "Demo Manager:"
echo "  Email: manager@demo.com"
echo "  Password: Manager123!"
echo ""
echo "Demo Employee:"
echo "  Email: employee@demo.com"
echo "  Password: Employee123!"
echo ""
print_warning "Please change default passwords in production!"
echo ""
echo "📚 Documentation:"
echo "  - Authentication Guide: docs/authentication/AUTH_SYSTEM_GUIDE.md"
echo "  - API Documentation: http://localhost:8000/docs"
echo ""
echo "🛑 To stop servers:"
echo "  ./scripts/stop_servers.sh"
echo ""
print_status "Setup completed successfully!"