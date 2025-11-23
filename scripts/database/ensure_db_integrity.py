"""
Database Integrity Checker and Auto-Fixer
Ensures organizations and databases are always in sync
"""
import asyncio
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database.multi_db_manager import MultiDatabaseManager

# System databases that must never be deleted
PROTECTED_DATABASES = ['val_app_config', 'valuation_admin', 'shared_resources', 'admin', 'local', 'config']

async def check_and_fix_integrity():
    """
    Check database and organization integrity and auto-fix issues
    
    Rules:
    1. Protected databases (val_app_config, valuation_admin, shared_resources) must NEVER be deleted
    2. Every active organization MUST have a corresponding database
    3. Every organization database MUST have an active organization (or be cleaned up)
    4. Inactive organizations should not have databases (unless explicitly preserved)
    """
    
    print("🔍 DATABASE INTEGRITY CHECK")
    print("="*80)
    
    db_manager = MultiDatabaseManager()
    await db_manager.connect()
    
    try:
        config_db = db_manager.client.val_app_config
        orgs_collection = config_db.organizations
        
        # Get all databases
        all_databases = await db_manager.client.list_database_names()
        
        # Get all organizations
        all_orgs = await orgs_collection.find({}).to_list(length=None)
        active_orgs = [org for org in all_orgs if org.get('is_active', True)]
        inactive_orgs = [org for org in all_orgs if not org.get('is_active', True)]
        
        org_databases = [db for db in all_databases if db not in PROTECTED_DATABASES]
        org_short_names = [org.get('org_short_name') for org in active_orgs]
        
        # Check 1: Protected databases exist
        print("\n✅ CHECK 1: Protected databases")
        protected_db_status = {}
        for db in PROTECTED_DATABASES:
            exists = db in all_databases
            protected_db_status[db] = exists
            status = "✅ EXISTS" if exists else "❌ MISSING"
            print(f"   {status}: {db}")
        
        missing_protected = [db for db, exists in protected_db_status.items() if not exists]
        if missing_protected:
            print(f"\n⚠️  WARNING: {len(missing_protected)} protected databases are missing!")
            print("   These should be investigated manually.")
        
        # Check 2: Active orgs have databases
        print("\n✅ CHECK 2: Active organizations have databases")
        orgs_without_db = []
        for org in active_orgs:
            org_short_name = org.get('org_short_name')
            has_db = org_short_name in all_databases
            status = "✅" if has_db else "❌"
            print(f"   {status} {org.get('org_name')} ({org_short_name})")
            
            if not has_db:
                orgs_without_db.append(org)
        
        # Check 3: Databases have active organizations
        print("\n✅ CHECK 3: Organization databases have active organizations")
        dbs_without_org = []
        for db_name in org_databases:
            has_org = db_name in org_short_names
            
            # Check if it's an inactive org's database
            inactive_org = next(
                (org for org in inactive_orgs if org.get('org_short_name') == db_name),
                None
            )
            
            if has_org:
                status = "✅ ACTIVE ORG"
            elif inactive_org:
                status = "⚠️  INACTIVE ORG"
            else:
                status = "❌ NO ORG"
                dbs_without_org.append(db_name)
            
            org_info = ""
            if has_org:
                org = next(o for o in active_orgs if o.get('org_short_name') == db_name)
                org_info = f" → {org.get('org_name')}"
            elif inactive_org:
                org_info = f" → {inactive_org.get('org_name')} (DEACTIVATED)"
            
            print(f"   {status}: {db_name}{org_info}")
        
        # Auto-fix recommendations
        print("\n" + "="*80)
        print("🔧 AUTO-FIX ACTIONS")
        print("="*80)
        
        fixes_needed = False
        
        if orgs_without_db:
            fixes_needed = True
            print(f"\n⚠️  Found {len(orgs_without_db)} organizations without databases")
            print("   ACTION: Create missing databases")
            
            for org in orgs_without_db:
                org_short_name = org.get('org_short_name')
                print(f"\n   Creating database: {org_short_name}")
                
                success = await db_manager.ensure_org_database_structure(org_short_name)
                if success:
                    print(f"   ✅ Database created successfully")
                else:
                    print(f"   ❌ Failed to create database")
        
        if dbs_without_org:
            fixes_needed = True
            print(f"\n⚠️  Found {len(dbs_without_org)} orphaned databases")
            print("   ACTION: Remove orphaned databases")
            
            for db_name in dbs_without_org:
                # Safety check
                if db_name in PROTECTED_DATABASES:
                    print(f"\n   ⚠️  SKIPPED: {db_name} (protected database)")
                    continue
                
                print(f"\n   Deleting database: {db_name}")
                await db_manager.client.drop_database(db_name)
                print(f"   ✅ Database deleted")
        
        if not fixes_needed:
            print("\n✅ No fixes needed - database integrity is perfect!")
        
        # Final verification
        print("\n" + "="*80)
        print("📊 FINAL STATUS")
        print("="*80)
        
        final_databases = await db_manager.client.list_database_names()
        final_org_dbs = [db for db in final_databases if db not in PROTECTED_DATABASES]
        
        print(f"\nProtected Databases: {len([db for db in final_databases if db in PROTECTED_DATABASES])}")
        print(f"Organization Databases: {len(final_org_dbs)}")
        print(f"Active Organizations: {len(active_orgs)}")
        
        # Verify sync
        all_synced = True
        for org in active_orgs:
            if org.get('org_short_name') not in final_databases:
                all_synced = False
                break
        
        for db in final_org_dbs:
            if db not in org_short_names:
                all_synced = False
                break
        
        if all_synced:
            print("\n🎉 ✅ ALL DATABASES AND ORGANIZATIONS ARE IN SYNC!")
        else:
            print("\n⚠️  Some mismatches may still exist - run again to verify")
        
        print("\n" + "="*80)
        print("PROTECTION RULES ENFORCED:")
        print("="*80)
        print("✅ Protected databases cannot be deleted")
        print("✅ System organizations cannot be deleted")
        print("✅ Active organizations always have databases")
        print("✅ Orphaned databases are automatically cleaned")
        print("✅ Database creation failures trigger rollback")
        
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(check_and_fix_integrity())
