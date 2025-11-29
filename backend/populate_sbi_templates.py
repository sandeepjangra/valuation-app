#!/usr/bin/env python3
"""
Populate template versioning system with SBI Land template data
Reads the actual SBI Land template data and creates versioned templates
"""

import asyncio
import os
import json
from pathlib import Path
from datetime import datetime, timezone

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    # If python-dotenv is not installed, try to read .env manually
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

from database.mongodb_manager import MongoDBManager

async def populate_sbi_land_templates():
    """Populate template versions with actual SBI Land template data"""
    
    db_manager = MongoDBManager()
    await db_manager.connect()
    
    try:
        if not db_manager.is_connected or db_manager.database is None:
            raise Exception("Failed to connect to database")
        
        db = db_manager.database
        
        print("🏗️ Populating SBI Land template data...")
        
        # Load the SBI Land template data
        template_data_path = Path(__file__).parent.parent / "dev-tools/data-samples/sbi_land_aggregated.json"
        
        if not template_data_path.exists():
            print("❌ SBI Land template data file not found")
            return
        
        with open(template_data_path) as f:
            sbi_data = json.load(f)
        
        template_info = sbi_data.get("templateInfo", {})
        common_fields = sbi_data.get("commonFields", [])
        bank_specific_fields = sbi_data.get("bankSpecificFields", [])
        
        print(f"📋 Template ID: {template_info.get('templateId')}")
        print(f"📋 Bank: {template_info.get('bankName')} ({template_info.get('bankCode')})")
        print(f"📋 Property Type: {template_info.get('propertyType')}")
        print(f"📋 Common Fields: {len(common_fields)}")
        print(f"📋 Bank-Specific Fields: {len(bank_specific_fields)}")
        
        # Create template version documents based on the logical structure
        templates_to_create = [
            {
                "templateId": "SBI_LAND_PROPERTY_DETAILS",
                "templateName": "SBI Land Property Details",
                "templateCategory": "property_details", 
                "uiName": "Property Details",
                "documentId": "PROPERTY_DETAILS_001",
                "documentName": "Property Details Document",
                "sections": [
                    {
                        "sectionId": "basic_info",
                        "sectionName": "Basic Information",
                        "displayOrder": 1,
                        "fields": common_fields
                    },
                    {
                        "sectionId": "property_location", 
                        "sectionName": "Property Location & Description",
                        "displayOrder": 2,
                        "fields": [f for f in bank_specific_fields if f.get("fieldId") in ["postal_address", "property_description", "property_location", "city_town_village", "area_type", "area_classification"]]
                    },
                    {
                        "sectionId": "site_details",
                        "sectionName": "Site Details & Boundaries", 
                        "displayOrder": 3,
                        "fields": [f for f in bank_specific_fields if f.get("fieldId") in ["boundaries", "dimensions", "longitude", "latitude", "site_area", "valuation_area", "occupied_by"]]
                    },
                    {
                        "sectionId": "locality_features",
                        "sectionName": "Locality & Environmental Features",
                        "displayOrder": 4, 
                        "fields": [f for f in bank_specific_fields if f.get("fieldId") in ["locality_classification", "surrounding_area", "flooding_possibility", "civic_amenities_feasibility", "land_level_topography", "land_shape"]]
                    },
                    {
                        "sectionId": "usage_planning",
                        "sectionName": "Usage & Town Planning",
                        "displayOrder": 5,
                        "fields": [f for f in bank_specific_fields if f.get("fieldId") in ["usage_type", "usage_restrictions", "town_planning_approved", "corner_or_intermittent"]]
                    },
                    {
                        "sectionId": "infrastructure",
                        "sectionName": "Infrastructure & Utilities",
                        "displayOrder": 6,
                        "fields": [f for f in bank_specific_fields if f.get("fieldId") in ["road_facilities", "road_type_present", "road_width", "landlocked_status", "water_potentiality", "underground_sewerage", "power_supply_available"]]
                    },
                    {
                        "sectionId": "additional_info",
                        "sectionName": "Additional Information", 
                        "displayOrder": 7,
                        "fields": [f for f in bank_specific_fields if f.get("fieldId") in ["site_advantages", "special_remarks", "municipal_corporation", "state_enactments", "agriculture_conversion"]]
                    }
                ]
            },
            {
                "templateId": "SBI_LAND_CONSTRUCTION_DETAILS",
                "templateName": "SBI Land Construction Details",
                "templateCategory": "construction_details",
                "uiName": "Construction Details",
                "documentId": "CONSTRUCTION_DETAILS_001", 
                "documentName": "Construction Details Document",
                "sections": [
                    {
                        "sectionId": "structural_details",
                        "sectionName": "Structural Components",
                        "displayOrder": 1,
                        "fields": [f for f in bank_specific_fields if f.get("fieldId") in ["foundation", "basement", "superstructure", "joinery_doors_windows", "rcc_works"]]
                    },
                    {
                        "sectionId": "finishing_details",
                        "sectionName": "Finishing & Special Features",
                        "displayOrder": 2,
                        "fields": [f for f in bank_specific_fields if f.get("fieldId") in ["plastering", "flooring_skirting_dadoing", "special_finish", "roofing_weatherproof", "drainage", "compound_wall"]]
                    },
                    {
                        "sectionId": "dimensions_construction",
                        "sectionName": "Dimensions & Construction Type",
                        "displayOrder": 3,
                        "fields": [f for f in bank_specific_fields if f.get("fieldId") in ["height", "length", "construction_type"]]
                    },
                    {
                        "sectionId": "electrical_plumbing",
                        "sectionName": "Electrical & Plumbing Installation",
                        "displayOrder": 4,
                        "fields": [f for f in bank_specific_fields if f.get("fieldId") in ["electrical_installation", "plumbing_installation"]]
                    }
                ]
            }
        ]
        
        # Insert template versions
        for template_def in templates_to_create:
            template_version = {
                "templateId": template_def["templateId"],
                "version": "1.0.0", 
                "bankCode": template_info.get("bankCode", "SBI"),
                "propertyType": template_info.get("propertyType", "Land"),
                "templateCategory": template_def["templateCategory"],
                "isActive": True,
                "isLatest": True,
                "createdAt": datetime.now(timezone.utc),
                "deprecatedAt": None,
                "templateDefinition": {
                    "templateId": template_def["templateId"],
                    "templateName": template_def["templateName"],
                    "uiName": template_def["uiName"],
                    "documentId": template_def["documentId"],
                    "documentName": template_def["documentName"],
                    "sections": template_def["sections"],
                    "metadata": {
                        "fieldCount": sum(len(section["fields"]) for section in template_def["sections"]),
                        "sectionCount": len(template_def["sections"]),
                        "hasCalculations": any("calculation" in str(field) for section in template_def["sections"] for field in section["fields"]),
                        "hasDynamicTables": any("dynamic_table" in str(field) for section in template_def["sections"] for field in section["fields"]),
                        "sourceTemplate": template_info.get("templateId"),
                        "migratedAt": datetime.now(timezone.utc).isoformat()
                    }
                },
                "versionChanges": {
                    "changeType": "initial_migration",
                    "description": f"Initial migration from legacy SBI Land template to versioned system",
                    "fieldsAdded": [],
                    "fieldsRemoved": [],
                    "fieldsModified": [],
                    "migrationRules": []
                }
            }
            
            # Insert or update template version
            result = await db.template_versions.update_one(
                {"templateId": template_def["templateId"], "version": "1.0.0"},
                {"$set": template_version},
                upsert=True
            )
            
            if result.upserted_id:
                print(f"  ✅ Created {template_def['templateId']} v1.0.0")
            else:
                print(f"  🔄 Updated {template_def['templateId']} v1.0.0")
        
        # Create a template snapshot for all SBI Land templates
        snapshot_data = {
            "templateIds": [t["templateId"] for t in templates_to_create],
            "version": "1.0.0",
            "contentHash": "",  # Will be calculated properly by TemplateSnapshotService
            "templateDefinitions": {
                template["templateId"]: template for template in templates_to_create
            },
            "createdAt": datetime.now(timezone.utc),
            "referencedByReports": []
        }
        
        # Calculate content hash (simple implementation)
        import hashlib
        content_str = json.dumps(snapshot_data["templateDefinitions"], sort_keys=True)
        snapshot_data["contentHash"] = hashlib.sha256(content_str.encode()).hexdigest()
        
        await db.template_snapshots.update_one(
            {"contentHash": snapshot_data["contentHash"]},
            {"$set": snapshot_data},
            upsert=True
        )
        
        print(f"  📸 Created template snapshot for SBI Land templates")
        
        # Display final statistics
        print("\\n📊 Template Versioning Statistics:")
        
        template_count = await db.template_versions.count_documents({})
        snapshot_count = await db.template_snapshots.count_documents({})
        
        print(f"  📋 Template Versions: {template_count}")
        print(f"  📸 Template Snapshots: {snapshot_count}")
        
        # Show created templates
        print("\\n🎯 Created Templates:")
        async for template in db.template_versions.find({"version": "1.0.0"}):
            fields_count = template["templateDefinition"]["metadata"]["fieldCount"]
            sections_count = template["templateDefinition"]["metadata"]["sectionCount"]
            print(f"  • {template['templateId']} - {sections_count} sections, {fields_count} fields")
        
        print("\\n✨ SBI Land template data populated successfully!")
        print("\\n🚀 Next Steps:")
        print("1. Test the TemplateSnapshotService with this data")
        print("2. Create version-aware report creation APIs")
        print("3. Build dynamic form renderer for SBI templates")
        print("4. Test full report lifecycle with versioning")
        
    except Exception as e:
        print(f"❌ Error populating SBI Land templates: {e}")
        raise
    
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(populate_sbi_land_templates())