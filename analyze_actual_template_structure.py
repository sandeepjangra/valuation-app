#!/usr/bin/env python3
"""
Analyze the actual SBI template structure from MongoDB to get real section names and group fields
"""

import asyncio
import json
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def analyze_sbi_template_from_db():
    """Analyze SBI template structure directly from MongoDB"""
    
    print("🔍 ANALYZING ACTUAL SBI TEMPLATE FROM MONGODB")
    print("=" * 80)
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient("mongodb://localhost:27017/")
        admin_db = client["admin"]
        
        # Get SBI template collection
        sbi_collection = admin_db["sbi_land_property_comprehensive_v3"]
        
        # Find all template documents
        template_docs = await sbi_collection.find({}).to_list(length=None)
        
        print(f"📋 Found {len(template_docs)} template documents")
        
        # Analyze each document for structure
        field_mapping = {}
        tab_structure = {}
        group_fields = {}
        
        for doc in template_docs:
            template_name = doc.get("templateName", "Unknown")
            ui_name = doc.get("uiName", template_name)
            sections = doc.get("sections", [])
            
            print(f"\n📂 TAB: '{ui_name}' ({template_name})")
            print(f"   📊 Sections: {len(sections)}")
            
            tab_structure[ui_name] = {
                'sections': [],
                'total_fields': 0
            }
            
            for section in sections:
                section_id = section.get("sectionId", "unknown_section")
                section_name = section.get("sectionName", "Unknown Section")
                fields = section.get("fields", [])
                original_fields = section.get("originalFields", [])
                
                print(f"   📁 SECTION: '{section_id}' - {section_name}")
                print(f"      📄 Fields: {len(fields)} + Original: {len(original_fields)}")
                
                section_info = {
                    'section_id': section_id,
                    'section_name': section_name,
                    'field_count': len(fields) + len(original_fields),
                    'fields': []
                }
                
                # Process regular fields
                for field in fields:
                    field_id = field.get("fieldId")
                    field_type = field.get("fieldType")
                    ui_display_name = field.get("uiDisplayName", "")
                    
                    if field_id:
                        field_mapping[field_id] = {
                            'tab': ui_name,
                            'section_id': section_id,
                            'section_name': section_name,
                            'type': field_type,
                            'ui_name': ui_display_name
                        }
                        
                        section_info['fields'].append(field_id)
                        
                        print(f"         📄 {field_id} ({field_type}): {ui_display_name}")
                        
                        # Handle group fields specially
                        if field_type == "group":
                            sub_fields = field.get("subFields", [])
                            if sub_fields:
                                print(f"            🔗 GROUP with {len(sub_fields)} subFields:")
                                group_fields[field_id] = {
                                    'tab': ui_name,
                                    'section_id': section_id,
                                    'section_name': section_name,
                                    'subFields': []
                                }
                                
                                for sub_field in sub_fields:
                                    sub_field_id = sub_field.get("fieldId")
                                    sub_field_type = sub_field.get("fieldType")
                                    sub_ui_name = sub_field.get("uiDisplayName", "")
                                    
                                    if sub_field_id:
                                        print(f"               📄 {sub_field_id} ({sub_field_type}): {sub_ui_name}")
                                        group_fields[field_id]['subFields'].append({
                                            'fieldId': sub_field_id,
                                            'fieldType': sub_field_type,
                                            'uiDisplayName': sub_ui_name
                                        })
                                        
                                        # Map subfield to parent group
                                        field_mapping[sub_field_id] = {
                                            'tab': ui_name,
                                            'section_id': section_id,
                                            'section_name': section_name,
                                            'type': sub_field_type,
                                            'ui_name': sub_ui_name,
                                            'parent_group': field_id
                                        }
                
                # Process original fields (document-based fields)
                for field_id in original_fields:
                    field_mapping[field_id] = {
                        'tab': ui_name,
                        'section_id': section_id,
                        'section_name': section_name,
                        'type': 'document',
                        'ui_name': field_id.replace('_', ' ').title()
                    }
                    section_info['fields'].append(field_id)
                    print(f"         📄 {field_id} (document): {field_id.replace('_', ' ').title()}")
                
                tab_structure[ui_name]['sections'].append(section_info)
                tab_structure[ui_name]['total_fields'] += section_info['field_count']
        
        # Save the complete analysis
        analysis_data = {
            'field_mapping': field_mapping,
            'tab_structure': tab_structure,
            'group_fields': group_fields
        }
        
        with open('sbi_template_complete_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2)
        
        print(f"\n📊 ANALYSIS SUMMARY:")
        print(f"   📂 Total tabs: {len(tab_structure)}")
        print(f"   📄 Total fields: {len(field_mapping)}")
        print(f"   🔗 Group fields: {len(group_fields)}")
        
        for tab_name, tab_info in tab_structure.items():
            print(f"   📂 {tab_name}: {len(tab_info['sections'])} sections, {tab_info['total_fields']} total fields")
        
        print(f"\n💾 Complete analysis saved to: sbi_template_complete_analysis.json")
        
        # Generate new transformation code
        generate_correct_transformation_code(field_mapping, tab_structure, group_fields)
        
        await client.close()
        
    except Exception as e:
        print(f"❌ Error analyzing template: {e}")
        import traceback
        print(f"Full error: {traceback.format_exc()}")

def generate_correct_transformation_code(field_mapping, tab_structure, group_fields):
    """Generate transformation code with correct section names and group handling"""
    
    print(f"\n🔧 GENERATING CORRECTED TRANSFORMATION CODE")
    print("=" * 80)
    
    transformation_code = f'''#!/usr/bin/env python3
"""
Corrected transformation functions with actual section names and group field handling
Generated from actual MongoDB template structure
"""

def transform_flat_to_template_structure_correct(flat_data):
    """
    Transform flat data to hierarchical structure using ACTUAL section names and group handling
    """
    
    # Complete field mapping from actual SBI template in MongoDB
    FIELD_MAPPING = {{
'''
    
    # Add all field mappings with actual data
    for field_id, location in field_mapping.items():
        tab = location['tab']
        section_id = location['section_id']
        section_name = location['section_name']
        field_type = location['type']
        parent_group = location.get('parent_group')
        
        transformation_code += f'        "{field_id}": {{\n'
        transformation_code += f'            "tab": "{tab}",\n'
        transformation_code += f'            "section_id": "{section_id}",\n'
        transformation_code += f'            "section_name": "{section_name}",\n'
        transformation_code += f'            "type": "{field_type}"'
        
        if parent_group:
            transformation_code += f',\n            "parent_group": "{parent_group}"'
        
        transformation_code += '\n        },\n'
    
    transformation_code += '''    }
    
    # Group field definitions
    GROUP_FIELDS = {'''
    
    # Add group field definitions
    for group_id, group_info in group_fields.items():
        transformation_code += f'\n        "{group_id}": {{\n'
        transformation_code += f'            "tab": "{group_info["tab"]}",\n'
        transformation_code += f'            "section_id": "{group_info["section_id"]}",\n'
        transformation_code += f'            "section_name": "{group_info["section_name"]}",\n'
        transformation_code += f'            "subFields": {json.dumps([sf["fieldId"] for sf in group_info["subFields"]])}\n'
        transformation_code += f'        }},'
    
    transformation_code += '''
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
        section_id = location['section_id']
        parent_group = location.get('parent_group')
        
        # Initialize tab if not exists
        if tab not in result:
            result[tab] = {}
            
        # Initialize section if not exists
        if section_id not in result[tab]:
            result[tab][section_id] = {}
        
        # Handle group fields
        if parent_group:
            # This is a subfield of a group
            if parent_group not in result[tab][section_id]:
                result[tab][section_id][parent_group] = {}
            result[tab][section_id][parent_group][field_id] = value
        else:
            # Regular field or group field itself
            result[tab][section_id][field_id] = value
    
    return result

def flatten_template_structure_correct(hierarchical_data):
    """
    Reverse transformation: Convert hierarchical structure back to flat
    Handles group fields properly
    """
    flat_data = {}
    
    for tab_name, tab_data in hierarchical_data.items():
        if tab_name == '_unmapped_':
            # Add unmapped fields directly
            flat_data.update(tab_data)
            continue
            
        for section_id, section_data in tab_data.items():
            for field_id, field_value in section_data.items():
                if isinstance(field_value, dict):
                    # This might be a group field with subfields
                    group_info = GROUP_FIELDS.get(field_id)
                    if group_info:
                        # This is a group field, flatten its subfields
                        for sub_field_id, sub_field_value in field_value.items():
                            flat_data[sub_field_id] = sub_field_value
                    else:
                        # Unknown nested structure, flatten all
                        for sub_key, sub_value in field_value.items():
                            flat_data[sub_key] = sub_value
                else:
                    # Regular field
                    flat_data[field_id] = field_value
    
    return flat_data

def get_template_structure_info():
    """
    Get information about the template structure
    """
    return {
        "tabs": list({loc["tab"] for loc in FIELD_MAPPING.values()}),
        "sections_per_tab": {tab: list(set(loc["section_id"] for loc in FIELD_MAPPING.values() if loc["tab"] == tab)) 
                            for tab in set(loc["tab"] for loc in FIELD_MAPPING.values())},
        "group_fields": list(GROUP_FIELDS.keys()),
        "total_fields": len(FIELD_MAPPING)
    }

# Example usage and testing
if __name__ == "__main__":
    # Sample data with group subfields
    sample_data = {
        "agreement_to_sell": "Available",
        "owner_details": "John Doe",
        "plot_survey_no": "Survey 123",  # subfield of property_location group
        "door_no": "45A",               # subfield of property_location group
        "socio_economic_class": "high", # subfield of area_classification group
        "urban_rural": "urban",         # subfield of area_classification group
        "longitude": "77.1234",         # subfield of coordinates group
        "latitude": "28.5678"           # subfield of coordinates group
    }
    
    print("🧪 Testing corrected transformation...")
    hierarchical = transform_flat_to_template_structure_correct(sample_data)
    print("Hierarchical result:")
    print(json.dumps(hierarchical, indent=2))
    
    print("\\nFlattening back...")
    flat_again = flatten_template_structure_correct(hierarchical)
    print("Flat result:", flat_again)
    
    print("\\nTemplate structure info:")
    info = get_template_structure_info()
    print(json.dumps(info, indent=2))
'''
    
    # Save the corrected transformation code
    with open('sbi_transformation_correct.py', 'w', encoding='utf-8') as f:
        f.write(transformation_code)
    
    print(f"✅ Corrected transformation functions saved to: sbi_transformation_correct.py")
    
    print(f"""
🎯 KEY IMPROVEMENTS:

1. ✅ ACTUAL SECTION NAMES: Uses real section IDs like 'property_part_a', 'property_part_b'
2. ✅ GROUP FIELD HANDLING: Properly handles group fields with subFields
3. ✅ MONGODB STRUCTURE: Based on actual template structure from database
4. ✅ DYNAMIC MAPPING: Will change automatically if template changes

STRUCTURE PREVIEW:
{{
  "Property Details": {{
    "property_part_a": {{ "agreement_to_sell": "..." }},
    "property_part_b": {{ 
      "owner_details": "...",
      "property_location": {{
        "plot_survey_no": "...",
        "door_no": "..."
      }}
    }},
    "property_part_c": {{
      "area_classification": {{
        "socio_economic_class": "high",
        "urban_rural": "urban"
      }}
    }}
  }}
}}

Next: Update backend transformation function and test!
""")

if __name__ == "__main__":
    asyncio.run(analyze_sbi_template_from_db())