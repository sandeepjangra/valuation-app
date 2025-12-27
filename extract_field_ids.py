#!/usr/bin/env python3
"""
Extract actual field IDs from the documents array structure
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

async def extract_field_ids():
    """Extract all field IDs from the template documents"""
    
    try:
        from database.multi_db_manager import MultiDatabaseManager
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        print("🔍 Extracting Field IDs from Template Documents")
        print("=" * 60)
        
        admin_db = db_manager.get_database("admin")
        
        # Get the SBI land property template document
        template_collection = admin_db["sbi_land_property_details"]
        doc = await template_collection.find_one({})
        
        if doc and "documents" in doc:
            documents = doc["documents"]
            all_field_ids = []
            
            for i, document in enumerate(documents):
                doc_id = document.get("documentId", f"doc_{i}")
                doc_name = document.get("documentName", f"Document {i+1}")
                print(f"\n📄 {doc_name} ({doc_id}):")
                
                # Check for sections (tab-based structure)
                if "sections" in document:
                    sections = document["sections"]
                    print(f"   📋 {len(sections)} sections found")
                    
                    for section in sections:
                        section_id = section.get("sectionId", "unknown")
                        section_name = section.get("sectionName", "Unknown Section")
                        
                        if "fields" in section:
                            fields = section["fields"]
                            print(f"   📂 {section_name} ({section_id}): {len(fields)} fields")
                            
                            for field in fields:
                                field_id = field.get("fieldId", "No ID")
                                ui_name = field.get("uiDisplayName", field.get("label", "No Name"))
                                field_type = field.get("fieldType", "unknown")
                                
                                print(f"      🔸 {field_id}: {ui_name} ({field_type})")
                                all_field_ids.append((field_id, doc_id, section_id))
                
                # Check for direct fields (non-sectioned)
                elif "fields" in document:
                    fields = document["fields"]
                    print(f"   📋 Direct fields: {len(fields)}")
                    
                    for field in fields:
                        field_id = field.get("fieldId", "No ID")
                        ui_name = field.get("uiDisplayName", field.get("label", "No Name"))
                        field_type = field.get("fieldType", "unknown")
                        
                        print(f"      🔸 {field_id}: {ui_name} ({field_type})")
                        all_field_ids.append((field_id, doc_id, "direct"))
            
            print(f"\n📊 Summary: Found {len(all_field_ids)} total fields")
            print("\n🗂️ Field to Tab Mapping:")
            
            # Group by document (which should correspond to tabs)
            tab_mapping = {}
            for field_id, doc_id, section_id in all_field_ids:
                tab_id = doc_id  # Use document ID as tab ID
                if tab_id not in tab_mapping:
                    tab_mapping[tab_id] = []
                tab_mapping[tab_id].append(field_id)
                print(f"   {field_id} -> {tab_id} (section: {section_id})")
            
            print(f"\n📁 Fields per tab:")
            for tab_id, field_ids in tab_mapping.items():
                print(f"   {tab_id}: {len(field_ids)} fields")
        
        await db_manager.disconnect()
        
    except Exception as e:
        print(f"❌ Field extraction failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(extract_field_ids())