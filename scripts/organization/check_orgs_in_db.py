"""
Check all organizations in val_app_config database
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime

async def check_organizations():
    """Check all organizations in the database"""
    
    # Get connection string
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    
    print(f"🔗 Connecting to: {mongodb_uri}")
    client = AsyncIOMotorClient(mongodb_uri)
    
    try:
        # Get val_app_config database
        config_db = client.val_app_config
        orgs_collection = config_db.organizations
        
        # Get ALL organizations (including inactive and system)
        print("\n" + "="*80)
        print("ALL ORGANIZATIONS IN DATABASE (including inactive and system)")
        print("="*80 + "\n")
        
        orgs_cursor = orgs_collection.find({})
        all_orgs = await orgs_cursor.to_list(length=None)
        
        print(f"📊 Total organizations found: {len(all_orgs)}\n")
        
        for idx, org in enumerate(all_orgs, 1):
            print(f"\n{'─'*80}")
            print(f"Organization #{idx}")
            print(f"{'─'*80}")
            print(f"  _id: {org['_id']}")
            print(f"  org_name: {org.get('org_name', 'N/A')}")
            print(f"  org_short_name: {org.get('org_short_name', 'N/A')}")
            print(f"  is_active: {org.get('is_active', 'N/A')}")
            print(f"  is_system_org: {org.get('is_system_org', 'N/A')}")
            
            # Check if it has old organization_id in metadata
            metadata = org.get('metadata', {})
            if 'original_organization_id' in metadata:
                print(f"  original_organization_id: {metadata['original_organization_id']}")
            
            # Show contact info
            contact_info = org.get('contact_info', {})
            if contact_info:
                print(f"  Contact: {contact_info}")
            
            # Show settings
            settings = org.get('settings', {})
            if settings:
                print(f"  Settings keys: {list(settings.keys())}")
            
            # Show dates
            if 'created_at' in org:
                print(f"  created_at: {org['created_at']}")
            if 'updated_at' in org:
                print(f"  updated_at: {org['updated_at']}")
        
        # Now check which ones are shown by the API
        print("\n" + "="*80)
        print("ORGANIZATIONS RETURNED BY API (is_active=True, is_system_org!=True)")
        print("="*80 + "\n")
        
        api_orgs_cursor = orgs_collection.find({
            "is_active": True,
            "is_system_org": {"$ne": True}
        })
        api_orgs = await api_orgs_cursor.to_list(length=None)
        
        print(f"📊 Organizations shown in API: {len(api_orgs)}\n")
        
        for idx, org in enumerate(api_orgs, 1):
            print(f"{idx}. {org.get('org_name', 'N/A')} ({org.get('org_short_name', 'N/A')})")
        
        # Check for any inactive organizations
        print("\n" + "="*80)
        print("INACTIVE ORGANIZATIONS")
        print("="*80 + "\n")
        
        inactive_cursor = orgs_collection.find({"is_active": False})
        inactive_orgs = await inactive_cursor.to_list(length=None)
        
        if inactive_orgs:
            print(f"📊 Found {len(inactive_orgs)} inactive organizations:\n")
            for org in inactive_orgs:
                print(f"  - {org.get('org_name', 'N/A')} ({org.get('org_short_name', 'N/A')})")
        else:
            print("✅ No inactive organizations found")
        
        # Check for system organizations
        print("\n" + "="*80)
        print("SYSTEM ORGANIZATIONS")
        print("="*80 + "\n")
        
        system_cursor = orgs_collection.find({"is_system_org": True})
        system_orgs = await system_cursor.to_list(length=None)
        
        if system_orgs:
            print(f"📊 Found {len(system_orgs)} system organizations:\n")
            for org in system_orgs:
                print(f"  - {org.get('org_name', 'N/A')} ({org.get('org_short_name', 'N/A')})")
        else:
            print("✅ No system organizations found")
        
    finally:
        client.close()
        print("\n✅ Connection closed")

if __name__ == "__main__":
    asyncio.run(check_organizations())
