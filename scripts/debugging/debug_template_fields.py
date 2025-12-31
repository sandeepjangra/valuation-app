#!/usr/bin/env python3
"""
Debug script to see what field IDs are available in the SBI land-property template
"""

import asyncio
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent / "backend" / ".env"
load_dotenv(dotenv_path=env_path)

async def debug_template_fields():
    """Debug what fields are actually in the template"""
    
    try:
        from services.template_field_mapping import TemplateFieldMappingService
        
        # Initialize the service
        mapping_service = TemplateFieldMappingService()
        await mapping_service.connect()
        
        print("🔍 Debugging Template Field IDs")
        print("=" * 50)
        
        # Get template structure
        bank_code = "SBI"
        template_id = "land-property"
        
        template_structure = await mapping_service.get_template_structure(bank_code, template_id)
        
        if template_structure:
            print(f"✅ Template structure loaded")
            print(f"📁 Tabs: {len(template_structure['tabs'])}")
            
            # Show all field IDs in each tab
            for tab_id, tab_info in template_structure["tabs"].items():
                print(f"\n📂 TAB: {tab_id} ({tab_info['tab_name']})")
                
                if tab_info.get("sections"):
                    for section_id, section_info in tab_info["sections"].items():
                        print(f"   📋 Section: {section_id} ({section_info['section_name']})")
                        fields = section_info.get("fields", [])
                        for field in fields:
                            field_id = field.get("fieldId", "No ID")
                            field_name = field.get("uiDisplayName", "No Name")
                            print(f"      🔸 {field_id}: {field_name}")
                else:
                    # Direct fields in tab
                    fields = tab_info.get("fields", [])
                    for field in fields:
                        field_id = field.get("fieldId", "No ID")
                        field_name = field.get("uiDisplayName", "No Name")
                        print(f"   🔸 {field_id}: {field_name}")
            
            # Show field to tab mapping
            field_to_tab = mapping_service.get_field_tab_mapping(template_structure)
            print(f"\n🗂️ Field to Tab Mapping ({len(field_to_tab)} mappings):")
            for field_id, tab_id in field_to_tab.items():
                print(f"   {field_id} -> {tab_id}")
                
        else:
            print("❌ Could not load template structure")
        
        # Also check common fields
        common_field_ids = await mapping_service.get_common_field_ids()
        print(f"\n📄 Common Field IDs ({len(common_field_ids)}):")
        for field_id in sorted(common_field_ids):
            print(f"   🔸 {field_id}")
            
        # Also check what's actually in the MongoDB documents
        print("\n🔍 Raw MongoDB Document Analysis:")
        
        admin_db = mapping_service.db_manager.get_database("admin")
        
        # Find the bank template
        unified_doc = await admin_db.banks.find_one({"_id": "all_banks_comprehensive_v4"})
        if unified_doc:
            banks = unified_doc.get("banks", [])
            sbi_bank = None
            for bank in banks:
                if bank.get("bankCode") == "SBI":
                    sbi_bank = bank
                    break
            
            if sbi_bank:
                templates = sbi_bank.get("templates", [])
                land_template = None
                for template in templates:
                    if template.get("templateCode") == "land-property":
                        land_template = template
                        break
                
                if land_template:
                    collection_ref = land_template.get("collectionRef")
                    print(f"📋 Collection Reference: {collection_ref}")
                    
                    # Get documents from the collection
                    if collection_ref:
                        template_collection = admin_db[collection_ref]
                        docs = await template_collection.find({}).to_list(length=None)
                        print(f"📄 Found {len(docs)} documents in {collection_ref}")
                        
                        for i, doc in enumerate(docs):
                            print(f"\n📄 Document {i+1}:")
                            template_metadata = doc.get("templateMetadata", {})
                            tabs_config = template_metadata.get("tabs", [])
                            print(f"   📁 Tabs in metadata: {len(tabs_config)}")
                            
                            for tab_config in tabs_config:
                                tab_id = tab_config.get("tabId", "")
                                has_sections = tab_config.get("hasSections", False)
                                print(f"   📂 {tab_id} (hasSections: {has_sections})")
                                
                                if has_sections:
                                    sections = tab_config.get("sections", [])
                                    for section in sections:
                                        section_id = section.get("sectionId", "")
                                        fields = section.get("fields", [])
                                        print(f"      📋 {section_id}: {len(fields)} fields")
                                        for field in fields[:3]:  # Show first 3 fields
                                            field_id = field.get("fieldId", "No ID")
                                            print(f"         🔸 {field_id}")
                                        if len(fields) > 3:
                                            print(f"         ... and {len(fields) - 3} more")
                                else:
                                    direct_fields = tab_config.get("fields", [])
                                    print(f"      Direct fields: {len(direct_fields)}")
        
        await mapping_service.disconnect()
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_template_fields())