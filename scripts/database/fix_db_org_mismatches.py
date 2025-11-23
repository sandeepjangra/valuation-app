"""
Fix Database and Organization Mismatches
1. Delete orphaned databases (abc-property-valuers, test-valuation-services)
2. Create missing databases (system-administration, sk-tindwal)
3. Ensure data integrity
"""
import asyncio
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database.multi_db_manager import MultiDatabaseManager

# System databases that must never be deleted
PROTECTED_DATABASES = ['val_app_config', 'valuation_admin', 'shared_resources', 'admin', 'local', 'config']

async def fix_mismatches():
    """Fix all database and organization mismatches"""
    
    print("🔧 FIXING DATABASE & ORGANIZATION MISMATCHES")
    print("="*80)
    
    db_manager = MultiDatabaseManager()
    await db_manager.connect()
    
    try:
        config_db = db_manager.client.val_app_config
        orgs_collection = config_db.organizations
        
        # Get all organizations
        all_orgs = await orgs_collection.find({}).to_list(length=None)
        active_orgs = [org for org in all_orgs if org.get('is_active', True)]
        
        # Get all databases
        all_databases = await db_manager.client.list_database_names()
        org_databases = [db for db in all_databases if db not in PROTECTED_DATABASES]
        
        print("\n" + "="*80)
        print("STEP 1: Delete orphaned databases")
        print("="*80)
        
        # Find orphaned databases
        org_short_names = [org.get('org_short_name') for org in active_orgs]
        orphaned_dbs = [db for db in org_databases if db not in org_short_names]
        
        if orphaned_dbs:
            for db_name in orphaned_dbs:
                print(f"\n🗑️  Deleting orphaned database: {db_name}")
                
                # Safety check - never delete protected databases
                if db_name in PROTECTED_DATABASES:
                    print(f"   ⚠️  SKIPPED - Protected database!")
                    continue
                
                # Check if belongs to inactive org
                inactive_org = next(
                    (org for org in all_orgs if org.get('org_short_name') == db_name and not org.get('is_active', True)),
                    None
                )
                
                if inactive_org:
                    print(f"   📝 Belongs to deactivated org: {inactive_org.get('org_name')}")
                
                # Drop the database
                await db_manager.client.drop_database(db_name)
                print(f"   ✅ Deleted database: {db_name}")
        else:
            print("\n✅ No orphaned databases found")
        
        print("\n" + "="*80)
        print("STEP 2: Create missing databases for active organizations")
        print("="*80)
        
        # Find orgs without databases
        orgs_without_db = []
        for org in active_orgs:
            org_short_name = org.get('org_short_name')
            if org_short_name not in all_databases:
                orgs_without_db.append(org)
        
        if orgs_without_db:
            for org in orgs_without_db:
                org_short_name = org.get('org_short_name')
                org_name = org.get('org_name')
                
                print(f"\n🏗️  Creating database for: {org_name} ({org_short_name})")
                
                # Use the database manager's method to ensure proper structure
                success = await db_manager.ensure_org_database_structure(org_short_name)
                
                if success:
                    print(f"   ✅ Database created: {org_short_name}")
                    print(f"      - Collections initialized")
                    print(f"      - Indexes created")
                else:
                    print(f"   ❌ Failed to create database: {org_short_name}")
        else:
            print("\n✅ All active organizations have databases")
        
        # Verify final state
        print("\n" + "="*80)
        print("STEP 3: Verify final state")
        print("="*80)
        
        # Re-check databases
        final_databases = await db_manager.client.list_database_names()
        final_org_databases = [db for db in final_databases if db not in PROTECTED_DATABASES]
        
        print(f"\n📊 Final database count:")
        print(f"   - Protected databases: {len([db for db in final_databases if db in PROTECTED_DATABASES])}")
        print(f"   - Organization databases: {len(final_org_databases)}")
        
        print(f"\n📊 Organization databases:")
        for db_name in sorted(final_org_databases):
            # Find corresponding org
            org = next(
                (o for o in active_orgs if o.get('org_short_name') == db_name),
                None
            )
            if org:
                print(f"   ✅ {db_name} → {org.get('org_name')}")
            else:
                print(f"   ⚠️  {db_name} → NO ORG FOUND!")
        
        # Check for any remaining mismatches
        remaining_orgs_without_db = []
        for org in active_orgs:
            if org.get('org_short_name') not in final_databases:
                remaining_orgs_without_db.append(org)
        
        remaining_dbs_without_org = []
        for db in final_org_databases:
            if db not in [o.get('org_short_name') for o in active_orgs]:
                remaining_dbs_without_org.append(db)
        
        print("\n" + "="*80)
        print("✅ FIX COMPLETE!")
        print("="*80)
        
        if remaining_orgs_without_db or remaining_dbs_without_org:
            print("\n⚠️  WARNING: Some mismatches remain!")
            if remaining_orgs_without_db:
                print(f"   - Organizations without DB: {len(remaining_orgs_without_db)}")
            if remaining_dbs_without_org:
                print(f"   - Databases without org: {len(remaining_dbs_without_org)}")
        else:
            print("\n🎉 All databases and organizations are now in sync!")
            print("\nActive Organizations:")
            for org in active_orgs:
                print(f"   ✅ {org.get('org_name')} ({org.get('org_short_name')})")
        
    finally:
        await db_manager.disconnect()
        print("\n✅ Database connection closed")

if __name__ == "__main__":
    asyncio.run(fix_mismatches())
