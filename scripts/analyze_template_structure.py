#!/usr/bin/env python3
"""
Analyze SBI Land Template Structure from MongoDB Atlas
This script fetches the template and analyzes its structure for migration planning
"""

import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
import json
from collections import defaultdict

# Load environment variables
load_dotenv()

def connect_to_mongodb():
    """Connect to MongoDB Atlas"""
    mongo_uri = os.getenv('MONGODB_URI')
    if not mongo_uri:
        print("❌ MONGODB_URI not found in environment variables")
        sys.exit(1)
    
    try:
        client = MongoClient(mongo_uri)
        # Test connection
        client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas")
        return client
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        sys.exit(1)

def analyze_field_structure(fields, level=0, parent_path=""):
    """Recursively analyze field structure"""
    field_stats = {
        'total_fields': 0,
        'field_types': defaultdict(int),
        'has_formula': 0,
        'has_subfields': 0,
        'max_nesting_level': level,
        'field_details': []
    }
    
    for field in fields:
        field_stats['total_fields'] += 1
        field_type = field.get('fieldType', 'unknown')
        field_stats['field_types'][field_type] += 1
        
        field_info = {
            'fieldId': field.get('fieldId'),
            'fieldType': field_type,
            'level': level,
            'path': f"{parent_path}/{field.get('fieldId')}" if parent_path else field.get('fieldId'),
            'hasFormula': bool(field.get('formula')),
            'hasSubFields': bool(field.get('subFields')),
            'hasCalculationMetadata': bool(field.get('calculationMetadata'))
        }
        field_stats['field_details'].append(field_info)
        
        # Check for formula
        if field.get('formula'):
            field_stats['has_formula'] += 1
            print(f"  {'  ' * level}🧮 Found formula field: {field.get('fieldId')} = {field.get('formula')}")
        
        # Check for subFields (groups)
        if field.get('subFields'):
            field_stats['has_subfields'] += 1
            print(f"  {'  ' * level}📦 Group field: {field.get('fieldId')} ({len(field.get('subFields'))} subfields)")
            sub_stats = analyze_field_structure(
                field.get('subFields'), 
                level + 1, 
                field_info['path']
            )
            field_stats['total_fields'] += sub_stats['total_fields']
            for ft, count in sub_stats['field_types'].items():
                field_stats['field_types'][ft] += count
            field_stats['has_formula'] += sub_stats['has_formula']
            field_stats['has_subfields'] += sub_stats['has_subfields']
            field_stats['max_nesting_level'] = max(
                field_stats['max_nesting_level'], 
                sub_stats['max_nesting_level']
            )
            field_stats['field_details'].extend(sub_stats['field_details'])
    
    return field_stats

def analyze_template(template):
    """Analyze the complete template structure"""
    print("\n" + "="*80)
    print("📊 TEMPLATE STRUCTURE ANALYSIS")
    print("="*80)
    
    analysis = {
        'template_id': template.get('templateId'),
        'template_name': template.get('templateName'),
        'bank_code': template.get('bankCode'),
        'property_type': template.get('propertyType'),
        'tabs': [],
        'total_fields': 0,
        'field_types_summary': defaultdict(int),
        'formula_fields': [],
        'group_fields': [],
        'table_fields': []
    }
    
    print(f"\n📋 Template: {analysis['template_name']}")
    print(f"   Bank: {analysis['bank_code']}")
    print(f"   Property Type: {analysis['property_type']}")
    print(f"   Template ID: {analysis['template_id']}")
    
    # Analyze tabs
    tabs = template.get('tabs', [])
    print(f"\n📑 Total Tabs: {len(tabs)}")
    
    for tab in tabs:
        tab_info = {
            'tabId': tab.get('tabId'),
            'tabName': tab.get('tabName'),
            'hasSections': tab.get('hasSections', False),
            'sections': []
        }
        
        print(f"\n  📂 Tab: {tab_info['tabName']} (ID: {tab_info['tabId']})")
        print(f"     Has Sections: {tab_info['hasSections']}")
        
        # Analyze sections
        if tab_info['hasSections']:
            sections = tab.get('sections', [])
            print(f"     Sections: {len(sections)}")
            
            for section in sections:
                section_info = {
                    'sectionId': section.get('sectionId'),
                    'sectionName': section.get('sectionName'),
                    'fields': []
                }
                
                print(f"\n       📄 Section: {section_info['sectionName']}")
                
                # Analyze fields in section
                fields = section.get('fields', [])
                if fields:
                    field_stats = analyze_field_structure(fields, level=2)
                    section_info['field_stats'] = field_stats
                    analysis['total_fields'] += field_stats['total_fields']
                    
                    for ft, count in field_stats['field_types'].items():
                        analysis['field_types_summary'][ft] += count
                    
                    print(f"       Total fields: {field_stats['total_fields']}")
                    print(f"       Formula fields: {field_stats['has_formula']}")
                    print(f"       Group fields: {field_stats['has_subfields']}")
                
                tab_info['sections'].append(section_info)
        else:
            # Tab has direct fields (no sections)
            fields = tab.get('fields', [])
            print(f"     Direct fields: {len(fields)}")
            
            if fields:
                field_stats = analyze_field_structure(fields, level=1)
                tab_info['field_stats'] = field_stats
                analysis['total_fields'] += field_stats['total_fields']
                
                for ft, count in field_stats['field_types'].items():
                    analysis['field_types_summary'][ft] += count
        
        analysis['tabs'].append(tab_info)
    
    # Summary
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    print(f"Total Fields: {analysis['total_fields']}")
    print(f"\nField Types Distribution:")
    for field_type, count in sorted(analysis['field_types_summary'].items()):
        print(f"  - {field_type}: {count}")
    
    return analysis

