#!/usr/bin/env python3
"""
Create the updated transformation function with dynamic template structure and group fields
"""

transformation_function = '''
async def transform_flat_to_template_structure(
    input_data: Dict[str, Any], 
    bank_code: str, 
    template_id: str,
    mapping_service: Any
) -> Dict[str, Any]:
    """
    Transform form data to hierarchical template structure using dynamic template fetching
    
    Expected Output Structure:
    {
        "Property Details": {
            "property_part_a": {
                "agreement_to_sell": "Available"
            },
            "property_part_b": {
                "owner_details": "John Doe",
                "property_location": {
                    "plot_survey_no": "Survey-123",
                    "door_no": "45A",
                    "ts_no_village": "Village-Test"
                }
            }
        }
    }
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
        
        # Initialize result structure
        result = {}
        common_fields = {}
        
        # Handle common fields (from template.commonFields)
        common_field_ids = set()
        for common_field in template_data.get('commonFields', []):
            field_id = common_field.get('fieldId')
            if field_id:
                common_field_ids.add(field_id)
        
        # Process input data
        for field_id, field_value in input_data.items():
            if field_value is None or field_value == "":
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
                    # Unmapped field - add to _unmapped_ tab
                    if "_unmapped_" not in result:
                        result["_unmapped_"] = {}
                    result["_unmapped_"][field_id] = field_value
        
        # Add common fields if any
        if common_fields:
            result["_common_fields_"] = common_fields
        
        logger.info(f"✅ Transformation complete: {len(result)} tabs created")
        return result
        
    except Exception as e:
        logger.error(f"❌ Transformation error: {e}")
        return await fallback_transformation(input_data)

async def fallback_transformation(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Fallback transformation when template fetch fails"""
    logger.info("🔄 Using fallback transformation")
    
    # Basic structure
    result = {
        "Property Details": {
            "property_part_a": {},
            "property_part_b": {}
        },
        "_unmapped_": {}
    }
    
    # Common fields that should not be in main structure
    common_field_ids = {"report_reference_number", "valuation_date", "applicant_name"}
    common_fields = {}
    
    for field_id, value in input_data.items():
        if value is None or value == "":
            continue
            
        if field_id in common_field_ids:
            common_fields[field_id] = value
        elif field_id in ["agreement_to_sell", "list_of_documents_produced", "layout_plan", "sales_deed"]:
            result["Property Details"]["property_part_a"][field_id] = value
        elif field_id in ["owner_details", "borrower_name", "postal_address"]:
            result["Property Details"]["property_part_b"][field_id] = value
        else:
            result["_unmapped_"][field_id] = value
    
    if common_fields:
        result["_common_fields_"] = common_fields
        
    return result
'''

print("🔧 UPDATED TRANSFORMATION FUNCTION")
print("=" * 80)
print("Key improvements:")
print("✅ Dynamic template structure fetching from API")
print("✅ Uses actual section IDs like 'property_part_a', 'property_part_b'")
print("✅ Proper group field handling with subfields")
print("✅ Group fields like 'property_location' contain subfields like 'plot_survey_no'")
print("✅ Fallback mechanism when template fetch fails")
print("✅ Common fields properly separated")
print()
print("📋 Group field examples that will be handled:")
print("   🏠 property_location: plot_survey_no, door_no, ts_no_village, ward_taluka_tehsil, mandal_district")
print("   🏘️ area_classification: socio_economic_class, urban_rural, area_type, municipal_corporation")
print("   📍 coordinates: longitude, latitude")
print()
print("Ready to replace in backend/main.py")