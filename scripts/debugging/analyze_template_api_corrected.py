#!/usr/bin/env python3
"""
Get actual SBI template structure via API to extract section names and group fields
"""

import requests
import json

def analyze_sbi_template_via_api():
    """Analyze SBI template structure via API"""
    
    print("🔍 ANALYZING SBI TEMPLATE VIA API")
    print("=" * 80)
    
    try:
        # Get template from API
        url = "http://localhost:8000/api/templates/SBI/land-property/aggregated-fields"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        template_data = response.json()
        
        # Save raw template data
        with open('sbi_template_raw_api.json', 'w', encoding='utf-8') as f:
            json.dump(template_data, f, indent=2)
        
        print(f"✅ Template data retrieved from API")
        
        # Analyze bank specific tabs
        bank_tabs = template_data.get('bankSpecificTabs', [])
        common_fields = template_data.get('commonFields', [])
        
        print(f"📊 Found {len(bank_tabs)} bank-specific tabs")
        print(f"📄 Found {len(common_fields)} common fields")
        
        field_mapping = {}
        group_fields = {}
        tab_structure = {}
        
        # Process each tab
        for tab in bank_tabs:
            tab_name = tab.get('tabName', 'Unknown')
            sections = tab.get('sections', [])
            
            print(f"\n📂 TAB: '{tab_name}'")
            print(f"   📊 Sections: {len(sections)}")
            
            tab_structure[tab_name] = {
                'sections': [],
                'total_fields': 0
            }
            
            # Process sections
            for section in sections:
                section_name = section.get('name', 'Unknown Section')
                fields = section.get('fields', [])
                
                print(f"   📁 SECTION: '{section_name}' ({len(fields)} fields)")
                
                section_info = {
                    'section_name': section_name,
                    'field_count': len(fields),
                    'fields': []
                }
                
                # Process fields in section
                for field in fields:
                    field_id = field.get('fieldId')
                    field_type = field.get('fieldType')
                    ui_name = field.get('uiDisplayName', '')
                    
                    if field_id:
                        field_mapping[field_id] = {
                            'tab': tab_name,
                            'section_name': section_name,
                            'type': field_type,
                            'ui_name': ui_name
                        }
                        
                        section_info['fields'].append(field_id)
                        print(f"      📄 {field_id} ({field_type}): {ui_name}")
                        
                        # Handle group fields
                        if field_type == "group":
                            sub_fields = field.get("subFields", [])
                            if sub_fields:
                                print(f"         🔗 GROUP with {len(sub_fields)} subFields:")
                                group_fields[field_id] = {
                                    'tab': tab_name,
                                    'section_name': section_name,
                                    'subFields': []
                                }
                                
                                for sub_field in sub_fields:
                                    sub_field_id = sub_field.get("fieldId")
                                    sub_field_type = sub_field.get("fieldType")
                                    sub_ui_name = sub_field.get("uiDisplayName", "")
                                    
                                    if sub_field_id:
                                        print(f"            📄 {sub_field_id} ({sub_field_type}): {sub_ui_name}")
                                        group_fields[field_id]['subFields'].append({
                                            'fieldId': sub_field_id,
                                            'fieldType': sub_field_type,
                                            'uiDisplayName': sub_ui_name
                                        })
                                        
                                        # Map subfield to parent group
                                        field_mapping[sub_field_id] = {
                                            'tab': tab_name,
                                            'section_name': section_name,
                                            'type': sub_field_type,
                                            'ui_name': sub_ui_name,
                                            'parent_group': field_id
                                        }
                
                tab_structure[tab_name]['sections'].append(section_info)
                tab_structure[tab_name]['total_fields'] += section_info['field_count']
        
        # Process common fields
        print(f"\n📄 COMMON FIELDS ({len(common_fields)} fields):")
        for field in common_fields:
            field_id = field.get('fieldId')
            field_type = field.get('fieldType')
            ui_name = field.get('uiDisplayName', '')
            
            if field_id:
                field_mapping[field_id] = {
                    'tab': '_common_fields_',
                    'section_name': None,
                    'type': field_type,
                    'ui_name': ui_name
                }
                print(f"   📄 {field_id} ({field_type}): {ui_name}")
        
        # Save complete analysis
        analysis_data = {
            'field_mapping': field_mapping,
            'tab_structure': tab_structure,
            'group_fields': group_fields,
            'common_fields_count': len(common_fields)
        }
        
        with open('sbi_template_analysis_corrected.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2)
        
        print(f"\n📊 CORRECTED ANALYSIS SUMMARY:")
        print(f"   📂 Total tabs: {len(tab_structure)}")
        print(f"   📄 Total fields: {len(field_mapping)}")
        print(f"   🔗 Group fields: {len(group_fields)}")
        print(f"   📄 Common fields: {len(common_fields)}")
        
        for tab_name, tab_info in tab_structure.items():
            print(f"   📂 {tab_name}: {len(tab_info['sections'])} sections, {tab_info['total_fields']} total fields")
        
        print(f"\n💾 Corrected analysis saved to: sbi_template_analysis_corrected.json")
        
        # Generate corrected transformation functions
        generate_corrected_transformation(field_mapping, tab_structure, group_fields)
        
        return analysis_data
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Full error: {traceback.format_exc()}")
        return None

def generate_corrected_transformation(field_mapping, tab_structure, group_fields):
    """Generate transformation functions with correct section names and group handling"""
    
    print(f"\n🔧 GENERATING CORRECTED TRANSFORMATION FUNCTIONS")
    print("=" * 80)
    
    # Create the corrected transformation code
    transformation_code = '''#!/usr/bin/env python3
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
'''
    
    # Add all field mappings
    for field_id, location in field_mapping.items():
        tab = location['tab']
        section_name = location['section_name']
        field_type = location['type']
        parent_group = location.get('parent_group')
        
        transformation_code += f'        "{field_id}": {{\n'
        transformation_code += f'            "tab": "{tab}",\n'
        transformation_code += f'            "section_name": "{section_name}",\n'
        transformation_code += f'            "type": "{field_type}"'
        
        if parent_group:
            transformation_code += f',\n            "parent_group": "{parent_group}"'
        
        transformation_code += '\n        },\n'
    
    transformation_code += '''    }
    
    # Group field definitions with subfields
    GROUP_FIELDS = {
'''
    
    # Add group field definitions
    for group_id, group_info in group_fields.items():
        subfield_ids = [sf['fieldId'] for sf in group_info['subFields']]
        transformation_code += f'        "{group_id}": {json.dumps(subfield_ids)},\n'
    
    transformation_code += '''    }
    
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
    print("\\nHierarchical result:")
    print(json.dumps(hierarchical, indent=2))
    
    print("\\nFlattening back...")
    flat_again = flatten_template_structure_corrected(hierarchical)
    print("Flat result:", flat_again)
    
    print("\\nTemplate info:")
    info = get_corrected_template_info()
    print(json.dumps(info, indent=2))
'''
    
    # Save the corrected transformation code
    with open('sbi_transformation_corrected.py', 'w', encoding='utf-8') as f:
        f.write(transformation_code)
    
    print(f"✅ Corrected transformation functions saved to: sbi_transformation_corrected.py")
    
    print(f"""
🎯 KEY CORRECTIONS IMPLEMENTED:

1. ✅ ACTUAL SECTION NAMES: Uses real section names from template API
2. ✅ GROUP FIELD HANDLING: Properly nests subfields within group fields  
3. ✅ API-BASED STRUCTURE: Based on actual template from running backend
4. ✅ DYNAMIC UPDATES: Will reflect template changes automatically

CORRECTED STRUCTURE EXAMPLE:
{{
  "Property Details": {{
    "Part A - Documents": {{ 
      "agreement_to_sell": "Available" 
    }},
    "Part B - Address Details": {{
      "owner_details": "John Doe",
      "property_location": {{
        "plot_survey_no": "Survey 123",
        "door_no": "45A"
      }}
    }},
    "Part C - Property Information": {{
      "area_classification": {{
        "socio_economic_class": "high",
        "urban_rural": "urban"
      }}
    }}
  }}
}}

Next Step: Update backend main.py with corrected transformation!
""")

if __name__ == "__main__":
    analyze_sbi_template_via_api()