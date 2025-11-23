"""
Clean up unnecessary organizations from val_app_config database
This script will:
1. Show all current organizations
2. Allow you to select which ones to keep
3. Deactivate (soft delete) the rest
"""
import asyncio
import sys
import os

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database.multi_db_manager import MultiDatabaseManager

async def cleanup_organizations():
    """Clean up unnecessary organizations"""
    
    print("🧹 Organization Cleanup Tool")
    print("="*80)
    
    db_manager = MultiDatabaseManager()
    await db_manager.connect()
    
    try:
        # Get organizations from val_app_config
        config_db = db_manager.client.val_app_config
        orgs_collection = config_db.organizations
        
        # Get all ACTIVE non-system organizations
        orgs_cursor = orgs_collection.find({
            "is_active": True,
            "is_system_org": {"$ne": True}
        })
        organizations = await orgs_cursor.to_list(length=None)
        
        print(f"\n📊 Found {len(organizations)} active organizations:\n")
        
        for idx, org in enumerate(organizations, 1):
            print(f"\n{idx}. {org.get('org_name')}")
            print(f"   Short name: {org.get('org_short_name')}")
            print(f"   ID: {org.get('_id')}")
            print(f"   Created: {org.get('created_at')}")
            
            # Show organization_id from metadata if exists
            metadata = org.get('metadata', {})
            if 'original_organization_id' in metadata:
                print(f"   Original org ID: {metadata['original_organization_id']}")
        
        print("\n" + "="*80)
        print("\n🎯 RECOMMENDATIONS:")
        print("\n✅ KEEP: SK Tindwal (sk-tindwal) - Your main working organization")
        print("\n❌ REMOVE:")
        print("   - Test Company Inc (test-company-inc) - Test organization")
        print("   - Valuation (valuation) - Legacy/duplicate organization")
        print("   - ABC Property Valuers (abc-property-valuers) - Test organization")
        
        print("\n" + "="*80)
        print("\n⚠️  OPTIONS:")
        print("1. Remove all except SK Tindwal (RECOMMENDED)")
        print("2. Manually select organizations to keep")
        print("3. Cancel (no changes)")
        
        choice = input("\nEnter your choice (1/2/3): ").strip()
        
        if choice == "3":
            print("\n✅ No changes made. Exiting...")
            return
        
        orgs_to_keep = []
        
        if choice == "1":
            # Keep only SK Tindwal
            orgs_to_keep = ["sk-tindwal"]
            print("\n✅ Will keep only: SK Tindwal")
        
        elif choice == "2":
            # Manual selection
            print("\n📝 Enter the numbers of organizations to KEEP (comma-separated):")
            keep_input = input("Keep: ").strip()
            keep_indices = [int(x.strip()) - 1 for x in keep_input.split(",") if x.strip()]
            
            for idx in keep_indices:
                if 0 <= idx < len(organizations):
                    orgs_to_keep.append(organizations[idx].get('org_short_name'))
            
            print(f"\n✅ Will keep: {', '.join(orgs_to_keep)}")
        
        else:
            print("\n❌ Invalid choice. Exiting...")
            return
        
        # Confirm action
        print("\n" + "="*80)
        print("⚠️  FINAL CONFIRMATION")
        print("="*80)
        print(f"\nOrganizations to KEEP (remain active): {', '.join(orgs_to_keep)}")
        
        orgs_to_deactivate = [
            org for org in organizations 
            if org.get('org_short_name') not in orgs_to_keep
        ]
        
        if orgs_to_deactivate:
            print(f"\nOrganizations to DEACTIVATE (soft delete):")
            for org in orgs_to_deactivate:
                print(f"  - {org.get('org_name')} ({org.get('org_short_name')})")
        else:
            print("\n✅ No organizations will be deactivated.")
            return
        
        confirm = input("\n⚠️  Proceed with deactivation? (yes/no): ").strip().lower()
        
        if confirm != "yes":
            print("\n✅ No changes made. Exiting...")
            return
        
        # Deactivate organizations
        print("\n🔄 Deactivating organizations...")
        
        for org in orgs_to_deactivate:
            org_id = org.get('_id')
            org_name = org.get('org_name')
            
            result = await orgs_collection.update_one(
                {"_id": org_id},
                {
                    "$set": {
                        "is_active": False,
                        "deactivated_at": asyncio.get_event_loop().time(),
                        "deactivation_reason": "Cleanup - unnecessary test/duplicate organization"
                    }
                }
            )
            
            if result.modified_count > 0:
                print(f"  ✅ Deactivated: {org_name}")
            else:
                print(f"  ⚠️  Failed to deactivate: {org_name}")
        
        print("\n" + "="*80)
        print("✅ CLEANUP COMPLETE!")
        print("="*80)
        
        # Show final state
        print("\n📊 Final organization list (active only):")
        
        final_cursor = orgs_collection.find({
            "is_active": True,
            "is_system_org": {"$ne": True}
        })
        final_orgs = await final_cursor.to_list(length=None)
        
        for idx, org in enumerate(final_orgs, 1):
            print(f"{idx}. {org.get('org_name')} ({org.get('org_short_name')})")
        
        print("\n💡 Refresh your frontend at http://localhost:4200/admin/organizations to see the changes")
        
    finally:
        await db_manager.disconnect()
        print("\n✅ Database connection closed")

if __name__ == "__main__":
    asyncio.run(cleanup_organizations())
