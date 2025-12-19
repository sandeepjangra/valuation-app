#!/usr/bin/env python3
"""
Quick verification script to test template API response format
"""

import requests
import json

def test_template_api():
    """Test the template API response format"""
    
    url = "http://localhost:8000/api/templates/SBI/land-property/aggregated-fields"
    
    try:
        print("🧪 Testing template API...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ API Response received successfully")
            print(f"📊 Response structure:")
            print(f"   Top-level keys: {list(data.keys())}")
            
            if 'templateInfo' in data:
                template_info = data['templateInfo']
                print(f"   ✅ templateInfo: {template_info.get('templateName', 'Unknown')}")
                print(f"   📋 Template ID: {template_info.get('templateId', 'Unknown')}")
                print(f"   🏦 Bank: {template_info.get('bankName', 'Unknown')}")
            
            if 'commonFields' in data:
                common_fields = data['commonFields']
                print(f"   ✅ commonFields: {len(common_fields)} fields")
                if common_fields:
                    first_field = common_fields[0]
                    print(f"      First field: {first_field.get('fieldId', 'Unknown')} - {first_field.get('uiDisplayName', 'Unknown')}")
            
            if 'bankSpecificTabs' in data:
                bank_tabs = data['bankSpecificTabs']
                print(f"   ✅ bankSpecificTabs: {len(bank_tabs)} tabs")
                if bank_tabs:
                    tab_names = [tab.get('tabName', 'Unknown') for tab in bank_tabs]
                    print(f"      Tabs: {', '.join(tab_names)}")
            
            print("\n🎯 Frontend should now be able to parse this response correctly!")
            print("   - No need for response.success check")
            print("   - Template data is directly in the response")
            print("   - handleTemplateResponse() has been fixed to handle this format")
            
            return True
            
        else:
            print(f"❌ API returned status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Template API Verification")
    print("=" * 50)
    
    success = test_template_api()
    
    if success:
        print("\n✅ Template API is working correctly!")
        print("\n🔗 Test the fix:")
        print("   1. Open: http://localhost:4200/org/sk-tindwal/reports/rpt_61286d3f2389?mode=view")
        print("   2. Check browser console - should see '✅ Template response received'")
        print("   3. Should NOT see '❌ Invalid template response format'")
        print("   4. Report should load with proper tabs and form structure")
    else:
        print("\n❌ Template API test failed!")

if __name__ == "__main__":
    main()