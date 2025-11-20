#!/usr/bin/env python3
"""
Organization Database Initialization Script

This script ensures an organization's database has all required standard collections:
- reports
- custom_templates  
- users_settings
- activity_logs
- files_metadata
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
import os
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from database.multi_db_manager import MultiDatabaseManager
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def initialize_org_database(org_id: str):
    """Initialize database structure for an organization"""
    
    logger.info("=" * 80)
    logger.info(f"Initializing Database for Organization: {org_id}")
    logger.info("=" * 80)
    
    db_manager = MultiDatabaseManager()
    
    try:
        # Connect to MongoDB
        logger.info("📡 Connecting to MongoDB...")
        await db_manager.connect()
        
        if not db_manager.is_connected:
            logger.error("❌ Failed to connect to MongoDB")
            return False
        
        logger.info("✅ Connected to MongoDB")
        
        # Use the new ensure_org_database_structure method
        success = await db_manager.ensure_org_database_structure(org_id)
        
        if success:
            logger.info("\n" + "=" * 80)
            logger.info("✅ ORGANIZATION DATABASE INITIALIZED SUCCESSFULLY")
            logger.info("=" * 80)
            
            # List all collections
            org_db = db_manager.get_org_database(org_id)
            collections = await org_db.list_collection_names()
            
            logger.info(f"\n📊 Collections in {org_id}:")
            for collection in sorted(collections):
                count = await org_db[collection].count_documents({})
                logger.info(f"  - {collection}: {count} documents")
            
            return True
        else:
            logger.error("❌ Failed to initialize organization database")
            return False
        
    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await db_manager.disconnect()
        logger.info("\n🔒 Disconnected from MongoDB")


async def list_org_databases():
    """List all organization databases"""
    
    logger.info("=" * 80)
    logger.info("Listing Organization Databases")
    logger.info("=" * 80)
    
    db_manager = MultiDatabaseManager()
    
    try:
        await db_manager.connect()
        
        # Get all databases
        db_list = await db_manager.client.list_database_names()
        
        # Filter for organization databases (exclude system and admin databases)
        system_dbs = ['admin', 'local', 'config', 'valuation_admin', 'shared_resources', 
                     'valuation_app_prod', 'valuation_reports']
        
        org_dbs = [db for db in db_list if db not in system_dbs]
        
        logger.info(f"\n📊 Found {len(org_dbs)} organization databases:")
        for org_db in sorted(org_dbs):
            # Get collection count
            db = db_manager.client[org_db]
            collections = await db.list_collection_names()
            logger.info(f"  - {org_db}: {len(collections)} collections")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to list databases: {e}")
        return False
    
    finally:
        await db_manager.disconnect()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize organization database structure")
    parser.add_argument("org_id", nargs="?", help="Organization ID (e.g., demo_org_001)")
    parser.add_argument("--list", action="store_true", help="List all organization databases")
    args = parser.parse_args()
    
    if args.list:
        success = asyncio.run(list_org_databases())
    elif args.org_id:
        success = asyncio.run(initialize_org_database(args.org_id))
    else:
        parser.print_help()
        sys.exit(1)
    
    sys.exit(0 if success else 1)
