#!/usr/bin/env python3
"""
Test authentication with AWS Cognito
"""

import os
import sys
import asyncio
import requests
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

async def test_authentication():
    """Test authentication flow"""
    
    base_url = "http://localhost:8000"
    
    # Test credentials
    test_users = [
        {"email": "admin@test.com", "password": "Admin123!", "role": "admin"},
        {"email": "manager@test.com", "password": "Manager123!", "role": "manager"},
        {"email": "employee@test.com", "password": "Employee123!", "role": "employee"}
    ]
    
    print("🧪 Testing Authentication Flow")
    print("=" * 40)
    
    for user in test_users:
        print(f"\n👤 Testing {user['role']}: {user['email']}")
        
        # Test login
        try:
            login_response = requests.post(f"{base_url}/api/auth/login", json={
                "email": user["email"],
                "password": user["password"]
            })
            
            if login_response.status_code == 200:
                data = login_response.json()
                token = data["data"]["access_token"]
                print(f"  ✅ Login successful")
                
                # Test protected endpoint
                headers = {"Authorization": f"Bearer {token}"}
                me_response = requests.get(f"{base_url}/api/auth/me", headers=headers)
                
                if me_response.status_code == 200:
                    user_data = me_response.json()["data"]
                    print(f"  ✅ Token valid - Role: {user_data.get('role')}")
                else:
                    print(f"  ❌ Token validation failed: {me_response.status_code}")
                    
            else:
                print(f"  ❌ Login failed: {login_response.status_code}")
                print(f"     Error: {login_response.text}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print(f"\n🔗 Test complete. Backend running at: {base_url}")

if __name__ == "__main__":
    asyncio.run(test_authentication())