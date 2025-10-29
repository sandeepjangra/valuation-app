#!/usr/bin/env python3
"""
Fix ObjectId formats in JSON files
"""

import json
import os
import re
from bson import ObjectId

def fix_objectid_in_file(file_path):
    """Fix ObjectId format in a JSON file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Fix ObjectIds in documents
        for doc in data.get('documents', []):
            if '_id' in doc:
                old_id = doc['_id']
                if isinstance(old_id, str) and len(old_id) != 24:
                    # Generate a new valid ObjectId
                    doc['_id'] = str(ObjectId())
                    print(f"Fixed ID in {file_path}: {old_id} -> {doc['_id']}")
        
        # Write back to file
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Fixed ObjectIds in {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def main():
    """Fix ObjectIds in all collection files"""
    
    files_to_fix = [
        "/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend/data/ubi/land/ubi_land_property_details.json",
        "/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend/data/hdfc/hdfc_all_property_details.json",
        "/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend/data/uco/uco_all_property_details.json",
        "/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend/data/cbi/cbi_all_property_details.json"
    ]
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            fix_objectid_in_file(file_path)
        else:
            print(f"⚠️  File not found: {file_path}")

if __name__ == "__main__":
    main()