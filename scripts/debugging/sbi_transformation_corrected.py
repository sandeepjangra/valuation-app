#!/usr/bin/env python3
"""
CORRECTED transformation functions with actual section names and proper group field handling
Based on actual SBI template structure from API
"""

def transform_flat_to_template_structure_corrected(flat_data):
    """
    Transform flat data to hierarchical structure using ACTUAL section names and group handling
    """
    
    # Complete field mapping from actual SBI template
    FIELD_MAPPING = {
        "agreement_to_sell": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "textarea"
        },
        "list_of_documents_produced": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "textarea"
        },
        "allotment_letter": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "textarea"
        },
        "layout_plan": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "textarea"
        },
        "sales_deed": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "textarea"
        },
        "ats": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "textarea"
        },
        "sanctioned_building_plan": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "textarea"
        },
        "owner_details": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "textarea"
        },
        "borrower_name": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "textarea"
        },
        "postal_address": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "textarea"
        },
        "property_description": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "textarea"
        },
        "property_location": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "group"
        },
        "plot_survey_no": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "text",
            "parent_group": "property_location"
        },
        "door_no": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "text",
            "parent_group": "property_location"
        },
        "ts_no_village": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "text",
            "parent_group": "property_location"
        },
        "ward_taluka_tehsil": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "text",
            "parent_group": "property_location"
        },
        "mandal_district": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "text",
            "parent_group": "property_location"
        },
        "city_town_village": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "select"
        },
        "area_classification": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "group"
        },
        "socio_economic_class": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "select",
            "parent_group": "area_classification"
        },
        "urban_rural": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "select",
            "parent_group": "area_classification"
        },
        "area_type": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "select",
            "parent_group": "area_classification"
        },
        "municipal_corporation": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "select",
            "parent_group": "area_classification"
        },
        "government_regulation": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "group"
        },
        "state_enactments": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "text",
            "parent_group": "government_regulation"
        },
        "agriculture_conversion": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "text",
            "parent_group": "government_regulation"
        },
        "boundaries_dimensions_table": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "table"
        },
        "coordinates": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "group"
        },
        "longitude": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "number",
            "parent_group": "coordinates"
        },
        "latitude": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "number",
            "parent_group": "coordinates"
        },
        "land_area_and_occupancy": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "group"
        },
        "site_area": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "number",
            "parent_group": "land_area_and_occupancy"
        },
        "valuation_area": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "number",
            "parent_group": "land_area_and_occupancy"
        },
        "occupied_by": {
            "tab": "Property Details",
            "section_name": "Unknown Section",
            "type": "text",
            "parent_group": "land_area_and_occupancy"
        },
        "locality_surroundings": {
            "tab": "Site Characteristics",
            "section_name": "Unknown Section",
            "type": "group"
        },
        "locality_classification": {
            "tab": "Site Characteristics",
            "section_name": "Unknown Section",
            "type": "select",
            "parent_group": "locality_surroundings"
        },
        "surrounding_area": {
            "tab": "Site Characteristics",
            "section_name": "Unknown Section",
            "type": "select",
            "parent_group": "locality_surroundings"
        },
        "civic_amenities_feasibility": {
            "tab": "Site Characteristics",
            "section_name": "Unknown Section",
            "type": "textarea",
            "parent_group": "locality_surroundings"
        },
        "physical_characteristics": {
            "tab": "Site Characteristics",
            "section_name": "Unknown Section",
            "type": "group"
        },
        "land_level_topography": {
            "tab": "Site Characteristics",
            "section_name": "Unknown Section",
            "type": "select",
            "parent_group": "physical_characteristics"
        },
        "land_shape": {
            "tab": "Site Characteristics",
            "section_name": "Unknown Section",
            "type": "select",
            "parent_group": "physical_characteristics"
        },
        "flooding_possibility": {
            "tab": "Site Characteristics",
            "section_name": "Unknown Section",
            "type": "select",
            "parent_group": "physical_characteristics"
        },
        "land_usage": {
            "tab": "Site Characteristics",
            "section_name": "Unknown Section",
            "type": "group"
        },
        "usage_type": {
            "tab": "Site Characteristics",
            "section_name": "Unknown Section",
            "type": "select",
            "parent_group": "land_usage"
        },
        "usage_restrictions": {
            "tab": "Site Characteristics",
            "section_name": "Unknown Section",
            "type": "textarea",
            "parent_group": "land_usage"
        },
        "planning_approvals": {
            "tab": "Site Characteristics",
            "section_name": "Unknown Section",
            "type": "group"
        },
        "town_planning_approved": {
            "tab": "Site Characteristics",
            "section_name": "Unknown Section",
            "type": "select",
            "parent_group": "planning_approvals"
        },
        "corner_or_intermittent": {
            "tab": "Site Characteristics",
            "section_name": "Unknown Section",
            "type": "select",
            "parent_group": "planning_approvals"
        },
        "road_access": {
            "tab": "Site Characteristics",
            "section_name": "Unknown Section",
            "type": "group"
        },
        "road_facilities": {
            "tab": "Site Characteristics",
            "section_name": "Unknown Section",
            "type": "select",
            "parent_group": "road_access"
        },
        "road_type_present": {
            "tab": "Site Characteristics",
            "section_name": "Unknown Section",
            "type": "select",
            "parent_group": "road_access"
        },
        "road_width": {
            "tab": "Site Characteristics",
            "section_name": "Unknown Section",
            "type": "select",
            "parent_group": "road_access"
        },
        "landlocked_status": {
            "tab": "Site Characteristics",
            "section_name": "Unknown Section",
            "type": "select",
            "parent_group": "road_access"
        },
        "utility_services_group": {
            "tab": "Site Characteristics",
            "section_name": "Unknown Section",
            "type": "group"
        },
        "water_potentiality": {
            "tab": "Site Characteristics",
            "section_name": "Unknown Section",
            "type": "select",
            "parent_group": "utility_services_group"
        },
        "underground_sewerage": {
            "tab": "Site Characteristics",
            "section_name": "Unknown Section",
            "type": "select",
            "parent_group": "utility_services_group"
        },
        "power_supply_available": {
            "tab": "Site Characteristics",
            "section_name": "Unknown Section",
            "type": "select",
            "parent_group": "utility_services_group"
        },
        "additional_information": {
            "tab": "Site Characteristics",
            "section_name": "Unknown Section",
            "type": "group"
        },
        "site_advantages": {
            "tab": "Site Characteristics",
            "section_name": "Unknown Section",
            "type": "text",
            "parent_group": "additional_information"
        },
        "special_remarks": {
            "tab": "Site Characteristics",
            "section_name": "Unknown Section",
            "type": "text",
            "parent_group": "additional_information"
        },
        "plot_size": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "group"
        },
        "north_south_dimension": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "number",
            "parent_group": "plot_size"
        },
        "east_west_dimension": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "number",
            "parent_group": "plot_size"
        },
        "total_extent_plot": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "number",
            "parent_group": "plot_size"
        },
        "market_rate": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "group"
        },
        "market_rate_min": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "currency",
            "parent_group": "market_rate"
        },
        "market_rate_max": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "currency",
            "parent_group": "market_rate"
        },
        "registrar_rate": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "currency",
            "parent_group": "market_rate"
        },
        "estimated_valuation": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "group"
        },
        "valuation_rate": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "currency",
            "parent_group": "estimated_valuation"
        },
        "estimated_land_value": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "currency",
            "parent_group": "estimated_valuation"
        },
        "building_constructed": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "select"
        },
        "building_basic_info": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "group"
        },
        "building_type": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "select",
            "parent_group": "building_basic_info"
        },
        "construction_type": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "select",
            "parent_group": "building_basic_info"
        },
        "construction_year": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "number",
            "parent_group": "building_basic_info"
        },
        "building_dimensions": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "group"
        },
        "number_of_floors": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "number",
            "parent_group": "building_dimensions"
        },
        "floor_height": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "number",
            "parent_group": "building_dimensions"
        },
        "plinth_area_floorwise": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "number",
            "parent_group": "building_dimensions"
        },
        "building_condition": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "group"
        },
        "exterior_condition": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "select",
            "parent_group": "building_condition"
        },
        "interior_condition": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "select",
            "parent_group": "building_condition"
        },
        "building_age_remarks": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "textarea",
            "parent_group": "building_condition"
        },
        "approval_documents": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "group"
        },
        "approved_map_date_validity": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "date",
            "parent_group": "approval_documents"
        },
        "approved_map_authority": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "select",
            "parent_group": "approval_documents"
        },
        "map_authenticity_verified": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "select",
            "parent_group": "approval_documents"
        },
        "valuer_comments_authenticity": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "textarea",
            "parent_group": "approval_documents"
        },
        "no_building_remarks": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "group"
        },
        "land_only_confirmation": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "select",
            "parent_group": "no_building_remarks"
        },
        "land_valuation_basis": {
            "tab": "Valuation",
            "section_name": "Unknown Section",
            "type": "textarea",
            "parent_group": "no_building_remarks"
        },
        "building_specifications_table": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "dynamic_table"
        },
        "floor_wise_valuation_table": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "dynamic_table"
        },
        "extra_items": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "group"
        },
        "portico": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "currency",
            "parent_group": "extra_items"
        },
        "ornamental_front_door": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "currency",
            "parent_group": "extra_items"
        },
        "sitout_verandah_grills": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "currency",
            "parent_group": "extra_items"
        },
        "overhead_water_tank": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "currency",
            "parent_group": "extra_items"
        },
        "extra_steel_gates": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "currency",
            "parent_group": "extra_items"
        },
        "amenities": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "group"
        },
        "wardrobes": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "currency",
            "parent_group": "amenities"
        },
        "glazed_tiles": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "currency",
            "parent_group": "amenities"
        },
        "extra_sinks_bathtubs": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "currency",
            "parent_group": "amenities"
        },
        "marble_ceramic_flooring": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "currency",
            "parent_group": "amenities"
        },
        "interior_decorations": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "currency",
            "parent_group": "amenities"
        },
        "architectural_elevation": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "currency",
            "parent_group": "amenities"
        },
        "paneling_works": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "currency",
            "parent_group": "amenities"
        },
        "aluminum_works": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "currency",
            "parent_group": "amenities"
        },
        "aluminum_handrails": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "currency",
            "parent_group": "amenities"
        },
        "false_ceiling": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "currency",
            "parent_group": "amenities"
        },
        "miscellaneous": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "group"
        },
        "separate_toilet": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "currency",
            "parent_group": "miscellaneous"
        },
        "separate_lumber_room": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "currency",
            "parent_group": "miscellaneous"
        },
        "separate_water_tank_sump": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "currency",
            "parent_group": "miscellaneous"
        },
        "trees_gardening": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "currency",
            "parent_group": "miscellaneous"
        },
        "services": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "group"
        },
        "water_supply_arrangements": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "currency",
            "parent_group": "services"
        },
        "drainage_arrangements": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "currency",
            "parent_group": "services"
        },
        "compound_wall": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "currency",
            "parent_group": "services"
        },
        "cb_deposits_fittings": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "currency",
            "parent_group": "services"
        },
        "pavement": {
            "tab": "Construction Specifications",
            "section_name": "Unknown Section",
            "type": "currency",
            "parent_group": "services"
        },
        "report_reference_number": {
            "tab": "_common_fields_",
            "section_name": "None",
            "type": "text"
        },
        "valuation_date": {
            "tab": "_common_fields_",
            "section_name": "None",
            "type": "date"
        },
        "inspection_date": {
            "tab": "_common_fields_",
            "section_name": "None",
            "type": "date"
        },
        "applicant_name": {
            "tab": "_common_fields_",
            "section_name": "None",
            "type": "text"
        },
        "valuation_purpose": {
            "tab": "_common_fields_",
            "section_name": "None",
            "type": "select"
        },
        "bank_branch": {
            "tab": "_common_fields_",
            "section_name": "None",
            "type": "select_dynamic"
        },
    }
    
    # Group field definitions with subfields
    GROUP_FIELDS = {
        "property_location": ["plot_survey_no", "door_no", "ts_no_village", "ward_taluka_tehsil", "mandal_district"],
        "area_classification": ["socio_economic_class", "urban_rural", "area_type", "municipal_corporation"],
        "government_regulation": ["state_enactments", "agriculture_conversion"],
        "coordinates": ["longitude", "latitude"],
        "land_area_and_occupancy": ["site_area", "valuation_area", "occupied_by"],
        "locality_surroundings": ["locality_classification", "surrounding_area", "civic_amenities_feasibility"],
        "physical_characteristics": ["land_level_topography", "land_shape", "flooding_possibility"],
        "land_usage": ["usage_type", "usage_restrictions"],
        "planning_approvals": ["town_planning_approved", "corner_or_intermittent"],
        "road_access": ["road_facilities", "road_type_present", "road_width", "landlocked_status"],
        "utility_services_group": ["water_potentiality", "underground_sewerage", "power_supply_available"],
        "additional_information": ["site_advantages", "special_remarks"],
        "plot_size": ["north_south_dimension", "east_west_dimension", "total_extent_plot"],
        "market_rate": ["market_rate_min", "market_rate_max", "registrar_rate"],
        "estimated_valuation": ["valuation_rate", "estimated_land_value"],
        "building_basic_info": ["building_type", "construction_type", "construction_year"],
        "building_dimensions": ["number_of_floors", "floor_height", "plinth_area_floorwise"],
        "building_condition": ["exterior_condition", "interior_condition", "building_age_remarks"],
        "approval_documents": ["approved_map_date_validity", "approved_map_authority", "map_authenticity_verified", "valuer_comments_authenticity"],
        "no_building_remarks": ["land_only_confirmation", "land_valuation_basis"],
        "extra_items": ["portico", "ornamental_front_door", "sitout_verandah_grills", "overhead_water_tank", "extra_steel_gates"],
        "amenities": ["wardrobes", "glazed_tiles", "extra_sinks_bathtubs", "marble_ceramic_flooring", "interior_decorations", "architectural_elevation", "paneling_works", "aluminum_works", "aluminum_handrails", "false_ceiling"],
        "miscellaneous": ["separate_toilet", "separate_lumber_room", "separate_water_tank_sump", "trees_gardening"],
        "services": ["water_supply_arrangements", "drainage_arrangements", "compound_wall", "cb_deposits_fittings", "pavement"],
    }
    
    # Initialize result structure
    result = {}
    
    # Process each field in flat data
    for field_id, value in flat_data.items():
        location = FIELD_MAPPING.get(field_id)
        if not location:
            # Handle unmapped fields
            if '_unmapped_' not in result:
                result['_unmapped_'] = {}
            result['_unmapped_'][field_id] = value
            continue
            
        tab = location['tab']
        section_name = location['section_name']
        parent_group = location.get('parent_group')
        
        # Initialize tab if not exists
        if tab not in result:
            result[tab] = {}
            
        # Handle section (use actual section name or direct for common fields)
        if section_name:
            # Initialize section if not exists
            if section_name not in result[tab]:
                result[tab][section_name] = {}
            target_section = result[tab][section_name]
        else:
            # Direct tab field (like common fields)
            target_section = result[tab]
        
        # Handle group fields
        if parent_group:
            # This is a subfield of a group
            if parent_group not in target_section:
                target_section[parent_group] = {}
            target_section[parent_group][field_id] = value
        else:
            # Regular field
            target_section[field_id] = value
    
    return result

