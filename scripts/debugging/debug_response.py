#!/usr/bin/env python3
"""
Test to debug the exact response format issue the frontend is seeing
"""

import requests
import json

def debug_response_format():
    """Debug the exact response format that might be causing frontend issues"""
    
    base_url = "http://localhost:8000"
    
    try:
        # Authenticate 
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
        
        # Use existing report
        report_id = "rpt_fe5432e36d95"
        
        # Test update with minimal data (like frontend might send)
        update_data = {
            "report_data": {
                "applicant_name": "Frontend Test Update",
                "test_timestamp": "2025-12-25T21:30:00"
            },
            "status": "draft"
        }
        
        print(f"\n🔄 Sending update request...")
        print(f"Request URL: {base_url}/api/reports/{report_id}")
        print(f"Request headers: {headers}")
        print(f"Request body: {json.dumps(update_data, indent=2)}")
        
        # Make the request
        response = requests.put(f"{base_url}/api/reports/{report_id}", json=update_data, headers=headers, timeout=10)
        
        print(f"\n📨 Response Analysis:")
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        # Check raw response
        print(f"\nRaw Response Text: '{response.text}'")
        print(f"Response Length: {len(response.text)}")
        
        # Try to parse JSON
        try:
            json_response = response.json()
            print(f"Parsed JSON: {json.dumps(json_response, indent=2)}")
            print(f"JSON Type: {type(json_response)}")
            
            if json_response is None:
                print("❌ ISSUE FOUND: JSON response is None!")
            elif isinstance(json_response, dict):
                if "success" in json_response:
                    print(f"✅ Success property found: {json_response['success']}")
                else:
                    print("❌ ISSUE: 'success' property missing from response")
                    print(f"Available keys: {list(json_response.keys())}")
            else:
                print(f"❌ ISSUE: Response is not a dict, it's: {type(json_response)}")
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parse Error: {e}")
            print("Response is not valid JSON")
        except Exception as e:
            print(f"❌ Other JSON Error: {e}")
            
        # Check content type
        content_type = response.headers.get('content-type', 'Not specified')
        print(f"\nContent-Type: {content_type}")
        
        if 'application/json' not in content_type.lower():
            print("⚠️  WARNING: Content-Type is not application/json")
            
    except Exception as e:
        print(f"❌ Test error: {str(e)}")

if __name__ == "__main__":
    debug_response_format()