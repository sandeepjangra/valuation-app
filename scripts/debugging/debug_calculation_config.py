#!/usr/bin/env python3
"""
Check SBI land template for calculated field configurations
"""
import os
import sys
sys.path.append('/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend')

from pymongo import MongoClient
import json
from dotenv import load_dotenv

def check_sbi_template():
    print("🔍 Checking SBI land template for calculated field configurations...")
    
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
        
        # Check valuation_admin for SBI templates
        admin_db = client['valuation_admin']
        
        # Check bank_templates collection
        templates_collection = admin_db['bank_templates']
        
        # Find SBI land template
        sbi_template = templates_collection.find_one({
            "bankCode": "SBI",
            "templateCode": "land-property"
        })
        
        if not sbi_template:
            print("❌ No SBI land-property template found")
            # List available templates
            templates = list(templates_collection.find({}, {"bankCode": 1, "templateCode": 1, "name": 1}))
            print(f"Available templates: {len(templates)}")
            for t in templates[:5]:
                print(f"  - {t.get('bankCode')}: {t.get('templateCode')} ({t.get('name')})")
            return
            
        print("✅ Found SBI land-property template")
        
        # Check for calculated field configurations
        tabs = sbi_template.get('tabs', [])
        print(f"📊 Template has {len(tabs)} tabs")
        
        calculated_fields_found = []
        
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
                    
                    # Check if this is a calculated field
                    if field.get('isCalculated'):
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
                    
                    # Also check for field names that suggest calculations
                    elif any(keyword in field_id.lower() for keyword in ['total', 'calculated', 'estimated', 'value', 'amount']):
                        print(f"    💰 POTENTIAL CALC FIELD: {field_id} ({field_name}) - isReadonly: {field.get('isReadonly')}")
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total calculated fields found: {len(calculated_fields_found)}")
        
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
            print("   This explains why real-time calculation is not working.")
            print("   The template needs to have fields with 'isCalculated: true' and 'calculationConfig'")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_sbi_template()