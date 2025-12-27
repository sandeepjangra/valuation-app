#!/usr/bin/env python3
"""
Deep dive into MongoDB document structure to find where actual field data is stored
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

async def deep_dive_template():
    """Look at complete MongoDB document structure"""
    
    try:
        from database.multi_db_manager import MultiDatabaseManager
        
        # Initialize the DB manager
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        print("🔍 Deep Dive: MongoDB Template Document Structure")
        print("=" * 60)
        
        admin_db = db_manager.get_database("admin")
        
        # Get the SBI land property template document
        template_collection = admin_db["sbi_land_property_details"]
        doc = await template_collection.find_one({})
        
        if doc:
            print("📄 Document found! Keys:")
            for key in doc.keys():
                value = doc[key]
                if isinstance(value, dict):
                    print(f"  📁 {key}: dict with {len(value)} keys")
                    if key not in ["_id", "templateMetadata"]:  # Show content of non-metadata
                        for subkey in list(value.keys())[:5]:  # Show first 5 keys
                            subvalue = value[subkey]
                            if isinstance(subvalue, dict):
                                print(f"    📂 {subkey}: dict with {len(subvalue)} keys")
                            elif isinstance(subvalue, list):
                                print(f"    📋 {subkey}: list with {len(subvalue)} items")
                            else:
                                print(f"    📄 {subkey}: {type(subvalue).__name__}")
                        if len(value) > 5:
                            print(f"    ... and {len(value) - 5} more keys")
                elif isinstance(value, list):
                    print(f"  📋 {key}: list with {len(value)} items")
                else:
                    print(f"  📄 {key}: {type(value).__name__} = {str(value)[:50]}...")
            
            # Look at the documents array which seems to contain the actual data
            if "documents" in doc:
                print(f"\n📋 Examining documents array:")
                documents = doc["documents"]
                print(f"   Found {len(documents)} documents")
                
                for i, document in enumerate(documents):
                    print(f"\n   📄 Document {i+1}:")
                    if isinstance(document, dict):
                        for key, value in document.items():
                            if isinstance(value, dict):
                                print(f"     📁 {key}: dict with {len(value)} keys")
                                # Show field names in this section
                                field_names = list(value.keys())[:3]
                                for field_name in field_names:
                                    field_value = value[field_name]
                                    if isinstance(field_value, dict) and "fieldId" in field_value:
                                        field_id = field_value.get("fieldId", "No ID")
                                        ui_name = field_value.get("uiDisplayName", "No Name")
                                        print(f"       🔸 {field_id}: {ui_name}")
                                    else:
                                        print(f"       📄 {field_name}: {type(field_value).__name__}")
                                if len(value) > 3:
                                    print(f"       ... and {len(value) - 3} more fields")
                            elif isinstance(value, list):
                                print(f"     📋 {key}: list with {len(value)} items")
                            else:
                                print(f"     📄 {key}: {type(value).__name__}")
                    else:
                        print(f"     Type: {type(document).__name__}")
            
            # Look at specific keys that might contain field data
            for potential_key in ["property_details", "site_characteristics", "valuation", "construction_specifications", "detailed_valuation"]:
                if potential_key in doc:
                    print(f"\n🎯 Examining {potential_key}:")
                    section_data = doc[potential_key]
                    if isinstance(section_data, dict):
                        for subsection_key, subsection_value in section_data.items():
                            if isinstance(subsection_value, dict):
                                print(f"  📂 {subsection_key}: {len(subsection_value)} fields")
                                # Show first few field names
                                field_names = list(subsection_value.keys())[:5]
                                for field_name in field_names:
                                    print(f"    🔸 {field_name}")
                                if len(subsection_value) > 5:
                                    print(f"    ... and {len(subsection_value) - 5} more fields")
                            else:
                                print(f"  📄 {subsection_key}: {type(subsection_value).__name__}")
        else:
            print("❌ No document found in sbi_land_property_details collection")
        
        await db_manager.disconnect()
        
    except Exception as e:
        print(f"❌ Deep dive failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(deep_dive_template())