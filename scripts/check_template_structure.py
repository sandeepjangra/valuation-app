#!/usr/bin/env python3
"""
Script to check SBI land property template structure
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

def check_template_structure():
    """Check SBI land property template structure"""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_URI, tlsAllowInvalidCertificates=True)
        db = client.shared_resources
        
        print("🔍 Checking SBI land property template structure...")
        
        # Get the document
        doc = db.sbi_land_property_details.find_one({})
        
        if not doc:
            print("❌ No document found")
            return
            
        print("\n=== DOCUMENT KEYS ===")
        print(list(doc.keys()))
        
        if "templateMetadata" in doc:
            print("\n=== TEMPLATE METADATA ===")
            metadata = doc["templateMetadata"]
            
            if "tabs" in metadata:
                print(f"Tabs count: {len(metadata['tabs'])}")
                
                print("\n=== FIRST TAB ===")
                tab = metadata["tabs"][0]
                print(f"Tab ID: {tab.get('tabId')}")
                print(f"Tab Name: {tab.get('tabName')}")
                print(f"Has Sections: {tab.get('hasSections')}")
                print(f"Sections type: {type(tab.get('sections'))}")
                print(f"Sections count: {len(tab.get('sections', []))}")
                
                if tab.get("sections"):
                    print("\n=== FIRST SECTION ===")
                    section = tab["sections"][0]
                    print(f"Section ID: {section.get('sectionId')}")
                    print(f"Section Name: {section.get('sectionName')}")
                    print(f"Fields type: {type(section.get('fields'))}")
                    
                    if section.get("fields") is not None:
                        print(f"Fields count: {len(section.get('fields', []))}")
                        
                        if section.get("fields"):
                            print("\n=== FIRST FIELD IN SECTION ===")
                            field = section["fields"][0]
                            print(json.dumps(field, indent=2, default=str))
                    else:
                        print("⚠️ Fields is None/null")
                        
                print("\n=== CHECKING ALL SECTIONS FOR FIELDS ===")
                for i, tab in enumerate(metadata["tabs"]):
                    print(f"\nTab {i+1}: {tab.get('tabName')}")
                    if tab.get("sections"):
                        for j, section in enumerate(tab["sections"]):
                            fields_count = len(section.get("fields", [])) if section.get("fields") else 0
                            print(f"  Section {j+1}: {section.get('sectionName')} - Fields: {fields_count if fields_count > 0 else 'None/null'}")
        
        client.close()
        print("\n✅ Check complete")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_template_structure()
