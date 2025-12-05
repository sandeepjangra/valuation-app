#!/usr/bin/env python3
"""
Script to migrate banks data from shared_resources to valuation_admin database
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Change to script directory and add backend to path
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
sys.path.append(os.path.join(script_dir, 'backend'))

from database.multi_db_manager import MultiDatabaseManager

async def main():
    """Migrate banks data from shared_resources to valuation_admin"""
    
    # Load environment variables from current directory
    env_path = os.path.join(script_dir, '.env')
    load_dotenv(env_path)
    
    if not os.getenv('MONGODB_URI'):
        print("❌ MONGODB_URI environment variable not found")
        return
    
    # Create database manager
    db_manager = MultiDatabaseManager()
    
    try:
        print("🔌 Connecting to MongoDB Atlas...")
        await db_manager.connect()
        
        # Get database connections
        shared_db = db_manager.get_database("shared")  # type: ignore
        admin_db = db_manager.get_database("admin")
        
        print("\n📊 Checking current state...")
        
        # Check what's in shared_resources.banks
        shared_banks_count = await shared_db.banks.count_documents({})
        print(f"📋 shared_resources.banks: {shared_banks_count} documents")
        
        if shared_banks_count > 0:
            # Get a sample document
            sample_shared = await shared_db.banks.find_one({})
            print(f"   Sample ID: {sample_shared.get('_id') if sample_shared else 'None'}")
            
        # Check what's in valuation_admin.banks  
        admin_banks_count = await admin_db.banks.count_documents({})
        print(f"📋 valuation_admin.banks: {admin_banks_count} documents")
        
        if admin_banks_count > 0:
            sample_admin = await admin_db.banks.find_one({})
            print(f"   Sample ID: {sample_admin.get('_id') if sample_admin else 'None'}")
        
        print("\n🔍 Looking for comprehensive banks document...")
        
        # Look for comprehensive document in shared
        comprehensive_in_shared = await shared_db.banks.find_one({"_id": {"$regex": ".*comprehensive.*"}})
        if comprehensive_in_shared:
            print(f"✅ Found comprehensive document in shared: {comprehensive_in_shared.get('_id')}")
        
        # Look for comprehensive document in admin
        comprehensive_in_admin = await admin_db.banks.find_one({"_id": {"$regex": ".*comprehensive.*"}})
        if comprehensive_in_admin:
            print(f"✅ Found comprehensive document in admin: {comprehensive_in_admin.get('_id')}")
        
        # Migration decision
        if comprehensive_in_shared and not comprehensive_in_admin:
            print(f"\n🚀 Migrating comprehensive document from shared to admin...")
            
            # Insert into admin database
            result = await admin_db.banks.insert_one(comprehensive_in_shared)
            print(f"✅ Inserted document with ID: {result.inserted_id}")
            
        elif comprehensive_in_shared and comprehensive_in_admin:
            print(f"\n⚠️  Comprehensive document exists in both databases")
            print(f"   Shared ID: {comprehensive_in_shared.get('_id')}")
            print(f"   Admin ID: {comprehensive_in_admin.get('_id')}")
            
        elif not comprehensive_in_shared:
            print(f"\n❌ No comprehensive document found in shared database")
            
            # Let's see all documents in shared
            print("📋 All documents in shared_resources.banks:")
            async for doc in shared_db.banks.find({}, {"_id": 1, "bankCode": 1}):
                print(f"   - ID: {doc.get('_id')}, Code: {doc.get('bankCode', 'N/A')}")
                
        else:
            print(f"\n✅ Comprehensive document already exists in admin database")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        await db_manager.disconnect()
        print("🔒 Disconnected from MongoDB")

if __name__ == "__main__":
    asyncio.run(main())