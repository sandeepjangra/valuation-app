#!/usr/bin/env python3
"""
MongoDB Collection Cleanup and Status Check Script
"""

import os
import sys
import ssl
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_mongodb_connection():
    """Get MongoDB connection using Atlas connection string"""
    try:
        connection_string = os.getenv("MONGODB_URI")
        if not connection_string:
            print("❌ MONGODB_URI environment variable not found")
            return None
        
        client = MongoClient(
            connection_string,
            serverSelectionTimeoutMS=5000,
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True
        )
        
        # Test the connection
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas!")
        
        db_name = os.getenv("MONGODB_DB_NAME", "valuation_app_prod")
        db = client[db_name]
        return db
        
    except ConnectionFailure as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def check_collections_status():
    """Check the status of all collections"""
    print("🔍 Checking MongoDB Collections Status...")
    
    db = get_mongodb_connection()
    if db is None:
        return False
    
    try:
        # Get all collections
        collections = db.list_collection_names()
        print(f"📚 Found {len(collections)} collections:")
        
        for collection_name in collections:
            collection = db[collection_name]
            count = collection.count_documents({})
            print(f"   📁 {collection_name}: {count} documents")
            
            # Show sample documents for our target collections
            if collection_name in ['banks', 'common_form_fields'] and count > 0:
                sample_doc = collection.find_one({})
                if sample_doc:
                    print(f"      📄 Sample document keys: {list(sample_doc.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking collections: {e}")
        return False

def cleanup_banks_collection():
    """Clean up banks collection"""
    print("\n🧹 Cleaning up banks collection...")
    
    db = get_mongodb_connection()
    if db is None:
        return False
    
    try:
        banks_collection = db['banks']
        
        # Drop the collection to start fresh
        banks_collection.drop()
        print("✅ Dropped existing banks collection")
        
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning up banks collection: {e}")
        return False

def cleanup_common_fields_collection():
    """Clean up common fields collection"""
    print("\n🧹 Cleaning up common_form_fields collection...")
    
    db = get_mongodb_connection()
    if db is None:
        return False
    
    try:
        fields_collection = db['common_form_fields']
        
        # Drop the collection to start fresh
        fields_collection.drop()
        print("✅ Dropped existing common_form_fields collection")
        
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning up common fields collection: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧹 MongoDB Collections Cleanup & Status Check")
    print("=" * 60)
    
    # Check current status
    check_collections_status()
    
    # Ask user if they want to clean up
    print("\n" + "=" * 60)
    response = input("Do you want to clean up and start fresh? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        print("\n🚀 Starting cleanup...")
        
        # Clean up collections
        cleanup_banks_collection()
        cleanup_common_fields_collection()
        
        print("\n✅ Cleanup complete! You can now run the setup scripts.")
    else:
        print("\n⏭️ Skipping cleanup. Collections remain as they are.")
    
    print("\nNext steps:")
    print("1. Run: python scripts/database/setup_banks_collection.py")
    print("2. Run: python scripts/database/setup_common_fields_collection.py")