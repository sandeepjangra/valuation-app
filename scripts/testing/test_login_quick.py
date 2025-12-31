#!/usr/bin/env python3
"""
Quick test with admin credentials
"""

import requests
import json

def test_admin_login():
    """Test login with admin credentials"""
    
    base_url = "http://localhost:8000"
    
    # Try different credential combinations
    test_credentials = [
        {"email": "admin@admin.com", "password": "admin123"},
        {"email": "admin@system.com", "password": "admin123"}, 
        {"email": "system@admin.com", "password": "admin123"},
        {"email": "sk@tindwal.com", "password": "password123"},
        {"email": "sk@tindwal.com", "password": "admin123"}
    ]
    
    print("🔐 Testing different login credentials...")
    
    for i, creds in enumerate(test_credentials):
        print(f"\\n{i+1}. Testing: {creds['email']} / {creds['password']}")
        
        try:
            response = requests.post(f"{base_url}/api/auth/login", json=creds, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"   ✅ SUCCESS! Token: {result['data']['access_token'][:50]}...")
                    return creds, result['data']['access_token']
                else:
                    print(f"   ❌ Failed: {result}")
            else:
                print(f"   ❌ HTTP Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\\n❌ No valid credentials found")
    return None, None

def test_organizations_with_token(token):
    """Test organizations endpoint with token"""
    
    if not token:
        print("No token available")
        return
    
    base_url = "http://localhost:8000"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{base_url}/api/organizations", headers=headers, timeout=10)
        print(f"\\n📊 Organizations response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Organizations: {json.dumps(result, indent=2)}")
        else:
            print(f"Organizations error: {response.text}")
            
    except Exception as e:
        print(f"Organizations request error: {e}")

if __name__ == "__main__":
    creds, token = test_admin_login()
    if token:
        test_organizations_with_token(token)