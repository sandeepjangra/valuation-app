#!/usr/bin/env python3
"""
Check SBI land property template for calculated field configurations
"""
import os
import sys
sys.path.append('/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend')

from pymongo import MongoClient
import json
from dotenv import load_dotenv

def check_sbi_land_template():
    print("🔍 Checking SBI land property template for calculated field configurations...")
    
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
        print(f"Template ID: {sbi_template.get('_id')}")
        print(f"Template Name: {sbi_template.get('templateName')}")
        
        # Check template structure
        tabs = sbi_template.get('tabs', [])
        print(f"📊 Template has {len(tabs)} tabs")
        
        calculated_fields_found = []
        all_fields_found = []
        
        for tab_idx, tab in enumerate(tabs):
            tab_name = tab.get('name', f'Tab {tab_idx}')
            print(f"\n📁 TAB: {tab_name}")
            
            sections = tab.get('sections', [])
            for section_idx, section in enumerate(sections):
                section_name = section.get('name', f'Section {section_idx}')
                print(f"  📂 Section: {section_name}")
                
                fields = section.get('fields', [])
                for field in fields:
                    field_id = field.get('fieldId')
                    field_name = field.get('uiDisplayName')
                    field_type = field.get('fieldType')
                    is_readonly = field.get('isReadonly', False)
                    is_calculated = field.get('isCalculated', False)
                    
                    all_fields_found.append({
                        'tab': tab_name,
                        'section': section_name,
                        'fieldId': field_id,
                        'name': field_name,
                        'type': field_type,
                        'readonly': is_readonly,
                        'calculated': is_calculated
                    })
                    
                    # Check if this is a calculated field
                    if is_calculated:
                        calculated_fields_found.append({
                            'tab': tab_name,
                            'section': section_name,
                            'fieldId': field_id,
                            'name': field_name,
                            'calculation': field.get('calculationConfig')
                        })
                        print(f"    🧮 CALCULATED FIELD: {field_id} ({field_name})")
                        
                        # Show calculation config
                        calc_config = field.get('calculationConfig')
                        if calc_config:
                            print(f"       Type: {calc_config.get('type')}")
                            print(f"       Source Fields: {calc_config.get('sourceFields', [])}")
                            if calc_config.get('customFormula'):
                                print(f"       Formula: {calc_config.get('customFormula')}")
                    
                    # Show all readonly fields (potential calculated fields)
                    elif is_readonly:
                        print(f"    🔒 READONLY FIELD: {field_id} ({field_name})")
                        
                    # Show fields with calculation-related names
                    elif any(keyword in field_id.lower() for keyword in ['total', 'calculated', 'estimated', 'value', 'amount']):
                        print(f"    💰 VALUE FIELD: {field_id} ({field_name}) - Type: {field_type}, Readonly: {is_readonly}")
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total fields found: {len(all_fields_found)}")
        print(f"   Total calculated fields: {len(calculated_fields_found)}")
        
        # Count readonly fields
        readonly_fields = [f for f in all_fields_found if f['readonly']]
        print(f"   Total readonly fields: {len(readonly_fields)}")
        
        if calculated_fields_found:
            print(f"\n🧮 CALCULATED FIELDS DETAILS:")
            for calc_field in calculated_fields_found:
                print(f"   {calc_field['fieldId']}:")
                print(f"     Location: {calc_field['tab']} > {calc_field['section']}")
                print(f"     Name: {calc_field['name']}")
                if calc_field['calculation']:
                    print(f"     Config: {calc_field['calculation']}")
        else:
            print("❌ No calculated fields found in template!")
            print("   This is likely why real-time calculation is not working.")
            
        # Show some readonly fields that could be calculated
        if readonly_fields:
            print(f"\n🔒 READONLY FIELDS (could be calculated):")
            for field in readonly_fields:
                print(f"   {field['fieldId']}: {field['name']} (Type: {field['type']})")
            
            print(f"\n💡 SUGGESTION:")
            print(f"   To enable real-time calculation, these readonly fields need:")
            print(f"   1. 'isCalculated': true")
            print(f"   2. 'calculationConfig': {{ 'type': 'sum|product|custom', 'sourceFields': [...] }}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_sbi_land_template()