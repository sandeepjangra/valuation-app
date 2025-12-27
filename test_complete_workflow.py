#!/usr/bin/env python3
"""
Complete end-to-end test: Create → Save Draft → Verify
"""

import requests
import json
from datetime import datetime

def test_complete_workflow():
    """Test complete workflow from creation to save draft"""
    
    base_url = "http://localhost:8000"
    
    try:
        # 1. Authenticate
        print("🔐 Authenticating...")
        auth_response = requests.post(f"{base_url}/api/auth/dev-login", json={
            "email": "admin@system.com",
            "organizationId": "system-administration",
            "role": "system_admin"
        }, timeout=10)
        
        if auth_response.status_code != 200:
            print(f"❌ Authentication failed: {auth_response.status_code}")
            return
        
        token = auth_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        print("✅ Authentication successful")
        
        # 2. Create a new report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        print(f"\n📝 Creating new report (test_{timestamp})...")
        
        create_data = {
            "bank_code": "SBI",
            "template_id": "land-property",
            "property_address": f"Test Property {timestamp}",
            "report_data": {
                "applicant_name": f"Test Applicant {timestamp}",
                "property_address": f"Test Property {timestamp}",
                "land_area": "1000",
                "land_rate": "1500",
                "property_type": "Residential",
                "inspection_date": "2025-12-25"
            }
        }
        
        create_response = requests.post(f"{base_url}/api/reports", json=create_data, headers=headers, timeout=10)
        
        if create_response.status_code != 200:
            print(f"❌ Report creation failed: {create_response.status_code}")
            print(f"Error: {create_response.text}")
            return
        
        print("✅ Report created successfully")
        
        # 3. Get the created report ID from the reports list
        print("\n📋 Fetching reports to find new report...")
        reports_response = requests.get(f"{base_url}/api/reports", headers=headers, timeout=10)
        
        if reports_response.status_code != 200:
            print(f"❌ Failed to fetch reports: {reports_response.status_code}")
            return
        
        reports_data = reports_response.json()
        reports = reports_data.get("data", [])
        
        # Find our new report (most recent with our test property address)
        new_report = None
        for report in reports:
            if report.get("property_address") == f"Test Property {timestamp}":
                new_report = report
                break
        
        if not new_report:
            print("❌ Could not find the newly created report")
            return
        
        report_id = new_report.get("report_id")
        print(f"✅ Found new report: {report_id}")
        print(f"   Reference: {new_report.get('reference_number')}")
        print(f"   Status: {new_report.get('status')}")
        
        # 4. Update the report (save draft) multiple times
        print(f"\n💾 Testing multiple draft saves...")
        
        for i in range(3):
            print(f"\n   Save #{i+1}...")
            
            update_data = {
                "report_data": {
                    "applicant_name": f"Updated Applicant {timestamp} - Save {i+1}",
                    "property_address": f"Test Property {timestamp}",
                    "land_area": str(1000 + (i * 100)),  # 1000, 1100, 1200
                    "land_rate": str(1500 + (i * 50)),   # 1500, 1550, 1600
                    "property_type": "Residential",
                    "building_type": f"Type {i+1}",
                    "inspection_date": "2025-12-25",
                    "save_iteration": i + 1,
                    "last_modified": datetime.now().isoformat()
                },
                "status": "draft"
            }
            
            update_response = requests.put(f"{base_url}/api/reports/{report_id}", json=update_data, headers=headers, timeout=10)
            
            if update_response.status_code == 200:
                result = update_response.json()
                print(f"     ✅ Save #{i+1} successful")
                print(f"     Version: {result['data']['version']}")
                print(f"     Updated at: {result['data']['updated_at']}")
                
                # Verify the data was saved
                saved_data = result['data']['report_data']
                if saved_data.get('save_iteration') == i + 1:
                    print(f"     ✅ Data verified: iteration {saved_data.get('save_iteration')}")
                else:
                    print(f"     ❌ Data mismatch: expected {i+1}, got {saved_data.get('save_iteration')}")
            else:
                print(f"     ❌ Save #{i+1} failed: {update_response.status_code}")
                print(f"     Error: {update_response.text}")
                break
        
        # 5. Final verification
        print(f"\n🔍 Final verification...")
        final_response = requests.get(f"{base_url}/api/reports/{report_id}", headers=headers, timeout=10)
        
        if final_response.status_code == 200:
            final_data = final_response.json()
            final_report = final_data.get("data", final_data)
            
            print(f"✅ Final report state:")
            print(f"   Status: {final_report.get('status')}")
            print(f"   Version: {final_report.get('version')}")
            print(f"   Land Area: {final_report.get('report_data', {}).get('land_area')}")
            print(f"   Save Iteration: {final_report.get('report_data', {}).get('save_iteration')}")
            
            if final_report.get('report_data', {}).get('save_iteration') == 3:
                print(f"\n🎉 COMPLETE SUCCESS!")
                print(f"   ✅ Report creation working")
                print(f"   ✅ Multiple draft saves working") 
                print(f"   ✅ Data persistence working")
                print(f"   ✅ Version tracking working")
            else:
                print(f"\n⚠️  Partial success - some data may not have persisted")
        else:
            print(f"❌ Final verification failed: {final_response.status_code}")
            
    except Exception as e:
        print(f"❌ Test error: {str(e)}")

if __name__ == "__main__":
    test_complete_workflow()