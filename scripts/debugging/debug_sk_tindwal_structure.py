#!/usr/bin/env python3
"""
Test to reproduce the duplicate field issue and understand the save structure
"""

import requests
import json

def test_sk_tindwal_report():
    """Test report creation in sk-tindwal org to see duplicate structure"""
    
    print("🧪 TESTING SK-TINDWAL REPORT STRUCTURE")
    print("=" * 80)
    
    # Login first
    login_data = {"email": "sk.tindwal@gmail.com", "password": "admin123"}
    login_response = requests.post("http://localhost:8000/api/auth/login", json=login_data, timeout=10)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    token = login_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print("✅ Login successful for sk.tindwal@gmail.com")
    
    # Simple test data
    test_data = {
        "bank_code": "SBI",
        "template_id": "land-property",
        "property_address": "Debug Test Property Address",
        "report_data": {
            # Basic fields only
            "agreement_to_sell": "Test Agreement",
            "owner_details": "Test Owner",
            
            # Group field subfields
            "plot_survey_no": "Test-Survey-123",
            "door_no": "Test-Door-456", 
            
            # Common fields
            "report_reference_number": "DEBUG/TEST/001/26122025",
            "valuation_date": "2025-12-26",
            "applicant_name": "Debug Test"
        }
    }
    
    print(f"📊 Test data: {len(test_data['report_data'])} fields")
    
    # Create report
    try:
        response = requests.post(
            "http://localhost:8000/api/reports",
            json=test_data,
            headers=headers,
            timeout=15
        )
        
        print(f"\n💾 Create response: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            if result.get("success"):
                report_id = result["data"]["report_id"]
                
                print(f"✅ Report created: {report_id}")
                
                # Now fetch the report to see exactly how it's stored
                get_response = requests.get(
                    f"http://localhost:8000/api/reports/{report_id}?organization_id=sk-tindwal",
                    headers=headers,
                    timeout=10
                )
                
                if get_response.status_code == 200:
                    get_result = get_response.json()
                    if get_result.get("success"):
                        report = get_result["data"]
                        
                        print(f"\n🔍 ACTUAL DATABASE STRUCTURE:")
                        print(f"📄 Top-level fields in database:")
                        
                        for key, value in report.items():
                            if isinstance(value, dict):
                                if key == "report_data":
                                    print(f"   📂 {key}: dict with {len(value)} keys")
                                    for sub_key, sub_value in value.items():
                                        if isinstance(sub_value, dict):
                                            print(f"      📁 {sub_key}: dict with {len(sub_value)} keys")
                                        else:
                                            print(f"      📄 {sub_key}: {type(sub_value).__name__}")
                                else:
                                    print(f"   📂 {key}: dict with {len(value)} keys")
                            else:
                                print(f"   📄 {key}: {value}")
                        
                        # Check for duplicates
                        print(f"\n🔍 CHECKING FOR DUPLICATES:")
                        
                        # Look for status field duplicates
                        status_count = 0
                        if "status" in report:
                            status_count += 1
                            print(f"   📄 Root level status: {report['status']}")
                        
                        if "report_data" in report and isinstance(report["report_data"], dict):
                            if "status" in report["report_data"]:
                                status_count += 1
                                print(f"   📄 report_data.status: {report['report_data']['status']}")
                        
                        print(f"   📊 Total 'status' fields found: {status_count}")
                        
                        # Check _unmapped_ content
                        report_data = report.get("report_data", {})
                        if "_unmapped_" in report_data:
                            unmapped = report_data["_unmapped_"]
                            print(f"\n⚠️ _unmapped_ section contains:")
                            if isinstance(unmapped, dict):
                                for field_id, field_value in unmapped.items():
                                    print(f"      📄 {field_id}: {field_value}")
                            else:
                                print(f"      Non-dict value: {unmapped}")
                
        else:
            print(f"❌ Request failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_sk_tindwal_report()