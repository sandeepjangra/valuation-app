#!/usr/bin/env python3
"""
Debug script to check what user context is available
"""

import requests
import json

def debug_user_context():
    """Debug user context for navigation"""
    
    base_url = "http://localhost:8000"
    
    print("🔍 Debugging User Context for Navigation")
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
        user_info = login_data['data']['user']
        
        print(f"✅ User Object Structure:")
        print(json.dumps(user_info, indent=2))
        
        print(f"\n🔍 Key Properties for Navigation:")
        print(f"   organization_id: {user_info.get('organization_id')}")
        print(f"   org_short_name: {user_info.get('org_short_name')}")
        print(f"   role: {user_info.get('role')}")
        
        # Check which property should be used for navigation
        org_short_name = user_info.get('org_short_name')
        organization_id = user_info.get('organization_id')
        
        print(f"\n🎯 Navigation URL should be:")
        if org_short_name:
            print(f"   /org/{org_short_name}/custom-templates")
        elif organization_id:
            print(f"   /org/{organization_id}/custom-templates")
        else:
            print(f"   ❌ No organization identifier found!")
            
        return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    debug_user_context()