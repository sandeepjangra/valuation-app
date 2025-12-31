
def transform_flat_to_template_structure(flat_data):
    """
    Transform flat data structure to hierarchical template structure
    Matches SBI land property template with tabs and sections
    """
    
    # Complete field mapping for SBI Land Property template
    FIELD_TO_LOCATION = {
        "agreement_to_sell": {"tab": "Property Details", "section": "Section 1", "type": "textarea"},
        "list_of_documents_produced": {"tab": "Property Details", "section": "Section 1", "type": "textarea"},
        "allotment_letter": {"tab": "Property Details", "section": "Section 1", "type": "textarea"},
        "layout_plan": {"tab": "Property Details", "section": "Section 1", "type": "textarea"},
        "sales_deed": {"tab": "Property Details", "section": "Section 1", "type": "textarea"},
        "ats": {"tab": "Property Details", "section": "Section 1", "type": "textarea"},
        "sanctioned_building_plan": {"tab": "Property Details", "section": "Section 1", "type": "textarea"},
        "owner_details": {"tab": "Property Details", "section": "Section 2", "type": "textarea"},
        "borrower_name": {"tab": "Property Details", "section": "Section 2", "type": "textarea"},
        "postal_address": {"tab": "Property Details", "section": "Section 2", "type": "textarea"},
        "property_description": {"tab": "Property Details", "section": "Section 2", "type": "textarea"},
        "property_location": {"tab": "Property Details", "section": "Section 2", "type": "group"},
        "city_town_village": {"tab": "Property Details", "section": "Section 2", "type": "select"},
        "area_classification": {"tab": "Property Details", "section": "Section 3", "type": "group"},
        "government_regulation": {"tab": "Property Details", "section": "Section 3", "type": "group"},
        "boundaries_dimensions_table": {"tab": "Property Details", "section": "Section 4", "type": "table"},
        "coordinates": {"tab": "Property Details", "section": "Section 4", "type": "group"},
        "land_area_and_occupancy": {"tab": "Property Details", "section": "Section 4", "type": "group"},
        "locality_surroundings": {"tab": "Site Characteristics", "section": "Section 1", "type": "group"},
        "physical_characteristics": {"tab": "Site Characteristics", "section": "Section 1", "type": "group"},
        "land_usage": {"tab": "Site Characteristics", "section": "Section 1", "type": "group"},
        "planning_approvals": {"tab": "Site Characteristics", "section": "Section 1", "type": "group"},
        "road_access": {"tab": "Site Characteristics", "section": "Section 2", "type": "group"},
        "utility_services_group": {"tab": "Site Characteristics", "section": "Section 2", "type": "group"},
        "additional_information": {"tab": "Site Characteristics", "section": "Section 2", "type": "group"},
        "plot_size": {"tab": "Valuation", "section": "Section 1", "type": "group"},
        "market_rate": {"tab": "Valuation", "section": "Section 1", "type": "group"},
        "estimated_valuation": {"tab": "Valuation", "section": "Section 1", "type": "group"},
        "building_constructed": {"tab": "Valuation", "section": "Section 2", "type": "select"},
        "building_basic_info": {"tab": "Valuation", "section": "Section 2", "type": "group"},
        "building_dimensions": {"tab": "Valuation", "section": "Section 2", "type": "group"},
        "building_condition": {"tab": "Valuation", "section": "Section 2", "type": "group"},
        "approval_documents": {"tab": "Valuation", "section": "Section 2", "type": "group"},
        "no_building_remarks": {"tab": "Valuation", "section": "Section 2", "type": "group"},
        "building_specifications_table": {"tab": "Construction Specifications", "section": "Section 1", "type": "dynamic_table"},
        "floor_wise_valuation_table": {"tab": "Construction Specifications", "section": "Section 1", "type": "dynamic_table"},
        "extra_items": {"tab": "Construction Specifications", "section": "Section 2", "type": "group"},
        "amenities": {"tab": "Construction Specifications", "section": "Section 2", "type": "group"},
        "miscellaneous": {"tab": "Construction Specifications", "section": "Section 2", "type": "group"},
        "services": {"tab": "Construction Specifications", "section": "Section 2", "type": "group"},
        "land_total": {"tab": "Detailed Valuation", "section": "None", "type": "currency"},
        "building_total": {"tab": "Detailed Valuation", "section": "None", "type": "currency"},
        "extra_items_total": {"tab": "Detailed Valuation", "section": "None", "type": "currency"},
        "amenities_total": {"tab": "Detailed Valuation", "section": "None", "type": "currency"},
        "miscellaneous_total": {"tab": "Detailed Valuation", "section": "None", "type": "currency"},
        "services_total": {"tab": "Detailed Valuation", "section": "None", "type": "currency"},
        "grand_total": {"tab": "Detailed Valuation", "section": "None", "type": "currency"},
        "report_reference_number": {"tab": "_common_fields_", "section": "None", "type": "text"},
        "valuation_date": {"tab": "_common_fields_", "section": "None", "type": "date"},
        "inspection_date": {"tab": "_common_fields_", "section": "None", "type": "date"},
        "applicant_name": {"tab": "_common_fields_", "section": "None", "type": "text"},
        "valuation_purpose": {"tab": "_common_fields_", "section": "None", "type": "select"},
        "bank_branch": {"tab": "_common_fields_", "section": "None", "type": "select_dynamic"},
    }
    
    # Initialize result structure
    result = {}
    
    # Process each field in flat data
    for field_id, value in flat_data.items():
        location = FIELD_TO_LOCATION.get(field_id)
        if not location:
            # Handle unmapped fields - add to _unmapped_ section
            if '_unmapped_' not in result:
                result['_unmapped_'] = {}
            result['_unmapped_'][field_id] = value
            continue
            
        tab = location['tab']
        section = location['section']
        
        # Initialize tab if not exists
        if tab not in result:
            result[tab] = {}
            
        # Place field in appropriate location
        if section and section != 'null' and section != 'None':
            # Section-based field
            if section not in result[tab]:
                result[tab][section] = {}
            result[tab][section][field_id] = value
        else:
            # Direct tab field
            result[tab][field_id] = value
    
    return result

