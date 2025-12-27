#!/usr/bin/env python3
"""
Get SBI template structure via backend API to analyze and propose storage format
"""

import asyncio
import aiohttp
import json

async def analyze_sbi_via_api():
    """Get SBI template structure through the backend API"""
    
    base_url = "http://localhost:8000"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Login first
            async with session.post(f'{base_url}/api/auth/login', 
                                  json={'email': 'sk.tindwal@gmail.com', 'password': 'admin123'}) as resp:
                if resp.status != 200:
                    print(f"❌ Login failed: {resp.status}")
                    return
                data = await resp.json()
                token = data['data']['access_token']
                print("✅ Logged in successfully")
            
            # Get SBI land-property template structure
            headers = {'Authorization': f'Bearer {token}'}
            async with session.get(f'{base_url}/api/templates/SBI/land-property/aggregated-fields', 
                                 headers=headers) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    print(f"❌ Template fetch failed: {resp.status} - {text}")
                    return
                
                template_data = await resp.json()
                print("✅ Got SBI land-property template structure")
                
                await analyze_template_structure(template_data)
                
    except Exception as e:
        print(f"❌ Error: {e}")

async def analyze_template_structure(template_data):
    """Analyze the template structure and propose storage format"""
    
    print(f"\n🔍 ANALYZING SBI LAND PROPERTY TEMPLATE")
    print("=" * 80)
    
    # Get template metadata
    template_metadata = template_data.get('templateMetadata', {})
    tabs = template_metadata.get('tabs', [])
    
    print(f"📊 Total Tabs: {len(tabs)}")
    
    # Analyze each tab
    storage_structure = {}
    field_mapping = {}  # Track where each field should go
    
    for tab_idx, tab in enumerate(tabs):
        tab_name = tab.get('tabName') or tab.get('name', f'Tab_{tab_idx}')
        sections = tab.get('sections', [])
        direct_fields = tab.get('fields', [])
        
        print(f"\n📁 TAB: '{tab_name}'")
        print(f"   📊 Sections: {len(sections)}")
        print(f"   📊 Direct Fields: {len(direct_fields)}")
        
        # Initialize tab structure
        tab_structure = {}
        
        # Process sections
        for section in sections:
            section_name = section.get('name', 'Unknown Section')
            section_type = section.get('type', 'form_group')
            fields = section.get('fields', [])
            
            print(f"   📁 SECTION: '{section_name}' (Type: {section_type})")
            print(f"      📊 Fields: {len(fields)}")
            
            # Show sample fields
            if fields:
                print(f"      📄 Sample Fields:")
                for i, field in enumerate(fields[:5]):  # Show first 5
                    field_id = field.get('fieldId', 'NO_ID')
                    field_type = field.get('fieldType', 'unknown')
                    label = field.get('label', 'No Label')[:30]
                    print(f"         {field_id} ({field_type}): {label}")
                    
                    # Map field to its location
                    field_mapping[field_id] = {
                        'tab': tab_name,
                        'section': section_name,
                        'type': field_type
                    }
                
                if len(fields) > 5:
                    print(f"         ... and {len(fields)-5} more fields")
            
            # Add section to tab structure
            if section_name not in tab_structure:
                tab_structure[section_name] = {
                    'type': section_type,
                    'fields': {}
                }
        
        # Process direct fields
        if direct_fields:
            print(f"   📄 DIRECT TAB FIELDS: {len(direct_fields)}")
            for field in direct_fields[:3]:  # Show first 3
                field_id = field.get('fieldId', 'NO_ID')
                field_type = field.get('fieldType', 'unknown')
                print(f"      {field_id} ({field_type})")
                
                field_mapping[field_id] = {
                    'tab': tab_name,
                    'section': '_direct_',  # Special marker for direct fields
                    'type': field_type
                }
        
        storage_structure[tab_name] = tab_structure
    
    print(f"\n📋 TOTAL FIELDS MAPPED: {len(field_mapping)}")
    
    # Now propose the storage structure
    await propose_storage_format(storage_structure, field_mapping, tabs)

async def propose_storage_format(storage_structure, field_mapping, tabs):
    """Propose the optimal storage format based on template analysis"""
    
    print(f"\n🎯 PROPOSED STORAGE STRUCTURE FOR SBI LAND PROPERTY")
    print("=" * 80)
    
    # Show the template hierarchy we discovered
    print(f"📋 TEMPLATE HIERARCHY DISCOVERED:")
    for tab_name, tab_data in storage_structure.items():
        print(f"\n📁 {tab_name}")
        for section_name, section_data in tab_data.items():
            section_type = section_data.get('type', 'unknown')
            print(f"   📂 {section_name} ({section_type})")
    
    print(f"\n💡 RECOMMENDED STORAGE FORMAT:")
    
    # Create example structure
    example_structure = {}
    
    print(f"""
OPTION 1 - HIERARCHICAL TAB → SECTION → FIELDS:
{{""")
    
    for tab_name in list(storage_structure.keys())[:2]:  # Show first 2 tabs as example
        print(f'  "{tab_name}": {{')
        
        sections = storage_structure[tab_name]
        for section_name in list(sections.keys())[:2]:  # Show first 2 sections
            print(f'    "{section_name}": {{')
            
            # Find sample fields for this tab/section
            sample_fields = []
            for field_id, location in field_mapping.items():
                if location['tab'] == tab_name and location['section'] == section_name:
                    sample_fields.append(field_id)
                if len(sample_fields) >= 3:
                    break
            
            for field_id in sample_fields:
                print(f'      "{field_id}": "sample_value",')
            
            print(f'    }},')
        print(f'  }},')
    
    print(f"""}}

ADVANTAGES OF THIS STRUCTURE:
✅ Preserves template hierarchy (Tab → Section → Field)
✅ Easy navigation: data["Property Details"]["Documents"]["agreement_to_sell"]
✅ Supports section-level operations and validation
✅ Clean separation of concerns
✅ Frontend can render forms directly from structure
✅ Backward compatible - can flatten if needed

IMPLEMENTATION:
1. Transform nested input → flat fields
2. Map each field to its Tab/Section using field_mapping
3. Rebuild hierarchical structure
4. Store in MongoDB with proper organization

EXAMPLE TRANSFORMATION:
Input:  property_details.property_part_a.agreement_to_sell = "Available"
Flat:   agreement_to_sell = "Available"  
Output: report_data["Property Details"]["Documents"]["agreement_to_sell"] = "Available"
""")

    # Generate the field mapping for transformation function
    print(f"\n🔧 FIELD MAPPING FOR TRANSFORMATION:")
    print("```python")
    print("FIELD_TO_LOCATION = {")
    
    # Show sample mapping
    sample_count = 0
    for field_id, location in field_mapping.items():
        if sample_count < 10:  # Show first 10 as example
            tab = location['tab']
            section = location['section']
            if section != '_direct_':
                print(f'    "{field_id}": {{"tab": "{tab}", "section": "{section}"}},')
            else:
                print(f'    "{field_id}": {{"tab": "{tab}", "section": null}},  # Direct field')
            sample_count += 1
        else:
            break
    
    print("    # ... (more field mappings)")
    print("}")
    print("```")

if __name__ == "__main__":
    print("🔍 SBI TEMPLATE ANALYSIS VIA API")
    print("🎯 Analyzing structure to design proper storage format")
    print("-" * 60)
    asyncio.run(analyze_sbi_via_api())