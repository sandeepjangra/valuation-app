#!/usr/bin/env python3
"""
Reset User Password
Script to reset password for sk.tindwal@gmail.com
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

def reset_user_password():
    """Reset password for sk.tindwal@gmail.com"""
    print("🔧 Resetting User Password")
    
    # Connect to MongoDB
    client = MongoClient(os.environ["MONGODB_URI"])
    admin_db = client["valuation_admin"]
    users_collection = admin_db["users"]
    
    email = "sk.tindwal@gmail.com"
    new_password = "user123"  # Setting a known password
    
    # Simple password hashing with bcrypt
    password_bytes = new_password.encode('utf-8')
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    print(f"📝 Resetting password for: {email}")
    print(f"🔑 New password: {new_password}")
    print(f"📝 New password hash: {password_hash[:50]}...")
    
    # Update user password
    result = users_collection.update_one(
        {"email": email},
        {
            "$set": {
                "password_hash": password_hash,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    if result.matched_count > 0:
        print("✅ Password updated successfully")
        print(f"🔐 User can now login with: {email} / {new_password}")
    else:
        print("❌ User not found")
    
    client.close()

if __name__ == "__main__":
    reset_user_password()