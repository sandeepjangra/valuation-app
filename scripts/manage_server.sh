#!/bin/bash

# MongoDB Server Management Script for Valuation Application
# This script starts and stops the FastAPI backend server with proper MongoDB configuration

# Set script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"
VENV_DIR="$PROJECT_ROOT/valuation_env"

# MongoDB Atlas Configuration
MONGODB_URI="mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster"
MONGODB_DB_NAME="valuation_admin"

# PID file to track running server
PID_FILE="$PROJECT_ROOT/.server.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[VALUATION APP]${NC} $1"
}

# Function to check if server is running
is_server_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0  # Server is running
        else
            # PID file exists but process is dead, clean up
            rm -f "$PID_FILE"
            return 1  # Server is not running
        fi
    else
        return 1  # Server is not running
    fi
}

# Function to start the server
start_server() {
    print_header "Starting Valuation Application Backend Server..."
    
    # Check if server is already running
    if is_server_running; then
        print_warning "Server is already running (PID: $(cat "$PID_FILE"))"
        print_status "Server URL: http://localhost:8000"
        print_status "API Docs: http://localhost:8000/api/docs"
        return 0
    fi
    
    # Validate directories
    if [ ! -d "$BACKEND_DIR" ]; then
        print_error "Backend directory not found: $BACKEND_DIR"
        return 1
    fi
    
    if [ ! -d "$VENV_DIR" ]; then
        print_error "Virtual environment not found: $VENV_DIR"
        return 1
    fi
    
    if [ ! -f "$BACKEND_DIR/main.py" ]; then
        print_error "main.py not found in backend directory"
        return 1
    fi
    
    # Change to backend directory
    cd "$BACKEND_DIR" || {
        print_error "Failed to change to backend directory"
        return 1
    }
    
    print_status "Activating virtual environment..."
    source "$VENV_DIR/bin/activate" || {
        print_error "Failed to activate virtual environment"
        return 1
    }
    
    print_status "Testing MongoDB connection..."
    MONGODB_URI="$MONGODB_URI" MONGODB_DB_NAME="$MONGODB_DB_NAME" python -c "
import os
import pymongo
try:
    client = pymongo.MongoClient(os.getenv('MONGODB_URI'), serverSelectionTimeoutMS=5000, tlsAllowInvalidCertificates=True)
    client.admin.command('ping')
    print('✅ MongoDB connection successful')
    client.close()
except Exception as e:
    print(f'❌ MongoDB connection failed: {e}')
    exit(1)
" || {
        print_error "MongoDB connection test failed"
        return 1
    }
    
    print_status "Starting FastAPI server..."
    
    # Start server in background and capture PID
    MONGODB_URI="$MONGODB_URI" MONGODB_DB_NAME="$MONGODB_DB_NAME" python main.py > "$PROJECT_ROOT/server.log" 2>&1 &
    local server_pid=$!
    
    # Save PID to file
    echo "$server_pid" > "$PID_FILE"
    
    # Wait a moment for server to start
    sleep 3
    
    # Check if server is actually running
    if ps -p "$server_pid" > /dev/null 2>&1; then
        print_status "✅ Server started successfully (PID: $server_pid)"
        print_status "🌐 Server URL: http://localhost:8000"
        print_status "📚 API Documentation: http://localhost:8000/api/docs"
        print_status "📊 Health Check: http://localhost:8000/api/health"
        print_status "📝 Server logs: $PROJECT_ROOT/server.log"
        
        # Test basic connectivity
        sleep 2
        if curl -s -f "http://localhost:8000/api/health" > /dev/null 2>&1; then
            print_status "✅ Server health check passed"
        else
            print_warning "⚠️  Server started but health check failed"
        fi
        
        return 0
    else
        print_error "❌ Server failed to start"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Function to stop the server
stop_server() {
    print_header "Stopping Valuation Application Backend Server..."
    
    if ! is_server_running; then
        print_warning "Server is not running"
        return 0
    fi
    
    local pid=$(cat "$PID_FILE")
    print_status "Stopping server (PID: $pid)..."
    
    # Try graceful shutdown first
    kill "$pid" 2>/dev/null
    
    # Wait for graceful shutdown
    local count=0
    while ps -p "$pid" > /dev/null 2>&1 && [ $count -lt 10 ]; do
        sleep 1
        count=$((count + 1))
    done
    
    # Force kill if still running
    if ps -p "$pid" > /dev/null 2>&1; then
        print_warning "Forcing server shutdown..."
        kill -9 "$pid" 2>/dev/null
        sleep 1
    fi
    
    # Clean up PID file
    rm -f "$PID_FILE"
    
    if ps -p "$pid" > /dev/null 2>&1; then
        print_error "❌ Failed to stop server"
        return 1
    else
        print_status "✅ Server stopped successfully"
        return 0
    fi
}

# Function to restart the server
restart_server() {
    print_header "Restarting Valuation Application Backend Server..."
    stop_server
    sleep 2
    start_server
}

# Function to show server status
show_status() {
    print_header "Valuation Application Backend Server Status"
    
    if is_server_running; then
        local pid=$(cat "$PID_FILE")
        print_status "✅ Server is running (PID: $pid)"
        print_status "🌐 Server URL: http://localhost:8000"
        
        # Check if server is responding
        if curl -s -f "http://localhost:8000/api/health" > /dev/null 2>&1; then
            print_status "✅ Server is responding to requests"
        else
            print_warning "⚠️  Server process exists but not responding"
        fi
        
        # Show memory usage
        local memory=$(ps -p "$pid" -o rss= 2>/dev/null | awk '{print int($1/1024) " MB"}')
        if [ -n "$memory" ]; then
            print_status "💾 Memory usage: $memory"
        fi
        
        # Show uptime
        local start_time=$(ps -p "$pid" -o lstart= 2>/dev/null)
        if [ -n "$start_time" ]; then
            print_status "⏰ Started: $start_time"
        fi
    else
        print_warning "❌ Server is not running"
    fi
}

# Function to show logs
show_logs() {
    local log_file="$PROJECT_ROOT/server.log"
    if [ -f "$log_file" ]; then
        print_header "Server Logs (last 50 lines):"
        tail -n 50 "$log_file"
    else
        print_warning "No log file found: $log_file"
    fi
}

# Function to show help
show_help() {
    echo "Valuation Application Server Management Script"
    echo ""
    echo "Usage: $0 {start|stop|restart|status|logs|help}"
    echo ""
    echo "Commands:"
    echo "  start     Start the backend server"
    echo "  stop      Stop the backend server"
    echo "  restart   Restart the backend server"
    echo "  status    Show server status"
    echo "  logs      Show server logs"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start    # Start the server"
    echo "  $0 status   # Check if server is running"
    echo "  $0 logs     # View recent logs"
    echo ""
}

# Main script logic
case "${1:-}" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Invalid command: ${1:-}"
        echo ""
        show_help
        exit 1
        ;;
esac

exit $?