def flatten_template_structure_corrected(hierarchical_data):
    """
    Reverse transformation: Convert hierarchical structure back to flat
    Properly handles group fields and actual section names
    """
    flat_data = {}
    
    for tab_name, tab_data in hierarchical_data.items():
        if tab_name == '_unmapped_':
            # Add unmapped fields directly
            flat_data.update(tab_data)
            continue
            
        for section_or_field, section_data in tab_data.items():
            if isinstance(section_data, dict):
                # This could be a section or a direct field that's a dict
                for field_id, field_value in section_data.items():
                    if isinstance(field_value, dict) and field_id in GROUP_FIELDS:
                        # This is a group field, flatten its subfields
                        for sub_field_id, sub_field_value in field_value.items():
                            flat_data[sub_field_id] = sub_field_value
                    else:
                        # Regular field
                        flat_data[field_id] = field_value
            else:
                # Direct field in tab
                flat_data[section_or_field] = section_data
    
    return flat_data

def get_corrected_template_info():
    """Get information about the corrected template structure"""
    tabs = list(set(loc["tab"] for loc in FIELD_MAPPING.values()))
    sections_per_tab = {}
    
    for tab in tabs:
        sections = set()
        for loc in FIELD_MAPPING.values():
            if loc["tab"] == tab and loc["section_name"]:
                sections.add(loc["section_name"])
        sections_per_tab[tab] = list(sections)
    
    return {
        "tabs": tabs,
        "sections_per_tab": sections_per_tab,
        "group_fields": list(GROUP_FIELDS.keys()),
        "total_fields": len(FIELD_MAPPING)
    }

# Example usage
if __name__ == "__main__":
    import json
    
    # Sample data with group subfields
    sample_data = {
        "agreement_to_sell": "Available",
        "owner_details": "John Doe",
        "plot_survey_no": "Survey 123",      # subfield of property_location group
        "door_no": "45A",                   # subfield of property_location group  
        "socio_economic_class": "high",     # subfield of area_classification group
        "urban_rural": "urban",             # subfield of area_classification group
        "longitude": "77.1234",             # subfield of coordinates group
        "latitude": "28.5678"               # subfield of coordinates group
    }
    
    print("🧪 Testing corrected transformation...")
    hierarchical = transform_flat_to_template_structure_corrected(sample_data)
    print("\nHierarchical result:")
    print(json.dumps(hierarchical, indent=2))
    
    print("\nFlattening back...")
    flat_again = flatten_template_structure_corrected(hierarchical)
    print("Flat result:", flat_again)
    
    print("\nTemplate info:")
    info = get_corrected_template_info()
    print(json.dumps(info, indent=2))
