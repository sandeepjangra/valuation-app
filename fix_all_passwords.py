#!/usr/bin/env python3
"""
Fix All User Passwords
Script to set all users' passwords to 'admin123' for easy testing
"""

import os
import sys
from datetime import datetime, timezone

# Set environment variables from .env
os.environ["MONGODB_URI"] = "mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster"

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from pymongo import MongoClient
import bcrypt

def fix_all_user_passwords():
    """Set all users' passwords to 'admin123' for easy testing"""
    print("🔧 Fixing All User Passwords")
    print("=" * 50)
    
    # Connect to MongoDB
    client = MongoClient(os.environ["MONGODB_URI"])
    
    # Standard password for all users
    standard_password = "admin123"
    password_bytes = standard_password.encode('utf-8')
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    print(f"🔑 Setting all passwords to: {standard_password}")
    print(f"📝 Password hash: {password_hash[:50]}...")
    print()
    
    # Databases to check for users
    databases_to_check = [
        "valuation_admin",
        "system-administration",
        "sk-tindwal", 
        "yogesh-jangra",
        "val_app_config"
    ]
    
    total_updated = 0
    
    for db_name in databases_to_check:
        print(f"📋 Checking database: {db_name}")
        
        try:
            db = client[db_name]
            
            # Check if users collection exists
            if "users" in db.list_collection_names():
                users_collection = db["users"]
                
                # Get all users
                users = list(users_collection.find({}, {"email": 1, "full_name": 1, "role": 1}))
                
                if users:
                    print(f"   Found {len(users)} users:")
                    
                    for user in users:
                        email = user.get('email', 'N/A')
                        name = user.get('full_name', 'N/A')
                        role = user.get('role', 'N/A')
                        
                        # Update password
                        result = users_collection.update_one(
                            {"_id": user["_id"]},
                            {
                                "$set": {
                                    "password_hash": password_hash,
                                    "updated_at": datetime.now(timezone.utc)
                                }
                            }
                        )
                        
                        if result.modified_count > 0:
                            print(f"   ✅ {email} ({name}) - Role: {role}")
                            total_updated += 1
                        else:
                            print(f"   ⚠️  {email} - No update needed")
                else:
                    print("   No users found")
            else:
                print("   No users collection")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    # Also ensure admin user exists in system-administration database
    print("🔐 Ensuring System Admin User exists...")
    sys_admin_db = client["system-administration"]
    sys_users = sys_admin_db["users"]
    
    admin_user = {
        "email": "admin@system.com",
        "full_name": "System Administrator",
        "first_name": "System",
        "last_name": "Administrator", 
        "role": "admin",
        "is_system_admin": True,
        "is_active": True,
        "password_hash": password_hash,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    result = sys_users.update_one(
        {"email": "admin@system.com"},
        {"$set": admin_user},
        upsert=True
    )
    
    if result.upserted_id:
        print("✅ Created system admin user")
        total_updated += 1
    else:
        print("✅ Updated system admin user")
        total_updated += 1
    
    print()
    print("=" * 50)
    print(f"🎉 Password reset complete!")
    print(f"📊 Total users updated: {total_updated}")
    print(f"🔑 All users can now login with password: {standard_password}")
    print()
    print("Common test users:")
    print("   • admin@system.com / admin123 (System Admin)")
    print("   • sk.tindwal@gmail.com / admin123 (Manager)")
    print("   • Any other user / admin123")
    
    client.close()

if __name__ == "__main__":
    fix_all_user_passwords()