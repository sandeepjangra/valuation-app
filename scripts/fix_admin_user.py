#!/usr/bin/env python3
"""
Fix admin user in MongoDB - ensure proper field naming
"""
import os
import sys

# Add parent directory to path to load .env
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def fix_admin_user():
    from pymongo import MongoClient
    
    # Read .env manually
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    env_vars = {}
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value.strip().strip('"')
    
    uri = env_vars.get('MONGODB_URI')
    if not uri:
        print("❌ MONGODB_URI not found in .env")
        return
    
    client = MongoClient(uri)
    db = client['valuation_admin']
    
    # Remove conflicting camelCase fields
    result = db.users.update_one(
        {'email': 'admin@system.com'},
        {
            '$unset': {
                'isActive': '',
                'isSystemAdmin': '',
                'orgShortName': '',
                'organizationName': '',
                'fullName': '',
                'userId': '',
                'createdAt': '',
                'updatedAt': '',
                'lastLogin': '',
                'passwordHash': ''
            }
        }
    )
    
    print(f'✅ Cleaned up camelCase fields - Modified: {result.modified_count}')
    
    # Ensure snake_case fields exist
    result = db.users.update_one(
        {'email': 'admin@system.com'},
        {
            '$set': {
                'is_active': True,
                'is_system_admin': True
            }
        }
    )
    
    print(f'✅ Set snake_case fields - Modified: {result.modified_count}')
    
    # Verify
    user = db.users.find_one({'email': 'admin@system.com'})
    if user:
        print(f'\n✅ User verified:')
        print(f'   Email: {user.get("email")}')
        print(f'   User ID: {user.get("user_id")}')
        print(f'   Role: {user.get("role")}')
        print(f'   Is Active: {user.get("is_active")}')
        print(f'   Is System Admin: {user.get("is_system_admin")}')
        print(f'\nAll fields: {list(user.keys())}')
    else:
        print('❌ User not found after update')

if __name__ == "__main__":
    fix_admin_user()
