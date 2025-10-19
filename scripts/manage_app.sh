#!/bin/bash

# =============================================================================
# Valuation Application - Unified Management Script
# =============================================================================
# Description: Manage both frontend and backend services together
# Author: AI Assistant
# Version: 1.0
# =============================================================================

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_SCRIPT="$SCRIPT_DIR/manage_server.sh"
FRONTEND_SCRIPT="$SCRIPT_DIR/manage_frontend.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${MAGENTA}[VALUATION APP]${NC} $1"
}

success() {
    echo -e "${MAGENTA}[VALUATION APP]${NC} ${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${MAGENTA}[VALUATION APP]${NC} ${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${MAGENTA}[VALUATION APP]${NC} ${RED}❌ $1${NC}"
}

# Check if scripts exist
check_scripts() {
    if [ ! -f "$BACKEND_SCRIPT" ]; then
        error "Backend management script not found: $BACKEND_SCRIPT"
        exit 1
    fi
    
    if [ ! -f "$FRONTEND_SCRIPT" ]; then
        error "Frontend management script not found: $FRONTEND_SCRIPT"
        exit 1
    fi
}

# Start both services
start_all() {
    log "🚀 Starting Valuation Application (Full Stack)"
    echo "=================================================="
    
    check_scripts
    
    log "1️⃣ Starting Backend API Server..."
    "$BACKEND_SCRIPT" start
    
    echo
    log "2️⃣ Starting Frontend Development Server..."
    "$FRONTEND_SCRIPT" start
    
    echo
    success "🎉 Valuation Application started successfully!"
    log "🌐 Backend API: http://localhost:8000"
    log "🌐 Frontend App: http://localhost:4200"
    log "📚 API Documentation: http://localhost:8000/api/docs"
}

# Stop both services
stop_all() {
    log "🛑 Stopping Valuation Application (Full Stack)"
    echo "================================================="
    
    check_scripts
    
    log "1️⃣ Stopping Frontend Development Server..."
    "$FRONTEND_SCRIPT" stop
    
    echo
    log "2️⃣ Stopping Backend API Server..."
    "$BACKEND_SCRIPT" stop
    
    echo
    success "🛑 Valuation Application stopped successfully!"
}

# Restart both services
restart_all() {
    log "🔄 Restarting Valuation Application (Full Stack)"
    echo "=================================================="
    
    stop_all
    echo
    start_all
}

# Show status of both services
status_all() {
    log "📊 Valuation Application Status"
    echo "================================"
    
    check_scripts
    
    echo
    log "🔹 Backend API Status:"
    "$BACKEND_SCRIPT" status
    
    echo
    log "🔹 Frontend Status:"
    "$FRONTEND_SCRIPT" status
    
    echo
    log "📋 Quick Links:"
    log "   • Frontend: http://localhost:4200"
    log "   • Backend API: http://localhost:8000"
    log "   • API Docs: http://localhost:8000/api/docs"
}

# Show logs from both services
show_logs() {
    local service="${2:-both}"
    
    case "$service" in
        backend)
            log "📋 Backend Logs:"
            "$BACKEND_SCRIPT" logs
            ;;
        frontend)
            log "📋 Frontend Logs:"
            "$FRONTEND_SCRIPT" logs
            ;;
        both|*)
            log "📋 Backend Logs:"
            echo "----------------------------------------"
            "$BACKEND_SCRIPT" logs
            echo
            echo
            log "📋 Frontend Logs:"
            echo "----------------------------------------"
            "$FRONTEND_SCRIPT" logs
            ;;
    esac
}

# Install dependencies for both services
install_deps() {
    log "📦 Installing Dependencies (Full Stack)"
    echo "======================================="
    
    check_scripts
    
    log "1️⃣ Installing Backend Dependencies..."
    cd "$PROJECT_DIR"
    
    # Activate virtual environment and install Python packages
    if [ -d "valuation_env" ]; then
        log "🐍 Activating Python virtual environment..."
        source valuation_env/bin/activate
        
        if [ -f "requirements.txt" ]; then
            log "📦 Installing Python packages..."
            pip install -r requirements.txt
        fi
    else
        warning "Python virtual environment not found. Backend dependencies not installed."
    fi
    
    echo
    log "2️⃣ Installing Frontend Dependencies..."
    "$FRONTEND_SCRIPT" install
    
    echo
    success "📦 All dependencies installed successfully!"
}

# Development setup
dev_setup() {
    log "🛠️ Development Environment Setup"
    echo "=================================="
    
    log "Setting up complete development environment..."
    
    # Install dependencies
    install_deps
    
    echo
    log "🧪 Running health checks..."
    
    # Check if we can start services
    start_all
    
    echo
    log "✅ Development environment ready!"
    log "🎯 Next steps:"
    log "   1. Open http://localhost:4200 for the frontend"
    log "   2. Open http://localhost:8000/api/docs for API documentation"
    log "   3. Use './scripts/manage_app.sh status' to check service status"
}

# Quick health check
health_check() {
    log "🏥 Health Check"
    echo "==============="
    
    local backend_healthy=false
    local frontend_healthy=false
    
    # Check backend
    if curl -s -f "http://localhost:8000/api/health" >/dev/null 2>&1; then
        success "Backend API is healthy"
        backend_healthy=true
    else
        error "Backend API is not responding"
    fi
    
    # Check frontend
    if curl -s -f "http://localhost:4200" >/dev/null 2>&1; then
        success "Frontend is healthy"
        frontend_healthy=true
    else
        error "Frontend is not responding"
    fi
    
    if [ "$backend_healthy" = true ] && [ "$frontend_healthy" = true ]; then
        success "🎉 Full stack application is healthy!"
    else
        warning "⚠️ Some services are not responding"
        log "Run './scripts/manage_app.sh status' for detailed information"
    fi
}

# Show help
show_help() {
    echo
    echo -e "${MAGENTA}Valuation Application - Unified Management Script${NC}"
    echo "================================================="
    echo
    echo "Usage: $0 {start|stop|restart|status|logs|install|setup|health|help} [service]"
    echo
    echo "Main Commands:"
    echo "  start         Start both frontend and backend services"
    echo "  stop          Stop both frontend and backend services"
    echo "  restart       Restart both services"
    echo "  status        Show status of both services"
    echo "  health        Quick health check for both services"
    echo
    echo "Development Commands:"
    echo "  install       Install dependencies for both services"
    echo "  setup         Complete development environment setup"
    echo
    echo "Logging Commands:"
    echo "  logs          Show logs from both services"
    echo "  logs backend  Show only backend logs"
    echo "  logs frontend Show only frontend logs"
    echo
    echo "Individual Service Management:"
    echo "  Backend:  ./scripts/manage_server.sh {start|stop|status}"
    echo "  Frontend: ./scripts/manage_frontend.sh {start|stop|status}"
    echo
    echo "Examples:"
    echo "  $0 start              # Start full application"
    echo "  $0 status             # Check both services"
    echo "  $0 logs backend       # View backend logs only"
    echo "  $0 health             # Quick health check"
    echo "  $0 setup              # First-time setup"
    echo
    echo "Quick Links:"
    echo "  Frontend:     http://localhost:4200"
    echo "  Backend API:  http://localhost:8000"
    echo "  API Docs:     http://localhost:8000/api/docs"
    echo
}

# Main script logic
case "${1:-}" in
    start)
        start_all
        ;;
    stop)
        stop_all
        ;;
    restart)
        restart_all
        ;;
    status)
        status_all
        ;;
    logs)
        show_logs "$@"
        ;;
    install)
        install_deps
        ;;
    setup)
        dev_setup
        ;;
    health)
        health_check
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