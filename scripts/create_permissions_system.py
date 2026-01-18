#!/usr/bin/env python3
"""
Create RBAC Permission System
- Creates permissions_templates collection
- Seeds default permissions for 3 roles: system_admin, org_admin (manager), employee
- Creates activity_logs collection with indexes
"""

import os
import sys
from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = 'valuation_app'

def create_permissions_templates(db):
    """Create and seed permissions templates for each role"""
    
    permissions_collection = db['permissions_templates']
    
    # Clear existing templates
    permissions_collection.delete_many({})
    
    # Define permission templates for each role
    templates = [
        {
            "role": "system_admin",
            "display_name": "System Administrator",
            "description": "Complete access across all organizations and system-wide settings",
            "is_system_wide": True,
            "permissions": {
                "organizations": {
                    "view_all": True,
                    "create": True,
                    "edit_any": True,
                    "delete": True,
                    "manage_settings": True
                },
                "users": {
                    "view_all_orgs": True,
                    "view_own_org": True,
                    "create": True,
                    "edit_any": True,
                    "delete_any": True,
                    "view_activity": True,
                    "manage_roles": True
                },
                "reports": {
                    "create": True,
                    "edit_own": True,
                    "edit_others": True,
                    "delete_own": True,
                    "delete_others": True,
                    "view_drafts": True,
                    "save_draft": True,
                    "submit": True,
                    "view_all_org": True,
                    "view_all_orgs": True,
                    "export": True
                },
                "templates": {
                    "view": True,
                    "view_bank_templates": True,
                    "create_custom": True,
                    "edit_custom": True,
                    "delete_custom": True,
                    "manage_bank_templates": True,
                    "share_across_orgs": True
                },
                "drafts": {
                    "create": True,
                    "edit_own": True,
                    "edit_others": True,
                    "view_own": True,
                    "view_others": True,
                    "delete_own": True,
                    "delete_others": True
                },
                "analytics": {
                    "view_own_activity": True,
                    "view_org_activity": True,
                    "view_all_activity": True,
                    "export_reports": True
                },
                "settings": {
                    "edit_org_settings": True,
                    "edit_system_settings": True,
                    "manage_integrations": True,
                    "view_logs": True
                }
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "role": "org_admin",
            "display_name": "Organization Administrator (Manager)",
            "description": "Full access within own organization, can manage users and submit reports",
            "is_system_wide": False,
            "permissions": {
                "organizations": {
                    "view_all": False,
                    "create": False,
                    "edit_any": False,
                    "delete": False,
                    "manage_settings": True  # Can manage own org settings
                },
                "users": {
                    "view_all_orgs": False,
                    "view_own_org": True,
                    "create": True,  # Can add users to own org
                    "edit_any": True,  # Can edit users in own org
                    "delete_any": False,
                    "view_activity": True,  # Can view activity in own org
                    "manage_roles": True  # Can assign roles within org
                },
                "reports": {
                    "create": True,
                    "edit_own": True,
                    "edit_others": True,  # Can edit any report in org
                    "delete_own": True,
                    "delete_others": True,  # Can delete reports in org
                    "view_drafts": True,
                    "save_draft": True,
                    "submit": True,  # SUBMIT = APPROVAL
                    "view_all_org": True,  # Can view all reports in org
                    "view_all_orgs": False,
                    "export": True
                },
                "templates": {
                    "view": True,
                    "view_bank_templates": True,
                    "create_custom": True,  # Can create org-specific templates
                    "edit_custom": True,
                    "delete_custom": True,
                    "manage_bank_templates": False,
                    "share_across_orgs": False
                },
                "drafts": {
                    "create": True,
                    "edit_own": True,
                    "edit_others": True,  # Can edit others' drafts
                    "view_own": True,
                    "view_others": True,
                    "delete_own": True,
                    "delete_others": True
                },
                "analytics": {
                    "view_own_activity": True,
                    "view_org_activity": True,  # Can view org-wide activity
                    "view_all_activity": False,
                    "export_reports": True
                },
                "settings": {
                    "edit_org_settings": True,  # Can edit own org settings
                    "edit_system_settings": False,
                    "manage_integrations": True,
                    "view_logs": True
                }
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "role": "employee",
            "display_name": "Employee",
            "description": "Basic access - can create and edit reports, save drafts",
            "is_system_wide": False,
            "permissions": {
                "organizations": {
                    "view_all": False,
                    "create": False,
                    "edit_any": False,
                    "delete": False,
                    "manage_settings": False
                },
                "users": {
                    "view_all_orgs": False,
                    "view_own_org": True,  # Can see other users in org
                    "create": False,
                    "edit_any": False,
                    "delete_any": False,
                    "view_activity": False,
                    "manage_roles": False
                },
                "reports": {
                    "create": True,
                    "edit_own": True,
                    "edit_others": True,  # Can edit any report in org (per your answer)
                    "delete_own": True,
                    "delete_others": False,
                    "view_drafts": True,
                    "save_draft": True,
                    "submit": False,  # Cannot submit (only manager can)
                    "view_all_org": True,  # Can view all reports in org
                    "view_all_orgs": False,
                    "export": True
                },
                "templates": {
                    "view": True,
                    "view_bank_templates": True,
                    "create_custom": False,
                    "edit_custom": False,
                    "delete_custom": False,
                    "manage_bank_templates": False,
                    "share_across_orgs": False
                },
                "drafts": {
                    "create": True,
                    "edit_own": True,
                    "edit_others": True,  # Can edit any draft in org
                    "view_own": True,
                    "view_others": True,  # Can view drafts in org
                    "delete_own": True,
                    "delete_others": False
                },
                "analytics": {
                    "view_own_activity": True,
                    "view_org_activity": False,
                    "view_all_activity": False,
                    "export_reports": False
                },
                "settings": {
                    "edit_org_settings": False,
                    "edit_system_settings": False,
                    "manage_integrations": False,
                    "view_logs": False
                }
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Insert templates
    result = permissions_collection.insert_many(templates)
    print(f"✅ Created {len(result.inserted_ids)} permission templates")
    
    # Create indexes
    permissions_collection.create_index([("role", ASCENDING)], unique=True)
    print("✅ Created index on 'role' field")
    
    return templates


def create_activity_logs_collection(db):
    """Create activity_logs collection with proper indexes"""
    
    activity_logs = db['activity_logs']
    
    # Create indexes for efficient querying
    indexes = [
        ([("userId", ASCENDING), ("timestamp", DESCENDING)], {}),
        ([("orgShortName", ASCENDING), ("timestamp", DESCENDING)], {}),
        ([("action", ASCENDING), ("timestamp", DESCENDING)], {}),
        ([("timestamp", DESCENDING)], {}),
        ([("entityType", ASCENDING), ("entityId", ASCENDING)], {})
    ]
    
    for index_fields, options in indexes:
        activity_logs.create_index(index_fields, **options)
    
    print(f"✅ Created activity_logs collection with {len(indexes)} indexes")
    
    # Insert sample activity log
    sample_log = {
        "userId": "system",
        "userEmail": "system@valuation-app.com",
        "orgShortName": "system-administration",
        "action": "system.permissions_created",
        "actionType": "create",
        "description": "RBAC permission system initialized",
        "entityType": "permissions_templates",
        "entityId": None,
        "metadata": {
            "roles_created": ["system_admin", "org_admin", "employee"]
        },
        "ipAddress": "127.0.0.1",
        "userAgent": "Python Script",
        "timestamp": datetime.utcnow()
    }
    
    activity_logs.insert_one(sample_log)
    print("✅ Inserted sample activity log")


def update_users_collection_schema(db):
    """Add permission-related fields to existing users"""
    
    users = db['users']
    
    # Update all existing users to have proper role structure
    result = users.update_many(
        {"role": {"$exists": True}},
        {
            "$set": {
                "isSystemAdmin": False,  # Will be manually set for system admins
                "permissionOverrides": {}  # Empty by default
            }
        }
    )
    
    print(f"✅ Updated {result.modified_count} users with permission fields")
    
    # Update system admin users
    admin_result = users.update_many(
        {"email": {"$regex": "admin@valuation-app.com", "$options": "i"}},
        {
            "$set": {
                "isSystemAdmin": True,
                "role": "system_admin"
            }
        }
    )
    
    print(f"✅ Updated {admin_result.modified_count} users to system_admin role")


def main():
    """Main execution"""
    print("\n" + "="*60)
    print("🚀 Creating RBAC Permission System")
    print("="*60 + "\n")
    
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_URI)
        db = client[DB_NAME]
        
        print(f"📦 Connected to MongoDB: {DB_NAME}\n")
        
        # Step 1: Create permissions templates
        print("Step 1: Creating permission templates...")
        templates = create_permissions_templates(db)
        print()
        
        # Step 2: Create activity logs collection
        print("Step 2: Setting up activity logs...")
        create_activity_logs_collection(db)
        print()
        
        # Step 3: Update users collection
        print("Step 3: Updating users with permission fields...")
        update_users_collection_schema(db)
        print()
        
        # Summary
        print("="*60)
        print("✅ RBAC SYSTEM SETUP COMPLETE")
        print("="*60)
        print("\nPermission Roles Created:")
        for template in templates:
            print(f"  • {template['display_name']} ({template['role']})")
        
        print("\nCollections Created/Updated:")
        print("  • permissions_templates (with 3 role definitions)")
        print("  • activity_logs (with indexes)")
        print("  • users (updated with permission fields)")
        
        print("\n🎉 Ready to implement backend services and frontend guards!\n")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    main()
