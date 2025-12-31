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

async def debug_org_context():
    """Debug organization context and reference number setup"""
    
    try:
        from database.multi_db_manager import MultiDatabaseManager
        from services.reference_number_service import ReferenceNumberService
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        print("🔍 Debugging Organization Context Issues")
        print("="*60)
        
        # Check config database organizations
        config_db = await db_manager.get_config_db()
        orgs = await config_db["organizations"].find({}).to_list(length=None)
        
        print(f"📋 Organizations in config database:")
        for org in orgs:
            org_short_name = org.get("org_short_name", "No short name")
            org_name = org.get("org_name", "No name") 
            settings = org.get("settings", {})
            initials = settings.get("report_reference_initials", "None")
            
            print(f"   • {org_short_name}: {org_name}")
            print(f"     - Initials: {initials}")
            print(f"     - Status: {org.get('status', 'No status')}")
            print(f"     - Type: {org.get('org_type', 'No type')}")
            
        print(f"\n🔍 Looking specifically for sk-tindwal:")
        
        # Check for sk-tindwal specifically 
        sk_org = await config_db["organizations"].find_one({
            "org_short_name": "sk-tindwal"
        })
        
        if sk_org:
            print(f"✅ Found sk-tindwal organization:")
            print(f"   • Name: {sk_org.get('org_name')}")
            print(f"   • Status: {sk_org.get('status')}")
            settings = sk_org.get("settings", {})
            initials = settings.get("report_reference_initials")
            print(f"   • Reference Initials: {initials}")
            
            if not initials:
                print(f"⚠️ sk-tindwal is missing reference initials! Fixing...")
                
                # Update with proper settings
                await config_db["organizations"].update_one(
                    {"org_short_name": "sk-tindwal"},
                    {
                        "$set": {
                            "settings.report_reference_initials": "SKT",
                            "settings.report_sequence_counter": 0,
                            "settings.auto_generate_reference": True,
                            "updated_at": "2025-12-21T00:00:00Z"
                        }
                    }
                )
                print(f"✅ Updated sk-tindwal with reference initials: SKT")
            
            # Test reference number generation
            ref_service = ReferenceNumberService(db_manager)
            
            try:
                preview = await ref_service.get_next_reference_preview("sk-tindwal")
                print(f"✅ Next reference number preview for sk-tindwal: {preview['reference_number']}")
            except Exception as e:
                print(f"❌ Error generating reference for sk-tindwal: {e}")
                
            try:
                preview_sys = await ref_service.get_next_reference_preview("system-administration")
                print(f"✅ Next reference number preview for system-administration: {preview_sys['reference_number']}")
            except Exception as e:
                print(f"❌ Error generating reference for system-administration: {e}")
                
        else:
            print(f"❌ sk-tindwal organization NOT found!")
            print(f"   Need to create it first")
            
            # Create sk-tindwal organization
            from datetime import datetime, timezone
            
            sk_tindwal_org = {
                "org_short_name": "sk-tindwal",
                "org_name": "SK Tindwal & Associates",
                "org_type": "valuation_company",
                "status": "active",
                "settings": {
                    "report_reference_initials": "SKT",
                    "report_sequence_counter": 0,
                    "auto_generate_reference": True,
                    "max_users": 25,
                    "plan": "basic"
                },
                "contact_info": {
                    "contact_email": "contact@sktindwal.com",
                    "contact_phone": "",
                    "address": ""
                },
                "subscription": {
                    "plan": "basic",
                    "status": "active",
                    "max_users": 25,
                    "features": ["reports", "templates", "users"]
                },
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            result = await config_db["organizations"].insert_one(sk_tindwal_org)
            print(f"✅ Created sk-tindwal organization with ID: {result.inserted_id}")
        
        await db_manager.disconnect()
        
        print(f"\n🎉 Organization context debugging completed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error debugging org context: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_org_context())
    if success:
        print("\n🎉 Organization debugging completed!")
    else:
        print("\n💥 Organization debugging failed!")
        sys.exit(1)