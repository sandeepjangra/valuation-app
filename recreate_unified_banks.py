#!/usr/bin/env python3

"""
Check current banks collection and recreate the correct structure
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

async def check_and_recreate_banks():
    """Check current banks and recreate with correct structure"""
    try:
        print("🔍 Checking current banks collection...")
        
        async with MultiDatabaseSession() as db:
            
            # Check existing documents
            existing_docs = await db.find_many("admin", "banks", {})
            print(f"📊 Found {len(existing_docs)} documents in banks collection")
            
            for doc in existing_docs:
                doc_id = doc.get("_id")
                print(f"   📄 Document: {doc_id}")
                if "banks" in doc:
                    print(f"      🏦 Contains {len(doc['banks'])} banks")
                else:
                    print(f"      ⚠️  Individual bank: {doc.get('bankCode', 'Unknown')}")
            
            # Delete ALL existing documents
            for doc in existing_docs:
                await db.delete_one("admin", "banks", {"_id": doc["_id"]})
            print(f"🗑️  Deleted all existing documents")
            
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
            
            print(f"\n✅ Created correct unified banks document:")
            print(f"   📊 Total Banks: {total_banks}")
            print(f"   📄 Total Templates: {total_templates}")
            print(f"   🔗 Collection Pattern: {{bankCode}}_{{propertyType}}_property_details")
            
            # Show the structure
            print(f"\n📋 Banks Structure:")
            for bank in unified_banks_document["banks"]:
                bank_code = bank["bankCode"]
                templates = bank["templates"]
                print(f"   🏦 {bank_code} - {bank['bankName']}")
                for template in templates:
                    property_type = template["propertyType"]
                    collection_ref = template["collectionRef"]
                    print(f"      📄 {property_type} → {collection_ref}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(check_and_recreate_banks())
    if success:
        print(f"\n🎉 CORRECT unified banks structure created!")
        print(f"📡 API Endpoints:")
        print(f"   - GET /api/banks → returns banks array from ONE document") 
        print(f"   - GET /api/templates/{{bank}}/{{template}}/aggregated-fields")
        print(f"     → common_form_fields + {{bank}}_{{template}}_property_details")
    else:
        print(f"\n❌ Failed!")
        sys.exit(1)