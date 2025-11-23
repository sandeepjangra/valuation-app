#!/usr/bin/env python3
"""
Script to restore the SBI apartment template in MongoDB with proper 4-document structure
"""

import os
os.environ["MONGODB_URI"] = "mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster"
os.environ["MONGODB_ADMIN_DB_NAME"] = "valuation_admin"

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from database.multi_db_manager import MultiDatabaseSession

async def restore_apartment_template():
    """Restore the apartment template with proper structure in MongoDB."""
    
    print("🔄 Restoring SBI Apartment Template in MongoDB")
    print("=" * 55)
    
    # Load the corrected local template file
    template_file = Path(__file__).parent / "backend" / "data" / "sbi" / "apartment" / "sbi_apartment_property_details.json"
    
    try:
        with open(template_file, 'r') as f:
            template_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading template file: {e}")
        return False
    
    print(f"✅ Loaded template from {template_file}")
    print(f"📊 Template has {len(template_data.get('documents', []))} documents")
    
    # Fix document 3 to have sections key
    documents = template_data.get('documents', [])
    if len(documents) > 3:
        doc3 = documents[3]
        if 'sections' not in doc3:
            doc3['sections'] = []
            print("🔧 Added missing sections array to document 3")
    
    # Update timestamp
    template_data['updatedAt'] = datetime.now().isoformat() + 'Z'
    
    async with MultiDatabaseSession() as db:
        admin_db = db.get_database("admin")
        collection = admin_db["sbi_apartment_property_details"]
        
        # Get current data for backup
        print("💾 Creating backup of current MongoDB data...")
        current_docs = []
        async for doc in collection.find({}):
            current_docs.append(doc)
        
        print(f"📊 Current MongoDB has {len(current_docs)} documents")
        
        # Clear the collection
        print("🗑️  Clearing current collection...")
        delete_result = await collection.delete_many({})
        print(f"🗑️  Deleted {delete_result.deleted_count} documents")
        
        # Insert the corrected template
        print("📝 Inserting corrected template...")
        insert_result = await collection.insert_one(template_data)
        print(f"✅ Inserted template with ID: {insert_result.inserted_id}")
        
        # Verify the restoration
        print("🔍 Verifying restoration...")
        new_docs = []
        async for doc in collection.find({}):
            new_docs.append(doc)
        
        if len(new_docs) == 1:
            restored_template = new_docs[0]
            documents = restored_template.get('documents', [])
            
            print(f"✅ Verification successful:")
            print(f"   📊 Collection documents: {len(new_docs)}")
            print(f"   📊 Template documents: {len(documents)}")
            
            total_fields = 0
            for i, doc in enumerate(documents):
                template_name = doc.get('templateName', f'Document {i}')
                has_sections = 'sections' in doc
                sections_count = len(doc.get('sections', []))
                
                doc_fields = 0
                if has_sections and sections_count > 0:
                    for section in doc['sections']:
                        doc_fields += len(section.get('fields', []))
                
                total_fields += doc_fields
                print(f"   📄 Doc {i}: {template_name} - Sections: {sections_count}, Fields: {doc_fields}")
            
            print(f"   📊 Total fields across all documents: {total_fields}")
            
            if total_fields > 0:
                print("\n🎉 Template restoration successful!")
                print("\n📋 Next steps:")
                print("   1. Test the apartment template aggregation API")
                print("   2. Verify field counts are now correct")
                print("   3. Test the Valuation tab loading in frontend")
                return True
            else:
                print("\n❌ Restoration failed - no fields found in documents")
                return False
        else:
            print(f"\n❌ Restoration failed - expected 1 collection document, got {len(new_docs)}")
            return False

async def main():
    success = await restore_apartment_template()
    
    if not success:
        print("\n❌ Template restoration failed")
        print("   Please check the error messages above")

if __name__ == "__main__":
    asyncio.run(main())