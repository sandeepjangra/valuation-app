#!/usr/bin/env python3

"""
Debug BOB template collection structure to understand why sections aren't matching
"""

import asyncio
import sys
import os
import json

# Set MongoDB URI
os.environ['MONGODB_URI'] = "mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster"

# Add backend path
sys.path.insert(0, '/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend')

from database.multi_db_manager import MultiDatabaseSession

async def debug_bob_collection():
    """Debug BOB collection structure in detail"""
    try:
        print("🔍 Debugging BOB collection structure...")
        
        async with MultiDatabaseSession() as db:
            
            docs = await db.find_many("admin", "bob_land_property_details", {})
            
            if not docs:
                print("❌ No documents found!")
                return False
            
            doc = docs[0]
            print(f"📄 Document structure:")
            
            # Check templateMetadata
            if "templateMetadata" in doc:
                metadata = doc["templateMetadata"]
                print(f"\n📋 Template Metadata:")
                print(f"   templateName: {metadata.get('templateName', 'N/A')}")
                print(f"   templateId: {metadata.get('templateId', 'N/A')}")
                
                if "tabs" in metadata:
                    print(f"\n🗂️  Tabs Configuration ({len(metadata['tabs'])}):")
                    for i, tab in enumerate(metadata["tabs"]):
                        tab_id = tab.get("tabId", "unknown")
                        tab_name = tab.get("tabName", "unknown")
                        has_sections = tab.get("hasSections", False)
                        print(f"   {i+1}. {tab_id} ({tab_name}) - hasSections: {has_sections}")
                        
                        if has_sections and "sections" in tab:
                            print(f"      Sections defined in tab:")
                            for section in tab["sections"][:3]:  # Show first 3
                                section_id = section.get("sectionId", "unknown")
                                section_name = section.get("sectionName", "unknown")
                                print(f"        - {section_id} ({section_name})")
            
            # Check document sections
            if "sections" in doc:
                print(f"\n📑 Document Sections ({len(doc['sections'])}):")
                for i, section in enumerate(doc["sections"][:5]):  # Show first 5
                    section_id = section.get("sectionId", "unknown")
                    section_name = section.get("sectionName", "unknown") 
                    fields_count = len(section.get("fields", []))
                    print(f"   {i+1}. {section_id} ({section_name}) - {fields_count} fields")
                    
                    if fields_count > 0:
                        # Show first field as sample
                        sample_field = section["fields"][0]
                        field_id = sample_field.get("fieldId", "unknown")
                        field_name = sample_field.get("uiDisplayName", "unknown")
                        print(f"      Sample field: {field_id} ({field_name})")
            
            # Check document fields (fallback)
            if "fields" in doc:
                print(f"\n📝 Document Fields ({len(doc['fields'])}):")
                for i, field in enumerate(doc["fields"][:3]):  # Show first 3
                    field_id = field.get("fieldId", "unknown")
                    field_name = field.get("uiDisplayName", "unknown")
                    field_type = field.get("fieldType", "unknown")
                    print(f"   {i+1}. {field_id} ({field_name}) - {field_type}")
            
            # Show the matching logic issue
            print(f"\n🔍 Debug: Matching Logic Test")
            metadata = doc.get("templateMetadata", {})
            tabs_config = metadata.get("tabs", [])
            
            if tabs_config:
                first_tab = tabs_config[0]
                print(f"First tab: {first_tab.get('tabId', 'unknown')}")
                print(f"Has sections: {first_tab.get('hasSections', False)}")
                
                if first_tab.get("hasSections") and "sections" in first_tab:
                    first_section_config = first_tab["sections"][0]
                    section_id_to_find = first_section_config.get("sectionId")
                    print(f"Looking for section: {section_id_to_find}")
                    
                    # Check if this section exists in document
                    found_section = None
                    for doc_section in doc.get("sections", []):
                        if doc_section.get("sectionId") == section_id_to_find:
                            found_section = doc_section
                            break
                    
                    if found_section:
                        print(f"✅ Found matching section with {len(found_section.get('fields', []))} fields")
                    else:
                        print(f"❌ Section not found in document sections")
                        print(f"Available section IDs: {[s.get('sectionId') for s in doc.get('sections', [])]}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error debugging BOB collection: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_bob_collection())
    if not success:
        sys.exit(1)