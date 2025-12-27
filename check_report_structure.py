#!/usr/bin/env python3
"""
Check the specific report structure in MongoDB
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

async def check_report_structure():
    """Check the structure of the specific report"""
    
    # Load environment variables
    load_dotenv('backend/.env')
    mongodb_uri = os.getenv('MONGODB_URI')
    
    if not mongodb_uri:
        print("❌ MongoDB URI not found in environment")
        return
    
    client = AsyncIOMotorClient(mongodb_uri)
    
    try:
        # Connect to sk-tindwal database
        db = client['sk-tindwal']
        reports_collection = db['reports']
        
        # Find the report with reference number CEV/RVO/299/0022/25122025
        report = await reports_collection.find_one({
            "reference_number": "CEV/RVO/299/0022/25122025"
        })
        
        if not report:
            print("❌ Report not found with reference number: CEV/RVO/299/0022/25122025")
            return
        
        print(f"✅ Found report: {report.get('report_id')}")
        print(f"📋 Reference: {report.get('reference_number')}")
        print(f"📋 Status: {report.get('status')}")
        print(f"📋 Version: {report.get('version')}")
        
        # Analyze the report_data structure
        report_data = report.get('report_data', {})
        print(f"\n🔍 REPORT DATA STRUCTURE ANALYSIS:")
        print(f"📊 Type: {type(report_data)}")
        
        if isinstance(report_data, dict):
            print(f"📊 Total keys: {len(report_data)}")
            print(f"📊 Top-level keys: {list(report_data.keys())[:10]}...")  # First 10 keys
            
            # Check if it has grouped structure
            grouped_tabs = []
            flat_fields = []
            
            for key, value in report_data.items():
                if isinstance(value, dict) and "documents" in value:
                    # This is a grouped tab
                    grouped_tabs.append(key)
                    print(f"✅ GROUPED TAB: '{key}' with {len(value['documents'])} documents")
                    
                    # Show first few documents in this tab
                    for i, doc in enumerate(value['documents'][:3]):
                        print(f"   📄 {i+1}. {doc.get('fieldId', 'NO_ID')}: {str(doc.get('value', 'NO_VALUE'))[:50]}...")
                        
                else:
                    # This is a flat field
                    flat_fields.append(key)
            
            print(f"\n📊 STRUCTURE SUMMARY:")
            print(f"   ✅ Grouped tabs: {len(grouped_tabs)}")
            print(f"   ❌ Flat fields: {len(flat_fields)}")
            
            if grouped_tabs:
                print(f"   📂 Grouped tabs: {grouped_tabs}")
            
            if flat_fields:
                print(f"   📄 Flat fields (first 10): {flat_fields[:10]}")
                
            # Check specific fields that should be grouped
            test_fields = [
                "agreement_to_sell",
                "list_of_documents_produced", 
                "owner_details",
                "borrower_name",
                "locality_surroundings",
                "plot_size"
            ]
            
            print(f"\n🎯 SPECIFIC FIELD LOCATIONS:")
            for field in test_fields:
                location = find_field_location(report_data, field)
                print(f"   {field}: {location}")
        
    except Exception as e:
        print(f"❌ Error checking report: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

def find_field_location(data, field_name):
    """Find where a specific field is located"""
    if not isinstance(data, dict):
        return "Data not a dictionary"
    
    # Check flat structure
    if field_name in data:
        value = str(data[field_name])[:30]
        return f"FLAT (root level): {value}..."
    
    # Check grouped structure
    for tab_name, tab_data in data.items():
        if isinstance(tab_data, dict) and "documents" in tab_data:
            for doc in tab_data["documents"]:
                if doc.get("fieldId") == field_name:
                    value = str(doc.get("value", ""))[:30]
                    return f"GROUPED in '{tab_name}': {value}..."
    
    return "NOT FOUND"

if __name__ == "__main__":
    print("🔍 CHECKING SPECIFIC REPORT STRUCTURE")
    print("🎯 Reference: CEV/RVO/299/0022/25122025")
    print("-" * 60)
    asyncio.run(check_report_structure())