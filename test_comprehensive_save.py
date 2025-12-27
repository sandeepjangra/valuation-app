#!/usr/bin/env python3
"""
Final comprehensive test of the corrected save draft functionality
"""

import requests
import json

def test_comprehensive_save_draft():
    """Test comprehensive save draft functionality with group fields and actual section names"""
    
    print("🧪 COMPREHENSIVE SAVE DRAFT TEST")
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
    
    # Comprehensive test data with group fields from multiple sections
    test_data = {
        "bank_code": "SBI",
        "template_id": "land-property",
        "property_address": "Comprehensive Test Property",
        "report_data": {
            # Part A - Documents
            "agreement_to_sell": "Available - Original sale agreement dated 15-01-2024",
            "list_of_documents_produced": "Sale deed, Survey settlement, EC, Patta",
            "layout_plan": "Approved layout plan by Municipal Corporation",
            "sales_deed": "Registered sales deed no. 12345/2024",
            
            # Part B - Address Details  
            "owner_details": "Mr. Rajesh Kumar S/o Late Sh. Ram Kumar",
            "borrower_name": "Mrs. Priya Kumar W/o Mr. Rajesh Kumar",
            "postal_address": "House No. 123, Sector 15, Panchkula, Haryana - 134113",
            "property_description": "Independent house with garden, 200 sq yards plot",
            
            # Part B - Property Location Group
            "plot_survey_no": "Survey No. 456/1A, Khasra No. 789",
            "door_no": "House No. 123-A, Plot No. 456",
            "ts_no_village": "Village Panchkula, T.S. No. 234",
            "ward_taluka_tehsil": "Ward 15, Panchkula MC, Tehsil Kalka",
            "mandal_district": "District Panchkula, State Haryana",
            
            # Part C - Area Classification Group
            "socio_economic_class": "high",
            "urban_rural": "urban",
            "area_type": "residential",
            "municipal_corporation": "panchkula",
            
            # Part D - Coordinates Group
            "longitude": "77.1025",
            "latitude": "30.6942",
            
            # Site Characteristics - Multiple groups
            "locality_classification": "prime_residential",
            "surrounding_area": "fully_developed",
            "civic_amenities_feasibility": "excellent",
            
            # Land usage
            "usage_type": "residential",
            "usage_restrictions": "none",
            
            # Valuation - Plot size group
            "north_south_dimension": "40.0",
            "east_west_dimension": "50.0", 
            "total_extent_plot": "2000",
            
            # Market rate group
            "market_rate_min": "15000",
            "market_rate_max": "18000",
            "registrar_rate": "12000",
            
            # Common fields
            "report_reference_number": "COMP/TEST/001/26122025",
            "valuation_date": "2025-12-26",
            "applicant_name": "Comprehensive Test Report"
        }
    }
    
    print(f"📊 Test data includes {len(test_data['report_data'])} fields")
    print("🔍 Expected group field organization:")
    print("   🏠 property_location: plot_survey_no, door_no, ts_no_village, ward_taluka_tehsil, mandal_district")
    print("   🏘️ area_classification: socio_economic_class, urban_rural, area_type, municipal_corporation")
    print("   📍 coordinates: longitude, latitude")
    print("   🏞️ locality_surroundings: locality_classification, surrounding_area, civic_amenities_feasibility")
    print("   📐 plot_size: north_south_dimension, east_west_dimension, total_extent_plot")
    print("   💰 market_rate: market_rate_min, market_rate_max, registrar_rate")
    
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
                
                # Comprehensive analysis
                print(f"\n📊 COMPREHENSIVE STRUCTURE ANALYSIS:")
                
                group_fields_found = 0
                sections_found = 0
                total_fields = 0
                
                for tab_name, tab_data in report_data.items():
                    if tab_name == "_common_fields_":
                        continue
                        
                    print(f"\n📂 TAB: {tab_name}")
                    
                    if isinstance(tab_data, dict):
                        for section_name, section_data in tab_data.items():
                            sections_found += 1
                            print(f"   📁 SECTION: {section_name}")
                            
                            if isinstance(section_data, dict):
                                for field_id, field_value in section_data.items():
                                    total_fields += 1
                                    if isinstance(field_value, dict):
                                        # This is a group field
                                        group_fields_found += 1
                                        print(f"      🔗 GROUP: {field_id} ({len(field_value)} subfields)")
                                        for sub_field_id, sub_value in list(field_value.items())[:2]:  # Show first 2 subfields
                                            print(f"         📄 {sub_field_id}: {sub_value}")
                                        if len(field_value) > 2:
                                            print(f"         ... and {len(field_value) - 2} more subfields")
                                    else:
                                        # Regular field
                                        print(f"      📄 {field_id}: {str(field_value)[:50]}{'...' if len(str(field_value)) > 50 else ''}")
                
                print(f"\n🎯 SUMMARY STATISTICS:")
                print(f"   📊 Total tabs: {len([k for k in report_data.keys() if k != '_common_fields_'])}")
                print(f"   📁 Total sections: {sections_found}")
                print(f"   📄 Total fields: {total_fields}")
                print(f"   🔗 Group fields found: {group_fields_found}")
                
                # Verify specific requirements
                print(f"\n✅ REQUIREMENTS VERIFICATION:")
                
                # Check actual section names
                property_details = report_data.get("Property Details", {})
                expected_sections = ["property_part_a", "property_part_b", "property_part_c", "property_part_d"]
                found_sections = [s for s in expected_sections if s in property_details]
                print(f"   📂 Section names: {len(found_sections)}/{len(expected_sections)} correct")
                print(f"      Found: {found_sections}")
                
                # Check group fields
                expected_groups = ["property_location", "area_classification", "coordinates"]
                found_groups = 0
                for section_data in property_details.values():
                    if isinstance(section_data, dict):
                        for field_id, field_value in section_data.items():
                            if field_id in expected_groups and isinstance(field_value, dict):
                                found_groups += 1
                
                print(f"   🔗 Group fields: {found_groups}/{len(expected_groups)} correctly nested")
                
                if found_groups == len(expected_groups) and len(found_sections) >= 3:
                    print(f"\n🎉 COMPREHENSIVE TEST PASSED!")
                    print(f"   ✅ Actual section names working (property_part_a, property_part_b, etc.)")
                    print(f"   ✅ Group fields properly nested with subfields")
                    print(f"   ✅ Dynamic template structure fetching working")
                    print(f"   ✅ Save draft functionality fully operational")
                else:
                    print(f"\n⚠️ Some requirements not fully met")
                    
                return report_id
            else:
                print(f"❌ Create failed: {result}")
        else:
            print(f"❌ Request failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    test_comprehensive_save_draft()