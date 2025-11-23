#!/usr/bin/env python3

"""
Properly recreate unified banks structure using upsert
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

async def create_unified_banks_properly():
    """Properly create unified banks using replace/upsert"""
    try:
        print("🏦 Creating unified banks structure properly...")
        
        async with MultiDatabaseSession() as db:
            
            # First, completely drop and recreate banks collection
            try:
                db_instance = db.client[db.db_configs["admin"]["database"]]
                await db_instance.drop_collection("banks")
                print("🗑️  Dropped entire banks collection")
            except Exception as e:
                print(f"⚠️  Collection drop info: {e}")
            
            # Create ONE unified banks document  
            unified_banks_document = {
                "_id": "all_banks_unified",
                "collectionName": "banks",
                "description": "Unified document containing all banks with template collection references",
                "version": "2.0", 
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "updatedAt": datetime.now(timezone.utc).isoformat(),
                "banks": [
                    {
                        "bankId": "sbi",
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
                        "totalBranches": 22405,
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
                                "collectionRef": "sbi_land_property_details"
                            },
                            {
                                "templateId": "apartment-property",
                                "templateCode": "apartment-property",
                                "templateName": "SBI Apartment Property Valuation", 
                                "templateType": "property_valuation",
                                "propertyType": "apartment",
                                "description": "Standard template for SBI apartment property valuation reports",
                                "version": "1.0",
                                "isActive": True,
                                "collectionRef": "sbi_apartment_property_details"
                            }
                        ]
                    },
                    {
                        "bankId": "bob",
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
                        "totalBranches": 9500,
                        "templates": [
                            {
                                "templateId": "land-property",
                                "templateCode": "land-property",
                                "templateName": "BOB Land Property Valuation",
                                "templateType": "property_valuation", 
                                "propertyType": "land",
                                "description": "Standard template for BOB land property valuation reports",
                                "version": "1.0",
                                "isActive": True,
                                "collectionRef": "bob_land_property_details"
                            },
                            {
                                "templateId": "apartment-property", 
                                "templateCode": "apartment-property",
                                "templateName": "BOB Apartment Property Valuation",
                                "templateType": "property_valuation",
                                "propertyType": "apartment", 
                                "description": "Standard template for BOB apartment property valuation reports",
                                "version": "1.0",
                                "isActive": True,
                                "collectionRef": "bob_apartment_property_details"
                            }
                        ]
                    },
                    {
                        "bankId": "ubi",
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
                        "totalBranches": 7500,
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
                                "collectionRef": "ubi_land_property_details"
                            },
                            {
                                "templateId": "apartment-property",
                                "templateCode": "apartment-property",
                                "templateName": "UBI Apartment Property Valuation",
                                "templateType": "property_valuation", 
                                "propertyType": "apartment",
                                "description": "Standard template for UBI apartment property valuation reports",
                                "version": "1.0",
                                "isActive": True,
                                "collectionRef": "ubi_apartment_property_details"
                            }
                        ]
                    },
                    {
                        "bankId": "boi",
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
                        "totalBranches": 5100,
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
                                "collectionRef": "boi_land_property_details"
                            },
                            {
                                "templateId": "apartment-property",
                                "templateCode": "apartment-property", 
                                "templateName": "BOI Apartment Property Valuation",
                                "templateType": "property_valuation",
                                "propertyType": "apartment",
                                "description": "Standard template for BOI apartment property valuation reports",
                                "version": "1.0", 
                                "isActive": True,
                                "collectionRef": "boi_apartment_property_details"
                            }
                        ]
                    }
                ]
            }
            
            # Insert the unified document
            await db.insert_one("admin", "banks", unified_banks_document)
            
            total_banks = len(unified_banks_document["banks"])
            total_templates = sum(len(bank["templates"]) for bank in unified_banks_document["banks"])
            
            print(f"\n✅ Created unified banks document:")
            print(f"   📊 Total Banks: {total_banks}")
            print(f"   📄 Total Templates: {total_templates}")
            print(f"   🔗 Collection Pattern: {{bankCode}}_{{propertyType}}_property_details")
            
            # Verify the document was created
            doc = await db.find_one("admin", "banks", {"_id": "all_banks_unified"})
            if doc and "banks" in doc:
                print(f"\n✅ Verification: Found unified document with {len(doc['banks'])} banks")
                
                # Show the structure
                print(f"\n📋 Banks and Templates:")
                for bank in doc["banks"]:
                    bank_code = bank["bankCode"]
                    templates = bank["templates"]
                    print(f"   🏦 {bank_code} - {bank['bankName']}")
                    for template in templates:
                        property_type = template["propertyType"]
                        collection_ref = template["collectionRef"]
                        print(f"      📄 {property_type} → {collection_ref}")
            else:
                print(f"\n❌ Verification failed: Document not found properly")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(create_unified_banks_properly())
    if success:
        print(f"\n🎉 SUCCESS: Unified banks structure created properly!")
        print(f"\n📡 API Structure:")
        print(f"   - GET /api/banks → returns 'banks' array from ONE unified document") 
        print(f"   - GET /api/templates/SBI/land-property/aggregated-fields")
        print(f"     → common_form_fields + sbi_land_property_details")
        print(f"   - GET /api/templates/BOB/apartment-property/aggregated-fields")
        print(f"     → common_form_fields + bob_apartment_property_details")
    else:
        print(f"\n❌ FAILED to create structure!")
        sys.exit(1)