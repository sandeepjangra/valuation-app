"""
Check organizations in valuation_admin database
"""

import os
import sys
from pymongo import MongoClient
from pprint import pprint

def check_valuation_admin_orgs():
    """Check organizations in valuation_admin database"""
    
    print("=" * 60)
    print("🔍 CHECKING VALUATION_ADMIN DATABASE")
    print("=" * 60)
    
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
        
        print("\n✅ Connected to MongoDB Atlas")
        
        # Check all databases
        print("\n📊 All Databases:")
        databases = client.list_database_names()
        for db_name in databases:
            print(f"   - {db_name}")
        
        # Check valuation_admin database
        if "valuation_admin" in databases:
            print("\n✅ valuation_admin database found")
            admin_db = client["valuation_admin"]
            
            # List all collections
            print("\n📋 Collections in valuation_admin:")
            collections = admin_db.list_collection_names()
            for coll_name in collections:
                count = admin_db[coll_name].count_documents({})
                print(f"   - {coll_name:30s} ({count} documents)")
            
            # Check if organizations collection exists
            if "organizations" in collections:
                print("\n" + "=" * 60)
                print("📊 ORGANIZATIONS COLLECTION (valuation_admin)")
                print("=" * 60)
                
                orgs_collection = admin_db["organizations"]
                org_count = orgs_collection.count_documents({})
                print(f"\n📊 Total organizations: {org_count}")
                
                # List all organizations with full details
                print("\n📋 All Organizations:")
                all_orgs = orgs_collection.find({})
                for i, org in enumerate(all_orgs, 1):
                    print(f"\n--- Organization {i} ---")
                    print(f"ID: {org.get('_id')}")
                    print(f"Organization ID: {org.get('organization_id', 'N/A')}")
                    print(f"Name: {org.get('name', 'N/A')}")
                    print(f"Status: {org.get('status', 'N/A')}")
                    print(f"Created At: {org.get('created_at', 'N/A')}")
                    print(f"Is Active: {org.get('isActive', 'N/A')}")
                    
                    # Check for contact info
                    if 'contact_info' in org:
                        print(f"Contact Email: {org['contact_info'].get('email', 'N/A')}")
                    
                    # Check for settings
                    if 'settings' in org:
                        print(f"Max Users: {org['settings'].get('max_users', 'N/A')}")
                        if 's3_prefix' in org['settings']:
                            print(f"S3 Prefix: {org['settings']['s3_prefix']}")
                    
                    print("\nFull Document:")
                    pprint(org, indent=2)
            else:
                print("\n❌ organizations collection NOT found in valuation_admin")
        else:
            print("\n❌ valuation_admin database NOT found")
        
        # Also check valuation_001 database
        if "valuation_001" in databases:
            print("\n" + "=" * 60)
            print("📊 VALUATION_001 DATABASE")
            print("=" * 60)
            
            v001_db = client["valuation_001"]
            
            print("\n📋 Collections in valuation_001:")
            collections = v001_db.list_collection_names()
            for coll_name in collections:
                count = v001_db[coll_name].count_documents({})
                print(f"   - {coll_name:30s} ({count} documents)")
            
            # Check organizations in valuation_001
            if "organizations" in collections:
                print("\n📊 Organizations in valuation_001:")
                orgs_collection = v001_db["organizations"]
                all_orgs = orgs_collection.find({})
                for org in all_orgs:
                    print(f"   - {org.get('org_name', 'N/A'):30s} | {org.get('org_short_name', 'N/A')}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    from pathlib import Path
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).parent / '.env'
        if not env_path.exists():
            env_path = Path(__file__).parent / 'backend' / '.env'
        load_dotenv(dotenv_path=env_path)
    except:
        pass
    
    check_valuation_admin_orgs()
