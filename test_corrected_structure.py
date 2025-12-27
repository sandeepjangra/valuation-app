#!/usr/bin/env python3
"""
Test the corrected structure without duplicate report_data nesting
"""

import requests
import json

def test_corrected_structure():
    """Test the corrected structure"""
    
    print("🧪 TESTING CORRECTED STRUCTURE (No Duplicate report_data)")
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
        
        # Test payload
        test_payload = {
            # Regular fields
            "sales_deed": "Corrected Structure Test Sale Deed",
            "borrower_name": "Corrected Test Borrower", 
            "postal_address": "Corrected Structure Address, Test City - 123456",
            "property_description": "Testing corrected structure without duplicate nesting",
            
            # Common fields  
            "valuation_date": "2025-12-27",
            "inspection_date": "2025-12-25",
            "applicant_name": "Corrected Test Applicant",
            "valuation_purpose": "structure_test",
            
            # Table
            "test_table": [
                {"item": "Test Item 1", "value": 100000},
                {"item": "Test Item 2", "value": 200000}
            ]
        }
        
        create_payload = {
            "bank_code": "SBI",
            "template_id": "land-property", 
            "report_data": test_payload
        }
        
        print(f"\n🔨 Creating test report with corrected structure...")
        
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
                
                print(f"✅ Test report created: {report_id}")
                
                print(f"\n📊 CORRECTED STRUCTURE ANALYSIS:")
                
                # Check the structure
                top_level_keys = list(report_data.keys())
                print(f"   📁 Top-level keys in report_data: {top_level_keys}")
                
                expected_keys = ["common_fields", "data", "tables", "template_version"]
                
                structure_correct = True
                
                for expected_key in expected_keys:
                    if expected_key in top_level_keys:
                        print(f"   ✅ {expected_key}: Present")
                        
                        if expected_key == "common_fields":
                            common_fields = report_data[expected_key]
                            if "applicant_name" in common_fields:
                                print(f"      📄 applicant_name: '{common_fields['applicant_name']}'")
                            else:
                                print(f"      ❌ applicant_name missing")
                                structure_correct = False
                                
                        elif expected_key == "data":
                            data_section = report_data[expected_key]
                            print(f"      📄 Data fields: {len(data_section)}")
                            if "postal_address" in data_section:
                                print(f"      📄 postal_address: '{data_section['postal_address']}'")
                            else:
                                print(f"      ❌ postal_address missing")
                                structure_correct = False
                                
                        elif expected_key == "tables":
                            tables_section = report_data[expected_key] 
                            print(f"      📊 Tables: {len(tables_section)}")
                            
                        elif expected_key == "template_version":
                            version = report_data[expected_key]
                            print(f"      📋 Version: {version}")
                    else:
                        print(f"   ❌ {expected_key}: Missing")
                        structure_correct = False
                
                # Check for unwanted nesting
                if "report_data" in report_data:
                    print(f"   ❌ Duplicate 'report_data' found inside report_data!")
                    structure_correct = False
                else:
                    print(f"   ✅ No duplicate 'report_data' nesting")
                
                # Test list API extraction
                print(f"\n🔍 TESTING LIST API EXTRACTION:")
                
                list_response = requests.get(
                    f"http://localhost:8000/api/reports?limit=1&sort_by=created_at&sort_order=desc",
                    headers=headers,
                    timeout=15
                )
                
                if list_response.status_code == 200:
                    list_result = list_response.json()
                    if list_result.get("success") and list_result.get("data"):
                        latest_report = list_result["data"][0]
                        if latest_report.get("report_id") == report_id:
                            
                            list_address = latest_report.get("property_address", "N/A")
                            list_applicant = latest_report.get("applicant_name", "N/A") 
                            
                            print(f"   📄 Listed property_address: '{list_address}'")
                            print(f"   👤 Listed applicant_name: '{list_applicant}'")
                            
                            if list_address != "N/A" and "Corrected Structure Address" in list_address:
                                print(f"      ✅ Address correctly extracted")
                            else:
                                print(f"      ❌ Address extraction failed")
                                structure_correct = False
                            
                            if list_applicant != "N/A" and "Corrected Test Applicant" in list_applicant:
                                print(f"      ✅ Applicant correctly extracted")
                            else:
                                print(f"      ❌ Applicant extraction failed")
                                structure_correct = False
                
                # Final assessment
                print(f"\n🏆 FINAL ASSESSMENT:")
                
                if structure_correct:
                    print(f"   🎉 STRUCTURE CORRECTED SUCCESSFULLY! 🎉")
                    print(f"   ✅ No duplicate report_data nesting")
                    print(f"   ✅ Flat structure: common_fields, data, tables at same level")
                    print(f"   ✅ UI extraction paths should work correctly")
                else:
                    print(f"   ⚠️ Structure issues still exist")
                
                return report_id
                    
        else:
            print(f"❌ Create failed: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_corrected_structure()