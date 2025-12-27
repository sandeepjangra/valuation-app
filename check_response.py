#!/usr/bin/env python3
"""
Simple test to see the response structure
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
        
        # Test data
        test_data = {
            "bank_code": "SBI",
            "template_id": "land-property",
            "property_address": "Test Property Address",
            "report_data": {
                "report_reference_number": "TEST-REF-12345",
                "applicant_name": "Test Applicant",
                "land_area": "1000",
                "boundaries_dimensions_table": [
                    {"direction": "North", "boundary": "Road", "dimension": "50 ft"}
                ]
            }
        }
        
        # Create report
        response = requests.post("http://localhost:8000/api/reports", json=test_data, headers=headers, timeout=10)
        
        print(f"Status: {response.status_code}")
        result = response.json()
        
        # Print the response structure
        print("\nResponse structure:")
        print(json.dumps(result, indent=2, default=str)[:1000] + "...")
        
    else:
        print(f"Auth failed: {auth_response.text}")

except Exception as e:
    print(f"Error: {e}")