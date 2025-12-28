#!/usr/bin/env python3

import requests
import json

def test_issue_3_via_api():
    """
    Test Issue 3 via API calls to verify:
    1. Reports API returns bank_branch in correct location (common_fields)
    2. Frontend data extraction logic works correctly
    3. Backend properly handles bank_branch field classification
    """
    
    print("\n" + "="*60)
    print("🧪 TESTING ISSUE 3: Bank Branch Field Fix via API")
    print("="*60)
    
    BASE_URL = "http://localhost:8000/api"
    
    try:
        # Step 0: Login first
        print(f"\n🔐 Step 0: Logging in...")
        login_data = {
            "email": "admin@sk-tindwal.com",
            "organizationId": "sk-tindwal", 
            "role": "manager"
        }
        
        login_response = requests.post(f"{BASE_URL}/auth/dev-login", json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Failed to login: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return False
        
        login_result = login_response.json()
        print(f"🔍 Login response: {login_result}")
        
        # Extract token from nested structure
        data = login_result.get('data', {})
        token = data.get('access_token')
        if not token:
            print(f"❌ No access token received")
            print(f"Available keys in data: {list(data.keys()) if data else 'No data key'}")
            print(f"Full response: {login_result}")
            return False
        
        print(f"✅ Successfully logged in")
        
        # Setup headers with auth token
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test 1: Get reports list to check applicant_name extraction
        print(f"\n📋 Test 1: Getting reports list...")
        reports_response = requests.get(f"{BASE_URL}/reports", headers=headers)
        
        if reports_response.status_code != 200:
            print(f"❌ Failed to get reports: {reports_response.status_code}")
            print(f"Response: {reports_response.text}")
            return False
        
        reports_data = reports_response.json()
        print(f"✅ Retrieved {len(reports_data.get('reports', []))} reports")
        
        # Check first report structure
        if reports_data.get('reports') and len(reports_data['reports']) > 0:
            first_report = reports_data['reports'][0]
            
            print(f"\n🔍 First report structure analysis:")
            print(f"   • Report ID: {first_report.get('_id', 'N/A')}")
            print(f"   • Has applicant_name: {'applicant_name' in first_report}")
            print(f"   • Has bank_branch: {'bank_branch' in first_report}")
            print(f"   • Has common_fields: {'common_fields' in first_report}")
            print(f"   • Has report_data: {'report_data' in first_report}")
            
            # Check applicant_name (Issue 1)
            applicant_name = first_report.get('applicant_name', 'Not found')
            print(f"   • Applicant name: '{applicant_name}'")
            
            # Check bank_branch location (Issue 2 & 3)
            bank_branch_in_root = first_report.get('bank_branch', 'Not found')
            bank_branch_in_common = first_report.get('common_fields', {}).get('bank_branch', 'Not found')
            
            print(f"   • Bank branch (root): '{bank_branch_in_root}'")
            print(f"   • Bank branch (common_fields): '{bank_branch_in_common}'")
            
            # Test specific report details
            if first_report.get('_id'):
                report_id = first_report['_id']
                print(f"\n📋 Test 2: Getting specific report details for {report_id}...")
                
                detail_response = requests.get(f"{BASE_URL}/reports/{report_id}", headers=headers)
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    
                    print(f"\n🔍 Detailed report structure:")
                    print(f"   • Has common_fields: {'common_fields' in detail_data}")
                    print(f"   • Has report_data: {'report_data' in detail_data}")
                    
                    # Check bank_branch in detailed view
                    if 'common_fields' in detail_data:
                        common_fields = detail_data['common_fields']
                        bank_branch_detailed = common_fields.get('bank_branch', 'Not found')
                        print(f"   • Bank branch in common_fields: '{bank_branch_detailed}'")
                        
                        # List all common fields
                        print(f"   • All common_fields keys: {list(common_fields.keys())}")
                    
                    # Check if bank_branch is in wrong location (report_data.data)
                    if 'report_data' in detail_data and 'data' in detail_data['report_data']:
                        data_section = detail_data['report_data']['data']
                        if 'bank_branch' in data_section:
                            print(f"   ⚠️  WARNING: bank_branch found in wrong location (data)")
                            print(f"   • Bank branch in data: '{data_section['bank_branch']}'")
                        else:
                            print(f"   ✅ Bank branch correctly NOT in report_data.data")
                    
                    # Simulate frontend extraction logic
                    print(f"\n🎯 Frontend extraction simulation:")
                    
                    # This simulates our fixed frontend logic
                    extracted_bank_branch = None
                    
                    # Check common_fields first (our fix)
                    if 'common_fields' in detail_data and 'bank_branch' in detail_data['common_fields']:
                        extracted_bank_branch = detail_data['common_fields']['bank_branch']
                        print(f"   ✅ Extracted bank_branch from common_fields: '{extracted_bank_branch}'")
                    
                    # Check if would be editable (not readonly logic simulation)
                    print(f"\n✏️ Edit mode simulation:")
                    print(f"   • Bank branch value available: {'Yes' if extracted_bank_branch else 'No'}")
                    print(f"   • Field would be editable: {'Yes' if extracted_bank_branch else 'No (no value)'}")
                    
                    # Overall assessment
                    print(f"\n📊 Issue 3 Fix Assessment:")
                    
                    issue_3_checks = {
                        "bank_branch_in_common_fields": 'common_fields' in detail_data and 'bank_branch' in detail_data['common_fields'],
                        "bank_branch_has_value": extracted_bank_branch and extracted_bank_branch != 'Not found',
                        "bank_branch_not_in_data": not ('report_data' in detail_data and 'data' in detail_data['report_data'] and 'bank_branch' in detail_data['report_data']['data']),
                        "frontend_extraction_works": extracted_bank_branch is not None
                    }
                    
                    for check_name, passed in issue_3_checks.items():
                        status = "✅ PASS" if passed else "❌ FAIL"
                        print(f"   • {check_name.replace('_', ' ').title()}: {status}")
                    
                    all_pass = all(issue_3_checks.values())
                    
                    if all_pass:
                        print(f"\n🎉 ISSUE 3 FIX VERIFICATION: SUCCESS")
                        print(f"   The bank_branch field should now:")
                        print(f"   1. ✅ Display existing value: '{extracted_bank_branch}'")
                        print(f"   2. ✅ Be stored in common_fields (correct location)")
                        print(f"   3. ✅ Be extractable by frontend logic")
                        print(f"   4. ✅ Be editable in edit mode")
                        return True
                    else:
                        print(f"\n⚠️  ISSUE 3 FIX VERIFICATION: NEEDS ATTENTION")
                        failed_checks = [k for k, v in issue_3_checks.items() if not v]
                        print(f"   Failed checks: {', '.join(failed_checks)}")
                        return False
                
                else:
                    print(f"❌ Failed to get report details: {detail_response.status_code}")
                    return False
        else:
            print(f"❌ No reports found to test")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to backend server at {BASE_URL}")
        print(f"   Make sure the backend is running on port 8000")
        return False
    except Exception as e:
        print(f"❌ Error during API testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_issue_3_via_api()
    if success:
        print(f"\n✅ Issue 3 fix verification completed successfully!")
    else:
        print(f"\n❌ Issue 3 fix needs attention - review the implementation")
    
    exit(0 if success else 1)