"""
Template Snapshot Service
Handles template versioning, snapshot creation, and template retrieval
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

class TemplateSnapshotService:
    """Service for managing template snapshots and versions"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
    
    async def capture_template_snapshot(self, template_ids: List[str], version: str = "1.0.0") -> str:
        """
        Capture a snapshot of multiple templates for a report.
        Returns snapshot_id for reference.
        
        Args:
            template_ids: List of template IDs to include in snapshot
            
        Returns:
            str: Snapshot ID for storing in report
        """
        try:
            db = self.db
            
            # Get latest versions of all specified templates
            template_definitions = {}
            version = None
            
            for template_id in template_ids:
                template_version = await db.template_versions.find_one({
                    "templateId": template_id,
                    "isLatest": True,
                    "isActive": True
                })
                
                if not template_version:
                    raise ValueError(f"No active template found for {template_id}")
                
                template_definitions[template_id] = template_version["templateDefinition"]
                
                # Use the version from first template (assuming all have same version)
                if version is None:
                    version = template_version["version"]
            
            # Create content hash for deduplication
            content_hash = self._calculate_content_hash(template_definitions)
            
            # Check if snapshot with same content already exists
            existing_snapshot = await db.template_snapshots.find_one({
                "contentHash": content_hash
            })
            
            if existing_snapshot:
                logger.info(f"Reusing existing snapshot {existing_snapshot['_id']} for hash {content_hash}")
                return str(existing_snapshot["_id"])
            
            # Create new snapshot
            snapshot = {
                "templateIds": template_ids,
                "version": version,
                "contentHash": content_hash,
                "templateDefinitions": template_definitions,
                "createdAt": datetime.utcnow(),
                "referencedByReports": []
            }
            
            result = await db.template_snapshots.insert_one(snapshot)
            snapshot_id = str(result.inserted_id)
            
            logger.info(f"Created new template snapshot {snapshot_id}")
            return snapshot_id
            
        except Exception as e:
            logger.error(f"Error capturing template snapshot: {e}")
            raise
    
    def _calculate_content_hash(self, template_definitions: Dict[str, Any]) -> str:
        """Calculate SHA256 hash of template definitions for deduplication"""
        
        # Sort keys to ensure consistent hash
        sorted_content = json.dumps(template_definitions, sort_keys=True, default=str)
        return hashlib.sha256(sorted_content.encode()).hexdigest()
    
    async def get_template_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        """
        Retrieve template definitions from snapshot ID
        
        Args:
            snapshot_id: Snapshot ID to retrieve
            
        Returns:
            Dict containing template definitions
        """
        try:
            db = self.db
            
            snapshot = await db.template_snapshots.find_one({
                "_id": ObjectId(snapshot_id)
            })
            
            if not snapshot:
                raise ValueError(f"Snapshot {snapshot_id} not found")
            
            return {
                "templateDefinitions": snapshot["templateDefinitions"],
                "version": snapshot["version"],
                "templateIds": snapshot["templateIds"],
                "createdAt": snapshot["createdAt"]
            }
            
        except Exception as e:
            logger.error(f"Error retrieving template snapshot {snapshot_id}: {e}")
            raise
    
    async def get_latest_template_version(self, template_id: str) -> str:
        """Get the latest version number for a template"""
        try:
            db = self.db
            
            template = await db.template_versions.find_one({
                "templateId": template_id,
                "isLatest": True,
                "isActive": True
            })
            
            if not template:
                raise ValueError(f"No active template found for {template_id}")
            
            return template["version"]
            
        except Exception as e:
            logger.error(f"Error getting latest template version for {template_id}: {e}")
            raise
    
    async def get_template_by_version(self, template_id: str, version: str) -> Dict[str, Any]:
        """Get specific version of a template"""
        try:
            db = self.db
            
            template = await db.template_versions.find_one({
                "templateId": template_id,
                "version": version
            })
            
            if not template:
                raise ValueError(f"Template {template_id} version {version} not found")
            
            return template["templateDefinition"]
            
        except Exception as e:
            logger.error(f"Error getting template {template_id} version {version}: {e}")
            raise
    
    async def get_sbi_land_template_ids(self) -> List[str]:
        """Get all template IDs for SBI Land property type"""
        try:
            db = self.db
            
            templates = await db.template_versions.find({
                "bankCode": "SBI",
                "propertyType": "Land",
                "isLatest": True,
                "isActive": True
            }).to_list(length=None)
            
            return [t["templateId"] for t in templates]
            
        except Exception as e:
            logger.error(f"Error getting SBI Land template IDs: {e}")
            raise
    
    async def create_new_template_version(
        self, 
        template_id: str, 
        new_version: str, 
        template_definition: Dict[str, Any],
        version_changes: Dict[str, Any]
    ) -> str:
        """
        Create a new version of a template
        
        Args:
            template_id: Base template identifier
            new_version: New version number (e.g., "1.1.0")
            template_definition: Complete template structure
            version_changes: Changes from previous version
            
        Returns:
            str: Created template version ID
        """
        try:
            db = self.db
            
            # Mark previous latest as not latest
            await db.template_versions.update_many({
                "templateId": template_id,
                "isLatest": True
            }, {
                "$set": {"isLatest": False}
            })
            
            # Extract basic info from template definition
            bank_code = template_definition.get("bankCode", "UNKNOWN")
            property_type = template_definition.get("propertyType", "UNKNOWN")
            template_category = template_definition.get("templateCategory", "UNKNOWN")
            
            # Create new version
            new_template_version = {
                "templateId": template_id,
                "version": new_version,
                "bankCode": bank_code,
                "propertyType": property_type,
                "templateCategory": template_category,
                "isActive": True,
                "isLatest": True,
                "createdAt": datetime.utcnow(),
                "deprecatedAt": None,
                "templateDefinition": template_definition,
                "versionChanges": version_changes
            }
            
            result = await db.template_versions.insert_one(new_template_version)
            
            logger.info(f"Created new template version {template_id} v{new_version}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error creating new template version: {e}")
            raise
    
    async def analyze_template_changes(
        self, 
        template_id: str, 
        old_version: str, 
        new_version: str
    ) -> Dict[str, Any]:
        """
        Analyze changes between two template versions
        
        Returns:
            Dict containing change analysis with fields added/removed/modified
        """
        try:
            db = self.db
            
            # Get both versions
            old_template = await db.template_versions.find_one({
                "templateId": template_id,
                "version": old_version
            })
            
            new_template = await db.template_versions.find_one({
                "templateId": template_id,
                "version": new_version
            })
            
            if not old_template or not new_template:
                raise ValueError(f"Template versions not found for comparison")
            
            # Extract field information from both versions
            old_fields = self._extract_all_fields(old_template["templateDefinition"])
            new_fields = self._extract_all_fields(new_template["templateDefinition"])
            
            old_field_ids = set(old_fields.keys())
            new_field_ids = set(new_fields.keys())
            
            # Analyze changes
            fields_added = list(new_field_ids - old_field_ids)
            fields_removed = list(old_field_ids - new_field_ids)
            
            # Check for modified fields (same fieldId but different properties)
            fields_modified = []
            for field_id in old_field_ids & new_field_ids:
                if old_fields[field_id] != new_fields[field_id]:
                    fields_modified.append({
                        "fieldId": field_id,
                        "oldField": old_fields[field_id],
                        "newField": new_fields[field_id]
                    })
            
            return {
                "templateId": template_id,
                "fromVersion": old_version,
                "toVersion": new_version,
                "fieldsAdded": fields_added,
                "fieldsRemoved": fields_removed,
                "fieldsModified": fields_modified,
                "hasBreakingChanges": len(fields_removed) > 0 or len(fields_modified) > 0,
                "canAutoMigrate": len(fields_removed) == 0 and len(fields_modified) == 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing template changes: {e}")
            raise
    
    def _extract_all_fields(self, template_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Extract all fields from template definition recursively"""
        fields = {}
        
        sections = template_definition.get("sections", [])
        for section in sections:
            section_fields = section.get("fields", [])
            for field in section_fields:
                fields[field["fieldId"]] = field
                
                # Handle group fields with subFields
                if field.get("fieldType") == "group" and field.get("subFields"):
                    for sub_field in field["subFields"]:
                        fields[sub_field["fieldId"]] = sub_field
        
        return fields
    
    async def add_report_reference(self, snapshot_id: str, report_id: str):
        """Add report reference to snapshot for tracking"""
        try:
            db = self.db
            
            await db.template_snapshots.update_one(
                {"_id": ObjectId(snapshot_id)},
                {"$addToSet": {"referencedByReports": report_id}}
            )
            
        except Exception as e:
            logger.error(f"Error adding report reference: {e}")
            # Don't raise - this is not critical
    
    async def remove_report_reference(self, snapshot_id: str, report_id: str):
        """Remove report reference from snapshot"""
        try:
            db = self.db
            
            await db.template_snapshots.update_one(
                {"_id": ObjectId(snapshot_id)},
                {"$pull": {"referencedByReports": report_id}}
            )
            
        except Exception as e:
            logger.error(f"Error removing report reference: {e}")
            # Don't raise - this is not critical

# Global instance - to be initialized with database connection
template_snapshot_service = None