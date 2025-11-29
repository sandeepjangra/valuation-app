#!/usr/bin/env python3
"""
Quick script to check existing collections in the database
"""

import asyncio
import os
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    # If python-dotenv is not installed, try to read .env manually
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

from database.mongodb_manager import MongoDBManager

async def check_collections():
    """Check existing collections and their data"""
    db_manager = MongoDBManager()
    await db_manager.connect()
    
    try:
        collections = await db_manager.database.list_collection_names()
        print('Available collections:')
        for collection in sorted(collections):
            count = await db_manager.database[collection].count_documents({})
            print(f'  - {collection}: {count} documents')
        
        # Look for any existing SBI or template data
        potential_template_collections = [c for c in collections if 'sbi' in c.lower() or 'template' in c.lower() or 'bank' in c.lower()]
        
        if potential_template_collections:
            print(f'\nPotential template collections:')
            for coll_name in potential_template_collections:
                count = await db_manager.database[coll_name].count_documents({})
                print(f'  - {coll_name}: {count} documents')
                
                # Show a sample document from collections with data
                if count > 0:
                    sample = await db_manager.database[coll_name].find_one({})
                    if sample:
                        print(f'    Sample keys: {list(sample.keys())}')
        
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(check_collections())