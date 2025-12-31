#!/usr/bin/env python3
"""
Debug why applicant_name is not being saved to common_fields
"""

import requests
import json

def debug_applicant_name():
    """Debug the applicant_name field processing"""
    
    print("🔍 DEBUGGING APPLICANT_NAME FIELD PROCESSING")
    print("=" * 80)
    
    # Login to sk-tindwal org
    login_data = {"email": "sk.tindwal@gmail.com", "password": "admin123"}
    
    try:
        login_response = requests.post("http://localhost:8000/api/auth/login", json=login_data, timeout=10)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return
        
        token = login_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        print("✅ Login successful for sk.tindwal@gmail.com")
        
        # Test payload with explicit focus on common fields
        test_payload = {
            # Regular fields
            "sales_deed": "Debug Test Sale Deed",
            "borrower_name": "Debug Test Borrower", 
            "postal_address": "Debug Address for Applicant Test",
            "property_description": "Debugging applicant_name field",
            "bank_branch": "sbi_debug_branch",
            
            # Common fields - these should go to common_fields section
            "valuation_date": "2025-12-27",
            "inspection_date": "2025-12-26",
            "applicant_name": "DEBUG APPLICANT NAME - THIS SHOULD BE IN COMMON_FIELDS",  # 🎯 Focus field
            "valuation_purpose": "debug_test"
        }
        
        create_payload = {
            "bank_code": "SBI",
            "template_id": "land-property", 
            "report_data": test_payload
        }
        
        print(f"\n🔨 Creating debug report...")
        print(f"   🎯 Specifically testing applicant_name: '{test_payload['applicant_name']}'")
        print(f"   📋 Common fields being sent: valuation_date, inspection_date, applicant_name, valuation_purpose")
        
        response = requests.post(
            "http://localhost:8000/api/reports",
            headers=headers,
            json=create_payload,
            timeout=30
        )
        
        if response.status_code == 201:
            result = response.json()
            if result.get("success"):
                report_id = result["data"]["report_id"]
                report_data = result["data"]["report_data"]
                
                print(f"✅ Debug report created: {report_id}")
                
                print(f"\n📊 FIELD PROCESSING ANALYSIS:")
                
                # Check common_fields section
                if "common_fields" in report_data:
                    common_fields = report_data["common_fields"]
                    print(f"   📋 common_fields section:")
                    for field, value in common_fields.items():
                        print(f"      ✅ {field}: '{value}'")
                    
                    # Check specifically for applicant_name
                    if "applicant_name" in common_fields:
                        applicant_value = common_fields["applicant_name"]
                        print(f"\n   🎯 APPLICANT_NAME CHECK:")
                        print(f"      ✅ Found in common_fields: '{applicant_value}'")
                        if "DEBUG APPLICANT NAME" in applicant_value:
                            print(f"      ✅ Correct value saved!")
                        else:
                            print(f"      ❌ Wrong value saved!")
                    else:
                        print(f"\n   🎯 APPLICANT_NAME CHECK:")
                        print(f"      ❌ NOT FOUND in common_fields!")
                        
                        # Check if it ended up in data section instead
                        if "data" in report_data and "applicant_name" in report_data["data"]:
                            data_value = report_data["data"]["applicant_name"]
                            print(f"      ⚠️ Found in data section instead: '{data_value}'")
                            print(f"      🔧 This indicates transformation logic issue")
                        else:
                            print(f"      ❌ Not found in data section either!")
                            print(f"      🚨 Field completely missing - input processing issue")
                else:
                    print(f"   ❌ No common_fields section found!")
                
                # Check data section for completeness
                if "data" in report_data:
                    data_section = report_data["data"]
                    print(f"\n   📄 data section: {len(data_section)} fields")
                    
                    # Check if any common fields accidentally ended up in data
                    common_field_ids = {"valuation_date", "applicant_name", "inspection_date", "valuation_purpose"}
                    misplaced_fields = []
                    for field_id in common_field_ids:
                        if field_id in data_section:
                            misplaced_fields.append(field_id)
                    
                    if misplaced_fields:
                        print(f"      ⚠️ Common fields found in data section: {misplaced_fields}")
                    else:
                        print(f"      ✅ No common fields misplaced in data section")
                
                # Test the extraction with the problematic report
                print(f"\n🔍 TESTING PROBLEMATIC REPORT rpt_cbb21f636c41:")
                
                problem_response = requests.get(
                    "http://localhost:8000/api/reports/rpt_cbb21f636c41",
                    headers=headers,
                    timeout=15
                )
                
                if problem_response.status_code == 200:
                    problem_result = problem_response.json()
                    if problem_result.get("success"):
                        problem_data = problem_result["data"]["report_data"]
                        
                        print(f"   📋 Problem report common_fields:")
                        problem_common = problem_data.get("common_fields", {})
                        for field, value in problem_common.items():
                            print(f"      {field}: '{value}'")
                        
                        if "applicant_name" not in problem_common:
                            print(f"      ❌ applicant_name missing from problem report!")
                            
                            # Check if it's in the data section
                            problem_data_section = problem_data.get("data", {})
                            if "applicant_name" in problem_data_section:
                                print(f"      ⚠️ Found in data section: '{problem_data_section['applicant_name']}'")
                            else:
                                print(f"      ❌ Not in data section either - completely missing!")
                
        else:
            print(f"❌ Create failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_applicant_name()