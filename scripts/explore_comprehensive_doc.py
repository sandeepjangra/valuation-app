#!/usr/bin/env python3
"""
Script to explore the comprehensive document structure
and find where common fields are stored.
"""

import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv('/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend/.env')

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    print("❌ MONGODB_URI environment variable not found")
    sys.exit(1)

def explore_comprehensive_doc():
    """Explore the comprehensive document structure"""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_URI, tlsAllowInvalidCertificates=True)
        db = client.valuation_admin
        collection = db.banks
        
        print("🔍 Searching for comprehensive document...")
        
        # Find the comprehensive document
        doc = collection.find_one({"_id": "all_banks_comprehensive_v4"})
        if not doc:
            print("❌ Comprehensive document not found")
            return False
        
        print("✅ Found comprehensive document")
        print(f"📋 Top-level keys: {list(doc.keys())}")
        
        # Look for common fields in different locations
        common_fields_locations = [
            'common_form_fields',
            'commonFields', 
            'common_fields',
            'fields'
        ]
        
        found_common_fields = False
        
        for location in common_fields_locations:
            if location in doc:
                print(f"\n🔍 Found {location}: {len(doc[location])} items")
                if len(doc[location]) > 0:
                    print(f"📋 First item structure: {list(doc[location][0].keys())}")
                    print(f"📋 First item: {json.dumps(doc[location][0], indent=2)}")
                    found_common_fields = True
                break
        
        if not found_common_fields:
            print("\n❌ No common fields found in expected locations")
            
            # Check if it's inside banks
            if 'banks' in doc and len(doc['banks']) > 0:
                first_bank = doc['banks'][0]
                print(f"\n🏦 First bank keys: {list(first_bank.keys())}")
                
                if 'templates' in first_bank and len(first_bank['templates']) > 0:
                    first_template = first_bank['templates'][0] 
                    print(f"📋 First template keys: {list(first_template.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    print("🔧 Exploring comprehensive document structure...")
    explore_comprehensive_doc()