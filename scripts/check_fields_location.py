#!/usr/bin/env python3
"""
Script to check where fields are stored in the template
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

def check_fields_location():
    """Check where fields are actually stored"""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_URI, tlsAllowInvalidCertificates=True)
        db = client.shared_resources
        
        print("🔍 Checking where fields are stored...")
        
        # Get the document
        doc = db.sbi_land_property_details.find_one({})
        
        if not doc:
            print("❌ No document found")
            return
        
        # Check top-level fields
        if "fields" in doc:
            print(f"\n✅ Found top-level 'fields' array with {len(doc['fields'])} fields")
            print("\n=== FIRST 3 FIELDS ===")
            for i, field in enumerate(doc['fields'][:3]):
                print(f"\nField {i+1}:")
                print(f"  Field ID: {field.get('fieldId')}")
                print(f"  UI Name: {field.get('uiDisplayName')}")
                print(f"  Type: {field.get('fieldType')}")
                print(f"  Section: {field.get('sectionId', 'N/A')}")
                print(f"  Tab: {field.get('tabId', 'N/A')}")
        
        # Check if fields have section/tab mappings
        if "fields" in doc:
            print("\n=== FIELD DISTRIBUTION BY TAB/SECTION ===")
            fields_by_tab = {}
            for field in doc['fields']:
                tab_id = field.get('tabId', 'unknown')
                section_id = field.get('sectionId', 'no_section')
                
                if tab_id not in fields_by_tab:
                    fields_by_tab[tab_id] = {}
                if section_id not in fields_by_tab[tab_id]:
                    fields_by_tab[tab_id][section_id] = 0
                fields_by_tab[tab_id][section_id] += 1
            
            for tab_id, sections in fields_by_tab.items():
                print(f"\nTab: {tab_id}")
                for section_id, count in sections.items():
                    print(f"  {section_id}: {count} fields")
        
        client.close()
        print("\n✅ Check complete")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_fields_location()
