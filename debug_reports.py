#!/usr/bin/env python3
"""
Debug script to check what reports exist and where
"""

import requests

def debug_reports():
    """Check what reports exist"""
    
    base_url = "http://localhost:8000"
    
    try:
        # Authenticate with sk-tindwal
        print("🔐 Authenticating with sk-tindwal...")
        auth_response = requests.post(f"{base_url}/api/auth/dev-login", json={
            "email": "admin@system.com",
            "organizationId": "sk-tindwal",
            "role": "system_admin"
        }, timeout=10)
        
        if auth_response.status_code == 200:
            token = auth_response.json()["data"]["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Get reports for sk-tindwal
            reports_response = requests.get(f"{base_url}/api/reports", headers=headers, timeout=10)
            
            if reports_response.status_code == 200:
                reports_data = reports_response.json()
                reports = reports_data.get("data", [])
                print(f"📊 sk-tindwal reports: {len(reports)} found")
                
                for i, report in enumerate(reports[:5]):
                    print(f"  {i+1}. ID: {report.get('report_id')}")
                    print(f"      Ref: {report.get('reference_number')}")
                    print(f"      Address: {report.get('property_address', 'N/A')}")
                    print(f"      Status: {report.get('status')}")
                    print(f"      Created: {report.get('created_at', 'N/A')}")
            else:
                print(f"❌ Failed to get sk-tindwal reports: {reports_response.status_code}")
        else:
            print(f"❌ sk-tindwal auth failed: {auth_response.text}")
        
        print("\n" + "="*50)
        
        # Also try with system-administration
        print("🔐 Authenticating with system-administration...")
        auth_response2 = requests.post(f"{base_url}/api/auth/dev-login", json={
            "email": "admin@system.com",
            "organizationId": "system-administration",
            "role": "system_admin"
        }, timeout=10)
        
        if auth_response2.status_code == 200:
            token2 = auth_response2.json()["data"]["access_token"]
            headers2 = {"Authorization": f"Bearer {token2}"}
            
            # Get reports for system-administration
            reports_response2 = requests.get(f"{base_url}/api/reports", headers=headers2, timeout=10)
            
            if reports_response2.status_code == 200:
                reports_data2 = reports_response2.json()
                reports2 = reports_data2.get("data", [])
                print(f"📊 system-administration reports: {len(reports2)} found")
                
                for i, report in enumerate(reports2[:5]):
                    print(f"  {i+1}. ID: {report.get('report_id')}")
                    print(f"      Ref: {report.get('reference_number')}")
                    print(f"      Address: {report.get('property_address', 'N/A')}")
                    print(f"      Status: {report.get('status')}")
                    print(f"      Created: {report.get('created_at', 'N/A')}")
            else:
                print(f"❌ Failed to get system-administration reports: {reports_response2.status_code}")
        else:
            print(f"❌ system-administration auth failed: {auth_response2.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_reports()