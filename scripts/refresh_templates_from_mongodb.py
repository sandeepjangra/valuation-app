#!/usr/bin/env python3
"""
Template Refresh Script for ValuationAppV1
Downloads all property detail templates from MongoDB and adds BankBranch fields
using existing bankBranches data from the banks collection.
"""

import os
import json
from pymongo import MongoClient
from datetime import datetime
import sys

def get_mongodb_client():
    """Get MongoDB client connection"""
    mongodb_uri = os.getenv('MONGODB_URI')
    if not mongodb_uri:
        mongodb_uri = "mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster"
    
    return MongoClient(mongodb_uri)

def get_bank_branches_data(client):
    """Extract bankBranches data from banks collection"""
    try:
        valuation_db = client.valuation_admin
        banks_collection = valuation_db.banks
        
        # Get the comprehensive banks document
        banks_doc = banks_collection.find_one({"_id": "all_banks_comprehensive_v4"})
        
        if not banks_doc:
            raise Exception("Banks document not found")
        
        print(f"✅ Found banks document with {len(banks_doc.get('banks', []))} banks")
        
        # Create bank branches mapping
        bank_branches_mapping = {}
        total_branches = 0
        
        for bank in banks_doc.get('banks', []):
            bank_code = bank.get('bankCode')
            bank_name = bank.get('bankName')
            branches = bank.get('bankBranches', [])
            
            branch_options = []
            for branch in branches:
                # Only include active branches
                if not branch.get('isActive', True):
                    continue
                branch_name = branch.get('branchName', '')
                branch_code = branch.get('branchCode', '')
                ifsc_code = branch.get('ifscCode', '')
                
                # Create display value
                display_value = f"{branch_name}"
                if branch_code:
                    display_value += f" ({branch_code})"
                if ifsc_code:
                    display_value += f" - {ifsc_code}"
                
                branch_options.append({
                    "value": branch.get('branchId', branch_code),
                    "label": display_value,
                    "branchCode": branch_code,
                    "branchName": branch_name,
                    "ifscCode": ifsc_code,
                    "branchAddress": branch.get('branchAddress', {}),
                    "contactDetails": branch.get('contactDetails', {})
                })
            
            if branch_options:
                bank_branches_mapping[bank_code] = {
                    "bankName": bank_name,
                    "bankCode": bank_code,
                    "branches": branch_options
                }
                total_branches += len(branch_options)
        
        print(f"✅ Processed {len(bank_branches_mapping)} banks with {total_branches} total branches")
        return bank_branches_mapping
        
    except Exception as e:
        print(f"❌ Error retrieving bank branches: {str(e)}")
        return {}

def create_bank_branch_field(bank_code, bank_branches_mapping):
    """Create BankBranch field for a specific bank"""
    if bank_code not in bank_branches_mapping:
        print(f"⚠️  No branches found for bank code: {bank_code}")
        return None
    
    bank_info = bank_branches_mapping[bank_code]
    
    return {
        "id": "BankBranch",
        "label": f"Bank Branch - {bank_info['bankName']}",
        "type": "select",
        "required": True,
        "validation": {
            "required": True,
            "message": f"Please select a {bank_info['bankName']} branch"
        },
        "options": bank_info['branches'],
        "placeholder": f"Select {bank_info['bankName']} branch...",
        "metadata": {
            "bankCode": bank_code,
            "bankName": bank_info['bankName'],
            "totalBranches": len(bank_info['branches']),
            "addedBy": "refresh_templates_from_mongodb.py",
            "addedDate": datetime.now().isoformat()
        }
    }

def get_bank_code_from_collection_name(collection_name):
    """Extract bank code from collection name"""
    bank_mapping = {
        'sbi': 'SBI',
        'bob': 'BOB', 
        'boi': 'BOI',
        'ubi': 'UBI',
        'cbi': 'CBI',
        'hdfc': 'HDFC',
        'pnb': 'PNB',
        'uco': 'UCO',
        'axis': 'AXIS',
        'icici': 'ICICI'
    }
    
    for prefix, code in bank_mapping.items():
        if collection_name.startswith(prefix):
            return code
    
    return None

