#!/usr/bin/env python3
"""
MongoDB Atlas Backup Script
Creates a local backup of all MongoDB Atlas databases and collections
Usage: python scripts/backup_mongodb.py
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import json_util

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MongoDBBackup:
    """Handles MongoDB Atlas backup operations"""
    
    def __init__(self, connection_uri: str, backup_dir: str = None):
        """
        Initialize backup manager
        
        Args:
            connection_uri: MongoDB Atlas connection string
            backup_dir: Directory to store backups (default: ./backups)
        """
        self.connection_uri = connection_uri
        self.backup_dir = backup_dir or os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'backups'
        )
        self.client = None
        
    def connect(self):
        """Establish connection to MongoDB Atlas"""
        try:
            logger.info("🔗 Connecting to MongoDB Atlas...")
            self.client = MongoClient(self.connection_uri)
            # Test connection
            self.client.admin.command('ping')
            logger.info("✅ Successfully connected to MongoDB Atlas")
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("🔒 Disconnected from MongoDB Atlas")
    
    def create_backup(self, databases: List[str] = None) -> Dict[str, Any]:
        """
        Create backup of specified databases
        
        Args:
            databases: List of database names to backup (None = all databases)
            
        Returns:
            Dictionary with backup statistics
        """
        # Create timestamp for this backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(self.backup_dir, f'backup_{timestamp}')
        
        # Create backup directory
        Path(backup_path).mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Backup directory: {backup_path}")
        
        stats = {
            'timestamp': timestamp,
            'backup_path': backup_path,
            'databases': {},
            'total_documents': 0,
            'total_collections': 0
        }
        
        try:
            # Get list of databases to backup
            if not databases:
                # Get all databases except system databases
                all_dbs = self.client.list_database_names()
                databases = [
                    db for db in all_dbs 
                    if db not in ['admin', 'local', 'config']
                ]
            
            logger.info(f"📋 Backing up {len(databases)} database(s): {', '.join(databases)}")
            
            # Backup each database
            for db_name in databases:
                logger.info(f"\n🗄️  Backing up database: {db_name}")
                db_stats = self._backup_database(db_name, backup_path)
                stats['databases'][db_name] = db_stats
                stats['total_documents'] += db_stats['total_documents']
                stats['total_collections'] += db_stats['collections_count']
            
            # Save backup metadata
            metadata_path = os.path.join(backup_path, 'backup_metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(stats, f, indent=2, default=str)
            
            logger.info(f"\n✅ Backup completed successfully!")
            logger.info(f"📊 Total: {stats['total_collections']} collections, {stats['total_documents']} documents")
            logger.info(f"💾 Backup location: {backup_path}")
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            raise
    
    def _backup_database(self, db_name: str, backup_path: str) -> Dict[str, Any]:
        """
        Backup a single database
        
        Args:
            db_name: Name of database to backup
            backup_path: Root backup directory path
            
        Returns:
            Dictionary with database backup statistics
        """
        db = self.client[db_name]
        collections = db.list_collection_names()
        
        db_path = os.path.join(backup_path, db_name)
        Path(db_path).mkdir(parents=True, exist_ok=True)
        
        db_stats = {
            'collections': {},
            'collections_count': len(collections),
            'total_documents': 0
        }
        
        # Backup each collection
        for collection_name in collections:
            logger.info(f"  📦 Backing up collection: {collection_name}")
            collection_stats = self._backup_collection(
                db[collection_name],
                db_path,
                collection_name
            )
            db_stats['collections'][collection_name] = collection_stats
            db_stats['total_documents'] += collection_stats['document_count']
            logger.info(f"     ✓ {collection_stats['document_count']} documents backed up")
        
        return db_stats
    
    def _backup_collection(
        self, 
        collection, 
        db_path: str, 
        collection_name: str
    ) -> Dict[str, Any]:
        """
        Backup a single collection
        
        Args:
            collection: MongoDB collection object
            db_path: Database backup directory path
            collection_name: Name of the collection
            
        Returns:
            Dictionary with collection backup statistics
        """
        # Get all documents from collection
        documents = list(collection.find({}))
        
        # Save to JSON file
        collection_file = os.path.join(db_path, f"{collection_name}.json")
        with open(collection_file, 'w') as f:
            # Use json_util to handle MongoDB types (ObjectId, datetime, etc.)
            json.dump(documents, f, indent=2, default=json_util.default)
        
        # Get collection stats
        stats = {
            'document_count': len(documents),
            'file_path': collection_file,
            'file_size_bytes': os.path.getsize(collection_file)
        }
        
        # Get indexes
        indexes = list(collection.list_indexes())
        if indexes:
            indexes_file = os.path.join(db_path, f"{collection_name}_indexes.json")
            with open(indexes_file, 'w') as f:
                json.dump(indexes, f, indent=2, default=json_util.default)
            stats['indexes_count'] = len(indexes)
        
        return stats
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backups
        
        Returns:
            List of backup metadata dictionaries
        """
        backups = []
        
        if not os.path.exists(self.backup_dir):
            return backups
        
        # Find all backup directories
        for backup_name in os.listdir(self.backup_dir):
            backup_path = os.path.join(self.backup_dir, backup_name)
            if not os.path.isdir(backup_path):
                continue
            
            # Try to read metadata
            metadata_path = os.path.join(backup_path, 'backup_metadata.json')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    backups.append(metadata)
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return backups
    
    def restore_backup(self, backup_timestamp: str, databases: List[str] = None):
        """
        Restore from a backup
        
        Args:
            backup_timestamp: Timestamp of the backup to restore
            databases: List of databases to restore (None = all)
        """
        backup_path = os.path.join(self.backup_dir, f'backup_{backup_timestamp}')
        
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup not found: {backup_path}")
        
        logger.info(f"🔄 Restoring backup from: {backup_path}")
        
        # Get list of databases to restore
        if not databases:
            databases = [
                d for d in os.listdir(backup_path) 
                if os.path.isdir(os.path.join(backup_path, d))
            ]
        
        logger.warning("⚠️  WARNING: This will overwrite existing data!")
        response = input("Continue with restore? (yes/no): ")
        if response.lower() != 'yes':
            logger.info("Restore cancelled")
            return
        
        # Restore each database
        for db_name in databases:
            logger.info(f"\n🗄️  Restoring database: {db_name}")
            self._restore_database(db_name, backup_path)
        
        logger.info(f"\n✅ Restore completed successfully!")
    
    def _restore_database(self, db_name: str, backup_path: str):
        """
        Restore a single database
        
        Args:
            db_name: Name of database to restore
            backup_path: Root backup directory path
        """
        db = self.client[db_name]
        db_path = os.path.join(backup_path, db_name)
        
        if not os.path.exists(db_path):
            logger.warning(f"⚠️  Database backup not found: {db_name}")
            return
        
        # Restore each collection
        for filename in os.listdir(db_path):
            if not filename.endswith('.json') or filename.endswith('_indexes.json'):
                continue
            
            collection_name = filename.replace('.json', '')
            logger.info(f"  📦 Restoring collection: {collection_name}")
            
            # Read collection data
            collection_file = os.path.join(db_path, filename)
            with open(collection_file, 'r') as f:
                documents = json.load(f, object_hook=json_util.object_hook)
            
            # Drop existing collection
            db[collection_name].drop()
            
            # Insert documents
            if documents:
                db[collection_name].insert_many(documents)
                logger.info(f"     ✓ {len(documents)} documents restored")
            
            # Restore indexes if available
            indexes_file = os.path.join(db_path, f"{collection_name}_indexes.json")
            if os.path.exists(indexes_file):
                with open(indexes_file, 'r') as f:
                    indexes = json.load(f, object_hook=json_util.object_hook)
                # Skip the default _id index
                for index in indexes:
                    if index.get('name') != '_id_':
                        try:
                            db[collection_name].create_index(
                                list(index['key'].items()),
                                name=index.get('name')
                            )
                        except Exception as e:
                            logger.warning(f"     ⚠️  Failed to restore index {index.get('name')}: {e}")


