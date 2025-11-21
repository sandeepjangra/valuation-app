#!/usr/bin/env python3
import asyncio
import sys, os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from database.multi_db_manager import MultiDatabaseManager

async def check_collections():
    db_manager = MultiDatabaseManager()
    await db_manager.connect()
    
    # Check what collections exist
    admin_db = db_manager.databases['admin']
    collections = await admin_db.list_collection_names()
    print('Collections in admin database:', collections)
    
    # Check for any common fields documents
    if 'common_form_fields' in collections:
        docs = await db_manager.find_many('admin', 'common_form_fields', {}, include_inactive=True)
        print(f'Found {len(docs)} documents in common_form_fields collection')
        for doc in docs:
            print(f'  - ID: {doc.get("_id")}, Active: {doc.get("isActive")}, Version: {doc.get("version")}')
    else:
        print('common_form_fields collection does not exist')
    
    await db_manager.disconnect()

asyncio.run(check_collections())