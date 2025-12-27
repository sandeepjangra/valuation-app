#!/usr/bin/env python3
"""
Test different request scenarios that might cause frontend null response
"""

import requests

def test_frontend_scenarios():
    """Test various scenarios that might cause frontend null response"""
    
    base_url = "http://localhost:8000"
    
    try:
        # Authenticate 
        auth_response = requests.post(f"{base_url}/api/auth/dev-login", json={
            "email": "admin@system.com",
            "organizationId": "system-administration", 
            "role": "system_admin"
        }, timeout=10)
        
        token = auth_response.json()["data"]["access_token"]
        report_id = "rpt_fe5432e36d95"  # Use existing report ID
        
        print("🧪 Testing different request scenarios that might cause null response...")
        
        # Scenario 1: Standard request (should work)
        print("\n1️⃣ Testing standard request...")
        headers1 = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        data1 = {"report_data": {"test": "scenario1"}, "status": "draft"}
        
        response1 = requests.put(f"{base_url}/api/reports/{report_id}", json=data1, headers=headers1, timeout=10)
        print(f"   Status: {response1.status_code}")
        if response1.status_code == 200:
            resp_json = response1.json()
            print(f"   Success: {resp_json.get('success')}")
            print(f"   Has data: {'data' in resp_json}")
        
        # Scenario 2: Missing Content-Type header
        print("\n2️⃣ Testing without Content-Type header...")
        headers2 = {"Authorization": f"Bearer {token}"}
        data2 = {"report_data": {"test": "scenario2"}, "status": "draft"}
        
        response2 = requests.put(f"{base_url}/api/reports/{report_id}", json=data2, headers=headers2, timeout=10)
        print(f"   Status: {response2.status_code}")
        if response2.status_code == 200:
            resp_json = response2.json()
            print(f"   Success: {resp_json.get('success')}")
        
        # Scenario 3: Using data parameter instead of json
        print("\n3️⃣ Testing with data parameter instead of json...")
        headers3 = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        import json
        data3_str = json.dumps({"report_data": {"test": "scenario3"}, "status": "draft"})
        
        response3 = requests.put(f"{base_url}/api/reports/{report_id}", data=data3_str, headers=headers3, timeout=10)
        print(f"   Status: {response3.status_code}")
        if response3.status_code == 200:
            resp_json = response3.json()
            print(f"   Success: {resp_json.get('success')}")
        
        # Scenario 4: Empty report_data
        print("\n4️⃣ Testing with empty report_data...")
        headers4 = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        data4 = {"report_data": {}, "status": "draft"}
        
        response4 = requests.put(f"{base_url}/api/reports/{report_id}", json=data4, headers=headers4, timeout=10)
        print(f"   Status: {response4.status_code}")
        if response4.status_code == 200:
            resp_json = response4.json()
            print(f"   Success: {resp_json.get('success')}")
            
        # Scenario 5: Large payload (might cause issues)
        print("\n5️⃣ Testing with large payload...")
        headers5 = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        large_data = {"report_data": {f"field_{i}": f"value_{i}" for i in range(100)}, "status": "draft"}
        
        response5 = requests.put(f"{base_url}/api/reports/{report_id}", json=large_data, headers=headers5, timeout=10)
        print(f"   Status: {response5.status_code}")
        if response5.status_code == 200:
            resp_json = response5.json()
            print(f"   Success: {resp_json.get('success')}")
            print(f"   Response size: {len(response5.text)} bytes")
        
        print(f"\n✅ All scenarios tested. If all returned success: True, the backend is working correctly.")
        print(f"   The null response issue is likely in the frontend JavaScript code.")
            
    except Exception as e:
        print(f"❌ Test error: {str(e)}")

if __name__ == "__main__":
    test_frontend_scenarios()