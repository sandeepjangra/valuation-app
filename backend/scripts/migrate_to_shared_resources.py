#!/usr/bin/env python3
"""
Migration Script: Move Banks and Templates to shared_resources Database

This script:
1. Creates shared_resources database
2. Migrates banks from valuation_admin/banks to shared_resources/banks
3. Migrates bank templates to shared_resources/bank_templates
4. Migrates common_form_fields to shared_resources/common_fields
5. Keeps original data intact until verification
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
import os
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from database.multi_db_manager import MultiDatabaseManager
from datetime import datetime, timezone
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def migrate_to_shared_resources():
    """Main migration function"""
    
    logger.info("=" * 80)
    logger.info("MIGRATION: Moving Banks and Templates to shared_resources")
    logger.info("=" * 80)
    
    db_manager = MultiDatabaseManager()
    
    try:
        # Connect to databases
        logger.info("📡 Connecting to MongoDB...")
        await db_manager.connect()
        
        if not db_manager.is_connected:
            logger.error("❌ Failed to connect to MongoDB")
            return False
        
        logger.info("✅ Connected to MongoDB")
        
        # Get database references
        admin_db = db_manager.get_database("admin")
        shared_db = db_manager.get_database("shared")
        
        # Step 1: Migrate Banks
        logger.info("\n" + "=" * 80)
        logger.info("STEP 1: Migrating Banks")
        logger.info("=" * 80)
        
        banks_doc = await admin_db.banks.find_one({"_id": "all_banks_unified_v3"})
        
        if not banks_doc:
            logger.error("❌ Banks document not found in valuation_admin")
            return False
        
        logger.info(f"📦 Found unified banks document with {len(banks_doc.get('banks', []))} banks")
        
        # Extract banks array
        banks_array = banks_doc.get("banks", [])
        
        # Insert each bank as individual document in shared_resources
        migrated_count = 0
        for bank in banks_array:
            bank_code = bank.get("bankCode")
            
            # Check if bank already exists in shared_resources
            existing = await shared_db.banks.find_one({"bankCode": bank_code})
            
            if existing:
                logger.info(f"⏭️  Bank {bank_code} already exists in shared_resources, skipping")
                continue
            
            # Prepare bank document
            bank_doc = {
                **bank,
                "migratedAt": datetime.now(timezone.utc),
                "migrationSource": "valuation_admin.banks",
                "isActive": bank.get("isActive", True),
                "createdAt": bank.get("createdAt", datetime.now(timezone.utc)),
                "updatedAt": datetime.now(timezone.utc)
            }
            
            # Insert into shared_resources
            result = await shared_db.banks.insert_one(bank_doc)
            migrated_count += 1
            logger.info(f"✅ Migrated bank: {bank_code} (ID: {result.inserted_id})")
        
        logger.info(f"\n✅ Total banks migrated: {migrated_count}/{len(banks_array)}")
        
        # Step 2: Migrate Bank Templates (from each bank's templates array)
        logger.info("\n" + "=" * 80)
        logger.info("STEP 2: Migrating Bank Templates")
        logger.info("=" * 80)
        
        template_count = 0
        for bank in banks_array:
            bank_code = bank.get("bankCode")
            templates = bank.get("templates", [])
            
            if not templates:
                logger.info(f"⏭️  Bank {bank_code} has no templates, skipping")
                continue
            
            logger.info(f"📋 Processing {len(templates)} templates for bank {bank_code}")
            
            for template in templates:
                template_id = template.get("templateId")
                
                # Check if template already exists
                existing_template = await shared_db.bank_templates.find_one({
                    "bankCode": bank_code,
                    "templateId": template_id
                })
                
                if existing_template:
                    logger.info(f"  ⏭️  Template {template_id} for {bank_code} already exists, skipping")
                    continue
                
                # Prepare template document
                template_doc = {
                    "bankCode": bank_code,
                    "bankName": bank.get("bankName"),
                    **template,
                    "migratedAt": datetime.now(timezone.utc),
                    "migrationSource": f"valuation_admin.banks.{bank_code}.templates",
                    "isActive": template.get("isActive", True),
                    "createdAt": template.get("createdAt", datetime.now(timezone.utc)),
                    "updatedAt": datetime.now(timezone.utc)
                }
                
                # Insert into shared_resources
                result = await shared_db.bank_templates.insert_one(template_doc)
                template_count += 1
                logger.info(f"  ✅ Migrated template: {template_id} for {bank_code}")
        
        logger.info(f"\n✅ Total templates migrated: {template_count}")
        
        # Step 3: Migrate Common Fields
        logger.info("\n" + "=" * 80)
        logger.info("STEP 3: Migrating Common Fields")
        logger.info("=" * 80)
        
        # Check for common_form_fields collection in admin
        collections = await admin_db.list_collection_names()
        
        if "common_form_fields" in collections:
            common_fields = await admin_db.common_form_fields.find({}).to_list(None)
            
            if common_fields:
                logger.info(f"📦 Found {len(common_fields)} common field documents")
                
                fields_migrated = 0
                for field_doc in common_fields:
                    field_id = field_doc.get("_id")
                    
                    # Check if already exists
                    existing = await shared_db.common_fields.find_one({"_id": field_id})
                    
                    if existing:
                        logger.info(f"⏭️  Common field {field_id} already exists, skipping")
                        continue
                    
                    # Migrate to shared_resources
                    field_doc["migratedAt"] = datetime.now(timezone.utc)
                    field_doc["migrationSource"] = "valuation_admin.common_form_fields"
                    
                    await shared_db.common_fields.insert_one(field_doc)
                    fields_migrated += 1
                    logger.info(f"✅ Migrated common field: {field_id}")
                
                logger.info(f"\n✅ Total common fields migrated: {fields_migrated}/{len(common_fields)}")
            else:
                logger.info("ℹ️  No common fields found to migrate")
        else:
            logger.info("ℹ️  common_form_fields collection not found in valuation_admin")
        
        # Step 4: Verification
        logger.info("\n" + "=" * 80)
        logger.info("VERIFICATION")
        logger.info("=" * 80)
        
        # Count documents in shared_resources
        banks_count = await shared_db.banks.count_documents({})
        templates_count = await shared_db.bank_templates.count_documents({})
        fields_count = await shared_db.common_fields.count_documents({})
        
        logger.info(f"📊 shared_resources.banks: {banks_count} documents")
        logger.info(f"📊 shared_resources.bank_templates: {templates_count} documents")
        logger.info(f"📊 shared_resources.common_fields: {fields_count} documents")
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ MIGRATION COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info("\nℹ️  Original data in valuation_admin is preserved")
        logger.info("ℹ️  You can safely test with shared_resources now")
        logger.info("ℹ️  After verification, you can remove old data from valuation_admin")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await db_manager.disconnect()
        logger.info("\n🔒 Disconnected from MongoDB")


async def verify_migration():
    """Verify the migration by comparing data"""
    
    logger.info("\n" + "=" * 80)
    logger.info("VERIFICATION CHECK")
    logger.info("=" * 80)
    
    db_manager = MultiDatabaseManager()
    
    try:
        await db_manager.connect()
        
        admin_db = db_manager.get_database("admin")
        shared_db = db_manager.get_database("shared")
        
        # Compare banks
        admin_banks_doc = await admin_db.banks.find_one({"_id": "all_banks_unified_v3"})
        admin_banks_count = len(admin_banks_doc.get("banks", [])) if admin_banks_doc else 0
        shared_banks_count = await shared_db.banks.count_documents({})
        
        logger.info(f"\n📊 Banks Comparison:")
        logger.info(f"  valuation_admin: {admin_banks_count} banks (unified document)")
        logger.info(f"  shared_resources: {shared_banks_count} banks (individual documents)")
        
        if admin_banks_count == shared_banks_count:
            logger.info("  ✅ Bank counts match!")
        else:
            logger.warning(f"  ⚠️  Bank counts differ by {abs(admin_banks_count - shared_banks_count)}")
        
        # Sample a few banks
        logger.info(f"\n📋 Sample Banks in shared_resources:")
        sample_banks = await shared_db.banks.find({}).limit(5).to_list(5)
        for bank in sample_banks:
            logger.info(f"  - {bank.get('bankCode')}: {bank.get('bankName')}")
        
        # Sample templates
        logger.info(f"\n📋 Sample Templates in shared_resources:")
        sample_templates = await shared_db.bank_templates.find({}).limit(5).to_list(5)
        for template in sample_templates:
            logger.info(f"  - {template.get('bankCode')}/{template.get('templateId')}: {template.get('templateName')}")
        
        return True
        
    finally:
        await db_manager.disconnect()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate banks and templates to shared_resources")
    parser.add_argument("--verify", action="store_true", help="Only run verification check")
    args = parser.parse_args()
    
    if args.verify:
        success = asyncio.run(verify_migration())
    else:
        success = asyncio.run(migrate_to_shared_resources())
    
    sys.exit(0 if success else 1)
