#!/bin/bash

# Valuation App - Enhanced Start Servers Script with Health Checks
# This script starts both .NET backend and Angular frontend with proper health monitoring

set -e  # Exit on error

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Calculate project root (script is in scripts/server/, so go up 2 levels)
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

# Change to project root directory
cd "$PROJECT_ROOT"

echo "📂 Working directory: $PROJECT_ROOT"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
BACKEND_PORT=8000
FRONTEND_PORT=4200
BACKEND_HEALTH_URL="http://localhost:${BACKEND_PORT}/api/health"
FRONTEND_HEALTH_URL="http://localhost:${FRONTEND_PORT}"
MAX_WAIT_BACKEND=30  # seconds
MAX_WAIT_FRONTEND=120  # seconds (Angular takes longer to compile)

# Log files
BACKEND_LOG="${PROJECT_ROOT}/logs/backend.log"
FRONTEND_LOG="${PROJECT_ROOT}/logs/frontend.log"

# Create logs directory if it doesn't exist
mkdir -p "${PROJECT_ROOT}/logs"

# Function to print colored messages
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${CYAN}$1${NC}"
}

# Function to check if port is in use
is_port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to kill process on port
kill_port() {
    local port=$1
    if is_port_in_use $port; then
        print_warning "Port $port is in use, killing process..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Function to check .NET SDK
check_dotnet() {
    if ! command -v dotnet &> /dev/null; then
        print_error ".NET SDK not found"
        print_info "Please install .NET 8.0 SDK from https://dotnet.microsoft.com/download"
        return 1
    fi
    
    local dotnet_version=$(dotnet --version)
    print_success ".NET SDK version: $dotnet_version"
    return 0
}

# Function to check Node modules
check_node_modules() {
    if [ ! -d "${PROJECT_ROOT}/valuation-frontend/node_modules" ]; then
        print_error "node_modules not found"
        print_info "Please run: cd valuation-frontend && npm install"
        return 1
    fi
    return 0
}

# Main script starts here
print_header "============================================"
print_header "🚀 Valuation App - Server Startup"
print_header "============================================"
echo ""

# Step 1: Cleanup existing processes
print_header "Step 1: Cleanup"
print_info "Stopping any existing servers..."
pkill -f "ng serve" 2>/dev/null || true
pkill -f "dotnet run" 2>/dev/null || true
pkill -f "ValuationApp.API" 2>/dev/null || true
kill_port $BACKEND_PORT
kill_port $FRONTEND_PORT
print_success "Cleanup complete"
echo ""

# Step 2: Pre-flight checks
print_header "Step 2: Pre-flight Checks"

# Verify we're in the correct directory
if [ ! -d "backend-dotnet/ValuationApp.API" ]; then
    print_error "Cannot find backend-dotnet/ValuationApp.API - are you in the correct directory?"
    print_info "Current directory: $(pwd)"
    print_info "Expected directory: Project root with backend-dotnet/ and valuation-frontend/ folders"
    exit 1
fi
print_success "Project directory verified"

if ! check_dotnet; then
    exit 1
fi

if ! check_node_modules; then
    exit 1
fi
print_success "Node modules OK"
echo ""

# Step 3: Start Backend
print_header "Step 3: Starting .NET Backend Server"
print_info "Port: $BACKEND_PORT"
print_info "Log:  $BACKEND_LOG"

cd "${PROJECT_ROOT}"

# Load environment variables from .env file
if [ -f ".env" ]; then
    print_info "Loading environment variables from .env"
    export $(grep -v '^#' .env | xargs)
else
    print_error ".env file not found!"
    print_info "Please create .env file in project root with MONGODB_URI"
    exit 1
fi

cd backend-dotnet/ValuationApp.API

# Clear old log
> "$BACKEND_LOG"

# Start backend with dotnet run
nohup dotnet run --urls "http://localhost:$BACKEND_PORT" > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!

print_info "Backend PID: $BACKEND_PID"
echo ""

# Wait for backend to be ready in background
print_info "Backend is starting... (will verify in background)"
print_info "Check startup: tail -f $BACKEND_LOG"
echo ""

# Quick check - wait up to 5 seconds for initial startup
sleep 3
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    print_error "Backend process died immediately! Check logs:"
    tail -20 "$BACKEND_LOG"
    exit 1
fi

# Try a quick health check (don't wait long)
QUICK_CHECK=0
for i in {1..5}; do
    if curl -s -f "$BACKEND_HEALTH_URL" > /dev/null 2>&1; then
        print_success "Backend is responding!"
        QUICK_CHECK=1
        break
    fi
    sleep 1
done

if [ $QUICK_CHECK -eq 0 ]; then
    print_warning "Backend is still starting up (this is normal)"
    print_info "It may take 10-15 seconds to be fully ready"
fi

echo ""

# Step 4: Start Frontend
print_header "Step 4: Starting Frontend Server"
print_info "Port: $FRONTEND_PORT"
print_info "Log:  $FRONTEND_LOG"

cd "${PROJECT_ROOT}/valuation-frontend"

# Clear old log
> "$FRONTEND_LOG"

# Start frontend with ng serve
nohup ng serve --host localhost --port $FRONTEND_PORT > "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!

print_info "Frontend PID: $FRONTEND_PID"
echo ""

print_info "Frontend is compiling... (will take 30-60 seconds)"
print_info "Check progress: tail -f $FRONTEND_LOG"
echo ""

# Quick check - make sure process didn't die immediately
sleep 2
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    print_error "Frontend process died immediately! Check logs:"
    tail -20 "$FRONTEND_LOG"
    exit 1
fi

print_info "Frontend compilation in progress (runs in background)"
echo ""

# Step 5: Final Status Report
print_header "============================================"
print_header "✅ Servers Started!"
print_header "============================================"
echo ""

print_success "Backend:  http://localhost:$BACKEND_PORT (PID: $BACKEND_PID)"
print_success "Frontend: http://localhost:$FRONTEND_PORT (PID: $FRONTEND_PID)"
echo ""

print_warning "⏳ Please wait 30-60 seconds for frontend to compile"
echo ""

print_info "📋 Quick Reference:"
echo ""
echo "  Backend Ready When:"
echo "    curl http://localhost:$BACKEND_PORT/api/health"
echo ""
echo "  Frontend Ready When:"
echo "    curl http://localhost:$FRONTEND_PORT | grep app-root"
echo ""

print_info "📊 Monitor Progress:"
echo "  Backend:  tail -f $BACKEND_LOG"
echo "  Frontend: tail -f $FRONTEND_LOG"
echo ""

print_info "🛑 Stop Servers:"
echo "  ./stop.sh or ./scripts/server/stop-servers.sh"
echo ""

print_info "🔍 Check Status:"
echo "  ps aux | grep -E '(dotnet run|ng serve)' | grep -v grep"
echo ""

# Wait a few seconds and do a final health check
print_info "⏱️  Waiting 5 seconds for backend to fully initialize..."
sleep 5

if curl -s -f "$BACKEND_HEALTH_URL" > /dev/null 2>&1; then
    print_success "✅ Backend is ready and responding!"
    echo ""
    print_info "🌐 API Endpoints Available:"
    echo "  - Health:           http://localhost:$BACKEND_PORT/api/health"
    echo "  - Banks:            http://localhost:$BACKEND_PORT/api/banks"
    echo "  - Templates:        http://localhost:$BACKEND_PORT/api/templates"
    echo "  - Organizations:    http://localhost:$BACKEND_PORT/api/organizations"
else
    print_warning "⚠️  Backend is still initializing (check logs)"
fi

echo ""
print_success "🎉 Startup script completed - servers running in background!"
print_info "📝 All output is being logged to files listed above"
echo ""
