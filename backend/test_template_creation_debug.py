#!/usr/bin/env python3
"""
Debug template creation to see which database is being used
"""

import requests
import json

def test_template_creation():
    """Test creating a template as admin in sk-tindwal"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Template Creation Debug")
    print("=" * 50)
    
    # Login as admin in sk-tindwal
    dev_login_data = {
        "email": "admin@system.com",
        "organizationId": "sk-tindwal",
        "role": "system_admin"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/dev-login",
            json=dev_login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            return False
            
        login_data = response.json()
        token = login_data['data']['access_token']
        user_info = login_data['data']['user']
        
        print(f"✅ Admin logged in:")
        print(f"   Email: {user_info['email']}")
        print(f"   Org: {user_info['org_short_name']}")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Create a test template
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    template_data = {
        "templateName": f"Debug Template {json.dumps({'timestamp': '2024-12-02T15:30:00'})}",
        "description": "Debug template to test database selection",
        "bankCode": "HDFC",
        "propertyType": "land",
        "fieldValues": {
            "test_field_1": "test_value_1",
            "test_field_2": "test_value_2"
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/custom-templates",
            json=template_data,
            headers=headers,
            timeout=10
        )
        
        print(f"\n📝 Create Template Response: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            template_info = data.get('data', {})
            
            print(f"✅ Template created successfully:")
            print(f"   Template ID: {template_info.get('_id')}")
            print(f"   Template Name: {template_info.get('templateName')}")
            print(f"   Bank Code: {template_info.get('bankCode')}")
            print(f"   Property Type: {template_info.get('propertyType')}")
            
            return template_info.get('_id')
            
        else:
            print(f"❌ Template creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Template creation error: {e}")
        return None

def test_template_listing():
    """Test listing templates as admin in sk-tindwal"""
    
    base_url = "http://localhost:8000"
    
    print("\n🔍 Testing Template Listing")
    print("=" * 30)
    
    # Login as admin in sk-tindwal
    dev_login_data = {
        "email": "admin@system.com",
        "organizationId": "sk-tindwal",
        "role": "system_admin"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/dev-login",
            json=dev_login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            return False
            
        login_data = response.json()
        token = login_data['data']['access_token']
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # List templates
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{base_url}/api/custom-templates",
            headers=headers,
            timeout=10
        )
        
        print(f"📋 List Templates Response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            templates = data.get('data', [])
            
            print(f"✅ Templates found: {len(templates)}")
            
            for template in templates:
                print(f"   - {template.get('templateName')}")
                print(f"     ID: {template.get('_id')}")
                print(f"     Created by: {template.get('createdByName')}")
                print(f"     Org ID: {template.get('organizationId')}")
                print(f"     Bank: {template.get('bankCode')}")
                print()
            
            return True
            
        else:
            print(f"❌ List templates failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ List templates error: {e}")
        return False

if __name__ == "__main__":
    # Test template creation
    template_id = test_template_creation()
    
    # Test template listing
    test_template_listing()
    
    print(f"\n🎯 Summary:")
    if template_id:
        print(f"   ✅ Template created with ID: {template_id}")
        print(f"   🔍 Check which database it was saved to by running the list test")
    else:
        print(f"   ❌ Template creation failed")