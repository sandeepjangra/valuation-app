#!/usr/bin/env python3
"""
Update BOI Template Script
Uploads the updated BOI template data to MongoDB
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone
from bson import ObjectId

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from backend.database.multi_db_manager import MultiDatabaseSession

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def update_boi_template():
    """Update BOI template in MongoDB with our local changes"""
    
    # Read the updated BOI template file
    boi_file_path = Path(__file__).parent / "backend" / "data" / "boi" / "boi_land_property_details"
    
    if not boi_file_path.exists():
        logger.error(f"❌ BOI template file not found: {boi_file_path}")
        return False
    
    try:
        # Read the JSON data
        with open(boi_file_path, 'r', encoding='utf-8') as f:
            template_data = json.load(f)
        
        logger.info(f"📄 Loaded BOI template data from {boi_file_path}")
        logger.info(f"📊 Template contains {len(template_data.get('documents', []))} documents")
        
        # Connect to MongoDB and update
        async with MultiDatabaseSession() as db:
            # Find existing BOI template document
            existing_doc = await db.find_one(
                "admin", 
                "boi_land_property_details", 
                {"templateMetadata.bankCode": "BOI"}
            )
            
            if existing_doc:
                logger.info(f"✅ Found existing BOI template document with ID: {existing_doc['_id']}")
                
                # Update the existing document
                update_data = {
                    "templateMetadata": template_data["templateMetadata"],
                    "documents": template_data["documents"],
                    "updatedAt": datetime.now(timezone.utc),
                    "version": template_data.get("version", 1)
                }
                
                success = await db.update_one(
                    "admin",
                    "boi_land_property_details",
                    {"_id": existing_doc["_id"]},
                    update_data
                )
                
                if success:
                    logger.info(f"✅ Successfully updated BOI template in MongoDB")
                    return True
                else:
                    logger.error(f"❌ Failed to update BOI template in MongoDB")
                    return False
            
            else:
                logger.info("📝 No existing BOI template found, creating new document")
                
                # Create new document
                new_doc = template_data.copy()
                new_doc["createdAt"] = datetime.now(timezone.utc)
                new_doc["updatedAt"] = datetime.now(timezone.utc)
                
                doc_id = await db.insert_one("admin", "boi_land_property_details", new_doc)
                
                if doc_id:
                    logger.info(f"✅ Successfully created new BOI template in MongoDB with ID: {doc_id}")
                    return True
                else:
                    logger.error(f"❌ Failed to create BOI template in MongoDB")
                    return False
                    
    except Exception as e:
        logger.error(f"❌ Error updating BOI template: {e}")
        import traceback
        traceback.print_exc()
        return False

async def verify_update():
    """Verify the update was successful"""
    try:
        async with MultiDatabaseSession() as db:
            # Check the updated document
            doc = await db.find_one(
                "admin",
                "boi_land_property_details", 
                {"templateMetadata.bankCode": "BOI"}
            )
            
            if doc:
                logger.info(f"✅ Verification successful - BOI template found")
                logger.info(f"📊 Template version: {doc.get('version', 'N/A')}")
                logger.info(f"📅 Last updated: {doc.get('updatedAt', 'N/A')}")
                
                # Check for our specific changes in Group 3
                documents = doc.get("documents", [])
                construction_specs_doc = None
                
                for document in documents:
                    if document.get("templateId") == "BOI_LAND_CONSTRUCTION_SPECS_V1":
                        construction_specs_doc = document
                        break
                
                if construction_specs_doc:
                    sections = construction_specs_doc.get("sections", [])
                    group_3_section = None
                    
                    for section in sections:
                        if section.get("sectionId") == "group_3":
                            group_3_section = section
                            break
                    
                    if group_3_section:
                        fields = group_3_section.get("fields", [])
                        valuation_table = None
                        
                        for field in fields:
                            if field.get("fieldId") == "valuation_floor_wise_table":
                                valuation_table = field
                                break
                        
                        if valuation_table:
                            table_config = valuation_table.get("tableConfig", {})
                            logger.info(f"🎯 Found valuation table with config:")
                            logger.info(f"   - Table Type: {table_config.get('tableType', 'N/A')}")
                            logger.info(f"   - Allow Add Rows: {table_config.get('allowAddRows', False)}")
                            logger.info(f"   - Max Rows: {table_config.get('maxRows', 'N/A')}")
                            logger.info(f"   - Fixed Columns: {len(table_config.get('fixedColumns', []))}")
                            
                            if table_config.get("tableType") == "row_dynamic":
                                logger.info(f"✅ Our changes are successfully applied!")
                                return True
                            else:
                                logger.warning(f"⚠️ Changes not found - tableType is not 'row_dynamic'")
                                return False
                        else:
                            logger.warning(f"⚠️ valuation_floor_wise_table not found")
                            return False
                    else:
                        logger.warning(f"⚠️ group_3 section not found")
                        return False
                else:
                    logger.warning(f"⚠️ Construction specs document not found")
                    return False
            else:
                logger.error(f"❌ BOI template not found after update")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error verifying update: {e}")
        return False

async def main():
    """Main function"""
    logger.info("🚀 Starting BOI Template Update Script")
    
    # Update the template
    success = await update_boi_template()
    
    if success:
        logger.info("✅ Update completed successfully")
        
        # Verify the update
        logger.info("🔍 Verifying update...")
        verified = await verify_update()
        
        if verified:
            logger.info("🎉 BOI template update completed and verified!")
        else:
            logger.error("❌ Update verification failed")
    else:
        logger.error("❌ Update failed")

if __name__ == "__main__":
    asyncio.run(main())