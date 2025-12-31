#!/usr/bin/env python3
"""
Find reports in MongoDB Atlas
"""
import os
import sys
sys.path.append('/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend')

# Load environment variables
from dotenv import load_dotenv
load_dotenv('/Users/sandeepjangra/Downloads/development/ValuationAppV1/.env')

from pymongo import MongoClient

def find_reports():
    print("🔍 Finding reports in MongoDB Atlas...")
    
    # Get MongoDB URI from environment
    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        print("❌ MONGODB_URI environment variable not found")
        return
    
    try:
        client = MongoClient(mongodb_uri)
        client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB Atlas: {e}")
        return
    
    print("\n📊 Listing all databases:")
    
    # List all databases
    databases = client.list_database_names()
    for db_name in databases:
        if db_name in ['admin', 'local', 'config']:
            continue
            
        print(f"\n🗂️  Database: {db_name}")
        db = client[db_name]
        
        collections = db.list_collection_names()
        print(f"   Collections: {collections}")
        
        # Check for reports-related collections
        report_collections = [c for c in collections if 'report' in c.lower()]
        if report_collections:
            print(f"   📄 Report-related collections: {report_collections}")
            
            for coll_name in report_collections:
                collection = db[coll_name]
                count = collection.count_documents({})
                print(f"      {coll_name}: {count} documents")
                
                if count > 0:
                    # Sample document
                    sample = collection.find_one()
                    if sample:
                        keys = list(sample.keys())
                        print(f"      Sample keys: {keys[:10]}...")
                        
                        # Check if it has report_data
                        if 'report_data' in sample:
                            report_data = sample['report_data']
                            if isinstance(report_data, dict):
                                data_keys = list(report_data.keys())
                                print(f"      report_data keys: {data_keys[:10]}...")
                                
                                # Check for readonly fields
                                readonly_fields = ['report_reference_number', 'estimated_value_of_land']
                                for field in readonly_fields:
                                    value = report_data.get(field)
                                    if value is not None:
                                        print(f"      {field}: {value}")

if __name__ == "__main__":
    find_reports()