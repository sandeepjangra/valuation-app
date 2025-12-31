#!/usr/bin/env python3

import requests

def check_existing_reports():
    """Check what reports exist via API"""
    
    BASE_URL = "http://localhost:8000/api"
    
    # Login as system admin to see all organizations
    print("🔐 Logging in as system admin...")
    login_data = {
        "email": "system@admin.com",
        "organizationId": "system_admin", 
        "role": "system_admin"
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/dev-login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Failed to login as system admin: {login_response.status_code}")
        return False
    
    auth_data = login_response.json()
    token = auth_data['data']['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Logged in as system admin")
    
    # Try to get organizations
    print("\n📋 Getting organizations...")
    orgs_response = requests.get(f"{BASE_URL}/admin/organizations", headers=headers)
    
    if orgs_response.status_code == 200:
        orgs_data = orgs_response.json()
        print(f"Found {len(orgs_data.get('organizations', []))} organizations:")
        
        for org in orgs_data.get('organizations', []):
            print(f"  • {org.get('short_name', 'N/A')}: {org.get('name', 'N/A')}")
    else:
        print(f"❌ Failed to get organizations: {orgs_response.status_code}")
    
    # Try sk-tindwal reports with different token
    print(f"\n🔐 Switching to sk-tindwal context...")
    login_data = {
        "email": "admin@sk-tindwal.com",
        "organizationId": "sk-tindwal", 
        "role": "manager"
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/dev-login", json=login_data)
    auth_data = login_response.json()
    token = auth_data['data']['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Logged in as sk-tindwal admin")
    
    # Check reports with more details
    print("\n📋 Getting reports for sk-tindwal...")
    reports_response = requests.get(f"{BASE_URL}/reports?limit=10", headers=headers)
    
    if reports_response.status_code == 200:
        reports_data = reports_response.json()
        print(f"Found {len(reports_data.get('reports', []))} reports")
        print(f"Pagination info: {reports_data.get('pagination', {})}")
        
        if reports_data.get('reports'):
            print(f"\nFirst report structure:")
            first_report = reports_data['reports'][0]
            print(f"  • ID: {first_report.get('_id')}")
            print(f"  • Status: {first_report.get('status')}")
            print(f"  • Created: {first_report.get('created_at')}")
            print(f"  • Top-level keys: {list(first_report.keys())}")
    else:
        print(f"❌ Failed to get reports: {reports_response.status_code}")
        print(f"Response: {reports_response.text}")

if __name__ == "__main__":
    check_existing_reports()