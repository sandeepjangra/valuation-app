#!/usr/bin/env python3
"""
Test script to verify that reports are being organized correctly by tabs
"""

import asyncio
import sys
from pathlib import Path
import os

# Add backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent / "backend" / ".env"
load_dotenv(dotenv_path=env_path)

async def test_template_mapping():
    """Test the template field mapping service"""
    
    try:
        from services.template_field_mapping import TemplateFieldMappingService
        
        # Initialize the service
        mapping_service = TemplateFieldMappingService()
        await mapping_service.connect()
        
        print("🧪 Testing Template Field Mapping Service")
        print("=" * 50)
        
        # Test data - simulating form submission
        test_form_data = {
            # Common fields (should stay at root level)
            "applicant_name": "Test Applicant",
            "bank_branch": "sbi_mumbai_main", 
            "valuation_date": "2025-12-21",
            "inspection_date": "2025-12-21",
            "property_address": "Test Property Address",
            
            # Tab-specific fields (should be nested)
            "total_extent_of_site": "1000",
            "valuation_rate_per_unit": "5000",
            "estimated_value_of_land": "5000000",
            "construction_cost": "2000000",
            "market_value": "7000000",
            
            # Other fields that should go in tabs
            "site_area": "1000 sq ft",
            "plot_survey_no": "123",
            "door_no": "45",
        }
        
        print(f"📝 Input: {len(test_form_data)} flat form fields")
        
        # Test organization
        bank_code = "SBI"
        template_id = "land-property"
        
        organized_data = await mapping_service.organize_form_data_by_tabs(
            test_form_data, bank_code, template_id
        )
        
        print(f"📊 Output: {len(organized_data)} organized entries")
        print("\nOrganized Data Structure:")
        print("-" * 30)
        
        # Show the organized structure
        for key, value in organized_data.items():
            if isinstance(value, dict) and value:
                print(f"📁 {key}/ (TAB)")
                for field_id, field_value in value.items():
                    print(f"   ├── {field_id}: {field_value}")
            else:
                print(f"📋 {key}: {value} (COMMON)")
        
        print(f"\n✅ Template mapping test completed!")
        
        # Test extraction (reverse process)
        print(f"\n🔄 Testing extraction...")
        extracted_data = await mapping_service.extract_form_data_from_tabs(
            organized_data, bank_code, template_id
        )
        
        print(f"📤 Extracted: {len(extracted_data)} flat fields")
        
        # Verify data integrity
        missing_fields = set(test_form_data.keys()) - set(extracted_data.keys())
        if missing_fields:
            print(f"⚠️ Missing fields after extraction: {missing_fields}")
        else:
            print("✅ All fields preserved during organization/extraction")
            
        await mapping_service.disconnect()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_template_mapping())