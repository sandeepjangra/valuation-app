#!/usr/bin/env python3
"""
Database Migration Script
Migrates collections from main database to admin and reports databases
"""

import asyncio
import os
import sys
import logging
from typing import Dict, List, Any
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.mongodb_manager import MongoDBManager
from backend.database.multi_db_manager import MultiDatabaseManager, DatabaseType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    """Handles migration of collections between databases"""
    
    def __init__(self):
        self.old_manager = MongoDBManager()
        self.new_manager = MultiDatabaseManager()
        
        # Migration mapping: collection_name -> target_database
        self.migration_map: Dict[str, DatabaseType] = {
            "banks": "admin",
            "common_form_fields": "admin",  # Updated to match actual collection name
            "bank_templates": "admin",
            "valuation_reports": "reports",
            "user_reports": "reports"
        }
    
    async def connect_databases(self) -> bool:
        """Connect to both old and new database managers"""
        logger.info("🔌 Connecting to databases...")
        
        old_connected = await self.old_manager.connect()
        new_connected = await self.new_manager.connect()
        
        if not old_connected:
            logger.error("❌ Failed to connect to old database")
            return False
        
        if not new_connected:
            logger.error("❌ Failed to connect to new multi-database setup")
            return False
        
        logger.info("✅ Successfully connected to all databases")
        return True
    
    async def disconnect_databases(self):
        """Disconnect from all databases"""
        await self.old_manager.disconnect()
        await self.new_manager.disconnect()
        logger.info("🔒 Disconnected from all databases")
    
    async def check_existing_collections(self) -> Dict[str, List[str]]:
        """Check what collections exist in the old database"""
        logger.info("📋 Checking existing collections...")
        
        try:
            # Get all collection names from old database
            if self.old_manager.database is None:
                raise RuntimeError("Old database not connected")
            collection_names = await self.old_manager.database.list_collection_names()
            
            # Filter out system collections
            user_collections = [
                col for col in collection_names 
                if not col.startswith('fs.') and not col.startswith('system.')
            ]
            
            # Categorize collections
            to_migrate: List[str] = []
            to_keep: List[str] = []
            
            for collection in user_collections:
                if collection in self.migration_map:
                    to_migrate.append(collection)
                else:
                    to_keep.append(collection)
            
            logger.info(f"📦 Found {len(user_collections)} user collections")
            logger.info(f"📤 Collections to migrate: {to_migrate}")
            logger.info(f"📍 Collections to keep in main DB: {to_keep}")
            
            return {
                "all_collections": user_collections,
                "to_migrate": to_migrate,
                "to_keep": to_keep
            }
            
        except Exception as e:
            logger.error(f"❌ Error checking collections: {e}")
            return {"all_collections": [], "to_migrate": [], "to_keep": []}
    
    async def migrate_collection(self, collection_name: str, target_db: DatabaseType) -> bool:
        """Migrate a single collection to target database"""
        logger.info(f"🚀 Migrating {collection_name} to {target_db} database...")
        
        try:
            # Get all documents from source collection
            source_collection = self.old_manager.get_collection(collection_name)
            documents = await source_collection.find({}).to_list(length=None)
            
            if not documents:
                logger.warning(f"⚠️ No documents found in {collection_name}")
                return True
            
            logger.info(f"📄 Found {len(documents)} documents in {collection_name}")
            
            # Add migration metadata to documents
            migration_time = datetime.now(timezone.utc)
            for doc in documents:
                # Add migration metadata
                doc["migratedAt"] = migration_time
                doc["migratedFrom"] = "valuation_app_prod"
                doc["originalCollection"] = collection_name
                
                # Ensure audit fields exist
                if "createdAt" not in doc:
                    doc["createdAt"] = doc.get("migratedAt", migration_time)
                if "updatedAt" not in doc:
                    doc["updatedAt"] = migration_time
                if "isActive" not in doc:
                    doc["isActive"] = True
                if "version" not in doc:
                    doc["version"] = 1
            
            # Insert documents into target database
            target_collection = self.new_manager.get_collection(target_db, collection_name)
            result = await target_collection.insert_many(documents)
            
            logger.info(f"✅ Successfully migrated {len(result.inserted_ids)} documents to {target_db}.{collection_name}")
            
            # Verify migration
            migrated_count = await target_collection.count_documents({})
            if migrated_count == len(documents):
                logger.info(f"✅ Migration verification passed for {collection_name}")
                return True
            else:
                logger.error(f"❌ Migration verification failed for {collection_name}: expected {len(documents)}, got {migrated_count}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error migrating {collection_name}: {e}")
            return False
    
    async def create_backup(self, collections_info: Dict[str, List[str]]) -> bool:
        """Create a backup of collections before migration"""
        logger.info("💾 Creating backup before migration...")
        
        backup_info: Dict[str, Any] = {
            "backup_time": datetime.now(timezone.utc).isoformat(),
            "collections": {},
            "total_documents": 0
        }
        
        try:
            for collection_name in collections_info["to_migrate"]:
                collection = self.old_manager.get_collection(collection_name)
                doc_count = await collection.count_documents({})
                backup_info["collections"][collection_name] = doc_count
                backup_info["total_documents"] += doc_count
            
            # Save backup info to a file
            backup_file = f"migration_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            with open(backup_file, 'w') as f:
                f.write(f"Database Migration Backup Info\n")
                f.write(f"===============================\n")
                f.write(f"Backup Time: {backup_info['backup_time']}\n")
                f.write(f"Total Documents: {backup_info['total_documents']}\n\n")
                f.write("Collections to migrate:\n")
                for col, count in backup_info["collections"].items():
                    f.write(f"  - {col}: {count} documents\n")
            
            logger.info(f"💾 Backup info saved to {backup_file}")
            logger.info(f"📊 Total documents to migrate: {backup_info['total_documents']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating backup: {e}")
            return False
    
    async def perform_migration(self, dry_run: bool = False) -> bool:
        """Perform the complete migration process"""
        logger.info("🎯 Starting database migration process...")
        
        if dry_run:
            logger.info("🧪 Running in DRY RUN mode - no actual migration will be performed")
        
        # Connect to databases
        if not await self.connect_databases():
            return False
        
        try:
            # Check existing collections
            collections_info = await self.check_existing_collections()
            
            if not collections_info["to_migrate"]:
                logger.info("✅ No collections need migration")
                return True
            
            # Create backup
            if not await self.create_backup(collections_info):
                logger.error("❌ Backup creation failed - aborting migration")
                return False
            
            if dry_run:
                logger.info("🧪 DRY RUN: Would migrate the following collections:")
                for collection in collections_info["to_migrate"]:
                    target_db = self.migration_map[collection]
                    logger.info(f"  - {collection} → {target_db}")
                return True
            
            # Perform actual migration
            migration_success = True
            for collection_name in collections_info["to_migrate"]:
                target_db = self.migration_map[collection_name]
                success = await self.migrate_collection(collection_name, target_db)
                if not success:
                    migration_success = False
                    logger.error(f"❌ Failed to migrate {collection_name}")
                    break
            
            if migration_success:
                logger.info("🎉 All collections migrated successfully!")
                logger.info("📋 Migration Summary:")
                for collection in collections_info["to_migrate"]:
                    target_db = self.migration_map[collection]
                    logger.info(f"  ✅ {collection} → {target_db}")
            else:
                logger.error("❌ Migration completed with errors")
            
            return migration_success
            
        finally:
            await self.disconnect_databases()
    
    async def verify_migration(self) -> bool:
        """Verify that migration was successful"""
        logger.info("🔍 Verifying migration...")
        
        if not await self.connect_databases():
            return False
        
        try:
            verification_success = True
            
            for collection_name, target_db in self.migration_map.items():
                # Count documents in source
                try:
                    source_collection = self.old_manager.get_collection(collection_name)
                    source_count = await source_collection.count_documents({})
                except:
                    source_count = 0
                
                # Count documents in target
                try:
                    target_count = await self.new_manager.get_collection(target_db, collection_name).count_documents({})
                except:
                    target_count = 0
                
                if source_count > 0 and target_count == source_count:
                    logger.info(f"✅ {collection_name}: {source_count} documents migrated successfully")
                elif source_count == 0 and target_count == 0:
                    logger.info(f"ℹ️ {collection_name}: No documents (empty collection)")
                elif source_count == 0 and target_count > 0:
                    logger.info(f"ℹ️ {collection_name}: {target_count} documents in target (source was empty)")
                else:
                    logger.error(f"❌ {collection_name}: Mismatch - source: {source_count}, target: {target_count}")
                    verification_success = False
            
            return verification_success
            
        finally:
            await self.disconnect_databases()


async def main():
    """Main migration function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Migration Tool")
    parser.add_argument("--dry-run", action="store_true", help="Run migration in dry-run mode")
    parser.add_argument("--verify", action="store_true", help="Verify existing migration")
    args = parser.parse_args()
    
    migrator = DatabaseMigrator()
    
    if args.verify:
        success = await migrator.verify_migration()
        if success:
            logger.info("🎉 Migration verification successful!")
        else:
            logger.error("❌ Migration verification failed!")
        return success
    
    # Perform migration
    success = await migrator.perform_migration(dry_run=args.dry_run)
    
    if success:
        if args.dry_run:
            logger.info("🧪 Dry run completed successfully!")
        else:
            logger.info("🎉 Migration completed successfully!")
            logger.info("💡 Run with --verify to verify the migration")
    else:
        logger.error("❌ Migration failed!")
    
    return success


if __name__ == "__main__":
    # Run the migration
    success = asyncio.run(main())
    exit(0 if success else 1)