#!/usr/bin/env python3

import requests

try:
    # Get auth token
    auth_response = requests.post("http://localhost:8000/api/auth/dev-login", json={
        "email": "admin@system.com",
        "organizationId": "system_org_id",  
        "role": "system_admin"
    }, timeout=10)
    
    if auth_response.status_code == 200:
        token = auth_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get organizations
        orgs_response = requests.get("http://localhost:8000/api/organizations", headers=headers, timeout=10)
        
        print(f"Organizations API response: {orgs_response.status_code}")
        
        if orgs_response.status_code == 200:
            orgs = orgs_response.json()
            
            if isinstance(orgs, list):
                print("Available Organizations:")
                for i, org in enumerate(orgs[:10]):
                    print(f"{i+1}. ID: '{org.get('id')}', Name: '{org.get('organizationName')}'")
            else:
                print(f"Response keys: {orgs.keys()}")
                orgs = orgs.get("data", orgs)  # Handle different response formats
                if isinstance(orgs, list):
                    print("Available Organizations:")
                    for i, org in enumerate(orgs[:10]):
                        print(f"{i+1}. ID: '{org.get('id')}', Name: '{org.get('organizationName')}'")
                else:
                    print("Organizations response is not a list:", type(orgs))
                    print("Sample content:", str(orgs)[:200])
        else:
            print(f"Failed to get orgs: {orgs_response.status_code} - {orgs_response.text}")
    else:
        print(f"Auth failed: {auth_response.text}")

except Exception as e:
    print(f"Error: {e}")