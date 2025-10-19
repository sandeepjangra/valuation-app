"""
Admin API Endpoints for Database Management
Provides CRUD operations for all collections across multiple databases
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timezone
from bson import ObjectId
import json
import logging
from database.multi_db_manager import MultiDatabaseSession, DatabaseType

logger = logging.getLogger(__name__)

# Create router for admin endpoints
admin_router = APIRouter(prefix="/api/admin", tags=["admin"])

# Helper function for current user (TODO: implement proper auth)
async def get_current_admin_user():
    """TODO: Implement proper admin authentication"""
    return {"_id": "admin", "username": "admin", "role": "admin"}

# JSON serialization helper
def json_serializer(obj):
    """JSON serializer for MongoDB objects"""
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

@admin_router.get("/databases")
async def get_databases():
    """Get list of all databases and their collections"""
    try:
        async with MultiDatabaseSession() as db:
            databases = []
            
            # Define our known databases and their collections
            database_info = {
                "admin": ["banks", "common_form_fields"],
                "main": ["users", "properties", "valuations"],
                "reports": ["valuation_reports", "audit_logs"]
            }
            
            for db_name, collections in database_info.items():
                databases.append({
                    "name": db_name,
                    "collections": collections
                })
            
            return databases
            
    except Exception as e:
        logger.error(f"Error getting databases: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve databases")

@admin_router.get("/databases/{database}/collections")
async def get_collections(database: str):
    """Get collections for a specific database"""
    try:
        if database not in ["admin", "main", "reports"]:
            raise HTTPException(status_code=404, detail="Database not found")
            
        collections_map = {
            "admin": ["banks", "common_form_fields"],
            "main": ["users", "properties", "valuations"],
            "reports": ["valuation_reports", "audit_logs"]
        }
        
        return collections_map.get(database, [])
        
    except Exception as e:
        logger.error(f"Error getting collections for {database}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve collections")

@admin_router.get("/databases/{database}/collections/{collection}/documents")
async def get_documents(
    database: str,
    collection: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Get paginated documents from a collection"""
    try:
        if database not in ["admin", "main", "reports"]:
            raise HTTPException(status_code=404, detail="Database not found")
            
        async with MultiDatabaseSession() as db:
            # Calculate skip value
            skip = (page - 1) * limit
            
            # Get total count
            total = await db.count_documents(database, collection, {})
            
            # Get paginated documents
            documents = await db.find_many(
                database, 
                collection, 
                {},
                skip=skip,
                limit=limit,
                sort=[("_id", -1)]  # Most recent first
            )
            
            # Calculate total pages
            total_pages = (total + limit - 1) // limit
            
            return {
                "documents": json.loads(json.dumps(documents, default=json_serializer)),
                "total": total,
                "page": page,
                "totalPages": total_pages
            }
            
    except Exception as e:
        logger.error(f"Error getting documents from {database}.{collection}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve documents")

@admin_router.get("/databases/{database}/collections/{collection}/documents/{document_id}")
async def get_document(database: str, collection: str, document_id: str):
    """Get a specific document by ID"""
    try:
        if database not in ["admin", "main", "reports"]:
            raise HTTPException(status_code=404, detail="Database not found")
            
        # Cast to proper type
        db_type: DatabaseType = database  # type: ignore
            
        async with MultiDatabaseSession() as db:
            # Try to find by string ID first (as stored), then by ObjectId
            document = await db.find_one(db_type, collection, {"_id": document_id}, include_inactive=True)
            
            if not document:
                # Try with ObjectId conversion
                try:
                    document = await db.find_one(db_type, collection, {"_id": ObjectId(document_id)}, include_inactive=True)
                except:
                    pass
            
            if not document:
                raise HTTPException(status_code=404, detail="Document not found")
            
            return document
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document {document_id} from {database}.{collection}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve document")

@admin_router.post("/databases/{database}/collections/{collection}/documents")
async def create_document(
    database: str,
    collection: str,
    document: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_admin_user)
):
    """Create a new document in a collection"""
    try:
        if database not in ["admin", "main", "reports"]:
            raise HTTPException(status_code=404, detail="Database not found")
        
        # Cast to proper type
        db_type: DatabaseType = database  # type: ignore
            
        # Add audit metadata
        now = datetime.now(timezone.utc)
        document.update({
            "createdAt": now,
            "createdBy": current_user["_id"],
            "updatedAt": now,
            "updatedBy": current_user["_id"],
            "version": 1
        })
        
        async with MultiDatabaseSession() as db:
            result = await db.insert_one(db_type, collection, document)
            
            # Log audit trail (skip for now - will fix separately)
            # await log_audit_trail(
            #     db, "CREATE", database, collection, str(result),
            #     current_user, None, document
            # )
            
            return {"_id": str(result)}
            
    except Exception as e:
        logger.error(f"Error creating document in {database}.{collection}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create document")

