#!/usr/bin/env python3

"""
Check current database structure and collections
"""

import asyncio
import sys
import os

# Set MongoDB URI
os.environ['MONGODB_URI'] = "mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster"

# Add backend path
sys.path.insert(0, '/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend')

from database.multi_db_manager import MultiDatabaseSession

async def check_database_structure():
    """Check what collections and data exist in the database"""
    try:
        print("🔍 Checking database structure...")
        
        async with MultiDatabaseSession() as db:
            # Get the databases and collections
            print("\n📊 Checking available collections in 'admin' database:")
            
            # Check banks collection
            print("\n1️⃣ Banks Collection:")
            banks = await db.find_many("admin", "banks", {})
            print(f"   Found {len(banks)} bank documents")
            
            for bank in banks:
                bank_code = bank.get("bankCode", "Unknown")
                bank_name = bank.get("bankName", "Unknown")
                is_active = bank.get("isActive", False)
                templates = bank.get("templates", [])
                
                print(f"   📍 {bank_code} - {bank_name} (Active: {is_active})")
                if templates:
                    print(f"      Templates: {len(templates)}")
                    for template in templates[:3]:  # Show first 3
                        print(f"        - {template.get('templateId', 'Unknown')}: {template.get('templateName', 'Unknown')}")
                else:
                    print(f"      ⚠️  No templates found")
            
            # Check common_form_fields collection
            print("\n2️⃣ Common Form Fields Collection:")
            common_fields_docs = await db.find_many("admin", "common_form_fields", {})
            print(f"   Found {len(common_fields_docs)} common field documents")
            
            total_fields = 0
            for doc in common_fields_docs:
                fields = doc.get("fields", [])
                total_fields += len(fields)
                doc_name = doc.get("_id", "Unknown")
                print(f"   📄 {doc_name}: {len(fields)} fields")
            
            print(f"   📊 Total common fields: {total_fields}")
            
            # Check for bank-specific template collections
            print("\n3️⃣ Checking Bank-Specific Template Collections:")
            
            # List of potential collections to check
            potential_collections = [
                "sbi_land_property_details",
                "bob_land_property_details", 
                "pnb_land_property_details",
                "ubi_land_property_details",
                "boi_land_property_details",
                "canara_land_property_details",
                "indian_land_property_details",
                "union_land_property_details"
            ]
            
            existing_collections = []
            for collection_name in potential_collections:
                try:
                    docs = await db.find_many("admin", collection_name, {})
                    if docs:
                        existing_collections.append(collection_name)
                        print(f"   ✅ {collection_name}: {len(docs)} documents")
                        
                        # Show sample document structure
                        if docs:
                            sample_doc = docs[0]
                            if "fields" in sample_doc:
                                print(f"      📋 Has {len(sample_doc['fields'])} fields")
                            if "templateMetadata" in sample_doc:
                                metadata = sample_doc["templateMetadata"]
                                print(f"      📝 Template: {metadata.get('templateName', 'Unknown')}")
                    else:
                        print(f"   ❌ {collection_name}: Not found or empty")
                except Exception as e:
                    print(f"   ❌ {collection_name}: Error - {e}")
            
            print(f"\n📈 Summary:")
            print(f"   Banks: {len(banks)}")
            print(f"   Common Field Documents: {len(common_fields_docs)} ({total_fields} total fields)")
            print(f"   Existing Template Collections: {len(existing_collections)}")
            
            if existing_collections:
                print(f"   Available Collections:")
                for col in existing_collections:
                    print(f"     - {col}")
            
            return {
                "banks": banks,
                "common_fields_docs": common_fields_docs,
                "existing_collections": existing_collections,
                "total_common_fields": total_fields
            }
            
    except Exception as e:
        print(f"❌ Error checking database structure: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(check_database_structure())
    if result:
        print(f"\n✅ Database structure check complete!")
    else:
        print(f"\n❌ Database structure check failed!")
        sys.exit(1)