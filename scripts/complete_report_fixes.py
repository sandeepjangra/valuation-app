#!/usr/bin/env python3
"""
Complete Report Management and Fix Implementation

This script provides comprehensive functionality for:
1. Implementing soft delete functionality
2. Fixing reference number duplication
3. Managing organization reports (list, delete, cleanup)
4. Testing the fixes

Usage:
    python scripts/complete_report_fixes.py --help
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List
import json

# Add backend directory to path
sys.path.append('/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend')

from database.multi_db_manager import MultiDatabaseManager

class ReportManagementSystem:
    def __init__(self):
        self.db_manager = MultiDatabaseManager()
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            await self.db_manager.connect()
            print("✅ Connected to MongoDB Atlas")
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        try:
            await self.db_manager.disconnect()
            print("✅ Disconnected from MongoDB")
        except Exception as e:
            print(f"⚠️ Error disconnecting: {e}")
    
    async def list_org_reports(self, org_short_name: str = "sk-tindwal", show_deleted: bool = False):
        """List all reports for organization with status breakdown"""
        print(f"\n📊 Listing reports for organization: {org_short_name}")
        print(f"   {'Including' if show_deleted else 'Excluding'} deleted reports")
        
        try:
            org_db = self.db_manager.get_org_database(org_short_name)
            
            # Build query filter
            query_filter = {}
            if not show_deleted:
                query_filter = {
                    "$or": [
                        {"is_deleted": {"$exists": False}},
                        {"is_deleted": False}
                    ]
                }
            
            reports = await org_db.reports.find(query_filter).sort("created_at", -1).to_list(None)
            
            if not reports:
                print("📄 No reports found")
                return
            
            # Status breakdown
            status_counts = {}
            deleted_count = 0
            reference_issues = 0
            
            print(f"\n📋 Found {len(reports)} reports:")
            print("=" * 80)
            
            for i, report in enumerate(reports, 1):
                report_id = report.get('report_id', 'Unknown')
                ref_num = report.get('reference_number', 'No Reference')
                status = report.get('status', 'unknown')
                is_deleted = report.get('is_deleted', False)
                created_at = report.get('created_at', 'Unknown')
                created_by = report.get('created_by_email', 'Unknown')
                property_addr = report.get('property_address', 'No Address')[:50]
                
                # Check for reference duplication
                has_nested_ref = bool(report.get('report_data', {}).get('report_reference_number'))
                
                if has_nested_ref:
                    reference_issues += 1
                
                # Count statuses
                if is_deleted:
                    deleted_count += 1
                    status_key = f"deleted ({status})"
                else:
                    status_key = status
                
                status_counts[status_key] = status_counts.get(status_key, 0) + 1
                
                # Display report info
                delete_flag = "🗑️ " if is_deleted else ""
                ref_flag = "⚠️ " if has_nested_ref else ""
                
                print(f"{i:2d}. {delete_flag}{ref_flag}{report_id}")
                print(f"    Reference: {ref_num}")
                print(f"    Status: {status} | Created: {created_at}")
                print(f"    By: {created_by}")
                print(f"    Property: {property_addr}")
                if has_nested_ref:
                    nested_ref = report.get('report_data', {}).get('report_reference_number')
                    print(f"    ⚠️ DUPLICATE REF: {nested_ref}")
                print()
            
            # Summary
            print("📈 Summary:")
            print(f"  Total reports: {len(reports)}")
            print(f"  Deleted reports: {deleted_count}")
            print(f"  Reports with reference duplication: {reference_issues}")
            print(f"\n📊 Status breakdown:")
            for status, count in sorted(status_counts.items()):
                print(f"  {status}: {count}")
            
            return {
                'total': len(reports),
                'deleted': deleted_count,
                'reference_issues': reference_issues,
                'status_counts': status_counts
            }
            
        except Exception as e:
            print(f"❌ Error listing reports: {e}")
            raise
    
    async def fix_reference_duplication(self, org_short_name: str = "sk-tindwal", dry_run: bool = True):
        """Fix reference number duplication by removing nested field"""
        print(f"\n🔧 {'[DRY RUN] ' if dry_run else ''}Fixing reference number duplication")
        
        try:
            org_db = self.db_manager.get_org_database(org_short_name)
            
            # Find reports with duplicate reference fields
            reports = await org_db.reports.find({
                "reference_number": {"$exists": True},
                "report_data.report_reference_number": {"$exists": True}
            }).to_list(None)
            
            print(f"📋 Found {len(reports)} reports with duplicate reference fields")
            
            if len(reports) == 0:
                print("✅ No duplicate reference fields found!")
                return {'fixed': 0, 'errors': 0}
            
            fixed_count = 0
            error_count = 0
            
            for report in reports:
                report_id = report.get('report_id')
                root_ref = report.get('reference_number')
                nested_ref = report.get('report_data', {}).get('report_reference_number')
                
                print(f"\n  Processing: {report_id}")
                print(f"    Root reference: {root_ref}")
                print(f"    Nested reference: {nested_ref}")
                
                if root_ref != nested_ref:
                    print(f"    ⚠️ MISMATCH detected! Keeping root reference: {root_ref}")
                
                if not dry_run:
                    try:
                        # Remove the nested reference field
                        update_result = await org_db.reports.update_one(
                            {"report_id": report_id},
                            {"$unset": {"report_data.report_reference_number": ""}}
                        )
                        
                        if update_result.modified_count > 0:
                            fixed_count += 1
                            print(f"    ✅ Removed duplicate nested reference")
                        else:
                            print(f"    ❌ Failed to update report")
                            error_count += 1
                    except Exception as e:
                        print(f"    ❌ Error updating report: {e}")
                        error_count += 1
                else:
                    fixed_count += 1
                    print(f"    🔍 Would remove nested reference field")
            
            print(f"\n📈 Summary:")
            print(f"  Reports processed: {len(reports)}")
            print(f"  Reports {'that would be ' if dry_run else ''}fixed: {fixed_count}")
            if error_count > 0:
                print(f"  Errors: {error_count}")
            
            if dry_run:
                print(f"\n⚠️ This was a DRY RUN. No changes were made.")
                print(f"   Run with --fix-refs to apply changes.")
            else:
                print(f"\n✅ Reference duplication cleanup completed!")
            
            return {'fixed': fixed_count, 'errors': error_count}
            
        except Exception as e:
            print(f"❌ Error fixing references: {e}")
            raise
    
    async def soft_delete_report(self, report_id: str, org_short_name: str = "sk-tindwal", deleted_by: str = "admin"):
        """Soft delete a single report"""
        try:
            org_db = self.db_manager.get_org_database(org_short_name)
            
            # Check if report exists
            report = await org_db.reports.find_one({"report_id": report_id})
            if not report:
                print(f"❌ Report {report_id} not found")
                return False
            
            # Update report with soft delete fields
            update_data = {
                "is_deleted": True,
                "deleted_at": datetime.now(),
                "deleted_by": deleted_by,
                "status": "deleted"
            }
            
            result = await org_db.reports.update_one(
                {"report_id": report_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                print(f"✅ Report {report_id} soft deleted")
                return True
            else:
                print(f"❌ Failed to soft delete report {report_id}")
                return False
                
        except Exception as e:
            print(f"❌ Error soft deleting report {report_id}: {e}")
            return False
    
    async def restore_deleted_report(self, report_id: str, org_short_name: str = "sk-tindwal"):
        """Restore a soft-deleted report"""
        try:
            org_db = self.db_manager.get_org_database(org_short_name)
            
            # Update report to restore
            update_data = {
                "is_deleted": False,
                "status": "draft"  # Restore as draft
            }
            
            result = await org_db.reports.update_one(
                {"report_id": report_id, "is_deleted": True},
                {
                    "$set": update_data,
                    "$unset": {"deleted_at": "", "deleted_by": ""}
                }
            )
            
            if result.modified_count > 0:
                print(f"✅ Report {report_id} restored")
                return True
            else:
                print(f"❌ Failed to restore report {report_id} (not found or not deleted)")
                return False
                
        except Exception as e:
            print(f"❌ Error restoring report {report_id}: {e}")
            return False
    
    async def cleanup_all_reports(self, org_short_name: str = "sk-tindwal", action: str = "soft_delete"):
        """Cleanup all reports for organization"""
        print(f"\n🧹 {'Soft deleting' if action == 'soft_delete' else 'Hard deleting'} all reports for: {org_short_name}")
        
        # Safety confirmation
        confirm_msg = f"This will {action.replace('_', ' ')} ALL reports. Type 'YES DELETE ALL' to confirm: "
        confirmation = input(confirm_msg)
        
        if confirmation != "YES DELETE ALL":
            print("❌ Operation cancelled - confirmation not received")
            return False
        
        try:
            org_db = self.db_manager.get_org_database(org_short_name)
            
            if action == "soft_delete":
                # Soft delete all non-deleted reports
                update_data = {
                    "is_deleted": True,
                    "deleted_at": datetime.now(),
                    "deleted_by": "admin_cleanup",
                    "status": "deleted"
                }
                
                result = await org_db.reports.update_many(
                    {
                        "$or": [
                            {"is_deleted": {"$exists": False}},
                            {"is_deleted": False}
                        ]
                    },
                    {"$set": update_data}
                )
                
                print(f"✅ Soft deleted {result.modified_count} reports")
                
            elif action == "hard_delete":
                # Hard delete all reports
                result = await org_db.reports.delete_many({})
                print(f"✅ Hard deleted {result.deleted_count} reports")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
            return False
    
    async def validate_reports_health(self, org_short_name: str = "sk-tindwal"):
        """Validate overall health of reports collection"""
        print(f"\n🏥 Validating reports health for: {org_short_name}")
        
        try:
            org_db = self.db_manager.get_org_database(org_short_name)
            
            # Get all reports
            reports = await org_db.reports.find({}).to_list(None)
            
            issues = {
                'duplicate_references': 0,
                'missing_reference': 0,
                'invalid_status': 0,
                'missing_created_at': 0,
                'orphaned_soft_deletes': 0
            }
            
            valid_statuses = {'draft', 'submitted', 'completed', 'deleted', 'rejected'}
            
            for report in reports:
                # Check reference duplication
                root_ref = report.get('reference_number')
                nested_ref = report.get('report_data', {}).get('report_reference_number')
                
                if root_ref and nested_ref:
                    issues['duplicate_references'] += 1
                elif not root_ref:
                    issues['missing_reference'] += 1
                
                # Check status validity
                status = report.get('status')
                if status not in valid_statuses:
                    issues['invalid_status'] += 1
                
                # Check created_at
                if not report.get('created_at'):
                    issues['missing_created_at'] += 1
                
                # Check soft delete consistency
                is_deleted = report.get('is_deleted', False)
                if is_deleted and status != 'deleted':
                    issues['orphaned_soft_deletes'] += 1
            
            print(f"\n📊 Health Report for {len(reports)} reports:")
            print(f"  Duplicate references: {issues['duplicate_references']}")
            print(f"  Missing references: {issues['missing_reference']}")
            print(f"  Invalid statuses: {issues['invalid_status']}")
            print(f"  Missing created_at: {issues['missing_created_at']}")
            print(f"  Orphaned soft deletes: {issues['orphaned_soft_deletes']}")
            
            total_issues = sum(issues.values())
            if total_issues == 0:
                print("✅ All reports are healthy!")
            else:
                print(f"⚠️ Found {total_issues} issues that need attention")
            
            return issues
            
        except Exception as e:
            print(f"❌ Error validating reports health: {e}")
            raise

async def main():
    """Main function with comprehensive command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Complete Report Management System')
    parser.add_argument('--org', default='sk-tindwal', help='Organization short name')
    
    # Main operations
    parser.add_argument('--list', action='store_true', help='List all reports')
    parser.add_argument('--list-deleted', action='store_true', help='List reports including deleted ones')
    parser.add_argument('--fix-refs', action='store_true', help='Fix duplicate reference fields')
    parser.add_argument('--validate', action='store_true', help='Validate reports health')
    
    # Single report operations
    parser.add_argument('--soft-delete', help='Soft delete specific report by ID')
    parser.add_argument('--restore', help='Restore soft-deleted report by ID')
    
    # Bulk operations (dangerous)
    parser.add_argument('--cleanup-soft', action='store_true', help='Soft delete ALL reports (requires confirmation)')
    parser.add_argument('--cleanup-hard', action='store_true', help='Hard delete ALL reports (requires confirmation)')
    
    # Run all safe operations
    parser.add_argument('--all', action='store_true', help='Run all safe operations (list, validate, fix-refs dry run)')
    
    args = parser.parse_args()
    
    rms = ReportManagementSystem()
    
    try:
        await rms.connect()
        
        if args.all:
            print("🔄 Running all safe operations...")
            await rms.list_org_reports(args.org)
            await rms.validate_reports_health(args.org)
            await rms.fix_reference_duplication(args.org, dry_run=True)
        
        if args.list:
            await rms.list_org_reports(args.org, show_deleted=False)
        
        if args.list_deleted:
            await rms.list_org_reports(args.org, show_deleted=True)
        
        if args.fix_refs:
            await rms.fix_reference_duplication(args.org, dry_run=False)
        
        if args.validate:
            await rms.validate_reports_health(args.org)
        
        if args.soft_delete:
            await rms.soft_delete_report(args.soft_delete, args.org)
        
        if args.restore:
            await rms.restore_deleted_report(args.restore, args.org)
        
        if args.cleanup_soft:
            await rms.cleanup_all_reports(args.org, "soft_delete")
        
        if args.cleanup_hard:
            await rms.cleanup_all_reports(args.org, "hard_delete")
        
        # Default operation if no specific action
        if not any([args.list, args.list_deleted, args.fix_refs, args.validate, 
                   args.soft_delete, args.restore, args.cleanup_soft, args.cleanup_hard, args.all]):
            print("🔍 No specific action provided. Running list operation...")
            await rms.list_org_reports(args.org)
    
    finally:
        await rms.disconnect()

if __name__ == "__main__":
    asyncio.run(main())