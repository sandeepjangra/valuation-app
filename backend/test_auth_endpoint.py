#!/usr/bin/env python3
"""
Test the authentication endpoints to verify they're working
"""

import asyncio
import requests
import json
from datetime import datetime

def test_auth_endpoints():
    """Test authentication endpoints"""
    
    base_url = "http://localhost:8000"
    
    print("🔐 Testing Authentication Endpoints")
    print("=" * 50)
    
    # Test health endpoint first
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        print(f"✅ Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test dev login endpoint
    dev_login_data = {
        "email": "manager@test.com",
        "organizationId": "sk-tindwal",
        "role": "manager"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/dev-login",
            json=dev_login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"🧪 Dev login response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dev login successful!")
            print(f"   Token: {data['data']['access_token'][:50]}...")
            print(f"   User: {data['data']['user']['email']}")
            print(f"   Org: {data['data']['user']['org_short_name']}")
            
            # Test creating a template with this token
            token = data['data']['access_token']
            return test_template_creation_with_token(base_url, token)
            
        else:
            print(f"❌ Dev login failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Dev login error: {e}")
        return False

def test_template_creation_with_token(base_url, token):
    """Test template creation with authentication token"""
    
    print(f"\n📝 Testing Template Creation with Token")
    print("=" * 50)
    
    template_data = {
        "templateName": f"API Test Template {datetime.now().strftime('%H%M%S')}",
        "description": "Test template created via API",
        "bankCode": "SBI",
        "propertyType": "land",
        "fieldValues": {
            "property_area": "2000 sq ft",
            "property_value": "6000000",
            "location": "API Test Location",
            "survey_number": "789/012",
            "village": "API Test Village"
        }
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/custom-templates",
            json=template_data,
            headers=headers,
            timeout=15
        )
        
        print(f"📝 Template creation response: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Template created successfully!")
            print(f"   Template ID: {data['data']['_id']}")
            print(f"   Template Name: {data['data']['templateName']}")
            print(f"   Bank: {data['data']['bankCode']}")
            return True
        else:
            print(f"❌ Template creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Template creation error: {e}")
        return False

if __name__ == "__main__":
    success = test_auth_endpoints()
    if success:
        print(f"\n🎉 All API tests passed!")
    else:
        print(f"\n❌ API tests failed!")