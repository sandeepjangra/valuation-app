#!/usr/bin/env python3
"""
Debug script to check applicant_name extraction from actual reports
"""
import os
import sys
import json
import asyncio
from datetime import datetime

# Set environment variables before importing anything
os.environ.setdefault('MONGODB_URI', 'mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreports.xsnyysn.mongodb.net/')

# Add the backend directory to Python path
sys.path.append('/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend')

from database.multi_db_manager import MultiDatabaseManager

async def check_applicant_name_extraction():
    """Check how applicant_name is being extracted from reports"""
    
    print("🔍 Debugging applicant_name extraction from reports...")
    
    # Get the function from main.py
    def get_report_display_data(report):
        """
        Extract display data from report handling both old and new structures
        Old: property_address at root, applicant_name in _common_fields_
        New: postal_address in report_data.data, applicant_name in report_data.common_fields
        """
        # Initialize defaults
        property_address = "N/A"
        applicant_name = "N/A"
        
        # Get the report_data section
        report_data = report.get("report_data", {})
        
        if isinstance(report_data, dict):
            # NEW FORMAT: Check report_data.common_fields.applicant_name (direct)
            if "common_fields" in report_data and isinstance(report_data["common_fields"], dict):
                applicant_name = report_data["common_fields"].get("applicant_name", "N/A")
            
            # NEW FORMAT: Check report_data.data.postal_address (direct) 
            if "data" in report_data and isinstance(report_data["data"], dict):
                data_section = report_data["data"]
                property_address = data_section.get("postal_address") or data_section.get("property_address", "N/A")
            
            # OLD FORMAT FALLBACK: report_data.report_data.data (nested)
            elif "report_data" in report_data and isinstance(report_data["report_data"], dict):
                nested_report_data = report_data["report_data"]
                if "data" in nested_report_data and isinstance(nested_report_data["data"], dict):
                    data_section = nested_report_data["data"]
                    property_address = data_section.get("postal_address") or data_section.get("property_address", "N/A")
            
            # OLD FORMAT: Direct fields in report_data
            elif isinstance(report_data, dict):
                property_address = report_data.get("postal_address") or report_data.get("property_address", "N/A")
            
            # OLD FORMAT FALLBACK: _common_fields_ inside report_data
            if applicant_name == "N/A" and "_common_fields_" in report_data and isinstance(report_data["_common_fields_"], dict):
                applicant_name = report_data["_common_fields_"].get("applicant_name", "N/A")
        
        # LEGACY FALLBACK: Try root level
        if property_address == "N/A":
            property_address = report.get("property_address", "N/A")
        
        if applicant_name == "N/A" and "common_fields" in report and isinstance(report["common_fields"], dict):
            applicant_name = report["common_fields"].get("applicant_name", "N/A")
        
        return {
            "property_address": property_address,
            "applicant_name": applicant_name
        }
    
    # Connect to database
    db_manager = MultiDatabaseManager()
    await db_manager.connect()
    
    # Get sk-tindwal organization reports
    org_db = db_manager.get_org_database("sk-tindwal")
    
    # Get all reports for this organization
    reports = await org_db.reports.find({}).sort("created_at", -1).limit(5).to_list(length=None)
    
    print(f"📊 Found {len(reports)} reports for sk-tindwal")
    print("=" * 60)
    
    for i, report in enumerate(reports, 1):
        print(f"\n🔍 Report {i}: {report.get('report_id', 'Unknown ID')}")
        print(f"Status: {report.get('status', 'No Status')}")
        print(f"Created: {report.get('created_at', 'No Date')}")
        
        # Extract display data using the function
        display_data = get_report_display_data(report)
        print(f"🏷️  Extracted applicant_name: '{display_data['applicant_name']}'")
        
        # Let's examine the actual report_data structure
        report_data = report.get("report_data", {})
        print(f"📄 report_data type: {type(report_data)}")
        
        if isinstance(report_data, dict):
            print(f"📄 report_data keys: {list(report_data.keys())}")
            
            # Check common_fields
            if "common_fields" in report_data:
                common_fields = report_data["common_fields"]
                print(f"📄 common_fields type: {type(common_fields)}")
                if isinstance(common_fields, dict):
                    print(f"📄 common_fields content: {json.dumps(common_fields, indent=2, default=str)}")
                else:
                    print(f"📄 common_fields value: {common_fields}")
            
            # Check data section
            if "data" in report_data:
                data_section = report_data["data"]
                print(f"📄 data section type: {type(data_section)}")
                if isinstance(data_section, dict):
                    # Look for any applicant-related fields
                    applicant_fields = {k: v for k, v in data_section.items() if "applicant" in k.lower()}
                    if applicant_fields:
                        print(f"📄 Found applicant fields in data: {json.dumps(applicant_fields, indent=2, default=str)}")
                    else:
                        print(f"📄 No applicant fields found in data section")
        
        print("-" * 40)
    
    await db_manager.disconnect()
    print("\n✅ Debugging complete!")

if __name__ == "__main__":
    asyncio.run(check_applicant_name_extraction())