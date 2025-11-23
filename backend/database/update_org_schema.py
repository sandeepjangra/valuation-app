"""
Update Organization Schema to support multi-tenancy with org_short_name
Creates System Administration org as default
"""

import asyncio
import os
import sys
from datetime import datetime, timezone
from pymongo import MongoClient
from bson import ObjectId

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def slugify(text: str) -> str:
    """Convert text to URL-safe slug"""
    import re
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text

def update_organizations_schema():
    """Update organizations collection schema"""
    
    # Get MongoDB connection string
    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        print("❌ MONGODB_URI environment variable not set")
        return False
    
    try:
        # Connect to MongoDB
        client = MongoClient(
            mongodb_uri,
            serverSelectionTimeoutMS=5000,
            tlsAllowInvalidCertificates=True  # Allow invalid SSL certificates for Atlas
        )
        db = client["val_app_config"]  # Central config database
        orgs_collection = db["organizations"]
        
        print("✅ Connected to MongoDB Atlas")
        
        # Check if System Administration org exists
        system_org = orgs_collection.find_one({"org_short_name": "system-administration"})
        
        if not system_org:
            # Create System Administration organization
            now = datetime.now(timezone.utc)
            system_org_doc = {
                "org_name": "System Administration",
                "org_short_name": "system-administration",  # URL-safe identifier
                "org_display_name": "System Administration",
                "is_system_org": True,  # Cannot be deleted
                "is_active": True,
                "contact_info": {
                    "email": "admin@valuationapp.com",
                    "phone": None,
                    "address": None
                },
                "settings": {
                    "max_users": 1000,  # Unlimited for system org
                    "features_enabled": ["reports", "templates", "banks", "users", "audit"],
                    "timezone": "UTC",
                    "date_format": "DD/MM/YYYY"
                },
                "subscription": {
                    "plan": "enterprise",
                    "max_reports_per_month": -1,  # Unlimited
                    "storage_limit_gb": -1,  # Unlimited
                    "expires_at": None
                },
                "created_by": "system",
                "created_at": now,
                "updated_at": now,
                "version": 1
            }
            
            result = orgs_collection.insert_one(system_org_doc)
            print(f"✅ Created System Administration organization: {result.inserted_id}")
        else:
            print(f"ℹ️ System Administration organization already exists: {system_org['_id']}")
        
        # Create indexes
        print("\n📋 Creating indexes...")
        
        indexes = [
            ("org_name", {"unique": True}),
            ("org_short_name", {"unique": True}),
            ("is_active", {}),
            ("created_at", {}),
        ]
        
        for field, options in indexes:
            try:
                orgs_collection.create_index([(field, 1)], **options)
                print(f"✅ Created index on: {field}")
            except Exception as e:
                print(f"⚠️ Index on {field} may already exist: {e}")
        
        # Update existing organizations to add org_short_name if missing
        print("\n🔄 Updating existing organizations...")
        
        existing_orgs = orgs_collection.find({"org_short_name": {"$exists": False}})
        updated_count = 0
        
        for org in existing_orgs:
            org_name = org.get("org_name") or org.get("organization_id", f"org-{org['_id']}")
            org_short_name = slugify(org_name)
            
            # Ensure uniqueness
            counter = 1
            original_short_name = org_short_name
            while orgs_collection.find_one({"org_short_name": org_short_name}):
                org_short_name = f"{original_short_name}-{counter}"
                counter += 1
            
            orgs_collection.update_one(
                {"_id": org["_id"]},
                {
                    "$set": {
                        "org_short_name": org_short_name,
                        "is_system_org": False,
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            updated_count += 1
            print(f"✅ Updated org: {org_name} -> {org_short_name}")
        
        print(f"\n✅ Updated {updated_count} existing organizations")
        
        # Display all organizations
        print("\n📊 Current Organizations:")
        all_orgs = orgs_collection.find({})
        for org in all_orgs:
            print(f"  - {org['org_name']:30s} | {org['org_short_name']:30s} | System Org: {org.get('is_system_org', False)}")
        
        client.close()
        print("\n🎉 Organization schema update completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error updating organization schema: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = update_organizations_schema()
    sys.exit(0 if success else 1)
