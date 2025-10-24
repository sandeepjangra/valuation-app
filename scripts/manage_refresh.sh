#!/bin/bash
"""
MongoDB Collections Refresh Management Script
Convenient wrapper for the Python refresh script
"""

# Set script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PYTHON_SCRIPT="$SCRIPT_DIR/refresh_collections.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_colored() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if backend is running
check_backend() {
    if curl -s "http://localhost:8000/api/health" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Show usage
show_usage() {
    echo "MongoDB Collections Refresh Management"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  status                    Show collections status"
    echo "  refresh-all              Refresh all collections"
    echo "  refresh <collection>     Refresh specific collection"
    echo "  interactive              Start interactive mode"
    echo "  start-backend            Start backend server"
    echo "  help                     Show this help"
    echo ""
    echo "Collections:"
    echo "  common_fields            Common form fields"
    echo "  sbi_land_property_details SBI land property details" 
    echo "  banks                    Bank and branch data"
    echo "  users                    User accounts"
    echo "  properties               Property records"
    echo "  valuations               Valuation assessments"
    echo "  valuation_reports        Generated reports"
    echo "  audit_logs               System audit logs"
    echo ""
    echo "Examples:"
    echo "  $0 status"
    echo "  $0 refresh common_fields"
    echo "  $0 refresh-all"
    echo "  $0 interactive"
}

# Start backend server
start_backend() {
    print_colored $BLUE "🚀 Starting backend server..."
    cd "$PROJECT_DIR"
    
    if [ -d "valuation_env" ]; then
        source valuation_env/bin/activate
        print_colored $GREEN "✅ Virtual environment activated"
    else
        print_colored $YELLOW "⚠️ Virtual environment not found"
    fi
    
    print_colored $BLUE "📡 Starting FastAPI server on port 8000..."
    python -m uvicorn backend.main:app --port 8000 --reload
}

# Main script logic
case "${1:-help}" in
    "status")
        print_colored $BLUE "📊 Checking collections status..."
        if check_backend; then
            cd "$PROJECT_DIR"
            python "$PYTHON_SCRIPT" --status
        else
            print_colored $RED "❌ Backend server is not running on port 8000"
            print_colored $YELLOW "💡 Start it with: $0 start-backend"
            exit 1
        fi
        ;;
        
    "refresh-all")
        print_colored $BLUE "🔄 Refreshing all collections..."
        if check_backend; then
            cd "$PROJECT_DIR"
            python "$PYTHON_SCRIPT" --all
        else
            print_colored $RED "❌ Backend server is not running"
            exit 1
        fi
        ;;
        
    "refresh")
        if [ -z "$2" ]; then
            print_colored $RED "❌ Please specify collection name"
            print_colored $YELLOW "💡 Usage: $0 refresh <collection_name>"
            exit 1
        fi
        
        print_colored $BLUE "🔄 Refreshing collection: $2"
        if check_backend; then
            cd "$PROJECT_DIR"
            python "$PYTHON_SCRIPT" --collection "$2"
        else
            print_colored $RED "❌ Backend server is not running"
            exit 1
        fi
        ;;
        
    "interactive")
        print_colored $BLUE "🎮 Starting interactive mode..."
        if check_backend; then
            cd "$PROJECT_DIR"
            python "$PYTHON_SCRIPT"
        else
            print_colored $RED "❌ Backend server is not running"
            print_colored $YELLOW "💡 Start it with: $0 start-backend"
            exit 1
        fi
        ;;
        
    "start-backend")
        start_backend
        ;;
        
    "help"|"--help"|"-h")
        show_usage
        ;;
        
    *)
        print_colored $RED "❌ Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac