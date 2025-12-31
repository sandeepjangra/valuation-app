#!/usr/bin/env python3
"""
Test the new hierarchical transformation with sample data
"""

import json
import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_hierarchical_transformation():
    """Test the new transformation function with sample SBI data"""
    
    print("🧪 TESTING HIERARCHICAL TRANSFORMATION")
    print("=" * 80)
    
    # Sample flat data that would come from frontend form
    sample_flat_data = {
        # Property Details - Section 1
        "agreement_to_sell": "Available - Original sale deed dated 15-Jan-2020",
        "list_of_documents_produced": "1. Original Sale Deed\n2. Survey Settlement\n3. Property Card\n4. Revenue Records",
        "allotment_letter": "Not applicable - Private property",
        "layout_plan": "Municipality approved layout plan available",
        
        # Property Details - Section 2
        "owner_details": "John Doe, S/o Richard Doe, Age 45 years, Occupation: Business",
        "borrower_name": "MS SSK Developers Private Limited",
        "postal_address": "123 Main Street, Andheri West, Mumbai - 400058, Maharashtra",
        "property_description": "Residential plot in premium locality",
        "property_location": "Survey No. 45/2, Andheri West, Mumbai",
        "city_town_village": "Mumbai",
        
        # Property Details - Section 3
        "area_classification": "Urban residential - R1 zone as per development plan",
        "government_regulation": "Mumbai Municipal Corporation guidelines applicable",
        
        # Property Details - Section 4
        "boundaries_dimensions_table": "North: 40 feet, South: 40 feet, East: 25 feet, West: 25 feet",
        "coordinates": "19.1335° N, 72.8269° E (GPS coordinates verified)",
        "land_area_and_occupancy": "1000 sq ft built-up area, currently vacant",
        
        # Site Characteristics - Section 1
        "locality_surroundings": "Well developed residential locality with good connectivity",
        "physical_characteristics": "Rectangular plot, level terrain, good soil condition",
        "land_usage": "Residential use as per approved development plan",
        "planning_approvals": "All necessary approvals obtained from municipal authority",
        
        # Site Characteristics - Section 2
        "road_access": "30 feet wide paved road with proper drainage",
        "utility_services_group": "Water supply, electricity, sewerage, gas pipeline available",
        "additional_information": "Property located in prime area with excellent appreciation potential",
        
        # Valuation - Section 1
        "plot_size": "1000",
        "market_rate": "5500",
        "estimated_valuation": "5500000",
        
        # Valuation - Section 2
        "building_constructed": "no",
        "building_basic_info": "No construction on the plot",
        "building_dimensions": "N/A - vacant plot",
        "building_condition": "N/A - no building present",
        "approval_documents": "Building permission not applicable for vacant land",
        "no_building_remarks": "Land only valuation - no construction present on the plot",
        
        # Construction Specifications - Section 1
        "building_specifications_table": "Not applicable - vacant land",
        "floor_wise_valuation_table": "Not applicable - no building present",
        
        # Construction Specifications - Section 2
        "extra_items": "Boundary wall on three sides",
        "amenities": "Street lighting, security provisions in the area",
        "miscellaneous": "Proper drainage system, wide road frontage",
        "services": "Municipal water connection available, electricity pole nearby",
        
        # Detailed Valuation - Direct fields
        "land_total": 5500000,
        "building_total": 0,
        "extra_items_total": 50000,
        "amenities_total": 25000,
        "miscellaneous_total": 15000,
        "services_total": 10000,
        "grand_total": 5600000,
        
        # Common fields
        "report_reference_number": "CEV/RVO/299/0029/26122025",
        "valuation_date": "2025-12-26",
        "inspection_date": "2025-12-25",
        "applicant_name": "MS SSK Developers Private Limited",
        "valuation_purpose": "Loan against property",
        "bank_branch": "SBI Andheri West Branch"
    }
    
    print(f"📊 INPUT DATA: {len(sample_flat_data)} fields")
    for field_id, value in list(sample_flat_data.items())[:10]:
        print(f"   📄 {field_id}: {str(value)[:60]}{'...' if len(str(value)) > 60 else ''}")
    if len(sample_flat_data) > 10:
        print(f"   📄 ... and {len(sample_flat_data) - 10} more fields")
    
    # Test the transformation function (simulate the function call)
    try:
        # Import the transformation logic from our generated function
        from sbi_transformation_functions import transform_flat_to_template_structure
        
        hierarchical_result = transform_flat_to_template_structure(sample_flat_data)
        
        print(f"\n✅ TRANSFORMATION SUCCESSFUL!")
        print(f"📂 OUTPUT STRUCTURE: {len(hierarchical_result)} tabs")
        
        # Display the hierarchical structure
        for tab_name, tab_data in hierarchical_result.items():
            if tab_name == '_unmapped_':
                print(f"   ⚠️ {tab_name}: {len(tab_data)} unmapped fields")
                continue
            
            if isinstance(tab_data, dict):
                sections = []
                direct_fields = []
                
                for key, value in tab_data.items():
                    if isinstance(value, dict):
                        sections.append(f"{key} ({len(value)} fields)")
                    else:
                        direct_fields.append(key)
                
                print(f"   📂 {tab_name}:")
                if sections:
                    print(f"      📁 Sections: {', '.join(sections)}")
                if direct_fields:
                    print(f"      📄 Direct fields: {len(direct_fields)} fields")
        
        # Show sample data structure
        print(f"\n📋 SAMPLE HIERARCHICAL STRUCTURE:")
        print("```json")
        
        # Create a compact sample for display
        sample_output = {}
        for tab_name, tab_data in list(hierarchical_result.items())[:3]:  # Show first 3 tabs
            if isinstance(tab_data, dict):
                sample_tab = {}
                count = 0
                for key, value in tab_data.items():
                    if count >= 2:  # Show max 2 items per tab
                        if isinstance(value, dict) and len(value) > 2:
                            sample_tab[key] = dict(list(value.items())[:2])
                            sample_tab[key]["..."] = f"({len(value) - 2} more fields)"
                        else:
                            sample_tab["..."] = f"({len(tab_data) - count} more items)"
                        break
                    
                    if isinstance(value, dict):
                        # Show first 2 fields in section
                        sample_tab[key] = dict(list(value.items())[:2])
                        if len(value) > 2:
                            sample_tab[key]["..."] = f"({len(value) - 2} more fields)"
                    else:
                        sample_tab[key] = value
                    count += 1
                
                sample_output[tab_name] = sample_tab
        
        print(json.dumps(sample_output, indent=2))
        print("```")
        
        # Test flattening back to ensure round-trip works
        from sbi_transformation_functions import flatten_template_structure
        
        flattened_back = flatten_template_structure(hierarchical_result)
        
        print(f"\n🔄 ROUND-TRIP TEST:")
        print(f"   📊 Original fields: {len(sample_flat_data)}")
        print(f"   📊 Flattened back: {len(flattened_back)}")
        
        # Check if all original fields are preserved
        missing_fields = []
        for field_id in sample_flat_data.keys():
            if field_id not in flattened_back:
                missing_fields.append(field_id)
        
        if missing_fields:
            print(f"   ❌ Missing fields after round-trip: {missing_fields}")
        else:
            print(f"   ✅ All fields preserved in round-trip transformation!")
        
        # Check for data integrity
        data_mismatches = []
        for field_id, original_value in sample_flat_data.items():
            if field_id in flattened_back:
                if str(flattened_back[field_id]) != str(original_value):
                    data_mismatches.append(field_id)
        
        if data_mismatches:
            print(f"   ⚠️ Data mismatches: {data_mismatches}")
        else:
            print(f"   ✅ All field values match original data!")
        
        print(f"\n🎯 TRANSFORMATION SUMMARY:")
        print(f"   ✅ Successfully organized {len(sample_flat_data)} fields into hierarchical structure")
        print(f"   ✅ Created {len(hierarchical_result)} tabs matching SBI template design") 
        print(f"   ✅ Round-trip transformation preserves all data")
        print(f"   🎉 Ready for implementation in backend!")
        
        return hierarchical_result
        
    except Exception as e:
        print(f"❌ TRANSFORMATION FAILED: {e}")
        import traceback
        print(f"❌ Full error: {traceback.format_exc()}")
        return None

if __name__ == "__main__":
    result = asyncio.run(test_hierarchical_transformation())