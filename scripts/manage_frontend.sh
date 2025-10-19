#!/bin/bash

# =============================================================================
# Valuation Application - Frontend Management Script
# =============================================================================
# Description: Manage Angular frontend development server
# Author: AI Assistant
# Version: 1.0
# =============================================================================

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_DIR/valuation-frontend"
PIDFILE="$PROJECT_DIR/.frontend.pid"
LOGFILE="$PROJECT_DIR/logs/frontend.log"
FRONTEND_PORT=4200

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[FRONTEND]${NC} $1"
}

success() {
    echo -e "${BLUE}[FRONTEND]${NC} ${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${BLUE}[FRONTEND]${NC} ${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${BLUE}[FRONTEND]${NC} ${RED}❌ $1${NC}"
}

# Setup Node.js environment
setup_node_env() {
    log "Setting up Node.js environment..."
    
    # Load nvm if available
    if [ -s "$HOME/.nvm/nvm.sh" ]; then
        export NVM_DIR="$HOME/.nvm"
        source "$NVM_DIR/nvm.sh"
        
        # Use the installed Node.js version
        if ! command -v node &> /dev/null; then
            nvm use --lts 2>/dev/null || nvm install --lts
        fi
    else
        error "nvm not found. Please install Node.js first."
        exit 1
    fi
    
    # Verify Node.js and npm
    if ! command -v node &> /dev/null; then
        error "Node.js not found after setup"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        error "npm not found after setup"
        exit 1
    fi
    
    success "Node.js $(node --version) and npm $(npm --version) ready"
}

# Check if frontend is running
is_frontend_running() {
    if [ -f "$PIDFILE" ]; then
        local pid=$(cat "$PIDFILE")
        if kill -0 "$pid" 2>/dev/null; then
            return 0
        else
            # PID file exists but process is dead, clean it up
            rm -f "$PIDFILE"
            return 1
        fi
    fi
    return 1
}

# Get frontend status
get_frontend_status() {
    if is_frontend_running; then
        local pid=$(cat "$PIDFILE")
        local memory=$(ps -o rss= -p "$pid" 2>/dev/null | awk '{print int($1/1024)}' || echo "N/A")
        local start_time=$(ps -o lstart= -p "$pid" 2>/dev/null || echo "Unknown")
        
        success "Frontend is running (PID: $pid)"
        log "🌐 Frontend URL: http://localhost:$FRONTEND_PORT"
        log "💾 Memory usage: ${memory} MB"
        log "⏰ Started: $start_time"
        
        # Check if port is responding
        if curl -s -f "http://localhost:$FRONTEND_PORT" >/dev/null 2>&1; then
            success "Frontend is responding to requests"
        else
            warning "Frontend process running but not responding on port $FRONTEND_PORT"
        fi
    else
        warning "Frontend is not running"
    fi
}

# Start frontend
start_frontend() {
    log "Angular Frontend Development Server"
    
    if is_frontend_running; then
        warning "Frontend is already running"
        get_frontend_status
        return 0
    fi
    
    # Setup Node.js environment
    setup_node_env
    
    # Check if frontend directory exists
    if [ ! -d "$FRONTEND_DIR" ]; then
        error "Frontend directory not found: $FRONTEND_DIR"
        exit 1
    fi
    
    # Check if package.json exists
    if [ ! -f "$FRONTEND_DIR/package.json" ]; then
        error "package.json not found in $FRONTEND_DIR"
        exit 1
    fi
    
    # Create logs directory
    mkdir -p "$(dirname "$LOGFILE")"
    
    log "📦 Installing/updating dependencies..."
    cd "$FRONTEND_DIR"
    
    # Check if node_modules exists, install if not
    if [ ! -d "node_modules" ]; then
        log "Installing npm dependencies..."
        npm install
    else
        log "Dependencies already installed"
    fi
    
    log "🚀 Starting Angular development server..."
    
    # Start the frontend server in background
    nohup npm start > "$LOGFILE" 2>&1 &
    local npm_pid=$!
    
    # Wait a moment for the process to stabilize
    sleep 2
    
    # Check if the process is still running
    if ! kill -0 "$npm_pid" 2>/dev/null; then
        error "Failed to start frontend server"
        if [ -f "$LOGFILE" ]; then
            error "Last few lines from log:"
            tail -10 "$LOGFILE"
        fi
        exit 1
    fi
    
    # Save PID
    echo "$npm_pid" > "$PIDFILE"
    
    # Wait for server to be ready
    log "⏳ Waiting for frontend server to start..."
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -f "http://localhost:$FRONTEND_PORT" >/dev/null 2>&1; then
            success "Frontend server started successfully!"
            get_frontend_status
            return 0
        fi
        
        # Check if process is still alive
        if ! kill -0 "$npm_pid" 2>/dev/null; then
            error "Frontend process died during startup"
            if [ -f "$LOGFILE" ]; then
                error "Last few lines from log:"
                tail -10 "$LOGFILE"
            fi
            rm -f "$PIDFILE"
            exit 1
        fi
        
        sleep 2
        ((attempt++))
        echo -n "."
    done
    
    echo
    warning "Frontend server started but may not be fully ready yet"
    log "Check logs: tail -f $LOGFILE"
    get_frontend_status
}

