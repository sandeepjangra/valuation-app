#!/usr/bin/env python3
"""
Simple transformation - save everything in one section with proper table handling
"""

def simple_transform_with_tables(input_data):
    """
    Simple transformation that saves everything in one section but handles tables properly
    
    Dynamic tables are identified by:
    1. Having 'table' in the field name or type
    2. Being arrays of objects with consistent structure
    3. Having special table metadata
    """
    
    result = {
        "report_data": {},
        "tables": {},  # Separate section for table definitions
        "metadata": {
            "transformation": "simple",
            "table_count": 0,
            "field_count": 0
        }
    }
    
    table_count = 0
    field_count = 0
    
    # Process each field in input data
    for field_id, field_value in input_data.items():
        
        # Skip system metadata
        if field_id in ['status', 'bankName', 'templateName', 'organizationId', 
                       'customTemplateId', 'propertyType', 'reportType', 'createdAt', 'updatedAt']:
            continue
            
        if field_value is None or field_value == "":
            continue
            
        # Check if this is a dynamic table
        if is_dynamic_table(field_id, field_value):
            table_definition = extract_table_definition(field_id, field_value)
            result["tables"][field_id] = table_definition
            
            # Also save in main data for backward compatibility
            result["report_data"][field_id] = field_value
            table_count += 1
            print(f"   📊 Table detected: {field_id} with {len(field_value) if isinstance(field_value, list) else 'N/A'} rows")
        else:
            # Regular field - save as is
            result["report_data"][field_id] = field_value
            
        field_count += 1
    
    result["metadata"]["table_count"] = table_count
    result["metadata"]["field_count"] = field_count
    
    return result

def is_dynamic_table(field_id, field_value):
    """
    Detect if a field represents a dynamic table
    """
    
    # Check by field name patterns
    table_indicators = ['table', 'list', 'items', 'rows', 'entries', 'specifications', 'valuation']
    if any(indicator in field_id.lower() for indicator in table_indicators):
        if isinstance(field_value, list) and len(field_value) > 0:
            return True
    
    # Check if it's an array of objects with consistent structure
    if isinstance(field_value, list) and len(field_value) > 0:
        first_item = field_value[0]
        if isinstance(first_item, dict):
            # Check if all items have similar structure
            first_keys = set(first_item.keys())
            if len(first_keys) > 1:  # More than just one field
                for item in field_value[1:3]:  # Check first few items
                    if isinstance(item, dict) and len(set(item.keys()).intersection(first_keys)) >= len(first_keys) * 0.7:
                        return True
    
    # Check for table metadata
    if isinstance(field_value, dict):
        if 'rows' in field_value or 'columns' in field_value or 'tableData' in field_value:
            return True
    
    return False

def extract_table_definition(field_id, field_value):
    """
    Extract table structure and metadata for proper saving/loading
    """
    
    definition = {
        "field_id": field_id,
        "table_type": "dynamic",
        "created_at": "2025-12-27T00:00:00Z",  # You can use actual timestamp
        "structure": {
            "columns": [],
            "rows": [],
            "metadata": {}
        }
    }
    
    if isinstance(field_value, list) and len(field_value) > 0:
        # Array of objects - extract column structure from first item
        first_item = field_value[0]
        if isinstance(first_item, dict):
            
            # Extract column definitions
            for col_key, col_value in first_item.items():
                column_def = {
                    "id": col_key,
                    "name": col_key.replace('_', ' ').title(),
                    "type": detect_column_type(col_value),
                    "editable": True,
                    "required": False
                }
                definition["structure"]["columns"].append(column_def)
            
            # Store all row data
            definition["structure"]["rows"] = field_value
            definition["structure"]["metadata"] = {
                "row_count": len(field_value),
                "column_count": len(definition["structure"]["columns"]),
                "allow_add_rows": True,
                "allow_add_columns": True,
                "allow_delete_rows": True,
                "allow_delete_columns": False  # Usually safer to not allow column deletion
            }
    
    elif isinstance(field_value, dict):
        # Object with table structure
        if 'rows' in field_value:
            definition["structure"]["rows"] = field_value.get('rows', [])
        if 'columns' in field_value:
            definition["structure"]["columns"] = field_value.get('columns', [])
        if 'tableData' in field_value:
            definition["structure"]["rows"] = field_value.get('tableData', [])
        
        # Extract metadata
        definition["structure"]["metadata"] = {
            "row_count": len(definition["structure"]["rows"]),
            "column_count": len(definition["structure"]["columns"]),
            "allow_add_rows": field_value.get('allowAddRows', True),
            "allow_add_columns": field_value.get('allowAddColumns', True),
            "allow_delete_rows": field_value.get('allowDeleteRows', True),
            "allow_delete_columns": field_value.get('allowDeleteColumns', False)
        }
    
    return definition

