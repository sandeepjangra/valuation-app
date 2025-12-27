#!/usr/bin/env python3
"""
Debug what the SBI template API actually returns
"""

import asyncio
import aiohttp
import json

async def debug_sbi_template():
    """Check the actual structure returned by the SBI template API"""
    
    base_url = "http://localhost:8000"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Login
            async with session.post(f'{base_url}/api/auth/login', 
                                  json={'email': 'sk.tindwal@gmail.com', 'password': 'admin123'}) as resp:
                data = await resp.json()
                token = data['data']['access_token']
                print("✅ Logged in successfully")
            
            # Get template
            headers = {'Authorization': f'Bearer {token}'}
            async with session.get(f'{base_url}/api/templates/SBI/land-property/aggregated-fields', 
                                 headers=headers) as resp:
                template_data = await resp.json()
                
                print("🔍 RAW TEMPLATE DATA STRUCTURE:")
                print("=" * 60)
                
                # Print the full structure in a readable way
                print("Top-level keys:", list(template_data.keys()))
                
                for key, value in template_data.items():
                    if key == 'templateMetadata':
                        print(f"\n📋 {key}:")
                        if isinstance(value, dict):
                            print(f"   Keys: {list(value.keys())}")
                            
                            # Check tabs specifically
                            tabs = value.get('tabs', [])
                            print(f"   📂 tabs: {type(tabs)} with length {len(tabs)}")
                            
                            if tabs:
                                print(f"   📂 First tab structure:")
                                print(json.dumps(tabs[0], indent=4)[:500] + "...")
                            else:
                                print(f"   ⚠️ No tabs found in templateMetadata")
                        else:
                            print(f"   Value type: {type(value)}")
                    
                    elif key == 'data':
                        print(f"\n📋 {key}:")
                        if isinstance(value, dict):
                            print(f"   Keys: {list(value.keys())}")
                        elif isinstance(value, list):
                            print(f"   List length: {len(value)}")
                            if value:
                                print(f"   First item keys: {list(value[0].keys()) if isinstance(value[0], dict) else type(value[0])}")
                        else:
                            print(f"   Value type: {type(value)}")
                    
                    else:
                        if isinstance(value, (dict, list)):
                            print(f"\n📋 {key}: {type(value)} with {len(value)} items")
                        else:
                            print(f"\n📋 {key}: {type(value)} = {str(value)[:100]}...")
                
                # Save full data to file for inspection
                with open('sbi_template_debug.json', 'w') as f:
                    json.dump(template_data, f, indent=2, default=str)
                print(f"\n💾 Full template data saved to 'sbi_template_debug.json'")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 DEBUGGING SBI TEMPLATE API RESPONSE")
    print("-" * 50)
    asyncio.run(debug_sbi_template())