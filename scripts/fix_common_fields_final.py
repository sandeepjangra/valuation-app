#!/usr/bin/env python3
"""
Script to fix common fields structure - looking inside fields array
"""

import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend/.env')

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    print("❌ MONGODB_URI environment variable not found")
    sys.exit(1)

def fix_field_structure(field):
    """Convert old field structure to new frontend-expected structure"""
    if not isinstance(field, dict):
        return field
    
    # Create new field structure by copying all existing fields
    new_field = field.copy()
    
    # Apply field mappings for old format fields
    field_mapping = {
        'id': 'fieldId',
        'label': 'uiDisplayName', 
        'type': 'fieldType',
        'required': 'isRequired'
    }
    
    changes_made = False
    
    # Apply mappings and remove old fields
    for old_key, new_key in field_mapping.items():
        if old_key in new_field:
            new_field[new_key] = new_field[old_key]
            del new_field[old_key]
            changes_made = True
    
    # Ensure required fields have defaults if missing
    defaults = {
        'technicalName': new_field.get('fieldId', ''),
        'placeholder': '',
        'helpText': '',
        'sortOrder': 1,
        'gridSize': 3,
        'isRequired': False
    }
    
    for key, default_value in defaults.items():
        if key not in new_field:
            new_field[key] = default_value
    
    return new_field, changes_made

def fix_common_fields_in_collection():
    """Fix common fields structure in the collection"""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_URI, tlsAllowInvalidCertificates=True)
        db = client.valuation_admin
        
        print("🔧 Fixing common fields collection...")
        
        # Get the common fields collection
        common_fields_collection = db.common_form_fields
        doc = common_fields_collection.find_one({})
        
        if not doc:
            print("❌ No common fields document found")
            return False
        
        if 'fields' not in doc:
            print("❌ No 'fields' array found in document")
            return False
        
        fields = doc['fields']
        print(f"📄 Found {len(fields)} common fields")
        
        # Show first field structure
        if len(fields) > 0:
            first_field = fields[0]
            print(f"📋 First field keys: {list(first_field.keys())}")
            
            # Check if we need to fix
            needs_fix = 'id' in first_field or 'label' in first_field or 'type' in first_field
            
            if not needs_fix:
                print("✅ Fields are already in correct format")
                return True
        
        # Fix each field
        fixed_fields = []
        changes_count = 0
        
        for i, field in enumerate(fields):
            print(f"🔄 Processing field {i+1}: {field.get('id', field.get('fieldId', 'unknown'))}")
            fixed_field, changed = fix_field_structure(field)
            fixed_fields.append(fixed_field)
            
            if changed:
                changes_count += 1
                print(f"   ✅ Converted: {fixed_field.get('fieldId')} ({fixed_field.get('fieldType')})")
        
        # Update the document
        if changes_count > 0:
            print(f"\n💾 Updating {changes_count} fields in database...")
            result = common_fields_collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"fields": fixed_fields}}
            )
            
            if result.modified_count > 0:
                print(f"✅ Successfully updated common fields document")
                print(f"📊 Summary: Fixed {changes_count} out of {len(fields)} fields")
                
                # Show sample of updated fields
                print("\n📋 Updated fields:")
                for field in fixed_fields[:3]:
                    print(f"  - {field['fieldId']}: {field['uiDisplayName']} ({field['fieldType']})")
                
                return True
            else:
                print("⚠️ No changes were made to database")
                return False
        else:
            print("✅ No changes needed - all fields are already in correct format")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    print("🔧 Starting common fields structure fix...")
    success = fix_common_fields_in_collection()
    
    if success:
        print("\n🎉 Common fields structure has been fixed!")
        print("The frontend should now be able to display the common fields correctly.")
    else:
        print("\n❌ Failed to fix common fields structure")
    
    sys.exit(0 if success else 1)