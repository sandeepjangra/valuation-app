#!/usr/bin/env python3

"""
Populate common_form_fields and verify template collections structure
"""

import asyncio
import sys
import os
from datetime import datetime, timezone

# Set MongoDB URI
os.environ['MONGODB_URI'] = "mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster"

# Add backend path
sys.path.insert(0, '/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend')

from database.multi_db_manager import MultiDatabaseSession

async def populate_common_fields():
    """Populate common_form_fields collection with sample data"""
    try:
        print("📋 Populating common form fields...")
        
        async with MultiDatabaseSession() as db:
            
            # Clear existing common fields
            existing_docs = await db.find_many("admin", "common_form_fields", {})
            print(f"🗑️  Clearing {len(existing_docs)} existing common field documents...")
            
            for doc in existing_docs:
                await db.delete_one("admin", "common_form_fields", {"_id": doc["_id"]})
            
            # Sample common fields that would be used across all banks/templates
            common_fields_data = {
                "_id": "common_fields_basic",
                "collectionName": "common_form_fields",
                "description": "Basic common fields used across all bank templates",
                "isActive": True,
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "fields": [
                    {
                        "_id": "report_date",
                        "fieldId": "report_date",
                        "technicalName": "report_date",
                        "uiDisplayName": "Report Date",
                        "fieldType": "date",
                        "fieldGroup": "basic_info",
                        "isRequired": True,
                        "isReadonly": False,
                        "placeholder": "Select report date",
                        "helpText": "Date when the valuation report was prepared",
                        "validation": {
                            "required": True
                        },
                        "gridSize": 6,
                        "sortOrder": 1,
                        "isActive": True,
                        "defaultValue": "today"
                    },
                    {
                        "_id": "valuator_name",
                        "fieldId": "valuator_name", 
                        "technicalName": "valuator_name",
                        "uiDisplayName": "Valuator Name",
                        "fieldType": "text",
                        "fieldGroup": "basic_info",
                        "isRequired": True,
                        "isReadonly": False,
                        "placeholder": "Enter valuator name",
                        "helpText": "Name of the certified valuator",
                        "validation": {
                            "required": True,
                            "minLength": 2,
                            "maxLength": 100
                        },
                        "gridSize": 6,
                        "sortOrder": 2,
                        "isActive": True
                    },
                    {
                        "_id": "property_address",
                        "fieldId": "property_address",
                        "technicalName": "property_address", 
                        "uiDisplayName": "Property Address",
                        "fieldType": "textarea",
                        "fieldGroup": "property_basic",
                        "isRequired": True,
                        "isReadonly": False,
                        "placeholder": "Enter complete property address",
                        "helpText": "Complete address of the property being valued",
                        "validation": {
                            "required": True,
                            "minLength": 10,
                            "maxLength": 500
                        },
                        "gridSize": 12,
                        "sortOrder": 3,
                        "isActive": True
                    },
                    {
                        "_id": "property_type",
                        "fieldId": "property_type",
                        "technicalName": "property_type",
                        "uiDisplayName": "Property Type", 
                        "fieldType": "select",
                        "fieldGroup": "property_basic",
                        "isRequired": True,
                        "isReadonly": False,
                        "placeholder": "Select property type",
                        "helpText": "Type of property being valued",
                        "validation": {
                            "required": True
                        },
                        "gridSize": 6,
                        "sortOrder": 4,
                        "isActive": True,
                        "options": [
                            {"value": "land", "label": "Land/Plot"},
                            {"value": "apartment", "label": "Apartment/Flat"},
                            {"value": "independent_house", "label": "Independent House"},
                            {"value": "commercial", "label": "Commercial Property"}
                        ]
                    },
                    {
                        "_id": "loan_amount",
                        "fieldId": "loan_amount",
                        "technicalName": "loan_amount", 
                        "uiDisplayName": "Loan Amount",
                        "fieldType": "currency",
                        "fieldGroup": "financial_info",
                        "isRequired": True,
                        "isReadonly": False,
                        "placeholder": "Enter loan amount",
                        "helpText": "Requested loan amount",
                        "validation": {
                            "required": True,
                            "min": 100000,
                            "max": 100000000
                        },
                        "gridSize": 6,
                        "sortOrder": 5,
                        "isActive": True,
                        "prefix": "₹"
                    }
                ]
            }
            
            await db.insert_one("admin", "common_form_fields", common_fields_data)
            print(f"✅ Inserted {len(common_fields_data['fields'])} common fields")
            
            # Verify insertion
            common_fields_docs = await db.find_many("admin", "common_form_fields", {"isActive": True})
            total_fields = sum(len(doc.get("fields", [])) for doc in common_fields_docs)
            
            print(f"📊 Total common fields available: {total_fields}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error populating common fields: {e}")
        import traceback
        traceback.print_exc()
        return False

async def check_template_collection_structure():
    """Check the structure of template collections to understand the data format"""
    try:
        print("\n🔍 Checking template collection structures...")
        
        async with MultiDatabaseSession() as db:
            
            collections = ["bob_land_property_details", "sbi_land_property_details"]
            
            for collection_name in collections:
                print(f"\n📄 Analyzing {collection_name}:")
                
                docs = await db.find_many("admin", collection_name, {})
                print(f"   Documents: {len(docs)}")
                
                if docs:
                    sample_doc = docs[0]
                    print(f"   Sample document structure:")
                    
                    if "templateMetadata" in sample_doc:
                        metadata = sample_doc["templateMetadata"]
                        print(f"     templateMetadata: {metadata.get('templateName', 'Unknown')}")
                        
                        if "tabs" in metadata:
                            print(f"     tabs: {len(metadata['tabs'])}")
                            for tab in metadata["tabs"][:2]:  # Show first 2 tabs
                                tab_id = tab.get("tabId", "unknown")
                                has_sections = tab.get("hasSections", False)
                                print(f"       - {tab_id} (hasSections: {has_sections})")
                    
                    if "fields" in sample_doc:
                        print(f"     fields: {len(sample_doc['fields'])}")
                    
                    if "sections" in sample_doc:
                        print(f"     sections: {len(sample_doc['sections'])}")
                        for section in sample_doc["sections"][:2]:  # Show first 2 sections
                            section_id = section.get("sectionId", "unknown")
                            fields_count = len(section.get("fields", []))
                            print(f"       - {section_id}: {fields_count} fields")
            
            return True
            
    except Exception as e:
        print(f"❌ Error checking template collections: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Setting up complete data structure for multi-collection aggregation...")
    
    success1 = asyncio.run(populate_common_fields())
    success2 = asyncio.run(check_template_collection_structure())
    
    if success1 and success2:
        print(f"\n✅ Setup complete! Ready to test aggregation API")
        print(f"🔗 Test endpoints:")
        print(f"   - GET http://localhost:8000/api/banks")
        print(f"   - GET http://localhost:8000/api/templates/BOB/land-apartment/aggregated-fields")
        print(f"   - GET http://localhost:8000/api/templates/SBI/land-property/aggregated-fields")
    else:
        print(f"\n❌ Setup failed!")
        sys.exit(1)