#!/usr/bin/env python3
"""
Test script to debug table field detection and saving
"""
import os
import sys
import json
import asyncio
from datetime import datetime

# Set environment variables before importing
os.environ.setdefault('MONGODB_URI', 'mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreports.xsnyysn.mongodb.net/')

# Add backend directory to path
sys.path.append('/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend')

from main import transform_flat_to_template_structure

async def test_table_detection():
    """Test different table formats to see what gets detected and saved"""
    
    print("🧪 Testing table field detection and saving...")
    print("=" * 60)
    
    # Test payload with various table formats
    test_payload = {
        "report_id": "test_tables_123",
        "bank_id": "sbi_bank",
        "applicant_name": "Test User",
        
        # Test 1: Simple array of objects (typical table format)
        "boundaries_dimensions_table": [
            {"direction": "North", "as_per_document": "20 ft", "dimensions_actuals": "19.5 ft"},
            {"direction": "South", "as_per_document": "20 ft", "dimensions_actuals": "19.8 ft"},
            {"direction": "East", "as_per_document": "30 ft", "dimensions_actuals": "29.2 ft"},
            {"direction": "West", "as_per_document": "30 ft", "dimensions_actuals": "29.7 ft"}
        ],
        
        # Test 2: Building specifications (column-dynamic)
        "building_specifications_table": [
            {"sr_no": "1", "description": "Foundation", "ground_floor": "RCC", "first_floor": "RCC"},
            {"sr_no": "2", "description": "Walls", "ground_floor": "Brick", "first_floor": "Brick"},
            {"sr_no": "3", "description": "Roofing", "ground_floor": "RCC Slab", "first_floor": "RCC Slab"}
        ],
        
        # Test 3: Floor-wise valuation (row-dynamic)  
        "floor_wise_valuation_table": [
            {
                "sr_no": "1",
                "floors_level": "Ground Floor", 
                "particulars_description": "Residential Area",
                "plinth_covered_area": "1200",
                "estimated_replacement_rate": "2500",
                "estimated_replacement_cost": "3000000",
                "depreciation": "150000", 
                "net_value": "2850000"
            },
            {
                "sr_no": "2",
                "floors_level": "First Floor",
                "particulars_description": "Residential Area", 
                "plinth_covered_area": "1200",
                "estimated_replacement_rate": "2500",
                "estimated_replacement_cost": "3000000",
                "depreciation": "150000",
                "net_value": "2850000"
            }
        ],
        
        # Test 4: Alternative format (object with rows)
        "test_table_object": {
            "rows": [
                {"col1": "value1", "col2": "value2"},
                {"col1": "value3", "col2": "value4"}
            ],
            "columns": ["col1", "col2"]
        },
        
        # Regular fields
        "postal_address": "123 Test Street",
        "property_type": "residential"
    }
    
    print(f"📥 Input payload with tables:")
    print(json.dumps(test_payload, indent=2))
    
    # Transform using our function
    result = await transform_flat_to_template_structure(test_payload, "sbi_bank", "sbi_template", None)
    
    print(f"\n📤 Transformation result:")
    print(json.dumps(result, indent=2, default=str))
    
    print(f"\n🔍 Table Detection Analysis:")
    
    table_fields_expected = [
        "boundaries_dimensions_table",
        "building_specifications_table", 
        "floor_wise_valuation_table",
        "test_table_object"
    ]
    
    tables_section = result.get("tables", {})
    data_section = result.get("data", {})
    
    for field_name in table_fields_expected:
        if field_name in tables_section:
            print(f"✅ {field_name}: Correctly detected as table")
            table_def = tables_section[field_name]
            print(f"   Structure: {table_def.get('structure', {}).get('metadata', {})}")
        elif field_name in data_section:
            print(f"⚠️ {field_name}: Saved to data (not detected as table)")
            print(f"   Value type: {type(data_section[field_name])}")
            if isinstance(data_section[field_name], list):
                print(f"   Array length: {len(data_section[field_name])}")
        else:
            print(f"❌ {field_name}: Not found anywhere!")
    
    print(f"\n📊 Summary:")
    print(f"Tables detected: {len(tables_section)}")
    print(f"Regular fields: {len(data_section)}")
    print(f"Table field IDs: {list(tables_section.keys())}")
    
    return result

if __name__ == "__main__":
    asyncio.run(test_table_detection())