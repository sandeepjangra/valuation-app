#!/usr/bin/env python3
"""
Simple MongoDB Atlas Connection Test with SSL handling
"""

import asyncio
import ssl
import certifi
from motor.motor_asyncio import AsyncIOMotorClient

async def test_connection():
    """Test MongoDB Atlas connection with proper SSL handling"""
    
    connection_string = "mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreportcluster.5ixm1s7.mongodb.net/valuation_app_prod?retryWrites=true&w=majority&appName=ValuationReportCluster"
    
    print("🔗 Testing MongoDB Atlas Connection...")
    print(f"📋 Cluster: valuationreportcluster.5ixm1s7.mongodb.net")
    print(f"👤 User: app_user")
    
    try:
        # Create client with proper options
        client = AsyncIOMotorClient(
            connection_string,
            serverSelectionTimeoutMS=10000
        )
        
        # Test connection
        print("   🔄 Attempting connection...")
        await client.admin.command('ping')
        print("   ✅ Connection successful!")
        
        # Get database
        database = client["valuation_app_prod"]
        
        # Test basic operation
        print("   🔄 Testing database operations...")
        result = await database.test_collection.insert_one({"test": "Hello MongoDB Atlas!", "success": True})
        print(f"   ✅ Insert test successful: {result.inserted_id}")
        
        # Clean up test document
        await database.test_collection.delete_one({"_id": result.inserted_id})
        print("   🧹 Test document cleaned up")
        
        # Get server info
        server_info = await client.server_info()
        print(f"   📊 MongoDB Version: {server_info.get('version', 'Unknown')}")
        
        # Close connection
        client.close()
        
        print("\n🎉 SUCCESS! Your MongoDB Atlas cluster is ready!")
        print("✅ Connection established")
        print("✅ Authentication successful") 
        print("✅ Database operations working")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        print("\n💡 Common solutions:")
        print("   1. Check your IP is whitelisted (0.0.0.0/0)")
        print("   2. Verify username/password are correct")
        print("   3. Ensure cluster is fully deployed")
        print("   4. Check if your network blocks MongoDB ports")
        
        return False

async def main():
    print("🧪 MongoDB Atlas Connection Test\n")
    success = await test_connection()
    
    if success:
        print("\n📋 Next steps:")
        print("1. ✅ .env file is configured")
        print("2. 🔄 Run database setup script")
        print("3. 🔄 Start building your application")
    else:
        print("\n⚠️  Please resolve the connection issues above")

if __name__ == "__main__":
    asyncio.run(main())