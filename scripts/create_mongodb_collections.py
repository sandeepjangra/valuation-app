#!/usr/bin/env python3
"""
Create property details collections in MongoDB Atlas cluster
Connects to ValuationReportCluster/valuation_admin and creates all required collections
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from bson import ObjectId

# Add parent directory to path to import backend modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

class MongoDBCollectionCreator:
    """Create property details collections in MongoDB Atlas"""
    
    def __init__(self):
        self.connection_string = os.getenv("MONGODB_URI")
        self.admin_db_name = os.getenv("MONGODB_ADMIN_DB_NAME", "valuation_admin")
        
        if not self.connection_string:
            raise ValueError("MONGODB_URI environment variable is required")
        
        self.client = None
        self.db = None
        
    async def connect(self):
        """Connect to MongoDB Atlas"""
        try:
            print("🔗 Connecting to MongoDB Atlas...")
            print(f"📋 Database: {self.admin_db_name}")
            
            # Create client with SSL settings
            self.client = AsyncIOMotorClient(
                self.connection_string,
                serverSelectionTimeoutMS=30000,
                connectTimeoutMS=30000,
                socketTimeoutMS=30000,
                maxPoolSize=10,
                minPoolSize=1,
                retryWrites=True,
                retryReads=True,
                tlsAllowInvalidCertificates=True
            )
            
            # Test connection
            await asyncio.wait_for(self.client.admin.command('ping'), timeout=15.0)
            
            # Connect to admin database
            self.db = self.client[self.admin_db_name]
            
            print("✅ Connected to MongoDB Atlas successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    async def create_collection_from_file(self, collection_name, file_path):
        """Create a collection from JSON file data"""
        try:
            print(f"📄 Reading {file_path}...")
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            documents = data.get('documents', [])
            if not documents:
                print(f"⚠️  No documents found in {file_path}")
                return False
            
            # Get collection
            collection = self.db[collection_name]
            
            # Clear existing documents
            await collection.delete_many({})
            print(f"🗑️  Cleared existing {collection_name} collection")
            
            # Convert string IDs to ObjectIds and insert documents
            for doc in documents:
                if '_id' in doc and isinstance(doc['_id'], str):
                    doc['_id'] = ObjectId(doc['_id'])
            
            # Insert documents
            result = await collection.insert_many(documents)
            print(f"✅ Created {len(result.inserted_ids)} documents in {collection_name}")
            
            # Create indexes if needed
            await self.create_indexes(collection, collection_name)
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating {collection_name}: {e}")
            return False
    
    async def create_indexes(self, collection, collection_name):
        """Create appropriate indexes for the collection"""
        try:
            # Common indexes for all property collections
            indexes = [
                [("bankCode", 1)],
                [("propertyType", 1)],
                [("templateCategory", 1)],
                [("isActive", 1)],
                [("bankCode", 1), ("propertyType", 1), ("templateCategory", 1)]
            ]
            
            for index_spec in indexes:
                await collection.create_index(index_spec)
            
            print(f"📚 Created indexes for {collection_name}")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not create indexes for {collection_name}: {e}")
    
    async def create_all_collections(self):
        """Create all property details collections"""
        
        collections_to_create = [
            {
                "name": "sbi_apartment_property_details",
                "file": "/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend/data/sbi/apartment/sbi_apartment_property_details.json"
            },
            {
                "name": "ubi_land_property_details", 
                "file": "/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend/data/ubi/land/ubi_land_property_details.json"
            },
            {
                "name": "pnb_all_property_details",
                "file": "/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend/data/pnb/pnb_all_property_details.json"
            },
            {
                "name": "hdfc_all_property_details",
                "file": "/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend/data/hdfc/hdfc_all_property_details.json"
            },
            {
                "name": "uco_all_property_details",
                "file": "/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend/data/uco/uco_all_property_details.json"
            },
            {
                "name": "cbi_all_property_details",
                "file": "/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend/data/cbi/cbi_all_property_details.json"
            }
        ]
        
        success_count = 0
        total_count = len(collections_to_create)
        
        for collection_info in collections_to_create:
            collection_name = collection_info["name"]
            file_path = collection_info["file"]
            
            if not os.path.exists(file_path):
                print(f"⚠️  File not found: {file_path}")
                continue
            
            success = await self.create_collection_from_file(collection_name, file_path)
            if success:
                success_count += 1
        
        print(f"\n🎉 Successfully created {success_count}/{total_count} collections!")
        return success_count == total_count
    
    async def verify_collections(self):
        """Verify that collections were created successfully"""
        try:
            print("\n🔍 Verifying created collections...")
            
            collections = await self.db.list_collection_names()
            property_collections = [name for name in collections if 'property_details' in name]
            
            print(f"📊 Found {len(property_collections)} property collections:")
            for collection_name in property_collections:
                count = await self.db[collection_name].count_documents({})
                print(f"   • {collection_name}: {count} documents")
            
            return True
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("🔌 Disconnected from MongoDB Atlas")

async def main():
    """Main function to create all collections"""
    creator = MongoDBCollectionCreator()
    
    try:
        # Connect to MongoDB
        if not await creator.connect():
            sys.exit(1)
        
        # Create all collections
        success = await creator.create_all_collections()
        
        if success:
            # Verify collections
            await creator.verify_collections()
            print("\n✅ All collections created successfully in MongoDB Atlas!")
        else:
            print("\n❌ Some collections failed to create")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Script failed: {e}")
        sys.exit(1)
    finally:
        await creator.close()

if __name__ == "__main__":
    asyncio.run(main())