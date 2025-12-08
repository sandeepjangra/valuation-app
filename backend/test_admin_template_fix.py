#!/usr/bin/env python3
"""
Test script to verify that admin users save templates to the correct organization
"""

import requests
import json
from datetime import datetime

def test_admin_template_creation():
    """Test template creation as admin in sk-tindwal organization"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Admin Template Creation Fix")
    print("=" * 50)
    
    # Step 1: Login as admin in sk-tindwal organization
    dev_login_data = {
        "email": "admin@system.com",
        "organizationId": "sk-tindwal",  # Admin working in sk-tindwal org
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
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
            
        login_data = response.json()
        token = login_data['data']['access_token']
        user_info = login_data['data']['user']
        
        print(f"✅ Admin logged in successfully")
        print(f"   User: {user_info['email']}")
        print(f"   Org: {user_info['org_short_name']}")
        print(f"   Token: {token[:50]}...")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Step 2: Create a template
    template_data = {
        "templateName": f"Admin Test Template {datetime.now().strftime('%H%M%S')}",
        "description": "Test template created by admin in sk-tindwal",
        "bankCode": "SBI",
        "propertyType": "land",
        "fieldValues": {
            "admin_test_field": "admin_test_value",
            "property_area": "3000 sq ft",
            "property_value": "8000000",
            "location": "Admin Test Location"
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
            
            # Step 3: Verify template was saved to sk-tindwal database
            return verify_template_location(data['data']['_id'], token, base_url)
            
        else:
            print(f"❌ Template creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Template creation error: {e}")
        return False

def verify_template_location(template_id, token, base_url):
    """Verify the template was saved to the correct organization database"""
    
    print(f"\n🔍 Verifying Template Location")
    print("=" * 30)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Get the template back
        response = requests.get(
            f"{base_url}/api/custom-templates/{template_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            template_data = response.json()['data']
            org_id = template_data.get('organizationId')
            
            print(f"✅ Template retrieved successfully")
            print(f"   Template ID: {template_id}")
            print(f"   Organization ID: {org_id}")
            
            # Check if organizationId is sk-tindwal (correct) or system-administration (incorrect)
            if org_id == "sk-tindwal":
                print(f"🎉 SUCCESS: Template saved to correct organization (sk-tindwal)")
                return True
            elif org_id == "system-administration":
                print(f"❌ FAILURE: Template saved to wrong organization (system-administration)")
                print(f"   This means the fix didn't work - admin templates are still going to admin org")
                return False
            else:
                print(f"⚠️ UNEXPECTED: Template saved to unknown organization ({org_id})")
                return False
        else:
            print(f"❌ Failed to retrieve template: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

if __name__ == "__main__":
    success = test_admin_template_creation()
    
    if success:
        print(f"\n🎉 TEST PASSED: Admin templates are now saved to the correct organization!")
    else:
        print(f"\n❌ TEST FAILED: Issue still exists - admin templates going to wrong org")