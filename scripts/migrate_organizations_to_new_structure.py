#!/usr/bin/env python3
"""
Migrate Organizations Collection to New C# Structure

This script migrates the organizations collection from the old camelCase structure
to the new C# PascalCase structure.

Old structure (camelCase):
    - shortName, fullName, reportReferenceInitials
    - lastReferenceNumber, isActive
    - createdAt, updatedAt

New structure (PascalCase):
    - ShortName, FullName, ReportReferenceInitials
    - LastReferenceNumber, IsActive
    - CreatedAt, UpdatedAt
"""

from pymongo import MongoClient
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from bson import ObjectId

# Load environment variables
load_dotenv()

def connect_to_mongodb():
    """Connect to MongoDB Atlas"""
    try:
        client = MongoClient(os.getenv('MONGODB_URI'))
        # Test connection
        client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas\n")
        return client
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        raise

def transform_organization(org):
    """Transform organization from camelCase to PascalCase"""
    # Handle datetime conversion
    created_at = org.get('createdAt')
    updated_at = org.get('updatedAt')
    
    if isinstance(created_at, datetime):
        created_at = created_at.isoformat()
    elif created_at is None:
        created_at = datetime.utcnow().isoformat()
    else:
        created_at = str(created_at)
    
    if isinstance(updated_at, datetime):
        updated_at = updated_at.isoformat()
    elif updated_at is None:
        updated_at = datetime.utcnow().isoformat()
    else:
        updated_at = str(updated_at)
    
    transformed = {
        "OrganizationId": str(org.get('_id', '')),
        "ShortName": org.get('shortName', ''),
        "FullName": org.get('fullName', ''),
        "Description": org.get('description', ''),
        "ReportReferenceInitials": org.get('reportReferenceInitials', ''),
        "LastReferenceNumber": org.get('lastReferenceNumber', 0),
        "ContactEmail": org.get('contactEmail', ''),
        "ContactPhone": org.get('contactPhone', ''),
        "IsActive": org.get('isActive', True),
        "CreatedAt": created_at,
        "UpdatedAt": updated_at
    }
    
    return transformed

def migrate_organizations(client):
    """Migrate all organizations to new structure"""
    db = client['valuation_admin']
    
    print("🏢 MIGRATING ORGANIZATIONS COLLECTION")
    
    # Get all organizations
    orgs = list(db.organizations.find())
    print(f"✅ Found {len(orgs)} organization(s)\n")
    
    # Transform each organization
    transformed_orgs = []
    for org in orgs:
        transformed = transform_organization(org)
        transformed_orgs.append(transformed)
        print(f"   ✅ {org.get('shortName', 'N/A')} - {org.get('fullName', 'N/A')}")
    
    # Create collection wrapper
    organizations_data = {
        "CollectionName": "Organizations",
        "Description": "Organizations collection for the valuation application",
        "Version": "2.0",
        "MigrationDate": datetime.utcnow().isoformat(),
        "CreatedAt": datetime.utcnow().isoformat(),
        "UpdatedAt": datetime.utcnow().isoformat(),
        "Organizations": transformed_orgs
    }
    
    print(f"\n📊 Migration Summary:")
    print(f"   Total Organizations: {len(transformed_orgs)}")
    print(f"   Active Organizations: {sum(1 for o in transformed_orgs if o['IsActive'])}")
    print(f"   Inactive Organizations: {sum(1 for o in transformed_orgs if not o['IsActive'])}")
    
    return organizations_data

def save_to_file(data, filename="organizations.json"):
    """Save migrated data to local file"""
    output_dir = "templates-csharp/migrated"
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Get file size
    file_size = os.path.getsize(output_path)
    size_kb = file_size / 1024
    
    print(f"\n💾 Saved to: {output_path} ({size_kb:.1f} KB)")
    return output_path

def upload_to_mongodb(client, data):
    """Upload migrated organizations to MongoDB Atlas"""
    db = client['valuation_templates']
    
    print(f"\n📤 Uploading to MongoDB Atlas...")
    print(f"   Database: valuation_templates")
    print(f"   Collection: organizations")
    
    # Replace existing document (or insert if doesn't exist)
    result = db.organizations.replace_one(
        {},  # Match any document (since there should be only one)
        data,
        upsert=True
    )
    
    if result.upserted_id:
        print(f"✅ Organizations document inserted")
        print(f"   MongoDB ID: {result.upserted_id}")
    else:
        print(f"✅ Organizations document updated")
        print(f"   Modified: {result.modified_count} document(s)")
    
    # Create indexes
    print(f"\n📊 Creating indexes...")
    db.organizations.create_index([("Organizations.ShortName", 1)])
    db.organizations.create_index([("Organizations.OrganizationId", 1)])
    db.organizations.create_index([("Organizations.IsActive", 1)])
    print(f"✅ Indexes created")

def verify_migration(client):
    """Verify the migration was successful"""
    db = client['valuation_templates']
    
    print(f"\n🔍 Migration Verification:")
    
    # Check if document exists
    doc = db.organizations.find_one({})
    if doc:
        print(f"   ✅ Organizations document found")
        orgs = doc.get('Organizations', [])
        print(f"   ✅ Organizations count: {len(orgs)}")
        
        print(f"\n   📋 Organizations:")
        for org in orgs:
            status = "✅ Active" if org.get('IsActive') else "⚠️ Inactive"
            print(f"      {status} {org.get('ShortName')} - {org.get('FullName')}")
    else:
        print(f"   ❌ Organizations document not found")

def main():
    print("=" * 80)
    print("🚀 ORGANIZATIONS COLLECTION MIGRATION TO C# STRUCTURE")
    print("=" * 80)
    print()
    
    try:
        # Connect to MongoDB
        client = connect_to_mongodb()
        
        # Migrate organizations
        organizations_data = migrate_organizations(client)
        
        # Save to local file
        local_file = save_to_file(organizations_data)
        
        # Ask user if they want to upload
        print(f"\n⚠️  Do you want to upload to MongoDB Atlas? (yes/no)")
        response = input().strip().lower()
        
        if response in ['yes', 'y']:
            upload_to_mongodb(client, organizations_data)
            verify_migration(client)
            print(f"\n🎉 ORGANIZATIONS MIGRATION COMPLETED SUCCESSFULLY")
        else:
            print(f"\n⏸️  Migration saved locally. Upload skipped.")
            print(f"   Run the script again and choose 'yes' to upload.")
        
        # Close connection
        client.close()
        print(f"✅ Database connection closed")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
