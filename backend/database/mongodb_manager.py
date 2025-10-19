"""
MongoDB Atlas Connection Module for Valuation Application
Handles database connections, operations, and GridFS file storage
"""

import os
from typing import Optional, Dict, Any, List, Type
from types import TracebackType
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorGridFSBucket, AsyncIOMotorCollection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from bson import ObjectId
import logging
from datetime import datetime, timezone

# Configure logging
logger = logging.getLogger(__name__)

class MongoDBManager:
    """
    MongoDB Atlas connection and operations manager
    Handles async connections, CRUD operations, and file storage
    """
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient[Any]] = None
        self.database: Optional[AsyncIOMotorDatabase[Any]] = None
        self.gridfs_bucket: Optional[AsyncIOMotorGridFSBucket] = None
        self.is_connected: bool = False
        
        # Load configuration from environment
        self.connection_string = os.getenv("MONGODB_URI")
        self.database_name = os.getenv("MONGODB_DB_NAME", "valuation_app_prod")
        self.gridfs_bucket_name = os.getenv("GRIDFS_BUCKET_NAME", "valuation_files")
        
        if not self.connection_string:
            raise ValueError("MONGODB_URI environment variable is required")
    
    async def connect(self) -> bool:
        """
        Establish connection to MongoDB Atlas
        Returns True if successful, False otherwise
        """
        try:
            logger.info("Connecting to MongoDB Atlas...")
            
            # Create async motor client
            self.client = AsyncIOMotorClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=10000,         # 10 second connection timeout
                maxPoolSize=50,                 # Maximum connections in pool
                retryWrites=True,
                tlsAllowInvalidCertificates=True  # Allow invalid SSL certificates for Atlas connection
            )
            
            # Get database reference
            self.database = self.client[self.database_name]
            
            # Test connection
            await self.client.admin.command('ping')
            
            # Setup GridFS bucket for file storage
            self.gridfs_bucket = AsyncIOMotorGridFSBucket(
                self.database, 
                bucket_name=self.gridfs_bucket_name
            )
            
            self.is_connected = True
            logger.info(f"✅ Successfully connected to MongoDB Atlas database: {self.database_name}")
            
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"❌ Failed to connect to MongoDB Atlas: {e}")
            self.is_connected = False
            return False
        except Exception as e:
            logger.error(f"💥 Unexpected error during MongoDB connection: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Close MongoDB connection"""
        if self.client is not None:
            self.client.close()
            self.is_connected = False
            logger.info("🔒 Disconnected from MongoDB Atlas")
    
    def get_collection(self, collection_name: str) -> AsyncIOMotorCollection[Any]:
        """Get a collection reference"""
        if not self.is_connected or self.database is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self.database[collection_name]
    
    # ================================
    # CRUD Operations
    # ================================
    
    async def insert_one(self, collection_name: str, document: Dict[str, Any]) -> ObjectId:
        """Insert a single document"""
        try:
            collection = self.get_collection(collection_name)
            result = await collection.insert_one(document)
            logger.debug(f"Inserted document in {collection_name}: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            logger.error(f"Error inserting document in {collection_name}: {e}")
            raise
    
    async def insert_many(self, collection_name: str, documents: List[Dict[str, Any]]) -> List[ObjectId]:
        """Insert multiple documents"""
        try:
            collection = self.get_collection(collection_name)
            result = await collection.insert_many(documents)
            logger.debug(f"Inserted {len(result.inserted_ids)} documents in {collection_name}")
            return result.inserted_ids
        except Exception as e:
            logger.error(f"Error inserting documents in {collection_name}: {e}")
            raise
    
    async def find_one(self, collection_name: str, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document"""
        try:
            collection = self.get_collection(collection_name)
            document = await collection.find_one(filter_dict)
            return document
        except Exception as e:
            logger.error(f"Error finding document in {collection_name}: {e}")
            raise
    
    async def find_many(self, collection_name: str, filter_dict: Optional[Dict[str, Any]] = None,
                       limit: Optional[int] = None, sort_by: Optional[Dict[str, int]] = None) -> List[Dict[str, Any]]:
        """Find multiple documents"""
        try:
            collection = self.get_collection(collection_name)
            cursor = collection.find(filter_dict or {})
            
            if sort_by:
                cursor = cursor.sort(list(sort_by.items()))
            
            if limit:
                cursor = cursor.limit(limit)
            
            documents = await cursor.to_list(length=limit)
            return documents
        except Exception as e:
            logger.error(f"Error finding documents in {collection_name}: {e}")
            raise
    
    async def update_one(self, collection_name: str, filter_dict: Dict[str, Any], 
                        update_dict: Dict[str, Any]) -> bool:
        """Update a single document"""
        try:
            collection = self.get_collection(collection_name)
            result = await collection.update_one(filter_dict, {"$set": update_dict})
            success = result.modified_count > 0
            logger.debug(f"Updated document in {collection_name}: {success}")
            return success
        except Exception as e:
            logger.error(f"Error updating document in {collection_name}: {e}")
            raise
    
    async def delete_one(self, collection_name: str, filter_dict: Dict[str, Any]) -> bool:
        """Delete a single document"""
        try:
            collection = self.get_collection(collection_name)
            result = await collection.delete_one(filter_dict)
            success = result.deleted_count > 0
            logger.debug(f"Deleted document in {collection_name}: {success}")
            return success
        except Exception as e:
            logger.error(f"Error deleting document in {collection_name}: {e}")
            raise
    
    # ================================
    # Specialized Business Operations
    # ================================
    
    async def get_bank_by_code(self, bank_code: str) -> Optional[Dict[str, Any]]:
        """Get bank details by bank code"""
        return await self.find_one("banks", {"bankCode": bank_code, "isActive": True})
    
    async def get_active_banks(self) -> List[Dict[str, Any]]:
        """Get all active banks"""
        return await self.find_many("banks", {"isActive": True}, sort_by={"bankName": 1})
    
    async def get_template_by_id(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get template by template ID"""
        return await self.find_one("templates", {"templateId": template_id, "isActive": True})
    
    async def get_templates_for_bank(self, bank_code: str) -> List[Dict[str, Any]]:
        """Get all templates for a specific bank"""
        bank = await self.get_bank_by_code(bank_code)
        if not bank:
            return []
        
        return await self.find_many("templates", 
                                  {"bankId": bank["_id"], "isActive": True},
                                  sort_by={"templateName": 1})
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        return await self.find_one("users", {"email": email, "isActive": True})
    
    async def create_valuation_report(self, report_data: Dict[str, Any]) -> ObjectId:
        """Create a new valuation report"""
        # Add metadata
        report_data.update({
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc),
            "workflow": {
                "status": "DRAFT",
                "submittedBy": report_data.get("createdBy"),
                "submittedAt": None,
                "reviewedBy": None,
                "reviewedAt": None
            },
            "auditTrail": [{
                "action": "CREATED",
                "performedBy": report_data.get("createdBy"),
                "timestamp": datetime.now(timezone.utc),
                "details": "Report created"
            }]
        })
        
        return await self.insert_one("valuation_reports", report_data)
    
    async def get_reports_for_user(self, user_id: ObjectId, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get reports created by a user"""
        filter_dict: Dict[str, Any] = {"workflow.submittedBy": user_id}
        if status:
            filter_dict["workflow.status"] = status
        
        return await self.find_many("valuation_reports", filter_dict, 
                                  sort_by={"createdAt": -1})
    
    # ================================
    # File Storage Operations (GridFS)
    # ================================
    
    async def upload_file(self, file_data: bytes, filename: str, 
                         content_type: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> ObjectId:
        """Upload file to GridFS"""
        try:
            if self.gridfs_bucket is None:
                raise RuntimeError("GridFS bucket not initialized")
            
            file_id = await self.gridfs_bucket.upload_from_stream(
                filename,
                file_data,
                metadata={
                    "contentType": content_type,
                    "uploadedAt": datetime.now(timezone.utc),
                    **(metadata or {})
                }
            )
            
            logger.debug(f"Uploaded file {filename} with ID: {file_id}")
            return file_id
            
        except Exception as e:
            logger.error(f"Error uploading file {filename}: {e}")
            raise
    
    async def download_file(self, file_id: ObjectId) -> bytes:
        """Download file from GridFS"""
        try:
            if self.gridfs_bucket is None:
                raise RuntimeError("GridFS bucket not initialized")
            
            grid_out = await self.gridfs_bucket.open_download_stream(file_id)
            file_data = await grid_out.read()
            
            logger.debug(f"Downloaded file with ID: {file_id}")
            return file_data
            
        except Exception as e:
            logger.error(f"Error downloading file {file_id}: {e}")
            raise
    
    async def delete_file(self, file_id: ObjectId) -> bool:
        """Delete file from GridFS"""
        try:
            if self.gridfs_bucket is None:
                raise RuntimeError("GridFS bucket not initialized")
            
            await self.gridfs_bucket.delete(file_id)
            logger.debug(f"Deleted file with ID: {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {e}")
            return False
    
    # ================================
    # Health Check
    # ================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Check database health and return status"""
        try:
            if not self.is_connected:
                return {"status": "disconnected", "message": "Not connected to database"}
            
            # Test connection
            if self.client is not None:
                await self.client.admin.command('ping')
            
            # Get database stats
            if self.database is not None:
                stats = await self.database.command("dbStats")
            else:
                stats = {}
            
            return {
                "status": "healthy",
                "database": self.database_name,
                "collections": stats.get("collections", 0),
                "dataSize": stats.get("dataSize", 0),
                "indexSize": stats.get("indexSize", 0),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

# Global database manager instance
db_manager = MongoDBManager()

# Helper functions for easy access
async def get_db_manager() -> MongoDBManager:
    """Get database manager instance"""
    if not db_manager.is_connected:
        await db_manager.connect()
    return db_manager

# Context manager for database operations
class DatabaseSession:
    """Context manager for database operations"""
    
    async def __aenter__(self) -> MongoDBManager:
        self.manager = await get_db_manager()
        return self.manager
    
    async def __aexit__(self, exc_type: Optional[Type[BaseException]], 
                       exc_val: Optional[BaseException], 
                       exc_tb: Optional[TracebackType]) -> None:
        # Optional: implement connection cleanup
        pass

# Example usage:
# async with DatabaseSession() as db:
#     banks = await db.get_active_banks()
#     user = await db.get_user_by_email("user@example.com")