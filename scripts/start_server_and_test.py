#!/usr/bin/env python3
"""
Start server and test endpoints
"""
import asyncio
import subprocess
import time
import aiohttp
import os
import signal
import sys

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
            print("❌ Could not connect to server")
            return False
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
    
    return True

def start_server():
    """Start the FastAPI server"""
    os.chdir("/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend")
    env = os.environ.copy()
    env['MONGODB_URI'] = "mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster"
    
    process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "main:app", 
        "--host", "0.0.0.0", "--port", "8000"
    ], env=env)
    
    return process

async def main():
    """Main function"""
    print("🚀 Starting FastAPI server...")
    server_process = start_server()
    
    try:
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        await asyncio.sleep(5)
        
        # Test endpoints
        success = await test_endpoints()
        
        if success:
            print("\n✅ All tests passed! Backend is working correctly with new MongoDB structure.")
        else:
            print("\n❌ Some tests failed.")
            
    finally:
        # Clean up
        print("\n🛑 Stopping server...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    asyncio.run(main())