"""
Migration Script: Copy organizations from valuation_admin to val_app_config with new schema
This script migrates SK Tindwal and Valuation organizations while preserving all data.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URI")  # Changed from MONGODB_URL to MONGODB_URI

def create_org_short_name(organization_id: str) -> str:
    """Convert organization_id to org_short_name (URL-safe slug)"""
    # Remove _001 suffix if present
    name = organization_id.replace('_001', '')
    # Replace underscores with hyphens
    return name.replace('_', '-')

async def migrate_organizations():
    # Connect with SSL configuration for macOS
    client = AsyncIOMotorClient(
        MONGODB_URL,
        tlsAllowInvalidCertificates=True  # For development; use proper certs in production
    )
    
    try:
        # Source: valuation_admin.organizations
        source_db = client.valuation_admin
        source_collection = source_db.organizations
        
        # Target: val_app_config.organizations
        target_db = client.val_app_config
        target_collection = target_db.organizations
        
        print("=" * 80)
        print("ORGANIZATION MIGRATION: valuation_admin → val_app_config")
        print("=" * 80)
        
        # Fetch all organizations from source
        orgs = await source_collection.find({}).to_list(length=None)
        print(f"\n✓ Found {len(orgs)} organizations in valuation_admin")
        
        # Organizations to migrate (exclude system_admin as it already exists)
        orgs_to_migrate = [org for org in orgs if org.get('organization_id') != 'system_admin']
        
        print(f"✓ Organizations to migrate: {len(orgs_to_migrate)}")
        
        for org in orgs_to_migrate:
            org_id = org.get('organization_id')
            org_name = org.get('name')
            org_short_name = create_org_short_name(org_id)
            
            print(f"\n{'-' * 80}")
            print(f"Migrating: {org_name} ({org_id})")
            print(f"New short name: {org_short_name}")
            
            # Check if already exists
            existing = await target_collection.find_one({"org_short_name": org_short_name})
            if existing:
                print(f"⚠️  Already exists in val_app_config, skipping...")
                continue
            
            # Map old schema to new schema
            new_org = {
                "org_name": org_name,
                "org_short_name": org_short_name,
                "org_display_name": org_name,
                "is_system_org": False,
                "is_active": org.get('status') == 'active',
                "created_at": org.get('created_at', datetime.utcnow()),
                "updated_at": datetime.utcnow(),
                
                # Preserve original data in metadata
                "metadata": {
                    "original_organization_id": org_id,
                    "migrated_from": "valuation_admin",
                    "migration_date": datetime.utcnow()
                },
                
                # Preserve settings
                "settings": {
                    "s3_prefix": org.get('settings', {}).get('s3_prefix', org_id),
                    "subscription_plan": org.get('settings', {}).get('subscription_plan', 'free'),
                    "max_reports_per_month": org.get('settings', {}).get('max_reports_per_month', 100),
                    "max_users": org.get('settings', {}).get('max_users', 10),
                    "max_storage_gb": org.get('settings', {}).get('max_storage_gb', 5)
                },
                
                # Preserve contact info
                "contact": {
                    "email": org.get('contact_email'),
                    "phone": org.get('contact_phone'),
                    "address": org.get('address')
                },
                
                # Preserve subscription details if exists
                "subscription": org.get('subscription', {})
            }
            
            # Insert into target collection
            result = await target_collection.insert_one(new_org)
            print(f"✓ Inserted with _id: {result.inserted_id}")
            print(f"  - org_short_name: {org_short_name}")
            print(f"  - S3 prefix preserved: {new_org['settings']['s3_prefix']}")
            print(f"  - Contact email: {new_org['contact']['email']}")
            print(f"  - Subscription plan: {new_org['settings']['subscription_plan']}")
        
        # Verify System Administration org exists
        print(f"\n{'-' * 80}")
        print("Verifying System Administration org...")
        system_org = await target_collection.find_one({"is_system_org": True})
        
        if system_org:
            print(f"✓ System Administration org exists")
            print(f"  - org_short_name: {system_org['org_short_name']}")
        else:
            print("⚠️  System Administration org not found, creating...")
            system_org = {
                "org_name": "System Administration",
                "org_short_name": "system-administration",
                "org_display_name": "System Administration",
                "is_system_org": True,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "settings": {
                    "s3_prefix": "system_admin",
                    "subscription_plan": "enterprise",
                    "max_reports_per_month": -1,  # Unlimited
                    "max_users": -1,  # Unlimited
                    "max_storage_gb": -1  # Unlimited
                }
            }
            result = await target_collection.insert_one(system_org)
            print(f"✓ Created System Administration org: {result.inserted_id}")
        
        # Summary
        print(f"\n{'=' * 80}")
        print("MIGRATION SUMMARY")
        print(f"{'=' * 80}")
        
        all_orgs = await target_collection.find({}).to_list(length=None)
        print(f"\nTotal organizations in val_app_config: {len(all_orgs)}")
        
        for org in all_orgs:
            status = "🔧 System" if org.get('is_system_org') else "✓ Active" if org.get('is_active') else "⚠️  Inactive"
            print(f"  {status} {org['org_name']} ({org['org_short_name']})")
            if org.get('metadata', {}).get('original_organization_id'):
                print(f"       → Migrated from: {org['metadata']['original_organization_id']}")
        
        print(f"\n{'=' * 80}")
        print("Migration completed successfully!")
        print(f"{'=' * 80}\n")
        
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(migrate_organizations())
