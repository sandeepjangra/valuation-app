#!/usr/bin/env python3
"""
Check User Password
Script to check what password is set for a specific user
"""

import os
import sys
from datetime import datetime, timezone

# Set environment variables from .env
os.environ["MONGODB_URI"] = "mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster"

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from pymongo import MongoClient

def check_user_password():
    """Check user password in database"""
    print("🔍 Checking User Password")
    
    # Connect to MongoDB
    client = MongoClient(os.environ["MONGODB_URI"])
    
    email = "sk.tindwal@gmail.com"
    
    # Check multiple possible databases
    databases_to_check = [
        "valuation_admin",
        "system-administration", 
        "val_app_config"
    ]
    
    for db_name in databases_to_check:
        print(f"\n📋 Checking database: {db_name}")
        db = client[db_name]
        
        # Check users collection
        if "users" in db.list_collection_names():
            users_collection = db["users"]
            user = users_collection.find_one({"email": email})
            
            if user:
                print(f"✅ Found user in {db_name}.users:")
                print(f"   Email: {user.get('email')}")
                print(f"   Full Name: {user.get('full_name', 'N/A')}")
                print(f"   Role: {user.get('role', 'N/A')}")
                print(f"   Organization: {user.get('organization_name', 'N/A')}")
                print(f"   Org Short Name: {user.get('org_short_name', 'N/A')}")
                print(f"   Active: {user.get('is_active', 'N/A')}")
                
                # Check if password_hash exists
                if 'password_hash' in user:
                    hash_preview = user['password_hash'][:50] + "..." if len(user['password_hash']) > 50 else user['password_hash']
                    print(f"   Password Hash: {hash_preview}")
                    print(f"   ⚠️  For security, actual password is not displayed")
                    print(f"   💡 Typical passwords might be: user123, password123, or the user's name")
                else:
                    print(f"   ❌ No password_hash field found")
                
                if 'created_at' in user:
                    print(f"   Created: {user['created_at']}")
                
                print()
                return True
    
    print(f"❌ User {email} not found in any database")
    
    # Also check if there are any users in the databases
    for db_name in databases_to_check:
        db = client[db_name]
        if "users" in db.list_collection_names():
            users_collection = db["users"]
            user_count = users_collection.count_documents({})
            print(f"📊 {db_name}.users has {user_count} total users")
            
            # Show first few users for reference
            if user_count > 0:
                sample_users = list(users_collection.find({}, {"email": 1, "full_name": 1, "role": 1}).limit(5))
                print("   Sample users:")
                for u in sample_users:
                    print(f"     - {u.get('email')} ({u.get('role', 'N/A')})")
    
    client.close()
    return False

if __name__ == "__main__":
    check_user_password()