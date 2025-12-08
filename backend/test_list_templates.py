#!/usr/bin/env python3
"""
Test the list templates endpoint to see which database it's querying
"""

import requests
import json

def test_list_templates():
    """Test listing templates as admin in sk-tindwal"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing List Templates Endpoint")
    print("=" * 40)
    
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
        
        print(f"\n📋 List Templates Response: {response.status_code}")
        
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
            
            # Check if we see templates from both databases
            org_ids = set(t.get('organizationId') for t in templates)
            print(f"📊 Organization IDs found: {org_ids}")
            
            if 'sk-tindwal' in org_ids and 'system-administration' in org_ids:
                print(f"⚠️ ISSUE: Templates from multiple organizations are being returned!")
                print(f"   This suggests the backend is not filtering by organization correctly.")
            elif 'sk-tindwal' in org_ids:
                print(f"✅ GOOD: Only sk-tindwal templates returned")
            elif 'system-administration' in org_ids:
                print(f"❌ ISSUE: Only system-administration templates returned")
                print(f"   Backend is using wrong organization database")
            else:
                print(f"❓ UNKNOWN: Unexpected organization IDs: {org_ids}")
            
            return True
            
        else:
            print(f"❌ List templates failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ List templates error: {e}")
        return False

if __name__ == "__main__":
    test_list_templates()