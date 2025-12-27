#!/usr/bin/env python3
"""
Test which MongoDB collection reports are created in
"""

import requests
from datetime import datetime

def test_report_creation_location():
    """Test exactly where reports are being created in MongoDB"""
    
    base_url = "http://localhost:8000"
    timestamp = datetime.now().strftime("%H%M%S")
    
    try:
        print(f"🧪 Testing report creation location at {timestamp}")
        print("="*60)
        
        # Test with system-administration
        print("\n1️⃣ Testing with system-administration organization...")
        auth_response = requests.post(f"{base_url}/api/auth/dev-login", json={
            "email": "admin@system.com",
            "organizationId": "system-administration",
            "role": "system_admin"
        }, timeout=10)
        
        if auth_response.status_code == 200:
            token = auth_response.json()["data"]["access_token"]
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            
            create_data = {
                "bank_code": "SBI",
                "template_id": "land-property",
                "property_address": f"LOCATION_TEST_{timestamp}_SYSADM",
                "report_data": {
                    "applicant_name": f"Test Location {timestamp}",
                    "created_timestamp": timestamp,
                    "test_organization": "system-administration"
                }
            }
            
            print("   📤 Creating report in system-administration context...")
            create_response = requests.post(f"{base_url}/api/reports", json=create_data, headers=headers, timeout=10)
            
            print(f"   📨 Response: {create_response.status_code}")
            if create_response.status_code == 200:
                print("   ✅ Report created successfully")
                print(f"   📍 MongoDB Collection: 'system-administration.reports'")
            else:
                print(f"   ❌ Failed: {create_response.text}")
                
        print("\n" + "="*60)
        
        # Test with sk-tindwal
        print("\n2️⃣ Testing with sk-tindwal organization...")
        auth_response2 = requests.post(f"{base_url}/api/auth/dev-login", json={
            "email": "admin@system.com",
            "organizationId": "sk-tindwal",
            "role": "system_admin"
        }, timeout=10)
        
        if auth_response2.status_code == 200:
            token2 = auth_response2.json()["data"]["access_token"]
            headers2 = {"Authorization": f"Bearer {token2}", "Content-Type": "application/json"}
            
            create_data2 = {
                "bank_code": "SBI", 
                "template_id": "land-property",
                "property_address": f"LOCATION_TEST_{timestamp}_SKTINDWAL",
                "report_data": {
                    "applicant_name": f"Test Location {timestamp}",
                    "created_timestamp": timestamp,
                    "test_organization": "sk-tindwal"
                }
            }
            
            print("   📤 Creating report in sk-tindwal context...")
            create_response2 = requests.post(f"{base_url}/api/reports", json=create_data2, headers=headers2, timeout=10)
            
            print(f"   📨 Response: {create_response2.status_code}")
            if create_response2.status_code == 200:
                print("   ✅ Report created successfully")
                print(f"   📍 MongoDB Collection: 'sk-tindwal.reports'")
            else:
                print(f"   ❌ Failed: {create_response2.text}")
        
        print(f"\n📊 Summary - Check these MongoDB collections:")
        print(f"   🗂️  system-administration.reports (for system-administration org)")
        print(f"   🗂️  sk-tindwal.reports (for sk-tindwal org)")  
        print(f"   🔍 Search for reports with property_address containing: 'LOCATION_TEST_{timestamp}'")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_report_creation_location()