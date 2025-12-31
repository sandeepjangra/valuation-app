#!/usr/bin/env python3

import requests
import json
from datetime import datetime

def test_sbi_land_template_placeholders():
    """Test if SBI land template has placeholder data accessible"""
    
    print("🔍 TESTING SBI LAND TEMPLATE PLACEHOLDERS")
    print("=" * 50)
    
    # Test template endpoints
    base_url = "http://localhost:8000"
    
    endpoints_to_test = [
        f"{base_url}/api/templates/sbi/land",
        f"{base_url}/api/templates/SBI/land",
        f"{base_url}/api/templates/SBI/Land",
        f"{base_url}/api/template-versions/SBI/land",
        f"{base_url}/api/template-versions/active/SBI/land",
        f"{base_url}/api/reports/template/sbi/land",
        f"{base_url}/api/reports/template/SBI/land"
    ]
    
    print("🌐 Testing template endpoints...")
    
    for endpoint in endpoints_to_test:
        try:
            print(f"\n📡 Testing: {endpoint}")
            response = requests.get(endpoint, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS! Status: {response.status_code}")
                
                # Check if this contains template sections and fields
                if isinstance(data, dict):
                    if 'template' in data and 'sections' in data['template']:
                        template = data['template']
                        print(f"📋 Template Name: {template.get('templateName', 'Unknown')}")
                        print(f"📊 Sections: {len(template.get('sections', []))}")
                        
                        # Check for fields with placeholders
                        placeholder_fields = []
                        for section in template.get('sections', []):
                            for field in section.get('fields', []):
                                if field.get('placeholder') or field.get('helpText'):
                                    placeholder_fields.append({
                                        'fieldId': field.get('fieldId'),
                                        'uiDisplayName': field.get('uiDisplayName'),
                                        'placeholder': field.get('placeholder'),
                                        'helpText': field.get('helpText'),
                                        'section': section.get('sectionName')
                                    })
                        
                        print(f"💡 Fields with placeholders: {len(placeholder_fields)}")
                        
                        if placeholder_fields:
                            print("\n📝 PLACEHOLDER FIELDS FOUND:")
                            for field in placeholder_fields[:5]:  # Show first 5
                                print(f"   • {field['uiDisplayName']}")
                                if field['placeholder']:
                                    print(f"     Placeholder: {field['placeholder'][:50]}...")
                                if field['helpText']:
                                    print(f"     Help: {field['helpText'][:50]}...")
                                print(f"     Section: {field['section']}")
                                print()
                            
                            if len(placeholder_fields) > 5:
                                print(f"   ... and {len(placeholder_fields) - 5} more fields")
                        
                        return True, endpoint, data
                    
                    elif 'sections' in data:
                        sections = data['sections']
                        print(f"📊 Direct sections found: {len(sections)}")
                        
                    elif isinstance(data, list):
                        print(f"📊 List response with {len(data)} items")
                        if data:
                            first_item = data[0]
                            if 'templateName' in first_item:
                                print(f"📋 First template: {first_item.get('templateName')}")
                
                print(f"📄 Response keys: {list(data.keys()) if isinstance(data, dict) else 'List response'}")
                
            else:
                print(f"❌ Failed: {response.status_code} - {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print(f"\n🔍 All endpoints tested. No valid template found with placeholder data.")
    return False, None, None

def test_frontend_template_data():
    """Test frontend template data access"""
    
    print(f"\n🎯 TESTING FRONTEND TEMPLATE ACCESS")
    print("=" * 50)
    
    try:
        # Test if we can access the Angular app
        response = requests.get("http://localhost:4200", timeout=5)
        if response.status_code == 200:
            print("✅ Angular frontend is running")
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Frontend error: {str(e)}")
    
    # Test API endpoints that Angular might use
    api_endpoints = [
        "http://localhost:8000/api/health",
        "http://localhost:8000/api/banks",
        "http://localhost:8000/api/templates",
    ]
    
    for endpoint in api_endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            print(f"📡 {endpoint}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    print(f"   Keys: {list(data.keys())}")
                elif isinstance(data, list):
                    print(f"   Items: {len(data)}")
        except Exception as e:
            print(f"   Error: {str(e)}")

if __name__ == "__main__":
    # Test template data access
    success, endpoint, data = test_sbi_land_template_placeholders()
    
    if success:
        print(f"\n🎉 SUCCESS! Template with placeholders found at: {endpoint}")
        print("\n💡 This means the information icons SHOULD be working!")
        print("📋 Check your Angular application at: http://localhost:4200")
        print("🔍 Navigate to: Create New Report → SBI → Land Property")
        print("👀 Look for ℹ️ icons next to field labels")
    else:
        print(f"\n❌ No template with placeholder data found")
        print("🔧 This explains why information icons are not showing")
        print("📝 The template needs placeholder/helpText fields to show icons")
    
    # Test frontend accessibility
    test_frontend_template_data()
    
    print(f"\n" + "=" * 50)
    print(f"🕐 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")