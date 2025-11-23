#!/bin/bash
#
# MongoDB Backup Runner Script
# Convenience script to run MongoDB backups
#

# Change to project root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/.."
cd "$PROJECT_ROOT"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   MongoDB Atlas Backup Script          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Error: .env file not found${NC}"
    echo "Please create a .env file with MONGODB_URI"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: python3 not found${NC}"
    echo "Please install Python 3"
    exit 1
fi

# Parse command line arguments
ACTION=${1:-backup}

case "$ACTION" in
    backup)
        echo -e "${GREEN}🚀 Starting MongoDB backup...${NC}"
        echo ""
        python3 scripts/backup_mongodb.py --action backup
        ;;
    
    restore)
        if [ -z "$2" ]; then
            echo -e "${YELLOW}Available backups:${NC}"
            python3 scripts/backup_mongodb.py --action list
            echo ""
            echo -e "${YELLOW}Usage: $0 restore <timestamp>${NC}"
            exit 1
        fi
        echo -e "${YELLOW}⚠️  Restoring backup: $2${NC}"
        python3 scripts/backup_mongodb.py --action restore --timestamp "$2"
        ;;
    
    list)
        echo -e "${BLUE}📋 Listing available backups...${NC}"
        echo ""
        python3 scripts/backup_mongodb.py --action list
        ;;
    
    help|--help|-h)
        echo "Usage: $0 [command] [options]"
        echo ""
        echo "Commands:"
        echo "  backup              Create a new backup (default)"
        echo "  restore <timestamp> Restore from a specific backup"
        echo "  list               List all available backups"
        echo "  help               Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 backup                    # Create backup"
        echo "  $0 list                      # List backups"
        echo "  $0 restore 20231123_145030   # Restore specific backup"
        ;;
    
    *)
        echo -e "${RED}❌ Unknown command: $ACTION${NC}"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac
