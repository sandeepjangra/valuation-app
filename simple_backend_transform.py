"""
Simple transformation replacement for the backend
"""

async def simple_transform_with_tables(input_data, bank_code, template_id, mapping_service):
    """
    SIMPLE TRANSFORMATION: Save all data in one section with proper table handling
    No complex grouping or nested structure - just clean data organization
    """
    from datetime import datetime
    
    print(f"🚀 SIMPLE TRANSFORMATION: {bank_code}/{template_id}")
    print(f"📋 Processing {len(input_data)} input fields")
    
    result = {
        "report_data": {},
        "tables": {},
        "_common_fields_": {}
    }
    
    # Common fields that go to separate section
    common_field_ids = {"valuation_date", "applicant_name", "inspection_date", "valuation_purpose"}
    
    # System metadata to filter out
    metadata_fields = {
        'status', 'bankName', 'templateName', 'organizationId', 
        'customTemplateId', 'customTemplateName', 'propertyType', 
        'reportType', 'createdAt', 'updatedAt'
    }
    
    table_count = 0
    field_count = 0
    
    def is_table_field(field_id, field_value):
        """Check if field is a table"""
        table_indicators = ['table', 'list', 'items', 'rows', 'entries', 'specifications', 'valuation_table', '_table']
        if any(indicator in field_id.lower() for indicator in table_indicators):
            if isinstance(field_value, (list, dict)):
                return True
        
        if isinstance(field_value, list) and len(field_value) > 0:
            first_item = field_value[0]
            if isinstance(first_item, dict) and len(first_item) > 1:
                return True
        
        if isinstance(field_value, dict):
            if 'rows' in field_value or 'columns' in field_value or 'tableData' in field_value:
                return True
        
        return False
    
    def create_table_def(field_id, field_value):
        """Create table definition"""
        definition = {
            "field_id": field_id,
            "table_type": "dynamic",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "structure": {
                "columns": [],
                "rows": [],
                "metadata": {}
            }
        }
        
        if isinstance(field_value, list) and len(field_value) > 0:
            first_item = field_value[0]
            if isinstance(first_item, dict):
                for col_key, col_value in first_item.items():
                    column_def = {
                        "id": col_key,
                        "name": col_key.replace('_', ' ').title(),
                        "type": "text",
                        "editable": True,
                        "required": False
                    }
                    definition["structure"]["columns"].append(column_def)
                
                definition["structure"]["rows"] = field_value
                definition["structure"]["metadata"] = {
                    "row_count": len(field_value),
                    "column_count": len(definition["structure"]["columns"]),
                    "allow_add_rows": True,
                    "allow_add_columns": True,
                    "allow_delete_rows": True
                }
        
        return definition
    
    # Process each field
    for field_id, field_value in input_data.items():
        
        # Skip empty values and metadata
        if field_value is None or field_value == "" or field_id in metadata_fields:
            continue
            
        # Handle structured data from frontend (flatten it)
        if isinstance(field_value, dict) and field_id not in common_field_ids:
            # Check if it's a nested structure like property_details
            if any(key.startswith(('property_part_', 'site_part_', 'valuation_part_', 'construction_part_')) for key in field_value.keys()):
                print(f"🔄 Flattening structured data from {field_id}")
                # Flatten the nested structure
                for section_key, section_data in field_value.items():
                    if isinstance(section_data, dict):
                        for sub_field_id, sub_field_value in section_data.items():
                            if sub_field_value is not None and sub_field_value != "":
                                result["report_data"][sub_field_id] = sub_field_value
                                field_count += 1
                continue
        
        # Check if it's a common field
        if field_id in common_field_ids:
            result["_common_fields_"][field_id] = field_value
            print(f"📄 Common field: {field_id}")
            continue
            
        # Check if it's a dynamic table
        if is_table_field(field_id, field_value):
            table_definition = create_table_def(field_id, field_value)
            result["tables"][field_id] = table_definition
            
            # Also save in main data for backward compatibility
            result["report_data"][field_id] = field_value
            table_count += 1
            print(f"📊 Table: {field_id} with {len(field_value) if isinstance(field_value, list) else 'object'} entries")
        else:
            # Regular field - save as is
            result["report_data"][field_id] = field_value
            print(f"📄 Field: {field_id}")
            
        field_count += 1
    
    print(f"✅ Simple transformation complete: {field_count} fields, {table_count} tables")
    return result

# Test it
if __name__ == "__main__":
    import asyncio
    
    test_data = {
        # Regular fields
        "property_address": "123 Main Street",
        "valuation_date": "2025-12-27",
        "inspector_name": "John Doe",
        
        # Structured data (should be flattened)
        "property_details": {
            "property_part_a": {
                "sales_deed": "NA",
                "ats": "NA"
            },
            "property_part_b": {
                "city_town_village": "town",
                "property_location": "central"
            }
        },
        
        # Table data
        "building_specifications_table": [
            {"item": "Foundation", "material": "RCC", "rate": 500},
            {"item": "Walls", "material": "Brick", "rate": 300}
        ],
        
        # Metadata (should be filtered)
        "status": "draft",
        "bankName": "SBI"
    }
    
    async def test():
        result = await simple_transform_with_tables(test_data, "SBI", "land-property", None)
        
        print(f"\n📊 RESULT:")
        print(f"   📄 Report data: {len(result['report_data'])} fields")
        print(f"   📊 Tables: {len(result['tables'])}")
        print(f"   📋 Common fields: {len(result['_common_fields_'])}")
        
        print(f"\n📄 Fields:")
        for field_id, value in result['report_data'].items():
            if not isinstance(value, list):  # Don't print table data
                print(f"      {field_id}: {value}")
        
        print(f"\n📊 Tables:")
        for table_id in result['tables'].keys():
            print(f"      {table_id}")
    
    asyncio.run(test())