def refresh_templates():
    """Main function to refresh all templates"""
    print("🔄 Starting template refresh from MongoDB...")
    
    # Connect to MongoDB
    client = get_mongodb_client()
    valuation_db = client.valuation_admin
    
    # Get bank branches data
    print("\n📋 Loading bank branches data...")
    bank_branches_mapping = get_bank_branches_data(client)
    
    if not bank_branches_mapping:
        print("❌ No bank branches data available. Exiting.")
        return False
    
    # Get all property detail collections
    collections = valuation_db.list_collection_names()
    template_collections = [col for col in collections if col.endswith('_property_details')]
    
    print(f"\n📁 Found {len(template_collections)} template collections:")
    for col in template_collections:
        print(f"  - {col}")
    
    # Create output directory
    output_dir = "templates_refreshed"
    os.makedirs(output_dir, exist_ok=True)
    
    success_count = 0
    total_processed = 0
    
    # Process each template collection
    for collection_name in template_collections:
        try:
            total_processed += 1
            print(f"\n🔧 Processing {collection_name}...")
            
            # Get bank code from collection name
            bank_code = get_bank_code_from_collection_name(collection_name)
            if not bank_code:
                print(f"  ⚠️  Could not determine bank code for {collection_name}")
                continue
            
            # Get template document
            collection = valuation_db[collection_name]
            template_doc = collection.find_one()
            
            if not template_doc:
                print(f"  ❌ No documents found in {collection_name}")
                continue
            
            # Remove MongoDB ObjectId for JSON serialization
            if '_id' in template_doc:
                del template_doc['_id']
            
            # Add/Update BankBranch field
            bank_branch_field = create_bank_branch_field(bank_code, bank_branches_mapping)
            
            if bank_branch_field:
                # Find existing BankBranch field or add new one
                fields = template_doc.get('fields', [])
                bank_branch_exists = False
                
                for i, field in enumerate(fields):
                    if field.get('id') == 'BankBranch':
                        fields[i] = bank_branch_field
                        bank_branch_exists = True
                        print(f"  ✅ Updated existing BankBranch field")
                        break
                
                if not bank_branch_exists:
                    # Insert BankBranch field at the beginning
                    fields.insert(0, bank_branch_field)
                    template_doc['fields'] = fields
                    print(f"  ✅ Added new BankBranch field with {len(bank_branch_field['options'])} branches")
                
                # Add metadata
                template_doc['metadata'] = template_doc.get('metadata', {})
                template_doc['metadata'].update({
                    'refreshedFrom': 'MongoDB',
                    'refreshDate': datetime.now().isoformat(),
                    'bankCode': bank_code,
                    'branchCount': len(bank_branch_field['options']),
                    'version': template_doc.get('version', '1.0')
                })
            
            # Save to JSON file
            output_file = f"{output_dir}/{collection_name}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(template_doc, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"  💾 Saved to {output_file}")
            success_count += 1
            
        except Exception as e:
            print(f"  ❌ Error processing {collection_name}: {str(e)}")
            continue
    
    # Summary
    print(f"\n🎉 Template refresh completed!")
    print(f"   ✅ Successfully processed: {success_count}/{total_processed}")
    print(f"   📁 Templates saved to: {output_dir}/")
    print(f"   🏦 Banks with branches: {len(bank_branches_mapping)}")
    
    if success_count > 0:
        # Show sample of what was processed
        print(f"\n📋 Sample bank branches added:")
        for bank_code, bank_info in list(bank_branches_mapping.items())[:3]:
            print(f"   {bank_code} ({bank_info['bankName']}): {len(bank_info['branches'])} branches")
    
    client.close()
    return success_count > 0

if __name__ == "__main__":
    try:
        success = refresh_templates()
        if success:
            print("\n✅ All templates refreshed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Template refresh failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Fatal error: {str(e)}")
        sys.exit(1)