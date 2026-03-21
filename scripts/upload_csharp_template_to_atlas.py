#!/usr/bin/env python3
"""
Upload C# Template to MongoDB Atlas
This script uploads the migrated C# template to the valuation_templates database
"""

import json
import sys
import os
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

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
        print("✅ Connected to MongoDB Atlas\n")
        return client
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        sys.exit(1)

def upload_template(client, template_path):
    """Upload template to valuation_templates database"""
    
    # Read the template file
    print(f"📂 Reading template from: {template_path}")
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = json.load(f)
        print(f"✅ Template loaded: {template.get('TemplateName', 'Unknown')}\n")
    except Exception as e:
        print(f"❌ Failed to read template file: {e}")
        sys.exit(1)
    
    # Connect to database
    db = client['valuation_templates']
    collection = db['templates']
    
    # Add metadata
    template['CreatedAt'] = datetime.utcnow()
    template['UpdatedAt'] = datetime.utcnow()
    template['Version'] = "1.0"
    template['Status'] = "Active"
    template['MigratedFrom'] = "MongoDB_Legacy_Structure"
    template['MigrationDate'] = datetime.utcnow()
    
    # Check if template already exists
    existing = collection.find_one({'TemplateId': template['TemplateId']})
    
    if existing:
        print(f"⚠️  Template '{template['TemplateId']}' already exists")
        print(f"   Existing ID: {existing['_id']}")
        
        response = input("\n❓ Do you want to replace it? (yes/no): ").strip().lower()
        
        if response == 'yes':
            # Update existing template
            result = collection.replace_one(
                {'TemplateId': template['TemplateId']},
                template
            )
            print(f"\n✅ Template updated successfully")
            print(f"   Modified Count: {result.modified_count}")
            print(f"   Template ID: {template['TemplateId']}")
            return existing['_id']
        else:
            print("\n⏸️  Template upload cancelled")
            return None
    else:
        # Insert new template
        result = collection.insert_one(template)
        print(f"✅ Template uploaded successfully")
        print(f"   Database: valuation_templates")
        print(f"   Collection: templates")
        print(f"   MongoDB ID: {result.inserted_id}")
        print(f"   Template ID: {template['TemplateId']}")
        print(f"   Template Name: {template['TemplateName']}")
        print(f"   Bank: {template['BankDetails']['BankName']}")
        print(f"   Property Type: {template['PropertyType']}")
        print(f"   Total Elements: {len(template['Elements'])}")
        print(f"   Calculation Rules: {len(template['CalculationRules'])}")
        
        # Create indexes
        print("\n📊 Creating indexes...")
        collection.create_index([('TemplateId', 1)], unique=True)
        collection.create_index([('BankDetails.BankCode', 1)])
        collection.create_index([('PropertyType', 1)])
        collection.create_index([('Status', 1)])
        print("✅ Indexes created")
        
        return result.inserted_id

def verify_template(client, template_id):
    """Verify the uploaded template"""
    db = client['valuation_templates']
    collection = db['templates']
    
    template = collection.find_one({'TemplateId': template_id})
    
    if template:
        print("\n🔍 Template Verification:")
        print(f"   ✅ Template found in database")
        print(f"   ✅ Elements count: {len(template.get('Elements', []))}")
        print(f"   ✅ Calculation Rules count: {len(template.get('CalculationRules', []))}")
        
        # Count tabs
        tabs = [e for e in template.get('Elements', []) 
                if e.get('$type') == 'container' and e.get('Container') == 'Tab']
        print(f"   ✅ Tabs count: {len(tabs)}")
        
        # List tab names
        print("\n   📑 Tabs:")
        for tab in tabs:
            print(f"      • {tab.get('Label', 'Unknown')}")
        
        # List calculation rules
        if template.get('CalculationRules'):
            print("\n   🧮 Calculation Rules:")
            for rule in template.get('CalculationRules', []):
                print(f"      • {rule.get('Description', 'Unknown')}")
                print(f"        Formula: {rule.get('Formula', 'N/A')}")
        
        return True
    else:
        print(f"\n❌ Template verification failed - not found in database")
        return False

def main():
    print("=" * 80)
    print("🚀 UPLOAD C# TEMPLATE TO MONGODB ATLAS")
    print("=" * 80)
    
    # Template path
    template_path = "templates-csharp/migrated/sbi_land_template.json"
    
    # Connect to MongoDB
    client = connect_to_mongodb()
    
    try:
        # Upload template
        mongo_id = upload_template(client, template_path)
        
        if mongo_id:
            # Verify upload
            verify_template(client, "SBI_LAND_TEMPLATE_V1")
            
            print("\n" + "=" * 80)
            print("🎉 TEMPLATE UPLOAD COMPLETED SUCCESSFULLY")
            print("=" * 80)
        else:
            print("\n" + "=" * 80)
            print("⏸️  TEMPLATE UPLOAD SKIPPED")
            print("=" * 80)
            
    finally:
        client.close()
        print("\n✅ Database connection closed")

if __name__ == "__main__":
    main()
