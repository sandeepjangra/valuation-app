#!/usr/bin/env python3
"""
Test save draft with group field handling
"""

import requests
import json

def test_group_fields_save_draft():
    """Test save draft with group field subfields"""
    
    print("🧪 TESTING GROUP FIELDS SAVE DRAFT")
    print("=" * 80)
    
    # Login first
    login_data = {"email": "admin@system.com", "password": "admin123"}
    login_response = requests.post("http://localhost:8000/api/auth/login", json=login_data, timeout=10)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    token = login_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print("✅ Login successful")
    
    # Test data with group subfields
    test_data = {
        "bank_code": "SBI",
        "template_id": "land-property",
        "property_address": "Test Property with Groups",
        "report_data": {
            # Basic fields
            "agreement_to_sell": "Available - Test document",
            "owner_details": "John Doe - Test Owner",
            
            # Group field subfields
            "plot_survey_no": "Survey-123-Test",  # property_location group
            "door_no": "45A-Test",                 # property_location group
            "ts_no_village": "Village-Test",       # property_location group
            "ward_taluka_tehsil": "Taluka-Test",  # property_location group
            "mandal_district": "District-Test",    # property_location group
            
            "socio_economic_class": "high",        # area_classification group
            "urban_rural": "urban",               # area_classification group
            "area_type": "residential",           # area_classification group
            "municipal_corporation": "panchkula", # area_classification group
            
            "longitude": "77.1234",               # coordinates group
            "latitude": "28.5678",                # coordinates group
            
            # Common fields
            "report_reference_number": "TEST/GROUP/001/26122025",
            "valuation_date": "2025-12-26",
            "applicant_name": "Group Fields Test"
        }
    }
    
    print(f"📊 Test data includes {len(test_data['report_data'])} fields")
    print("📄 Group field subfields:")
    print("   🏠 property_location: plot_survey_no, door_no, ts_no_village, ward_taluka_tehsil, mandal_district")
    print("   🏘️ area_classification: socio_economic_class, urban_rural, area_type, municipal_corporation") 
    print("   📍 coordinates: longitude, latitude")
    
    # Create report
    try:
        response = requests.post(
            "http://localhost:8000/api/reports",
            json=test_data,
            headers=headers,
            timeout=15
        )
        
        print(f"\n💾 Create report response: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            if result.get("success"):
                report_id = result["data"]["report_id"]
                report_data = result["data"]["report_data"]
                
                print(f"✅ Report created: {report_id}")
                
                # Analyze the saved structure
                print(f"\n🔍 ANALYZING SAVED STRUCTURE:")
                
                for tab_name, tab_data in report_data.items():
                    print(f"📂 TAB: {tab_name}")
                    
                    if isinstance(tab_data, dict):
                        for section_name, section_data in tab_data.items():
                            print(f"   📁 SECTION: {section_name}")
                            
                            if isinstance(section_data, dict):
                                for field_id, field_value in section_data.items():
                                    if isinstance(field_value, dict):
                                        # This should be a group field
                                        print(f"      🔗 GROUP: {field_id}")
                                        for sub_field_id, sub_value in field_value.items():
                                            print(f"         📄 {sub_field_id}: {sub_value}")
                                    else:
                                        # Regular field
                                        print(f"      📄 {field_id}: {field_value}")
                
                print(f"\n🎯 GROUP FIELD VERIFICATION:")
                
                # Check if group fields are properly structured
                property_details = report_data.get("Property Details", {})
                
                expected_groups = {
                    "property_location": ["plot_survey_no", "door_no", "ts_no_village", "ward_taluka_tehsil", "mandal_district"],
                    "area_classification": ["socio_economic_class", "urban_rural", "area_type", "municipal_corporation"],
                    "coordinates": ["longitude", "latitude"]
                }
                
                for section_name, section_data in property_details.items():
                    if isinstance(section_data, dict):
                        for group_name, expected_subfields in expected_groups.items():
                            if group_name in section_data:
                                group_data = section_data[group_name]
                                if isinstance(group_data, dict):
                                    found_subfields = list(group_data.keys())
                                    missing_subfields = [sf for sf in expected_subfields if sf not in found_subfields]
                                    
                                    print(f"   ✅ {group_name}: {len(found_subfields)} subfields found")
                                    if missing_subfields:
                                        print(f"      ⚠️ Missing: {missing_subfields}")
                                    else:
                                        print(f"      ✅ All subfields present: {found_subfields}")
                                else:
                                    print(f"   ❌ {group_name}: Not a group structure (value: {group_data})")
                
                print(f"\n🎉 GROUP FIELDS TEST COMPLETE!")
                return report_id
            else:
                print(f"❌ Create failed: {result}")
        else:
            print(f"❌ Request failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    test_group_fields_save_draft()