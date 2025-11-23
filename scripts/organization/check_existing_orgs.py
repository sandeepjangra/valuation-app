"""
Check current organization setup in the database
"""

import os
import sys
from pymongo import MongoClient
from bson import ObjectId
import json

def check_current_orgs():
    """Check all existing organizations in database"""
    
    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        print("❌ MONGODB_URI not set")
        return False
    
    try:
        # Connect to MongoDB
        client = MongoClient(
            mongodb_uri,
            serverSelectionTimeoutMS=5000,
            tlsAllowInvalidCertificates=True
        )
        db = client["valuation_001"]
        
        print("=" * 80)
        print("🔍 CHECKING EXISTING ORGANIZATIONS")
        print("=" * 80)
        
        # Check organizations collection
        orgs_collection = db["organizations"]
        
        print("\n📊 Total organizations in database:", orgs_collection.count_documents({}))
        print("\n" + "=" * 80)
        
        # List all organizations with full details
        all_orgs = orgs_collection.find({})
        
        for idx, org in enumerate(all_orgs, 1):
            print(f"\n{'=' * 80}")
            print(f"ORGANIZATION #{idx}")
            print(f"{'=' * 80}")
            
            # Convert ObjectId to string for display
            org_copy = dict(org)
            org_copy['_id'] = str(org_copy['_id'])
            
            # Pretty print the organization
            for key, value in org_copy.items():
                if key in ['created_at', 'updated_at']:
                    print(f"{key:25s}: {value}")
                elif isinstance(value, dict):
                    print(f"{key:25s}:")
                    for sub_key, sub_value in value.items():
                        print(f"  {sub_key:23s}: {sub_value}")
                else:
                    print(f"{key:25s}: {value}")
        
        # Check if there are orgs without org_short_name
        print("\n" + "=" * 80)
        print("🔍 CHECKING FOR MISSING FIELDS")
        print("=" * 80)
        
        missing_short_name = orgs_collection.count_documents({"org_short_name": {"$exists": False}})
        missing_is_system = orgs_collection.count_documents({"is_system_org": {"$exists": False}})
        
        print(f"\nOrganizations missing 'org_short_name': {missing_short_name}")
        print(f"Organizations missing 'is_system_org': {missing_is_system}")
        
        if missing_short_name > 0:
            print("\n⚠️  Organizations without org_short_name:")
            orgs_no_short = orgs_collection.find({"org_short_name": {"$exists": False}})
            for org in orgs_no_short:
                print(f"   - ID: {org['_id']}")
                print(f"     Name: {org.get('name') or org.get('org_name') or org.get('organization_id', 'UNKNOWN')}")
        
        # Check users collection
        print("\n" + "=" * 80)
        print("🔍 CHECKING USERS COLLECTION")
        print("=" * 80)
        
        users_collection = db["users_settings"]
        total_users = users_collection.count_documents({})
        
        print(f"\n📊 Total users: {total_users}")
        
        # Group users by organization
        pipeline = [
            {"$group": {
                "_id": "$org_id",
                "org_short_name": {"$first": "$org_short_name"},
                "count": {"$sum": 1},
                "roles": {"$push": "$role"}
            }}
        ]
        
        user_groups = list(users_collection.aggregate(pipeline))
        
        if user_groups:
            print("\n📊 Users by Organization:")
            for group in user_groups:
                org_id = group['_id'] or 'NULL'
                org_name = group.get('org_short_name', 'UNKNOWN')
                count = group['count']
                roles = group.get('roles', [])
                role_counts = {}
                for role in roles:
                    role_counts[role] = role_counts.get(role, 0) + 1
                
                print(f"\n   Organization: {org_name}")
                print(f"   - Org ID: {org_id}")
                print(f"   - Total Users: {count}")
                print(f"   - Roles: {role_counts}")
        
        # List all users
        print("\n" + "=" * 80)
        print("📋 ALL USERS DETAILS")
        print("=" * 80)
        
        all_users = users_collection.find({})
        for idx, user in enumerate(all_users, 1):
            print(f"\nUser #{idx}:")
            print(f"   - ID: {user.get('_id')}")
            print(f"   - Username: {user.get('username', 'N/A')}")
            print(f"   - Email: {user.get('email', 'N/A')}")
            print(f"   - Org ID: {user.get('org_id', 'N/A')}")
            print(f"   - Org Short Name: {user.get('org_short_name', 'N/A')}")
            print(f"   - Role: {user.get('role', 'N/A')}")
            print(f"   - Is Active: {user.get('is_active', 'N/A')}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Load environment variables
    from pathlib import Path
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).parent / '.env'
        if not env_path.exists():
            env_path = Path(__file__).parent / 'backend' / '.env'
        load_dotenv(dotenv_path=env_path)
    except:
        pass
    
    check_current_orgs()
