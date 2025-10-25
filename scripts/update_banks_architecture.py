#!/usr/bin/env python3
"""
Update banks collection to use clean reference-based template architecture
Converts existing field arrays to collectionRef structure with MongoDB lookup capability
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from bson import ObjectId

# Add parent directory to path to import backend modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

class BanksCollectionUpdater:
    """Update banks collection with clean reference-based architecture"""
    
    def __init__(self):
        self.connection_string = os.getenv("MONGODB_URI")
        self.admin_db_name = os.getenv("MONGODB_ADMIN_DB_NAME", "valuation_admin")
        
        if not self.connection_string:
            raise ValueError("MONGODB_URI environment variable is required")
        
        self.client = None
        self.db = None
        
    async def connect(self):
        """Connect to MongoDB Atlas"""
        try:
            print("🔗 Connecting to MongoDB Atlas...")
            
            self.client = AsyncIOMotorClient(
                self.connection_string,
                serverSelectionTimeoutMS=30000,
                connectTimeoutMS=30000,
                socketTimeoutMS=30000,
                maxPoolSize=10,
                retryWrites=True,
                retryReads=True,
                tlsAllowInvalidCertificates=True
            )
            
            await asyncio.wait_for(self.client.admin.command('ping'), timeout=15.0)
            self.db = self.client[self.admin_db_name]
            
            print("✅ Connected to MongoDB Atlas successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def create_new_template_structure(self, bank_code, template_code, property_type, template_name, description):
        """Create new template structure with collection references"""
        
        # Define collection mappings for each bank
        collection_mappings = {
            "SBI": {
                "land": "sbi_land_property_details",
                "apartment": "sbi_apartment_property_details"
            },
            "UBI": {
                "land": "ubi_land_property_details",
                "all": "ubi_land_property_details"  # UBI only has land for now
            },
            "PNB": {
                "all": "pnb_all_property_details"
            },
            "HDFC": {
                "all": "hdfc_all_property_details"
            },
            "UCO": {
                "all": "uco_all_property_details"
            },
            "CBI": {
                "all": "cbi_all_property_details"
            }
        }
        
        # Get the collection reference for this bank and property type
        bank_collections = collection_mappings.get(bank_code, {})
        collection_ref = bank_collections.get(property_type) or bank_collections.get("all")
        
        if not collection_ref:
            print(f"⚠️  No collection mapping found for {bank_code} - {property_type}")
            return None
        
        # Create new template structure
        new_template = {
            "templateId": f"{bank_code}_{property_type.upper()}_REF_001",
            "templateCode": template_code,
            "templateName": template_name,
            "templateType": "property_valuation",
            "propertyType": property_type,
            "description": description,
            "version": "2.0",  # New version for reference-based architecture
            "isActive": True,
            "fields": {
                "commonFields": {
                    "collectionRef": "common_form_fields",
                    "filter": {
                        "isActive": True,
                        "applicableFor": "all"
                    }
                },
                "bankSpecificFields": {
                    "collectionRef": collection_ref,
                    "filter": {
                        "isActive": True
                    }
                }
            },
            "aggregationPipeline": [
                {
                    "$lookup": {
                        "from": "common_form_fields",
                        "pipeline": [
                            {"$match": {"isActive": True, "applicableFor": "all"}}
                        ],
                        "as": "commonFields"
                    }
                },
                {
                    "$lookup": {
                        "from": collection_ref,
                        "pipeline": [
                            {"$match": {"isActive": True}}
                        ],
                        "as": "bankSpecificTabs"
                    }
                }
            ],
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "updatedAt": datetime.now(timezone.utc).isoformat()
        }
        
        return new_template
    
    async def update_bank_templates(self, bank_code):
        """Update templates for a specific bank"""
        try:
            banks_collection = self.db["banks"]
            
            # Find the bank document
            bank_doc = await banks_collection.find_one({"bankCode": bank_code})
            if not bank_doc:
                print(f"⚠️  Bank {bank_code} not found")
                return False
            
            print(f"📝 Updating templates for {bank_code}...")
            
            # Create new templates based on bank type
            new_templates = []
            
            if bank_code == "SBI":
                # SBI has separate land and apartment templates
                land_template = self.create_new_template_structure(
                    "SBI", "land", "land", 
                    "SBI Land Property Valuation",
                    "Template for land property valuation with common and SBI-specific fields"
                )
                apartment_template = self.create_new_template_structure(
                    "SBI", "apartment", "apartment",
                    "SBI Apartment Property Valuation", 
                    "Template for apartment property valuation with common and SBI-specific fields"
                )
                if land_template:
                    new_templates.append(land_template)
                if apartment_template:
                    new_templates.append(apartment_template)
                    
            elif bank_code == "UBI":
                # UBI has land template
                land_template = self.create_new_template_structure(
                    "UBI", "land", "land",
                    "UBI Land Property Valuation",
                    "Template for land property valuation with common and UBI-specific fields"
                )
                if land_template:
                    new_templates.append(land_template)
                    
            else:
                # PNB, HDFC, UCO, CBI have unified templates
                unified_template = self.create_new_template_structure(
                    bank_code, "all", "all",
                    f"{bank_code} Property Valuation",
                    f"Unified template for all property types with common and {bank_code}-specific fields"
                )
                if unified_template:
                    new_templates.append(unified_template)
            
            if not new_templates:
                print(f"❌ No templates created for {bank_code}")
                return False
            
            # Update the bank document with new templates
            update_result = await banks_collection.update_one(
                {"bankCode": bank_code},
                {
                    "$set": {
                        "templates": new_templates,
                        "templatesLastUpdated": datetime.now(timezone.utc).isoformat(),
                        "templatesVersion": "2.0",
                        "architecture": "reference_based",
                        "updatedAt": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            if update_result.modified_count > 0:
                print(f"✅ Updated {bank_code} with {len(new_templates)} reference-based templates")
                return True
            else:
                print(f"❌ Failed to update {bank_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error updating {bank_code}: {e}")
            return False
    
    async def update_all_banks(self):
        """Update all banks with new reference-based architecture"""
        # Only update banks that exist in the collection
        banks_to_update = ["SBI", "PNB", "HDFC", "UCO", "CBI"]
        
        success_count = 0
        total_count = len(banks_to_update)
        
        for bank_code in banks_to_update:
            success = await self.update_bank_templates(bank_code)
            if success:
                success_count += 1
        
        print(f"\n🎉 Successfully updated {success_count}/{total_count} banks!")
        return success_count == total_count
    
    async def verify_updates(self):
        """Verify that banks were updated correctly"""
        try:
            print("\n🔍 Verifying bank template updates...")
            
            banks_collection = self.db["banks"]
            updated_banks = await banks_collection.find(
                {"architecture": "reference_based"}
            ).to_list(length=None)
            
            print(f"📊 Found {len(updated_banks)} banks with reference-based architecture:")
            
            for bank in updated_banks:
                bank_code = bank.get("bankCode")
                templates = bank.get("templates", [])
                print(f"   • {bank_code}: {len(templates)} templates")
                
                for template in templates:
                    template_code = template.get("templateCode")
                    property_type = template.get("propertyType")
                    common_ref = template.get("fields", {}).get("commonFields", {}).get("collectionRef")
                    bank_ref = template.get("fields", {}).get("bankSpecificFields", {}).get("collectionRef")
                    print(f"     - {template_code} ({property_type})")
                    print(f"       Common: {common_ref}")
                    print(f"       Bank-specific: {bank_ref}")
            
            return True
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("🔌 Disconnected from MongoDB Atlas")

async def main():
    """Main function to update banks collection"""
    updater = BanksCollectionUpdater()
    
    try:
        # Connect to MongoDB
        if not await updater.connect():
            sys.exit(1)
        
        # Update all banks
        success = await updater.update_all_banks()
        
        if success:
            # Verify updates
            await updater.verify_updates()
            print("\n✅ Banks collection successfully updated to reference-based architecture!")
            print("\nNew Architecture Benefits:")
            print("• Single API calls using MongoDB $lookup aggregation")
            print("• Clean separation between common and bank-specific fields")
            print("• No data duplication between collections")
            print("• Flexible filtering and tabbed UI organization")
        else:
            print("\n❌ Some banks failed to update")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Script failed: {e}")
        sys.exit(1)
    finally:
        await updater.close()

if __name__ == "__main__":
    asyncio.run(main())