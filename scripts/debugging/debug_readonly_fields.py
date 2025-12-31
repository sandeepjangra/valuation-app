#!/usr/bin/env python3
"""
Debug readonly fields in reports
"""
import os
import sys
sys.path.append('/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend')

# Load environment variables
from dotenv import load_dotenv
load_dotenv('/Users/sandeepjangra/Downloads/development/ValuationAppV1/.env')

from pymongo import MongoClient
import json

def check_readonly_fields():
    print("🔍 Checking readonly fields in reports...")
    
    # Get MongoDB URI from environment (Atlas connection)
    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        print("❌ MONGODB_URI environment variable not found")
        print("Available env vars:", [k for k in os.environ.keys() if 'MONGO' in k])
        return
    
    # Connect to MongoDB Atlas
    try:
        client = MongoClient(mongodb_uri)
        # Test connection
        client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB Atlas: {e}")
        return
    
    # Get database names from environment
    admin_db_name = os.getenv("MONGODB_ADMIN_DB_NAME", "valuation_admin")
    reports_db_name = os.getenv("MONGODB_REPORTS_DB_NAME", "valuation_reports")
    
    print(f"📊 Using databases: admin={admin_db_name}, reports={reports_db_name}")
    
    # Check admin database for common fields
    admin_db = client[admin_db_name]
    
    # Check admin database for common fields
    admin_db = client[admin_db_name]
    
    # Try to check reports in different possible databases
    databases_to_check = [
        (admin_db_name, admin_db),
        (reports_db_name, client[reports_db_name]) if reports_db_name != admin_db_name else None,
        ("valuation_app_prod", client["valuation_app_prod"]),
    ]
    
    # Filter out None values
    databases_to_check = [db for db in databases_to_check if db is not None]
    
    reports_found = []
    
    for db_name, db in databases_to_check:
        try:
            if 'reports' in db.list_collection_names():
                reports_collection = db['reports']
                reports = list(reports_collection.find({}).sort('created_at', -1).limit(2))
                if reports:
                    print(f"\n📊 Found {len(reports)} reports in database: {db_name}")
                    reports_found.extend([(db_name, report) for report in reports])
            else:
                print(f"📊 No 'reports' collection found in database: {db_name}")
        except Exception as e:
            print(f"❌ Error checking database {db_name}: {e}")
    
    if not reports_found:
        print("❌ No reports found in any database")
        return
    
    # Analyze reports
    for db_name, report in reports_found[:3]:  # Limit to first 3 reports
        print(f"\n--- Report from {db_name} ---")
        print(f"ID: {report.get('_id')}")
        print(f"Status: {report.get('status')}")
        print(f"Reference: {report.get('reference_number')}")
        
        # Check report_data for key readonly fields
        report_data = report.get('report_data', {})
        
        # Check for report_reference_number
        ref_num = report_data.get('report_reference_number')
        print(f"Report Reference Number in data: {ref_num}")
        
        # Check for calculated fields
        estimated_land_value = report_data.get('estimated_value_of_land')
        print(f"Estimated Value of Land in data: {estimated_land_value}")
        
        # Check for any other readonly fields
        readonly_fields = [
            'report_reference_number',
            'estimated_value_of_land', 
            'total_value',
            'calculated_area',
            'total_cost'
        ]
        
        print("All readonly field values in report_data:")
        for field in readonly_fields:
            value = report_data.get(field)
            if value is not None:
                print(f"  {field}: {value}")
        
        # Show first few keys of report_data to understand structure
        if report_data:
            print(f"Report data keys (first 15): {list(report_data.keys())[:15]}...")
        else:
            print("❌ No report_data found!")
        
        # Also check if reference number exists at top level
        top_level_ref = report.get('reference_number')
        print(f"Top-level reference_number: {top_level_ref}")
    
    # Check common form fields for readonly configuration
    print(f"\n🔧 Checking common form fields for readonly configuration...")
    
    try:
        common_fields = admin_db['common_form_fields']
        common_doc = common_fields.find_one({'_id': 'common_fields'})
        
        if common_doc:
            fields = common_doc.get('fields', [])
            readonly_common_fields = [f for f in fields if f.get('isReadonly')]
            
            print(f"Found {len(readonly_common_fields)} readonly common fields:")
            for field in readonly_common_fields:
                print(f"  - {field.get('fieldId')} ({field.get('uiDisplayName')})")
                print(f"    Default Value: {field.get('defaultValue', 'None')}")
                print(f"    Help Text: {field.get('helpText', 'None')}")
        else:
            print("❌ No common_fields document found!")
    except Exception as e:
        print(f"❌ Error checking common fields: {e}")

if __name__ == "__main__":
    check_readonly_fields()