#!/usr/bin/env python3
"""
Fetch Complete SBI Land Template from MongoDB Atlas
This script searches all relevant collections to build the complete template
"""

import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

def connect_to_mongodb():
    """Connect to MongoDB Atlas"""
    mongo_uri = os.getenv('MONGODB_URI')
    if not mongo_uri:
        print("❌ MONGODB_URI not found in environment variables")
        sys.exit(1)
    
    try:
        client = MongoClient(mongo_uri)
        client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas")
        return client
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        sys.exit(1)

def main():
    print("🔍 Fetching Complete SBI Land Template Structure...")
    
    client = connect_to_mongodb()
    db = client['valuation_admin']
    
    # List all collections
    print("\n📋 All collections in valuation_admin:")
    collections = db.list_collection_names()
    for coll in sorted(collections):
        count = db[coll].count_documents({})
        print(f"   - {coll}: {count} documents")
    
    # Check for common fields collection
    print("\n🔍 Searching for common fields...")
    common_fields_collections = [c for c in collections if 'common' in c.lower() or 'field' in c.lower()]
    
    if common_fields_collections:
        print(f"   Found {len(common_fields_collections)} potential collections:")
        for coll in common_fields_collections:
            print(f"   - {coll}")
            # Show sample document keys
            sample = db[coll].find_one({})
            if sample:
                print(f"     Keys: {list(sample.keys())}")
    
    # Check for template definitions
    print("\n🔍 Searching for template definitions...")
    template_collections = [c for c in collections if 'template' in c.lower()]
    
    if template_collections:
        print(f"   Found {len(template_collections)} template collections:")
        for coll in template_collections:
            print(f"   - {coll}")
            sample = db[coll].find_one({})
            if sample:
                print(f"     Keys: {list(sample.keys())}")
                if 'templateId' in sample:
                    print(f"     TemplateId: {sample.get('templateId')}")
    
    # Check SBI Land specific collections in detail
    print("\n🔍 Detailed check of sbi_land_property_details...")
    sbi_land_doc = db['sbi_land_property_details'].find_one({})
    
    if sbi_land_doc:
        print(f"   Document keys: {list(sbi_land_doc.keys())}")
        print(f"   TemplateId: {sbi_land_doc.get('templateId')}")
        print(f"   TemplateName: {sbi_land_doc.get('templateName')}")
        print(f"   Has sections: {bool(sbi_land_doc.get('sections'))}")
        print(f"   Sections count: {len(sbi_land_doc.get('sections', []))}")
        print(f"   Direct fields count: {len(sbi_land_doc.get('fields', []))}")
        
        # Save full document
        output_file = 'sbi_land_property_details_full.json'
        with open(output_file, 'w') as f:
            json.dump(sbi_land_doc, f, indent=2, default=str)
        print(f"\n💾 Full document saved to: {output_file}")
    
    client.close()
    print("\n✅ Complete!")

if __name__ == "__main__":
    main()
