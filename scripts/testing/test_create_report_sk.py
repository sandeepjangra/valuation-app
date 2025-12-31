#!/usr/bin/env python3
"""
Test create report functionality for sk.tindwal user
This tests the fixed create report endpoint that was returning null response
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_create_report():
    """Test creating a new report as sk.tindwal user"""
    
    # Test configuration
    base_url = "http://localhost:8000"
    
    # Login credentials for sk.tindwal user
    login_data = {
        "email": "sk.tindwal@gmail.com",
        "password": "admin123"
    }
    
    # Sample report data matching frontend structure
    report_data = {
        "bank_code": "SBI",
        "template_id": "land-property", 
        "property_address": "Test Property for CREATE - Fixed Indentation",
        "report_data": {
            "property_type": "Land",
            "property_address": "Test Property for CREATE - Fixed Indentation",
            "valuation_purpose": "Loan Security",
            "inspection_date": "2024-12-25",
            "report_reference_number": "",  # Will be auto-generated
            # Add some sample fields
            "land_area": "1000 sq ft",
            "market_rate": "5000 per sq ft",
            "total_value": "5000000"
        }
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            # Step 1: Login to get authentication token
            print("🔐 Step 1: Logging in as sk.tindwal@gmail.com...")
            async with session.post(f"{base_url}/api/auth/login", json=login_data) as response:
                if response.status != 200:
                    response_text = await response.text()
                    print(f"❌ Login failed with status {response.status}: {response_text}")
                    return
                
                login_result = await response.json()
                if not login_result.get("success"):
                    print(f"❌ Login failed: {login_result.get('message')}")
                    return
                
                token = login_result["data"]["access_token"]
                print(f"✅ Login successful! Token obtained.")
                
            # Step 2: Create new report
            print("📝 Step 2: Creating new report...")
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            async with session.post(f"{base_url}/api/reports", json=report_data, headers=headers) as response:
                response_text = await response.text()
                print(f"🔍 Response Status: {response.status}")
                print(f"🔍 Response Headers: {dict(response.headers)}")
                print(f"🔍 Raw Response: {response_text}")
                
                # Check if response is successful
                if response.status == 201:
                    try:
                        result = await response.json()
                        print(f"\n✅ CREATE REPORT SUCCESS!")
                        print(f"📊 Response format: {type(result)}")
                        print(f"🔧 Success field: {result.get('success')}")
                        print(f"💬 Message: {result.get('message')}")
                        
                        if result.get("data"):
                            report_data = result["data"]
                            print(f"📋 Report ID: {report_data.get('report_id')}")
                            print(f"📋 Reference Number: {report_data.get('reference_number')}")
                            print(f"📋 Organization: {report_data.get('organization_id')}")
                            print(f"📋 Status: {report_data.get('status')}")
                            print(f"📋 Version: {report_data.get('version')}")
                            
                            # Test the specific field that frontend checks
                            if result.get("success") is True:
                                print(f"🎉 FRONTEND COMPATIBILITY: result.success = {result.get('success')}")
                            else:
                                print(f"⚠️ FRONTEND ISSUE: result.success = {result.get('success')}")
                        else:
                            print(f"⚠️ No report data in response")
                            
                    except json.JSONDecodeError as e:
                        print(f"❌ Failed to parse JSON response: {e}")
                        print(f"📄 Raw response: {response_text}")
                        
                else:
                    print(f"❌ CREATE REPORT FAILED!")
                    print(f"Status: {response.status}")
                    print(f"Response: {response_text}")
                    
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("🧪 Testing CREATE REPORT functionality for sk.tindwal user")
    print("🎯 This tests the fixed backend create endpoint")
    print("-" * 60)
    asyncio.run(test_create_report())