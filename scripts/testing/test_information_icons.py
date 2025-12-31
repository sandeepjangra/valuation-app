#!/usr/bin/env python3

import requests
import json

def test_placeholder_information_icons():
    """
    Test that placeholder information icons are working:
    1. Verify template has placeholder fields
    2. Check specific fields with placeholders
    """
    
    print("🔍 TESTING PLACEHOLDER INFORMATION ICONS")
    print("=" * 50)
    
    BASE_URL = "http://localhost:8000/api"
    
    try:
        # Login
        print("🔐 Logging in...")
        login_data = {
            "email": "admin@sk-tindwal.com",
            "organizationId": "sk-tindwal", 
            "role": "manager"
        }
        
        login_response = requests.post(f"{BASE_URL}/auth/dev-login", json=login_data, timeout=10)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
        
        auth_data = login_response.json()
        token = auth_data['data']['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful")
        
        # Get SBI land property template to check placeholders
        print(f"\n📋 Getting SBI Land Property template...")
        
        template_response = requests.get(f"{BASE_URL}/templates/sbi-land-property", headers=headers, timeout=10)
        
        if template_response.status_code != 200:
            print(f"❌ Failed to get template: {template_response.status_code}")
            return False
        
        template_data = template_response.json()
        print(f"✅ Retrieved template")
        
        # Analyze placeholder fields in template
        placeholder_fields = []
        
        def find_placeholders_recursive(obj, path=""):
            if isinstance(obj, dict):
                # Check if this is a field with placeholder
                if 'fieldId' in obj and 'placeholder' in obj and obj.get('placeholder'):
                    placeholder_fields.append({
                        'fieldId': obj['fieldId'],
                        'fieldType': obj.get('fieldType', 'unknown'),
                        'uiDisplayName': obj.get('uiDisplayName', ''),
                        'placeholder': obj['placeholder'],
                        'path': path
                    })
                
                # Recursively check all dictionary values
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    find_placeholders_recursive(value, new_path)
                    
            elif isinstance(obj, list):
                # Recursively check all list items
                for i, item in enumerate(obj):
                    new_path = f"{path}[{i}]"
                    find_placeholders_recursive(item, new_path)
        
        find_placeholders_recursive(template_data)
        
        print(f"\n📊 PLACEHOLDER ANALYSIS:")
        print(f"   Total fields with placeholders: {len(placeholder_fields)}")
        
        if len(placeholder_fields) > 0:
            print(f"\n🎯 Fields with Information Icons:")
            for i, field in enumerate(placeholder_fields[:10]):  # Show first 10
                print(f"   {i+1}. {field['uiDisplayName']} ({field['fieldId']})")
                print(f"      Type: {field['fieldType']}")
                print(f"      Placeholder: \"{field['placeholder'][:80]}{'...' if len(field['placeholder']) > 80 else ''}\"")
                print()
            
            if len(placeholder_fields) > 10:
                print(f"   ... and {len(placeholder_fields) - 10} more fields with placeholders")
        
        # Check specific important fields that should have info icons
        important_fields = [
            'owner_details',
            'borrower_name', 
            'postal_address',
            'property_description',
            'coordinates',
            'longitude',
            'latitude',
            'site_area',
            'valuation_area'
        ]
        
        found_important = []
        for field in placeholder_fields:
            if field['fieldId'] in important_fields:
                found_important.append(field)
        
        print(f"\n🎯 IMPORTANT FIELDS WITH INFO ICONS:")
        for field in found_important:
            print(f"   ✅ {field['uiDisplayName']}: \"{field['placeholder'][:60]}{'...' if len(field['placeholder']) > 60 else ''}\"")
        
        missing_important = [fid for fid in important_fields if not any(f['fieldId'] == fid for f in found_important)]
        if missing_important:
            print(f"\n⚠️ Important fields WITHOUT placeholders:")
            for fid in missing_important:
                print(f"   • {fid}")
        
        # Group by field type
        by_type = {}
        for field in placeholder_fields:
            field_type = field['fieldType']
            if field_type not in by_type:
                by_type[field_type] = []
            by_type[field_type].append(field)
        
        print(f"\n📊 PLACEHOLDERS BY FIELD TYPE:")
        for field_type, fields in by_type.items():
            print(f"   • {field_type}: {len(fields)} fields")
        
        print(f"\n🎨 UI TESTING INSTRUCTIONS:")
        print(f"1. 🌐 Open: http://localhost:4200")
        print(f"2. 🔐 Login to the application")
        print(f"3. ➕ Create New Report → SBI → Land Property")
        print(f"4. 🔍 Look for information icons (ℹ️) next to field labels")
        print(f"5. 🖱️  Hover over icons to see placeholder tooltips")
        
        print(f"\n✅ Key fields to test:")
        test_fields = found_important[:5] if found_important else placeholder_fields[:5]
        for field in test_fields:
            print(f"   • {field['uiDisplayName']}: Should show icon with tooltip")
        
        if len(placeholder_fields) > 0:
            print(f"\n🎉 SUCCESS: Template has {len(placeholder_fields)} fields with placeholders")
            print(f"   Information icons should appear next to these fields in the UI!")
            return True
        else:
            print(f"\n❌ WARNING: No placeholder fields found in template")
            print(f"   Check template structure or placeholder definitions")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    success = test_placeholder_information_icons()
    
    if success:
        print(f"\n🎯 Information icons implementation ready for testing!")
        print(f"Check the Angular UI for ℹ️ icons next to fields with placeholders")
    else:
        print(f"\n❌ Issue with placeholder detection - check template structure")
    
    exit(0 if success else 1)