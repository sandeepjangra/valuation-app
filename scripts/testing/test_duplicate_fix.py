#!/usr/bin/env python3
"""
Test the fixed transformation with mixed input data that previously caused duplicates
"""

import requests
import json

def test_mixed_input_fix():
    """Test that mixed input formats are handled correctly without duplicates"""
    
    print("🧪 TESTING FIXED MIXED INPUT HANDLING")
    print("=" * 80)
    
    # Login to sk-tindwal org (the one that had the issue)
    login_data = {"email": "sk.tindwal@gmail.com", "password": "admin123"}
    login_response = requests.post("http://localhost:8000/api/auth/login", json=login_data, timeout=10)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    token = login_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print("✅ Login successful for sk.tindwal@gmail.com")
    
    # Simulate the problematic mixed input format that caused duplicates
    test_data = {
        "bank_code": "SBI",
        "template_id": "land-property",
        "property_address": "Fixed Duplicate Test Property",
        "report_data": {
            # STRUCTURED DATA (like from frontend forms)
            "property_details": {
                "property_part_a": {
                    "agreement_to_sell": "Form Agreement Data",
                    "sales_deed": "Form Sales Deed"
                },
                "property_part_b": {
                    "owner_details": "Form Owner Data"
                }
            },
            
            # FLAT INDIVIDUAL FIELDS (that should be grouped)
            "plot_survey_no": "Individual-Survey-999",
            "door_no": "Individual-Door-888",
            "socio_economic_class": "high",
            "urban_rural": "urban",
            "longitude": "77.9999",
            "latitude": "28.9999",
            
            # METADATA FIELDS (should be filtered out)
            "status": "draft",
            "bankName": "State Bank of India", 
            "templateName": "SBI Land Property Valuation",
            "organizationId": "sk-tindwal",
            "customTemplateId": "test-custom-id",
            "propertyType": "land",
            "reportType": "valuation_report",
            
            # COMMON FIELDS
            "report_reference_number": "FIXED/DUPLICATE/001/26122025",
            "valuation_date": "2025-12-26",
            "applicant_name": "Fixed Duplicate Test"
        }
    }
    
    print(f"📊 Test data simulates problematic mixed format:")
    print(f"   📂 Structured tabs: 1 (property_details)")
    print(f"   📄 Individual fields: 6 (group subfields)")
    print(f"   🏷️ Metadata fields: 7 (should be filtered)")
    print(f"   📋 Common fields: 3")
    
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
                
                # Get the actual saved report
                get_response = requests.get(
                    f"http://localhost:8000/api/reports/{report_id}?organization_id=sk-tindwal",
                    headers=headers,
                    timeout=10
                )
                
                if get_response.status_code == 200:
                    get_result = get_response.json()
                    if get_result.get("success"):
                        report = get_result["data"]
                        
                        print(f"\n✅ FIXED STRUCTURE ANALYSIS:")
                        
                        # Check for duplicate issues
                        issues_found = []
                        
                        # 1. Check for duplicate status fields
                        status_locations = []
                        if "status" in report:
                            status_locations.append("root")
                        if "report_data" in report and "status" in report["report_data"]:
                            status_locations.append("report_data")
                        
                        if len(status_locations) > 1:
                            issues_found.append(f"Duplicate status fields in: {status_locations}")
                        else:
                            print(f"   ✅ No duplicate status fields (found in: {status_locations or 'none'})")
                        
                        # 2. Check for duplicate tab names
                        report_data = report.get("report_data", {})
                        tab_names = list(report_data.keys())
                        duplicate_tabs = []
                        seen_tabs = set()
                        
                        for tab in tab_names:
                            normalized = tab.lower().replace(' ', '_')
                            if normalized in seen_tabs:
                                duplicate_tabs.append(tab)
                            seen_tabs.add(normalized)
                        
                        if duplicate_tabs:
                            issues_found.append(f"Duplicate tab names: {duplicate_tabs}")
                        else:
                            print(f"   ✅ No duplicate tab names")
                        
                        # 3. Check for _unmapped_ section
                        if "_unmapped_" in report_data:
                            if report_data["_unmapped_"]:
                                issues_found.append(f"_unmapped_ section contains: {list(report_data['_unmapped_'].keys())}")
                            else:
                                print(f"   ✅ _unmapped_ section is empty (good)")
                        else:
                            print(f"   ✅ No _unmapped_ section (excellent)")
                        
                        # 4. Check group field organization
                        property_details = report_data.get("Property Details", {})
                        group_fields_found = 0
                        
                        for section_name, section_data in property_details.items():
                            if isinstance(section_data, dict):
                                for field_name, field_value in section_data.items():
                                    if isinstance(field_value, dict) and field_name in ['property_location', 'area_classification', 'coordinates']:
                                        group_fields_found += 1
                                        print(f"   ✅ Group field {field_name}: {len(field_value)} subfields")
                        
                        if group_fields_found == 0:
                            issues_found.append("No group fields found - subfields may be unmapped")
                        
                        # 5. Check metadata filtering
                        metadata_in_report_data = []
                        for key in report_data.keys():
                            if key in ['status', 'bankName', 'templateName', 'organizationId', 'customTemplateId']:
                                metadata_in_report_data.append(key)
                        
                        if metadata_in_report_data:
                            issues_found.append(f"Metadata fields in report_data: {metadata_in_report_data}")
                        else:
                            print(f"   ✅ Metadata fields properly filtered out")
                        
                        # Summary
                        print(f"\n🎯 FINAL ASSESSMENT:")
                        if not issues_found:
                            print(f"   🎉 ALL DUPLICATE ISSUES FIXED!")
                            print(f"   ✅ Clean structure with no duplicates")
                            print(f"   ✅ Proper group field organization") 
                            print(f"   ✅ Metadata fields filtered correctly")
                            print(f"   ✅ No unnecessary _unmapped_ sections")
                        else:
                            print(f"   ⚠️ Issues still present:")
                            for issue in issues_found:
                                print(f"      ❌ {issue}")
                        
                        return len(issues_found) == 0
                        
        else:
            print(f"❌ Request failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return False

if __name__ == "__main__":
    success = test_mixed_input_fix()
    if success:
        print(f"\n🎉 DUPLICATE STRUCTURE ISSUES SUCCESSFULLY RESOLVED!")
    else:
        print(f"\n⚠️ Some issues may remain - check the analysis above")