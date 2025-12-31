#!/usr/bin/env python3
"""
Test script to debug organization edit functionality
"""
import requests
import json

API_BASE = "http://localhost:8000/api"

# First, get the organization
print("📋 Fetching organization list...")
response = requests.get(f"{API_BASE}/admin/organizations")
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    if data.get("success") and data.get("data"):
        org = data["data"][0]  # Get first organization
        org_id = org.get("organization_id")
        
        print(f"\n🏢 Testing with organization: {org.get('name')}")
        print(f"   ID: {org_id}")
        print(f"   Short Name: {org.get('org_short_name')}")
        
        # Get full organization details
        print(f"\n📋 Fetching full organization details...")
        response = requests.get(f"{API_BASE}/admin/organizations/{org_id}")
        
        if response.status_code == 200:
            org_details = response.json().get("data", {})
            print(f"\n✅ Current organization data:")
            print(f"   Name: {org_details.get('name')}")
            print(f"   Contact Email: {org_details.get('contact_info', {}).get('email')}")
            print(f"   Contact Phone: {org_details.get('contact_info', {}).get('phone')}")
            
            # Now try to update
            print(f"\n🔄 Testing update with changed name and email...")
            
            update_payload = {
                "org_name": "UPDATED - " + org_details.get('name', 'Test'),
                "contact_info": {
                    "email": "updated_email@example.com",
                    "phone": org_details.get('contact_info', {}).get('phone', ''),
                    "address": org_details.get('contact_info', {}).get('address', '')
                },
                "settings": org_details.get('settings', {})
            }
            
            print(f"\n📤 Sending update payload:")
            print(json.dumps(update_payload, indent=2))
            
            response = requests.patch(
                f"{API_BASE}/admin/organizations/{org_id}",
                json=update_payload
            )
            
            print(f"\n📥 Response Status: {response.status_code}")
            print(f"📥 Response Body:")
            print(json.dumps(response.json(), indent=2))
            
            if response.status_code == 200:
                result = response.json()
                changes_count = len(result.get('changes_applied', []))
                print(f"\n✅ Update completed!")
                print(f"   Changes detected: {changes_count}")
                if changes_count > 0:
                    print(f"   Changes:")
                    for change in result.get('changes_applied', []):
                        print(f"      - {change['field']}: {change['old_value']} → {change['new_value']}")
                else:
                    print(f"   ⚠️  WARNING: No changes detected!")
        else:
            print(f"❌ Failed to get organization details: {response.status_code}")
            print(response.text)
else:
    print(f"❌ Failed to get organizations: {response.status_code}")
    print(response.text)
