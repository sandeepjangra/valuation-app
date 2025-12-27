#!/usr/bin/env python3
"""
Debug the list API extraction issue
"""

import requests
import json

def debug_list_extraction():
    """Debug why the list API is not extracting address and applicant correctly"""
    
    print("🔍 DEBUGGING LIST API EXTRACTION")
    print("=" * 80)
    
    # Login
    login_data = {"email": "sk.tindwal@gmail.com", "password": "admin123"}
    
    try:
        login_response = requests.post("http://localhost:8000/api/auth/login", json=login_data, timeout=10)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed")
            return
        
        token = login_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get the most recent report
        list_response = requests.get(
            "http://localhost:8000/api/reports?limit=1&sort_by=created_at&sort_order=desc",
            headers=headers,
            timeout=15
        )
        
        if list_response.status_code == 200:
            result = list_response.json()
            if result.get("success") and result.get("data"):
                latest_report = result["data"][0]
                report_id = latest_report.get("report_id")
                
                print(f"📋 Latest report: {report_id}")
                print(f"   📄 Listed property_address: '{latest_report.get('property_address', 'MISSING')}'")
                print(f"   👤 Listed applicant_name: '{latest_report.get('applicant_name', 'MISSING')}'")
                
                # Now get the full report to see the actual structure
                detail_response = requests.get(
                    f"http://localhost:8000/api/reports/{report_id}",
                    headers=headers,
                    timeout=15
                )
                
                if detail_response.status_code == 200:
                    detail_result = detail_response.json()
                    if detail_result.get("success"):
                        full_report = detail_result["data"]
                        
                        print(f"\n📊 FULL REPORT STRUCTURE:")
                        
                        # Check top-level structure
                        print(f"   📁 Top-level keys: {list(full_report.keys())}")
                        
                        # Check common_fields
                        if "common_fields" in full_report:
                            common_fields = full_report["common_fields"]
                            print(f"   ✅ common_fields: {common_fields}")
                        else:
                            print(f"   ❌ No common_fields at root")
                        
                        # Check report_data structure
                        if "report_data" in full_report:
                            report_data = full_report["report_data"]
                            print(f"   📂 report_data keys: {list(report_data.keys())}")
                            
                            if "data" in report_data:
                                data_section = report_data["data"]
                                print(f"   📄 report_data.data keys: {list(data_section.keys())[:10]}...")  # First 10
                                
                                # Check for address fields
                                address_fields = [k for k in data_section.keys() if 'address' in k.lower() or 'postal' in k.lower()]
                                print(f"   🏠 Address-related fields: {address_fields}")
                                
                                if "postal_address" in data_section:
                                    print(f"      postal_address: '{data_section['postal_address']}'")
                            else:
                                print(f"   ❌ No 'data' section in report_data")
                            
                            # Check for old structure
                            if "report_data" in report_data:
                                nested_data = report_data["report_data"]
                                print(f"   📂 Nested report_data keys: {list(nested_data.keys())[:5]}...")
                            
                            if "_common_fields_" in report_data:
                                old_common = report_data["_common_fields_"]
                                print(f"   📂 Old _common_fields_: {old_common}")
                        else:
                            print(f"   ❌ No report_data section")
                        
                        print(f"\n🔧 SIMULATING EXTRACTION LOGIC:")
                        
                        # Simulate the get_report_display_data function
                        property_address = "N/A"
                        applicant_name = "N/A"
                        
                        report_data = full_report.get("report_data", {})
                        
                        if isinstance(report_data, dict):
                            # New format: report_data: { data: {}, tables: {} }
                            if "data" in report_data and isinstance(report_data["data"], dict):
                                address_from_data = report_data["data"].get("postal_address") or report_data["data"].get("property_address")
                                print(f"   🏠 Address from report_data.data: '{address_from_data}'")
                                if address_from_data and address_from_data != "N/A":
                                    property_address = address_from_data
                            
                            # Old format fallback: report_data: { report_data: {} }  
                            elif "report_data" in report_data and isinstance(report_data["report_data"], dict):
                                address_from_nested = report_data["report_data"].get("postal_address") or report_data["report_data"].get("property_address")
                                print(f"   🏠 Address from nested report_data: '{address_from_nested}'")
                                if address_from_nested and address_from_nested != "N/A":
                                    property_address = address_from_nested
                        
                        # If still no address, try root level (legacy)
                        if property_address == "N/A":
                            root_address = full_report.get("property_address")
                            print(f"   🏠 Address from root: '{root_address}'")
                            if root_address:
                                property_address = root_address
                        
                        # Try new format for applicant_name (common_fields)
                        if "common_fields" in full_report and isinstance(full_report["common_fields"], dict):
                            applicant_from_common = full_report["common_fields"].get("applicant_name")
                            print(f"   👤 Applicant from common_fields: '{applicant_from_common}'")
                            if applicant_from_common:
                                applicant_name = applicant_from_common
                        
                        # Old format fallback (_common_fields_ inside report_data)
                        elif isinstance(report_data, dict):
                            if "_common_fields_" in report_data and isinstance(report_data["_common_fields_"], dict):
                                applicant_from_old = report_data["_common_fields_"].get("applicant_name")
                                print(f"   👤 Applicant from old _common_fields_: '{applicant_from_old}'")
                                if applicant_from_old:
                                    applicant_name = applicant_from_old
                        
                        print(f"\n🎯 EXTRACTION RESULTS:")
                        print(f"   📄 Final property_address: '{property_address}'")
                        print(f"   👤 Final applicant_name: '{applicant_name}'")
                        
                        if property_address != "N/A" and applicant_name != "N/A":
                            print(f"   ✅ Extraction should work correctly!")
                        else:
                            print(f"   ❌ Extraction logic has issues")
                            
        else:
            print(f"❌ List API failed: {list_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_list_extraction()