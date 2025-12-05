#!/usr/bin/env python3
"""
Script to fix the common fields structure in the comprehensive document
to match the frontend interface expectations.

Changes:
- id -> fieldId
- label -> uiDisplayName  
- type -> fieldType
- required -> isRequired
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
    
    # Create new field structure
    new_field = {}
    
    # Map old field names to new ones
    field_mapping = {
        'id': 'fieldId',
        'label': 'uiDisplayName', 
        'type': 'fieldType',
        'required': 'isRequired'
    }
    
    # Apply mappings
    for old_key, new_key in field_mapping.items():
        if old_key in field:
            new_field[new_key] = field[old_key]
    
    # Copy over fields that don't need mapping
    preserve_fields = [
        'technicalName', 'placeholder', 'helpText', 'validation',
        'sortOrder', 'gridSize', 'fieldGroup', 'options', 'dataSource',
        'dataSourceConfig', 'defaultValue', 'units', 'isReadonly'
    ]
    
    for key in preserve_fields:
        if key in field:
            new_field[key] = field[key]
    
    # Add missing fields with defaults
    if 'fieldId' not in new_field and 'id' in field:
        new_field['fieldId'] = field['id']
    
    if 'uiDisplayName' not in new_field and 'label' in field:
        new_field['uiDisplayName'] = field['label']
        
    if 'fieldType' not in new_field and 'type' in field:
        new_field['fieldType'] = field['type']
        
    if 'isRequired' not in new_field:
        new_field['isRequired'] = field.get('required', False)
    
    # Ensure required fields have defaults
    if 'technicalName' not in new_field:
        new_field['technicalName'] = new_field.get('fieldId', '')
    
    if 'placeholder' not in new_field:
        new_field['placeholder'] = ''
        
    if 'helpText' not in new_field:
        new_field['helpText'] = ''
        
    if 'sortOrder' not in new_field:
        new_field['sortOrder'] = 1
        
    if 'gridSize' not in new_field:
        new_field['gridSize'] = 3
    
    return new_field

def fix_common_fields_in_comprehensive_doc():
    """Fix common fields structure in the comprehensive document"""
    try:
        # Connect to MongoDB with SSL configuration
        client = MongoClient(MONGODB_URI, tlsAllowInvalidCertificates=True)
        db = client.valuation_admin
        collection = db.banks
        
        print("🔍 Searching for comprehensive document...")
        
        # Find the comprehensive document
        doc = collection.find_one({"_id": "all_banks_comprehensive_v4"})
        if not doc:
            print("❌ Comprehensive document not found")
            return False
        
        print(f"✅ Found comprehensive document with {len(doc.get('banks', []))} banks")
        
        # Find common fields document
        common_fields_doc = None
        if 'common_form_fields' in doc:
            common_fields_doc = doc['common_form_fields']
        else:
            print("❌ No common_form_fields found in comprehensive document")
            return False
        
        print(f"📄 Found {len(common_fields_doc)} common fields")
        
        # Fix each common field
        fixed_fields = []
        for field in common_fields_doc:
            print(f"🔄 Processing field: {field.get('id', field.get('fieldId', 'unknown'))}")
            fixed_field = fix_field_structure(field)
            fixed_fields.append(fixed_field)
            print(f"   ✅ Converted to: {fixed_field.get('fieldId')}")
        
        # Update the document
        print("💾 Updating comprehensive document...")
        result = collection.update_one(
            {"_id": "all_banks_comprehensive_v4"},
            {"$set": {"common_form_fields": fixed_fields}}
        )
        
        if result.modified_count > 0:
            print(f"✅ Successfully updated {len(fixed_fields)} common fields")
            
            # Show sample of updated fields
            print("\n📋 Sample updated fields:")
            for field in fixed_fields[:3]:
                print(f"  - {field['fieldId']}: {field['uiDisplayName']} ({field['fieldType']})")
            
            return True
        else:
            print("⚠️ No changes were made")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    print("🔧 Starting common fields structure fix...")
    success = fix_common_fields_in_comprehensive_doc()
    
    if success:
        print("\n🎉 Common fields structure has been fixed!")
        print("The frontend should now be able to display the common fields correctly.")
    else:
        print("\n❌ Failed to fix common fields structure")
    
    sys.exit(0 if success else 1)