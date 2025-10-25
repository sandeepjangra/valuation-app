#!/usr/bin/env python3
"""
Clean Upload of Dynamic Template Structure to MongoDB Atlas
This script cleans up the collection and uploads only the dynamic template
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from backend.database.multi_db_manager import MultiDatabaseSession

async def clean_and_upload_template():
    """Clean the collection and upload only the dynamic template"""
    
    print("🧹 Starting clean upload of dynamic template to MongoDB Atlas...")
    
    # Load the dynamic template structure from local file
    template_file = project_root / "backend" / "data" / "sbi_land_property_details.json"
    
    if not template_file.exists():
        print(f"❌ Template file not found: {template_file}")
        return False
    
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            template_data = json.load(f)
        
        print(f"✅ Loaded template data from {template_file}")
        
        # Add required fields for the database manager
        template_data.update({
            "isActive": True,
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc),
            "version": 1
        })
        
        # Connect to MongoDB Atlas
        async with MultiDatabaseSession() as db:
            print("🔗 Connected to MongoDB Atlas")
            
            # Get direct access to the collection for cleanup
            collection = db.get_collection("admin", "sbi_land_property_details")
            
            # Delete ALL documents in the collection to start fresh
            print("🗑️  Clearing existing collection...")
            delete_result = await collection.delete_many({})
            print(f"✅ Deleted {delete_result.deleted_count} existing documents")
            
            # Insert the new dynamic template
            print("📝 Inserting dynamic template...")
            insert_result = await collection.insert_one(template_data)
            
            if insert_result.inserted_id:
                print(f"✅ Successfully inserted dynamic template with ID: {insert_result.inserted_id}")
            else:
                print("❌ Failed to insert dynamic template")
                return False
            
            # Verify the upload
            print("🔍 Verifying uploaded template...")
            verification_data = await db.find_one("admin", "sbi_land_property_details", {})
            
            if verification_data:
                has_metadata = 'templateMetadata' in verification_data
                has_documents = 'documents' in verification_data
                tabs_count = len(verification_data.get('templateMetadata', {}).get('tabs', []))
                docs_count = len(verification_data.get('documents', []))
                
                print(f"✅ Verification successful:")
                print(f"   - Has templateMetadata: {has_metadata}")
                print(f"   - Has documents: {has_documents}")
                print(f"   - Number of tabs: {tabs_count}")
                print(f"   - Number of documents: {docs_count}")
                print(f"   - Is active: {verification_data.get('isActive', False)}")
                
                if has_metadata and has_documents and tabs_count == 5:
                    print("🎉 Dynamic template successfully uploaded to MongoDB Atlas!")
                    print("💡 The application will now load dynamic tabs from MongoDB Atlas")
                    
                    # Show the tab structure
                    tabs = verification_data.get('templateMetadata', {}).get('tabs', [])
                    print("\n📑 Uploaded tab structure:")
                    for i, tab in enumerate(tabs, 1):
                        tab_id = tab.get('tabId', 'N/A')
                        tab_name = tab.get('tabName', 'N/A')
                        has_sections = tab.get('hasSections', False)
                        print(f"   {i}. {tab_name} (ID: {tab_id}) - Sections: {has_sections}")
                    
                    return True
                else:
                    print("❌ Verification failed - uploaded data is incomplete")
                    return False
            else:
                print("❌ Verification failed - could not read back uploaded data")
                return False
                
    except Exception as e:
        print(f"❌ Error uploading dynamic template: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function to run the clean upload process"""
    print("🚀 Dynamic Template Clean Upload Script")
    print("=" * 50)
    
    # Check if MongoDB URI is configured
    if not os.getenv("MONGODB_URI"):
        print("⚠️  MONGODB_URI environment variable not set")
        print("📝 Please ensure MongoDB Atlas is configured before running this script")
        return
    
    success = await clean_and_upload_template()
    
    if success:
        print("\n🎯 NEXT STEPS:")
        print("1. Start the backend server: python -m backend.main")
        print("2. Test the dynamic API endpoint: /api/templates/SBI/LAND/aggregated-fields")
        print("3. Verify that 5 dynamic tabs are returned with proper structure")
        print("4. Start the frontend and test the dynamic tab rendering")
    else:
        print("\n❌ Upload failed. Please check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())