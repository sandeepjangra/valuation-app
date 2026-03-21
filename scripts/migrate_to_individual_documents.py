#!/usr/bin/env python3
"""
Migrate banks from single-document-with-array to individual-documents structure
This matches the templates collection pattern for better maintainability
"""

import os
import sys
from pymongo import MongoClient
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def migrate_banks_to_individual_documents():
    """Migrate banks from array structure to individual documents"""
    
    uri = os.environ.get('MONGODB_URI')
    if not uri:
        print("❌ Error: MONGODB_URI not found in environment")
        return False
    
    client = MongoClient(uri)
    db = client['valuation_templates']
    
    print("=" * 80)
    print("🔄 MIGRATING BANKS TO INDIVIDUAL DOCUMENTS")
    print("=" * 80)
    
    # 1. Get the current banks collection document
    banks_collection_doc = db.banks.find_one()
    
    if not banks_collection_doc:
        print("❌ No banks collection found")
        return False
    
    banks_array = banks_collection_doc.get('Banks', [])
    print(f"\n📊 Found {len(banks_array)} banks in array structure")
    
    # 2. Backup the old structure first
    backup_collection = f"banks_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    db[backup_collection].insert_one(banks_collection_doc)
    print(f"💾 Backed up to collection: {backup_collection}")
    
    # 3. Create individual documents for each bank
    print(f"\n📝 Creating individual bank documents...")
    
    migration_metadata = {
        "MigratedFrom": "banks_array_structure",
        "MigrationDate": datetime.utcnow(),
        "MigrationScript": "migrate_banks_to_individual_documents.py"
    }
    
    for bank in banks_array:
        # Add migration metadata
        bank.update(migration_metadata)
        
        # Use BankCode as unique identifier
        bank_code = bank.get('BankCode')
        
        # Check if document already exists
        existing = db.banks.find_one({"BankCode": bank_code})
        if existing:
            print(f"  ⚠️  Bank {bank_code} already exists as individual document, skipping...")
            continue
        
        # Insert as individual document
        result = db.banks.insert_one(bank)
        print(f"  ✅ Created document for {bank_code} (ID: {result.inserted_id})")
    
    # 4. Delete the old array-based document
    old_doc_id = banks_collection_doc['_id']
    db.banks.delete_one({"_id": old_doc_id})
    print(f"\n🗑️  Deleted old array-based document (ID: {old_doc_id})")
    
    # 5. Verify the migration
    individual_count = db.banks.count_documents({})
    print(f"\n✅ Migration complete!")
    print(f"   Total individual bank documents: {individual_count}")
    
    return True

def migrate_organizations_to_individual_documents():
    """Migrate organizations from array structure to individual documents"""
    
    uri = os.environ.get('MONGODB_URI')
    if not uri:
        print("❌ Error: MONGODB_URI not found in environment")
        return False
    
    client = MongoClient(uri)
    db = client['valuation_templates']
    
    print("\n" + "=" * 80)
    print("🔄 MIGRATING ORGANIZATIONS TO INDIVIDUAL DOCUMENTS")
    print("=" * 80)
    
    # 1. Get the current organizations collection document
    orgs_collection_doc = db.organizations.find_one()
    
    if not orgs_collection_doc:
        print("❌ No organizations collection found")
        return False
    
    orgs_array = orgs_collection_doc.get('Organizations', [])
    print(f"\n📊 Found {len(orgs_array)} organizations in array structure")
    
    # 2. Backup the old structure first
    backup_collection = f"organizations_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    db[backup_collection].insert_one(orgs_collection_doc)
    print(f"💾 Backed up to collection: {backup_collection}")
    
    # 3. Create individual documents for each organization
    print(f"\n📝 Creating individual organization documents...")
    
    migration_metadata = {
        "MigratedFrom": "organizations_array_structure",
        "MigrationDate": datetime.utcnow(),
        "MigrationScript": "migrate_organizations_to_individual_documents.py"
    }
    
    for org in orgs_array:
        # Add migration metadata
        org.update(migration_metadata)
        
        # Use ShortName as unique identifier
        short_name = org.get('ShortName')
        
        # Check if document already exists
        existing = db.organizations.find_one({"ShortName": short_name})
        if existing:
            print(f"  ⚠️  Organization {short_name} already exists as individual document, skipping...")
            continue
        
        # Insert as individual document
        result = db.organizations.insert_one(org)
        print(f"  ✅ Created document for {short_name} (ID: {result.inserted_id})")
    
    # 4. Delete the old array-based document
    old_doc_id = orgs_collection_doc['_id']
    db.organizations.delete_one({"_id": old_doc_id})
    print(f"\n🗑️  Deleted old array-based document (ID: {old_doc_id})")
    
    # 5. Verify the migration
    individual_count = db.organizations.count_documents({})
    print(f"\n✅ Migration complete!")
    print(f"   Total individual organization documents: {individual_count}")
    
    return True

if __name__ == "__main__":
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 15 + "MIGRATE TO INDIVIDUAL DOCUMENTS STRUCTURE" + " " * 22 + "║")
    print("╚" + "═" * 78 + "╝")
    
    # Migrate banks
    banks_success = migrate_banks_to_individual_documents()
    
    # Migrate organizations
    orgs_success = migrate_organizations_to_individual_documents()
    
    print("\n" + "=" * 80)
    if banks_success and orgs_success:
        print("✅ ALL MIGRATIONS COMPLETED SUCCESSFULLY!")
    else:
        print("⚠️  Some migrations failed. Check output above for details.")
    print("=" * 80 + "\n")
