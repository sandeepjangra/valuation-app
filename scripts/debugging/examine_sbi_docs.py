#!/usr/bin/env python3
"""
Examine the documents structure in SBI land template for calculated fields
"""
import os
import sys
sys.path.append('/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend')

from pymongo import MongoClient
import json
from dotenv import load_dotenv

def examine_sbi_documents():
    print("🔍 Examining SBI land property template documents for calculated fields...")
    
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
        
        # Examine the documents structure
        documents = sbi_template.get('documents', [])
        print(f"\n📄 Found {len(documents)} documents")
        
        calculated_fields_found = []
        readonly_fields_found = []
        
        for doc_idx, document in enumerate(documents):
            print(f"\n📄 DOCUMENT {doc_idx + 1}:")
            print(f"   ID: {document.get('_id')}")
            print(f"   Template: {document.get('templateName')}")
            
            # Check for tabs structure
            tabs = document.get('tabs', [])
            print(f"   📁 Tabs: {len(tabs)}")
            
            for tab_idx, tab in enumerate(tabs):
                tab_name = tab.get('name', f'Tab {tab_idx}')
                print(f"      📁 {tab_name}")
                
                sections = tab.get('sections', [])
                for section in sections:
                    section_name = section.get('name', 'Unnamed Section')
                    print(f"         📂 {section_name}")
                    
                    fields = section.get('fields', [])
                    for field in fields:
                        field_id = field.get('fieldId')
                        field_name = field.get('uiDisplayName')
                        field_type = field.get('fieldType')
                        is_readonly = field.get('isReadonly', False)
                        is_calculated = field.get('isCalculated', False)
                        
                        # Track calculated fields
                        if is_calculated:
                            calc_config = field.get('calculationConfig', {})
                            calculated_fields_found.append({
                                'document': doc_idx + 1,
                                'tab': tab_name,
                                'section': section_name,
                                'fieldId': field_id,
                                'name': field_name,
                                'type': field_type,
                                'config': calc_config
                            })
                            print(f"            🧮 CALCULATED: {field_id} ({field_name})")
                            if calc_config:
                                print(f"               Type: {calc_config.get('type')}")
                                print(f"               Sources: {calc_config.get('sourceFields', [])}")
                        
                        # Track readonly fields (potential calculated fields)
                        elif is_readonly and any(keyword in field_id.lower() for keyword in ['total', 'calculated', 'estimated', 'value']):
                            readonly_fields_found.append({
                                'document': doc_idx + 1,
                                'tab': tab_name,
                                'section': section_name,
                                'fieldId': field_id,
                                'name': field_name,
                                'type': field_type
                            })
                            print(f"            🔒 READONLY VALUE: {field_id} ({field_name})")
        
        print(f"\n📊 SUMMARY:")
        print(f"   Calculated fields with config: {len(calculated_fields_found)}")
        print(f"   Readonly value fields: {len(readonly_fields_found)}")
        
        if calculated_fields_found:
            print(f"\n🧮 CALCULATED FIELDS:")
            for field in calculated_fields_found:
                print(f"   📄 Document {field['document']}: {field['fieldId']}")
                print(f"      Location: {field['tab']} > {field['section']}")
                print(f"      Name: {field['name']}")
                print(f"      Config: {field['config']}")
                
        if readonly_fields_found:
            print(f"\n🔒 READONLY VALUE FIELDS (could be made calculated):")
            for field in readonly_fields_found[:10]:  # Limit output
                print(f"   📄 Document {field['document']}: {field['fieldId']}")
                print(f"      Location: {field['tab']} > {field['section']}")
                print(f"      Name: {field['name']} (Type: {field['type']})")
                
        # Now check what the frontend is actually loading
        print(f"\n🔍 CHECKING FRONTEND API ENDPOINT:")
        print(f"   The frontend likely calls: /api/templates/SBI/land-property/aggregated-fields")
        print(f"   This endpoint should return calculated field configurations.")
        print(f"   If real-time calculation isn't working, the issue might be:")
        print(f"   1. API not returning calculated field configs")
        print(f"   2. Frontend not properly setting up calculated field listeners")
        print(f"   3. Template doesn't have 'isCalculated: true' on the right fields")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    examine_sbi_documents()