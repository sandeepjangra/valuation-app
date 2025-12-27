#!/usr/bin/env python3

import requests

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
        
        # Get reports
        response = requests.get("http://localhost:8000/api/reports", headers=headers, timeout=10)
        result = response.json()
        
        print("Response type:", type(result))
        print("Response keys:" if isinstance(result, dict) else "Response length:", 
              list(result.keys()) if isinstance(result, dict) else len(result) if isinstance(result, list) else "Unknown")
        
        if isinstance(result, dict) and 'data' in result:
            reports = result['data']
            print(f"Found {len(reports)} reports")
            for report in reports[:3]:
                print(f"  - ID: {report.get('report_id', 'Unknown')}, Ref: {report.get('reference_number', 'None')}")
        elif isinstance(result, list):
            print(f"Found {len(result)} reports")
            for report in result[:3]:
                print(f"  - ID: {report.get('report_id', 'Unknown')}, Ref: {report.get('reference_number', 'None')}")

except Exception as e:
    print(f"Error: {e}")