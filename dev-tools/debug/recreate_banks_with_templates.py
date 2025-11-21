#!/usr/bin/env python3

"""
Recreate banks collection with proper template definitions
"""

import asyncio
import sys
import os
from datetime import datetime, timezone

# Set MongoDB URI
os.environ['MONGODB_URI'] = "mongodb+srv://app_user:kHxlQqJ1Uc3bmoL6@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster"

# Add backend path
sys.path.insert(0, '/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend')

from database.multi_db_manager import MultiDatabaseSession

async def recreate_banks_collection():
    """Recreate banks collection with proper template definitions and collection references"""
    try:
        print("🏦 Recreating banks collection with template definitions...")
        
        async with MultiDatabaseSession() as db:
            
            # Bank definitions with templates that have collection references
            banks_data = [
                {
                    "_id": "sbi",
                    "bankCode": "SBI",
                    "bankName": "State Bank of India",
                    "bankShortName": "SBI",
                    "bankType": "Public Sector",
                    "isActive": True,
                    "headquarters": {
                        "city": "Mumbai",
                        "state": "Maharashtra",
                        "pincode": "400001"
                    },
                    "templates": [
                        {
                            "templateId": "land-property",
                            "templateCode": "land-property",
                            "templateName": "SBI Land Property Valuation",
                            "templateType": "property_valuation",
                            "propertyType": "land",
                            "description": "Standard template for SBI land property valuation reports",
                            "version": "1.0",
                            "isActive": True,
                            "collectionRef": "sbi_land_property_details",
                            "fields": [
                                "property_location_details",
                                "property_description",
                                "property_measurement_details",
                                "property_boundaries",
                                "property_access_details",
                                "property_market_analysis",
                                "property_valuation_details",
                                "property_legal_verification"
                            ],
                            "validationRules": {
                                "required_fields": ["property_location_details", "property_description", "property_valuation_details"],
                                "minimum_documents": 3
                            },
                            "allowCustomFields": True,
                            "maxCustomFields": 10
                        }
                    ],
                    "totalBranches": 22405,
                    "createdAt": datetime.now(timezone.utc).isoformat(),
                    "updatedAt": datetime.now(timezone.utc).isoformat(),
                    "version": 1
                },
                {
                    "_id": "bob",
                    "bankCode": "BOB",
                    "bankName": "Bank of Baroda",
                    "bankShortName": "BOB",
                    "bankType": "Public Sector",
                    "isActive": True,
                    "headquarters": {
                        "city": "Vadodara",
                        "state": "Gujarat",
                        "pincode": "390007"
                    },
                    "templates": [
                        {
                            "templateId": "land-apartment",
                            "templateCode": "land-apartment",
                            "templateName": "BOB Land & Apartment Valuation",
                            "templateType": "property_valuation",
                            "propertyType": "land_apartment",
                            "description": "Standard template for BOB land and apartment property valuation reports",
                            "version": "1.0",
                            "isActive": True,
                            "collectionRef": "bob_land_property_details",
                            "fields": [
                                "property_identification",
                                "property_location_analysis",
                                "property_physical_characteristics",
                                "property_legal_status",
                                "property_marketability",
                                "property_comparable_analysis",
                                "property_valuation_approach",
                                "property_final_valuation"
                            ],
                            "validationRules": {
                                "required_fields": ["property_identification", "property_location_analysis", "property_final_valuation"],
                                "minimum_documents": 4
                            },
                            "allowCustomFields": True,
                            "maxCustomFields": 8
                        }
                    ],
                    "totalBranches": 9500,
                    "createdAt": datetime.now(timezone.utc).isoformat(),
                    "updatedAt": datetime.now(timezone.utc).isoformat(),
                    "version": 1
                },
                {
                    "_id": "ubi",
                    "bankCode": "UBI",
                    "bankName": "Union Bank of India",
                    "bankShortName": "UBI",
                    "bankType": "Public Sector",
                    "isActive": True,
                    "headquarters": {
                        "city": "Mumbai",
                        "state": "Maharashtra",
                        "pincode": "400013"
                    },
                    "templates": [
                        {
                            "templateId": "land-property",
                            "templateCode": "land-property",
                            "templateName": "UBI Land Property Valuation",
                            "templateType": "property_valuation",
                            "propertyType": "land",
                            "description": "Standard template for UBI land property valuation reports",
                            "version": "1.0",
                            "isActive": True,
                            "collectionRef": "ubi_land_property_details",
                            "fields": [
                                "property_basic_information",
                                "property_site_details",
                                "property_survey_details",
                                "property_development_potential",
                                "property_infrastructure_analysis",
                                "property_market_comparison",
                                "property_risk_assessment",
                                "property_value_determination"
                            ],
                            "validationRules": {
                                "required_fields": ["property_basic_information", "property_site_details", "property_value_determination"],
                                "minimum_documents": 3
                            },
                            "allowCustomFields": True,
                            "maxCustomFields": 5
                        }
                    ],
                    "totalBranches": 7500,
                    "createdAt": datetime.now(timezone.utc).isoformat(),
                    "updatedAt": datetime.now(timezone.utc).isoformat(),
                    "version": 1
                },
                {
                    "_id": "boi",
                    "bankCode": "BOI",
                    "bankName": "Bank of India",
                    "bankShortName": "BOI",
                    "bankType": "Public Sector",
                    "isActive": True,
                    "headquarters": {
                        "city": "Mumbai",
                        "state": "Maharashtra",
                        "pincode": "400001"
                    },
                    "templates": [
                        {
                            "templateId": "land-property",
                            "templateCode": "land-property",
                            "templateName": "BOI Land Property Valuation",
                            "templateType": "property_valuation",
                            "propertyType": "land",
                            "description": "Standard template for BOI land property valuation reports",
                            "version": "1.0",
                            "isActive": True,
                            "collectionRef": "boi_land_property_details",
                            "fields": [
                                "property_general_information",
                                "property_location_assessment",
                                "property_technical_specifications",
                                "property_ownership_verification",
                                "property_neighborhood_analysis",
                                "property_comparable_sales",
                                "property_valuation_methodology",
                                "property_conclusion_recommendation"
                            ],
                            "validationRules": {
                                "required_fields": ["property_general_information", "property_location_assessment", "property_conclusion_recommendation"],
                                "minimum_documents": 4
                            },
                            "allowCustomFields": True,
                            "maxCustomFields": 6
                        }
                    ],
                    "totalBranches": 5100,
                    "createdAt": datetime.now(timezone.utc).isoformat(),
                    "updatedAt": datetime.now(timezone.utc).isoformat(),
                    "version": 1
                }
            ]
            
            # Clear existing banks collection
            print("🗑️  Clearing existing banks collection...")
            existing_banks = await db.find_many("admin", "banks", {})
            for bank in existing_banks:
                await db.delete_one("admin", "banks", {"_id": bank["_id"]})
            
            # Insert new bank documents
            print("📥 Inserting bank documents with template definitions...")
            for bank_data in banks_data:
                await db.insert_one("admin", "banks", bank_data)
                print(f"   ✅ {bank_data['bankCode']}: {bank_data['bankName']}")
                print(f"      Templates: {len(bank_data['templates'])}")
                for template in bank_data['templates']:
                    print(f"        - {template['templateCode']}: {template['collectionRef']}")
            
            # Verify the insertion
            print("\n🔍 Verifying banks collection...")
            banks = await db.find_many("admin", "banks", {})
            print(f"✅ Successfully created {len(banks)} bank documents")
            
            # Create metadata document for banks collection
            metadata = {
                "_id": "banks_metadata",
                "collectionName": "banks",
                "description": "Bank definitions with template configurations and collection references",
                "totalBanks": len(banks_data),
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "version": "2.0",
                "schema": {
                    "bankCode": "Unique bank identifier code",
                    "bankName": "Full bank name",
                    "templates": "Array of template configurations with collection references",
                    "collectionRef": "Reference to bank-specific template collection using pattern {bankCode}_{templateCode}_property_details"
                }
            }
            
            await db.insert_one("admin", "banks", metadata)
            print(f"📋 Added metadata document")
            
            print(f"\n🎉 Banks collection recreation complete!")
            print(f"📊 Summary:")
            print(f"   - Total Banks: {len(banks_data)}")
            print(f"   - Template Collections Pattern: {{bankCode}}_{{templateCode}}_property_details")
            print(f"   - Available Endpoints:")
            print(f"     * GET /api/banks (list all banks)")
            print(f"     * GET /api/templates/{{bankCode}}/{{templateCode}}/aggregated-fields")
            
            return True
            
    except Exception as e:
        print(f"❌ Error recreating banks collection: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(recreate_banks_collection())
    if success:
        print(f"\n✅ Banks collection recreation successful!")
    else:
        print(f"\n❌ Banks collection recreation failed!")
        sys.exit(1)