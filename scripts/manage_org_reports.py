#!/usr/bin/env python3
"""
Delete All Reports for Organization
This script will delete all reports for a specific organization from MongoDB.
"""

import os
import sys
import argparse
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

def delete_all_org_reports(org_short_name, confirm=False):
    """Delete all reports for a specific organization"""
    print(f"🗑️ DELETE ALL REPORTS FOR ORGANIZATION: {org_short_name}")
    print("=" * 60)
    
    try:
        mongodb_uri = os.getenv('MONGODB_URI')
        if not mongodb_uri:
            print("❌ MONGODB_URI environment variable not found")
            return False
            
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=10000)
        
        # Test connection
        client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas")
        
        # Connect to organization database
        db = client[org_short_name]
        
        print(f"📋 Checking reports in '{org_short_name}' database...")
        
        # Count reports before deletion
        count_before = db.reports.count_documents({})
        print(f"📊 Found {count_before} reports")
        
        if count_before == 0:
            print("ℹ️ No reports to delete")
            client.close()
            return True
        
        # Show some sample reports
        sample_reports = list(db.reports.find({}).limit(3))
        print(f"\n📄 Sample reports:")
        for i, report in enumerate(sample_reports):
            print(f"   {i+1}. {report.get('reference_number', 'N/A')} - {report.get('status', 'N/A')} - {report.get('created_at', 'N/A')}")
        
        if not confirm:
            print(f"\n⚠️ WARNING: This will PERMANENTLY DELETE all {count_before} reports!")
            print("This action cannot be undone.")
            response = input("Type 'DELETE' to confirm: ")
            
            if response != 'DELETE':
                print("❌ Deletion cancelled")
                client.close()
                return False
        
        print(f"\n🗑️ Deleting all reports...")
        
        # Delete all reports
        result = db.reports.delete_many({})
        
        print(f"✅ Deleted {result.deleted_count} reports")
        
        # Verify deletion
        count_after = db.reports.count_documents({})
        print(f"📊 Reports after deletion: {count_after}")
        
        if count_after == 0:
            print("✅ All reports successfully deleted")
            client.close()
            return True
        else:
            print(f"⚠️ {count_after} reports still remain")
            client.close()
            return False
        
    except Exception as e:
        print(f"❌ Error deleting reports: {e}")
        return False

def soft_delete_all_org_reports(org_short_name, confirm=False):
    """Mark all reports as deleted (soft delete) for a specific organization"""
    print(f"🗑️ SOFT DELETE ALL REPORTS FOR ORGANIZATION: {org_short_name}")
    print("=" * 60)
    
    try:
        mongodb_uri = os.getenv('MONGODB_URI')
        if not mongodb_uri:
            print("❌ MONGODB_URI environment variable not found")
            return False
            
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=10000)
        
        # Test connection
        client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas")
        
        # Connect to organization database
        db = client[org_short_name]
        
        print(f"📋 Checking reports in '{org_short_name}' database...")
        
        # Count active reports
        count_active = db.reports.count_documents({"status": {"$ne": "deleted"}})
        count_total = db.reports.count_documents({})
        
        print(f"📊 Total reports: {count_total}")
        print(f"📊 Active reports: {count_active}")
        print(f"📊 Already deleted: {count_total - count_active}")
        
        if count_active == 0:
            print("ℹ️ No active reports to delete")
            client.close()
            return True
        
        if not confirm:
            print(f"\n⚠️ WARNING: This will SOFT DELETE all {count_active} active reports!")
            print("Reports will be marked as deleted but remain in database.")
            response = input("Type 'SOFT-DELETE' to confirm: ")
            
            if response != 'SOFT-DELETE':
                print("❌ Soft deletion cancelled")
                client.close()
                return False
        
        print(f"\n🗑️ Marking all active reports as deleted...")
        
        # Soft delete all active reports
        result = db.reports.update_many(
            {"status": {"$ne": "deleted"}},
            {
                "$set": {
                    "status": "deleted",
                    "deleted_at": datetime.utcnow(),
                    "deleted_by": "admin_script"
                }
            }
        )
        
        print(f"✅ Soft deleted {result.modified_count} reports")
        
        # Verify soft deletion
        count_after_active = db.reports.count_documents({"status": {"$ne": "deleted"}})
        count_after_deleted = db.reports.count_documents({"status": "deleted"})
        
        print(f"📊 Active reports after deletion: {count_after_active}")
        print(f"📊 Deleted reports: {count_after_deleted}")
        
        if count_after_active == 0:
            print("✅ All reports successfully soft deleted")
            client.close()
            return True
        else:
            print(f"⚠️ {count_after_active} reports still active")
            client.close()
            return False
        
    except Exception as e:
        print(f"❌ Error soft deleting reports: {e}")
        return False

