#!/usr/bin/env python3
"""
Test save draft functionality
"""

import requests
import json

def test_save_draft():
    """Test saving a report as draft"""
    
    base_url = "http://localhost:8000"
    
    try:
        # 1. First authenticate
        print("🔐 Authenticating...")
        auth_response = requests.post(f"{base_url}/api/auth/dev-login", json={
            "email": "admin@system.com",
            "organizationId": "sk-tindwal",
            "role": "system_admin"
        }, timeout=10)
        
        if auth_response.status_code != 200:
            print(f"❌ Authentication failed: {auth_response.status_code}")
            print(f"Response: {auth_response.text}")
            return
        
        token = auth_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        print("✅ Authentication successful")
        
        # 2. Create a new report first
        print("\n📝 Creating a new report...")
        create_data = {
            "bank_code": "SBI",
            "template_id": "land-property",
            "property_address": "Test Property for Draft Save",
            "report_data": {
                "applicant_name": "Test Applicant",
                "property_address": "Test Property for Draft Save",
                "land_area": "500",
                "land_rate": "1000"
            }
        }
        
        create_response = requests.post(f"{base_url}/api/reports", json=create_data, headers=headers, timeout=10)
        
        if create_response.status_code != 200:
            print(f"❌ Report creation failed: {create_response.status_code}")
            print(f"Response: {create_response.text}")
            return
        
        print("✅ Report created successfully")
        
        # 3. Get the list of reports to find our new report
        print("\n📋 Fetching reports to get report ID...")
        reports_response = requests.get(f"{base_url}/api/reports", headers=headers, timeout=10)
        
        if reports_response.status_code != 200:
            print(f"❌ Failed to fetch reports: {reports_response.status_code}")
            return
        
        reports_data = reports_response.json()
        reports = reports_data.get("data", [])
        
        # Find our test report
        test_report = None
        for report in reports:
            if report.get("property_address") == "Test Property for Draft Save":
                test_report = report
                break
        
        if not test_report:
            print("❌ Could not find the created test report")
            return
        
        report_id = test_report.get("report_id")
        print(f"✅ Found test report with ID: {report_id}")
        
        # 4. Now test updating the report (save draft)
        print(f"\n💾 Testing save draft for report: {report_id}")
        
        update_data = {
            "report_data": {
                "applicant_name": "Updated Test Applicant",
                "property_address": "Test Property for Draft Save",
                "land_area": "750",  # Changed value
                "land_rate": "1200",  # Changed value
                "building_type": "Commercial",  # New field
                "inspection_date": "2024-12-25"  # New field
            },
            "status": "draft"  # Explicitly set as draft
        }
        
        update_response = requests.put(f"{base_url}/api/reports/{report_id}", json=update_data, headers=headers, timeout=10)
        
        print(f"📨 Update response status: {update_response.status_code}")
        
        if update_response.status_code == 200:
            print("✅ Save draft successful!")
            
            # 5. Verify the update by fetching the report again
            print("\n🔍 Verifying the saved changes...")
            get_response = requests.get(f"{base_url}/api/reports/{report_id}", headers=headers, timeout=10)
            
            if get_response.status_code == 200:
                updated_report = get_response.json()
                print("✅ Report retrieved successfully")
                
                # Check if changes were saved
                report_data = updated_report.get("report_data", {})
                
                print(f"📊 Updated values:")
                print(f"  Land Area: {report_data.get('land_area', 'Not found')}")
                print(f"  Land Rate: {report_data.get('land_rate', 'Not found')}")
                print(f"  Building Type: {report_data.get('building_type', 'Not found')}")
                print(f"  Status: {updated_report.get('status', 'Not found')}")
                
                if report_data.get("land_area") == "750":
                    print("🎉 SUCCESS: Draft save is working correctly!")
                else:
                    print("❌ ISSUE: Changes were not saved properly")
            else:
                print(f"❌ Failed to retrieve updated report: {get_response.status_code}")
        else:
            print(f"❌ Save draft failed: {update_response.status_code}")
            print(f"Error response: {update_response.text}")
            
    except Exception as e:
        print(f"❌ Test error: {str(e)}")

if __name__ == "__main__":
    test_save_draft()