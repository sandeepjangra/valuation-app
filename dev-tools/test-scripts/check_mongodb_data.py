#!/usr/bin/env python3
"""
Script to check the MongoDB apartment template data integrity
"""

import os
os.environ["MONGODB_URI"] = "mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster"
os.environ["MONGODB_ADMIN_DB_NAME"] = "valuation_admin"

import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from database.multi_db_manager import MultiDatabaseSession

async def check_apartment_data():
    """Check the apartment template data in MongoDB."""
    
    print("🔍 Checking Apartment Template Data in MongoDB")
    print("=" * 55)
    
    async with MultiDatabaseSession() as db:
        admin_db = db.get_database("admin")
        collection = admin_db["sbi_apartment_property_details"]
        
        documents = []
        async for doc in collection.find({}):
            documents.append(doc)
        
        print(f"📊 Total documents: {len(documents)}")
        
        total_fields_all_docs = 0
        
        for i, doc in enumerate(documents):
            template_name = doc.get('templateName', f'Document {i}')
            template_id = doc.get('templateId', 'Unknown')
            has_sections = 'sections' in doc
            sections_count = len(doc.get('sections', []))
            
            print(f"\n📄 Document {i}: {template_name}")
            print(f"   Template ID: {template_id}")
            print(f"   Has sections: {has_sections}")
            print(f"   Sections count: {sections_count}")
            
            if has_sections and sections_count > 0:
                total_fields_this_doc = 0
                for j, section in enumerate(doc['sections']):
                    section_name = section.get('sectionName', f'Section {j}')
                    section_id = section.get('sectionId', 'Unknown')
                    fields_count = len(section.get('fields', []))
                    total_fields_this_doc += fields_count
                    
                    print(f"     📁 Section {j}: {section_name} (ID: {section_id})")
                    print(f"        Fields: {fields_count}")
                    
                    # Show first few field names
                    if fields_count > 0:
                        field_names = [f.get('fieldId', 'Unknown') for f in section.get('fields', [])[:3]]
                        print(f"        Sample fields: {', '.join(field_names)}{'...' if fields_count > 3 else ''}")
                
                print(f"   📊 Total fields in document: {total_fields_this_doc}")
                total_fields_all_docs += total_fields_this_doc
            else:
                print(f"   ⚠️  No sections or empty sections")
                
                # Check if there are any top-level fields
                if 'fields' in doc:
                    fields_count = len(doc.get('fields', []))
                    print(f"   📊 Top-level fields: {fields_count}")
                    total_fields_all_docs += fields_count
        
        print(f"\n📈 SUMMARY:")
        print(f"   Total documents: {len(documents)}")
        print(f"   Total fields across all documents: {total_fields_all_docs}")
        
        # Compare with what the API should return based on templateMetadata
        template_metadata = documents[0].get('templateMetadata', {}) if documents else {}
        tabs_config = template_metadata.get('tabs', [])
        print(f"   Template metadata tabs: {len(tabs_config)}")
        
        if tabs_config:
            valuation_tab = None
            for tab in tabs_config:
                if tab.get('tabName') == 'Valuation':
                    valuation_tab = tab
                    break
            
            if valuation_tab:
                sections_config = valuation_tab.get('sections', [])
                print(f"   Valuation tab configured sections: {len(sections_config)}")
                for section_config in sections_config:
                    print(f"     - {section_config.get('sectionName')} (ID: {section_config.get('sectionId')})")

async def main():
    await check_apartment_data()

if __name__ == "__main__":
    asyncio.run(main())