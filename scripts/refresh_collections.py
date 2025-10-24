#!/usr/bin/env python3
"""
MongoDB Collections Refresh Script
Standalone script to refresh all collections from MongoDB to local JSON files
"""

import asyncio
import logging
import sys
import os
import json
import requests
from datetime import datetime, timezone
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/refresh_collections.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Backend API configuration
API_BASE_URL = "http://localhost:8000/api"
TIMEOUT = 30

def ensure_logs_directory():
    """Ensure logs directory exists"""
    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)

def check_backend_status():
    """Check if backend server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def refresh_all_collections_api():
    """Refresh all collections using the REST API"""
    try:
        logger.info("🔄 Starting refresh of all collections via API...")
        
        response = requests.post(
            f"{API_BASE_URL}/admin/refresh-collections",
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ All collections refreshed successfully!")
            logger.info(f"📊 Results: {data.get('successful_count', 0)}/{data.get('total_count', 0)} collections")
            
            # Show detailed results
            results = data.get('results', {})
            for collection, success in results.items():
                status = "✅" if success else "❌"
                logger.info(f"   {status} {collection}")
            
            return True
        else:
            logger.error(f"❌ API call failed with status {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error calling refresh API: {e}")
        return False

def refresh_single_collection_api(collection_name):
    """Refresh a single collection using the REST API"""
    try:
        logger.info(f"🔄 Refreshing collection: {collection_name}")
        
        response = requests.post(
            f"{API_BASE_URL}/admin/refresh-collection/{collection_name}",
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ {collection_name} refreshed successfully!")
            logger.info(f"📊 {data.get('documents_count', 0)} documents updated")
            return True
        else:
            logger.error(f"❌ Failed to refresh {collection_name}: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error refreshing {collection_name}: {e}")
        return False

def get_collections_status():
    """Get status of all collections"""
    try:
        response = requests.get(f"{API_BASE_URL}/admin/collections-status", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        logger.error(f"Error getting collections status: {e}")
        return None

def print_collections_status():
    """Print current status of all collections"""
    logger.info("📋 Getting collections status...")
    status = get_collections_status()
    
    if not status:
        logger.error("❌ Failed to get collections status")
        return
    
    logger.info("📊 Collections Status:")
    logger.info("-" * 80)
    
    for collection_name, info in status.items():
        if info.get('file_exists', False):
            docs = info.get('total_documents', 0)
            last_mod = info.get('last_modified', 'Unknown')
            if last_mod != 'Unknown':
                # Format the timestamp
                try:
                    dt = datetime.fromisoformat(last_mod.replace('Z', '+00:00'))
                    last_mod = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass
            
            logger.info(f"✅ {collection_name:<25} | {docs:>4} docs | Updated: {last_mod}")
        else:
            logger.info(f"❌ {collection_name:<25} | File missing")
    
    logger.info("-" * 80)

def interactive_menu():
    """Interactive menu for refresh operations"""
    collections = [
        "common_fields",
        "sbi_land_property_details", 
        "banks",
        "users",
        "properties",
        "valuations",
        "valuation_reports",
        "audit_logs"
    ]
    
    while True:
        print("\n" + "="*60)
        print("🔄 MongoDB Collections Refresh Tool")
        print("="*60)
        print("1. Refresh ALL collections")
        print("2. Refresh specific collection")
        print("3. Show collections status")
        print("4. Test backend connection")
        print("5. Exit")
        print("-"*60)
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == "1":
            print("\n🔄 Refreshing all collections...")
            success = refresh_all_collections_api()
            if success:
                print("\n🎉 All collections refreshed successfully!")
            else:
                print("\n❌ Some collections failed to refresh. Check logs for details.")
                
        elif choice == "2":
            print("\nAvailable collections:")
            for i, collection in enumerate(collections, 1):
                print(f"{i:2d}. {collection}")
            
            try:
                coll_choice = int(input(f"\nEnter collection number (1-{len(collections)}): "))
                if 1 <= coll_choice <= len(collections):
                    collection_name = collections[coll_choice - 1]
                    refresh_single_collection_api(collection_name)
                else:
                    print("❌ Invalid collection number")
            except ValueError:
                print("❌ Please enter a valid number")
                
        elif choice == "3":
            print_collections_status()
            
        elif choice == "4":
            print("\n🔍 Testing backend connection...")
            if check_backend_status():
                print("✅ Backend is running and accessible")
            else:
                print("❌ Backend is not accessible")
                print("💡 Make sure the backend server is running on port 8000")
                
        elif choice == "5":
            print("\n👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-5.")

def main():
    """Main function"""
    ensure_logs_directory()
    
    logger.info("🚀 MongoDB Collections Refresh Script Started")
    logger.info(f"🎯 Target API: {API_BASE_URL}")
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            # Refresh all collections
            if not check_backend_status():
                logger.error("❌ Backend server is not running. Please start it first.")
                sys.exit(1)
            
            success = refresh_all_collections_api()
            sys.exit(0 if success else 1)
            
        elif sys.argv[1] == "--status":
            # Show status only
            if not check_backend_status():
                logger.error("❌ Backend server is not running.")
                sys.exit(1)
            
            print_collections_status()
            sys.exit(0)
            
        elif sys.argv[1] == "--collection":
            # Refresh specific collection
            if len(sys.argv) < 3:
                logger.error("❌ Please specify collection name: --collection <name>")
                sys.exit(1)
            
            collection_name = sys.argv[2]
            if not check_backend_status():
                logger.error("❌ Backend server is not running.")
                sys.exit(1)
            
            success = refresh_single_collection_api(collection_name)
            sys.exit(0 if success else 1)
            
        elif sys.argv[1] in ["--help", "-h"]:
            print("MongoDB Collections Refresh Script")
            print("\nUsage:")
            print("  python refresh_collections.py                    # Interactive mode")
            print("  python refresh_collections.py --all              # Refresh all collections")
            print("  python refresh_collections.py --status           # Show collections status")
            print("  python refresh_collections.py --collection <name> # Refresh specific collection")
            print("  python refresh_collections.py --help             # Show this help")
            print("\nExamples:")
            print("  python refresh_collections.py --collection common_fields")
            print("  python refresh_collections.py --collection sbi_land_property_details")
            sys.exit(0)
        else:
            logger.error(f"❌ Unknown argument: {sys.argv[1]}")
            logger.error("Use --help for usage information")
            sys.exit(1)
    
    # Interactive mode
    if not check_backend_status():
        logger.error("❌ Backend server is not running on port 8000")
        logger.error("💡 Please start the backend server first:")
        logger.error("   cd /path/to/project && source valuation_env/bin/activate")
        logger.error("   python -m uvicorn backend.main:app --port 8000")
        sys.exit(1)
    
    # Run interactive menu
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Script interrupted by user. Goodbye!")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()