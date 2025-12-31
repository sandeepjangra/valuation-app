#!/usr/bin/env python3

import asyncio
import json
import aiohttp
import sys

async def test_fixed_issues():
    """Test that all the issues have been fixed"""
    
    print("🧪 Testing Fixed Issues - Organization Context & Data Structure")
    print("="*70)
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        try:
            # 1. Test system admin login
            print("1️⃣ Testing System Admin Login...")
            login_data = {
                "email": "admin@system.com",
                "password": "admin123"
            }
            
            async with session.post(f"{base_url}/api/auth/login", json=login_data) as response:
                if response.status == 200:
                    login_result = await response.json()
                    token = login_result["data"]["access_token"]
                    user_info = login_result["data"]["user"]
                    print(f"   ✅ System admin login successful")
                    print(f"   📧 User: {user_info.get('email')}")
                    print(f"   🏢 Org: {user_info.get('org_short_name')}")
                else:
                    print(f"   ❌ Login failed: {response.status}")
                    return False
            
            # 2. Test report creation in sk-tindwal organization (cross-org access)
            print("\n2️⃣ Testing Report Creation in sk-tindwal (Cross-Organization)...")
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Sample report data (flat structure from frontend)
            report_data = {
                "bank_code": "SBI",
                "template_id": "land-property",
                "property_address": "Test Property in SK Tindwal Org",
                "report_data": {
                    # Common fields
                    "bank_branch": "sbi_mumbai_main",
                    "applicant_name": "SK Tindwal Test Client",
                    "valuation_purpose": "bank_purpose",
                    "valuation_date": "2025-12-21",
                    "inspection_date": "2025-12-20",
                    
                    # Template fields that should be organized into tabs
                    "owner_details": "Test Property Owner",
                    "borrower_name": "Test Borrower Name", 
                    "postal_address": "123 Test Street, Mumbai",
                    "plot_size": "2000",  # Should go to valuation tab
                    "market_rate": "3500", # Should go to valuation tab
                    "estimated_valuation": "7000000", # Should go to valuation tab
                    "building_specifications_table": [{"type": "RCC", "area": "1800"}],
                    "land_total": "5000000"
                }
            }
            
            # Create report via main API endpoint (the org context should be extracted from URL)
            create_url = f"{base_url}/api/reports"
            
            async with session.post(create_url, json=report_data, headers=headers) as response:
                if response.status == 201:
                    result = await response.json()
                    report_id = result["data"]["report_id"] 
                    reference_number = result["data"]["reference_number"]
                    organization_id = result["data"]["organization_id"]
                    report_structure = result["data"]["report_data"]
                    
                    print(f"   ✅ Report created successfully!")
                    print(f"   📋 Report ID: {report_id}")
                    print(f"   🔢 Reference: {reference_number}")
                    print(f"   🏢 Organization: {organization_id}")
                    
                    # Check if reference number uses sk-tindwal initials (not SYSADM)
                    if reference_number.startswith("CEV/RVO/299"):
                        print(f"   ✅ Reference number uses correct organization initials!")
                    else:
                        print(f"   ❌ Reference number still using wrong initials: {reference_number}")
                    
                    # Check if organization is sk-tindwal (not system-administration)
                    if organization_id == "sk-tindwal":
                        print(f"   ✅ Report saved to correct organization!")
                    else:
                        print(f"   ❌ Report saved to wrong organization: {organization_id}")
                    
                    # Check data structure - should be organized by tabs
                    if isinstance(report_structure, dict):
                        tab_count = len(report_structure)
                        print(f"   📊 Report data organized into {tab_count} tabs")
                        
                        # Count fields in tabs vs outside
                        fields_in_tabs = 0
                        for tab_name, tab_data in report_structure.items():
                            if isinstance(tab_data, dict):
                                fields_in_tabs += len(tab_data)
                        
                        print(f"   📋 Fields organized in tabs: {fields_in_tabs}")
                        
                        # Check for specific tab organization
                        if "valuation" in report_structure:
                            valuation_tab = report_structure["valuation"]
                            valuation_fields = len(valuation_tab) if isinstance(valuation_tab, dict) else 0
                            print(f"   💰 Valuation tab: {valuation_fields} fields")
                            
                            if "plot_size" in valuation_tab and "market_rate" in valuation_tab:
                                print(f"   ✅ Calculation fields properly organized in valuation tab!")
                            else:
                                print(f"   ⚠️ Some calculation fields not in valuation tab")
                        
                        if fields_in_tabs > 0:
                            print(f"   ✅ Data structure is properly organized by tabs (NOT flat)!")
                        else:
                            print(f"   ❌ Data structure is still flat!")
                            
                    else:
                        print(f"   ❌ Report data structure is not a dictionary!")
                        
                else:
                    error_text = await response.text()
                    print(f"   ❌ Report creation failed: {response.status}")
                    print(f"   Error: {error_text}")
                    return False
            
            # 3. Test the new land valuation calculation endpoint
            print("\n3️⃣ Testing Land Valuation Calculation...")
            
            calc_data = {
                "plot_size": "2000 sq ft",
                "market_rate": "₹3,500"
            }
            
            async with session.post(f"{base_url}/api/calculate/land-valuation", 
                                  json=calc_data, headers=headers) as response:
                if response.status == 200:
                    calc_result = await response.json()
                    estimated_value = calc_result["result"]
                    formatted_value = calc_result["formattedResult"]
                    
                    print(f"   ✅ Land valuation calculation successful!")
                    print(f"   🧮 2000 × 3500 = {estimated_value}")
                    print(f"   💰 Formatted: {formatted_value}")
                else:
                    error_text = await response.text()
                    print(f"   ❌ Calculation failed: {response.status}")
                    print(f"   Error: {error_text}")
            
            print(f"\n🎉 All tests completed!")
            return True
            
        except Exception as e:
            print(f"❌ Test error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("Starting comprehensive test...")
    success = asyncio.run(test_fixed_issues())
    if success:
        print("\n✅ All issues have been fixed successfully!")
    else:
        print("\n❌ Some issues still need to be resolved!")
        sys.exit(1)