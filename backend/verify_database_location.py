#!/usr/bin/env python3
"""
Verify template location in database directly
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Load environment variables
from dotenv import load_dotenv
env_path = backend_dir / '.env'
load_dotenv(dotenv_path=env_path)

from database.multi_db_manager import MultiDatabaseManager

async def verify_template_locations():
    """Check where templates are stored in the database"""
    
    print("🔍 Verifying Template Database Locations")
    print("=" * 50)
    
    try:
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        # Check sk-tindwal database
        sk_db = db_manager.get_org_database("sk-tindwal")
        sk_templates = await sk_db.custom_templates.find({"isActive": True}).to_list(length=None)
        
        print(f"📋 sk-tindwal database:")
        print(f"   Templates found: {len(sk_templates)}")
        for template in sk_templates[-3:]:  # Show last 3
            print(f"   - {template.get('templateName')} (ID: {str(template['_id'])})")
            print(f"     Created by: {template.get('createdByName')}")
            print(f"     Org ID: {template.get('organizationId')}")
        
        # Check system-administration database
        try:
            sys_db = db_manager.get_org_database("system-administration")
            sys_templates = await sys_db.custom_templates.find({"isActive": True}).to_list(length=None)
            
            print(f"\n📋 system-administration database:")
            print(f"   Templates found: {len(sys_templates)}")
            for template in sys_templates[-3:]:  # Show last 3
                print(f"   - {template.get('templateName')} (ID: {str(template['_id'])})")
                print(f"     Created by: {template.get('createdByName')}")
                print(f"     Org ID: {template.get('organizationId')}")
        except Exception as e:
            print(f"\n📋 system-administration database: Not accessible or empty ({e})")
        
        await db_manager.disconnect()
        
        print(f"\n✅ Database verification complete!")
        
        if len(sk_templates) > 0:
            latest_sk = sk_templates[-1]
            if latest_sk.get('createdByName') == 'admin@system.com':
                print(f"🎉 SUCCESS: Latest template in sk-tindwal was created by admin@system.com")
                print(f"   This confirms admin templates are going to the correct organization!")
            else:
                print(f"ℹ️ Latest template in sk-tindwal was created by: {latest_sk.get('createdByName')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database verification failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(verify_template_locations())