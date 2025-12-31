#!/usr/bin/env python3
"""
Investigate the specific report that was saved with wrong format
"""

import requests
import json

def investigate_report():
    """Check the specific problematic report"""
    
    print("🔍 INVESTIGATING PROBLEMATIC REPORT")
    print("=" * 80)
    
    # Login to sk-tindwal org
    login_data = {"email": "sk.tindwal@gmail.com", "password": "admin123"}
    
    try:
        login_response = requests.post("http://localhost:8000/api/auth/login", json=login_data, timeout=10)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return
        
        token = login_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print("✅ Login successful for sk.tindwal@gmail.com")
        
        # Get the specific report
        report_id = "rpt_431b6b6ada7f"
        
        print(f"📋 Retrieving report: {report_id}")
        
        response = requests.get(
            f"http://localhost:8000/api/reports/{report_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                report_data = result["data"]["report_data"]
                
                print(f"\n📊 REPORT STRUCTURE ANALYSIS:")
                print(f"   📋 Report ID: {report_id}")
                
                # Check current structure
                sections = list(report_data.keys())
                print(f"   📁 Top-level sections: {len(sections)}")
                
                for section in sections:
                    section_data = report_data[section]
                    if isinstance(section_data, dict):
                        field_count = len(section_data)
                        print(f"      📂 {section}: {field_count} fields")
                        
                        # Check if it's empty
                        if field_count == 0:
                            print(f"         ⚠️ EMPTY SECTION!")
                        else:
                            # Sample a few fields
                            sample_fields = list(section_data.keys())[:3]
                            print(f"         📄 Sample fields: {sample_fields}")
                    else:
                        print(f"      📄 {section}: {type(section_data).__name__}")
                
                # Specific checks for the problematic structure
                print(f"\n🔍 PROBLEM ANALYSIS:")
                
                # Check for empty Property Details
                if "Property Details" in report_data:
                    prop_details = report_data["Property Details"]
                    if isinstance(prop_details, dict) and len(prop_details) == 0:
                        print(f"   ❌ 'Property Details' section is EMPTY (this was the problem)")
                    else:
                        print(f"   ✅ 'Property Details' has {len(prop_details)} fields")
                else:
                    print(f"   📋 No 'Property Details' section found")
                
                # Check for _unmapped_ section
                if "_unmapped_" in report_data:
                    unmapped = report_data["_unmapped_"]
                    if isinstance(unmapped, dict):
                        print(f"   ⚠️ '_unmapped_' section has {len(unmapped)} fields")
                        if len(unmapped) > 10:
                            print(f"      🚨 This indicates transformation failure!")
                        # Show sample unmapped fields
                        sample_unmapped = list(unmapped.keys())[:5]
                        print(f"      📄 Sample unmapped: {sample_unmapped}")
                    else:
                        print(f"   📄 '_unmapped_': {type(unmapped).__name__}")
                else:
                    print(f"   ✅ No '_unmapped_' section (good!)")
                
                # Check for tables section
                if "tables" in report_data:
                    tables = report_data["tables"]
                    if isinstance(tables, dict):
                        print(f"   📊 'tables' section has {len(tables)} tables")
                        for table_id in tables.keys():
                            print(f"      📋 Table: {table_id}")
                    else:
                        print(f"   📊 'tables': {type(tables).__name__}")
                else:
                    print(f"   📊 No 'tables' section found")
                
                # Check for report_data section (new simple format)
                if "report_data" in report_data:
                    main_data = report_data["report_data"]
                    if isinstance(main_data, dict):
                        print(f"   📄 'report_data' section has {len(main_data)} fields")
                    else:
                        print(f"   📄 'report_data': {type(main_data).__name__}")
                else:
                    print(f"   📄 No 'report_data' section found")
                
                print(f"\n🏆 CONCLUSION:")
                
                # Determine if this report still has the old problematic structure
                has_empty_sections = False
                has_large_unmapped = False
                
                if "Property Details" in report_data and len(report_data.get("Property Details", {})) == 0:
                    has_empty_sections = True
                
                if "_unmapped_" in report_data and len(report_data.get("_unmapped_", {})) > 10:
                    has_large_unmapped = True
                
                if has_empty_sections and has_large_unmapped:
                    print(f"   🚨 This report still has the OLD problematic format")
                    print(f"   💡 This report was created before the transformation fix")
                    print(f"   🔧 New reports will use the simple transformation")
                elif "report_data" in report_data and "tables" in report_data:
                    print(f"   ✅ This report has the NEW simple format")
                    print(f"   🎉 The transformation fix is working!")
                else:
                    print(f"   ❓ This report has a mixed or unknown format")
                
            else:
                print(f"❌ API returned success=false: {result}")
                
        else:
            print(f"❌ Failed to retrieve report: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    investigate_report()