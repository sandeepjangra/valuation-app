#!/usr/bin/env python3
"""
Template Versioning Database Setup
Creates the collections and indexes needed for template versioning system
"""

import asyncio
import logging
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING, TEXT
import os
from pathlib import Path
import sys

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = backend_dir / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    # If python-dotenv is not installed, try to read .env manually
    env_path = backend_dir / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

from database.mongodb_manager import MongoDBManager

logger = logging.getLogger(__name__)

async def create_template_versioning_collections():
    """Create all collections needed for template versioning"""
    
    try:
        # Initialize database manager
        db_manager = MongoDBManager()
        await db_manager.connect()
        
        if not db_manager.is_connected or db_manager.database is None:
            raise Exception("Failed to connect to database")
        
        db = db_manager.database
        
        # 1. Template Versions Collection
        print("Creating template_versions collection...")
        
        # Drop existing collection if it exists (for clean setup)
        await db.template_versions.drop()
        
        # Create collection with schema validation
        await db.create_collection("template_versions", validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["templateId", "version", "bankCode", "propertyType", "templateDefinition"],
                "properties": {
                    "templateId": {
                        "bsonType": "string",
                        "description": "Base template identifier like SBI_LAND_PROPERTY_DETAILS"
                    },
                    "version": {
                        "bsonType": "string", 
                        "pattern": "^\\d+\\.\\d+\\.\\d+$",
                        "description": "Semantic version like 1.0.0"
                    },
                    "bankCode": {
                        "bsonType": "string",
                        "description": "Bank identifier like SBI, UBI, ICICI"
                    },
                    "propertyType": {
                        "bsonType": "string",
                        "description": "Property type like Land, Apartment"
                    },
                    "templateCategory": {
                        "bsonType": "string",
                        "description": "Category like property_details, valuation"
                    },
                    "isActive": {
                        "bsonType": "bool",
                        "description": "Whether this version is active"
                    },
                    "isLatest": {
                        "bsonType": "bool", 
                        "description": "Whether this is the latest version"
                    },
                    "templateDefinition": {
                        "bsonType": "object",
                        "description": "Complete template structure"
                    },
                    "versionChanges": {
                        "bsonType": "object",
                        "description": "Changes from previous version"
                    },
                    "createdAt": {
                        "bsonType": "date"
                    },
                    "deprecatedAt": {
                        "bsonType": ["date", "null"]
                    }
                }
            }
        })
        
        # Create indexes for template_versions
        await db.template_versions.create_index([("templateId", ASCENDING), ("version", ASCENDING)], unique=True)
        await db.template_versions.create_index([("templateId", ASCENDING), ("isLatest", ASCENDING)])
        await db.template_versions.create_index([("bankCode", ASCENDING), ("propertyType", ASCENDING)])
        await db.template_versions.create_index([("isActive", ASCENDING)])
        await db.template_versions.create_index([("createdAt", DESCENDING)])
        
        print("✅ template_versions collection created with indexes")
        
        # 2. Template Snapshots Collection  
        print("Creating template_snapshots collection...")
        
        await db.template_snapshots.drop()
        
        await db.create_collection("template_snapshots", validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["templateIds", "version", "contentHash", "templateDefinitions"],
                "properties": {
                    "templateIds": {
                        "bsonType": "array",
                        "items": {"bsonType": "string"},
                        "description": "Array of template IDs in this snapshot"
                    },
                    "version": {
                        "bsonType": "string",
                        "description": "Template version when snapshot was created"
                    },
                    "contentHash": {
                        "bsonType": "string",
                        "description": "SHA256 hash of template definitions for deduplication"
                    },
                    "templateDefinitions": {
                        "bsonType": "object",
                        "description": "Complete template definitions keyed by templateId"
                    },
                    "createdAt": {
                        "bsonType": "date"
                    },
                    "referencedByReports": {
                        "bsonType": "array",
                        "items": {"bsonType": "string"},
                        "description": "Report IDs that reference this snapshot"
                    }
                }
            }
        })
        
        # Create indexes for template_snapshots
        await db.template_snapshots.create_index([("contentHash", ASCENDING)], unique=True)
        await db.template_snapshots.create_index([("templateIds", ASCENDING)])
        await db.template_snapshots.create_index([("version", ASCENDING)])
        await db.template_snapshots.create_index([("createdAt", DESCENDING)])
        
        print("✅ template_snapshots collection created with indexes")
        
        # 3. Template Migrations Collection
        print("Creating template_migrations collection...")
        
        await db.template_migrations.drop()
        
        await db.create_collection("template_migrations", validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["templateId", "fromVersion", "toVersion", "migrationRules"],
                "properties": {
                    "templateId": {
                        "bsonType": "string",
                        "description": "Template identifier"
                    },
                    "fromVersion": {
                        "bsonType": "string",
                        "description": "Source version"
                    },
                    "toVersion": {
                        "bsonType": "string", 
                        "description": "Target version"
                    },
                    "migrationRules": {
                        "bsonType": "object",
                        "description": "Field mapping and transformation rules"
                    },
                    "isAutomatic": {
                        "bsonType": "bool",
                        "description": "Whether migration can be done automatically"
                    },
                    "createdAt": {
                        "bsonType": "date"
                    }
                }
            }
        })
        
        # Create indexes for template_migrations
        await db.template_migrations.create_index([("templateId", ASCENDING), ("fromVersion", ASCENDING), ("toVersion", ASCENDING)], unique=True)
        await db.template_migrations.create_index([("templateId", ASCENDING)])
        
        print("✅ template_migrations collection created with indexes")
        
        # 4. Update existing valuation_reports collection
        print("Updating valuation_reports collection schema...")
        
        # Add new fields to existing reports (backward compatible)
        await db.valuation_reports.update_many(
            {"templateSnapshot": {"$exists": False}},
            {
                "$set": {
                    "templateSnapshot": {
                        "templateIds": [],
                        "version": "1.0.0",
                        "snapshotId": None,
                        "capturedAt": None
                    },
                    "migrationStatus": {
                        "currentTemplateVersion": "1.0.0",
                        "isUpgradeAvailable": False,
                        "canAutoMigrate": True,
                        "conflictingFields": []
                    }
                }
            }
        )
        
        # Create indexes for report versioning
        await db.valuation_reports.create_index([("templateSnapshot.version", ASCENDING)])
        await db.valuation_reports.create_index([("templateSnapshot.snapshotId", ASCENDING)])
        await db.valuation_reports.create_index([("migrationStatus.isUpgradeAvailable", ASCENDING)])
        
        print("✅ valuation_reports collection updated with versioning support")
        
        print("\n🎉 Template versioning database setup completed successfully!")
        
        # Display collection stats
        collections = ["template_versions", "template_snapshots", "template_migrations", "valuation_reports"]
        print("\n📊 Collection Statistics:")
        for collection_name in collections:
            collection = getattr(db, collection_name)
            count = await collection.count_documents({})
            indexes = await collection.list_indexes().to_list(length=None)
            print(f"  {collection_name}: {count} documents, {len(indexes)} indexes")
        
        # Clean up connection
        await db_manager.disconnect()
            
    except Exception as e:
        logger.error(f"Error setting up template versioning collections: {e}")
        # Clean up connection on error
        if 'db_manager' in locals():
            await db_manager.disconnect()
        raise

