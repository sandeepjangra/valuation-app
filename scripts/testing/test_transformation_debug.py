#!/usr/bin/env python3
"""
Test what structure is actually being saved in MongoDB
Debug the transformation process
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_transformation_debug():
    """Test what structure is actually being saved during report creation"""
    
    # Test configuration
    base_url = "http://localhost:8000"
    
    # Login credentials for sk.tindwal user
    login_data = {
        "email": "sk.tindwal@gmail.com",
        "password": "admin123"
    }
    
    # Sample report data - let's send very specific test fields
    report_data = {
        "bank_code": "SBI",
        "template_id": "land-property", 
        "property_address": "DEBUG TRANSFORMATION TEST",
        "report_data": {
            # Fields that should be in Property Details > Part A
            "agreement_to_sell": "TEST_AGREEMENT_VALUE",
            "list_of_documents_produced": "TEST_DOCUMENTS_VALUE",
            "allotment_letter": "TEST_ALLOTMENT_VALUE",
            
            # Fields that should be in Property Details > Part B  
            "owner_details": "TEST_OWNER_VALUE",
            "borrower_name": "TEST_BORROWER_VALUE",
            
            # Fields that should be in Site Characteristics
            "locality_surroundings": "TEST_LOCALITY_VALUE",
            
            # Fields that should be in Valuation
            "plot_size": "TEST_PLOT_SIZE",
            "market_rate": "TEST_MARKET_RATE"
        }
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            # Step 1: Login to get authentication token
            print("🔐 Step 1: Logging in as sk.tindwal@gmail.com...")
            async with session.post(f"{base_url}/api/auth/login", json=login_data) as response:
                if response.status != 200:
                    response_text = await response.text()
                    print(f"❌ Login failed with status {response.status}: {response_text}")
                    return
                
                login_result = await response.json()
                token = login_result["data"]["access_token"]
                print(f"✅ Login successful!")
                
            # Step 2: Create new report and analyze structure
            print("📝 Step 2: Creating report with debug fields...")
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            async with session.post(f"{base_url}/api/reports", json=report_data, headers=headers) as response:
                if response.status == 201:
                    result = await response.json()
                    report_data_saved = result["data"]["report_data"]
                    
                    print(f"\n🔍 TRANSFORMATION ANALYSIS:")
                    print(f"📊 Saved structure type: {type(report_data_saved)}")
                    print(f"📊 Top-level keys: {list(report_data_saved.keys()) if isinstance(report_data_saved, dict) else 'Not a dict'}")
                    
                    # Check if it's grouped structure
                    has_grouped_structure = False
                    if isinstance(report_data_saved, dict):
                        for key, value in report_data_saved.items():
                            if isinstance(value, dict) and "documents" in value:
                                has_grouped_structure = True
                                print(f"✅ Found grouped structure in tab: {key}")
                                documents = value["documents"]
                                print(f"   📄 Documents count: {len(documents)}")
                                for doc in documents[:3]:  # Show first 3
                                    print(f"      - {doc.get('fieldId')}: {doc.get('value')}")
                                break
                    
                    if not has_grouped_structure:
                        print(f"❌ NO GROUPED STRUCTURE FOUND!")
                        print(f"📄 Structure appears to be flat:")
                        if isinstance(report_data_saved, dict):
                            flat_fields = [(k, v) for k, v in report_data_saved.items()]
                            print(f"   First 5 fields: {flat_fields[:5]}")
                    
                    # Check specific test fields
                    print(f"\n🎯 TEST FIELD LOCATIONS:")
                    test_fields = [
                        "agreement_to_sell", 
                        "owner_details", 
                        "locality_surroundings",
                        "plot_size"
                    ]
                    
                    for field in test_fields:
                        found_location = find_field_in_structure(report_data_saved, field)
                        print(f"   {field}: {found_location}")
                        
                    return result["data"]["report_id"]
                    
                else:
                    response_text = await response.text()
                    print(f"❌ Failed to create report: {response.status} - {response_text}")
                    return None
                    
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            return None

def find_field_in_structure(data, field_name):
    """Find where a field is located in the data structure"""
    if not isinstance(data, dict):
        return "Not in dict structure"
    
    # Check if field is at root level (flat structure)
    if field_name in data:
        return f"ROOT LEVEL (flat) - value: {data[field_name]}"
    
    # Check if field is in grouped structure
    for tab_name, tab_data in data.items():
        if isinstance(tab_data, dict) and "documents" in tab_data:
            for doc in tab_data["documents"]:
                if doc.get("fieldId") == field_name:
                    return f"GROUPED in {tab_name} - value: {doc.get('value')}"
    
    return "NOT FOUND"

if __name__ == "__main__":
    print("🧪 TRANSFORMATION STRUCTURE DEBUG TEST")
    print("🎯 This will show exactly how fields are being stored")
    print("-" * 60)
    asyncio.run(test_transformation_debug())