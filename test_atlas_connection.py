#!/usr/bin/env python3
"""
MongoDB Atlas Connection Test & Setup Script
Run this after getting your connection string from Atlas
"""

import asyncio
import os
import sys
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

class AtlasConnectionTester:
    def __init__(self, connection_string, database_name="valuation_app_prod"):
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.database = None

    async def test_connection(self):
        """Test basic connection to MongoDB Atlas"""
        print("🔗 Testing MongoDB Atlas connection...")
        
        try:
            self.client = AsyncIOMotorClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000
            )
            
            # Test ping
            await self.client.admin.command('ping')
            print("   ✅ Connection successful!")
            
            # Get database
            self.database = self.client[self.database_name]
            print(f"   ✅ Database '{self.database_name}' accessible")
            
            return True
            
        except ConnectionFailure as e:
            print(f"   ❌ Connection failed: {e}")
            return False
        except ServerSelectionTimeoutError as e:
            print(f"   ❌ Server selection timeout: {e}")
            print("   💡 Check your IP whitelist and credentials")
            return False
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            return False

    async def get_cluster_info(self):
        """Get information about the cluster"""
        print("\n📊 Getting cluster information...")
        
        try:
            # Get server info
            server_info = await self.client.server_info()
            print(f"   📋 MongoDB Version: {server_info.get('version', 'Unknown')}")
            
            # Get database stats
            stats = await self.database.command("dbStats")
            print(f"   📊 Database: {stats.get('db', 'Unknown')}")
            print(f"   📁 Collections: {stats.get('collections', 0)}")
            print(f"   💾 Data Size: {stats.get('dataSize', 0)} bytes")
            
            # List existing collections
            collection_names = await self.database.list_collection_names()
            if collection_names:
                print(f"   📚 Existing Collections: {', '.join(collection_names)}")
            else:
                print("   📚 No collections found (this is normal for new databases)")
                
            return True
            
        except Exception as e:
            print(f"   ❌ Error getting cluster info: {e}")
            return False

    async def test_operations(self):
        """Test basic CRUD operations"""
        print("\n🔧 Testing database operations...")
        
        try:
            # Test collection
            test_collection = self.database["connection_test"]
            
            # Insert test document
            test_doc = {
                "test": True,
                "timestamp": datetime.utcnow(),
                "message": "MongoDB Atlas connection test successful!"
            }
            
            result = await test_collection.insert_one(test_doc)
            print(f"   ✅ Insert test: Document ID {result.inserted_id}")
            
            # Read test document
            found_doc = await test_collection.find_one({"_id": result.inserted_id})
            if found_doc:
                print("   ✅ Read test: Document retrieved successfully")
            
            # Update test document
            update_result = await test_collection.update_one(
                {"_id": result.inserted_id},
                {"$set": {"updated": True}}
            )
            print(f"   ✅ Update test: {update_result.modified_count} document updated")
            
            # Delete test document
            delete_result = await test_collection.delete_one({"_id": result.inserted_id})
            print(f"   ✅ Delete test: {delete_result.deleted_count} document deleted")
            
            # Clean up test collection
            await test_collection.drop()
            print("   🧹 Test collection cleaned up")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error testing operations: {e}")
            return False

    async def close_connection(self):
        """Close the connection"""
        if self.client:
            self.client.close()
            print("\n🔒 Connection closed")

async def main():
    """Main function to run all tests"""
    print("🧪 MongoDB Atlas Connection & Operations Test\n")
    
    # Check if connection string is provided
    if len(sys.argv) < 2:
        print("❌ Please provide MongoDB Atlas connection string as argument")
        print("\nUsage:")
        print("   python test_atlas_connection.py 'mongodb+srv://user:pass@cluster.mongodb.net/db'")
        print("\nOr set MONGODB_URI environment variable")
        return False
    
    connection_string = sys.argv[1]
    
    # Validate connection string format
    if not connection_string.startswith("mongodb+srv://"):
        print("❌ Invalid connection string format. Should start with 'mongodb+srv://'")
        return False
    
    # Create tester
    tester = AtlasConnectionTester(connection_string)
    
    try:
        # Run tests
        print("🎯 Running comprehensive Atlas tests...\n")
        
        # Test 1: Basic Connection
        connection_ok = await tester.test_connection()
        if not connection_ok:
            print("\n💥 Connection test failed. Please check:")
            print("   1. Connection string is correct")
            print("   2. Username and password are correct")
            print("   3. Your IP is whitelisted in Atlas")
            print("   4. Database user has proper permissions")
            return False
        
        # Test 2: Cluster Information
        info_ok = await tester.get_cluster_info()
        
        # Test 3: CRUD Operations
        operations_ok = await tester.test_operations()
        
        # Summary
        print("\n" + "="*50)
        print("📊 TEST SUMMARY")
        print("="*50)
        print(f"Connection Test:    {'✅ PASS' if connection_ok else '❌ FAIL'}")
        print(f"Cluster Info:       {'✅ PASS' if info_ok else '❌ FAIL'}")
        print(f"CRUD Operations:    {'✅ PASS' if operations_ok else '❌ FAIL'}")
        print("="*50)
        
        if connection_ok and info_ok and operations_ok:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Your MongoDB Atlas cluster is ready for the Valuation Application!")
            print("\n📋 Next steps:")
            print("   1. Update your .env file with this connection string")
            print("   2. Run the database setup script")
            print("   3. Start building your application")
            return True
        else:
            print("\n⚠️  Some tests failed. Please resolve the issues above.")
            return False
            
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {e}")
        return False
    finally:
        await tester.close_connection()

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)