def main():
    """Main entry point for the backup script"""
    # Load environment variables
    load_dotenv()
    
    # Get MongoDB URI
    mongodb_uri = os.getenv('MONGODB_URI')
    if not mongodb_uri:
        logger.error("❌ MONGODB_URI not found in environment variables")
        sys.exit(1)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='MongoDB Atlas Backup Tool')
    parser.add_argument(
        '--action',
        choices=['backup', 'restore', 'list'],
        default='backup',
        help='Action to perform (default: backup)'
    )
    parser.add_argument(
        '--databases',
        nargs='*',
        help='Specific databases to backup/restore (default: all)'
    )
    parser.add_argument(
        '--timestamp',
        help='Timestamp of backup to restore (for restore action)'
    )
    parser.add_argument(
        '--backup-dir',
        help='Directory to store backups (default: ./backups)'
    )
    
    args = parser.parse_args()
    
    # Create backup manager
    backup_manager = MongoDBBackup(
        mongodb_uri,
        backup_dir=args.backup_dir
    )
    
    try:
        # Connect to MongoDB
        backup_manager.connect()
        
        # Perform requested action
        if args.action == 'backup':
            logger.info("🚀 Starting MongoDB backup...")
            stats = backup_manager.create_backup(databases=args.databases)
            
        elif args.action == 'list':
            logger.info("📋 Available backups:")
            backups = backup_manager.list_backups()
            if not backups:
                logger.info("No backups found")
            else:
                for backup in backups:
                    logger.info(f"\n  Timestamp: {backup['timestamp']}")
                    logger.info(f"  Location: {backup['backup_path']}")
                    logger.info(f"  Databases: {len(backup['databases'])}")
                    logger.info(f"  Total Collections: {backup['total_collections']}")
                    logger.info(f"  Total Documents: {backup['total_documents']}")
        
        elif args.action == 'restore':
            if not args.timestamp:
                logger.error("❌ --timestamp required for restore action")
                sys.exit(1)
            backup_manager.restore_backup(
                args.timestamp,
                databases=args.databases
            )
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        # Disconnect from MongoDB
        backup_manager.disconnect()


if __name__ == '__main__':
    main()
