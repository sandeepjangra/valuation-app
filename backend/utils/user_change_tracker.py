"""
User Change Tracking Utilities
Handles delta computation, change history, and audit trail for users
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone


# Fields that cannot be edited (immutable)
USER_IMMUTABLE_FIELDS = {
    '_id',
    'email',  # Email cannot be changed after creation
    'created_at',
    'created_by',
    'password_hash',  # Password changes handled separately
    'org_id',
    'org_short_name',
    'current_version'
}


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """
    Flatten nested dictionary for field-level comparison
    Example: {'settings': {'theme': 'dark'}} 
    => {'settings.theme': 'dark'}
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def compute_user_changes(
    current_user: Dict[str, Any],
    update_data: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Compute delta between current user state and update request
    
    Args:
        current_user: Current user document from database
        update_data: New values from update request
    
    Returns:
        List of changes in format:
        [
            {
                "field": "role",
                "old_value": "employee",
                "new_value": "manager"
            },
            ...
        ]
    """
    changes = []
    
    # Flatten both dicts for easier comparison
    current_flat = flatten_dict(current_user)
    update_flat = flatten_dict(update_data)
    
    # Find all changed fields
    for field, new_value in update_flat.items():
        # Skip immutable fields
        if field in USER_IMMUTABLE_FIELDS or field.split('.')[0] in USER_IMMUTABLE_FIELDS:
            continue
        
        # Get current value (might not exist for new nested fields)
        old_value = current_flat.get(field)
        
        # Only track if value actually changed
        if old_value != new_value:
            changes.append({
                "field": field,
                "old_value": old_value,
                "new_value": new_value
            })
    
    return changes


def validate_user_editable_fields(update_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
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
        if field in USER_IMMUTABLE_FIELDS or base_field in USER_IMMUTABLE_FIELDS:
            return False, f"Field '{field}' is immutable and cannot be modified"
    
    return True, None


async def create_user_change_record(
    changes_collection,
    user_id: str,
    changes: List[Dict[str, Any]],
    changed_by: str,
    change_type: str = "update",
    current_version: int = 0,
    metadata: Optional[Dict[str, Any]] = None
) -> int:
    """
    Create a new user change history record
    
    Args:
        changes_collection: MongoDB collection for user_changes
        user_id: User ID
        changes: List of field changes
        changed_by: User ID who made the change
        change_type: Type of change (created, update, deactivate, activate, delete)
        current_version: Current version number
        metadata: Additional metadata about the change
    
    Returns:
        New version number
    """
    new_version = current_version + 1
    
    change_record = {
        "user_id": user_id,
        "version": new_version,
        "changed_by": changed_by,
        "changed_at": datetime.now(timezone.utc),
        "change_type": change_type,
        "changes": changes,
        "metadata": metadata or {}
    }
    
    await changes_collection.insert_one(change_record)
    
    return new_version


async def get_user_change_history(
    changes_collection,
    user_id: str,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve change history for a user
    
    Args:
        changes_collection: MongoDB collection for user_changes
        user_id: User ID
        limit: Maximum number of records to return (None = all)
    
    Returns:
        List of change records sorted by version (newest first)
    """
    query = {"user_id": user_id}
    
    cursor = changes_collection.find(query).sort("version", -1)
    
    if limit:
        cursor = cursor.limit(limit)
    
    changes = await cursor.to_list(length=None)
    
    # Convert to JSON-serializable format
    for change in changes:
        change["_id"] = str(change["_id"])
        if change.get("changed_at"):
            change["changed_at"] = change["changed_at"].isoformat()
    
    return changes


async def create_user_creation_record(
    changes_collection,
    user_id: str,
    user_data: Dict[str, Any],
    created_by: str
) -> int:
    """
    Create initial change record when user is created
    
    Args:
        changes_collection: MongoDB collection for user_changes
        user_id: User ID
        user_data: Complete user document
        created_by: User ID who created this user
    
    Returns:
        Version number (always 1 for creation)
    """
    change_record = {
        "user_id": user_id,
        "version": 1,
        "changed_by": created_by,
        "changed_at": datetime.now(timezone.utc),
        "change_type": "created",
        "changes": [
            {
                "field": "user_created",
                "old_value": None,
                "new_value": {
                    "email": user_data.get("email"),
                    "full_name": user_data.get("full_name"),
                    "role": user_data.get("role"),
                    "phone": user_data.get("phone", "")
                }
            }
        ],
        "metadata": {
            "initial_role": user_data.get("role"),
            "initial_status": "active"
        }
    }
    
    await changes_collection.insert_one(change_record)
    
    return 1


async def create_status_change_record(
    changes_collection,
    user_id: str,
    old_status: bool,
    new_status: bool,
    changed_by: str,
    current_version: int
) -> int:
    """
    Create change record for status toggle (activate/deactivate)
    
    Args:
        changes_collection: MongoDB collection for user_changes
        user_id: User ID
        old_status: Previous is_active value
        new_status: New is_active value
        changed_by: User ID who made the change
        current_version: Current version number
    
    Returns:
        New version number
    """
    change_type = "activated" if new_status else "deactivated"
    
    new_version = current_version + 1
    
    change_record = {
        "user_id": user_id,
        "version": new_version,
        "changed_by": changed_by,
        "changed_at": datetime.now(timezone.utc),
        "change_type": change_type,
        "changes": [
            {
                "field": "is_active",
                "old_value": old_status,
                "new_value": new_status
            }
        ],
        "metadata": {
            "action": change_type
        }
    }
    
    await changes_collection.insert_one(change_record)
    
    return new_version


async def create_deletion_record(
    changes_collection,
    user_id: str,
    user_data: Dict[str, Any],
    deleted_by: str,
    current_version: int
) -> int:
    """
    Create change record when user is deleted
    
    Args:
        changes_collection: MongoDB collection for user_changes
        user_id: User ID
        user_data: User document before deletion
        deleted_by: User ID who deleted this user
        current_version: Current version number
    
    Returns:
        New version number
    """
    new_version = current_version + 1
    
    change_record = {
        "user_id": user_id,
        "version": new_version,
        "changed_by": deleted_by,
        "changed_at": datetime.now(timezone.utc),
        "change_type": "deleted",
        "changes": [
            {
                "field": "user_deleted",
                "old_value": {
                    "email": user_data.get("email"),
                    "full_name": user_data.get("full_name"),
                    "role": user_data.get("role"),
                    "is_active": user_data.get("is_active")
                },
                "new_value": None
            }
        ],
        "metadata": {
            "deleted_at": datetime.now(timezone.utc).isoformat(),
            "final_role": user_data.get("role"),
            "final_status": user_data.get("is_active")
        }
    }
    
    await changes_collection.insert_one(change_record)
    
    return new_version
