#!/usr/bin/env python3
"""
Migrate Banks Collection to New C# Structure
This script transforms the banks collection to the new C# naming convention
"""

import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
import json
from datetime import datetime

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
        client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas\n")
        return client
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        sys.exit(1)

def transform_branch(branch):
    """Transform branch to new C# structure"""
    return {
        'BranchId': branch.get('branchId', ''),
        'BranchCode': branch.get('branchCode', ''),
        'BranchName': branch.get('branchName', ''),
        'BranchAddress': {
            'Street': branch.get('branchAddress', {}).get('street', ''),
            'City': branch.get('branchAddress', {}).get('city', ''),
            'State': branch.get('branchAddress', {}).get('state', ''),
            'Pincode': branch.get('branchAddress', {}).get('pincode', ''),
            'Country': branch.get('branchAddress', {}).get('country', 'India')
        },
        'IfscCode': branch.get('ifscCode', ''),
        'ContactDetails': {
            'Phone': branch.get('contactDetails', {}).get('phone', ''),
            'Email': branch.get('contactDetails', {}).get('email', '')
        },
        'IsActive': branch.get('isActive', True),
        'CreatedAt': branch.get('createdAt'),
        'UpdatedAt': branch.get('updatedAt')
    }

def transform_template_reference(template):
    """Transform template reference to new C# structure"""
    return {
        'TemplateId': template.get('templateId', ''),
        'TemplateCode': template.get('templateCode', ''),
        'TemplateName': template.get('templateName', ''),
        'TemplateType': template.get('templateType', ''),
        'PropertyType': template.get('propertyType', ''),
        'Description': template.get('description', ''),
        'Version': template.get('version', '1.0'),
        'IsActive': template.get('isActive', True),
        'CollectionRef': template.get('collectionRef', ''),
        'CommonFieldsCollectionRef': template.get('commonFieldsCollectionRef', 'common_form_fields')
    }

def transform_bank(bank):
    """Transform bank to new C# structure"""
    return {
        'BankId': bank.get('bankId', ''),
        'BankCode': bank.get('bankCode', ''),
        'BankName': bank.get('bankName', ''),
        'BankShortName': bank.get('bankShortName', ''),
        'BankType': bank.get('bankType', ''),
        'IsActive': bank.get('isActive', True),
        'Headquarters': {
            'City': bank.get('headquarters', {}).get('city', ''),
            'State': bank.get('headquarters', {}).get('state', ''),
            'Pincode': bank.get('headquarters', {}).get('pincode', '')
        },
        'TotalBranches': bank.get('totalBranches', 0),
        'Branches': [transform_branch(branch) for branch in bank.get('bankBranches', [])],
        'Templates': [transform_template_reference(template) for template in bank.get('templates', [])]
    }

def migrate_banks(client):
    """Migrate banks collection"""
    print("=" * 80)
    print("🏦 MIGRATING BANKS COLLECTION")
    print("=" * 80)
    
    # Fetch from source
    source_db = client['valuation_admin']
    banks_doc = source_db['banks'].find_one()
    
    if not banks_doc:
        print("❌ No banks document found")
        return None
    
    banks_list = banks_doc.get('banks', [])
    print(f"✅ Found {len(banks_list)} banks")
    
    # Transform to new structure
    new_structure = {
        'CollectionName': 'Banks',
        'Description': 'Comprehensive collection of all banks with branches and template references',
        'Version': '5.0',
        'MigrationDate': datetime.utcnow(),
        'CreatedAt': banks_doc.get('createdAt'),
        'UpdatedAt': datetime.utcnow(),
        'Banks': []
    }
    
    print("\n📋 Transforming banks...")
    for bank in banks_list:
        transformed_bank = transform_bank(bank)
        new_structure['Banks'].append(transformed_bank)
        
        bank_code = bank.get('bankCode', 'Unknown')
        branches_count = len(bank.get('bankBranches', []))
        templates_count = len(bank.get('templates', []))
        
        print(f"   ✅ {bank_code}: {branches_count} branches, {templates_count} templates")
    
    # Statistics
    total_branches = sum(len(b['Branches']) for b in new_structure['Banks'])
    total_templates = sum(len(b['Templates']) for b in new_structure['Banks'])
    active_banks = sum(1 for b in new_structure['Banks'] if b['IsActive'])
    
    print(f"\n📊 Migration Summary:")
    print(f"   Total Banks: {len(new_structure['Banks'])}")
    print(f"   Active Banks: {active_banks}")
    print(f"   Total Branches: {total_branches}")
    print(f"   Total Template References: {total_templates}")
    
    return new_structure

