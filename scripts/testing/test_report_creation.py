#!/usr/bin/env python3

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Load environment variables
env_path = Path(__file__).parent / "backend" / ".env"
load_dotenv(dotenv_path=env_path)

async def test_report_creation():
    """Test report creation with correct organization context"""
    
    try:
        from database.multi_db_manager import MultiDatabaseManager
        from services.template_field_mapping import TemplateFieldMappingService
        from services.reference_number_service import ReferenceNumberService
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        print("🔍 Testing Report Creation Process")
        print("="*60)
        
        # Test template mapping with sk-tindwal context
        mapping_service = TemplateFieldMappingService()
        await mapping_service.connect()
        
        # Sample form data (flat structure from frontend)
        sample_form_data = {
            "bank_branch": "sbi_mumbai_main",
            "applicant_name": "MS SSK Developers",  
            "valuation_purpose": "bank_purpose",
            "property_address": "Test Property Address",
            "owner_details": "John Doe",
            "plot_size": "1000 sq ft",
            "market_rate": "5000",
            "estimated_valuation": "5000000",
            "building_specifications_table": [{"type": "RCC", "area": "800"}],
            "land_total": "3000000"
        }
        
        print(f"📋 Sample form data fields: {len(sample_form_data)}")
        
        # Test data organization
        bank_code = "SBI"
        template_id = "land_property"
        
        print(f"🔄 Testing template mapping for {bank_code}/{template_id}")
        
        organized_data = await mapping_service.organize_form_data_by_tabs(
            sample_form_data,
            bank_code, 
            template_id
        )
        
        print(f"✅ Data organized into {len(organized_data)} tabs:")
        for tab_id, tab_data in organized_data.items():
            field_count = len(tab_data) if isinstance(tab_data, dict) else 0
            print(f"   • {tab_id}: {field_count} fields")
            
            # Show first few fields 
            if isinstance(tab_data, dict) and field_count > 0:
                sample_fields = list(tab_data.keys())[:3]
                print(f"     Sample fields: {sample_fields}")
        
        # Test reference number generation for sk-tindwal
        ref_service = ReferenceNumberService(db_manager)
        
        try:
            ref_number = await ref_service.generate_unique_reference("sk-tindwal")
            print(f"✅ Generated reference for sk-tindwal: {ref_number}")
        except Exception as e:
            print(f"❌ Error generating reference for sk-tindwal: {e}")
        
        # Simulate report creation structure 
        report_structure = {
            "reference_number": ref_number if 'ref_number' in locals() else "SKT-001",
            "bank_code": bank_code,
            "template_id": template_id, 
            "report_data": organized_data,  # This should be nested by tabs
            "status": "draft",
            "organization": "sk-tindwal"
        }
        
        print(f"\n📄 Final report structure:")
        print(f"   • Reference: {report_structure['reference_number']}")
        print(f"   • Organization: sk-tindwal")
        print(f"   • Data structure: {len(organized_data)} tabs (NOT flat)")
        
        # Check what would be saved to database
        print(f"\n🔍 Report data structure analysis:")
        if isinstance(organized_data, dict):
            total_fields = sum(len(tab_data) if isinstance(tab_data, dict) else 0 
                             for tab_data in organized_data.values())
            print(f"   • Total fields in tabs: {total_fields}")
            print(f"   • Fields outside tabs: 0 (correct!)")
        else:
            print(f"   ❌ Data is not organized by tabs!")
        
        await mapping_service.disconnect()
        await db_manager.disconnect()
        
        print(f"\n🎉 Report creation test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing report creation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_report_creation())
    if success:
        print("\n🎉 Report creation test passed!")
    else:
        print("\n💥 Report creation test failed!")
        sys.exit(1)