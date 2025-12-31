#!/usr/bin/env python3
"""
Fix Admin User Password
Simple script to reset admin user password with proper bcrypt handling
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

def fix_admin_password():
    """Fix system admin user password with simple bcrypt"""
    print("🔧 Fixing Admin User Password")
    
    # Connect to MongoDB
    client = MongoClient(os.environ["MONGODB_URI"])
    admin_db = client["valuation_admin"]
    users_collection = admin_db["users"]
    
    # Simple password hashing with bcrypt
    password = "admin123"
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    print(f"📝 New password hash: {password_hash[:50]}...")
    
    # Update admin user
    result = users_collection.update_one(
        {"email": "admin@system.com"},
        {
            "$set": {
                "password_hash": password_hash,
                "updated_at": datetime.now(timezone.utc)
            }
        },
        upsert=True
    )
    
    if result.upserted_id:
        print("✅ Created new admin user")
        # Also create the user record with proper structure
        users_collection.update_one(
            {"email": "admin@system.com"},
            {
                "$set": {
                    "full_name": "System Administrator",
                    "role": "admin",
                    "is_system_admin": True,
                    "org_short_name": "system-administration",
                    "organization_id": "69230378b621a5665cd8d160",
                    "organization_name": "System Administration",
                    "is_active": True,
                    "created_at": datetime.now(timezone.utc)
                }
            }
        )
    else:
        print("✅ Updated existing admin user password")
    
    print("🔐 Admin user ready: admin@system.com / admin123")
    
    client.close()

if __name__ == "__main__":
    fix_admin_password()