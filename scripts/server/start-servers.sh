#!/bin/bash

# Valuation App - Enhanced Start Servers Script with Health Checks
# This script starts both backend and frontend with proper health monitoring

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="/Users/sandeepjangra/Downloads/development/ValuationAppV1"
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

# Function to wait for backend health check
wait_for_backend() {
    local elapsed=0
    print_info "Waiting for backend to be ready (max ${MAX_WAIT_BACKEND}s)..."
    
    while [ $elapsed -lt $MAX_WAIT_BACKEND ]; do
        if curl -s -f "$BACKEND_HEALTH_URL" > /dev/null 2>&1; then
            print_success "Backend is ready! (took ${elapsed}s)"
            return 0
        fi
        
        # Show progress indicator
        echo -n "."
        sleep 1
        elapsed=$((elapsed + 1))
    done
    
    echo ""
    print_error "Backend failed to start within ${MAX_WAIT_BACKEND}s"
    print_info "Check logs: tail -f $BACKEND_LOG"
    return 1
}

# Function to wait for frontend health check
wait_for_frontend() {
    local elapsed=0
    print_info "Waiting for frontend to compile and serve (max ${MAX_WAIT_FRONTEND}s)..."
    print_warning "This may take 30-60 seconds for initial compilation..."
    
    while [ $elapsed -lt $MAX_WAIT_FRONTEND ]; do
        # Check if Angular compilation is complete by looking for specific output
        if curl -s -f "$FRONTEND_HEALTH_URL" > /dev/null 2>&1; then
            # Verify it's actually the Angular app, not just a placeholder
            if curl -s "$FRONTEND_HEALTH_URL" | grep -q "app-root" 2>/dev/null; then
                print_success "Frontend is ready! (took ${elapsed}s)"
                return 0
            fi
        fi
        
        # Show progress indicator every 5 seconds
        if [ $((elapsed % 5)) -eq 0 ]; then
            echo -n "."
        fi
        
        sleep 1
        elapsed=$((elapsed + 1))
    done
    
    echo ""
    print_error "Frontend failed to start within ${MAX_WAIT_FRONTEND}s"
    print_info "Check logs: tail -f $FRONTEND_LOG"
    return 1
}

# Function to check Python virtual environment
check_venv() {
    if [ ! -d "${PROJECT_ROOT}/valuation_env" ]; then
        print_error "Virtual environment not found at ${PROJECT_ROOT}/valuation_env"
        print_info "Please create it first: python3 -m venv valuation_env"
        return 1
    fi
    
    # Check if required packages are installed
    if ! source "${PROJECT_ROOT}/valuation_env/bin/activate" 2>/dev/null; then
        print_error "Failed to activate virtual environment"
        return 1
    fi
    
    if ! python -c "import fastapi" 2>/dev/null; then
        print_warning "FastAPI not found in venv. Installing dependencies..."
        pip install -r "${PROJECT_ROOT}/requirements.txt" > /dev/null 2>&1 || true
    fi
    
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
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "python.*main.py" 2>/dev/null || true
kill_port $BACKEND_PORT
kill_port $FRONTEND_PORT
print_success "Cleanup complete"
echo ""

# Step 2: Pre-flight checks
print_header "Step 2: Pre-flight Checks"
if ! check_venv; then
    exit 1
fi
print_success "Python virtual environment OK"

if ! check_node_modules; then
    exit 1
fi
print_success "Node modules OK"
echo ""

# Step 3: Start Backend
print_header "Step 3: Starting Backend Server"
print_info "Port: $BACKEND_PORT"
print_info "Log:  $BACKEND_LOG"

cd "${PROJECT_ROOT}"
source valuation_env/bin/activate
cd backend

# Clear old log
> "$BACKEND_LOG"

# Start backend with uvicorn
nohup uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!

print_info "Backend PID: $BACKEND_PID"

# Wait for backend to be ready
if ! wait_for_backend; then
    print_error "Backend startup failed!"
    echo ""
    print_info "Last 20 lines of backend log:"
    tail -20 "$BACKEND_LOG"
    exit 1
fi

# Verify backend API
print_info "Testing backend API endpoints..."
BACKEND_TEST_PASSED=true

# Test health endpoint
if curl -s -f "$BACKEND_HEALTH_URL" > /dev/null 2>&1; then
    print_success "Health endpoint: OK"
else
    print_error "Health endpoint: FAILED"
    BACKEND_TEST_PASSED=false
fi

# Test common fields endpoint
if curl -s -f "http://localhost:${BACKEND_PORT}/api/common-fields" > /dev/null 2>&1; then
    print_success "Common fields endpoint: OK"
else
    print_warning "Common fields endpoint: FAILED (non-critical)"
fi

if [ "$BACKEND_TEST_PASSED" = false ]; then
    print_error "Backend tests failed!"
    exit 1
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

# Wait for frontend to be ready
if ! wait_for_frontend; then
    print_error "Frontend startup failed!"
    echo ""
    print_info "Last 30 lines of frontend log:"
    tail -30 "$FRONTEND_LOG"
    
    print_warning "Frontend may still be compiling. Check logs with:"
    print_info "tail -f $FRONTEND_LOG"
    exit 1
fi

echo ""

# Step 5: Final Status Report
print_header "============================================"
print_header "✅ Startup Complete!"
print_header "============================================"
echo ""

print_success "Backend:  http://localhost:$BACKEND_PORT"
print_success "Frontend: http://localhost:$FRONTEND_PORT"
echo ""

print_info "API Endpoints:"
echo "  - Health:         http://localhost:$BACKEND_PORT/api/health"
echo "  - Common Fields:  http://localhost:$BACKEND_PORT/api/common-fields"
echo "  - Banks:          http://localhost:$BACKEND_PORT/api/banks"
echo "  - Custom Templates: http://localhost:$BACKEND_PORT/api/custom-templates"
echo ""

print_info "Frontend Pages:"
echo "  - Dashboard:      http://localhost:$FRONTEND_PORT/dashboard"
echo "  - New Report:     http://localhost:$FRONTEND_PORT/new-report"
echo "  - Custom Templates: http://localhost:$FRONTEND_PORT/custom-templates"
echo ""

print_info "Process Management:"
echo "  - Backend PID:  $BACKEND_PID"
echo "  - Frontend PID: $FRONTEND_PID"
echo ""

print_info "To stop servers:"
echo "  pkill -f 'ng serve'"
echo "  pkill -f 'uvicorn'"
echo ""

print_info "To view logs:"
echo "  Backend:  tail -f $BACKEND_LOG"
echo "  Frontend: tail -f $FRONTEND_LOG"
echo ""

print_success "🎉 All systems operational!"