def detect_column_type(sample_value):
    """
    Detect column type from sample value
    """
    if isinstance(sample_value, bool):
        return "boolean"
    elif isinstance(sample_value, int):
        return "number"
    elif isinstance(sample_value, float):
        return "decimal"
    elif isinstance(sample_value, str):
        # Check for specific patterns
        if sample_value.lower() in ['yes', 'no', 'true', 'false']:
            return "boolean"
        elif sample_value.startswith('₹') or sample_value.startswith('$'):
            return "currency"
        elif any(char.isdigit() for char in sample_value):
            if '.' in sample_value:
                return "decimal"
            elif sample_value.replace('-', '').replace(',', '').isdigit():
                return "number"
        return "text"
    else:
        return "text"

# Test the solution
if __name__ == "__main__":
    
    print("🧪 TESTING SIMPLE TRANSFORMATION WITH TABLE HANDLING")
    print("=" * 80)
    
    # Test data with dynamic tables
    test_data = {
        # Regular fields
        "property_address": "123 Main Street",
        "valuation_date": "2025-12-27",
        "inspector_name": "John Doe",
        
        # Dynamic table - building specifications
        "building_specifications_table": [
            {"item": "Foundation", "material": "RCC", "condition": "Good", "area_sqft": 1200, "rate_per_sqft": 500, "total_value": 600000},
            {"item": "Walls", "material": "Brick", "condition": "Excellent", "area_sqft": 800, "rate_per_sqft": 300, "total_value": 240000},
            {"item": "Roofing", "material": "RCC Slab", "condition": "Good", "area_sqft": 1000, "rate_per_sqft": 400, "total_value": 400000}
        ],
        
        # Dynamic table - floor wise valuation
        "floor_wise_valuation_table": [
            {"floor": "Ground Floor", "area": 1200, "rate": 2000, "value": 2400000},
            {"floor": "First Floor", "area": 1000, "rate": 1800, "value": 1800000}
        ],
        
        # Table in different format
        "amenities_list": {
            "rows": [
                {"amenity": "Swimming Pool", "available": "Yes", "condition": "Excellent"},
                {"amenity": "Gym", "available": "Yes", "condition": "Good"},
                {"amenity": "Parking", "available": "Yes", "condition": "Fair"}
            ],
            "allowAddRows": True,
            "allowDeleteRows": True
        },
        
        # System metadata (should be filtered out)
        "status": "draft",
        "bankName": "SBI",
        "organizationId": "sk-tindwal"
    }
    
    # Transform the data
    result = simple_transform_with_tables(test_data)
    
    print(f"📊 TRANSFORMATION RESULTS:")
    print(f"   📄 Total fields: {result['metadata']['field_count']}")
    print(f"   📊 Tables detected: {result['metadata']['table_count']}")
    
    print(f"\n📋 REGULAR DATA:")
    for field_id, value in result["report_data"].items():
        if not is_dynamic_table(field_id, value):
            print(f"   📄 {field_id}: {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}")
    
    print(f"\n📊 DYNAMIC TABLES:")
    for table_id, table_def in result["tables"].items():
        structure = table_def["structure"]
        print(f"   📊 {table_id}:")
        print(f"      📏 Columns: {len(structure['columns'])} ({[col['name'] for col in structure['columns']]})")
        print(f"      📋 Rows: {len(structure['rows'])}")
        print(f"      🔧 Add Rows: {structure['metadata']['allow_add_rows']}")
        print(f"      🔧 Add Columns: {structure['metadata']['allow_add_columns']}")
    
    print(f"\n📋 SAMPLE TABLE STRUCTURE:")
    if "building_specifications_table" in result["tables"]:
        table_def = result["tables"]["building_specifications_table"]
        print(f"   Table: building_specifications_table")
        print(f"   Columns:")
        for col in table_def["structure"]["columns"]:
            print(f"      - {col['name']} ({col['type']})")
        print(f"   Sample Row: {table_def['structure']['rows'][0] if table_def['structure']['rows'] else 'No data'}")
    
    print(f"\n✅ This structure can be easily saved/retrieved with proper table handling!")