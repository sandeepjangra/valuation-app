"""
Clean up organizations - Remove all test/duplicate organizations
Keep only SK Tindwal as the main working organization
"""
import asyncio
import sys
import os
from datetime import datetime, timezone

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database.multi_db_manager import MultiDatabaseManager

async def clean_organizations():
    """Clean up all organizations except SK Tindwal"""
    
    print("🧹 Cleaning Organizations - Starting Fresh")
    print("="*80)
    
    db_manager = MultiDatabaseManager()
    await db_manager.connect()
    
    try:
        # Get organizations from val_app_config
        config_db = db_manager.client.val_app_config
        orgs_collection = config_db.organizations
        
        # Get all ACTIVE non-system organizations
        print("\n📊 Finding all active organizations...")
        orgs_cursor = orgs_collection.find({
            "is_active": True,
            "is_system_org": {"$ne": True}
        })
        organizations = await orgs_cursor.to_list(length=None)
        
        print(f"Found {len(organizations)} active organizations:\n")
        
        orgs_to_keep = []
        orgs_to_remove = []
        
        for org in organizations:
            org_name = org.get('org_name')
            org_short_name = org.get('org_short_name')
            
            print(f"  - {org_name} ({org_short_name})")
            
            # Keep only SK Tindwal
            if org_short_name == 'sk-tindwal':
                orgs_to_keep.append(org)
            else:
                orgs_to_remove.append(org)
        
        print("\n" + "="*80)
        print("📋 CLEANUP PLAN:")
        print("="*80)
        
        if orgs_to_keep:
            print("\n✅ KEEPING:")
            for org in orgs_to_keep:
                print(f"  - {org.get('org_name')} ({org.get('org_short_name')})")
        
        if orgs_to_remove:
            print("\n❌ REMOVING:")
            for org in orgs_to_remove:
                print(f"  - {org.get('org_name')} ({org.get('org_short_name')})")
        else:
            print("\n✅ No organizations to remove. Database is already clean!")
            return
        
        print("\n" + "="*80)
        
        # Deactivate (soft delete) unwanted organizations
        print("\n🔄 Deactivating unwanted organizations...")
        
        for org in orgs_to_remove:
            org_id = org.get('_id')
            org_name = org.get('org_name')
            org_short_name = org.get('org_short_name')
            
            result = await orgs_collection.update_one(
                {"_id": org_id},
                {
                    "$set": {
                        "is_active": False,
                        "deactivated_at": datetime.now(timezone.utc),
                        "deactivation_reason": "Cleanup - test/duplicate organization removed"
                    }
                }
            )
            
            if result.modified_count > 0:
                print(f"  ✅ Deactivated: {org_name} ({org_short_name})")
            else:
                print(f"  ⚠️  Failed to deactivate: {org_name}")
        
        print("\n" + "="*80)
        print("✅ CLEANUP COMPLETE!")
        print("="*80)
        
        # Verify final state
        print("\n📊 Final active organizations:")
        
        final_cursor = orgs_collection.find({
            "is_active": True,
            "is_system_org": {"$ne": True}
        })
        final_orgs = await final_cursor.to_list(length=None)
        
        if final_orgs:
            for idx, org in enumerate(final_orgs, 1):
                print(f"\n{idx}. {org.get('org_name')}")
                print(f"   Short name: {org.get('org_short_name')}")
                print(f"   Status: Active")
        else:
            print("\n⚠️  No active organizations remaining (except system org)")
        
        print("\n💡 Next steps:")
        print("  1. Refresh frontend at: http://localhost:4200/admin/organizations")
        print("  2. You can now create new organizations cleanly")
        
    finally:
        await db_manager.disconnect()
        print("\n✅ Database connection closed")

if __name__ == "__main__":
    asyncio.run(clean_organizations())
