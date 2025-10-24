#!/bin/bash

# =============================================================================
# Valuation Application - Backend Management Script
# =============================================================================
# Description: Manage backend service
# Author: AI Assistant
# Version: 1.0
# =============================================================================

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_SCRIPT="$SCRIPT_DIR/manage_server.sh"

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
}

# Start backend service
start_services() {
    log "🚀 Starting Valuation Application Backend..."
    check_scripts
    
    log "1️⃣ Starting Backend API Server..."
    "$BACKEND_SCRIPT" start
    
    success "🎉 Backend started successfully!"
    log "🌐 Backend API: http://localhost:8000"
    log "📚 API Documentation: http://localhost:8000/api/docs"
}

# Stop backend service
stop_services() {
    log "🛑 Stopping Valuation Application Backend..."
    check_scripts
    
    log "1️⃣ Stopping Backend API Server..."
    "$BACKEND_SCRIPT" stop
    
    success "🎉 Backend stopped successfully!"
}

# Restart backend service
restart_services() {
    log "🔄 Restarting Valuation Application Backend..."
    stop_services
    sleep 2
    start_services
}

# Get status of backend service
get_status() {
    log "📊 Valuation Application Status"
    check_scripts
    
    log "🔹 Backend Status:"
    "$BACKEND_SCRIPT" status
    
    echo
    log "🌐 Service URLs:"
    log "   • Backend API: http://localhost:8000"
    log "   • API Documentation: http://localhost:8000/api/docs"
}

# Show logs
show_logs() {
    local service="${1:-all}"
    
    case "$service" in
        backend|all|*)
            log "📋 Backend Logs:"
            "$BACKEND_SCRIPT" logs
            ;;
    esac
}

# Health check
health_check() {
    log "🏥 Health Check"
    check_scripts
    
    "$BACKEND_SCRIPT" status
    
    # Test backend API
    if curl -s -f "http://localhost:8000/api/health" >/dev/null 2>&1; then
        success "Backend API is responding"
    else
        warning "Backend API is not responding"
    fi
}

# Install dependencies
install_deps() {
    log "📦 Installing Dependencies"
    check_scripts
    
    log "1️⃣ Installing Backend Dependencies..."
    cd "$PROJECT_DIR"
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        success "Backend dependencies installed"
    else
        warning "requirements.txt not found"
    fi
}

# Development setup
setup_env() {
    log "🛠️  Setting up Development Environment"
    
    # Install dependencies
    install_deps
    
    # Start services
    start_services
    
    success "🎉 Development environment setup complete!"
    log "Backend API is available at: http://localhost:8000"
}

# Show help
show_help() {
    echo
    echo -e "${MAGENTA}Valuation Application - Backend Management Script${NC}"
    echo "================================================="
    echo
    echo "Usage: $0 {start|stop|restart|status|logs|health|install|setup|help}"
    echo
    echo "Commands:"
    echo "  start         Start the backend service"
    echo "  stop          Stop the backend service"
    echo "  restart       Restart the backend service"
    echo "  status        Show backend service status"
    echo "  logs [SERVICE] Show logs (backend or all)"
    echo "  health        Perform health check"
    echo "  install       Install backend dependencies"
    echo "  setup         Complete development environment setup"
    echo "  help          Show this help message"
    echo
    echo "Examples:"
    echo "  $0 start      # Start backend"
    echo "  $0 status     # Check backend status"
    echo "  $0 logs       # View backend logs"
    echo
    echo "Service URLs:"
    echo "  Backend API:  http://localhost:8000"
    echo "  API Docs:     http://localhost:8000/api/docs"
    echo
}

# Main script logic
case "${1:-}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        get_status
        ;;
    logs)
        show_logs "${2:-all}"
        ;;
    health)
        health_check
        ;;
    install)
        install_deps
        ;;
    setup)
        setup_env
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
