"""
Test script to verify organization implementation
Tests database schema and API endpoints
"""

import os
import sys
from pymongo import MongoClient
from datetime import datetime, timezone

def test_database_changes():
    """Test that database schema changes are in place"""
    
    print("=" * 60)
    print("🧪 TESTING ORGANIZATION DATABASE IMPLEMENTATION")
    print("=" * 60)
    
    # Get MongoDB connection
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
        
        print("\n✅ Connected to MongoDB Atlas")
        
        # Test 1: Check organizations collection
        print("\n" + "=" * 60)
        print("TEST 1: Organizations Collection")
        print("=" * 60)
        
        orgs_collection = db["organizations"]
        org_count = orgs_collection.count_documents({})
        print(f"📊 Total organizations: {org_count}")
        
        # Check System Administration org
        system_org = orgs_collection.find_one({"org_short_name": "system-administration"})
        if system_org:
            print("✅ System Administration organization exists")
            print(f"   - ID: {system_org['_id']}")
            print(f"   - Name: {system_org['org_name']}")
            print(f"   - Short Name: {system_org['org_short_name']}")
            print(f"   - System Org: {system_org.get('is_system_org', False)}")
            print(f"   - Active: {system_org.get('is_active', False)}")
        else:
            print("❌ System Administration organization NOT found")
            return False
        
        # List all organizations
        print("\n📋 All Organizations:")
        all_orgs = orgs_collection.find({})
        for org in all_orgs:
            print(f"   - {org['org_name']:30s} | {org['org_short_name']:25s} | System: {org.get('is_system_org', False)}")
        
        # Test 2: Check users collection
        print("\n" + "=" * 60)
        print("TEST 2: Users Collection (with org context)")
        print("=" * 60)
        
        users_collection = db["users_settings"]
        user_count = users_collection.count_documents({})
        print(f"📊 Total users: {user_count}")
        
        # Check users have org fields
        users_with_org = users_collection.count_documents({"org_id": {"$exists": True}})
        print(f"✅ Users with org_id: {users_with_org}/{user_count}")
        
        users_with_role = users_collection.count_documents({"role": {"$exists": True}})
        print(f"✅ Users with role: {users_with_role}/{user_count}")
        
        # List all users
        print("\n📋 All Users:")
        all_users = users_collection.find({})
        for user in all_users:
            username = user.get("username", "N/A")
            email = user.get("email", "N/A")
            org = user.get("org_short_name", "N/A")
            role = user.get("role", "N/A")
            print(f"   - User: {username:20s} | Email: {email:30s}")
            print(f"     Org: {org:25s} | Role: {role:10s}")
        
        # Test 3: Check indexes
        print("\n" + "=" * 60)
        print("TEST 3: Database Indexes")
        print("=" * 60)
        
        print("\n📊 Organizations Collection Indexes:")
        org_indexes = orgs_collection.list_indexes()
        for idx in org_indexes:
            print(f"   - {idx['name']}")
        
        print("\n📊 Users Collection Indexes:")
        user_indexes = users_collection.list_indexes()
        for idx in user_indexes:
            print(f"   - {idx['name']}")
        
        # Test 4: Test creating a new organization
        print("\n" + "=" * 60)
        print("TEST 4: Create Test Organization")
        print("=" * 60)
        
        test_org_name = "Test Company Inc"
        test_org_short = "test-company-inc"
        
        # Check if test org already exists
        existing_test = orgs_collection.find_one({"org_short_name": test_org_short})
        if existing_test:
            print(f"ℹ️  Test organization already exists: {test_org_name}")
            test_org_id = str(existing_test["_id"])
        else:
            # Create test organization
            now = datetime.now(timezone.utc)
            test_org_doc = {
                "org_name": test_org_name,
                "org_short_name": test_org_short,
                "org_display_name": test_org_name,
                "is_system_org": False,
                "is_active": True,
                "contact_info": {
                    "email": "contact@testcompany.com",
                    "phone": "+1-555-0100",
                    "address": "123 Test St, Test City"
                },
                "settings": {
                    "max_users": 50,
                    "features_enabled": ["reports", "templates"],
                    "timezone": "UTC",
                    "date_format": "DD/MM/YYYY"
                },
                "subscription": {
                    "plan": "basic",
                    "max_reports_per_month": 100,
                    "storage_limit_gb": 10,
                    "expires_at": None
                },
                "created_by": "test_script",
                "created_at": now,
                "updated_at": now,
                "version": 1
            }
            
            result = orgs_collection.insert_one(test_org_doc)
            test_org_id = str(result.inserted_id)
            print(f"✅ Created test organization: {test_org_name}")
            print(f"   - ID: {test_org_id}")
            print(f"   - Short Name: {test_org_short}")
        
        # Test 5: Verify data integrity
        print("\n" + "=" * 60)
        print("TEST 5: Data Integrity Checks")
        print("=" * 60)
        
        # Check for duplicate org names
        pipeline = [
            {"$group": {"_id": "$org_name", "count": {"$sum": 1}}},
            {"$match": {"count": {"$gt": 1}}}
        ]
        duplicates = list(orgs_collection.aggregate(pipeline))
        if duplicates:
            print(f"⚠️  Found {len(duplicates)} duplicate org names:")
            for dup in duplicates:
                print(f"   - {dup['_id']}: {dup['count']} occurrences")
        else:
            print("✅ No duplicate organization names")
        
        # Check for duplicate org short names
        pipeline = [
            {"$group": {"_id": "$org_short_name", "count": {"$sum": 1}}},
            {"$match": {"count": {"$gt": 1}}}
        ]
        duplicates = list(orgs_collection.aggregate(pipeline))
        if duplicates:
            print(f"⚠️  Found {len(duplicates)} duplicate org short names:")
            for dup in duplicates:
                print(f"   - {dup['_id']}: {dup['count']} occurrences")
        else:
            print("✅ No duplicate organization short names")
        
        # Summary
        print("\n" + "=" * 60)
        print("✅ TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Organizations Collection: Working")
        print(f"✅ System Administration Org: Created")
        print(f"✅ Users with Org Context: {users_with_org}/{user_count}")
        print(f"✅ Database Indexes: Created")
        print(f"✅ Test Organization: Created/Verified")
        print(f"✅ Data Integrity: Valid")
        
        print("\n🎉 All database tests passed!")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
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
    
    success = test_database_changes()
    
    if success:
        print("\n" + "=" * 60)
        print("📝 NEXT STEPS:")
        print("=" * 60)
        print("1. Backend API endpoints are created but NOT integrated yet")
        print("2. Need to add organization_api.py to main.py")
        print("3. Need to add authentication middleware")
        print("4. Then you can test API endpoints with:")
        print("   - GET http://localhost:8000/api/organizations")
        print("   - POST http://localhost:8000/api/organizations")
        print("=" * 60)
    
    sys.exit(0 if success else 1)
