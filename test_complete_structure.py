#!/usr/bin/env python3
"""
Test creating a report with COMPLETE template structure
This mimics what the frontend sends with all fields organized properly
"""

import asyncio
import aiohttp
import json

async def test_complete_report_structure():
    """Create a report with complete template structure"""
    
    base_url = "http://localhost:8000"
    
    # Login credentials
    login_data = {
        "email": "sk.tindwal@gmail.com",
        "password": "admin123"
    }
    
    # Complete report data structure matching your template design
    report_data = {
        "bank_code": "SBI",
        "template_id": "land-property",
        "property_address": "Complete Template Structure Test Property",
        "report_data": {
            # Property Details Tab
            "property_details": {
                "property_part_a": {
                    "agreement_to_sell": "Available",
                    "list_of_documents_produced": "Sale deed, Survey settlement, Patta documents",
                    "allotment_letter": "Available",
                    "layout_plan": "Available",
                    "sales_deed": "Available",
                    "ats": "Available", 
                    "sanctioned_building_plan": "NA"
                },
                "property_part_b": {
                    "owner_details": "Mr. John Doe, S/o Mr. Richard Doe",
                    "borrower_name": "MS SSK Developers",
                    "postal_address": "123 Main Street, Mumbai, Maharashtra - 400001",
                    "property_description": "Residential land plot",
                    "property_location": "Prime location in Mumbai suburban area",
                    "city_town_village": "Mumbai"
                },
                "property_part_c": {
                    "area_classification": "Urban residential area",
                    "government_regulation": "As per Mumbai Municipal Corporation guidelines"
                },
                "property_part_d": {
                    "boundaries_dimensions_table": "North: 40 ft, South: 40 ft, East: 25 ft, West: 25 ft",
                    "coordinates": "19.0760° N, 72.8777° E",
                    "land_area_and_occupancy": "1000 sq ft, vacant land"
                }
            },
            
            # Site Characteristics Tab
            "site_characteristics": {
                "site_part_a": {
                    "locality_surroundings": "Well developed residential locality with good connectivity",
                    "physical_characteristics": "Rectangular plot, level terrain",
                    "land_usage": "Residential",
                    "planning_approvals": "Approved by municipal authority"
                },
                "site_part_b": {
                    "road_access": "30 ft wide paved road access",
                    "utility_services_group": "Water, electricity, drainage available",
                    "additional_information": "Good public transport connectivity"
                }
            },
            
            # Valuation Tab  
            "valuation": {
                "valuation_part_a": {
                    "plot_size": "1000",
                    "market_rate": "5000",
                    "estimated_valuation": "5000000"
                },
                "valuation_part_b": {
                    "building_constructed": "no",
                    "building_basic_info": "",
                    "building_dimensions": "",
                    "building_condition": "",
                    "approval_documents": "",
                    "no_building_remarks": "Land only - no construction present"
                }
            },
            
            # Construction Specifications Tab
            "construction_specifications": {
                "construction_part_a": {
                    "building_specifications_table": "",
                    "floor_wise_valuation_table": ""
                },
                "construction_part_b": {
                    "extra_items": "",
                    "amenities": "",
                    "miscellaneous": "",
                    "services": ""
                }
            },
            
            # Detailed Valuation Tab
            "detailed_valuation": {
                "land_total": 5000000,
                "building_total": 0,
                "extra_items_total": 0,
                "amenities_total": 0,
                "miscellaneous_total": 0,
                "services_total": 0,
                "grand_total": 5000000
            },
            
            # Common fields (not in tabs)
            "report_reference_number": "",  # Auto-generated
            "valuation_date": "2025-12-25",
            "inspection_date": "2025-12-04",
            "applicant_name": "MS SSK Developers",
            "valuation_purpose": "bank_purpose",
            "bank_branch": "sbi_mumbai_main",
            "plot_survey_no": "123/45",
            "door_no": "456",
            "ts_no_village": "Mumbai",
            "ward_taluka_tehsil": "Mumbai Suburban",
            "mandal_district": "Mumbai",
            "socio_economic_class": "Middle class",
            "urban_rural": "urban",
            "area_type": "residential",
            "municipal_corporation": "Brihanmumbai Municipal Corporation",
            "state_enactments": "Maharashtra State regulations",
            "agriculture_conversion": "Not applicable",
            "longitude": "72.8777",
            "latitude": "19.0760",
            "site_area": "1000",
            "valuation_area": "1000",
            "occupied_by": "Vacant",
            "locality_classification": "residential",
            "surrounding_area": "developed",
            "civic_amenities_feasibility": "The basic facilities are available at a distance of about 2.0 km to 5.0 km",
            "land_level_topography": "level",
            "land_shape": "rectangular",
            "flooding_possibility": "none",
            "usage_type": "residential",
            "usage_restrictions": "Only for Residential Purposes",
            "town_planning_approved": "yes",
            "corner_or_intermittent": "intermittent",
            "road_facilities": "yes", 
            "road_type_present": "cc_road",
            "road_width": "below_20",
            "landlocked_status": "no",
            "water_potentiality": "yes",
            "underground_sewerage": "yes",
            "power_supply_available": "yes",
            "site_advantages": "Prime location with good connectivity",
            "special_remarks": "Property suitable for residential construction",
            "north_south_dimension": 40,
            "east_west_dimension": 25,
            "total_extent_plot": 1000,
            "market_rate_min": 4500,
            "market_rate_max": 5500,
            "registrar_rate": 4000,
            "valuation_rate": 5000,
            "estimated_land_value": "₹50,00,000",
            "building_type": "",
            "construction_type": "",
            "construction_year": None,
            "number_of_floors": None,
            "floor_height": None,
            "plinth_area_floorwise": None,
            "exterior_condition": "",
            "interior_condition": "",
            "building_age_remarks": "",
            "approved_map_date_validity": "",
            "approved_map_authority": "",
            "map_authenticity_verified": "",
            "valuer_comments_authenticity": "",
            "land_only_confirmation": "confirmed",
            "land_valuation_basis": "Valuation restricted to land only as no building exists on the property."
        }
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            # Login
            print("🔐 Logging in as sk.tindwal@gmail.com...")
            async with session.post(f"{base_url}/api/auth/login", json=login_data) as response:
                login_result = await response.json()
                token = login_result["data"]["access_token"]
                print("✅ Login successful")
                
            # Create complete report
            print("📝 Creating report with COMPLETE template structure...")
            print(f"📊 Total fields in report_data: {count_total_fields(report_data['report_data'])}")
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            async with session.post(f"{base_url}/api/reports", json=report_data, headers=headers) as response:
                if response.status == 201:
                    result = await response.json()
                    report_id = result["data"]["report_id"]
                    ref_number = result["data"]["reference_number"]
                    
                    print(f"✅ Complete report created!")
                    print(f"📋 ID: {report_id}")
                    print(f"📋 Reference: {ref_number}")
                    
                    # Analyze the saved structure
                    saved_data = result["data"]["report_data"]
                    
                    print(f"\n🔍 SAVED STRUCTURE ANALYSIS:")
                    analyze_structure(saved_data)
                    
                    return ref_number
                    
                else:
                    response_text = await response.text()
                    print(f"❌ Failed to create report: {response.status}")
                    print(f"Response: {response_text}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

def count_total_fields(data, prefix=""):
    """Recursively count all fields in the data structure"""
    count = 0
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                count += count_total_fields(value, f"{prefix}.{key}" if prefix else key)
            else:
                count += 1
    return count

def analyze_structure(data):
    """Analyze and report on the data structure"""
    if not isinstance(data, dict):
        print(f"❌ Data is not a dictionary: {type(data)}")
        return
    
    print(f"📊 Total top-level keys: {len(data)}")
    
    # Check for grouped vs flat structure
    grouped_tabs = []
    flat_fields = []
    nested_objects = []
    
    for key, value in data.items():
        if isinstance(value, dict):
            if "documents" in value:
                # This is a grouped tab with documents array
                grouped_tabs.append(key)
                print(f"✅ GROUPED TAB: '{key}' with {len(value['documents'])} documents")
            else:
                # This is a nested object (old structure)
                nested_objects.append(key)
                sub_field_count = count_total_fields(value)
                print(f"📁 NESTED OBJECT: '{key}' with {sub_field_count} sub-fields")
        else:
            # This is a flat field
            flat_fields.append(key)
    
    print(f"\n📊 STRUCTURE SUMMARY:")
    print(f"   ✅ Grouped tabs (new format): {len(grouped_tabs)}")
    print(f"   📁 Nested objects (old format): {len(nested_objects)}")  
    print(f"   📄 Flat fields: {len(flat_fields)}")
    
    if grouped_tabs:
        print(f"   🎉 GROUPED TABS: {grouped_tabs}")
    
    if nested_objects:
        print(f"   📁 NESTED OBJECTS: {nested_objects}")
        
    if flat_fields and len(flat_fields) <= 10:
        print(f"   📄 FLAT FIELDS: {flat_fields}")
    elif flat_fields:
        print(f"   📄 FLAT FIELDS (first 10): {flat_fields[:10]}...")

if __name__ == "__main__":
    print("🧪 TESTING COMPLETE TEMPLATE STRUCTURE")
    print("🎯 This creates a report with ALL fields organized in proper structure")
    print("-" * 70)
    asyncio.run(test_complete_report_structure())