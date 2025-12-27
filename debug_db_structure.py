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

async def debug_template_structure():
    """Debug the actual template structure in MongoDB"""
    
    try:
        from database.multi_db_manager import MultiDatabaseManager
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        print("🔍 Debugging Template Structure in MongoDB")
        print("=" * 60)
        
        admin_db = db_manager.get_database("admin")
        
        # Check what collections exist
        collections = await admin_db.list_collection_names()
        template_collections = [c for c in collections if 'template' in c.lower() or 'sbi' in c.lower()]
        
        print(f"📁 Template-related collections:")
        for collection in template_collections:
            print(f"   • {collection}")
        
        # Check if there's a banks collection
        if "banks" in collections:
            print(f"\n🏦 Banks Collection:")
            banks_collection = admin_db["banks"]
            banks = await banks_collection.find({}).to_list(length=10)
            for bank in banks:
                bank_code = bank.get("bankCode", "Unknown")
                templates_count = len(bank.get("templates", []))
                print(f"   • {bank_code}: {templates_count} templates")
                
                # Show template details for SBI
                if bank_code.upper() == "SBI":
                    templates = bank.get("templates", [])
                    for template in templates:
                        template_id = template.get("templateId", "No ID")
                        template_name = template.get("templateName", "No Name")
                        collection_ref = template.get("collectionRef", "No Ref")
                        print(f"     - {template_id}: {template_name} → {collection_ref}")
        
        # Check sbi_land_property_details directly
        if "sbi_land_property_details" in collections:
            print(f"\n📄 SBI Land Property Details Collection:")
            template_collection = admin_db["sbi_land_property_details"]
            doc = await template_collection.find_one({})
            
            if doc:
                print(f"   • Document found with ID: {doc.get('_id')}")
                print(f"   • Template ID: {doc.get('templateId', 'Not found')}")
                print(f"   • Template Name: {doc.get('templateName', 'Not found')}")
                print(f"   • Has templateMetadata: {'templateMetadata' in doc}")
                print(f"   • Has documents array: {'documents' in doc}")
                
                if 'templateMetadata' in doc:
                    metadata = doc['templateMetadata']
                    print(f"   • Metadata tabs: {len(metadata.get('tabs', []))}")
                    for tab in metadata.get('tabs', []):
                        tab_id = tab.get('tabId', 'No ID')
                        tab_name = tab.get('tabName', 'No Name')
                        print(f"     - {tab_id}: {tab_name}")
                
                if 'documents' in doc:
                    documents = doc['documents']
                    print(f"   • Documents array: {len(documents)} documents")
                    for document in documents:
                        doc_id = document.get('documentId', 'No ID')
                        doc_name = document.get('documentName', 'No Name')
                        print(f"     - {doc_id}: {doc_name}")
        
        await db_manager.close()
        
    except Exception as e:
        print(f"❌ Error debugging template structure: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_template_structure())