@admin_router.put("/databases/{database}/collections/{collection}/documents/{document_id}")
async def update_document(
    database: str,
    collection: str,
    document_id: str,
    document: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_admin_user)
):
    """Update an existing document"""
    try:
        if database not in ["admin", "main", "reports"]:
            raise HTTPException(status_code=404, detail="Database not found")
        
        # Cast to proper type
        db_type: DatabaseType = database  # type: ignore
            
        async with MultiDatabaseSession() as db:
            # Get existing document for audit trail - try both string and ObjectId
            existing_doc = await db.find_one(db_type, collection, {"_id": document_id}, include_inactive=True)
            
            if not existing_doc:
                # Try with ObjectId conversion
                try:
                    existing_doc = await db.find_one(db_type, collection, {"_id": ObjectId(document_id)}, include_inactive=True)
                except:
                    pass
            
            if not existing_doc:
                raise HTTPException(status_code=404, detail="Document not found")
            
            # Merge the existing document with updates
            updated_document = existing_doc.copy()
            updated_document.update(document)  # Override with new values
            
            # Update metadata
            now = datetime.now(timezone.utc)
            updated_document.update({
                "updatedAt": now,
                "updatedBy": current_user["_id"],
                "version": existing_doc.get("version", 1) + 1
            })
            
            # Preserve creation metadata
            if "createdAt" in existing_doc:
                updated_document["createdAt"] = existing_doc["createdAt"]
            if "createdBy" in existing_doc:
                updated_document["createdBy"] = existing_doc["createdBy"]
            
            # Remove _id from the update document since MongoDB doesn't allow modifying it
            updated_document.pop("_id", None)
            
            # For now, do a simple direct update instead of the complex versioning
            collection_obj = db.get_collection(db_type, collection)
            
            # Try to update with string ID first
            mongo_result = await collection_obj.update_one(
                {"_id": document_id}, 
                {"$set": updated_document}
            )
            
            # If no documents matched, try with ObjectId
            if mongo_result.matched_count == 0:
                try:
                    mongo_result = await collection_obj.update_one(
                        {"_id": ObjectId(document_id)}, 
                        {"$set": updated_document}
                    )
                except Exception as e:
                    logger.error(f"Failed to update with ObjectId: {e}")
            
            result = mongo_result.modified_count > 0
            
            if not result:
                raise HTTPException(status_code=404, detail="Document not found or no changes made")
            
            # Calculate changes for audit trail
            changes = calculate_changes(existing_doc, document)
            
            # Log audit trail (temporarily disabled)
            # await log_audit_trail(
            #     db, "UPDATE", database, collection, document_id,
            #     current_user, existing_doc, document
            # )
            
            return {"success": True}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating document {document_id} in {database}.{collection}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update document")

@admin_router.delete("/databases/{database}/collections/{collection}/documents/{document_id}")
async def delete_document(
    database: str,
    collection: str,
    document_id: str,
    current_user: Dict[str, Any] = Depends(get_current_admin_user)
):
    """Delete a document from a collection"""
    try:
        if database not in ["admin", "main", "reports"]:
            raise HTTPException(status_code=404, detail="Database not found")
        
        # Cast to proper type
        db_type: DatabaseType = database  # type: ignore
            
        async with MultiDatabaseSession() as db:
            # Get existing document for audit trail - try both string and ObjectId
            existing_doc = await db.find_one(db_type, collection, {"_id": document_id}, include_inactive=True)
            
            if not existing_doc:
                # Try with ObjectId conversion
                try:
                    existing_doc = await db.find_one(db_type, collection, {"_id": ObjectId(document_id)}, include_inactive=True)
                except:
                    pass
            
            if not existing_doc:
                raise HTTPException(status_code=404, detail="Document not found")
            
            # For admin interface, do a soft delete by setting isActive to false
            collection_obj = db.get_collection(db_type, collection)
            
            # Try to update with string ID first (soft delete)
            mongo_result = await collection_obj.update_one(
                {"_id": document_id}, 
                {"$set": {"isActive": False, "deletedAt": datetime.now(timezone.utc), "deletedBy": current_user["_id"]}}
            )
            
            # If no documents matched, try with ObjectId
            if mongo_result.matched_count == 0:
                try:
                    mongo_result = await collection_obj.update_one(
                        {"_id": ObjectId(document_id)}, 
                        {"$set": {"isActive": False, "deletedAt": datetime.now(timezone.utc), "deletedBy": current_user["_id"]}}
                    )
                except Exception as e:
                    logger.info(f"Failed to delete with ObjectId: {e}")
            
            result = mongo_result.modified_count > 0
            
            if not result:
                raise HTTPException(status_code=404, detail="Document not found")
            
            # Log audit trail (temporarily disabled)
            # await log_audit_trail(
            #     db, "DELETE", database, collection, document_id,
            #     current_user, existing_doc, None
            # )
            
            return {"success": True}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document {document_id} from {database}.{collection}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete document")

