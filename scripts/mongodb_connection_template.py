#!/usr/bin/env python3
"""
Template for MongoDB connection using environment variables
Use this template for any scripts that need to connect to MongoDB
"""

import os
from pymongo import MongoClient

def get_mongodb_connection():
    """
    Get MongoDB connection using environment variable
    Returns MongoClient instance or None if connection fails
    """
    mongodb_uri = os.getenv("MONGODB_URI")
    
    if not mongodb_uri:
        print("❌ MONGODB_URI environment variable not found")
        print("💡 Set it with: export MONGODB_URI='mongodb+srv://user:pass@cluster.mongodb.net/db'")
        return None
    
    try:
        # Connect to MongoDB Atlas (use tlsAllowInvalidCertificates=True if needed for development)
        client = MongoClient(mongodb_uri, tlsAllowInvalidCertificates=True)
        
        # Test the connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful")
        
        return client
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return None

def main():
    """Example usage"""
    client = get_mongodb_connection()
    
    if client:
        try:
            # List available databases
            db_list = client.list_database_names()
            print(f"📚 Available databases: {db_list}")
            
            # Example: Access a specific database
            db = client.your_database_name
            collections = db.list_collection_names()
            print(f"📁 Collections in database: {collections}")
            
        except Exception as e:
            print(f"❌ Error accessing database: {e}")
        finally:
            client.close()
            print("🔌 MongoDB connection closed")

if __name__ == "__main__":
    main()