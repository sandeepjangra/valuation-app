#!/usr/bin/env python3
"""
Complete analysis of SBI template and proposed storage structure
"""

import json

def analyze_sbi_template():
    """Analyze the SBI template structure from the saved JSON file"""
    
    print("🔍 SBI LAND PROPERTY TEMPLATE STRUCTURE ANALYSIS")
    print("=" * 80)
    
    # Load the template data
    with open('sbi_template_debug.json', 'r') as f:
        template_data = json.load(f)
    
    bank_specific_tabs = template_data.get('bankSpecificTabs', [])
    common_fields = template_data.get('commonFields', [])
    
    print(f"📊 Template Overview:")
    print(f"   📂 Bank-specific tabs: {len(bank_specific_tabs)}")
    print(f"   📄 Common fields: {len(common_fields)}")
    
    # Analyze each tab
    field_mapping = {}
    tab_structure = {}
    
    print(f"\n📁 TAB STRUCTURE ANALYSIS:")
    
    for tab in bank_specific_tabs:
        tab_name = tab.get('tabName', 'Unknown Tab')
        sections = tab.get('sections', [])
        tab_fields = tab.get('fields', [])
        
        print(f"\n📂 TAB: '{tab_name}'")
        print(f"   📊 Total sections: {len(sections)}")
        print(f"   📊 Direct fields: {len(tab_fields)}")
        
        tab_structure[tab_name] = {
            'sections': [],
            'direct_fields': []
        }
        
        # Analyze sections
        if sections:
            for i, section in enumerate(sections):
                section_name = section.get('name') or f"Section {i+1}"
                section_fields = section.get('fields', [])
                
                print(f"   📁 SECTION {i+1}: '{section_name}' ({len(section_fields)} fields)")
                
                # Show sample fields
                if section_fields:
                    sample_fields = section_fields[:3]  # Show first 3
                    for field in sample_fields:
                        field_id = field.get('fieldId', 'NO_ID')
                        field_type = field.get('fieldType', 'unknown')
                        label = field.get('uiDisplayName', 'No Label')[:40]
                        print(f"      📄 {field_id} ({field_type}): {label}")
                        
                        # Map field location
                        field_mapping[field_id] = {
                            'tab': tab_name,
                            'section': section_name,
                            'section_index': i,
                            'type': field_type
                        }
                    
                    if len(section_fields) > 3:
                        print(f"      📄 ... and {len(section_fields) - 3} more fields")
                
                tab_structure[tab_name]['sections'].append({
                    'name': section_name,
                    'index': i,
                    'field_count': len(section_fields)
                })
        
        # Direct tab fields
        if tab_fields:
            print(f"   📄 DIRECT TAB FIELDS: ({len(tab_fields)} fields)")
            for field in tab_fields[:3]:
                field_id = field.get('fieldId', 'NO_ID')
                field_type = field.get('fieldType', 'unknown')
                label = field.get('uiDisplayName', 'No Label')[:40]
                print(f"      📄 {field_id} ({field_type}): {label}")
                
                field_mapping[field_id] = {
                    'tab': tab_name,
                    'section': None,  # Direct field
                    'section_index': None,
                    'type': field_type
                }
            
            if len(tab_fields) > 3:
                print(f"      📄 ... and {len(tab_fields) - 3} more fields")
    
    # Add common fields
    print(f"\n📄 COMMON FIELDS:")
    for field in common_fields:
        field_id = field.get('fieldId', 'NO_ID')
        field_type = field.get('fieldType', 'unknown')
        label = field.get('uiDisplayName', 'No Label')[:40]
        print(f"   📄 {field_id} ({field_type}): {label}")
        
        field_mapping[field_id] = {
            'tab': '_common_',
            'section': None,
            'section_index': None,
            'type': field_type
        }
    
    print(f"\n📋 TOTAL FIELDS MAPPED: {len(field_mapping)}")
    
    # Now propose storage structure
    propose_storage_structure(tab_structure, field_mapping)