def flatten_template_structure(hierarchical_data):
    """
    Reverse transformation: Convert hierarchical structure back to flat
    """
    flat_data = {}
    
    for tab_name, tab_data in hierarchical_data.items():
        if tab_name == '_unmapped_':
            # Add unmapped fields directly
            flat_data.update(tab_data)
            continue
            
        for key, value in tab_data.items():
            if isinstance(value, dict):
                # This is a section - flatten its contents
                for field_id, field_value in value.items():
                    flat_data[field_id] = field_value
            else:
                # This is a direct field
                flat_data[key] = value
    
    return flat_data

def validate_template_structure(data, expected_tabs=None):
    """
    Validate that the data matches expected template structure
    """
    if expected_tabs is None:
        expected_tabs = ['Property Details', 'Site Characteristics', 'Valuation', 
                        'Construction Specifications', 'Detailed Valuation', '_common_fields_']
    
    validation_results = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'tabs_found': list(data.keys()),
        'missing_tabs': []
    }
    
    # Check for expected tabs
    for tab in expected_tabs:
        if tab not in data:
            validation_results['missing_tabs'].append(tab)
            validation_results['warnings'].append(f"Missing expected tab: {tab}")
    
    # Check for unexpected tabs
    for tab in data.keys():
        if tab not in expected_tabs and tab != '_unmapped_':
            validation_results['warnings'].append(f"Unexpected tab found: {tab}")
    
    return validation_results

# Example usage:
if __name__ == "__main__":
    # Example flat data
    sample_flat_data = {
        "agreement_to_sell": "Available",
        "list_of_documents_produced": "Sale deed, Survey settlement",
        "owner_details": "John Doe, S/o Richard Doe",
        "borrower_name": "MS SSK Developers",
        "plot_size": "1000",
        "market_rate": "5000",
        "land_total": 5000000,
        "report_reference_number": "CEV/RVO/299/0029/26122025"
    }
    
    # Transform to hierarchical
    hierarchical = transform_flat_to_template_structure(sample_flat_data)
    print("Hierarchical structure:")
    import json
    print(json.dumps(hierarchical, indent=2))
    
    # Validate
    validation = validate_template_structure(hierarchical)
    print(f"\nValidation: {validation}")
    
    # Transform back to flat
    flat_again = flatten_template_structure(hierarchical)
    print(f"\nFlattened back: {flat_again}")