def main():
    print("🔍 Fetching SBI Land Template from MongoDB Atlas...")
    
    client = connect_to_mongodb()
    db = client['valuation_admin']
    
    # First, list all collections to understand structure
    print("\n📋 Available collections in valuation_admin database:")
    collections = db.list_collection_names()
    sbi_collections = [c for c in collections if 'sbi' in c.lower()]
    for coll in sbi_collections:
        count = db[coll].count_documents({})
        print(f"   - {coll}: {count} documents")
    
    # Fetch from individual collections and build template
    print("\n🔍 Building complete template from SBI Land collections...")
    
    # Find all SBI Land related collections dynamically
    sbi_land_collections = [c for c in collections if 'sbi' in c.lower() and 'land' in c.lower()]
    
    if not sbi_land_collections:
        print("❌ No SBI Land collections found")
        sys.exit(1)
    
    print(f"   Found {len(sbi_land_collections)} collections:")
    for coll in sbi_land_collections:
        print(f"   - {coll}")
    
    template = {
        'templateMetadata': {
            'templateId': 'SBI_LAND_TEMPLATE_V1',
            'templateName': 'SBI Land Property Valuation',
            'bankCode': 'SBI',
            'propertyType': 'Land',
            'version': '2.0',
            'tabs': []
        }
    }
    
    # Fetch each collection
    for coll_name in sbi_land_collections:
        print(f"\n   📂 Processing: {coll_name}")
        doc = db[coll_name].find_one({})  # Get the first (and likely only) document
        
        if doc:
            # Remove MongoDB _id for cleaner output
            doc.pop('_id', None)
            
            tab_info = {
                'tabId': doc.get('templateCategory', coll_name.replace('sbi_land_', '')),
                'tabName': doc.get('uiName', doc.get('templateName', coll_name)),
                'templateId': doc.get('templateId'),
                'hasSections': bool(doc.get('sections', [])),
                'sections': doc.get('sections', []),
                'fields': doc.get('fields', [])
            }
            
            # Count fields
            total_fields = len(tab_info['fields'])
            for section in tab_info['sections']:
                total_fields += len(section.get('fields', []))
            
            template['templateMetadata']['tabs'].append(tab_info)
            print(f"      ✅ {tab_info['tabName']}")
            print(f"         Sections: {len(tab_info['sections'])}")
            print(f"         Total fields: {total_fields}")
    
    if not template['templateMetadata']['tabs']:
        print("❌ No template data found")
        sys.exit(1)
    
    print(f"✅ Template found: {template.get('templateMetadata', {}).get('templateName')}")
    
    # Save raw template for reference
    output_file = 'sbi_land_template_analysis.json'
    with open(output_file, 'w') as f:
        json.dump(template, f, indent=2, default=str)
    print(f"\n💾 Raw template saved to: {output_file}")
    
    # Analyze structure
    template_metadata = template.get('templateMetadata', {})
    analysis = analyze_template(template_metadata)
    
    # Save analysis
    analysis_file = 'sbi_land_template_structure_analysis.json'
    with open(analysis_file, 'w') as f:
        json.dump(analysis, f, indent=2, default=str)
    print(f"\n💾 Analysis saved to: {analysis_file}")
    
    print("\n✅ Analysis complete!")
    
    client.close()

if __name__ == "__main__":
    main()
