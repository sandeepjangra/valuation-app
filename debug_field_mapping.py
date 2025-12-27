#!/usr/bin/env python3
"""
Debug specific fields to see why they're not being mapped
"""

import asyncio
import httpx

async def debug_field_mapping():
    """Debug why specific fields are not being mapped to groups"""
    
    print("🔍 DEBUGGING FIELD MAPPING")
    print("=" * 80)
    
    # Test fields that should be in groups
    test_fields = [
        'plot_survey_no',      # Should be in property_location group
        'door_no',             # Should be in property_location group  
        'socio_economic_class', # Should be in area_classification group
        'urban_rural',         # Should be in area_classification group
        'area_type',           # Should be in area_classification group
        'municipal_corporation' # Should be in area_classification group
    ]
    
    # Fetch template structure
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
    
    # Build field mapping exactly like the transformation function
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
    
    print(f"\n📊 Template analysis complete:")
    print(f"   📋 Total fields mapped: {len(field_to_location)}")
    print(f"   🔗 Total group fields: {len(group_fields)}")
    
    # Debug the specific test fields
    print(f"\n🔍 Testing specific fields:")
    
    for field_id in test_fields:
        print(f"\n   📄 {field_id}:")
        
        # Check if directly mapped
        if field_id in field_to_location:
            location = field_to_location[field_id]
            print(f"      ✅ DIRECTLY MAPPED:")
            print(f"         Tab: {location['tab']}")
            print(f"         Section: {location['section']}")
            print(f"         Type: {location['type']}")
        else:
            print(f"      ❌ NOT directly mapped")
            
            # Check if it's a subfield of a group
            parent_group = None
            for group_id, subfield_list in group_fields.items():
                if field_id in subfield_list:
                    parent_group = group_id
                    break
            
            if parent_group:
                print(f"      ✅ FOUND IN GROUP: {parent_group}")
                if parent_group in field_to_location:
                    group_location = field_to_location[parent_group]
                    print(f"         Group location:")
                    print(f"           Tab: {group_location['tab']}")
                    print(f"           Section: {group_location['section']}")
                    print(f"           Type: {group_location['type']}")
                else:
                    print(f"         ❌ But group {parent_group} not in field_to_location!")
            else:
                print(f"      ❌ NOT found in any group")
                
                # Show all groups for debugging
                print(f"         Available groups:")
                for group_id, subfields in list(group_fields.items())[:10]:  # Show first 10
                    if field_id.lower() in [sf.lower() for sf in subfields]:
                        print(f"           🔍 {group_id}: {subfields} (case mismatch?)")
                    else:
                        print(f"           📁 {group_id}: {subfields}")
                
                if len(group_fields) > 10:
                    print(f"           ... and {len(group_fields) - 10} more groups")
    
    # Show all group fields for reference
    print(f"\n📋 ALL GROUP FIELDS:")
    for group_id, subfields in group_fields.items():
        print(f"   🔗 {group_id}: {subfields}")
    
    return field_to_location, group_fields

if __name__ == "__main__":
    asyncio.run(debug_field_mapping())