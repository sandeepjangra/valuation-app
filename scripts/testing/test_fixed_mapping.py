#!/usr/bin/env python3

import asyncio
import sys
import os
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

from services.template_field_mapping import TemplateFieldMappingService

async def test_fixed_template_mapping():
    """Test the fixed template field mapping service."""
    try:
        # Create service instance
        service = TemplateFieldMappingService()
        
        # Connect to database
        await service.db_manager.connect()
        
        # Test with SBI template ID  
        bank_code = "SBI"
        template_id = "land_property"  # This should match the collection name pattern
        
        print(f"Testing template field mapping for bank: {bank_code}, template ID: {template_id}")
        print("="*60)
        
        # Get template structure
        template_structure = await service.get_template_structure(bank_code, template_id)
        
        if template_structure:
            print(f"✅ Template structure loaded successfully!")
            print(f"   Template ID: {template_structure.get('template_id')}")
            print(f"   Template Name: {template_structure.get('template_name')}")
            print(f"   Number of tabs: {len(template_structure.get('tabs', {}))}")
            print(f"   Total fields mapped: {len(template_structure.get('field_to_tab_mapping', {}))}")
            
            print("\n📋 Tab Structure:")
            tabs = template_structure.get('tabs', {})
            for tab_id, tab_info in tabs.items():
                fields_count = len(tab_info.get('fields', []))
                sections_count = len(tab_info.get('sections', {}))
                print(f"   • {tab_id}: {fields_count} fields, {sections_count} sections")
                
                # Show first few field IDs
                fields = tab_info.get('fields', [])
                if fields:
                    field_ids = [f.get('fieldId', 'unknown') for f in fields[:3]]
                    more_text = f" (+ {len(fields)-3} more)" if len(fields) > 3 else ""
                    print(f"     Fields: {field_ids}{more_text}")
            
            print(f"\n🔗 Field Mapping Sample (first 10):")
            field_mapping = template_structure.get('field_to_tab_mapping', {})
            for i, (field_id, tab_id) in enumerate(field_mapping.items()):
                if i >= 10:
                    print(f"     ... and {len(field_mapping) - 10} more fields")
                    break
                print(f"     {field_id} → {tab_id}")
            
            # Test organizing some sample form data
            print(f"\n🧪 Testing Data Organization:")
            sample_form_data = {
                "bank_branch_code": "SBI001",
                "applicant_id": "APP123", 
                "owner_details": "John Doe",
                "plot_size": "1000 sq ft",
                "estimated_valuation": "500000",
                "building_specifications_table": [{"type": "RCC", "area": "800"}]
            }
            
            organized_data = await service.organize_form_data_by_tabs(
                sample_form_data, bank_code, template_id
            )
            
            print(f"   Sample form data organized into {len(organized_data)} tabs:")
            for tab_id, tab_data in organized_data.items():
                field_count = len(tab_data) if isinstance(tab_data, dict) else 0
                print(f"     • {tab_id}: {field_count} fields")
            
            return True
        else:
            print("❌ Failed to load template structure")
            return False
            
    except Exception as e:
        print(f"❌ Error testing template mapping: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup database connection
        try:
            if 'service' in locals():
                await service.db_manager.close()
        except:
            pass

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_fixed_template_mapping())
    if success:
        print("\n🎉 Template field mapping test completed successfully!")
    else:
        print("\n💥 Template field mapping test failed!")
        sys.exit(1)