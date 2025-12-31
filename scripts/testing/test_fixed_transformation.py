#!/usr/bin/env python3
"""
Test the fixed transformation function
"""

import asyncio
import aiohttp
import json

async def test_fixed_transformation():
    """Test creating a report with the fixed transformation"""
    
    base_url = "http://localhost:8000"
    
    # Login credentials
    login_data = {
        "email": "sk.tindwal@gmail.com",
        "password": "admin123"
    }
    
    # Test data that mimics what frontend sends
    report_data = {
        "bank_code": "SBI",
        "template_id": "land-property",
        "property_address": "TEST FIXED TRANSFORMATION",
        "report_data": {
            # Nested structure like frontend sends
            "property_details": {
                "property_part_a": {
                    "agreement_to_sell": "TEST_AGREEMENT",
                    "list_of_documents_produced": "TEST_DOCUMENTS",
                    "allotment_letter": "TEST_ALLOTMENT"
                },
                "property_part_b": {
                    "owner_details": "TEST_OWNER",
                    "borrower_name": "TEST_BORROWER"
                }
            },
            "site_characteristics": {
                "site_part_a": {
                    "locality_surroundings": "TEST_LOCALITY"
                }
            },
            "valuation": {
                "valuation_part_a": {
                    "plot_size": "1000 sq ft",
                    "market_rate": "5000 per sq ft"
                }
            },
            # Some flat fields too
            "valuation_date": "2025-12-25",
            "inspection_date": "2025-12-25",
            "applicant_name": "Test Applicant"
        }
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            # Login
            print("🔐 Logging in...")
            async with session.post(f"{base_url}/api/auth/login", json=login_data) as response:
                login_result = await response.json()
                token = login_result["data"]["access_token"]
                print("✅ Login successful")
                
            # Create report
            print("📝 Creating report with nested data...")
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            async with session.post(f"{base_url}/api/reports", json=report_data, headers=headers) as response:
                if response.status == 201:
                    result = await response.json()
                    report_id = result["data"]["report_id"]
                    ref_number = result["data"]["reference_number"]
                    
                    print(f"✅ Report created!")
                    print(f"📋 ID: {report_id}")
                    print(f"📋 Ref: {ref_number}")
                    
                    # Check the structure
                    saved_data = result["data"]["report_data"]
                    
                    print(f"\n🔍 SAVED STRUCTURE ANALYSIS:")
                    print(f"📊 Type: {type(saved_data)}")
                    print(f"📊 Keys: {list(saved_data.keys()) if isinstance(saved_data, dict) else 'Not dict'}")
                    
                    # Check for grouped format
                    if isinstance(saved_data, dict):
                        grouped_count = 0
                        for key, value in saved_data.items():
                            if isinstance(value, dict) and "documents" in value:
                                grouped_count += 1
                                print(f"✅ GROUPED TAB: '{key}' with {len(value['documents'])} documents")
                                
                                # Show first few documents
                                for doc in value['documents'][:3]:
                                    field_id = doc.get('fieldId', 'NO_ID')
                                    field_value = str(doc.get('value', ''))[:30]
                                    print(f"   📄 {field_id}: {field_value}...")
                        
                        if grouped_count > 0:
                            print(f"🎉 SUCCESS: Found {grouped_count} properly grouped tabs!")
                        else:
                            print(f"❌ NO GROUPED STRUCTURE - still flat format")
                            
                    return ref_number
                    
                else:
                    response_text = await response.text()
                    print(f"❌ Failed: {response.status} - {response_text}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("🧪 TESTING FIXED TRANSFORMATION FUNCTION")
    print("🎯 This should create proper grouped structure with documents arrays")
    print("-" * 60)
    asyncio.run(test_fixed_transformation())