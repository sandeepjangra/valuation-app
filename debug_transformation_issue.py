#!/usr/bin/env python3
"""
Debug transformation in real-time by creating a test report with the same data
"""

import requests
import json

def debug_transformation():
    """Test the transformation function with problematic data"""
    
    print("🔍 DEBUGGING TRANSFORMATION ISSUE")
    print("=" * 80)
    
    # Login to sk-tindwal org
    login_data = {"email": "sk.tindwal@gmail.com", "password": "admin123"}
    login_response = requests.post("http://localhost:8000/api/auth/login", json=login_data, timeout=10)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    token = login_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print("✅ Login successful for sk.tindwal@gmail.com")
    
    # Simulate the exact same payload format that's causing issues
    # This appears to be what the frontend is sending based on the investigation
    test_payload = {
        # This is likely the format causing the issue - mixed structured and flat
        "property_details": {
            "property_part_a": {
                "sales_deed": "NA",
                "ats": "NA", 
                "sanctioned_building_plan": "NA"
            },
            "property_part_b": {
                "city_town_village": "town"
            },
            "property_part_c": {},
            "property_part_d": {
                "coordinates": "NA"
            }
        },
        "valuation": {
            "valuation_part_b": {
                "building_constructed": "no"
            }
        },
        # Plus individual flat fields that need to be organized
        "inspection_date": "2025-12-04",
        "valuation_purpose": "bank_purpose",
        "plot_survey_no": "-",
        "door_no": "-",
        "socio_economic_class": "middle",
        "urban_rural": "rural",
        "area_type": "residential",
        "municipal_corporation": "panchkula",
        "state_enactments": "NA",
        "agriculture_conversion": "NA",
        "longitude": "NA",
        "latitude": "NA",
        "estimated_land_value": "₹0.00",
        "land_only_confirmation": "confirmed",
        "land_valuation_basis": "Valuation restricted to land only",
        "valuation_date": "2025-12-26",
        "applicant_name": "MS SSK Developers",
        # Metadata that should be filtered out
        "status": "draft",
        "bankName": "State Bank of India",
        "templateName": "SBI Land Property Valuation",
        "organizationId": "sk-tindwal",
        "customTemplateId": "69370dd798c7d79553ae4a66",
        "propertyType": "land",
        "reportType": "valuation_report"
    }
    
    print(f"📋 Test payload has {len(test_payload)} top-level keys:")
    for key, value in test_payload.items():
        if isinstance(value, dict):
            print(f"   📁 {key}: dict with {len(value)} keys")
        else:
            print(f"   📄 {key}: {type(value).__name__} = {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}")
    
    # Create report to test transformation
    create_payload = {
        "bank_code": "SBI",
        "template_id": "land-property", 
        "report_data": test_payload,
        "property_address": "Test Property for Debugging",
        "organization_id": "sk-tindwal"
    }
    
    try:
        print(f"\n🔨 Creating test report to debug transformation...")
        
        response = requests.post(
            "http://localhost:8000/api/reports",
            headers=headers,
            json=create_payload,
            timeout=30
        )
        
        print(f"📥 Create report response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                report_id = result["data"]["report_id"]
                print(f"✅ Test report created: {report_id}")
                
                # Now fetch it to see the structure
                fetch_response = requests.get(
                    f"http://localhost:8000/api/reports/{report_id}?organization_id=sk-tindwal",
                    headers=headers,
                    timeout=10
                )
                
                if fetch_response.status_code == 200:
                    report = fetch_response.json()["data"]
                    report_data = report.get("report_data", {})
                    
                    print(f"\n🔍 TRANSFORMATION RESULT ANALYSIS:")
                    print(f"📂 Report data structure ({len(report_data)} top-level keys):")
                    
                    for key, value in report_data.items():
                        if isinstance(value, dict):
                            print(f"   📁 {key}: dict with {len(value)} keys")
                            if key == "_unmapped_" and len(value) > 0:
                                print(f"      ❌ PROBLEM: _unmapped_ section contains:")
                                for unmapped_key in list(value.keys())[:10]:  # Show first 10
                                    print(f"         - {unmapped_key}")
                                if len(value) > 10:
                                    print(f"         ... and {len(value) - 10} more")
                        else:
                            print(f"   📄 {key}: {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}")
                    
                    return report_id
                    
        else:
            print(f"❌ Create failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    debug_transformation()