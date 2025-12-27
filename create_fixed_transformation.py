#!/usr/bin/env python3
"""
Create a fixed transformation function that handles mixed input formats
"""

def create_fixed_transformation():
    """Generate the fixed transformation function"""
    
    fixed_function = '''async def transform_flat_to_template_structure(
    input_data: Dict[str, Any], 
    bank_code: str, 
    template_id: str,
    mapping_service: Any
) -> Dict[str, Any]:
    """
    Transform form data to hierarchical template structure using dynamic template fetching
    
    Handles mixed input formats:
    1. Already structured data (from frontend forms)
    2. Flat individual fields that need grouping
    3. Mix of both (removes duplicates and organizes properly)
    """
    try:
        import httpx
        logger.info(f"🔄 Starting dynamic transformation with template structure fetching")
        logger.info(f"🔍 Input data type: {type(input_data)}, keys: {list(input_data.keys()) if isinstance(input_data, dict) else 'Not dict'}")
        
        # Fetch template structure dynamically
        template_url = f"http://localhost:8000/api/templates/{bank_code}/{template_id}/aggregated-fields"
        
        try:
            async with httpx.AsyncClient() as client:
                template_response = await client.get(template_url, timeout=10.0)
                if template_response.status_code != 200:
                    logger.error(f"❌ Failed to fetch template: {template_response.status_code}")
                    return await fallback_transformation(input_data)
                
                template_data = template_response.json()
                logger.info(f"✅ Template fetched successfully")
                
        except Exception as e:
            logger.error(f"❌ Template fetch error: {e}")
            return await fallback_transformation(input_data)
        
        # Build field mapping from template structure
        field_to_location = {}
        group_fields = {}
        
        # Process bank specific tabs
        bank_tabs = template_data.get('bankSpecificTabs', [])
        
        for tab in bank_tabs:
            tab_id = tab.get('tabId', 'unknown')
            tab_name = tab.get('tabName', 'Unknown Tab')
            
            sections = tab.get('sections', [])
            for section in sections:
                section_id = section.get('sectionId', 'unknown')
                section_name = section.get('sectionName', 'Unknown Section')
                
                fields = section.get('fields', [])
                for field in fields:
                    field_id = field.get('fieldId')
                    field_type = field.get('fieldType', 'text')
                    
                    if field_id:
                        field_to_location[field_id] = {
                            "tab": tab_name,
                            "section": section_id,  # Use actual section ID like property_part_a
                            "type": field_type
                        }
                        
                        # Handle group fields
                        if field_type == 'group':
                            subfields = field.get('subFields', [])
                            group_fields[field_id] = [sf.get('fieldId') for sf in subfields if sf.get('fieldId')]
                            logger.info(f"🔗 Group field {field_id}: {len(group_fields[field_id])} subfields")
        
        logger.info(f"📊 Mapped {len(field_to_location)} fields, {len(group_fields)} group fields")
        
        # Identify already structured vs flat data
        structured_tabs = set()
        flat_fields = {}
        
        # Handle common fields (from template.commonFields)
        common_field_ids = set()
        for common_field in template_data.get('commonFields', []):
            field_id = common_field.get('fieldId')
            if field_id:
                common_field_ids.add(field_id)
        
        # Separate structured tabs from individual fields
        for key, value in input_data.items():
            if isinstance(value, dict) and key not in common_field_ids:
                # Check if this looks like a structured tab
                expected_tabs = {tab.get('tabName') for tab in bank_tabs}
                expected_tabs.update(['property_details', 'site_characteristics', 'valuation', 'construction_specifications', 'detailed_valuation'])
                
                if key in expected_tabs or key.lower().replace(' ', '_') in {t.lower().replace(' ', '_') for t in expected_tabs}:
                    structured_tabs.add(key)
                else:
                    flat_fields[key] = value
            else:
                # Individual field or common field
                flat_fields[key] = value
        
        logger.info(f"📊 Found {len(structured_tabs)} structured tabs, {len(flat_fields)} individual fields")
        
        # Start with structured data if it exists
        result = {}
        
        # Skip structured tabs that contain old format data - only use properly formatted ones
        for tab_key, tab_data in input_data.items():
            if tab_key in structured_tabs and isinstance(tab_data, dict):
                # Map old tab names to new ones
                tab_mapping = {
                    'property_details': 'Property Details',
                    'site_characteristics': 'Site Characteristics', 
                    'valuation': 'Valuation',
                    'construction_specifications': 'Construction Specifications',
                    'detailed_valuation': 'Detailed Valuation'
                }
                
                proper_tab_name = tab_mapping.get(tab_key, tab_key)
                
                # Only include if it has proper section structure
                if any(section_key.startswith(('property_part_', 'site_part_', 'valuation_part_', 'construction_part_')) for section_key in tab_data.keys()):
                    if proper_tab_name not in result:
                        result[proper_tab_name] = {}
                    result[proper_tab_name].update(tab_data)
        
        # Process individual flat fields
        common_fields = {}
        
        # Filter out metadata fields that shouldn't be processed
        metadata_fields = {
            'status', 'bankName', 'templateName', 'organizationId', 'customTemplateId', 
            'customTemplateName', 'propertyType', 'reportType', 'createdAt', 'updatedAt'
        }
        
        for field_id, field_value in flat_fields.items():
            if field_value is None or field_value == "" or field_id in metadata_fields:
                continue
                
            # Check if it's a common field
            if field_id in common_field_ids:
                common_fields[field_id] = field_value
                continue
            
            # Check if field is mapped in template
            if field_id in field_to_location:
                location = field_to_location[field_id]
                tab_name = location["tab"]
                section_id = location["section"]
                
                # Initialize tab and section if needed
                if tab_name not in result:
                    result[tab_name] = {}
                if section_id not in result[tab_name]:
                    result[tab_name][section_id] = {}
                
                result[tab_name][section_id][field_id] = field_value
                
            else:
                # Check if this field is a subfield of a group
                parent_group = None
                for group_id, subfield_list in group_fields.items():
                    if field_id in subfield_list:
                        parent_group = group_id
                        break
                
                if parent_group and parent_group in field_to_location:
                    # This is a subfield - add it to its parent group
                    location = field_to_location[parent_group]
                    tab_name = location["tab"]
                    section_id = location["section"]
                    
                    # Initialize structures
                    if tab_name not in result:
                        result[tab_name] = {}
                    if section_id not in result[tab_name]:
                        result[tab_name][section_id] = {}
                    if parent_group not in result[tab_name][section_id]:
                        result[tab_name][section_id][parent_group] = {}
                    
                    # Add subfield to group
                    result[tab_name][section_id][parent_group][field_id] = field_value
                    logger.info(f"📄 Added subfield {field_id} to group {parent_group}")
                    
                else:
                    # Only add unmapped fields if they are actual form data (not metadata)
                    if not field_id.startswith(('_', 'custom', 'bank', 'template', 'organization', 'property_type', 'report_type')):
                        if "_unmapped_" not in result:
                            result["_unmapped_"] = {}
                        result["_unmapped_"][field_id] = field_value
        
        # Add common fields if any
        if common_fields:
            result["_common_fields_"] = common_fields
        
        # Clean up empty _unmapped_ section
        if "_unmapped_" in result and not result["_unmapped_"]:
            del result["_unmapped_"]
        
        logger.info(f"✅ Transformation complete: {len(result)} tabs created")
        return result
        
    except Exception as e:
        logger.error(f"❌ Transformation error: {e}")
        return await fallback_transformation(input_data)'''
    
    return fixed_function

print("🔧 FIXED TRANSFORMATION FUNCTION")
print("=" * 80)
print("Key fixes:")
print("✅ Handles mixed input formats (structured + flat)")
print("✅ Prevents duplicate tab creation (property_details vs Property Details)")
print("✅ Filters out metadata fields (status, bankName, etc.)")
print("✅ Removes empty _unmapped_ sections")
print("✅ Maps old tab names to proper template names")
print("✅ Only processes actual form data, not system metadata")
print()
print(create_fixed_transformation())