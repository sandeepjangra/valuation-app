#!/usr/bin/env python3
"""
Collection Refresh Script
Refreshes specific collections from MongoDB ValuationReportCluster to local JSON files
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from backend.utils.collection_file_manager import CollectionFileManager
from backend.database.multi_db_manager import MultiDatabaseSession

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('collection_refresh.log')
    ]
)
logger = logging.getLogger(__name__)

async def test_database_connection():
    """Test connection to MongoDB"""
    logger.info("🔍 Testing MongoDB connection...")
    try:
        async with MultiDatabaseSession() as db:
            # Test connection to admin database (valuation_admin)
            collections = await db.list_collections("admin")
            logger.info(f"✅ Connected to valuation_admin database. Collections: {collections}")
            
            # Test specific collections
            common_fields_count = await db.count_documents("admin", "common_form_fields", {})
            logger.info(f"📊 common_form_fields collection has {common_fields_count} documents")
            
            banks_count = await db.count_documents("admin", "banks", {})
            logger.info(f"📊 banks collection has {banks_count} documents")
            
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

async def refresh_specific_collection(collection_name: str):
    """Refresh a specific collection"""
    logger.info(f"🔄 Starting refresh for {collection_name}...")
    
    manager = CollectionFileManager()
    success = await manager.refresh_collection_from_database(collection_name)
    
    if success:
        logger.info(f"✅ Successfully refreshed {collection_name}")
        
        # Read and display the file content
        file_path = manager.get_file_path(collection_name)
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                logger.info(f"📄 File size: {len(content)} characters")
                logger.info(f"📄 First 500 characters:\n{content[:500]}")
        
        # Get collection info
        info = manager.get_collection_info(collection_name)
        logger.info(f"📊 Collection info: {info}")
    else:
        logger.error(f"❌ Failed to refresh {collection_name}")
    
    return success

async def refresh_all_collections():
    """Refresh all collections"""
    logger.info("🔄 Starting refresh of all collections...")
    
    manager = CollectionFileManager()
    results = await manager.refresh_all_collections_from_database()
    
    logger.info(f"📊 Refresh results: {results}")
    
    # Display status of all collections
    status = manager.get_all_collections_status()
    for name, info in status.items():
        logger.info(f"📋 {name}: {info.get('total_documents', 0)} documents")

async def main():
    """Main function"""
    logger.info("🚀 Starting Collection Refresh Script")
    
    # Test connection first
    if not await test_database_connection():
        logger.error("❌ Cannot proceed without database connection")
        return
    
    # Menu for user choice
    print("\n" + "="*50)
    print("Collection Refresh Script")
    print("="*50)
    print("1. Refresh common_fields only")
    print("2. Refresh banks only")
    print("3. Refresh all collections")
    print("4. Test connection only")
    print("="*50)
    
    choice = input("Enter your choice (1-4): ").strip()
    
    if choice == "1":
        await refresh_specific_collection("common_fields")
    elif choice == "2":
        await refresh_specific_collection("banks")
    elif choice == "3":
        await refresh_all_collections()
    elif choice == "4":
        logger.info("✅ Connection test completed")
    else:
        logger.error("❌ Invalid choice")

if __name__ == "__main__":
    asyncio.run(main())