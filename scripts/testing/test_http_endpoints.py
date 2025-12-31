#!/usr/bin/env python3
"""
Test HTTP endpoints for custom templates
"""
import asyncio
import aiohttp
import json

async def test_endpoints():
    """Test the custom template HTTP endpoints"""
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        try:
            # Test 1: Banks endpoint
            print("🔍 Testing /api/custom-templates/banks endpoint...")
            async with session.get(f"{base_url}/api/custom-templates/banks") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Banks endpoint returned {len(data.get('data', []))} banks")
                    for bank in data.get('data', []):
                        print(f"  {bank.get('bankCode')}: {bank.get('propertyTypes')}")
                else:
                    print(f"❌ Banks endpoint failed with status {response.status}")
                    text = await response.text()
                    print(f"Error: {text}")
            
            # Test 2: Fields endpoint for SBI/land
            print("\n🔍 Testing /api/custom-templates/fields endpoint...")
            params = {"bank_code": "SBI", "property_type": "land"}
            async with session.get(f"{base_url}/api/custom-templates/fields", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    bank_tabs = data.get('bankSpecificTabs', [])
                    if bank_tabs:
                        fields = bank_tabs[0].get('fields', [])
                        print(f"✅ Fields endpoint returned {len(fields)} fields for SBI/land")
                        for field in fields[:3]:  # Show first 3
                            print(f"  {field.get('fieldId')}: {field.get('uiDisplayName')}")
                    else:
                        print("❌ No bank-specific tabs found")
                else:
                    print(f"❌ Fields endpoint failed with status {response.status}")
                    text = await response.text()
                    print(f"Error: {text}")
                    
        except aiohttp.ClientConnectorError:
            print("❌ Could not connect to server. Make sure the backend is running on port 8000")
        except Exception as e:
            print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_endpoints())