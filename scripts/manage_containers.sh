#!/bin/bash

# =============================================================================
# Valuation Application - Podman Container Management Script
# =============================================================================
# Description: Build and manage containers using Podman
# Author: AI Assistant
# Version: 1.0
# =============================================================================

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${MAGENTA}[PODMAN]${NC} $1"
}

success() {
    echo -e "${MAGENTA}[PODMAN]${NC} ${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${MAGENTA}[PODMAN]${NC} ${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${MAGENTA}[PODMAN]${NC} ${RED}❌ $1${NC}"
}

# Check if Podman is installed
check_podman() {
    if ! command -v podman &> /dev/null; then
        error "Podman is not installed. Please install Podman first."
        echo "Install with: brew install podman"
        exit 1
    fi
    
    if ! command -v podman-compose &> /dev/null; then
        warning "podman-compose not found. Installing..."
        pip3 install podman-compose
    fi
    
    success "Podman is available"
}

# Build images
build_images() {
    log "🔨 Building Valuation Application Images"
    echo "========================================"
    
    cd "$PROJECT_DIR"
    
    log "1️⃣ Building Backend Image..."
    podman build -t valuation-backend ./backend
    
    log "2️⃣ Building Frontend Image..."
    podman build -t valuation-frontend ./valuation-frontend
    
    success "🎉 All images built successfully!"
    
    log "📋 Built Images:"
    podman images | grep valuation
}

# Run containers using compose
start_containers() {
    log "🚀 Starting Valuation Application Containers"
    echo "============================================="
    
    cd "$PROJECT_DIR"
    
    # Copy environment file if it doesn't exist
    if [ ! -f ".env" ]; then
        log "📄 Creating environment file..."
        cp .env.container .env
        warning "Please review and update .env file with your settings"
    fi
    
    log "🐳 Starting containers with Podman Compose..."
    podman-compose -f podman-compose.yml up -d
    
    success "🎉 Containers started successfully!"
    
    log "📋 Container Status:"
    podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    echo
    log "🌐 Application URLs:"
    log "   • Frontend: http://localhost"
    log "   • Backend API: http://localhost:8000"
    log "   • API Docs: http://localhost:8000/api/docs"
}

# Stop containers
stop_containers() {
    log "🛑 Stopping Valuation Application Containers"
    echo "============================================="
    
    cd "$PROJECT_DIR"
    podman-compose -f podman-compose.yml down
    
    success "🛑 Containers stopped successfully!"
}

# View logs
view_logs() {
    local service="${1:-}"
    
    cd "$PROJECT_DIR"
    
    if [ -z "$service" ]; then
        log "📋 Viewing all container logs:"
        podman-compose -f podman-compose.yml logs -f
    else
        log "📋 Viewing logs for: $service"
        podman-compose -f podman-compose.yml logs -f "$service"
    fi
}

# Container status
container_status() {
    log "📊 Container Status"
    echo "==================="
    
    log "🐳 Running Containers:"
    podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    echo
    log "💽 Images:"
    podman images | grep valuation
    
    echo
    log "📊 System Info:"
    podman system df
}

# Clean up
cleanup() {
    log "🧹 Cleaning up containers and images"
    echo "===================================="
    
    cd "$PROJECT_DIR"
    
    log "1️⃣ Stopping containers..."
    podman-compose -f podman-compose.yml down -v
    
    log "2️⃣ Removing images..."
    podman rmi valuation-backend valuation-frontend 2>/dev/null || true
    
    log "3️⃣ Pruning system..."
    podman system prune -f
    
    success "🧹 Cleanup completed!"
}

# Development mode (with hot reload)
dev_mode() {
    log "🔧 Starting Development Mode"
    echo "============================="
    
    cd "$PROJECT_DIR"
    
    # Copy environment file if it doesn't exist
    if [ ! -f ".env" ]; then
        cp .env.container .env
    fi
    
    log "🚀 Starting in development mode with volume mounts..."
    podman-compose -f docker-compose.yml up -d
    
    success "🔧 Development containers started!"
    log "📁 Source code is mounted for hot reload"
}

# Show help
show_help() {
    echo
    echo -e "${MAGENTA}Valuation Application - Podman Management Script${NC}"
    echo "================================================="
    echo
    echo "Usage: $0 {build|start|stop|logs|status|cleanup|dev|help} [service]"
    echo
    echo "Main Commands:"
    echo "  build         Build container images"
    echo "  start         Start all containers"
    echo "  stop          Stop all containers"
    echo "  status        Show container status and system info"
    echo "  cleanup       Stop containers and remove images"
    echo
    echo "Development Commands:"
    echo "  dev           Start in development mode (with hot reload)"
    echo
    echo "Logging Commands:"
    echo "  logs          Show logs from all containers"
    echo "  logs backend  Show only backend logs"
    echo "  logs frontend Show only frontend logs"
    echo
    echo "Examples:"
    echo "  $0 build              # Build all images"
    echo "  $0 start              # Start all containers"
    echo "  $0 logs backend       # View backend logs"
    echo "  $0 status             # Check container status"
    echo "  $0 cleanup            # Clean up everything"
    echo
    echo "Quick Links (after starting):"
    echo "  Frontend:     http://localhost"
    echo "  Backend API:  http://localhost:8000"
    echo "  API Docs:     http://localhost:8000/api/docs"
    echo
}

# Main script logic
case "${1:-}" in
    build)
        check_podman
        build_images
        ;;
    start)
        check_podman
        start_containers
        ;;
    stop)
        stop_containers
        ;;
    logs)
        view_logs "${2:-}"
        ;;
    status)
        container_status
        ;;
    cleanup)
        cleanup
        ;;
    dev)
        check_podman
        dev_mode
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