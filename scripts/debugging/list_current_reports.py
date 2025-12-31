#!/usr/bin/env python3
"""
List reports in sk-tindwal organization to see current reports
"""

import requests
import json
from datetime import datetime

def list_reports():
    """List all reports in sk-tindwal organization"""
    
    print("📋 LISTING REPORTS IN SK-TINDWAL ORGANIZATION")
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
        
        # Get all reports
        print(f"📋 Retrieving reports list...")
        
        response = requests.get(
            "http://localhost:8000/api/reports",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                reports = result["data"]
                
                print(f"\n📊 REPORTS SUMMARY:")
                print(f"   📁 Total reports found: {len(reports)}")
                
                if len(reports) == 0:
                    print("   📝 No reports found in this organization")
                    return
                
                # Sort reports by creation date (newest first)
                sorted_reports = sorted(reports, 
                                      key=lambda r: r.get("created_at", ""), 
                                      reverse=True)
                
                print(f"\n📋 RECENT REPORTS:")
                
                for i, report in enumerate(sorted_reports[:10]):  # Show last 10 reports
                    report_id = report.get("report_id", "unknown")
                    created_at = report.get("created_at", "unknown")
                    status = report.get("status", "unknown")
                    property_address = report.get("property_address", "No address")
                    
                    # Parse created_at to make it more readable
                    try:
                        if created_at != "unknown":
                            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            created_display = dt.strftime("%Y-%m-%d %H:%M")
                        else:
                            created_display = "unknown"
                    except:
                        created_display = created_at
                    
                    print(f"   {i+1:2}. 📄 {report_id}")
                    print(f"       🏠 {property_address}")
                    print(f"       📅 {created_display} | 🏷️ {status}")
                    
                    # If this is a recent report, let's check its structure
                    if i < 3:  # Check structure of 3 most recent reports
                        print(f"       🔍 Checking structure...")
                        
                        # Get detailed report
                        detail_response = requests.get(
                            f"http://localhost:8000/api/reports/{report_id}",
                            headers=headers,
                            timeout=10
                        )
                        
                        if detail_response.status_code == 200:
                            detail_result = detail_response.json()
                            if detail_result.get("success"):
                                report_data = detail_result["data"]["report_data"]
                                
                                # Quick structure analysis
                                sections = list(report_data.keys())
                                
                                # Check for new format indicators
                                has_tables_section = "tables" in sections
                                has_report_data_section = "report_data" in sections
                                has_unmapped = "_unmapped_" in sections
                                has_empty_sections = False
                                
                                # Check for empty sections (old problem)
                                for section_name, section_data in report_data.items():
                                    if isinstance(section_data, dict) and len(section_data) == 0:
                                        has_empty_sections = True
                                        break
                                
                                unmapped_count = len(report_data.get("_unmapped_", {})) if has_unmapped else 0
                                
                                if has_tables_section and has_report_data_section:
                                    print(f"       ✅ NEW SIMPLE FORMAT - tables: ✓, report_data: ✓")
                                elif has_empty_sections and unmapped_count > 10:
                                    print(f"       ❌ OLD PROBLEMATIC FORMAT - empty sections, {unmapped_count} unmapped")
                                elif has_unmapped and unmapped_count > 5:
                                    print(f"       ⚠️ MIXED FORMAT - {unmapped_count} unmapped fields")
                                else:
                                    print(f"       ❓ UNKNOWN FORMAT - {len(sections)} sections")
                        else:
                            print(f"       ❌ Could not retrieve details")
                    
                    print()  # Empty line for readability
                
                # Look for the specific report mentioned
                target_report = "rpt_431b6b6ada7f"
                found_target = None
                for report in reports:
                    if report.get("report_id") == target_report:
                        found_target = report
                        break
                
                if found_target:
                    print(f"\n🎯 TARGET REPORT FOUND: {target_report}")
                    print(f"   📅 Created: {found_target.get('created_at', 'unknown')}")
                    print(f"   🏷️ Status: {found_target.get('status', 'unknown')}")
                    print(f"   🏠 Address: {found_target.get('property_address', 'No address')}")
                else:
                    print(f"\n❌ TARGET REPORT NOT FOUND: {target_report}")
                    print(f"   💡 It may have been deleted or is in a different organization")
                
            else:
                print(f"❌ API returned success=false: {result}")
                
        else:
            print(f"❌ Failed to retrieve reports: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    list_reports()