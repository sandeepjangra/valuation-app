"""
Update Reports Schema with Organization Context
Adds org_short_name field and ensures proper status workflow fields
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

MONGODB_URI = os.getenv("MONGODB_URI")

# Organization ID to short name mapping
ORG_MAPPING = {
    "system_admin": "system-administration",
    "sk_tindwal_001": "sk-tindwal",
    "val_app_config": "val-app-config"  # Central config database (not an org)
}

async def update_reports_schema():
    """Update all reports to include org_short_name"""
    client = AsyncIOMotorClient(
        MONGODB_URI,
        tlsAllowInvalidCertificates=True
    )
    
    try:
        print("=" * 80)
        print("REPORTS SCHEMA UPDATE - Adding Organization Context")
        print("=" * 80)
        
        # Get all databases
        db_list = await client.list_database_names()
        
        # Filter organization databases (exclude system databases)
        org_databases = [db for db in db_list if db not in [
            'admin', 'local', 'config', 'shared_resources', 'valuation_admin'
        ]]
        
        print(f"\n✓ Found {len(org_databases)} organization databases")
        
        total_updated = 0
        
        for db_name in org_databases:
            print(f"\n{'-' * 80}")
            print(f"Processing database: {db_name}")
            
            db = client[db_name]
            
            # Check if reports collection exists
            collections = await db.list_collection_names()
            if 'reports' not in collections:
                print(f"  ⚠️  No reports collection found, skipping...")
                continue
            
            reports_collection = db.reports
            
            # Get all reports
            reports = await reports_collection.find({}).to_list(length=None)
            print(f"  ✓ Found {len(reports)} reports")
            
            if len(reports) == 0:
                continue
            
            # Update each report
            updated_count = 0
            for report in reports:
                report_id = report.get('report_id', str(report.get('_id')))
                org_id = report.get('organization_id')
                
                # Skip if already has org_short_name
                if report.get('org_short_name'):
                    continue
                
                # Determine org_short_name
                org_short_name = None
                if org_id:
                    org_short_name = ORG_MAPPING.get(org_id)
                    if org_short_name:
                        # Try to fetch from organizations collection
                        orgs_db = client.val_app_config
                        org_doc = await orgs_db.organizations.find_one({
                            "metadata.original_organization_id": org_id
                        })
                        if org_doc:
                            org_short_name = org_doc.get('org_short_name')
                
                # Default to database name if we can't determine org_short_name
                if not org_short_name:
                    if db_name == 'sk_tindwal_001':
                        org_short_name = 'sk-tindwal'
                    else:
                        org_short_name = db_name.replace('_001', '').replace('_', '-')
                
                # Prepare update
                update_doc = {
                    "$set": {
                        "org_short_name": org_short_name,
                        "updated_at": datetime.utcnow()
                    }
                }
                
                # Ensure status field exists (default to 'draft' if missing)
                if not report.get('status'):
                    update_doc["$set"]["status"] = "draft"
                
                # Ensure created_by exists
                if not report.get('created_by'):
                    update_doc["$set"]["created_by"] = "unknown"
                
                # Update the report
                await reports_collection.update_one(
                    {"_id": report["_id"]},
                    update_doc
                )
                
                updated_count += 1
                print(f"    ✓ Updated report {report_id}: org_short_name = {org_short_name}")
            
            print(f"  ✓ Updated {updated_count} reports in {db_name}")
            total_updated += updated_count
        
        # Create indexes on reports collections
        print(f"\n{'-' * 80}")
        print("Creating indexes on reports collections...")
        
        for db_name in org_databases:
            db = client[db_name]
            collections = await db.list_collection_names()
            
            if 'reports' in collections:
                reports_collection = db.reports
                
                # Create indexes
                await reports_collection.create_index("org_short_name")
                await reports_collection.create_index("status")
                await reports_collection.create_index("created_by")
                await reports_collection.create_index([("org_short_name", 1), ("status", 1)])
                await reports_collection.create_index([("created_by", 1), ("status", 1)])
                
                print(f"  ✓ Created indexes on {db_name}.reports")
        
        print(f"\n{'=' * 80}")
        print("SUMMARY")
        print(f"{'=' * 80}")
        print(f"Total reports updated: {total_updated}")
        print(f"Databases processed: {len(org_databases)}")
        print(f"\n{'=' * 80}")
        print("Schema update completed successfully!")
        print(f"{'=' * 80}\n")
        
    except Exception as e:
        print(f"\n❌ Error during schema update: {e}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(update_reports_schema())
