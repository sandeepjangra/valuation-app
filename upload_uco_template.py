#!/usr/bin/env python3
"""
Upload UCO Land Template to MongoDB
This script uploads the uco_land_property_details.json file to MongoDB Atlas
"""

import json
import sys
import os
from pymongo import MongoClient
import asyncio

# Add the backend directory to the path to import database modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def upload_uco_template():
    try:
        # Read the UCO template JSON file
        with open('backend/data/uco/uco_land_property_details.json', 'r') as f:
            uco_template_data = json.load(f)
        
        print(f"📁 Loaded UCO template data from JSON file")
        print(f"   Template ID: {uco_template_data.get('templateMetadata', {}).get('templateId')}")
        print(f"   Total Documents: {len(uco_template_data.get('documents', []))}")
        
        # Get MongoDB connection string
        mongodb_uri = os.getenv('MONGODB_URI')
        if not mongodb_uri:
            raise Exception("MONGODB_URI environment variable not set")
        
        # Connect to MongoDB
        client = MongoClient(mongodb_uri)
        db = client['valuation_admin']
        collection = db['uco_land_property_details']
        
        print(f"🔗 Connected to MongoDB Atlas")
        
        # Check if collection already exists and has data
        existing_count = collection.count_documents({})
        if existing_count > 0:
            print(f"⚠️  Collection already has {existing_count} documents")
            response = input("Do you want to replace existing data? (y/N): ")
            if response.lower() != 'y':
                print("❌ Upload cancelled")
                return
            
            # Clear existing data
            collection.delete_many({})
            print(f"🗑️  Cleared existing data")
        
        # Insert the UCO template data
        result = collection.insert_one(uco_template_data)
        
        if result.inserted_id:
            print(f"✅ Successfully uploaded UCO template to MongoDB")
            print(f"   Inserted ID: {result.inserted_id}")
            print(f"   Collection: valuation_admin.uco_land_property_details")
            
            # Verify the upload
            verification = collection.find_one({"_id": result.inserted_id})
            if verification:
                tab_count = len(verification.get('templateMetadata', {}).get('tabs', []))
                doc_count = len(verification.get('documents', []))
                print(f"✅ Verification successful:")
                print(f"   - {tab_count} tabs defined")
                print(f"   - {doc_count} documents uploaded")
                
                # Print tab structure
                print(f"\n📋 Tab Structure:")
                for tab in verification.get('templateMetadata', {}).get('tabs', []):
                    has_sections = "✓" if tab.get('hasSections') else "✗"
                    print(f"   {tab.get('sortOrder', 0)}. {tab.get('tabName')} (sections: {has_sections})")
                    print(f"      Source: {tab.get('documentSource')}")
                
        else:
            print(f"❌ Failed to upload UCO template")
            
    except FileNotFoundError:
        print(f"❌ UCO template file not found: backend/data/uco/uco_land_property_details.json")
    except Exception as e:
        print(f"❌ Error uploading UCO template: {str(e)}")
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    print("🚀 UCO Land Template Upload Script")
    print("=" * 50)
    asyncio.run(upload_uco_template())