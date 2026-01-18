"""
MongoDB Collection Migration Script
====================================
Migrates bank-specific and common collections from valuation_admin to shared_resources

Collections to migrate:
1. *_property_details (bank-specific templates) -> 14 collections
2. common_form_fields -> 1 collection  
3. document_types -> 1 collection

Total: 16 collections
"""

from pymongo import MongoClient
import os
from datetime import datetime

MONGODB_URI = "mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority"

def migrate_collections():
    client = MongoClient(MONGODB_URI)
    
    source_db = client['valuation_admin']
    target_db = client['shared_resources']
    
    print("🚀 Starting MongoDB Collection Migration")
    print("=" * 70)
    
    # Collections to migrate
    property_details_collections = [
        'bob_land_property_details',
        'boi_apartment_property_details',
        'boi_land_property_details',
        'cbi_all_property_details',
        'hdfc_all_property_details',
        'pnb_land_property_details',
        'sbi_apartment_property_details',
        'sbi_land_property_details',
        'ubi_apartment_property_details',
        'ubi_land_property_details',
        'uco_apartment_property_details',
        'uco_land_property_details',
    ]
    
    common_collections = [
        'common_form_fields',
        'document_types'
    ]
    
    all_collections = property_details_collections + common_collections
    
    migrated_count = 0
    skipped_count = 0
    
    for collection_name in all_collections:
        print(f"\n📦 Processing: {collection_name}")
        
        # Check if already exists in target
        if collection_name in target_db.list_collection_names():
            existing_count = target_db[collection_name].count_documents({})
            print(f"   ⚠️  Already exists in shared_resources ({existing_count} documents)")
            
            # Ask user what to do
            response = input(f"   ❓ Drop and recreate? (y/n): ").strip().lower()
            if response == 'y':
                target_db[collection_name].drop()
                print(f"   🗑️  Dropped existing collection")
            else:
                print(f"   ⏭️  Skipping...")
                skipped_count += 1
                continue
        
        # Get all documents from source
        source_collection = source_db[collection_name]
        documents = list(source_collection.find())
        
        if not documents:
            print(f"   ❌ No documents found in source")
            continue
        
        # Add migration metadata
        for doc in documents:
            doc['migrationMetadata'] = {
                'migratedFrom': f'valuation_admin.{collection_name}',
                'migratedAt': datetime.utcnow().isoformat(),
                'migrationScript': 'migrate_collections_to_shared_resources.py',
                'originalDatabase': 'valuation_admin'
            }
        
        # Insert into target
        target_collection = target_db[collection_name]
        result = target_collection.insert_many(documents)
        
        print(f"   ✅ Migrated {len(result.inserted_ids)} documents")
        migrated_count += 1
    
    print("\n" + "=" * 70)
    print(f"✅ Migration Complete!")
    print(f"   Migrated: {migrated_count} collections")
    print(f"   Skipped: {skipped_count} collections")
    print(f"   Total: {len(all_collections)} collections processed")
    
    # Verify migration
    print("\n🔍 Verification:")
    for collection_name in all_collections:
        source_count = source_db[collection_name].count_documents({})
        target_count = target_db[collection_name].count_documents({})
        status = "✅" if target_count > 0 else "❌"
        print(f"   {status} {collection_name}: {target_count} docs (source: {source_count})")
    
    print("\n🎉 Migration process completed!")

if __name__ == "__main__":
    print("⚠️  This will migrate collections from valuation_admin to shared_resources")
    print("⚠️  Existing collections in shared_resources may be overwritten")
    print()
    
    response = input("Continue? (yes/no): ").strip().lower()
    if response == 'yes':
        migrate_collections()
    else:
        print("❌ Migration cancelled")
