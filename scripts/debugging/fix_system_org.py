#!/usr/bin/env python3

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Load environment variables
env_path = Path(__file__).parent / "backend" / ".env"
load_dotenv(dotenv_path=env_path)

async def restore_system_organization():
    """Restore system administration organization with proper configuration after deletion"""
    
    try:
        from database.multi_db_manager import MultiDatabaseManager
        from datetime import datetime, timezone
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        print("🔧 Restoring System Administration organization configuration...")
        print("="*60)
        
        # Get config database
        config_db = await db_manager.get_config_db()
        
        # Check if system-administration organization exists
        existing_org = await config_db["organizations"].find_one({
            "org_short_name": "system-administration"
        })
        
        if existing_org:
            print(f"✅ Found existing system-administration organization")
            
            # Check if it has report_reference_initials
            settings = existing_org.get("settings", {})
            initials = settings.get("report_reference_initials")
            
            if not initials:
                print(f"⚠️ Missing report_reference_initials, updating...")
                
                # Update with proper settings
                await config_db["organizations"].update_one(
                    {"org_short_name": "system-administration"},
                    {
                        "$set": {
                            "settings.report_reference_initials": "SYSADM",
                            "settings.report_sequence_counter": 0,
                            "settings.auto_generate_reference": True,
                            "updated_at": datetime.now(timezone.utc)
                        }
                    }
                )
                print(f"✅ Updated system-administration with reference initials: SYSADM")
            else:
                print(f"✅ System org already has initials: {initials}")
        else:
            print(f"❌ System-administration organization not found, creating...")
            
            # Create system administration organization
            system_org = {
                "org_short_name": "system-administration",
                "org_name": "System Administration",
                "org_type": "system",
                "is_system_org": True,
                "status": "active",
                "settings": {
                    "report_reference_initials": "SYSADM",
                    "report_sequence_counter": 0,
                    "auto_generate_reference": True,
                    "max_users": 50,
                    "plan": "system"
                },
                "contact_info": {
                    "contact_email": "admin@system.com",
                    "contact_phone": "",
                    "address": ""
                },
                "subscription": {
                    "plan": "system",
                    "status": "active",
                    "max_users": 50,
                    "features": ["unlimited_reports", "admin_access", "system_management"]
                },
                "metadata": {
                    "created_via": "system_restore_script",
                    "original_organization_id": "system-administration"
                },
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            result = await config_db["organizations"].insert_one(system_org)
            print(f"✅ Created system-administration organization with ID: {result.inserted_id}")
        
        # Also check/create system-administration database with users collection
        sys_db = db_manager.get_org_database("system-administration")
        
        # Check if admin user exists
        admin_user = await sys_db["users"].find_one({"email": "admin@system.com"})
        
        if not admin_user:
            print(f"⚠️ Admin user not found, creating...")
            
            # Create admin user
            import bcrypt
            hashed_password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            admin_user_doc = {
                "email": "admin@system.com",
                "first_name": "System",
                "last_name": "Administrator", 
                "full_name": "System Administrator",
                "password_hash": hashed_password,
                "role": "admin",
                "organization_id": "system-administration",
                "is_system_admin": True,
                "is_active": True,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            result = await sys_db["users"].insert_one(admin_user_doc)
            print(f"✅ Created admin user with ID: {result.inserted_id}")
            print(f"   📧 Email: admin@system.com")
            print(f"   🔑 Password: admin123")
        else:
            print(f"✅ Admin user already exists: {admin_user.get('email')}")
        
        # Create indexes if they don't exist
        try:
            await config_db["organizations"].create_index("org_short_name", unique=True)
            await sys_db["users"].create_index("email", unique=True)
            print(f"✅ Created database indexes")
        except Exception as e:
            print(f"⚠️ Indexes might already exist: {e}")
        
        await db_manager.disconnect()
        
        print(f"\n🎉 System organization restoration completed!")
        print(f"\n📋 Configuration Summary:")
        print(f"   • Organization: system-administration")
        print(f"   • Reference Initials: SYSADM")
        print(f"   • Admin Email: admin@system.com")
        print(f"   • Admin Password: admin123")
        print(f"\n✅ You can now create reports without reference number errors!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error restoring system organization: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(restore_system_organization())
    if success:
        print("\n🎉 System restoration completed successfully!")
    else:
        print("\n💥 System restoration failed!")
        sys.exit(1)