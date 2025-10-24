#!/bin/bash

# =============================================================================
# Valuation Application - Docker Container Management Script
# =============================================================================
# Description: Build and manage containers using Docker
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
    echo -e "${MAGENTA}[DOCKER]${NC} $1"
}

success() {
    echo -e "${MAGENTA}[DOCKER]${NC} ${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${MAGENTA}[DOCKER]${NC} ${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${MAGENTA}[DOCKER]${NC} ${RED}❌ $1${NC}"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker Desktop first."
        echo "Download from: https://www.docker.com/products/docker-desktop"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "docker-compose is not installed. Please install docker-compose."
        echo "Install with: brew install docker-compose"
        exit 1
    fi
    
    success "Docker is available"
}

# Build images
build_images() {
    log "🔨 Building Valuation Application Backend Image"
    echo "=============================================="
    
    cd "$PROJECT_DIR"
    
    log "1️⃣ Building Backend Image..."
    docker build -t valuation-backend ./backend
    
    success "🎉 Backend image built successfully!"
    
    log "📋 Built Images:"
    docker images | grep valuation
}

# Build production images
build_prod_images() {
    log "🔨 Building Production Backend Image"
    echo "==================================="
    
    cd "$PROJECT_DIR"
    
    log "1️⃣ Building Production Backend Image..."
    docker build -f ./backend/Dockerfile.prod -t valuation-backend:prod ./backend
    
    success "🎉 Production backend image built successfully!"
    
    log "📋 Built Images:"
    docker images | grep valuation
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
    
    log "🐳 Starting containers with Docker Compose..."
    docker-compose up -d
    
    success "🎉 Containers started successfully!"
    
    log "📋 Container Status:"
    docker-compose ps
    
    echo
    log "🌐 Application URLs:"
    log "   • Backend API: http://localhost:8000"
    log "   • API Docs: http://localhost:8000/api/docs"
}

# Stop containers
stop_containers() {
    log "🛑 Stopping Valuation Application Containers"
    echo "============================================="
    
    cd "$PROJECT_DIR"
    docker-compose down
    
    success "🛑 Containers stopped successfully!"
}

# View logs
view_logs() {
    local service="${1:-}"
    
    cd "$PROJECT_DIR"
    
    if [ -z "$service" ]; then
        log "📋 Viewing all container logs:"
        docker-compose logs -f
    else
        log "📋 Viewing logs for: $service"
        docker-compose logs -f "$service"
    fi
}

# Container status
container_status() {
    log "📊 Container Status"
    echo "==================="
    
    log "🐳 Running Containers:"
    docker-compose ps
    
    echo
    log "💽 Images:"
    docker images | grep valuation
    
    echo
    log "📊 System Info:"
    docker system df
}

# Clean up
cleanup() {
    log "🧹 Cleaning up containers and images"
    echo "===================================="
    
    cd "$PROJECT_DIR"
    
    log "1️⃣ Stopping containers..."
    docker-compose down -v
    
    log "2️⃣ Removing images..."
    docker rmi valuation-backend 2>/dev/null || true
    docker rmi valuation-backend:prod 2>/dev/null || true
    
    log "3️⃣ Pruning system..."
    docker system prune -f
    
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
    docker-compose up -d
    
    success "🔧 Development containers started!"
    log "📁 Source code is mounted for hot reload"
}

# Show help
show_help() {
    echo
    echo -e "${MAGENTA}Valuation Application - Docker Management Script${NC}"
    echo "================================================="
    echo
    echo "Usage: $0 {build|build-prod|start|stop|logs|status|cleanup|dev|help} [service]"
    echo
    echo "Main Commands:"
    echo "  build         Build development container images"
    echo "  build-prod    Build production container images"
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
    echo
    echo "Examples:"
    echo "  $0 build              # Build all images"
    echo "  $0 start              # Start all containers"
    echo "  $0 logs backend       # View backend logs"
    echo "  $0 status             # Check container status"
    echo "  $0 cleanup            # Clean up everything"
    echo
    echo "Quick Links (after starting):"
    echo "  Backend API:  http://localhost:8000"
    echo "  API Docs:     http://localhost:8000/api/docs"
    echo
}

# Main script logic
case "${1:-}" in
    build)
        check_docker
        build_images
        ;;
    build-prod)
        check_docker
        build_prod_images
        ;;
    start)
        check_docker
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
        check_docker
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