async def populate_initial_template_versions():
    """Populate initial template versions from existing SBI Land templates"""
    
    try:
        # Initialize database manager
        db_manager = MongoDBManager()
        await db_manager.connect()
        
        if not db_manager.is_connected or db_manager.database is None:
            raise Exception("Failed to connect to database")
        
        db = db_manager.database
        
        print("\nPopulating initial template versions from existing SBI Land templates...")
        
        # Get existing SBI Land templates
        existing_templates = await db.sbi_land_property_details.find({}).to_list(length=None)
        
        if not existing_templates:
            print("⚠️  No existing SBI Land templates found")
            return
            
        # Process the documents array from your current data structure
        for template_doc in existing_templates:
            if "documents" not in template_doc:
                continue
                
            for doc in template_doc["documents"]:
                template_version = {
                    "templateId": doc["templateId"],
                    "version": "1.0.0",  # Initial version
                    "bankCode": doc["bankCode"],
                    "propertyType": doc["propertyType"],
                    "templateCategory": doc["templateCategory"],
                    "isActive": True,
                    "isLatest": True,
                    "createdAt": datetime.utcnow(),
                    "deprecatedAt": None,
                    "templateDefinition": {
                        "templateId": doc["templateId"],
                        "templateName": doc["templateName"],
                        "uiName": doc["uiName"],
                        "documentId": doc["documentId"],
                        "documentName": doc["documentName"],
                        "sections": doc["sections"]
                    },
                    "versionChanges": {
                        "changeType": "initial",
                        "fieldsAdded": [],
                        "fieldsRemoved": [],
                        "fieldsModified": [],
                        "migrationRules": []
                    }
                }
                
                # Insert or update template version
                await db.template_versions.update_one(
                    {"templateId": doc["templateId"], "version": "1.0.0"},
                    {"$set": template_version},
                    upsert=True
                )
                
                print(f"  ✅ Created v1.0.0 for {doc['templateId']}")
        
        print(f"\n✅ Populated {len(existing_templates)} initial template versions")
        
        # Clean up connection
        await db_manager.disconnect()
        
    except Exception as e:
        logger.error(f"Error populating initial template versions: {e}")
        # Clean up connection on error
        if 'db_manager' in locals():
            await db_manager.disconnect()
        raise

async def main():
    """Main setup function"""
    print("🚀 Starting Template Versioning Database Setup")
    print("=" * 60)
    
    try:
        # Create collections and indexes
        await create_template_versioning_collections()
        
        # Populate initial data
        await populate_initial_template_versions()
        
        print("\n🎯 Next Steps:")
        print("1. Implement TemplateSnapshotService")
        print("2. Create version-aware report creation")
        print("3. Build dynamic form renderer")
        print("4. Test with SBI Land template")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)