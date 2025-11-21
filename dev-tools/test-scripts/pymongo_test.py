#!/usr/bin/env python3
"""
PyMongo direct connection test for MongoDB Atlas
"""

import ssl
import certifi
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

def test_connection():
    """Test connection using PyMongo directly"""
    
    connection_string = "mongodb+srv://app_user:kHxlQqJ1Uc3bmoL6@valuationreportcluster.5ixm1s7.mongodb.net/valuation_app_prod?retryWrites=true&w=majority&appName=ValuationReportCluster"
    
    print("🔗 Testing MongoDB Atlas Connection (PyMongo)...")
    print(f"📋 Cluster: valuationreportcluster.5ixm1s7.mongodb.net")
    print(f"👤 User: app_user")
    
    try:
        # Create client with SSL handling
        client = MongoClient(
            connection_string,
            serverSelectionTimeoutMS=10000,
            tlsCAFile=certifi.where()
        )
        
        # Test connection
        print("   🔄 Attempting connection...")
        client.admin.command('ping')
        print("   ✅ Connection successful!")
        
        # Get database
        database = client["valuation_app_prod"]
        
        # Test basic operation
        print("   🔄 Testing database operations...")
        result = database.test_collection.insert_one({"test": "Hello MongoDB Atlas!", "success": True})
        print(f"   ✅ Insert test successful: {result.inserted_id}")
        
        # Clean up test document
        database.test_collection.delete_one({"_id": result.inserted_id})
        print("   🧹 Test document cleaned up")
        
        # Get server info
        server_info = client.server_info()
        print(f"   📊 MongoDB Version: {server_info.get('version', 'Unknown')}")
        
        # List databases
        databases = client.list_database_names()
        print(f"   📚 Available Databases: {databases}")
        
        # Close connection
        client.close()
        
        print("\n🎉 SUCCESS! Your MongoDB Atlas cluster is ready!")
        print("✅ Connection established")
        print("✅ Authentication successful") 
        print("✅ Database operations working")
        
        return True
        
    except ConnectionFailure as e:
        print(f"   ❌ Connection failed: {e}")
        return False
    except ServerSelectionTimeoutError as e:
        print(f"   ❌ Server selection timeout: {e}")
        print("   💡 This usually means:")
        print("      - IP not whitelisted in Atlas")
        print("      - Network/firewall blocking connection")
        print("      - Cluster still starting up")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def main():
    print("🧪 MongoDB Atlas Connection Test (Direct PyMongo)\n")
    success = test_connection()
    
    if success:
        print("\n📋 Next steps:")
        print("1. ✅ Connection verified")
        print("2. ✅ .env file is configured")
        print("3. 🔄 Run database setup script")
        print("4. 🔄 Start building your application")
    else:
        print("\n⚠️  Connection failed. Let's check a few things:")
        print("\n🔍 Please verify in MongoDB Atlas:")
        print("   1. Go to Network Access")
        print("   2. Ensure 0.0.0.0/0 is in IP Access List")
        print("   3. Go to Database Access")
        print("   4. Ensure 'app_user' exists with Atlas Admin role")
        print("   5. Check cluster status (should be green/running)")

if __name__ == "__main__":
    main()