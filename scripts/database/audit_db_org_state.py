"""
Audit Database and Organization State
Check for mismatches between organizations and databases
"""
import asyncio
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database.multi_db_manager import MultiDatabaseManager

# System databases that must never be deleted
PROTECTED_DATABASES = ['val_app_config', 'valuation_admin', 'shared_resources', 'admin', 'local', 'config']

async def audit_state():
    """Audit current state of databases and organizations"""
    
    print("🔍 DATABASE & ORGANIZATION AUDIT")
    print("="*80)
    
    db_manager = MultiDatabaseManager()
    await db_manager.connect()
    
    try:
        # 1. Get all databases
        print("\n📊 STEP 1: Listing all databases...")
        all_databases = await db_manager.client.list_database_names()
        
        print(f"\nFound {len(all_databases)} total databases:")
        for db_name in sorted(all_databases):
            is_protected = db_name in PROTECTED_DATABASES
            protection = "🔒 PROTECTED" if is_protected else ""
            print(f"  - {db_name} {protection}")
        
        # 2. Get all organizations
        print("\n📊 STEP 2: Listing all organizations...")
        config_db = db_manager.client.val_app_config
        orgs_collection = config_db.organizations
        
        all_orgs = await orgs_collection.find({}).to_list(length=None)
        active_orgs = [org for org in all_orgs if org.get('is_active', True)]
        inactive_orgs = [org for org in all_orgs if not org.get('is_active', True)]
        
        print(f"\nFound {len(all_orgs)} total organizations:")
        print(f"  - Active: {len(active_orgs)}")
        print(f"  - Inactive: {len(inactive_orgs)}")
        
        print("\nActive Organizations:")
        for org in active_orgs:
            print(f"  ✅ {org.get('org_name')} ({org.get('org_short_name')})")
        
        if inactive_orgs:
            print("\nInactive Organizations:")
            for org in inactive_orgs:
                print(f"  ❌ {org.get('org_name')} ({org.get('org_short_name')})")
        
        # 3. Find org databases (exclude system databases)
        print("\n📊 STEP 3: Identifying organization databases...")
        org_databases = [db for db in all_databases if db not in PROTECTED_DATABASES]
        
        print(f"\nFound {len(org_databases)} organization databases:")
        for db_name in sorted(org_databases):
            print(f"  - {db_name}")
        
        # 4. Check for mismatches
        print("\n" + "="*80)
        print("🔍 MISMATCH ANALYSIS")
        print("="*80)
        
        # 4a. Organizations without databases
        print("\n⚠️  Organizations WITHOUT databases:")
        orgs_without_db = []
        for org in active_orgs:
            org_short_name = org.get('org_short_name')
            if org_short_name not in all_databases:
                orgs_without_db.append(org)
                print(f"  ❌ {org.get('org_name')} ({org_short_name}) - MISSING DATABASE!")
        
        if not orgs_without_db:
            print("  ✅ All active organizations have databases")
        
        # 4b. Databases without organizations
        print("\n⚠️  Databases WITHOUT active organizations:")
        dbs_without_org = []
        org_short_names = [org.get('org_short_name') for org in active_orgs]
        
        for db_name in org_databases:
            if db_name not in org_short_names:
                dbs_without_org.append(db_name)
                print(f"  ❌ {db_name} - ORPHANED DATABASE!")
        
        if not dbs_without_org:
            print("  ✅ All organization databases have active organizations")
        
        # 5. Recommendations
        print("\n" + "="*80)
        print("💡 RECOMMENDATIONS")
        print("="*80)
        
        if orgs_without_db:
            print("\n🔧 Organizations needing database creation:")
            for org in orgs_without_db:
                print(f"  → Create database: {org.get('org_short_name')}")
                print(f"     For organization: {org.get('org_name')}")
        
        if dbs_without_org:
            print("\n🗑️  Orphaned databases to delete:")
            for db_name in dbs_without_org:
                # Check if it's an inactive org's database
                inactive_org = next(
                    (org for org in inactive_orgs if org.get('org_short_name') == db_name),
                    None
                )
                if inactive_org:
                    print(f"  → Delete database: {db_name}")
                    print(f"     (Belongs to deactivated org: {inactive_org.get('org_name')})")
                else:
                    print(f"  → Delete database: {db_name}")
                    print(f"     (No organization found)")
        
        # 6. Summary
        print("\n" + "="*80)
        print("📋 SUMMARY")
        print("="*80)
        print(f"\nProtected Databases: {len([db for db in all_databases if db in PROTECTED_DATABASES])}")
        print(f"Organization Databases: {len(org_databases)}")
        print(f"Active Organizations: {len(active_orgs)}")
        print(f"Inactive Organizations: {len(inactive_orgs)}")
        print(f"\nMismatches:")
        print(f"  - Organizations without DB: {len(orgs_without_db)}")
        print(f"  - Databases without org: {len(dbs_without_org)}")
        
        # Return results for automated fixing
        return {
            'orgs_without_db': orgs_without_db,
            'dbs_without_org': dbs_without_org,
            'all_databases': all_databases,
            'protected_databases': PROTECTED_DATABASES
        }
        
    finally:
        await db_manager.disconnect()
        print("\n✅ Audit complete")

if __name__ == "__main__":
    asyncio.run(audit_state())
