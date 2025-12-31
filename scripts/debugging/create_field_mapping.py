#!/usr/bin/env python3
"""
Create complete field mapping for proper transformation
"""

import json

def create_complete_field_mapping():
    """Create complete field mapping from SBI template structure"""
    
    print("🗺️ CREATING COMPLETE FIELD MAPPING")
    print("=" * 80)
    
    # Load the template data
    with open('sbi_template_debug.json', 'r', encoding='utf-8') as f:
        template_data = json.load(f)
    
    field_mapping = {}
    bank_specific_tabs = template_data.get('bankSpecificTabs', [])
    common_fields = template_data.get('commonFields', [])
    
    # Process bank-specific tabs
    for tab in bank_specific_tabs:
        tab_name = tab.get('tabName', 'Unknown Tab')
        sections = tab.get('sections', [])
        
        print(f"\n📂 Processing Tab: '{tab_name}'")
        
        # Process sections first (these have priority over direct tab fields)
        if sections:
            for i, section in enumerate(sections):
                section_name = section.get('name') or f"Section {i+1}"
                section_fields = section.get('fields', [])
                
                print(f"   📁 Processing Section: '{section_name}' ({len(section_fields)} fields)")
                
                for field in section_fields:
                    field_id = field.get('fieldId')
                    if field_id:
                        field_mapping[field_id] = {
                            'tab': tab_name,
                            'section': section_name,
                            'section_index': i + 1,
                            'type': field.get('fieldType', 'unknown'),
                            'label': field.get('uiDisplayName', '')
                        }
                        print(f"      ✅ {field_id} → {tab_name} / {section_name}")
        
        # For tabs without sections or fields not in sections, store as direct tab fields
        tab_fields = tab.get('fields', [])
        if tab_fields:
            # Check if this field is already mapped from sections
            unmapped_fields = [f for f in tab_fields if f.get('fieldId') not in field_mapping]
            
            if unmapped_fields:
                print(f"   📄 Processing Direct Tab Fields: ({len(unmapped_fields)} unmapped fields)")
                for field in unmapped_fields:
                    field_id = field.get('fieldId')
                    if field_id:
                        field_mapping[field_id] = {
                            'tab': tab_name,
                            'section': None,  # Direct tab field
                            'section_index': None,
                            'type': field.get('fieldType', 'unknown'),
                            'label': field.get('uiDisplayName', '')
                        }
                        print(f"      ✅ {field_id} → {tab_name} (direct)")
    
    # Process common fields
    print(f"\n📄 Processing Common Fields ({len(common_fields)} fields)")
    for field in common_fields:
        field_id = field.get('fieldId')
        if field_id:
            field_mapping[field_id] = {
                'tab': '_common_fields_',
                'section': None,
                'section_index': None,
                'type': field.get('fieldType', 'unknown'),
                'label': field.get('uiDisplayName', '')
            }
            print(f"   ✅ {field_id} → _common_fields_")
    
    print(f"\n📊 FIELD MAPPING SUMMARY:")
    print(f"   Total fields mapped: {len(field_mapping)}")
    
    # Count by tab
    tab_counts = {}
    section_counts = {}
    
    for field_id, location in field_mapping.items():
        tab = location['tab']
        section = location['section']
        
        tab_counts[tab] = tab_counts.get(tab, 0) + 1
        
        if section:
            section_key = f"{tab} / {section}"
            section_counts[section_key] = section_counts.get(section_key, 0) + 1
    
    for tab, count in tab_counts.items():
        print(f"   📂 {tab}: {count} fields")
    
    print(f"\n📁 SECTION BREAKDOWN:")
    for section_key, count in section_counts.items():
        print(f"   📁 {section_key}: {count} fields")
    
    # Save the complete mapping
    with open('complete_field_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(field_mapping, f, indent=2)
    
    print(f"\n💾 Complete field mapping saved to: complete_field_mapping.json")
    
    # Generate Python code for the transformation function
    generate_transformation_code(field_mapping)

def generate_transformation_code(field_mapping):
    """Generate the complete transformation code"""
    
    print(f"\n🔧 TRANSFORMATION CODE GENERATION")
    print("=" * 80)
    
    # Create the code file
    transformation_code = f'''
def transform_flat_to_template_structure(flat_data):
    """
    Transform flat data structure to hierarchical template structure
    Matches SBI land property template with tabs and sections
    """
    
    # Complete field mapping for SBI Land Property template
    FIELD_TO_LOCATION = {{
'''
    
    # Add all field mappings
    for field_id, location in field_mapping.items():
        tab = location['tab']
        section = location['section']
        field_type = location['type']
        
        transformation_code += f'        "{field_id}": {{"tab": "{tab}", "section": "{section}", "type": "{field_type}"}},\n'
    
    transformation_code += '''    }
    
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
        if section and section != 'null':
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
    print(f"\\nValidation: {validation}")
    
    # Transform back to flat
    flat_again = flatten_template_structure(hierarchical)
    print(f"\\nFlattened back: {flat_again}")
'''
    
    # Save the transformation code
    with open('sbi_transformation_functions.py', 'w', encoding='utf-8') as f:
        f.write(transformation_code)
    
    print(f"✅ Transformation functions saved to: sbi_transformation_functions.py")
    
    print(f"""
🚀 IMPLEMENTATION READY!

FILES CREATED:
1. complete_field_mapping.json - Complete field location mapping ({len(field_mapping)} fields)
2. sbi_transformation_functions.py - Ready-to-use transformation functions

NEXT STEPS:
1. Update backend/main.py with new transform_flat_to_template_structure()
2. Test with sample data
3. Update save/load functions to use hierarchical structure
4. Frontend integration for grouped data handling

The new structure will store reports like:
{{
  "Property Details": {{
    "Section 1": {{ "agreement_to_sell": "Available", ... }},
    "Section 2": {{ "owner_details": "John Doe", ... }}
  }},
  "Site Characteristics": {{ ... }},
  "_common_fields_": {{ "report_reference_number": "...", ... }}
}}

This perfectly matches your SBI template design! 🎯
""")

if __name__ == "__main__":
    create_complete_field_mapping()