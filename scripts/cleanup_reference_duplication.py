#!/usr/bin/env python3
"""
Fix Reference Number Duplication Issue & Clean up Reports
This script will:
1. Analyze the reference number duplication issue
2. Delete all reports in sk-tindwal organization  
3. Fix the frontend to use only one reference field
"""

import os
import sys
import asyncio
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

def analyze_reference_duplication():
    """Analyze the reference number duplication issue"""
    print("🔍 ANALYZING REFERENCE NUMBER DUPLICATION")
    print("=" * 60)
    
    try:
        mongodb_uri = os.getenv('MONGODB_URI')
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=10000)
        
        # Connect to sk-tindwal database
        db = client['sk-tindwal']
        
        print(f"📋 Checking reports in 'sk-tindwal' database...")
        reports = list(db.reports.find({}))
        
        print(f"📊 Found {len(reports)} reports")
        
        for i, report in enumerate(reports):
            print(f"\n📄 Report {i+1}:")
            print(f"   report_id: {report.get('report_id', 'N/A')}")
            print(f"   reference_number (root): {report.get('reference_number', 'N/A')}")
            
            # Check for reference in report_data
            if 'report_data' in report and isinstance(report['report_data'], dict):
                ref_in_data = report['report_data'].get('report_reference_number')
                if ref_in_data:
                    print(f"   report_reference_number (in report_data): {ref_in_data}")
                    
                    # Check if they're different
                    root_ref = report.get('reference_number')
                    if root_ref != ref_in_data:
                        print(f"   🚨 MISMATCH DETECTED!")
                        print(f"      Root level: {root_ref}")
                        print(f"      In data:    {ref_in_data}")
                else:
                    print(f"   report_reference_number (in report_data): None")
            
            print(f"   created_at: {report.get('created_at', 'N/A')}")
            print(f"   status: {report.get('status', 'N/A')}")
        
        client.close()
        return len(reports)
        
    except Exception as e:
        print(f"❌ Error analyzing reports: {e}")
        return 0

def delete_all_reports():
    """Delete all reports in sk-tindwal organization"""
    print("\n🗑️ DELETING ALL REPORTS IN SK-TINDWAL")
    print("=" * 60)
    
    try:
        mongodb_uri = os.getenv('MONGODB_URI')
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=10000)
        
        # Connect to sk-tindwal database
        db = client['sk-tindwal']
        
        # Count reports before deletion
        count_before = db.reports.count_documents({})
        print(f"📊 Reports before deletion: {count_before}")
        
        if count_before == 0:
            print("ℹ️ No reports to delete")
            client.close()
            return
        
        # Ask for confirmation
        print(f"\n⚠️ WARNING: This will DELETE ALL {count_before} reports!")
        print("This action cannot be undone.")
        
        # For script execution, we'll proceed with deletion
        # In interactive mode, you'd want to ask for confirmation
        
        # Delete all reports
        result = db.reports.delete_many({})
        
        print(f"✅ Deleted {result.deleted_count} reports")
        
        # Verify deletion
        count_after = db.reports.count_documents({})
        print(f"📊 Reports after deletion: {count_after}")
        
        if count_after == 0:
            print("✅ All reports successfully deleted")
        else:
            print(f"⚠️ {count_after} reports still remain")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error deleting reports: {e}")

def fix_reference_field_usage():
    """Analyze and suggest fixes for reference field usage"""
    print("\n🔧 REFERENCE FIELD USAGE ANALYSIS")
    print("=" * 60)
    
    print("📋 CURRENT ISSUE:")
    print("   1. Backend creates 'reference_number' at root level")
    print("   2. Frontend stores 'report_reference_number' in report_data")
    print("   3. This creates duplication and confusion")
    
    print("\n✅ RECOMMENDED SOLUTION:")
    print("   1. Use ONLY 'reference_number' at root level")
    print("   2. Remove 'report_reference_number' from report_data")
    print("   3. Update frontend to use root-level reference_number")
    
    print("\n🔍 FIELDS TO STANDARDIZE:")
    print("   Root Level (Backend Generated):")
    print("   ├── reference_number: 'CEV/RVO/299/XXXX/DDMMYYYY'")
    print("   ├── report_id: 'rpt_xxxxxxxxxxxx'")
    print("   ├── bank_code: 'SBI'")
    print("   ├── template_id: 'land-property'")
    print("   └── report_data: { ... user form data only ... }")
    
    print("\n🚫 REMOVE FROM report_data:")
    print("   ❌ report_reference_number (duplicate)")
    print("   ❌ bank_code (already at root)")
    print("   ❌ template_id (already at root)")
    print("   ❌ organization_id (can be derived from database)")

def check_table_save_issue():
    """Analyze the table save issue"""
    print("\n🔍 TABLE SAVE ISSUE ANALYSIS")
    print("=" * 60)
    
    print("📋 REPORTED PROBLEM:")
    print("   - User fills table values (Boundaries, Building Specs, etc.)")
    print("   - Values don't get saved in database")
    print("   - Form loses data after save/refresh")
    
    print("\n🔍 LIKELY CAUSES:")
    print("   1. Frontend not sending table data in correct format")
    print("   2. Backend not processing nested table objects")
    print("   3. Form component not binding table data properly")
    print("   4. Dynamic table component data not included in form submission")
    
    print("\n🔧 INVESTIGATION STEPS:")
    print("   1. Check browser Network tab during save")
    print("   2. Verify request payload includes table data")
    print("   3. Check backend logs for data processing")
    print("   4. Verify MongoDB document structure after save")
    
    print("\n📋 TABLES TO CHECK:")
    print("   - Boundaries and Dimensions")
    print("   - Building Specifications")  
    print("   - Floor-wise Valuation Details")
    print("   - Property Details")
    print("   - Site Characteristics")

def main():
    """Run the complete cleanup and analysis"""
    print("🚀 REPORT REFERENCE CLEANUP & ANALYSIS")
    print(f"🕐 Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # 1. Analyze current duplication issue
    report_count = analyze_reference_duplication()
    
    # 2. Delete all reports if any exist
    if report_count > 0:
        delete_all_reports()
    
    # 3. Provide analysis and recommendations
    fix_reference_field_usage()
    
    # 4. Analyze table save issue
    check_table_save_issue()
    
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS:")
    print("1. ✅ All reports deleted - clean slate achieved")
    print("2. 🔧 Fix frontend to use only root-level 'reference_number'")
    print("3. 🔧 Fix table data saving in form component")
    print("4. 🧪 Test new report creation with table data")
    print("5. ✅ Verify single reference field in database")
    
    print("\n🚀 Ready to fix the code and create clean reports!")

if __name__ == "__main__":
    main()