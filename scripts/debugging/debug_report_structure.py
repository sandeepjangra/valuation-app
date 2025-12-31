#!/usr/bin/env python3

import requests
import json
from pprint import pprint

def debug_report_structure():
    """Debug the actual report structure to understand what's happening"""
    
    BASE_URL = "http://localhost:8000/api"
    
    try:
        # Login
        print("🔐 Logging in...")
        login_data = {
            "email": "admin@sk-tindwal.com",
            "organizationId": "sk-tindwal", 
            "role": "manager"
        }
        
        login_response = requests.post(f"{BASE_URL}/auth/dev-login", json=login_data, timeout=10)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            return
        
        auth_data = login_response.json()
        token = auth_data['data']['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        
        print("✅ Login successful")
        
        # Get the problematic report
        report_id = "rpt_08618a7b9df4"
        print(f"\n📋 Getting report {report_id}...")
        
        report_response = requests.get(f"{BASE_URL}/reports/{report_id}", headers=headers, timeout=10)
        
        if report_response.status_code != 200:
            print(f"❌ Failed to get report: {report_response.status_code}")
            print(report_response.text)
            return
        
        response_json = report_response.json()
        print(f"✅ Retrieved report: {report_id}")
        
        # Debug the actual structure
        print("\n🔍 FULL REPORT STRUCTURE DEBUG:")
        print("="*50)
        print(f"Top level keys: {list(response_json.keys())}")
        
        # Handle the API response wrapper
        if response_json.get('success') and 'data' in response_json:
            report_data = response_json['data']
            print(f"Report data keys: {list(report_data.keys())}")
        else:
            print("❌ Unexpected response structure")
            return
        
        if 'report_data' in report_data:
            report_data_section = report_data['report_data']
            print(f"\nreport_data keys: {list(report_data_section.keys())}")
            
            # Check each section
            for section_name in ['data', 'tables', 'common_fields']:
                if section_name in report_data_section:
                    section = report_data_section[section_name]
                    print(f"\n{section_name} section:")
                    print(f"  Type: {type(section)}")
                    print(f"  Keys: {list(section.keys()) if isinstance(section, dict) else 'Not a dict'}")
                    
                    # Look for table-like fields
                    if isinstance(section, dict):
                        table_fields = []
                        for key, value in section.items():
                            if 'table' in key.lower():
                                table_fields.append(key)
                                print(f"  Found table field '{key}' with type {type(value)}")
                                if isinstance(value, dict):
                                    print(f"    Value keys: {list(value.keys())}")
                        
                        if table_fields:
                            print(f"  Table fields found: {table_fields}")
                        else:
                            print(f"  No table fields found")
                else:
                    print(f"\n{section_name} section: NOT FOUND")
        
        # Test creating a simple report with table
        print(f"\n📝 Testing simple table creation...")
        
        test_form_data = {
            "applicant_name": "Debug Test",
            "simple_table": {
                "columns": [{"columnId": "col1", "columnName": "Column 1"}],
                "rows": [{"col1": "value1"}]
            }
        }
        
        create_data = {
            "bank_code": "SBI",
            "template_id": "land-property", 
            "report_data": test_form_data
        }
        
        print("Creating test report...")
        create_response = requests.post(f"{BASE_URL}/reports", json=create_data, headers=headers, timeout=10)
        
        print(f"Create response status: {create_response.status_code}")
        if create_response.status_code != 201:
            print(f"Create response body: {create_response.text}")
            return
            
        create_result = create_response.json()
        
        # Handle the API response wrapper for created report
        if create_result.get('success') and 'data' in create_result:
            new_report_id = create_result['data'].get('report_id')
        else:
            new_report_id = create_result.get('report_id')  # fallback
            
        print(f"✅ Created test report: {new_report_id}")
        
        # Immediately fetch it back
        if new_report_id:
            print(f"\n📋 Fetching back test report {new_report_id}...")
            fetch_response = requests.get(f"{BASE_URL}/reports/{new_report_id}", headers=headers, timeout=10)
            
            if fetch_response.status_code == 200:
                fetch_response_json = fetch_response.json()
                
                # Handle API response wrapper
                if fetch_response_json.get('success') and 'data' in fetch_response_json:
                    fetch_result = fetch_response_json['data']
                else:
                    fetch_result = fetch_response_json
                    
                print(f"✅ Retrieved test report")
                
                # Check structure of new report
                if 'report_data' in fetch_result:
                    new_report_data = fetch_result['report_data']
                    print(f"\nNEW REPORT STRUCTURE:")
                    print(f"Top keys: {list(new_report_data.keys())}")
                    
                    for section in ['data', 'tables']:
                        if section in new_report_data:
                            section_data = new_report_data[section]
                            print(f"{section} section: {list(section_data.keys()) if isinstance(section_data, dict) else type(section_data)}")
                            
                            if section == 'tables' and 'simple_table' in section_data:
                                print(f"✅ simple_table found in tables section!")
                            elif section == 'data' and 'simple_table' in section_data:
                                print(f"⚠️ simple_table found in data section (should be in tables)")
            else:
                print(f"❌ Failed to fetch test report: {fetch_response.status_code}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_report_structure()