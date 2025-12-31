#!/usr/bin/env python3
"""
Explore the actual structure of SBI land template
"""
import os
import sys
sys.path.append('/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend')

from pymongo import MongoClient
import json
from dotenv import load_dotenv

def explore_sbi_template():
    print("🔍 Exploring SBI land property template structure...")
    
    # Load environment variables
    load_dotenv('/Users/sandeepjangra/Downloads/development/ValuationAppV1/.env')
    
    mongodb_uri = os.getenv('MONGODB_URI')
    if not mongodb_uri:
        print("❌ MONGODB_URI not found in environment variables")
        return
    
    # Connect to MongoDB Atlas
    try:
        client = MongoClient(mongodb_uri)
        print("✅ Connected to MongoDB Atlas")
        
        # Check valuation_admin for SBI land template
        admin_db = client['valuation_admin']
        
        # Check SBI land property details collection
        sbi_collection = admin_db['sbi_land_property_details']
        
        # Get the template document
        sbi_template = sbi_collection.find_one({})
        
        if not sbi_template:
            print("❌ No SBI land property template found")
            return
            
        print("✅ Found SBI land property template")
        
        # Show the full structure
        print(f"\n📋 TEMPLATE KEYS:")
        for key in sbi_template.keys():
            value = sbi_template[key]
            if isinstance(value, list):
                print(f"   {key}: list with {len(value)} items")
                if len(value) > 0 and isinstance(value[0], dict):
                    sample_keys = list(value[0].keys())
                    print(f"      Sample item keys: {sample_keys[:5]}...")
            elif isinstance(value, dict):
                print(f"   {key}: dict with keys: {list(value.keys())[:5]}...")
            else:
                print(f"   {key}: {type(value).__name__} = {str(value)[:50]}...")
        
        # Look for fields in different possible structures
        potential_field_keys = ['fields', 'sections', 'tabs', 'formFields', 'schema', 'structure']
        
        for key in potential_field_keys:
            if key in sbi_template:
                print(f"\n🔍 Exploring {key}:")
                data = sbi_template[key]
                
                if isinstance(data, list):
                    print(f"   Found list with {len(data)} items")
                    for i, item in enumerate(data[:3]):  # Show first 3 items
                        print(f"   Item {i}: {type(item).__name__}")
                        if isinstance(item, dict):
                            item_keys = list(item.keys())
                            print(f"      Keys: {item_keys}")
                            
                            # Look for calculation indicators
                            calc_indicators = ['isCalculated', 'calculation', 'sourceFields', 'formula']
                            calc_keys = [k for k in item_keys if any(ind in k for ind in calc_indicators)]
                            if calc_keys:
                                print(f"      🧮 Calculation keys found: {calc_keys}")
                            
                            # Look for field structure
                            if 'fieldId' in item:
                                print(f"      📝 Field: {item.get('fieldId')} ({item.get('uiDisplayName')})")
                                print(f"         Type: {item.get('fieldType')}, Readonly: {item.get('isReadonly')}")
                                if item.get('isCalculated'):
                                    print(f"         🧮 IS CALCULATED!")
                elif isinstance(data, dict):
                    print(f"   Found dict with keys: {list(data.keys())}")
        
        # Look specifically for calculation-related fields in the entire document
        print(f"\n🔍 Searching for calculation-related content...")
        template_str = str(sbi_template)
        
        calc_terms = ['calculat', 'formula', 'sourceField', 'sum', 'product', 'total', 'estimated']
        for term in calc_terms:
            if term.lower() in template_str.lower():
                print(f"   ✅ Found '{term}' in template")
        
        # Check if there are any fields with calculation-related names
        if 'fields' in sbi_template:
            fields = sbi_template['fields']
            if isinstance(fields, list):
                calc_named_fields = []
                readonly_fields = []
                for field in fields:
                    if isinstance(field, dict):
                        field_id = field.get('fieldId', '')
                        field_name = field.get('uiDisplayName', '')
                        
                        if any(term in field_id.lower() for term in ['total', 'calculated', 'estimated', 'value']):
                            calc_named_fields.append(f"{field_id} ({field_name})")
                            
                        if field.get('isReadonly'):
                            readonly_fields.append(f"{field_id} ({field_name})")
                
                if calc_named_fields:
                    print(f"\n💰 Fields with calculation-related names:")
                    for field in calc_named_fields[:5]:
                        print(f"   {field}")
                        
                if readonly_fields:
                    print(f"\n🔒 Readonly fields:")
                    for field in readonly_fields[:5]:
                        print(f"   {field}")
                        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    explore_sbi_template()