# Stop frontend
stop_frontend() {
    log "Stopping Angular Frontend Development Server"
    
    if ! is_frontend_running; then
        warning "Frontend server is not running"
        return 0
    fi
    
    local pid=$(cat "$PIDFILE")
    log "🛑 Stopping frontend server (PID: $pid)..."
    
    # Try graceful shutdown first
    if kill -TERM "$pid" 2>/dev/null; then
        # Wait for graceful shutdown
        local max_wait=10
        local wait_count=0
        
        while [ $wait_count -lt $max_wait ]; do
            if ! kill -0 "$pid" 2>/dev/null; then
                break
            fi
            sleep 1
            ((wait_count++))
        done
        
        # Force kill if still running
        if kill -0 "$pid" 2>/dev/null; then
            warning "Graceful shutdown failed, force killing..."
            kill -KILL "$pid" 2>/dev/null || true
        fi
    fi
    
    # Clean up PID file
    rm -f "$PIDFILE"
    
    # Also kill any remaining Angular/Node processes on the port
    local port_pid=$(lsof -ti:$FRONTEND_PORT 2>/dev/null || true)
    if [ -n "$port_pid" ]; then
        log "🔫 Killing remaining processes on port $FRONTEND_PORT..."
        kill -KILL $port_pid 2>/dev/null || true
    fi
    
    success "Frontend server stopped"
}

# Restart frontend
restart_frontend() {
    log "Restarting Angular Frontend Development Server"
    stop_frontend
    sleep 2
    start_frontend
}

# Show logs
show_logs() {
    if [ -f "$LOGFILE" ]; then
        log "📋 Showing frontend logs (last 50 lines):"
        echo "----------------------------------------"
        tail -50 "$LOGFILE"
        echo "----------------------------------------"
        log "To follow logs in real-time: tail -f $LOGFILE"
    else
        warning "No log file found at $LOGFILE"
    fi
}

# Install dependencies
install_deps() {
    log "Installing Frontend Dependencies"
    
    setup_node_env
    
    if [ ! -d "$FRONTEND_DIR" ]; then
        error "Frontend directory not found: $FRONTEND_DIR"
        exit 1
    fi
    
    cd "$FRONTEND_DIR"
    log "📦 Installing npm dependencies..."
    npm install
    success "Dependencies installed successfully"
}

# Clean install (remove node_modules and reinstall)
clean_install() {
    log "Clean Installing Frontend Dependencies"
    
    setup_node_env
    
    if [ ! -d "$FRONTEND_DIR" ]; then
        error "Frontend directory not found: $FRONTEND_DIR"
        exit 1
    fi
    
    cd "$FRONTEND_DIR"
    
    if [ -d "node_modules" ]; then
        log "🧹 Removing existing node_modules..."
        rm -rf node_modules
    fi
    
    if [ -f "package-lock.json" ]; then
        log "🧹 Removing package-lock.json..."
        rm -f package-lock.json
    fi
    
    log "📦 Clean installing npm dependencies..."
    npm install
    success "Clean install completed successfully"
}

# Show help
show_help() {
    echo
    echo -e "${BLUE}Valuation Application - Frontend Management Script${NC}"
    echo "================================================="
    echo
    echo "Usage: $0 {start|stop|restart|status|logs|install|clean-install|help}"
    echo
    echo "Commands:"
    echo "  start         Start the Angular frontend development server"
    echo "  stop          Stop the frontend server"
    echo "  restart       Restart the frontend server"
    echo "  status        Show frontend server status"
    echo "  logs          Show frontend server logs"
    echo "  install       Install npm dependencies"
    echo "  clean-install Remove node_modules and reinstall dependencies"
    echo "  help          Show this help message"
    echo
    echo "Examples:"
    echo "  $0 start      # Start the frontend server"
    echo "  $0 status     # Check if frontend is running"
    echo "  $0 logs       # View recent logs"
    echo
    echo "Frontend URL: http://localhost:$FRONTEND_PORT"
    echo "Log file: $LOGFILE"
    echo
}

# Main script logic
case "${1:-}" in
    start)
        start_frontend
        ;;
    stop)
        stop_frontend
        ;;
    restart)
        restart_frontend
        ;;
    status)
        get_frontend_status
        ;;
    logs)
        show_logs
        ;;
    install)
        install_deps
        ;;
    clean-install)
        clean_install
        ;;
    help|--help|-h)
        show_help
        ;;
    "")
        error "No command specified"
        show_help
        exit 1
        ;;
    *)
        error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac