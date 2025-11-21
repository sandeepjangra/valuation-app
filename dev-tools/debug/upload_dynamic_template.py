#!/usr/bin/env python3
"""
Upload Dynamic Template Structure to MongoDB Atlas
This script uploads the dynamic SBI Land template with templateMetadata to MongoDB Atlas
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from backend.database.multi_db_manager import MultiDatabaseSession

async def upload_dynamic_template():
    """Upload the dynamic SBI Land template structure to MongoDB Atlas"""
    
    print("🔄 Starting dynamic template upload to MongoDB Atlas...")
    
    # Load the dynamic template structure from local file
    template_file = project_root / "backend" / "data" / "sbi_land_property_details.json"
    
    if not template_file.exists():
        print(f"❌ Template file not found: {template_file}")
        return False
    
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            template_data = json.load(f)
        
        print(f"✅ Loaded template data from {template_file}")
        print(f"📊 Template contains:")
        print(f"   - templateMetadata: {'templateMetadata' in template_data}")
        print(f"   - documents: {len(template_data.get('documents', []))} documents")
        print(f"   - tabs: {len(template_data.get('templateMetadata', {}).get('tabs', []))} tabs")
        
        # Connect to MongoDB Atlas
        async with MultiDatabaseSession() as db:
            print("🔗 Connected to MongoDB Atlas")
            
            # Check if collection exists and has data
            existing_data = await db.find_one("admin", "sbi_land_property_details", {})
            
            if existing_data:
                print("⚠️  Existing SBI Land template found in MongoDB Atlas")
                print("🔄 Updating with dynamic structure...")
                
                # For the database manager's versioned system, we'll delete and insert new
                # First delete existing data
                delete_success = await db.delete_one("admin", "sbi_land_property_details", {})
                
                if delete_success:
                    print("✅ Removed existing template data")
                else:
                    print("⚠️  Could not remove existing data, proceeding with insert...")
                
                # Insert new document with dynamic structure
                try:
                    result = await db.insert_one("admin", "sbi_land_property_details", template_data)
                    if result:
                        print("✅ Successfully inserted updated template with dynamic structure")
                    else:
                        print("❌ Failed to insert updated template")
                        return False
                except Exception as e:
                    print(f"❌ Error inserting updated template: {e}")
                    return False
                    
            else:
                print("📝 No existing template found, inserting new dynamic template...")
                
                # Insert new document
                try:
                    result = await db.insert_one("admin", "sbi_land_property_details", template_data)
                    
                    if result:
                        print(f"✅ Successfully inserted new dynamic template with ID: {result}")
                    else:
                        print("❌ Failed to insert dynamic template")
                        return False
                except Exception as e:
                    print(f"❌ Error inserting new template: {e}")
                    return False
            
            # Verify the upload by reading back the data
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
                
                if has_metadata and has_documents and tabs_count == 5:
                    print("🎉 Dynamic template successfully uploaded to MongoDB Atlas!")
                    print("💡 The application will now load dynamic tabs from MongoDB Atlas")
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
    """Main function to run the upload process"""
    print("🚀 Dynamic Template Upload Script")
    print("=" * 50)
    
    # Check if MongoDB URI is configured
    if not os.getenv("MONGODB_URI"):
        print("⚠️  MONGODB_URI environment variable not set")
        print("📝 Please ensure MongoDB Atlas is configured before running this script")
        print("💡 You can set it in your environment or .env file")
        return
    
    success = await upload_dynamic_template()
    
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