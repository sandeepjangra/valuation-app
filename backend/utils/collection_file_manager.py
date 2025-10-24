"""
Multi-Collection File Manager for Valuation Application
Handles all collections (banks, users, properties, valuations, etc.) as local JSON files
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, cast
from backend.database.multi_db_manager import MultiDatabaseSession, DatabaseType

try:
    from pymongo import MongoClient
    from bson import ObjectId
    mongodb_available = True
except ImportError:
    mongodb_available = False

logger = logging.getLogger(__name__)

class CollectionFileManager:
    """Manages all collection data as local JSON files"""
    
    # Define all collections and their databases
    COLLECTIONS_CONFIG = {
        "common_fields": {
            "database": "valuation_admin", 
            "collection": "common_form_fields",
            "description": "Common form fields"
        },
        "sbi_land_property_details": {
            "database": "valuation_admin", 
            "collection": "sbi_land_property_details",
            "description": "SBI Land Property Details Form Fields"
        },
        "banks": {
            "database": "valuation_admin", 
            "collection": "banks",
            "description": "Bank and branch information"
        },
        "users": {
            "database": "main", 
            "collection": "users",
            "description": "User accounts and profiles"
        },
        "properties": {
            "database": "main", 
            "collection": "properties",
            "description": "Property records"
        },
        "valuations": {
            "database": "main", 
            "collection": "valuations",
            "description": "Valuation assessments"
        },
        "valuation_reports": {
            "database": "reports", 
            "collection": "valuation_reports",
            "description": "Generated valuation reports"
        },
        "audit_logs": {
            "database": "reports", 
            "collection": "audit_logs",
            "description": "System audit trails"
        }
    }
    
    def __init__(self, data_dir: Optional[str] = None):
        """Initialize the collection file manager"""
        if data_dir is None:
            # Default to backend/data directory
            backend_dir = Path(__file__).parent.parent
            self.data_dir = backend_dir / "data"
        else:
            self.data_dir = Path(data_dir)
        
        self.data_dir.mkdir(exist_ok=True)
        
        logger.info(f"📁 CollectionFileManager initialized with data directory: {self.data_dir}")
    
    async def _refresh_critical_collection(self, collection_name: str, database: str, collection: str) -> bool:
        """Direct MongoDB refresh for all collections with optimized performance"""
        try:
            from pymongo import MongoClient
            
            # MongoDB configuration
            MONGODB_URI = "mongodb+srv://app_user:kHxlQqJ1Uc3bmoL6@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster"
            
            # Map logical database names to actual MongoDB database names
            db_name_mapping = {
                "valuation_admin": "valuation_admin",
                "admin": "valuation_admin",  # admin type maps to valuation_admin
                "main": "valuation_app_prod",
                "reports": "valuation_reports"
            }
            
            actual_db_name = db_name_mapping.get(database, database)
            
            client = MongoClient(MONGODB_URI, 
                               serverSelectionTimeoutMS=10000,
                               tlsAllowInvalidCertificates=True)
            
            db = client[actual_db_name]
            documents = list(db[collection].find({}))  # type: ignore
            
            logger.info(f"📊 Direct connection retrieved {len(documents)} documents from {actual_db_name}.{collection}")
            
            # Handle both empty and non-empty collections
            if documents:
                # Sort based on collection type
                if collection_name == "common_fields":
                    documents.sort(key=lambda x: (x.get('fieldGroup', ''), x.get('sortOrder', 0)))  # type: ignore
                elif collection_name == "banks":
                    documents.sort(key=lambda x: x.get('bankName', ''))  # type: ignore
                elif collection_name == "audit_logs":
                    documents.sort(key=lambda x: x.get('timestamp', ''), reverse=True)  # type: ignore
                
                # Serialize documents
                serialized_docs = [self._serialize_mongodb_doc(doc) for doc in documents]  # type: ignore
            else:
                # Empty collection is still valid
                serialized_docs = []
            
            # Write to file
            success = self.write_collection(collection_name, cast(List[Dict[str, Any]], serialized_docs))
            client.close()
            
            if success:
                logger.info(f"✅ Successfully wrote {len(serialized_docs)} documents for {collection_name}")
            
            return success
                
        except Exception as e:
            logger.error(f"❌ Direct refresh failed for {collection_name}: {e}")
            return False
    
    def _serialize_mongodb_doc(self, obj: Any) -> Any:
        """Convert MongoDB document to JSON serializable format"""
        try:
            from bson import ObjectId
            if isinstance(obj, ObjectId):
                return str(obj)
        except ImportError:
            # Handle case where bson is not available
            if hasattr(obj, '__class__') and 'ObjectId' in str(obj.__class__):
                return str(obj)
        
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {key: self._serialize_mongodb_doc(value) for key, value in obj.items()}  # type: ignore
        elif isinstance(obj, list):
            return [self._serialize_mongodb_doc(item) for item in obj]  # type: ignore
        return obj
    
    def get_file_path(self, collection_name: str) -> Path:
        """Get the file path for a collection"""
        return self.data_dir / f"{collection_name}.json"
    
    def write_collection(self, collection_name: str, documents: List[Dict[str, Any]]) -> bool:
        """Write documents to a collection file"""
        try:
            file_path = self.get_file_path(collection_name)
            
            # Prepare metadata
            metadata = {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "collection_name": collection_name,
                "total_documents": len(documents),
                "version": "1.0",
                "database": self.COLLECTIONS_CONFIG.get(collection_name, {}).get("database", "unknown")
            }
            
            # Prepare data structure - use 'fields' for common_fields to match field_file_manager
            if collection_name == "common_fields":
                data = {
                    "metadata": metadata,
                    "fields": documents
                }
            else:
                data = {
                    "metadata": metadata,
                    "documents": documents
                }
            
            # Write to temporary file first (atomic operation)
            temp_path = file_path.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=self._json_serializer)
            
            # Atomic rename
            temp_path.rename(file_path)
            
            logger.info(f"✅ Wrote {len(documents)} documents to {collection_name}.json")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error writing collection {collection_name}: {e}")
            return False
    
    def read_collection(self, collection_name: str) -> Optional[List[Dict[str, Any]]]:
        """Read documents from a collection file"""
        try:
            file_path = self.get_file_path(collection_name)
            
            if not file_path.exists():
                logger.warning(f"⚠️ Collection file not found: {collection_name}.json")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different data structures - common_fields uses 'fields', others use 'documents'
            if collection_name == "common_fields":
                documents = data.get("fields", [])
            else:
                documents = data.get("documents", [])
                
            logger.info(f"📖 Read {len(documents)} documents from {collection_name}.json")
            return documents
            
        except Exception as e:
            logger.error(f"❌ Error reading collection {collection_name}: {e}")
            return None
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about a collection file"""
        file_path = self.get_file_path(collection_name)
        
        if not file_path.exists():
            return {
                "collection_name": collection_name,
                "file_exists": False,
                "file_path": str(file_path),
                "database": self.COLLECTIONS_CONFIG.get(collection_name, {}).get("database", "unknown"),
                "description": self.COLLECTIONS_CONFIG.get(collection_name, {}).get("description", "No description")
            }
        
        try:
            # Get file stats
            stat = file_path.stat()
            file_size = stat.st_size
            last_modified = datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat()
            
            # Read metadata
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            metadata = data.get("metadata", {})
            
            # Handle different data structures - common_fields uses 'fields', others use 'documents'
            if collection_name == "common_fields":
                documents = data.get("fields", [])
            else:
                documents = data.get("documents", [])
            
            return {
                "collection_name": collection_name,
                "file_exists": True,
                "file_path": str(file_path),
                "file_size": file_size,
                "last_modified": last_modified,
                "generated_at": metadata.get("generated_at"),
                "version": metadata.get("version"),
                "total_documents": len(documents),
                "database": metadata.get("database", self.COLLECTIONS_CONFIG.get(collection_name, {}).get("database", "unknown")),
                "description": self.COLLECTIONS_CONFIG.get(collection_name, {}).get("description", "No description")
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting collection info for {collection_name}: {e}")
            return {
                "collection_name": collection_name,
                "file_exists": True,
                "file_path": str(file_path),
                "error": str(e),
                "database": self.COLLECTIONS_CONFIG.get(collection_name, {}).get("database", "unknown"),
                "description": self.COLLECTIONS_CONFIG.get(collection_name, {}).get("description", "No description")
            }
    
    def get_all_collections_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all configured collections"""
        status: Dict[str, Dict[str, Any]] = {}
        for collection_name in self.COLLECTIONS_CONFIG.keys():
            status[collection_name] = self.get_collection_info(collection_name)
        return status
    
    def delete_collection_file(self, collection_name: str) -> bool:
        """Delete a collection file"""
        try:
            file_path = self.get_file_path(collection_name)
            if file_path.exists():
                file_path.unlink()
                logger.info(f"🗑️ Deleted collection file: {collection_name}.json")
                return True
            else:
                logger.warning(f"⚠️ Collection file not found for deletion: {collection_name}.json")
                return False
        except Exception as e:
            logger.error(f"❌ Error deleting collection {collection_name}: {e}")
            return False
    
    async def refresh_collection_from_database(self, collection_name: str) -> bool:
        """Refresh a single collection from MongoDB with proper error handling"""
        if collection_name not in self.COLLECTIONS_CONFIG:
            logger.error(f"❌ Unknown collection: {collection_name}")
            return False
        
        config = self.COLLECTIONS_CONFIG[collection_name]
        database = config["database"]
        collection = config.get("collection", collection_name)  # Use configured collection name or fallback
        
        try:
            logger.info(f"🔄 Refreshing {collection_name} from database {database}.{collection}")
            
            # Use direct MongoDB connection for all collections during refresh for better performance
            success = await self._refresh_critical_collection(collection_name, database, collection)
            if success:
                logger.info(f"✅ Successfully refreshed {collection_name} using direct connection")
                return True
            else:
                logger.warning(f"⚠️ Direct connection failed for {collection_name}, trying fallback method")
            
            # Fallback to MultiDatabaseSession for other collections
            async with MultiDatabaseSession() as db:
                # For valuation_admin database, we need to use the correct database type
                if database == "valuation_admin":
                    # Use admin database type for valuation_admin
                    db_type = cast(DatabaseType, "admin")
                elif database not in ["main", "admin", "reports"]:
                    logger.error(f"❌ Invalid database type: {database}")
                    return False
                else:
                    db_type = cast(DatabaseType, database)
                
                # Fetch all documents from the collection using the correct collection name
                documents = await db.find_many(db_type, collection, {})
                
                logger.info(f"📊 Found {len(documents)} documents in {database}.{collection}")
                
                # Special handling for specific collections
                if collection_name == "common_fields":
                    # Sort common fields by group and order
                    documents.sort(key=lambda x: (x.get('fieldGroup', ''), x.get('sortOrder', 0)))
                elif collection_name == "banks":
                    # Sort banks by name
                    documents.sort(key=lambda x: x.get('bankName', ''))
                elif collection_name == "audit_logs":
                    # Sort audit logs by timestamp (newest first)
                    documents.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                
                # Write to file
                success = self.write_collection(collection_name, documents)
                
                if success:
                    logger.info(f"✅ Successfully refreshed {collection_name} with {len(documents)} documents")
                    return True
                else:
                    logger.error(f"❌ Failed to write refreshed {collection_name} to file")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error refreshing {collection_name} from database: {e}")
            return False
    
    async def refresh_all_collections_from_database(self) -> Dict[str, bool]:
        """Refresh all collections from MongoDB"""
        logger.info("🔄 Starting refresh of all collections from database")
        
        results = {}
        total_collections = len(self.COLLECTIONS_CONFIG)
        
        for i, collection_name in enumerate(self.COLLECTIONS_CONFIG.keys(), 1):
            logger.info(f"📋 Refreshing collection {i}/{total_collections}: {collection_name}")
            
            try:
                success = await self.refresh_collection_from_database(collection_name)
                results[collection_name] = success
                
                if success:
                    logger.info(f"✅ {collection_name} refreshed successfully")
                else:
                    logger.warning(f"⚠️ {collection_name} refresh failed")
                    
            except Exception as e:
                logger.error(f"❌ Error refreshing {collection_name}: {e}")
                results[collection_name] = False
        
        successful_count = sum(1 for success in results.values() if success)  # type: ignore
        logger.info(f"🎯 Refresh completed: {successful_count}/{total_collections} collections updated successfully")
        
        return results
    
    def _json_serializer(self, obj: Any) -> str:
        """JSON serializer for MongoDB objects"""
        from bson import ObjectId
        
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

# Create a global instance
collection_file_manager = CollectionFileManager()