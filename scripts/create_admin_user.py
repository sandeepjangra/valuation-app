#!/usr/bin/env python3
"""
Create System Admin User
Creates the system admin user in valuation_admin.users collection for traditional login
"""

import asyncio
import sys
import os
from datetime import datetime, timezone

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database.multi_db_manager import MultiDatabaseManager
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin_user():
    """Create system admin user"""
    print("=" * 70)
    print("🔐 Creating System Admin User")
    print("=" * 70)
    
    db_manager = MultiDatabaseManager()
    
    try:
        await db_manager.connect()
        print("✅ Connected to MongoDB")
        
        admin_db = db_manager.get_database("admin")
        
        # Check if admin user already exists
        existing_admin = await admin_db.users.find_one({"email": "admin@system.com"})
        
        if existing_admin:
            print("⚠️  Admin user already exists!")
            print(f"   Email: {existing_admin.get('email')}")
            print(f"   User ID: {existing_admin.get('user_id')}")
            print(f"   Role: {existing_admin.get('role')}")
            return
        
        # Create admin user
        admin_user = {
            "user_id": "user_system_admin_001",
            "email": "admin@system.com",
            "full_name": "System Administrator",
            "phone": "",
            "password_hash": pwd_context.hash("admin123"),  # Default password
            "organization_id": "system_admin",
            "role": "system_admin",
            "is_active": True,
            "created_by": "system",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "last_login": None
        }
        
        result = await admin_db.users.insert_one(admin_user)
        print(f"\n✅ Admin user created successfully!")
        print(f"   Email: admin@system.com")
        print(f"   Password: admin123")
        print(f"   User ID: user_system_admin_001")
        print(f"   MongoDB _id: {result.inserted_id}")
        
        print("\n📝 You can now login using:")
        print("   Method 1: Development Quick Login → System Admin button")
        print("   Method 2: Email/Password form → admin@system.com / admin123")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await db_manager.disconnect()
        print("\n✅ Done!")

if __name__ == "__main__":
    asyncio.run(create_admin_user())
