"""
Multi-Database MongoDB Atlas Connection Module for Valuation Application
Handles connections to multiple databases: main, admin, and reports
"""

import os
from typing import Optional, Dict, Any, List, Type, Literal, Tuple
from types import TracebackType
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorGridFSBucket, AsyncIOMotorCollection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from bson import ObjectId
import logging
from datetime import datetime, timezone

# Configure logging
logger = logging.getLogger(__name__)

DatabaseType = Literal["main", "admin", "reports"]

class MultiDatabaseManager:
    """
    Multi-Database MongoDB Atlas connection and operations manager
    Handles async connections to multiple databases for different purposes
    """
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient[Any]] = None
        self.databases: Dict[str, AsyncIOMotorDatabase[Any]] = {}
        self.gridfs_buckets: Dict[str, AsyncIOMotorGridFSBucket] = {}
        self.is_connected: bool = False
        
        # Load configuration from environment
        self.connection_string = os.getenv("MONGODB_URI")
        if not self.connection_string:
            raise ValueError("MONGODB_URI environment variable is required")
        
        # Database names configuration
        self.database_names = {
            "main": os.getenv("MONGODB_DB_NAME", "valuation_app_prod"),
            "admin": os.getenv("MONGODB_ADMIN_DB_NAME", "valuation_admin"),
            "reports": os.getenv("MONGODB_REPORTS_DB_NAME", "valuation_reports")
        }
        
        # GridFS bucket names
        self.gridfs_bucket_names = {
            "main": os.getenv("GRIDFS_BUCKET_NAME", "valuation_files"),
            "admin": "admin_files",
            "reports": "report_files"
        }
    
    async def connect(self) -> bool:
        """
        Establish connections to all MongoDB Atlas databases with retry logic
        Returns True if successful, False otherwise
        """
        max_retries = 3
        retry_delay = 2  # Start with 2 seconds
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Connecting to MongoDB Atlas (Multi-Database) - Attempt {attempt + 1}/{max_retries}...")
                
                # Create async motor client with more robust connection settings
                self.client = AsyncIOMotorClient(
                    self.connection_string,
                    serverSelectionTimeoutMS=30000,  # 30 second timeout for initial connection
                    connectTimeoutMS=30000,          # 30 second connection timeout
                    socketTimeoutMS=30000,           # 30 second socket timeout
                    maxPoolSize=10,                  # Reduce pool size for stability
                    minPoolSize=5,                   # Maintain minimum connections
                    maxIdleTimeMS=60000,             # Keep connections alive for 1 minute
                    retryWrites=True,
                    retryReads=True,                 # Enable retry for reads
                    tlsAllowInvalidCertificates=True, # Allow invalid SSL certificates for Atlas connection
                    # Add heartbeat settings for connection health
                    heartbeatFrequencyMS=30000       # Check connection health every 30 seconds
                )
                
                # Test connection with timeout
                import asyncio
                await asyncio.wait_for(self.client.admin.command('ping'), timeout=15.0)
                
                # Setup database references
                for db_type, db_name in self.database_names.items():
                    self.databases[db_type] = self.client[db_name]
                    logger.info(f"📋 Connected to {db_type} database: {db_name}")
                    
                    # Setup GridFS bucket for each database
                    self.gridfs_buckets[db_type] = AsyncIOMotorGridFSBucket(
                        self.databases[db_type], 
                        bucket_name=self.gridfs_bucket_names[db_type]
                    )
                
                self.is_connected = True
                logger.info("✅ Successfully connected to all MongoDB Atlas databases")
                
                return True
                
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                logger.warning(f"⚠️ Connection attempt {attempt + 1} failed: {e}")
                self.is_connected = False
                
                if attempt < max_retries - 1:  # Don't sleep on the last attempt
                    logger.info(f"🔄 Retrying in {retry_delay} seconds...")
                    import asyncio
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                
            except Exception as e:
                logger.error(f"💥 Unexpected error during MongoDB connection: {e}")
                self.is_connected = False
                
                if attempt < max_retries - 1:
                    logger.info(f"🔄 Retrying in {retry_delay} seconds...")
                    import asyncio
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
        
        logger.error(f"❌ Failed to connect to MongoDB Atlas after {max_retries} attempts")
        return False
    
    async def ensure_connection(self) -> bool:
        """Ensure we have a healthy connection, reconnect if necessary"""
        if not self.is_connected or not self.client:
            logger.info("🔄 Connection lost, attempting to reconnect...")
            return await self.connect()
        
        try:
            # Quick health check
            import asyncio
            await asyncio.wait_for(self.client.admin.command('ping'), timeout=5.0)
            return True
        except Exception as e:
            logger.warning(f"⚠️ Connection health check failed: {e}")
            self.is_connected = False
            return await self.connect()

    async def disconnect(self):
        """Close MongoDB connection"""
        if self.client is not None:
            self.client.close()
            self.is_connected = False
            logger.info("🔒 Disconnected from MongoDB Atlas")
            self.databases.clear()
            self.gridfs_buckets.clear()
            logger.info("🔒 Disconnected from MongoDB Atlas")
    
    def get_database(self, db_type: DatabaseType) -> AsyncIOMotorDatabase[Any]:
        """Get database reference by type"""
        if not self.is_connected:
            raise RuntimeError("Database not connected. Call connect() first.")
        if db_type not in self.databases:
            raise ValueError(f"Unknown database type: {db_type}")
        return self.databases[db_type]
    
    def get_collection(self, db_type: DatabaseType, collection_name: str) -> AsyncIOMotorCollection[Any]:
        """Get a collection reference from specific database"""
        database = self.get_database(db_type)
        return database[collection_name]
    
    def get_gridfs_bucket(self, db_type: DatabaseType) -> AsyncIOMotorGridFSBucket:
        """Get GridFS bucket reference by database type"""
        if not self.is_connected:
            raise RuntimeError("Database not connected. Call connect() first.")
        if db_type not in self.gridfs_buckets:
            raise ValueError(f"Unknown database type: {db_type}")
        return self.gridfs_buckets[db_type]
    
    # ================================
    # CRUD Operations with Database Selection
    # ================================
    
    async def insert_one(self, db_type: DatabaseType, collection_name: str, document: Dict[str, Any]) -> ObjectId:
        """Insert a single document into specified database"""
        if not await self.ensure_connection():
            raise RuntimeError("Failed to establish database connection")
        
        # Add audit fields
        now = datetime.now(timezone.utc)
        document.update({
            "createdAt": now,
            "updatedAt": now,
            "isActive": True
        })
        
        collection = self.get_collection(db_type, collection_name)
        result = await collection.insert_one(document)
        
        logger.info(f"📝 Inserted document into {db_type}.{collection_name}: {result.inserted_id}")
        return result.inserted_id
    
    async def find_one(self, db_type: DatabaseType, collection_name: str, filter_dict: Dict[str, Any], 
                      include_inactive: bool = False) -> Optional[Dict[str, Any]]:
        """Find a single document"""
        if not await self.ensure_connection():
            raise RuntimeError("Failed to establish database connection")
        
        # Add isActive filter unless specifically requesting inactive documents
        if not include_inactive:
            filter_dict["isActive"] = True
        
        collection = self.get_collection(db_type, collection_name)
        result = await collection.find_one(filter_dict)
        
        if result and "_id" in result:
            result["_id"] = str(result["_id"])
        
        return result
    
    async def find_many(self, db_type: DatabaseType, collection_name: str, filter_dict: Optional[Dict[str, Any]] = None,
                       sort: Optional[List[Tuple[str, int]]] = None, skip: Optional[int] = None,
                       limit: Optional[int] = None, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """Find multiple documents with advanced options"""
        if not self.is_connected:
            raise RuntimeError("Database not connected")
        
        if filter_dict is None:
            filter_dict = {}
        
        # Add isActive filter unless specifically requesting inactive documents
        if not include_inactive:
            filter_dict["isActive"] = True
        
        collection = self.get_collection(db_type, collection_name)
        cursor = collection.find(filter_dict)
        
        if sort:
            cursor = cursor.sort(sort)
        elif not sort:
            # Default sort by _id descending for consistent results
            cursor = cursor.sort([("_id", -1)])
        
        if skip:
            cursor = cursor.skip(skip)
            
        if limit:
            cursor = cursor.limit(limit)
        
        results = await cursor.to_list(length=None)
        
        # Convert ObjectId to string
        for result in results:
            if "_id" in result:
                result["_id"] = str(result["_id"])
        
        return results
    
    async def update_one(self, db_type: DatabaseType, collection_name: str, filter_dict: Dict[str, Any], 
                        update_dict: Dict[str, Any], user_id: Optional[str] = None) -> bool:
        """Update a single document with version control"""
        if not self.is_connected:
            raise RuntimeError("Database not connected")
        
        collection = self.get_collection(db_type, collection_name)
        
        # Find the current document
        current_doc = await self.find_one(db_type, collection_name, filter_dict, include_inactive=False)
        if not current_doc:
            logger.warning(f"Document not found for update in {db_type}.{collection_name}")
            return False
        
        # Deactivate current document
        await collection.update_one(
            {"_id": ObjectId(current_doc["_id"])},
            {
                "$set": {
                    "isActive": False,
                    "deactivatedAt": datetime.now(timezone.utc),
                    "deactivatedBy": user_id
                }
            }
        )
        
        # Create new version
        new_document = current_doc.copy()
        new_document.pop("_id", None)  # Remove _id to get new ObjectId
        new_document.update(update_dict)
        new_document.update({
            "updatedAt": datetime.now(timezone.utc),
            "modifiedBy": user_id,
            "version": current_doc.get("version", 1) + 1,
            "isActive": True
        })
        
        result = await collection.insert_one(new_document)
        
        logger.info(f"📝 Updated document in {db_type}.{collection_name} (new version: {result.inserted_id})")
        return True
    
    async def delete_one(self, db_type: DatabaseType, collection_name: str, filter_dict: Dict[str, Any], 
                        user_id: Optional[str] = None) -> bool:
        """Soft delete a document (mark as inactive)"""
        if not self.is_connected:
            raise RuntimeError("Database not connected")
        
        # Add isActive filter to only delete active documents
        filter_dict["isActive"] = True
        
        collection = self.get_collection(db_type, collection_name)
        result = await collection.update_one(
            filter_dict,
            {
                "$set": {
                    "isActive": False,
                    "deletedAt": datetime.now(timezone.utc),
                    "deletedBy": user_id
                }
            }
        )
        
        success = result.modified_count > 0
        if success:
            logger.info(f"🗑️ Soft deleted document from {db_type}.{collection_name}")
        else:
            logger.warning(f"No document found to delete in {db_type}.{collection_name}")
        
        return success
    
    # ================================
    # Admin-specific operations
    # ================================
    
    async def get_all_collections(self, db_type: DatabaseType) -> List[str]:
        """Get list of all collections in specified database"""
        if not self.is_connected:
            raise RuntimeError("Database not connected")
        
        database = self.get_database(db_type)
        collections = await database.list_collection_names()
        
        # Filter out system collections
        filtered_collections = [
            col for col in collections 
            if not col.startswith('fs.') and not col.startswith('system.')
        ]
        
        return filtered_collections
    
    async def get_collection_stats(self, db_type: DatabaseType, collection_name: str) -> Dict[str, Any]:
        """Get statistics for a specific collection"""
        if not self.is_connected:
            raise RuntimeError("Database not connected")
        
        collection = self.get_collection(db_type, collection_name)
        
        # Get basic stats
        total_count = await collection.count_documents({})
        active_count = await collection.count_documents({"isActive": True})
        inactive_count = total_count - active_count
        
        # Get sample document for schema understanding
        sample_doc = await collection.find_one({"isActive": True})
        
        return {
            "collection_name": collection_name,
            "database": db_type,
            "total_documents": total_count,
            "active_documents": active_count,
            "inactive_documents": inactive_count,
            "sample_fields": list(sample_doc.keys()) if sample_doc else [],
            "last_updated": sample_doc.get("updatedAt") if sample_doc else None
        }
    
    async def get_all_documents(self, db_type: DatabaseType, collection_name: str, 
                               include_inactive: bool = False, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all documents from a collection with pagination"""
        return await self.find_many(
            db_type, collection_name, {}, 
            sort=[("updatedAt", -1)], 
            limit=limit, 
            include_inactive=include_inactive
        )
    
    # ================================
    # Health Check
    # ================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for all databases"""
        if not self.is_connected:
            return {"status": "disconnected", "databases": {}}
        
        health_status: Dict[str, Any] = {
            "status": "healthy",
            "databases": {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        for db_type, database in self.databases.items():
            try:
                # Test database connection
                await database.command("ping")
                collections = await database.list_collection_names()
                
                health_status["databases"][db_type] = {
                    "status": "healthy",
                    "name": self.database_names[db_type],
                    "collections": len(collections),
                    "collection_names": collections
                }
            except Exception as e:
                health_status["databases"][db_type] = {
                    "status": "error",
                    "error": str(e)
                }
                health_status["status"] = "partial"
        
        return health_status

    async def count_documents(self, db_type: DatabaseType, collection_name: str, filter_dict: Optional[Dict[str, Any]] = None) -> int:
        """Count documents in a collection"""
        if not self.is_connected:
            raise RuntimeError("Database not connected")
        
        if filter_dict is None:
            filter_dict = {}
        
        collection = self.get_collection(db_type, collection_name)
        return await collection.count_documents(filter_dict)


# ================================
# Session Context Manager
# ================================

class MultiDatabaseSession:
    """Context manager for database operations across multiple databases"""
    
    def __init__(self):
        self.manager = MultiDatabaseManager()
    
    async def __aenter__(self) -> MultiDatabaseManager:
        await self.manager.connect()
        return self.manager
    
    async def __aexit__(self, 
                       exc_type: Optional[Type[BaseException]], 
                       exc_val: Optional[BaseException], 
                       exc_tb: Optional[TracebackType]) -> None:
        await self.manager.disconnect()


# Global instance for import
multi_db_manager = MultiDatabaseManager()