#!/usr/bin/env python3
"""
Script to download complete SBI land template from MongoDB
"""

import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
import json
from bson import ObjectId

# Custom JSON encoder to handle ObjectId
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

# Load environment variables
load_dotenv('/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend/.env')

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    print("❌ MONGODB_URI environment variable not found")
    sys.exit(1)

def download_template():
    """Download complete SBI land property template"""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_URI, tlsAllowInvalidCertificates=True)
        db = client.shared_resources
        
        print("🔍 Downloading SBI land property template...")
        
        # Get the complete document
        doc = db.sbi_land_property_details.find_one({})
        
        if not doc:
            print("❌ No document found")
            return
        
        # Save to file
        output_file = "sbi_land_template_complete.json"
        with open(output_file, 'w') as f:
            json.dump(doc, f, indent=2, cls=MongoJSONEncoder)
        
        print(f"✅ Template saved to: {output_file}")
        print(f"📊 File size: {os.path.getsize(output_file)} bytes")
        
        # Print summary
        print("\n=== TEMPLATE SUMMARY ===")
        print(f"Collection keys: {list(doc.keys())}")
        print(f"Total fields: {len(doc.get('fields', []))}")
        print(f"Total tabs: {len(doc.get('templateMetadata', {}).get('tabs', []))}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    download_template()
