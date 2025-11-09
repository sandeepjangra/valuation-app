#!/usr/bin/env python3
"""
Bank Collection Consolidation Migration Script

This script consolidates 8 separate bank documents into a unified structure
to simplify backend aggregation and improve maintainability.
"""

import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any
from pymongo import MongoClient
from bson import ObjectId

# MongoDB connection configuration
MONGO_URI = "mongodb+srv://sandeepjangra:sandeep123@valuation.5ksdt.mongodb.net/"
DATABASE_NAME = "valuation_system"

class BankConsolidationMigrator:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DATABASE_NAME]
        self.migration_log = []
        
    def log(self, message: str):
        """Log migration progress"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        self.migration_log.append(log_entry)
    
    async def analyze_current_structure(self):
        """Analyze current bank documents and collections"""
        self.log("🔍 Analyzing current bank structure...")
        
        # Get all banks
        banks_collection = self.db["banks"]
        banks = list(banks_collection.find())
        
        self.log(f"Found {len(banks)} bank documents")
        
        analysis = {
            "banks": {},
            "collections": {},
            "total_fields": 0
        }
        
        for bank in banks:
            bank_name = bank.get("bankName", "Unknown")
            bank_code = bank.get("bankCode", bank_name.upper()[:3])
            
            self.log(f"  📋 Analyzing {bank_name} ({bank_code})")
            
            templates = bank.get("templates", [])
            bank_analysis = {
                "templates": len(templates),
                "collections_used": [],
                "field_count": 0
            }
            
            # Analyze each template
            for template in templates:
                # Get collection references
                fields = template.get("fields", {})
                
                # Check bank specific fields
                bank_specific = fields.get("bankSpecificFields", {})
                collection_ref = bank_specific.get("collectionRef")
                
                if collection_ref:
                    bank_analysis["collections_used"].append(collection_ref)
                    
                    # Count fields in collection
                    if collection_ref not in analysis["collections"]:
                        collection = self.db[collection_ref]
                        field_count = collection.count_documents({})
                        analysis["collections"][collection_ref] = field_count
                        bank_analysis["field_count"] += field_count
                        analysis["total_fields"] += field_count
            
            analysis["banks"][bank_code] = bank_analysis
        
        return analysis
    
    async def create_unified_bank_templates(self, analysis: Dict):
        """Create unified bank templates collection"""
        self.log("🏗️ Creating unified_bank_templates collection...")
        
        # Drop existing unified collection if exists
        if "unified_bank_templates" in self.db.list_collection_names():
            self.db["unified_bank_templates"].drop()
            self.log("  🗑️ Dropped existing unified_bank_templates collection")
        
        unified_collection = self.db["unified_bank_templates"]
        
        # Get all banks to process
        banks_collection = self.db["banks"]
        banks = list(banks_collection.find())
        
        migrated_count = 0
        
        for bank in banks:
            bank_code = bank.get("bankCode", bank.get("bankName", "").upper()[:3])
            bank_name = bank.get("bankName", "Unknown")
            
            self.log(f"  🏦 Processing {bank_name} ({bank_code})")
            
            templates = bank.get("templates", [])
            
            for template in templates:
                template_id = template.get("templateId", f"{bank_code}_UNKNOWN")
                property_type = template.get("propertyType", "unknown")
                
                # Get bank-specific fields
                fields = template.get("fields", {})
                bank_specific = fields.get("bankSpecificFields", {})
                collection_ref = bank_specific.get("collectionRef")
                
                if collection_ref and collection_ref in analysis["collections"]:
                    # Migrate all fields from the original collection
                    source_collection = self.db[collection_ref]
                    source_fields = list(source_collection.find())
                    
                    # Add bank and property type metadata to each field
                    for field in source_fields:
                        # Remove old _id and create new document
                        field.pop("_id", None)
                        
                        unified_doc = {
                            "bankCode": bank_code,
                            "bankName": bank_name,
                            "propertyType": property_type,
                            "templateId": template_id,
                            "version": "3.0",
                            "isActive": True,
                            "migratedFrom": collection_ref,
                            "migratedAt": datetime.utcnow(),
                            **field  # Include all original field data
                        }
                        
                        unified_collection.insert_one(unified_doc)
                        migrated_count += 1
        
        self.log(f"  ✅ Migrated {migrated_count} template documents")
        return migrated_count
    
    async def create_unified_banks_document(self):
        """Create single unified banks document"""
        self.log("🏗️ Creating unified_banks document...")
        
        # Get all existing banks
        banks_collection = self.db["banks"]
        existing_banks = list(banks_collection.find())
        
        # Build unified structure
        unified_banks = {
            "_id": "unified_banks_v3",
            "version": "3.0",
            "architecture": "unified_reference_based",
            "createdAt": datetime.utcnow(),
            "lastUpdated": datetime.utcnow(),
            "migrationInfo": {
                "migratedFrom": "separate_bank_documents",
                "originalBankCount": len(existing_banks),
                "migrationDate": datetime.utcnow()
            },
            "banks": []
        }
        
        for bank in existing_banks:
            bank_code = bank.get("bankCode", bank.get("bankName", "").upper()[:3])
            
            # Update template references to use unified collections
            templates = bank.get("templates", [])
            updated_templates = []
            
            for template in templates:
                updated_template = {
                    **template,  # Keep all existing data
                    "version": "3.0",
                    "fields": {
                        "commonFields": {
                            "collectionRef": "common_form_fields"
                        },
                        "bankSpecificFields": {
                            "collectionRef": "unified_bank_templates",
                            "filter": {
                                "bankCode": bank_code,
                                "propertyType": template.get("propertyType", "land"),
                                "isActive": True
                            }
                        }
                    }
                }
                updated_templates.append(updated_template)
            
            # Create unified bank entry
            unified_bank = {
                **bank,  # Keep all existing bank data
                "bankCode": bank_code,
                "templates": updated_templates,
                "architecture": "unified_reference_based",
                "lastUpdated": datetime.utcnow()
            }
            
            # Remove old _id
            unified_bank.pop("_id", None)
            
            unified_banks["banks"].append(unified_bank)
        
        # Insert unified document
        unified_collection = self.db["unified_banks"]
        
        # Drop existing if present
        if "unified_banks" in self.db.list_collection_names():
            unified_collection.drop()
            self.log("  🗑️ Dropped existing unified_banks collection")
        
        unified_collection.insert_one(unified_banks)
        self.log(f"  ✅ Created unified_banks document with {len(unified_banks['banks'])} banks")
        
        return unified_banks
    
    async def validate_migration(self, analysis: Dict):
        """Validate migration was successful"""
        self.log("🔍 Validating migration...")
        
        # Check unified collections exist
        collections = self.db.list_collection_names()
        
        validation = {
            "unified_banks_exists": "unified_banks" in collections,
            "unified_templates_exists": "unified_bank_templates" in collections,
            "field_count_match": False,
            "bank_count_match": False
        }
        
        if validation["unified_templates_exists"]:
            unified_count = self.db["unified_bank_templates"].count_documents({})
            original_count = analysis["total_fields"]
            validation["field_count_match"] = unified_count >= original_count
            self.log(f"  📊 Field count: {unified_count} unified vs {original_count} original")
        
        if validation["unified_banks_exists"]:
            unified_doc = self.db["unified_banks"].find_one({"_id": "unified_banks_v3"})
            if unified_doc:
                unified_bank_count = len(unified_doc.get("banks", []))
                original_bank_count = len(analysis["banks"])
                validation["bank_count_match"] = unified_bank_count == original_bank_count
                self.log(f"  🏦 Bank count: {unified_bank_count} unified vs {original_bank_count} original")
        
        all_valid = all(validation.values())
        self.log(f"  {'✅' if all_valid else '❌'} Migration validation: {'PASSED' if all_valid else 'FAILED'}")
        
        return validation
    
    async def backup_original_collections(self):
        """Backup original collections before migration"""
        self.log("💾 Creating backup of original collections...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Get all collections to backup
        collections_to_backup = [
            "banks",
            "bob_land_property_details",
            "bob_apartment_property_details", 
            "sbi_land_property_details",
            "sbi_apartment_property_details",
            "boi_land_property_details",
            "boi_apartment_property_details",
            "hdfc_all_property_details",
            "pnb_all_property_details",
            "cbi_all_property_details",
            "uco_all_property_details",
            "ubi_land_property_details",
            "ubi_apartment_property_details"
        ]
        
        existing_collections = self.db.list_collection_names()
        
        for collection_name in collections_to_backup:
            if collection_name in existing_collections:
                backup_name = f"{collection_name}_backup_{timestamp}"
                
                # Copy collection
                original = self.db[collection_name]
                backup = self.db[backup_name]
                
                documents = list(original.find())
                if documents:
                    backup.insert_many(documents)
                    self.log(f"  📋 Backed up {collection_name} ({len(documents)} docs) → {backup_name}")
    
    async def run_migration(self):
        """Run complete migration process"""
        self.log("🚀 Starting Bank Collection Consolidation Migration")
        
        try:
            # Step 1: Analyze current structure
            analysis = await self.analyze_current_structure()
            
            # Step 2: Create backup
            await self.backup_original_collections()
            
            # Step 3: Create unified collections
            template_count = await self.create_unified_bank_templates(analysis)
            unified_banks = await self.create_unified_banks_document()
            
            # Step 4: Validate migration
            validation = await self.validate_migration(analysis)
            
            # Step 5: Generate summary
            self.log("📋 Migration Summary:")
            self.log(f"  • Analyzed {len(analysis['banks'])} banks")
            self.log(f"  • Migrated {analysis['total_fields']} fields to unified structure")
            self.log(f"  • Created unified_banks document with {len(unified_banks['banks'])} banks")
            self.log(f"  • Validation: {'PASSED' if all(validation.values()) else 'FAILED'}")
            
            if all(validation.values()):
                self.log("✅ Migration completed successfully!")
            else:
                self.log("❌ Migration completed with validation issues")
                
            return {
                "success": all(validation.values()),
                "analysis": analysis,
                "validation": validation,
                "log": self.migration_log
            }
            
        except Exception as e:
            self.log(f"❌ Migration failed: {str(e)}")
            raise
        
        finally:
            self.client.close()

async def main():
    """Main migration execution"""
    migrator = BankConsolidationMigrator()
    
    # Ask for confirmation
    print("🚨 This will consolidate 8 separate bank collections into unified structure")
    print("📋 Original collections will be backed up with timestamp")
    
    confirm = input("Continue with migration? (y/N): ").lower().strip()
    
    if confirm != 'y':
        print("❌ Migration cancelled")
        return
    
    result = await migrator.run_migration()
    
    # Save migration log
    with open("consolidation_migration_log.json", "w") as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\n📄 Migration log saved to: consolidation_migration_log.json")

if __name__ == "__main__":
    asyncio.run(main())