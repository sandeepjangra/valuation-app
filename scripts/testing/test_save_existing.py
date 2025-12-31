#!/usr/bin/env python3
"""
Test save draft with existing report from system-administration
"""

import requests

def test_save_draft_existing():
    """Test saving an existing report as draft"""
    
    base_url = "http://localhost:8000"
    
    try:
        # Authenticate with system-administration (where the reports exist)
        print("🔐 Authenticating with system-administration...")
        auth_response = requests.post(f"{base_url}/api/auth/dev-login", json={
            "email": "admin@system.com",
            "organizationId": "system-administration",
            "role": "system_admin"
        }, timeout=10)
        
        if auth_response.status_code != 200:
            print(f"❌ Authentication failed: {auth_response.status_code}")
            print(f"Response: {auth_response.text}")
            return
        
        token = auth_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        print("✅ Authentication successful")
        
        # Use the existing report ID from our debug
        report_id = "rpt_fe5432e36d95"  # Existing report
        
        print(f"\n💾 Testing save draft for existing report: {report_id}")
        
        # First, get the current report data
        get_response = requests.get(f"{base_url}/api/reports/{report_id}", headers=headers, timeout=10)
        
        if get_response.status_code != 200:
            print(f"❌ Failed to get existing report: {get_response.status_code}")
            print(f"Response: {get_response.text}")
            return
        
        current_report = get_response.json()
        print(f"✅ Current report retrieved")
        print(f"   Current status: {current_report.get('status')}")
        print(f"   Current address: {current_report.get('property_address')}")
        
        # Now update the report (save draft)
        update_data = {
            "report_data": {
                "applicant_name": "Updated via API Test",
                "property_address": "Test Property Address - UPDATED",
                "land_area": "999",  # Updated value
                "land_rate": "2000",  # Updated value
                "building_type": "Mixed Use",  # New field
                "inspection_date": "2024-12-25",  # New field
                "test_field": f"Updated at {requests.utils.default_headers()}"  # Timestamp field
            },
            "status": "draft"  # Keep as draft
        }
        
        print(f"\n🔄 Sending update request...")
        update_response = requests.put(f"{base_url}/api/reports/{report_id}", json=update_data, headers=headers, timeout=10)
        
        print(f"📨 Update response status: {update_response.status_code}")
        
        if update_response.status_code == 200:
            update_result = update_response.json()
            print("✅ Save draft successful!")
            print(f"   Response: {update_result}")
            
            # Verify the update by fetching the report again
            print(f"\n🔍 Verifying the saved changes...")
            verify_response = requests.get(f"{base_url}/api/reports/{report_id}", headers=headers, timeout=10)
            
            if verify_response.status_code == 200:
                response_data = verify_response.json()
                updated_report = response_data.get("data", response_data)  # Handle nested response
                print("✅ Updated report retrieved successfully")
                
                # Check if changes were saved
                report_data = updated_report.get("report_data", {})
                
                print(f"\n📊 Verification Results:")
                print(f"  Land Area: {report_data.get('land_area', 'Not found')}")
                print(f"  Land Rate: {report_data.get('land_rate', 'Not found')}")
                print(f"  Building Type: {report_data.get('building_type', 'Not found')}")
                print(f"  Status: {updated_report.get('status', 'Not found')}")
                print(f"  Updated At: {updated_report.get('updated_at', 'Not found')}")
                print(f"  Version: {updated_report.get('version', 'Not found')}")
                
                # Check if our test field was saved
                if report_data.get("land_area") == "999":
                    print("\n🎉 SUCCESS: Draft save is working correctly!")
                    print("   ✅ All changes were saved properly")
                else:
                    print("\n❌ ISSUE: Changes were not saved properly")
                    print(f"   Expected land_area: 999, Got: {report_data.get('land_area')}")
                    
                    # Debug: show what we actually got
                    if isinstance(report_data, dict):
                        print(f"   Available keys in report_data: {list(report_data.keys())[:10]}")
                    else:
                        print(f"   report_data type: {type(report_data)}")
            else:
                print(f"❌ Failed to retrieve updated report: {verify_response.status_code}")
                print(f"Response: {verify_response.text}")
        else:
            print(f"❌ Save draft failed: {update_response.status_code}")
            print(f"Error response: {update_response.text}")
            
    except Exception as e:
        print(f"❌ Test error: {str(e)}")

if __name__ == "__main__":
    test_save_draft_existing()