def propose_storage_structure(tab_structure, field_mapping):
    """Propose the optimal storage structure"""
    
    print(f"\n🎯 PROPOSED STORAGE STRUCTURE")
    print("=" * 80)
    
    print(f"""
DISCOVERED TEMPLATE HIERARCHY:
📂 Property Details (4 sections)
📂 Site Characteristics (2 sections) 
📂 Valuation (2 sections)
📂 Construction Specifications (2 sections)
📂 Detailed Valuation (0 sections - direct fields)
📄 Common Fields (report-level)

RECOMMENDED STORAGE FORMAT - HIERARCHICAL STRUCTURE:
""")
    
    # Create example structure
    example_data = {
        "Property Details": {
            "Section 1": {
                "agreement_to_sell": "Available",
                "list_of_documents_produced": "Sale deed, Survey settlement",
                "allotment_letter": "Available"
            },
            "Section 2": {
                "owner_details": "John Doe, S/o Richard Doe",
                "borrower_name": "MS SSK Developers",
                "postal_address": "123 Main Street, Mumbai"
            },
            "Section 3": {
                "area_classification": "Urban residential",
                "government_regulation": "Mumbai Municipal Corp guidelines"
            },
            "Section 4": {
                "boundaries_dimensions_table": "N:40ft, S:40ft, E:25ft, W:25ft",
                "coordinates": "19.0760° N, 72.8777° E",
                "land_area_and_occupancy": "1000 sq ft, vacant"
            }
        },
        "Site Characteristics": {
            "Section 1": {
                "locality_surroundings": "Well developed residential locality",
                "physical_characteristics": "Rectangular plot, level terrain"
            },
            "Section 2": {
                "road_access": "30 ft wide paved road access",
                "utility_services_group": "Water, electricity, drainage available"
            }
        },
        "Valuation": {
            "Section 1": {
                "plot_size": "1000",
                "market_rate": "5000",
                "estimated_valuation": "5000000"
            },
            "Section 2": {
                "building_constructed": "no",
                "building_basic_info": "",
                "no_building_remarks": "Land only - no construction"
            }
        },
        "Construction Specifications": {
            "Section 1": {
                "building_specifications_table": "",
                "floor_wise_valuation_table": ""
            },
            "Section 2": {
                "extra_items": "",
                "amenities": "",
                "services": ""
            }
        },
        "Detailed Valuation": {
            "land_total": 5000000,
            "building_total": 0,
            "grand_total": 5000000
        },
        "_common_fields_": {
            "report_reference_number": "CEV/RVO/299/0029/26122025",
            "valuation_date": "2025-12-26",
            "inspection_date": "2025-12-25",
            "applicant_name": "MS SSK Developers"
        }
    }
    
    print("```json")
    print(json.dumps(example_data, indent=2))
    print("```")
    
    print(f"""
✅ ADVANTAGES OF THIS STRUCTURE:

1. 🎯 PERFECT ALIGNMENT: Matches SBI template hierarchy exactly
   - Tab → Section → Fields structure preserved
   
2. 🚀 FRONTEND EFFICIENCY: Easy form rendering
   - data["Property Details"]["Section 1"]["agreement_to_sell"]
   - Clean section-based form generation
   
3. 🔧 BACKEND SIMPLICITY: Clear transformation path
   - Flatten input → Map to tab/section → Rebuild hierarchy
   
4. 📊 VALIDATION READY: Section-level and tab-level validation
   - Validate entire sections at once
   - Progressive validation during form filling
   
5. 🔄 SAVE/DRAFT COMPATIBLE: Perfect for incremental saves
   - Save individual sections
   - Preserve partial progress
   - Easy conflict resolution

TRANSFORMATION ALGORITHM:
""")
    
    # Generate field mapping code
    print("```python")
    print("FIELD_TO_LOCATION = {")
    
    # Show sample mapping for first 15 fields
    sample_count = 0
    for field_id, location in field_mapping.items():
        if sample_count < 15:
            tab = location['tab']
            section = location['section']
            section_idx = location['section_index']
            
            if section and section_idx is not None:
                print(f'    "{field_id}": {{"tab": "{tab}", "section": "Section {section_idx + 1}"}},')
            elif tab == '_common_':
                print(f'    "{field_id}": {{"tab": "_common_fields_", "section": null}},')
            else:
                print(f'    "{field_id}": {{"tab": "{tab}", "section": null}},')
            
            sample_count += 1
        else:
            break
    
    print("    # ... (remaining field mappings)")
    print("}")
    
    print("""
def transform_to_hierarchical_structure(flat_data):
    result = {}
    
    for field_id, value in flat_data.items():
        location = FIELD_TO_LOCATION.get(field_id)
        if not location:
            continue
            
        tab = location['tab']
        section = location['section']
        
        # Initialize tab
        if tab not in result:
            result[tab] = {}
            
        # Place field in appropriate location
        if section:
            if section not in result[tab]:
                result[tab][section] = {}
            result[tab][section][field_id] = value
        else:
            result[tab][field_id] = value
    
    return result
```

🚀 IMPLEMENTATION STEPS:

1. Update transform_flat_to_template_structure() function
2. Use bankSpecificTabs structure from template API
3. Create section-based field mapping
4. Transform flat data to hierarchical structure
5. Save in MongoDB with proper organization
6. Update frontend to handle hierarchical data

This structure will solve your save draft issues by providing consistent
data organization that matches your template design!
""")

if __name__ == "__main__":
    analyze_sbi_template()