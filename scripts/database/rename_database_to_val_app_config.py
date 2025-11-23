"""
Rename valuation_001 database to val_app_config
This script copies all collections and data from valuation_001 to val_app_config
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

MONGODB_URI = os.getenv("MONGODB_URI")

async def rename_database():
    """Copy valuation_001 to val_app_config and verify"""
    client = AsyncIOMotorClient(
        MONGODB_URI,
        tlsAllowInvalidCertificates=True
    )
    
    try:
        print("=" * 80)
        print("DATABASE RENAME: valuation_001 → val_app_config")
        print("=" * 80)
        
        source_db = client.valuation_001
        target_db = client.val_app_config
        
        # Get all collections from source
        collection_names = await source_db.list_collection_names()
        print(f"\n✓ Found {len(collection_names)} collections in valuation_001:")
        for name in collection_names:
            print(f"  - {name}")
        
        print(f"\n{'-' * 80}")
        print("Copying collections to val_app_config...")
        
        for collection_name in collection_names:
            source_collection = source_db[collection_name]
            target_collection = target_db[collection_name]
            
            # Get all documents
            documents = await source_collection.find({}).to_list(length=None)
            count = len(documents)
            
            if count > 0:
                # Insert into target
                await target_collection.insert_many(documents)
                print(f"  ✓ Copied {count} documents from {collection_name}")
            else:
                print(f"  ⚠️  Collection {collection_name} is empty")
            
            # Copy indexes
            indexes = await source_collection.list_indexes().to_list(length=None)
            for index in indexes:
                if index['name'] != '_id_':  # Skip default _id index
                    # Extract index specification
                    keys = index['key']
                    options = {}
                    if 'unique' in index:
                        options['unique'] = index['unique']
                    if 'sparse' in index:
                        options['sparse'] = index['sparse']
                    if 'name' in index:
                        options['name'] = index['name']
                    
                    try:
                        await target_collection.create_index(list(keys.items()), **options)
                        print(f"    ✓ Created index: {index['name']}")
                    except Exception as e:
                        print(f"    ⚠️  Index {index['name']} already exists or error: {e}")
        
        # Verify copy
        print(f"\n{'-' * 80}")
        print("Verification:")
        
        for collection_name in collection_names:
            source_count = await source_db[collection_name].count_documents({})
            target_count = await target_db[collection_name].count_documents({})
            
            if source_count == target_count:
                print(f"  ✓ {collection_name}: {source_count} documents (matched)")
            else:
                print(f"  ❌ {collection_name}: source={source_count}, target={target_count} (MISMATCH!)")
        
        print(f"\n{'=' * 80}")
        print("Database rename completed successfully!")
        print(f"{'=' * 80}")
        print("\nNOTE: valuation_001 is still intact. You can drop it manually after verifying val_app_config works.")
        print("To drop: db.getSiblingDB('valuation_001').dropDatabase()")
        print(f"{'=' * 80}\n")
        
    except Exception as e:
        print(f"\n❌ Error during database rename: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(rename_database())