def save_to_file(data, filename):
    """Save to JSON file"""
    filepath = f"templates-csharp/migrated/{filename}"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    file_size = os.path.getsize(filepath)
    print(f"\n💾 Saved to: {filepath} ({file_size / 1024:.1f} KB)")
    return filepath

def upload_to_mongodb(client, data):
    """Upload to new collection"""
    db = client['valuation_templates']
    collection = db['banks']
    
    # Check if exists
    existing = collection.find_one({})
    
    if existing:
        print(f"\n⚠️  Banks document already exists")
        response = input("   Replace existing document? (yes/no): ").strip().lower()
        
        if response == 'yes':
            collection.delete_many({})
            result = collection.insert_one(data)
            print(f"\n✅ Banks document replaced")
            print(f"   MongoDB ID: {result.inserted_id}")
        else:
            print("\n⏸️  Upload cancelled")
            return None
    else:
        result = collection.insert_one(data)
        print(f"\n✅ Banks document uploaded")
        print(f"   Database: valuation_templates")
        print(f"   Collection: banks")
        print(f"   MongoDB ID: {result.inserted_id}")
        
        # Create indexes
        print("\n📊 Creating indexes...")
        collection.create_index([('Banks.BankCode', 1)])
        collection.create_index([('Banks.BankId', 1)])
        collection.create_index([('Banks.IsActive', 1)])
        collection.create_index([('Banks.Branches.IfscCode', 1)])
        print("✅ Indexes created")
    
    return result.inserted_id if not existing or response == 'yes' else None

def verify_migration(client):
    """Verify the migrated data"""
    db = client['valuation_templates']
    collection = db['banks']
    
    doc = collection.find_one({})
    
    if doc:
        print("\n🔍 Migration Verification:")
        print(f"   ✅ Banks document found")
        print(f"   ✅ Banks count: {len(doc.get('Banks', []))}")
        
        # List banks
        print(f"\n   📋 Banks:")
        for bank in doc.get('Banks', []):
            status = "✅" if bank.get('IsActive') else "⚠️"
            print(f"      {status} {bank.get('BankCode', 'Unknown')} - {bank.get('BankName', 'Unknown')}")
            print(f"         Branches: {len(bank.get('Branches', []))}, Templates: {len(bank.get('Templates', []))}")
        
        return True
    else:
        print(f"\n❌ Verification failed - banks document not found")
        return False

def main():
    print("=" * 80)
    print("🚀 BANKS COLLECTION MIGRATION TO C# STRUCTURE")
    print("=" * 80)
    print()
    
    # Connect to MongoDB
    client = connect_to_mongodb()
    
    try:
        # Migrate banks
        new_structure = migrate_banks(client)
        
        if new_structure:
            # Save to file
            filepath = save_to_file(new_structure, 'banks.json')
            
            # Ask to upload
            print("\n" + "=" * 80)
            response = input("❓ Upload to MongoDB Atlas valuation_templates.banks? (yes/no): ").strip().lower()
            
            if response == 'yes':
                mongo_id = upload_to_mongodb(client, new_structure)
                
                if mongo_id:
                    # Verify
                    verify_migration(client)
                    
                    print("\n" + "=" * 80)
                    print("🎉 BANKS MIGRATION COMPLETED SUCCESSFULLY")
                    print("=" * 80)
                else:
                    print("\n" + "=" * 80)
                    print("⏸️  BANKS MIGRATION SAVED TO FILE ONLY")
                    print("=" * 80)
            else:
                print("\n" + "=" * 80)
                print("💾 BANKS MIGRATION SAVED TO FILE ONLY")
                print("=" * 80)
                print(f"   File: {filepath}")
                print("   Run upload script later if needed")
                print("=" * 80)
        else:
            print("\n❌ Migration failed")
            
    finally:
        client.close()
        print("\n✅ Database connection closed")

if __name__ == "__main__":
    main()
