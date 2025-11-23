"""
Organization Change Tracking Utilities
Handles delta computation, change history, and audit trail
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone


# Fields that cannot be edited (immutable)
IMMUTABLE_FIELDS = {
    '_id',
    'org_short_name',
    'created_at',
    'created_by',
    'current_version',
    'updated_at',
    'updated_by'
}


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """
    Flatten nested dictionary for field-level comparison
    Example: {'contact_info': {'email': 'test@example.com'}} 
    => {'contact_info.email': 'test@example.com'}
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def unflatten_dict(d: Dict[str, Any], sep: str = '.') -> Dict[str, Any]:
    """
    Unflatten dictionary back to nested structure
    Example: {'contact_info.email': 'test@example.com'}
    => {'contact_info': {'email': 'test@example.com'}}
    """
    result = {}
    for key, value in d.items():
        parts = key.split(sep)
        target = result
        for part in parts[:-1]:
            if part not in target:
                target[part] = {}
            target = target[part]
        target[parts[-1]] = value
    return result


def compute_changes(
    current_org: Dict[str, Any],
    update_data: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Compute delta between current organization state and update request
    
    Args:
        current_org: Current organization document from database
        update_data: New values from update request
    
    Returns:
        List of changes in format:
        [
            {
                "field": "org_name",
                "old_value": "SK Tindwal",
                "new_value": "SK Tindwal Properties"
            },
            ...
        ]
    """
    changes = []
    
    # Flatten both dicts for easier comparison
    current_flat = flatten_dict(current_org)
    update_flat = flatten_dict(update_data)
    
    # Find all changed fields
    for field, new_value in update_flat.items():
        # Skip immutable fields
        if field in IMMUTABLE_FIELDS or field.split('.')[0] in IMMUTABLE_FIELDS:
            continue
        
        # Get current value (might not exist for new nested fields)
        old_value = current_flat.get(field)
        
        # Only track if value actually changed
        # Important: Convert None to match missing fields
        if old_value != new_value:
            changes.append({
                "field": field,
                "old_value": old_value,
                "new_value": new_value
            })
    
    return changes


def validate_editable_fields(update_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate that update request doesn't try to modify immutable fields
    
    Returns:
        (is_valid, error_message)
    """
    # Flatten to check all nested fields
    flat_data = flatten_dict(update_data)
    
    # Check for immutable fields
    for field in flat_data.keys():
        base_field = field.split('.')[0]
        if field in IMMUTABLE_FIELDS or base_field in IMMUTABLE_FIELDS:
            return False, f"Field '{field}' is immutable and cannot be modified"
    
    return True, None


def build_update_document(changes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build MongoDB $set update document from changes list
    
    Args:
        changes: List of field changes
    
    Returns:
        Dictionary suitable for MongoDB update operation
    """
    update_fields = {}
    
    for change in changes:
        field = change["field"]
        new_value = change["new_value"]
        update_fields[field] = new_value
    
    return update_fields


async def create_change_record(
    changes_collection,
    org_id: str,
    changes: List[Dict[str, Any]],
    changed_by: str,
    change_type: str = "update",
    current_version: int = 0
) -> int:
    """
    Create a new change history record
    
    Args:
        changes_collection: MongoDB collection for organization_changes
        org_id: Organization ID
        changes: List of field changes
        changed_by: User ID who made the change
        change_type: Type of change (update, deactivate, delete)
        current_version: Current version number
    
    Returns:
        New version number
    """
    from bson import ObjectId
    
    new_version = current_version + 1
    
    change_record = {
        "org_id": ObjectId(org_id) if isinstance(org_id, str) else org_id,
        "version": new_version,
        "changed_by": changed_by,
        "changed_at": datetime.now(timezone.utc),
        "change_type": change_type,
        "changes": changes
    }
    
    await changes_collection.insert_one(change_record)
    
    return new_version


async def get_change_history(
    changes_collection,
    org_id: str,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve change history for an organization
    
    Args:
        changes_collection: MongoDB collection for organization_changes
        org_id: Organization ID
        limit: Maximum number of records to return (None = all)
    
    Returns:
        List of change records sorted by version (newest first)
    """
    from bson import ObjectId
    
    query = {"org_id": ObjectId(org_id) if isinstance(org_id, str) else org_id}
    
    cursor = changes_collection.find(query).sort("version", -1)
    
    if limit:
        cursor = cursor.limit(limit)
    
    changes = await cursor.to_list(length=None)
    
    # Convert ObjectIds to strings for JSON serialization
    for change in changes:
        change["_id"] = str(change["_id"])
        change["org_id"] = str(change["org_id"])
        if change.get("changed_at"):
            change["changed_at"] = change["changed_at"].isoformat()
    
    return changes


async def verify_data_integrity(
    orgs_collection,
    changes_collection,
    org_id: str
) -> Dict[str, Any]:
    """
    Verify that current state matches history (for debugging/validation)
    
    Args:
        orgs_collection: MongoDB organizations collection
        changes_collection: MongoDB organization_changes collection
        org_id: Organization ID
    
    Returns:
        Dictionary with verification results
    """
    from bson import ObjectId
    
    # Get current state
    current_org = await orgs_collection.find_one(
        {"_id": ObjectId(org_id) if isinstance(org_id, str) else org_id}
    )
    
    if not current_org:
        return {"valid": False, "error": "Organization not found"}
    
    # Get all changes
    changes = await changes_collection.find(
        {"org_id": ObjectId(org_id) if isinstance(org_id, str) else org_id}
    ).sort("version", 1).to_list(length=None)
    
    # Check version consistency
    expected_version = len(changes)
    actual_version = current_org.get("current_version", 0)
    
    if expected_version != actual_version:
        return {
            "valid": False,
            "error": f"Version mismatch: expected {expected_version}, got {actual_version}",
            "expected_version": expected_version,
            "actual_version": actual_version
        }
    
    return {
        "valid": True,
        "version": actual_version,
        "total_changes": len(changes)
    }
