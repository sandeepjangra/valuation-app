"""
Update Users Schema to include organization context
Adds org_id, org_short_name, and role fields to existing users
"""

import os
import sys
from datetime import datetime, timezone
from pymongo import MongoClient
from bson import ObjectId

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def update_users_schema():
    """Update users collection schema with organization context"""
    
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
            tlsAllowInvalidCertificates=True
        )
        db = client["val_app_config"]  # Central config database
        users_collection = db["users_settings"]
        orgs_collection = db["organizations"]
        
        print("✅ Connected to MongoDB Atlas")
        
        # Get System Administration org
        system_org = orgs_collection.find_one({"org_short_name": "system-administration"})
        if not system_org:
            print("❌ System Administration organization not found. Run update_org_schema.py first.")
            return False
        
        system_org_id = str(system_org["_id"])
        print(f"✅ Found System Administration org: {system_org_id}")
        
        # Create indexes
        print("\n📋 Creating indexes on users collection...")
        
        indexes = [
            ("email", {"unique": True}),
            ("username", {"unique": True}),
            ("org_id", {}),
            ("org_short_name", {}),
            ("role", {}),
            ("is_active", {}),
        ]
        
        for field, options in indexes:
            try:
                users_collection.create_index([(field, 1)], **options)
                print(f"✅ Created index on: {field}")
            except Exception as e:
                print(f"⚠️  Index on {field} may already exist: {e}")
        
        # Compound indexes
        try:
            users_collection.create_index([("org_id", 1), ("role", 1)], name="idx_org_role")
            print(f"✅ Created compound index: org_id + role")
        except Exception as e:
            print(f"⚠️  Compound index may already exist: {e}")
        
        # Update existing users
        print("\n🔄 Updating existing users...")
        
        existing_users = users_collection.find({})
        updated_count = 0
        
        for user in existing_users:
            # Check if user already has org context
            if "org_id" in user and "org_short_name" in user and "role" in user:
                continue
            
            # Assign to System Administration org by default
            # Set role based on username or email (admin users go to system org)
            username = user.get("username", "")
            email = user.get("email", "")
            
            # Determine role (default to admin for existing users in system org)
            if "admin" in username.lower() or "admin" in email.lower():
                role = "admin"
            else:
                role = "manager"  # Existing users get manager role
            
            update_doc = {
                "$set": {
                    "org_id": system_org_id,
                    "org_short_name": "system-administration",
                    "role": role,
                    "is_active": user.get("is_active", True),
                    "updated_at": datetime.now(timezone.utc)
                }
            }
            
            users_collection.update_one(
                {"_id": user["_id"]},
                update_doc
            )
            
            updated_count += 1
            print(f"✅ Updated user: {username or email} -> {role} @ system-administration")
        
        print(f"\n✅ Updated {updated_count} existing users")
        
        # Display all users
        print("\n📊 Current Users:")
        all_users = users_collection.find({})
        for user in all_users:
            username = user.get("username", "N/A")
            email = user.get("email", "N/A")
            org = user.get("org_short_name", "N/A")
            role = user.get("role", "N/A")
            print(f"  - {username:20s} | {email:30s} | {org:25s} | {role:10s}")
        
        client.close()
        print("\n🎉 Users schema update completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error updating users schema: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = update_users_schema()
    sys.exit(0 if success else 1)
