#!/usr/bin/env python3
"""
Final investigation - let's look at the actual report and see if we can fix it directly
"""

import requests
import json

def final_investigation():
    """Fix the report structure issue by understanding the root cause"""
    
    print("🔍 FINAL INVESTIGATION - ROOT CAUSE ANALYSIS")
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
    
    # Get the original problematic report
    try:
        response = requests.get(
            f"http://localhost:8000/api/reports/rpt_431b6b6ada7f?organization_id=sk-tindwal",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                report = result["data"]
                report_data = report.get("report_data", {})
                
                print(f"📋 ANALYZING ORIGINAL REPORT: {report.get('report_id')}")
                print(f"🔍 Current structure issues:")
                
                # Identify the exact problems
                problems = []
                
                # Check for empty Property Details with populated _unmapped_
                if "Property Details" in report_data:
                    prop_details = report_data["Property Details"]
                    if prop_details.get("property_part_a") == {} and prop_details.get("property_part_b") == {}:
                        problems.append("Empty Property Details sections")
                
                if "_unmapped_" in report_data and len(report_data["_unmapped_"]) > 0:
                    unmapped = report_data["_unmapped_"]
                    if "property_details" in unmapped:
                        problems.append("Structured data wrongly placed in _unmapped_")
                    
                    # Count flat fields that should be grouped
                    flat_field_count = sum(1 for k, v in unmapped.items() if not isinstance(v, dict))
                    if flat_field_count > 0:
                        problems.append(f"{flat_field_count} flat fields need proper grouping")
                
                print(f"❌ Problems found: {problems}")
                
                # Now let's create the CORRECT structure manually
                print(f"\n🔧 CREATING CORRECT STRUCTURE:")
                
                # Extract data from _unmapped_
                unmapped_data = report_data.get("_unmapped_", {})
                
                corrected_structure = {
                    "Property Details": {
                        "property_part_a": {},
                        "property_part_b": {},
                        "property_part_c": {},
                        "property_part_d": {}
                    }
                }
                
                # Process structured data from _unmapped_
                if "property_details" in unmapped_data and isinstance(unmapped_data["property_details"], dict):
                    structured_prop = unmapped_data["property_details"]
                    
                    for section_key, section_data in structured_prop.items():
                        if section_key in corrected_structure["Property Details"] and isinstance(section_data, dict):
                            # Copy the data from the wrongly placed structured data
                            corrected_structure["Property Details"][section_key].update(section_data)
                            print(f"   ✅ Moved {len(section_data)} fields from _unmapped_.property_details.{section_key}")
                
                # Process flat fields and group them correctly
                field_groups = {
                    "property_location": ["plot_survey_no", "door_no", "ts_no_village", "ward_taluka_tehsil", "mandal_district"],
                    "area_classification": ["socio_economic_class", "urban_rural", "area_type", "municipal_corporation"],
                    "government_regulation": ["state_enactments", "agriculture_conversion"],
                    "coordinates": ["longitude", "latitude"],
                    "land_area_and_occupancy": ["site_area", "valuation_area", "occupied_by"],
                    "no_building_remarks": ["land_only_confirmation", "land_valuation_basis"]
                }
                
                # Group flat fields
                for field_id, field_value in unmapped_data.items():
                    if not isinstance(field_value, dict) and field_value is not None and field_value != "":
                        # Find which group this field belongs to
                        for group_name, group_fields in field_groups.items():
                            if field_id in group_fields:
                                # Determine which section this group belongs to
                                section_map = {
                                    "property_location": "property_part_b",
                                    "area_classification": "property_part_c", 
                                    "government_regulation": "property_part_c",
                                    "coordinates": "property_part_d",
                                    "land_area_and_occupancy": "property_part_d",
                                    "no_building_remarks": "valuation_part_b"  # This might be in Valuation tab
                                }
                                
                                section_id = section_map.get(group_name)
                                if section_id and section_id in corrected_structure["Property Details"]:
                                    if group_name not in corrected_structure["Property Details"][section_id]:
                                        corrected_structure["Property Details"][section_id][group_name] = {}
                                    
                                    corrected_structure["Property Details"][section_id][group_name][field_id] = field_value
                                    print(f"   ✅ Grouped {field_id} into {section_id}.{group_name}")
                                break
                
                # Add other tabs that were in _unmapped_
                for key, value in unmapped_data.items():
                    if key in ["site_characteristics", "valuation", "construction_specifications", "detailed_valuation"] and isinstance(value, dict):
                        tab_mapping = {
                            "site_characteristics": "Site Characteristics",
                            "valuation": "Valuation", 
                            "construction_specifications": "Construction Specifications",
                            "detailed_valuation": "Detailed Valuation"
                        }
                        proper_name = tab_mapping.get(key, key)
                        corrected_structure[proper_name] = value
                        print(f"   ✅ Added {proper_name} tab with {len(value)} sections")
                
                # Keep common fields
                if "_common_fields_" in report_data:
                    corrected_structure["_common_fields_"] = report_data["_common_fields_"]
                    print(f"   ✅ Preserved common fields")
                
                print(f"\n📊 CORRECTED STRUCTURE:")
                for tab_name, tab_content in corrected_structure.items():
                    if isinstance(tab_content, dict):
                        print(f"   📁 {tab_name}: {len(tab_content)} sections")
                        for section_name, section_content in tab_content.items():
                            if isinstance(section_content, dict):
                                print(f"      📂 {section_name}: {len(section_content)} items")
                    else:
                        print(f"   📄 {tab_name}: {tab_content}")
                
                # Now UPDATE the report with the correct structure
                print(f"\n🔧 UPDATING REPORT WITH CORRECT STRUCTURE...")
                
                update_payload = {
                    "report_data": corrected_structure
                }
                
                update_response = requests.patch(
                    f"http://localhost:8000/api/reports/rpt_431b6b6ada7f?organization_id=sk-tindwal",
                    headers=headers,
                    json=update_payload,
                    timeout=30
                )
                
                print(f"📥 Update response: {update_response.status_code}")
                if update_response.status_code == 200:
                    print(f"✅ Report structure corrected successfully!")
                    
                    # Verify the fix
                    verify_response = requests.get(
                        f"http://localhost:8000/api/reports/rpt_431b6b6ada7f?organization_id=sk-tindwal",
                        headers=headers,
                        timeout=10
                    )
                    
                    if verify_response.status_code == 200:
                        verified_report = verify_response.json()["data"]
                        verified_data = verified_report.get("report_data", {})
                        
                        print(f"\n✅ VERIFICATION:")
                        has_unmapped = "_unmapped_" in verified_data and len(verified_data["_unmapped_"]) > 0
                        has_empty_sections = (verified_data.get("Property Details", {}).get("property_part_a") == {} and 
                                            verified_data.get("Property Details", {}).get("property_part_b") == {})
                        
                        if not has_unmapped and not has_empty_sections:
                            print(f"   🎉 ALL ISSUES FIXED! Report now has proper structure.")
                        else:
                            print(f"   ⚠️ Some issues remain:")
                            if has_unmapped:
                                print(f"      - Still has _unmapped_ section with {len(verified_data['_unmapped_'])} items")
                            if has_empty_sections:
                                print(f"      - Still has empty Property Details sections")
                else:
                    print(f"❌ Update failed: {update_response.status_code} - {update_response.text}")
                    
        else:
            print(f"❌ Failed to get report: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    final_investigation()