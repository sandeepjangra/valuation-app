#!/usr/bin/env python3
"""
Debug script to test the aggregated-fields API response
to see if the calculated fields are properly included
"""
import requests
import json

def test_aggregated_fields_api():
    """Test the aggregated fields API for SBI land template"""
    
    # API endpoint - using a valid template ID from the database
    url = "http://localhost:8000/api/templates/SBI/69370b2cc8a7f05dc81aef0d/aggregated-fields"
    
    try:
        print(f"🌐 Testing API: {url}")
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ API Response received")
        print(f"📊 Status: {response.status_code}")
        
        # Check structure
        print(f"\n📋 Response Structure:")
        print(f"  - templateInfo: {data.get('templateInfo', {}).get('templateCode', 'N/A')}")
        print(f"  - commonFields: {len(data.get('commonFields', []))}")
        print(f"  - bankSpecificTabs: {len(data.get('bankSpecificTabs', []))}")
        
        # Look for calculated fields
        all_fields = []
        
        # Check common fields
        for field in data.get('commonFields', []):
            all_fields.append(field)
            
        # Check bank-specific fields
        for tab in data.get('bankSpecificTabs', []):
            for field in tab.get('fields', []):
                all_fields.append(field)
                
            for section in tab.get('sections', []):
                for field in section.get('fields', []):
                    all_fields.append(field)
        
        print(f"\n🔍 Total fields found: {len(all_fields)}")
        
        # Look for calculated fields
        calculated_fields = []
        for field in all_fields:
            # Check various possible calculation indicators
            if (field.get('calculationMetadata', {}).get('isCalculatedField') or 
                field.get('calculatedField') or 
                field.get('formula')):
                calculated_fields.append(field)
        
        print(f"\n🧮 Calculated fields found: {len(calculated_fields)}")
        for field in calculated_fields:
            print(f"  - {field.get('fieldId')}: {field.get('label', 'No Label')}")
            if field.get('calculationMetadata'):
                print(f"    Formula: {field['calculationMetadata'].get('formula', 'N/A')}")
                print(f"    Dependencies: {field['calculationMetadata'].get('dependencies', [])}")
        
        # Look specifically for estimated_land_value
        estimated_field = None
        for field in all_fields:
            if field.get('fieldId') == 'estimated_land_value':
                estimated_field = field
                break
        
        if estimated_field:
            print(f"\n🎯 Found estimated_land_value field:")
            print(json.dumps(estimated_field, indent=2))
        else:
            print(f"\n❌ estimated_land_value field not found in API response")
            
        # Save full response for inspection
        with open('/Users/sandeepjangra/Downloads/development/ValuationAppV1/api_response_debug.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n💾 Full response saved to api_response_debug.json")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is the backend running?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_aggregated_fields_api()