#!/usr/bin/env python3
"""
Test script for the new aggregation endpoint
"""
import asyncio
import httpx

async def test_aggregation_endpoint():
    """Test the new aggregation endpoint"""
    base_url = "http://localhost:8000"
    
    # Test cases
    test_cases = [
        {"bank_code": "SBI", "template_id": "land"},
        {"bank_code": "SBI", "template_id": "apartment"},
        {"bank_code": "UBI", "template_id": "land"},
        {"bank_code": "PNB", "template_id": "all"},
        {"bank_code": "HDFC", "template_id": "all"},
    ]
    
    async with httpx.AsyncClient() as client:
        for test in test_cases:
            bank_code = test["bank_code"]
            template_id = test["template_id"]
            
            print(f"\n{'='*60}")
            print(f"Testing: {bank_code} - {template_id}")
            print(f"{'='*60}")
            
            # Test the new aggregation endpoint
            try:
                url = f"{base_url}/api/templates/{bank_code}/{template_id}/aggregated-fields"
                print(f"URL: {url}")
                
                response = await client.get(url)
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    template_info = data.get("templateInfo", {})
                    common_fields = data.get("commonFields", [])
                    bank_specific = data.get("bankSpecificFields", [])
                    
                    print(f"Template: {template_info.get('templateName', 'Unknown')}")
                    print(f"Bank: {template_info.get('bankName', 'Unknown')}")
                    print(f"Property Type: {template_info.get('propertyType', 'Unknown')}")
                    print(f"Common Fields: {len(common_fields)}")
                    print(f"Bank Specific Fields: {len(bank_specific)}")
                    
                    if common_fields:
                        print(f"First Common Field: {common_fields[0].get('fieldName', 'Unknown')}")
                    if bank_specific:
                        print(f"First Bank Field: {bank_specific[0].get('fieldName', 'Unknown')}")
                        
                else:
                    print(f"Error: {response.text}")
                    
            except Exception as e:
                print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_aggregation_endpoint())