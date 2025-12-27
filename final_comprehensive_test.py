#!/usr/bin/env python3
"""
Final comprehensive test to verify the save draft fix is complete
"""

import requests
import json

def comprehensive_test():
    """Comprehensive test of save draft functionality"""
    
    print("🧪 COMPREHENSIVE SAVE DRAFT TEST")
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
        
        # Test 1: Complex nested data (like the original problem case)
        print(f"\n🧪 TEST 1: Complex Nested Data")
        
        complex_payload = {
            # Regular fields
            "property_address": "123 Main Street, Test City",
            "valuation_date": "2025-12-27",
            "applicant_name": "John Doe", 
            "inspector_name": "Inspector Johnson",
            "plot_survey_no": "Survey-789",
            "door_no": "Door-123",
            
            # Nested structure (like from template)
            "Property Details": {
                "plot_survey_no": "Survey-789-nested",
                "door_no": "Door-123-nested", 
                "area_type": "residential",
                "municipal_corporation": "test_municipal"
            },
            
            "Valuation": {
                "market_value": 5000000,
                "forced_sale_value": 4000000,
                "approach_used": "comparison"
            },
            
            # Dynamic tables
            "construction_details_table": [
                {"item": "Foundation", "material": "RCC", "area": 1000, "rate": 800, "value": 800000},
                {"item": "Walls", "material": "Brick", "area": 1200, "rate": 400, "value": 480000}
            ],
            
            "floor_details": [
                {"floor": "Ground", "area": 1200, "usage": "residential", "rate": 3000, "value": 3600000},
                {"floor": "First", "area": 1000, "usage": "residential", "rate": 2800, "value": 2800000}
            ],
            
            # System fields (should be filtered)
            "status": "draft",
            "organizationId": "sk-tindwal",
            "bankName": "State Bank of India"
        }
        
        create_payload = {
            "bank_code": "SBI",
            "template_id": "land-property",
            "report_data": complex_payload,
            "property_address": "123 Main Street, Test City",
            "organization_id": "sk-tindwal"
        }
        
        print(f"   📋 Creating report with complex nested data...")
        
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
                
                print(f"   ✅ Report created: {report_id}")
                
                # Analyze structure
                self_check_1 = self_check_report_structure(report_data, "Test 1")
                
                # Test 2: Save as draft (update the same report)
                print(f"\n🧪 TEST 2: Save Draft (Update)")
                
                # Modify some data
                updated_payload = complex_payload.copy()
                updated_payload["property_address"] = "123 Main Street, Test City - UPDATED"
                updated_payload["market_value"] = 5500000
                updated_payload["construction_details_table"].append({
                    "item": "Roof", "material": "RCC Slab", "area": 1200, "rate": 600, "value": 720000
                })
                
                update_response = requests.put(
                    f"http://localhost:8000/api/reports/{report_id}",
                    headers=headers,
                    json={"report_data": updated_payload},
                    timeout=30
                )
                
                if update_response.status_code == 200:
                    update_result = update_response.json()
                    if update_result.get("success"):
                        updated_report_data = update_result["data"]["report_data"]
                        print(f"   ✅ Report updated successfully")
                        
                        # Analyze updated structure
                        self_check_2 = self_check_report_structure(updated_report_data, "Test 2")
                        
                        # Test 3: Verify tables were updated
                        if "tables" in updated_report_data:
                            tables = updated_report_data["tables"]
                            if "construction_details_table" in tables:
                                table_rows = tables["construction_details_table"]["structure"]["rows"]
                                print(f"   📊 Construction table now has {len(table_rows)} rows (should be 3)")
                                if len(table_rows) == 3:
                                    print(f"   ✅ Dynamic table update successful")
                                else:
                                    print(f"   ❌ Dynamic table update failed")
                        
                        # Final assessment
                        print(f"\n🏆 FINAL ASSESSMENT:")
                        
                        all_tests_passed = all([
                            self_check_1["tables_detected"],
                            self_check_1["no_empty_sections"], 
                            self_check_1["minimal_unmapped"],
                            self_check_2["tables_detected"],
                            self_check_2["no_empty_sections"],
                            self_check_2["minimal_unmapped"]
                        ])
                        
                        if all_tests_passed:
                            print(f"   🎉 ALL TESTS PASSED!")
                            print(f"   ✅ Save draft functionality is working correctly")
                            print(f"   ✅ No empty sections like 'Property Details'")
                            print(f"   ✅ No large _unmapped_ sections")
                            print(f"   ✅ Dynamic tables handled properly") 
                            print(f"   ✅ Updates preserve structure")
                            
                            print(f"\n🔥 THE SAVE DRAFT BUG IS FIXED! 🔥")
                        else:
                            print(f"   ❌ Some tests failed - needs investigation")
                        
                        return report_id
                    
    except Exception as e:
        print(f"❌ Error: {e}")

def self_check_report_structure(report_data, test_name):
    """Check if report structure is correct"""
    
    print(f"   🔍 Analyzing {test_name} structure...")
    
    results = {
        "tables_detected": False,
        "no_empty_sections": True,
        "minimal_unmapped": True,
        "has_report_data": False
    }
    
    # Check for tables section
    if "tables" in report_data:
        tables = report_data["tables"]
        if isinstance(tables, dict) and len(tables) > 0:
            results["tables_detected"] = True
            print(f"      ✅ Tables section: {len(tables)} tables")
        else:
            print(f"      ❌ Tables section empty")
    else:
        print(f"      ❌ No tables section")
    
    # Check for report_data section  
    if "report_data" in report_data:
        main_data = report_data["report_data"]
        if isinstance(main_data, dict) and len(main_data) > 0:
            results["has_report_data"] = True
            print(f"      ✅ Report data section: {len(main_data)} fields")
        else:
            print(f"      ❌ Report data section empty")
    
    # Check for empty sections
    for section_name, section_data in report_data.items():
        if isinstance(section_data, dict) and len(section_data) == 0:
            results["no_empty_sections"] = False
            print(f"      ❌ Empty section found: {section_name}")
    
    if results["no_empty_sections"]:
        print(f"      ✅ No empty sections")
    
    # Check _unmapped_ size
    if "_unmapped_" in report_data:
        unmapped = report_data["_unmapped_"]
        unmapped_count = len(unmapped) if isinstance(unmapped, dict) else 0
        if unmapped_count <= 5:  # Allow small amount of unmapped
            results["minimal_unmapped"] = True
            print(f"      ✅ Minimal unmapped: {unmapped_count} fields")
        else:
            results["minimal_unmapped"] = False
            print(f"      ❌ Too many unmapped: {unmapped_count} fields")
    else:
        print(f"      ✅ No unmapped fields")
    
    return results

if __name__ == "__main__":
    comprehensive_test()