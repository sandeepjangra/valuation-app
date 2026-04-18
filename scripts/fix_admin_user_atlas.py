#!/usr/bin/env python3
"""
Check and fix admin user organization assignment (MongoDB Atlas)
"""

from pymongo import MongoClient
from datetime import datetime
import os

# MongoDB Atlas connection
MONGODB_URI = "mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster"

print("🔌 Connecting to MongoDB Atlas...")
client = MongoClient(MONGODB_URI)
db = client['valuation_admin']
users_collection = db['users']

# Email to check
admin_email = 'admin@system.com'

print(f"\n🔍 Checking user: {admin_email}")
print("=" * 60)

# Find the user
user = users_collection.find_one({'email': admin_email})

if not user:
    print(f"❌ User {admin_email} NOT FOUND in database")
    print("\n📝 Creating admin user...")
    
    # Create admin user
    admin_user = {
        'user_id': 'admin-001',
        'email': admin_email,
        'full_name': 'System Administrator',
        'password_hash': '$2a$11$rGz9LPBnJnKpYGYqLQZQa.3vHDhPNLDnXvQZ8X5lqaJCl7oQpRrKW',
        'organization_id': 'system-administration',
        'org_short_name': 'system-administration',
        'organization_name': 'System Administration',
        'role': 'admin',
        'roles': ['admin', 'manager'],
        'status': 'active',
        'is_active': True,
        'is_system_admin': True,
        'phone': '',
        'department': 'Administration',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'last_login': None,
        'permissions': {
            'can_submit_reports': True,
            'can_manage_users': True,
            'is_manager': True,
            'is_admin': True
        }
    }
    
    result = users_collection.insert_one(admin_user)
    print(f"✅ Admin user created with ID: {result.inserted_id}")
    print(f"📧 Email: {admin_email}")
    print(f"🔑 Password: Admin@123")
    print(f"🏢 Organization: system-administration")
    
else:
    print(f"✅ User FOUND")
    print(f"\n📄 Current user details:")
    print(f"  - user_id: {user.get('user_id', 'N/A')}")
    print(f"  - email: {user.get('email', 'N/A')}")
    print(f"  - full_name: {user.get('full_name', 'N/A')}")
    print(f"  - organization_id: {user.get('organization_id', 'N/A')}")
    print(f"  - org_short_name: {user.get('org_short_name', 'N/A')}")
    print(f"  - organization_name: {user.get('organization_name', 'N/A')}")
    print(f"  - role: {user.get('role', 'N/A')}")
    print(f"  - is_active: {user.get('is_active', 'N/A')}")
    print(f"  - is_system_admin: {user.get('is_system_admin', 'N/A')}")
    
    # Check if org_short_name is missing or wrong
    if not user.get('org_short_name') or user.get('org_short_name') != 'system-administration':
        print(f"\n⚠️  ISSUE FOUND: org_short_name is '{user.get('org_short_name')}' but should be 'system-administration'")
        print("\n�� Fixing user organization...")
        
        # Update the user
        update_result = users_collection.update_one(
            {'email': admin_email},
            {
                '$set': {
                    'organization_id': 'system-administration',
                    'org_short_name': 'system-administration',
                    'organization_name': 'System Administration',
                    'is_system_admin': True,
                    'role': 'admin',
                    'roles': ['admin', 'manager'],
                    'is_active': True,
                    'updated_at': datetime.utcnow(),
                    'permissions': {
                        'can_submit_reports': True,
                        'can_manage_users': True,
                        'is_manager': True,
                        'is_admin': True
                    }
                }
            }
        )
        
        if update_result.modified_count > 0:
            print("✅ User updated successfully!")
            
            # Verify update
            updated_user = users_collection.find_one({'email': admin_email})
            print(f"\n✅ Verified updated user:")
            print(f"  - org_short_name: {updated_user.get('org_short_name')}")
            print(f"  - organization_id: {updated_user.get('organization_id')}")
            print(f"  - is_system_admin: {updated_user.get('is_system_admin')}")
        else:
            print("❌ Failed to update user")
    else:
        print("\n✅ User organization is correct!")
        print("   No changes needed.")

print("\n" + "=" * 60)
print("✅ Done!")
print("\n💡 You can now login with:")
print(f"   Email: {admin_email}")
print(f"   Password: Admin@123 (default)")
print()

client.close()
