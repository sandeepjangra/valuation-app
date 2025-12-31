#!/usr/bin/env python3
"""
Find where templates are stored and check calculation configurations
"""
import os
import sys
sys.path.append('/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend')

from pymongo import MongoClient
import json
from dotenv import load_dotenv

def find_templates():
    print("🔍 Finding where templates are stored...")
    
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
        
        # Check multiple databases
        databases_to_check = [
            'valuation_admin',
            'sk-tindwal',
            'sbi-templates',
            'templates'
        ]
        
        for db_name in databases_to_check:
            try:
                db = client[db_name]
                collections = db.list_collection_names()
                print(f"\n📊 Database: {db_name}")
                print(f"   Collections: {collections}")
                
                # Check for template-related collections
                template_collections = [col for col in collections if 'template' in col.lower()]
                
                for col_name in template_collections:
                    collection = db[col_name]
                    count = collection.count_documents({})
                    print(f"   📁 {col_name}: {count} documents")
                    
                    # Show sample document
                    if count > 0:
                        sample = collection.find_one({})
                        if sample:
                            keys = list(sample.keys())
                            print(f"      Sample keys: {keys[:10]}...")
                            
                            # Check if it has calculation-related fields
                            calc_indicators = ['isCalculated', 'calculation', 'sourceFields', 'formula']
                            has_calc = any(indicator in str(sample) for indicator in calc_indicators)
                            if has_calc:
                                print(f"      🧮 Contains calculation indicators!")
                                
                # Also check collections that might contain template data
                other_collections = ['bank_templates', 'templates', 'form_templates', 'sbi_templates']
                for col_name in other_collections:
                    if col_name in collections:
                        collection = db[col_name]
                        count = collection.count_documents({})
                        if count > 0:
                            print(f"   📋 {col_name}: {count} documents")
                            sample = collection.find_one({})
                            if sample:
                                # Look for SBI or land property
                                if any(term in str(sample).lower() for term in ['sbi', 'land', 'property']):
                                    print(f"      🏦 Contains SBI/land property data!")
                                    
                                # Check for calculation fields
                                calc_fields = [k for k in sample.keys() if 'calc' in k.lower() or 'formula' in k.lower()]
                                if calc_fields:
                                    print(f"      🧮 Calculation fields: {calc_fields}")
                                    
            except Exception as e:
                print(f"   ❌ Error accessing {db_name}: {e}")
        
        # Check for specific SBI land template in sk-tindwal
        print(f"\n🔍 Looking specifically for SBI land template in sk-tindwal...")
        sk_db = client['sk-tindwal']
        
        for col_name in sk_db.list_collection_names():
            collection = sk_db[col_name]
            
            # Try to find SBI land template
            sbi_docs = list(collection.find({
                "$or": [
                    {"bankCode": "SBI"},
                    {"templateCode": "land-property"},
                    {"name": {"$regex": "land", "$options": "i"}},
                    {"type": {"$regex": "land", "$options": "i"}}
                ]
            }).limit(3))
            
            if sbi_docs:
                print(f"\n📁 Found {len(sbi_docs)} SBI/land documents in {col_name}:")
                for doc in sbi_docs:
                    doc_id = doc.get('_id')
                    name = doc.get('name') or doc.get('templateName') or doc.get('title')
                    bank = doc.get('bankCode') or doc.get('bank')
                    print(f"   📄 {doc_id}: {name} (Bank: {bank})")
                    
                    # Check for calculation configuration
                    calc_keys = [k for k in doc.keys() if 'calc' in k.lower()]
                    if calc_keys:
                        print(f"      🧮 Calculation keys: {calc_keys}")
                    
                    # Check for tabs/sections structure
                    if 'tabs' in doc:
                        tabs = doc['tabs']
                        print(f"      📂 Has {len(tabs) if isinstance(tabs, list) else 'unknown'} tabs")
                        
                        # Look for calculated fields in tabs
                        if isinstance(tabs, list):
                            for tab in tabs[:2]:  # Check first 2 tabs
                                if isinstance(tab, dict) and 'sections' in tab:
                                    for section in tab['sections']:
                                        if isinstance(section, dict) and 'fields' in section:
                                            calc_fields = [f for f in section['fields'] if isinstance(f, dict) and f.get('isCalculated')]
                                            if calc_fields:
                                                print(f"        🧮 Found {len(calc_fields)} calculated fields in section")
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_templates()