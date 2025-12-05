#!/usr/bin/env python3
"""
Script to find and fix common fields through collection references
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

def find_common_fields():
    """Find common fields through collection references"""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_URI, tlsAllowInvalidCertificates=True)
        db = client.valuation_admin
        
        print("🔍 Searching for comprehensive document...")
        
        # Find the comprehensive document
        banks_collection = db.banks
        doc = banks_collection.find_one({"_id": "all_banks_comprehensive_v4"})
        if not doc:
            print("❌ Comprehensive document not found")
            return False
        
        # Look for SBI bank and land-property template
        sbi_bank = None
        for bank in doc['banks']:
            if bank.get('bankCode', '').upper() == 'SBI':
                sbi_bank = bank
                break
        
        if not sbi_bank:
            print("❌ SBI bank not found")
            return False
        
        print(f"✅ Found SBI bank with {len(sbi_bank.get('templates', []))} templates")
        
        # Find land-property template
        land_template = None
        for template in sbi_bank.get('templates', []):
            if template.get('templateCode') == 'land-property':
                land_template = template
                break
        
        if not land_template:
            print("❌ land-property template not found")
            return False
        
        print(f"✅ Found land-property template")
        print(f"📋 Template structure: {json.dumps(land_template, indent=2)}")
        
        # Check common fields collection reference
        common_fields_ref = land_template.get('commonFieldsCollectionRef')
        if not common_fields_ref:
            print("❌ No commonFieldsCollectionRef found")
            return False
        
        print(f"🔗 Common fields reference: {common_fields_ref}")
        
        # Find the common fields collection
        common_fields_collection = db[common_fields_ref]
        common_fields_docs = list(common_fields_collection.find({}))
        
        print(f"📄 Found {len(common_fields_docs)} documents in {common_fields_ref}")
        
        if len(common_fields_docs) > 0:
            first_field = common_fields_docs[0]
            print(f"📋 First common field structure: {list(first_field.keys())}")
            print(f"📋 First field: {json.dumps(first_field, indent=2)}")
            
            # Check if it needs structure fixing
            needs_fix = False
            old_format_fields = ['id', 'label', 'type']
            new_format_fields = ['fieldId', 'uiDisplayName', 'fieldType']
            
            if any(field in first_field for field in old_format_fields):
                needs_fix = True
                print("⚠️ Fields are in old format, need to be converted")
            elif any(field in first_field for field in new_format_fields):
                print("✅ Fields are already in new format")
            else:
                print("❓ Unknown field format")
            
            return needs_fix
        
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'client' in locals():
            client.close()

def fix_common_fields_collection():
    """Fix the common fields collection structure"""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_URI, tlsAllowInvalidCertificates=True)
        db = client.valuation_admin
        
        # Get the collection name from comprehensive doc
        banks_collection = db.banks
        doc = banks_collection.find_one({"_id": "all_banks_comprehensive_v4"})
        
        # Find SBI land-property template
        sbi_bank = None
        for bank in doc['banks']:
            if bank.get('bankCode', '').upper() == 'SBI':
                sbi_bank = bank
                break
        
        land_template = None
        for template in sbi_bank.get('templates', []):
            if template.get('templateCode') == 'land-property':
                land_template = template
                break
        
        common_fields_ref = land_template.get('commonFieldsCollectionRef')
        if not common_fields_ref:
            print("❌ No common fields collection reference found")
            return False
        
        print(f"🔧 Fixing collection: {common_fields_ref}")
        
        # Get the collection
        common_fields_collection = db[common_fields_ref]
        docs = list(common_fields_collection.find({}))
        
        # Fix each document
        fixed_count = 0
        for doc in docs:
            if 'id' in doc or 'label' in doc or 'type' in doc:
                # Convert to new format
                update_fields = {}
                
                if 'id' in doc:
                    update_fields['fieldId'] = doc['id']
                if 'label' in doc:
                    update_fields['uiDisplayName'] = doc['label']
                if 'type' in doc:
                    update_fields['fieldType'] = doc['type']
                if 'required' in doc:
                    update_fields['isRequired'] = doc['required']
                
                # Update the document
                result = common_fields_collection.update_one(
                    {"_id": doc["_id"]},
                    {"$set": update_fields, "$unset": {"id": "", "label": "", "type": "", "required": ""}}
                )
                
                if result.modified_count > 0:
                    fixed_count += 1
                    print(f"✅ Fixed field: {update_fields.get('fieldId', doc.get('_id'))}")
        
        print(f"🎉 Fixed {fixed_count} fields")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    print("🔧 Finding common fields collection...")
    
    if find_common_fields():
        print("\n🔧 Fixing common fields structure...")
        success = fix_common_fields_collection()
        
        if success:
            print("\n🎉 Common fields structure has been fixed!")
        else:
            print("\n❌ Failed to fix common fields structure")
    else:
        print("\n✅ No fixes needed or fields not found")