@admin_router.post("/databases/{database}/collections/{collection}/search")
async def search_documents(
    database: str,
    collection: str,
    query: Dict[str, Any],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Search documents in a collection"""
    try:
        if database not in ["admin", "main", "reports"]:
            raise HTTPException(status_code=404, detail="Database not found")
        
        # Cast to proper type
        db_type: DatabaseType = database  # type: ignore
            
        async with MultiDatabaseSession() as db:
            # Calculate skip value
            skip = (page - 1) * limit
            
            # Get total count
            total = await db.count_documents(db_type, collection, query)
            
            # Get paginated documents
            documents = await db.find_many(
                db_type, 
                collection, 
                query,
                skip=skip,
                limit=limit,
                sort=[("_id", -1)]
            )
            
            return {
                "documents": json.loads(json.dumps(documents, default=json_serializer)),
                "total": total
            }
            
    except Exception as e:
        logger.error(f"Error searching documents in {database}.{collection}: {e}")
        raise HTTPException(status_code=500, detail="Failed to search documents")

@admin_router.get("/databases/{database}/collections/{collection}/stats")
async def get_collection_stats(database: str, collection: str):
    """Get statistics for a collection"""
    try:
        if database not in ["admin", "main", "reports"]:
            raise HTTPException(status_code=404, detail="Database not found")
        
        # Cast to proper type
        db_type: DatabaseType = database  # type: ignore
            
        async with MultiDatabaseSession() as db:
            # Get document count
            count = await db.count_documents(db_type, collection, {})
            
            # Get collection stats (simplified - MongoDB commands require more complex setup)
            stats = {
                "count": count,
                "size": count * 1024,  # Estimated
                "avgObjSize": 1024,    # Estimated
                "indexes": []          # TODO: Get actual index info
            }
            
            return stats
            
    except Exception as e:
        logger.error(f"Error getting stats for {database}.{collection}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve collection stats")

@admin_router.get("/audit-logs")
async def get_audit_logs(
    database: Optional[str] = Query(None),
    collection: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100)
):
    """Get audit logs with optional filtering"""
    try:
        async with MultiDatabaseSession() as db:
            # Build query
            query = {}
            if database:
                query["database"] = database
            if collection:
                query["collection"] = collection
            
            # Calculate skip value
            skip = (page - 1) * limit
            
            # Get total count
            total = await db.count_documents("reports", "audit_logs", query)
            
            # Get paginated logs
            logs = await db.find_many(
                "reports",
                "audit_logs",
                query,
                skip=skip,
                limit=limit,
                sort=[("timestamp", -1)]  # Most recent first
            )
            
            return {
                "logs": json.loads(json.dumps(logs, default=json_serializer)),
                "total": total
            }
            
    except Exception as e:
        logger.error(f"Error getting audit logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve audit logs")

# Helper functions
async def log_audit_trail(
    db: MultiDatabaseSession,
    operation: str,
    database: str,
    collection: str,
    document_id: str,
    user: Dict[str, Any],
    previous_version: Optional[Dict[str, Any]] = None,
    new_version: Optional[Dict[str, Any]] = None,
    changes: Optional[Dict[str, Any]] = None
):
    """Log an audit trail entry"""
    try:
        # audit_entry = {
        #     "operation": operation,
        #     "database": database,
        #     "collection": collection,
        #     "documentId": document_id,
        #     "userId": user["_id"],
        #     "userName": user.get("username", "Unknown"),
        #     "timestamp": datetime.now(timezone.utc),
        #     "changes": changes,
        #     "previousVersion": previous_version,
        #     "newVersion": new_version
        # }
        
        # Temporarily disabled - type issues with MultiDatabaseSession
        # await db.insert_one("reports", "audit_logs", audit_entry)
        pass
        
    except Exception as e:
        logger.error(f"Error logging audit trail: {e}")
        # Don't raise here as this is supplementary logging

def calculate_changes(old_doc: Dict[str, Any], new_doc: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate changes between two documents"""
    changes = {}
    
    # Get all keys from both documents
    all_keys = set(old_doc.keys()) | set(new_doc.keys())
    
    for key in all_keys:
        old_value = old_doc.get(key)
        new_value = new_doc.get(key)
        
        # Skip metadata fields
        if key in ["updatedAt", "updatedBy", "version"]:
            continue
            
        if old_value != new_value:
            changes[key] = {
                "from": old_value,
                "to": new_value
            }
    
    return changes