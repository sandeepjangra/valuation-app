#!/usr/bin/env python3
"""
Test the frontend integration by simulating the API calls
and verifying the data structure matches frontend expectations
"""

import httpx
import json
from typing import Dict, Any

def test_aggregation_endpoint():
    """Test the aggregation endpoint that frontend will use"""
    
    print("🔄 Testing Frontend Integration - API Data Flow")
    print("=" * 60)
    
    # Test different bank/template combinations
    test_cases = [
        {"bank": "SBI", "template": "land", "description": "SBI Land Property"},
        {"bank": "SBI", "template": "apartment", "description": "SBI Apartment Property"},
        {"bank": "PNB", "template": "all", "description": "PNB All Property Types"},
        {"bank": "HDFC", "template": "all", "description": "HDFC All Property Types"},
    ]
    
    for test_case in test_cases:
        print(f"\n📋 Testing: {test_case['description']}")
        print("-" * 40)
        
        try:
            # Make API call
            url = f"http://localhost:8000/api/templates/{test_case['bank']}/{test_case['template']}/aggregated-fields"
            response = httpx.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Analyze the structure for frontend compatibility
                template_info = data.get('templateInfo', {})
                common_fields = data.get('commonFields', [])
                bank_specific_fields = data.get('bankSpecificFields', [])
                
                print(f"✅ Status: {response.status_code}")
                print(f"📊 Template: {template_info.get('templateName', 'Unknown')}")
                print(f"🏛️ Bank: {template_info.get('bankName', 'Unknown')}")
                print(f"🏠 Property Type: {template_info.get('propertyType', 'Unknown')}")
                print(f"📝 Common Fields: {len(common_fields)}")
                print(f"🔧 Bank-Specific Fields: {len(bank_specific_fields)}")
                print(f"📊 Total Fields: {len(common_fields) + len(bank_specific_fields)}")
                
                # Check field structure compatibility with frontend
                print(f"📋 Field Structure Analysis:")
                if common_fields:
                    sample_field = common_fields[0]
                    required_keys = ['fieldId', 'uiDisplayName', 'fieldType', 'isRequired', 'gridSize', 'sortOrder']
                    missing_keys = [key for key in required_keys if key not in sample_field]
                    if missing_keys:
                        print(f"⚠️  Missing required keys in common fields: {missing_keys}")
                    else:
                        print(f"✅ Common fields structure is compatible")
                        
                    # Check field types
                    field_types = set(field.get('fieldType', 'unknown') for field in common_fields)
                    print(f"📝 Common field types: {', '.join(field_types)}")
                
                if bank_specific_fields:
                    # Analyze bank-specific field structure (might be different)
                    sample_bank_field = bank_specific_fields[0]
                    bank_field_keys = list(sample_bank_field.keys())
                    print(f"🔧 Bank-specific field keys: {bank_field_keys[:5]}{'...' if len(bank_field_keys) > 5 else ''}")
                    
                    # Check for field groups
                    field_groups = set()
                    for field in bank_specific_fields:
                        if 'fieldGroup' in field:
                            field_groups.add(field['fieldGroup'])
                    
                    if field_groups:
                        print(f"📂 Field groups found: {', '.join(field_groups)}")
                    else:
                        print(f"📂 No field groups (will use default grouping)")
                
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Connection Error: {e}")
    
    print(f"\n🎯 Frontend Integration Test Summary:")
    print("=" * 60)
    print("✅ All working endpoints should show:")
    print("   - Common fields: 7 fields (basic valuation info)")
    print("   - Bank-specific fields: 15-52 fields (depending on template)")
    print("   - Proper field structure with required frontend keys")
    print("   - Field types compatible with Angular form controls")
    print("\n🔄 Next: Test the Angular frontend UI to see data rendering")

if __name__ == "__main__":
    test_aggregation_endpoint()