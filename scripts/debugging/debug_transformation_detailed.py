#!/usr/bin/env python3
"""
Direct transformation test to debug the issue step by step
"""

import asyncio
import httpx
import json

async def test_transformation():
    """Test the transformation logic directly"""
    
    # Simulate the problematic input data
    input_data = {
        "property_details": {
            "property_part_a": {
                "sales_deed": "NA",
                "ats": "NA", 
                "sanctioned_building_plan": "NA"
            },
            "property_part_b": {
                "city_town_village": "town"
            },
            "property_part_c": {},
            "property_part_d": {
                "coordinates": "NA"
            }
        },
        "valuation": {
            "valuation_part_b": {
                "building_constructed": "no"
            }
        },
        "inspection_date": "2025-12-04",
        "valuation_purpose": "bank_purpose",
        "plot_survey_no": "-",
        "door_no": "-",
        "socio_economic_class": "middle",
        "urban_rural": "rural",
        "area_type": "residential",
        "municipal_corporation": "panchkula",
        "estimated_land_value": "₹0.00",
        "land_only_confirmation": "confirmed",
        "land_valuation_basis": "Valuation restricted to land only",
        "valuation_date": "2025-12-26",
        "applicant_name": "MS SSK Developers",
        # Metadata that should be filtered out
        "status": "draft",
        "bankName": "State Bank of India",
        "templateName": "SBI Land Property Valuation",
        "organizationId": "sk-tindwal",
        "customTemplateId": "69370dd798c7d79553ae4a66",
        "propertyType": "land",
        "reportType": "valuation_report"
    }
    
    print("🔍 DEBUGGING TRANSFORMATION STEP BY STEP")
    print("=" * 80)
    
    print(f"📋 Input data analysis:")
    for key, value in input_data.items():
        if isinstance(value, dict):
            print(f"   📁 {key}: dict with {len(value)} keys")
            if key == "property_details":
                print(f"      🔍 property_details contents:")
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, dict):
                        print(f"         📂 {sub_key}: {len(sub_value)} fields")
                        for field_id, field_val in sub_value.items():
                            print(f"            📄 {field_id}: {field_val}")
                    else:
                        print(f"         📄 {sub_key}: {sub_value}")
        else:
            print(f"   📄 {key}: {type(value).__name__} = {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}")
    
    # Fetch template structure
    print(f"\n🌐 Fetching template structure...")
    template_url = "http://localhost:8000/api/templates/SBI/land-property/aggregated-fields"
    
    try:
        async with httpx.AsyncClient() as client:
            template_response = await client.get(template_url, timeout=10.0)
            if template_response.status_code != 200:
                print(f"❌ Failed to fetch template: {template_response.status_code}")
                return
            
            template_data = template_response.json()
            print(f"✅ Template fetched successfully")
            
    except Exception as e:
        print(f"❌ Template fetch error: {e}")
        return
    
    # Build field mapping like the real transformation
    field_to_location = {}
    group_fields = {}
    
    bank_tabs = template_data.get('bankSpecificTabs', [])
    
    for tab in bank_tabs:
        tab_id = tab.get('tabId', 'unknown')
        tab_name = tab.get('tabName', 'Unknown Tab')
        
        sections = tab.get('sections', [])
        for section in sections:
            section_id = section.get('sectionId', 'unknown')
            
            fields = section.get('fields', [])
            for field in fields:
                field_id = field.get('fieldId')
                field_type = field.get('fieldType', 'text')
                
                if field_id:
                    field_to_location[field_id] = {
                        "tab": tab_name,
                        "section": section_id,
                        "type": field_type
                    }
                    
                    # Handle group fields
                    if field_type == 'group':
                        subfields = field.get('subFields', [])
                        group_fields[field_id] = [sf.get('fieldId') for sf in subfields if sf.get('fieldId')]
    
    print(f"📊 Template analysis:")
    print(f"   📋 Mapped {len(field_to_location)} fields")
    print(f"   🔗 Found {len(group_fields)} group fields")
    
    # Show some group fields for debugging
    print(f"\n🔗 Group fields found:")
    for group_id, subfields in list(group_fields.items())[:5]:  # Show first 5
        print(f"   📁 {group_id}: {subfields}")
    
    # Identify structured vs flat data like the real function
    structured_tabs = set()
    flat_fields = {}
    
    common_field_ids = set()
    for common_field in template_data.get('commonFields', []):
        field_id = common_field.get('fieldId')
        if field_id:
            common_field_ids.add(field_id)
    
    print(f"\n📋 Common fields: {common_field_ids}")
    
    # Separate structured tabs from individual fields
    expected_tabs = {tab.get('tabName') for tab in bank_tabs}
    expected_tabs.update(['property_details', 'site_characteristics', 'valuation', 'construction_specifications', 'detailed_valuation'])
    
    print(f"\n📂 Expected tabs: {expected_tabs}")
    
    for key, value in input_data.items():
        if isinstance(value, dict) and key not in common_field_ids:
            if key in expected_tabs or key.lower().replace(' ', '_') in {t.lower().replace(' ', '_') for t in expected_tabs}:
                structured_tabs.add(key)
                print(f"   ✅ {key} recognized as structured tab")
            else:
                flat_fields[key] = value
                print(f"   📄 {key} treated as flat field (dict)")
        else:
            flat_fields[key] = value
            if not (key in common_field_ids):
                print(f"   📄 {key} treated as flat field")
    
    print(f"\n📊 Classification result:")
    print(f"   📁 Structured tabs: {structured_tabs}")
    print(f"   📄 Flat fields: {len(flat_fields)} items")
    
    # Now simulate the structured data processing
    result = {}
    
    print(f"\n🔄 Processing structured tabs...")
    for tab_key in structured_tabs:
        tab_data = input_data[tab_key]
        print(f"\n   📁 Processing {tab_key}:")
        
        # Map tab name
        tab_mapping = {
            'property_details': 'Property Details',
            'site_characteristics': 'Site Characteristics', 
            'valuation': 'Valuation',
            'construction_specifications': 'Construction Specifications',
            'detailed_valuation': 'Detailed Valuation'
        }
        
        proper_tab_name = tab_mapping.get(tab_key, tab_key)
        print(f"      🏷️ Mapped to: {proper_tab_name}")
        
        # Check structure
        has_proper_sections = any(section_key.startswith(('property_part_', 'site_part_', 'valuation_part_', 'construction_part_')) for section_key in tab_data.keys())
        print(f"      🔍 Has proper sections: {has_proper_sections}")
        
        if has_proper_sections:
            if proper_tab_name not in result:
                result[proper_tab_name] = {}
            
            # Process each section
            for section_key, section_data in tab_data.items():
                print(f"         📂 Section {section_key}: {len(section_data) if isinstance(section_data, dict) else 'not dict'} items")
                
                if isinstance(section_data, dict) and section_data:  # Only process non-empty sections
                    if section_key not in result[proper_tab_name]:
                        result[proper_tab_name][section_key] = {}
                    
                    # Process fields in this section
                    for field_id, field_value in section_data.items():
                        if field_value is not None and field_value != "":
                            print(f"            📄 Field {field_id} = {field_value}")
                            
                            # Check if this field is a group field
                            if field_id in group_fields:
                                print(f"               🔗 {field_id} is a GROUP field")
                                if isinstance(field_value, dict):
                                    result[proper_tab_name][section_key][field_id] = field_value
                                else:
                                    result[proper_tab_name][section_key][field_id] = field_value
                            else:
                                # Check if this is a subfield that should be grouped
                                parent_group = None
                                for group_id, subfield_list in group_fields.items():
                                    if field_id in subfield_list:
                                        parent_group = group_id
                                        break
                                
                                if parent_group:
                                    print(f"               📁 {field_id} belongs to group {parent_group}")
                                    if parent_group not in result[proper_tab_name][section_key]:
                                        result[proper_tab_name][section_key][parent_group] = {}
                                    result[proper_tab_name][section_key][parent_group][field_id] = field_value
                                else:
                                    print(f"               📄 {field_id} is regular field")
                                    result[proper_tab_name][section_key][field_id] = field_value
        
        # Remove from flat_fields
        if tab_key in flat_fields:
            del flat_fields[tab_key]
            print(f"      ✅ Removed {tab_key} from flat_fields")
    
    print(f"\n📊 FINAL RESULT:")
    print(f"   📁 Result has {len(result)} tabs")
    for tab_name, tab_content in result.items():
        print(f"      📂 {tab_name}: {len(tab_content)} sections")
        for section_name, section_content in tab_content.items():
            print(f"         📄 {section_name}: {len(section_content)} fields")
    
    print(f"\n   📄 Remaining flat fields: {len(flat_fields)}")
    if flat_fields:
        print(f"      Some flat fields: {list(flat_fields.keys())[:10]}")
    
    return result

if __name__ == "__main__":
    asyncio.run(test_transformation())