def list_org_reports(org_short_name):
    """List all reports for an organization"""
    print(f"📋 LIST ALL REPORTS FOR ORGANIZATION: {org_short_name}")
    print("=" * 60)
    
    try:
        mongodb_uri = os.getenv('MONGODB_URI')
        if not mongodb_uri:
            print("❌ MONGODB_URI environment variable not found")
            return False
            
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=10000)
        
        # Test connection
        client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas")
        
        # Connect to organization database
        db = client[org_short_name]
        
        reports = list(db.reports.find({}).sort('created_at', -1))
        
        print(f"📊 Found {len(reports)} total reports")
        
        if len(reports) == 0:
            print("ℹ️ No reports found")
            client.close()
            return True
        
        print(f"\n📄 Reports list:")
        print(f"{'#':<3} {'Reference':<25} {'Status':<10} {'Created':<20} {'Bank':<5}")
        print("-" * 70)
        
        for i, report in enumerate(reports):
            ref_num = report.get('reference_number', 'N/A')[:24]
            status = report.get('status', 'N/A')
            created = str(report.get('created_at', 'N/A'))[:19]
            bank = report.get('bank_code', 'N/A')
            
            print(f"{i+1:<3} {ref_num:<25} {status:<10} {created:<20} {bank:<5}")
        
        # Summary by status
        statuses = {}
        for report in reports:
            status = report.get('status', 'unknown')
            statuses[status] = statuses.get(status, 0) + 1
        
        print(f"\n📊 Summary by status:")
        for status, count in statuses.items():
            print(f"   {status}: {count}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error listing reports: {e}")
        return False

def main():
    """Main function with command line arguments"""
    parser = argparse.ArgumentParser(description='Manage organization reports')
    parser.add_argument('organization', help='Organization short name (e.g., sk-tindwal)')
    parser.add_argument('action', choices=['list', 'delete', 'soft-delete'], 
                       help='Action to perform')
    parser.add_argument('--confirm', action='store_true', 
                       help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    print("🚀 ORGANIZATION REPORTS MANAGER")
    print(f"🕐 Timestamp: {datetime.now().isoformat()}")
    print(f"🏢 Organization: {args.organization}")
    print(f"⚡ Action: {args.action}")
    
    if args.action == 'list':
        success = list_org_reports(args.organization)
    elif args.action == 'delete':
        success = delete_all_org_reports(args.organization, args.confirm)
    elif args.action == 'soft-delete':
        success = soft_delete_all_org_reports(args.organization, args.confirm)
    
    if success:
        print(f"\n✅ Action '{args.action}' completed successfully!")
    else:
        print(f"\n❌ Action '{args.action}' failed!")
    
    print("\n📋 Usage examples:")
    print("  python3 scripts/manage_org_reports.py sk-tindwal list")
    print("  python3 scripts/manage_org_reports.py sk-tindwal soft-delete")
    print("  python3 scripts/manage_org_reports.py sk-tindwal delete --confirm")

if __name__ == "__main__":
    main()