#!/usr/bin/env python3
"""
Script to analyze saved report structure and compare with template expectations
This will help us understand why the report rpt_61286d3f2389 is not loading properly
"""

import asyncio
import os
import json
from pathlib import Path
from datetime import datetime, timezone
from bson import ObjectId

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    print("⚠️ python-dotenv not installed, loading .env manually")
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

from backend.database.multi_db_manager import MultiDatabaseManager

async def analyze_saved_report():
    """Analyze the saved report structure"""
    
    print("🔍 Analyzing saved report structure...")
    
    db_manager = MultiDatabaseManager()
    await db_manager.connect()
    
    try:
        # Get organization database for sk-tindwal
        org_db = db_manager.get_org_database("sk-tindwal")
        
        print(f"📋 Connected to organization database: sk-tindwal")
        
        # Find the specific report
        report_id = "rpt_61286d3f2389"
        report = await org_db.reports.find_one({"report_id": report_id})
        
        if not report:
            print(f"❌ Report {report_id} not found in sk-tindwal database")
            return False
        
        print(f"✅ Report {report_id} found!")
        
        # Analyze report structure
        print("\n📊 Report Analysis:")
        print(f"   Report ID: {report.get('report_id')}")
        print(f"   Reference Number: {report.get('reference_number')}")
        print(f"   Bank Code: {report.get('bank_code')}")
        print(f"   Template ID: {report.get('template_id')}")
        print(f"   Property Type: {report.get('property_type')}")
        print(f"   Status: {report.get('status')}")
        print(f"   Created At: {report.get('created_at')}")
        print(f"   Property Address: {report.get('property_address')}")
        
        # Analyze report_data structure
        report_data = report.get('report_data', {})
        print(f"\n🏗️ Report Data Structure Analysis:")
        print(f"   Total keys in report_data: {len(report_data)}")
        
        if report_data:
            print(f"\n📂 Top-level keys in report_data:")
            for key in sorted(report_data.keys()):
                value = report_data[key]
                if isinstance(value, dict):
                    print(f"     {key}: dict with {len(value)} keys")
                    if len(value) <= 5:  # Show details for small dicts
                        for subkey in sorted(value.keys()):
                            subvalue = value[subkey]
                            if isinstance(subvalue, dict):
                                print(f"       └─ {subkey}: dict with {len(subvalue)} keys")
                            elif isinstance(subvalue, list):
                                print(f"       └─ {subkey}: list with {len(subvalue)} items")
                            else:
                                print(f"       └─ {subkey}: {type(subvalue).__name__}")
                    else:
                        print(f"       └─ (showing first 3 keys)")
                        for subkey in sorted(list(value.keys())[:3]):
                            subvalue = value[subkey]
                            if isinstance(subvalue, dict):
                                print(f"       └─ {subkey}: dict with {len(subvalue)} keys")
                            elif isinstance(subvalue, list):
                                print(f"       └─ {subkey}: list with {len(subvalue)} items")
                            else:
                                print(f"       └─ {subkey}: {type(subvalue).__name__}")
                        print(f"       └─ ... and {len(value) - 3} more")
                elif isinstance(value, list):
                    print(f"     {key}: list with {len(value)} items")
                elif isinstance(value, str):
                    preview = value[:50] + "..." if len(value) > 50 else value
                    print(f"     {key}: '{preview}'")
                else:
                    print(f"     {key}: {type(value).__name__} = {value}")
        
        # Check for expected nested structure
        print(f"\n🎯 Checking for Expected Template Structure:")
        expected_tabs = ['property_details', 'valuation', 'building_specification', 'construction_details']
        
        for tab in expected_tabs:
            if tab in report_data:
                tab_data = report_data[tab]
                if isinstance(tab_data, dict):
                    print(f"   ✅ {tab}: Found with {len(tab_data)} sections/fields")
                    for section_key in sorted(tab_data.keys()):
                        section_data = tab_data[section_key]
                        if isinstance(section_data, dict):
                            print(f"      └─ {section_key}: {len(section_data)} fields")
                        else:
                            print(f"      └─ {section_key}: {type(section_data).__name__}")
                else:
                    print(f"   ⚠️ {tab}: Found but not a dict (type: {type(tab_data).__name__})")
            else:
                print(f"   ❌ {tab}: Not found")
        
        # Check for flat field structure (old format)
        flat_fields_count = 0
        for key, value in report_data.items():
            if not isinstance(value, (dict, list)) and key not in ['status', 'bankName', 'templateName', 'referenceNumber', 'organizationId', 'customTemplateId', 'customTemplateName', 'propertyType', 'reportType', 'createdAt', 'updatedAt']:
                flat_fields_count += 1
        
        print(f"\n📋 Flat Fields Analysis:")
        print(f"   Flat fields (non-nested): {flat_fields_count}")
        
        if flat_fields_count > 20:
            print(f"   ⚠️ High number of flat fields suggests old save format")
        elif flat_fields_count > 0:
            print(f"   ℹ️ Some flat fields present (possibly common fields)")
        else:
            print(f"   ✅ No flat fields - likely using new nested format")
        
        # Save detailed analysis to file for review
        analysis_file = Path(__file__).parent / f"report_analysis_{report_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        analysis_data = {
            "report_id": report_id,
            "analysis_timestamp": datetime.now().isoformat(),
            "report_metadata": {
                "report_id": report.get('report_id'),
                "reference_number": report.get('reference_number'),
                "bank_code": report.get('bank_code'),
                "template_id": report.get('template_id'),
                "property_type": report.get('property_type'),
                "status": report.get('status'),
                "created_at": str(report.get('created_at')),
                "property_address": report.get('property_address')
            },
            "report_data_structure": {
                "total_keys": len(report_data),
                "top_level_keys": list(report_data.keys()),
                "nested_structure_present": any(key in report_data for key in expected_tabs),
                "flat_fields_count": flat_fields_count
            },
            "expected_tabs_analysis": {
                tab: {
                    "present": tab in report_data,
                    "type": type(report_data.get(tab)).__name__ if tab in report_data else None,
                    "size": len(report_data[tab]) if tab in report_data and isinstance(report_data[tab], (dict, list)) else None
                }
                for tab in expected_tabs
            }
        }
        
        with open(analysis_file, 'w') as f:
            json.dump(analysis_data, f, indent=2, default=str)
        
        print(f"\n📄 Detailed analysis saved to: {analysis_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing report: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await db_manager.disconnect()

async def main():
    """Main function"""
    print("🚀 Starting Report Structure Analysis")
    print("=" * 50)
    
    try:
        success = await analyze_saved_report()
        
        if success:
            print("\n✅ Report analysis completed successfully!")
        else:
            print("\n❌ Report analysis failed!")
            
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())