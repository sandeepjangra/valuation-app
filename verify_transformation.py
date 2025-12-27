#!/usr/bin/env python3
"""
Test to verify the report was saved with proper template structure
"""

import requests
import json

try:
    # Get auth token
    auth_response = requests.post("http://localhost:8000/api/auth/dev-login", json={
        "email": "admin@system.com",
        "organizationId": "69230833b51083d26dab6087",
        "role": "system_admin"
    }, timeout=10)
    
    if auth_response.status_code == 200:
        token = auth_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print("🔍 Fetching reports to verify transformation...")
        
        # Get list of reports
        reports_response = requests.get("http://localhost:8000/api/reports", headers=headers, timeout=10)
        
        print(f"Reports API status: {reports_response.status_code}")
        
        if reports_response.status_code == 200:
            reports = reports_response.json()
            print(f"Found {len(reports)} reports" if isinstance(reports, list) else "Reports response format unexpected")
            
            # Look for our test report
            test_reports = []
            if isinstance(reports, list):
                for report in reports:
                    if report.get("reference_number") == "TEST-REF-12345":
                        test_reports.append(report)
            
            if test_reports:
                print(f"\n🎉 Found our test report: {test_reports[0].get('reference_number')}")
                report = test_reports[0]
                
                # Check the report_data structure
                report_data = report.get("report_data", {})
                print(f"\nReport data structure analysis:")
                print(f"📊 Top-level keys: {list(report_data.keys())}")
                
                # Check for template tabs
                expected_tabs = [
                    "Property Details", 
                    "Site Characteristics", 
                    "Valuation", 
                    "Construction Specifications", 
                    "Detailed Valuation"
                ]
                
                found_tabs = []
                for tab in expected_tabs:
                    if tab in report_data:
                        found_tabs.append(tab)
                        tab_data = report_data[tab]
                        if isinstance(tab_data, dict) and "documents" in tab_data:
                            doc_count = len(tab_data["documents"])
                            print(f"  ✅ {tab}: {doc_count} fields")
                        else:
                            print(f"  ⚠️  {tab}: No documents structure")
                    else:
                        print(f"  ❌ {tab}: Missing")
                
                if len(found_tabs) > 0:
                    print(f"\n🎉 TRANSFORMATION SUCCESS! Report saved with {len(found_tabs)}/{len(expected_tabs)} tabs")
                    
                    # Show sample of transformed data
                    for tab in found_tabs[:2]:
                        tab_data = report_data[tab]
                        if isinstance(tab_data, dict) and "documents" in tab_data:
                            print(f"\n📄 Sample from {tab}:")
                            for i, doc in enumerate(tab_data["documents"][:3]):
                                if isinstance(doc, dict):
                                    field_id = doc.get("fieldId", "Unknown")
                                    value = doc.get("value", "No value")
                                    print(f"    {i+1}. {field_id}: {value}")
                else:
                    print(f"\n❌ TRANSFORMATION FAILED: No template tabs found")
                    print(f"Raw keys found: {list(report_data.keys())[:10]}")
            else:
                print("❌ Test report not found")
        else:
            print(f"Failed to fetch reports: {reports_response.text}")
    else:
        print(f"Auth failed: {auth_response.text}")

except Exception as e:
    print(f"Error: {e}")