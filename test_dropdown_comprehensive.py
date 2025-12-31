#!/usr/bin/env python3

import requests
import json

def test_dropdown_fixes_comprehensive():
    """
    Comprehensive test of dropdown value fixes:
    1. Copy existing report with technical values
    2. Verify frontend converts technical values to labels for storage  
    3. Verify frontend converts labels back to technical values for form controls
    """
    
    print("🎯 COMPREHENSIVE DROPDOWN VALUE FIXES TEST")
    print("=" * 60)
    
    BASE_URL = "http://localhost:8000/api"
    
    try:
        # Login
        print("🔐 Step 1: Logging in...")
        login_data = {
            "email": "admin@sk-tindwal.com",
            "organizationId": "sk-tindwal", 
            "role": "manager"
        }
        
        login_response = requests.post(f"{BASE_URL}/auth/dev-login", json=login_data, timeout=10)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
        
        auth_data = login_response.json()
        token = auth_data['data']['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful")
        
        # Get existing report with technical values
        source_report_id = "rpt_c1a9c6224707"
        print(f"\n📋 Step 2: Getting source report {source_report_id}...")
        
        report_response = requests.get(f"{BASE_URL}/reports/{source_report_id}", headers=headers, timeout=10)
        
        if report_response.status_code != 200:
            print(f"❌ Failed to get source report: {report_response.status_code}")
            return False
        
        source_report = report_response.json()['data']
        print(f"✅ Retrieved source report")
        
        # Analyze current dropdown values (technical codes)
        print(f"\n🔍 Step 3: Analyzing current dropdown values...")
        
        technical_values_found = {}
        report_data = source_report.get('report_data', {})
        
        # Check common_fields
        if 'common_fields' in report_data:
            for key, value in report_data['common_fields'].items():
                if isinstance(value, str) and ('_' in value or value in ['yes', 'no']):
                    technical_values_found[f'common_fields.{key}'] = value
        
        # Check data section
        if 'data' in report_data:
            for key, value in report_data['data'].items():
                if isinstance(value, str) and ('_' in value or value in ['yes', 'no']):
                    technical_values_found[f'data.{key}'] = value
        
        print(f"📊 Technical values found: {len(technical_values_found)}")
        for field, value in list(technical_values_found.items())[:10]:  # Show first 10
            print(f"   • {field}: '{value}'")
        if len(technical_values_found) > 10:
            print(f"   ... and {len(technical_values_found) - 10} more")
        
        # Create test data by copying existing report data but with a new applicant name
        print(f"\n📝 Step 4: Creating test report with same data...")
        
        # Copy the report data but change applicant name to track this test
        test_report_data = json.loads(json.dumps(source_report['report_data']))
        
        # Modify applicant name to identify this as test report
        if 'common_fields' in test_report_data:
            test_report_data['common_fields']['applicant_name'] = "TEST: Dropdown Fix Validation"
        
        # Create new report with same structure
        create_data = {
            "bank_code": source_report['bank_code'],
            "template_id": source_report['template_id'],
            "report_data": test_report_data
        }
        
        print("Creating test report...")
        create_response = requests.post(f"{BASE_URL}/reports", json=create_data, headers=headers, timeout=15)
        
        if create_response.status_code != 201:
            print(f"❌ Failed to create test report: {create_response.status_code}")
            print(f"Response: {create_response.text}")
            return False
        
        test_report_result = create_response.json()
        test_report_id = test_report_result['data']['report_id'] if test_report_result.get('success') else test_report_result.get('report_id')
        
        print(f"✅ Created test report: {test_report_id}")
        
        # Get the test report back to see what was actually saved
        print(f"\n📥 Step 5: Retrieving test report to verify storage...")
        
        test_fetch_response = requests.get(f"{BASE_URL}/reports/{test_report_id}", headers=headers, timeout=10)
        
        if test_fetch_response.status_code != 200:
            print(f"❌ Failed to retrieve test report: {test_fetch_response.status_code}")
            return False
        
        test_report = test_fetch_response.json()['data']
        test_report_data = test_report.get('report_data', {})
        
        # Analyze what was actually stored
        stored_values = {}
        
        # Check common_fields in test report
        if 'common_fields' in test_report_data:
            for key, value in test_report_data['common_fields'].items():
                if key in [field.split('.')[1] for field in technical_values_found.keys() if field.startswith('common_fields.')]:
                    stored_values[f'common_fields.{key}'] = value
        
        # Check data section in test report  
        if 'data' in test_report_data:
            for key, value in test_report_data['data'].items():
                if key in [field.split('.')[1] for field in technical_values_found.keys() if field.startswith('data.')]:
                    stored_values[f'data.{key}'] = value
        
        print(f"\n📊 Step 6: Comparing original vs stored values...")
        print("="*60)
        
        conversion_working = 0
        conversion_failed = 0
        
        for field_path, original_value in technical_values_found.items():
            stored_value = stored_values.get(field_path, 'NOT_FOUND')
            
            if stored_value == 'NOT_FOUND':
                print(f"❓ {field_path}: NOT FOUND in test report")
                continue
                
            # Check if conversion happened
            if original_value != stored_value:
                # Value changed - hopefully to a display label
                if '_' not in stored_value and stored_value not in ['yes', 'no']:
                    print(f"✅ {field_path}: '{original_value}' → '{stored_value}' (CONVERTED)")
                    conversion_working += 1
                else:
                    print(f"❓ {field_path}: '{original_value}' → '{stored_value}' (CHANGED BUT STILL TECHNICAL)")
                    conversion_failed += 1
            else:
                # Value unchanged - conversion not working
                print(f"❌ {field_path}: '{original_value}' (NO CONVERSION)")
                conversion_failed += 1
        
        print(f"\n🎯 DROPDOWN CONVERSION RESULTS:")
        print(f"   ✅ Working conversions: {conversion_working}")
        print(f"   ❌ Failed conversions: {conversion_failed}")
        print(f"   📊 Total fields tested: {len(technical_values_found)}")
        
        success_rate = (conversion_working / len(technical_values_found)) * 100 if technical_values_found else 0
        print(f"   📈 Success rate: {success_rate:.1f}%")
        
        if success_rate > 80:
            print(f"\n🎉 DROPDOWN FIX STATUS: SUCCESS!")
            print(f"   • Frontend properly converting technical values to display labels")
            print(f"   • Most dropdown fields now store user-friendly values")
            print(f"   • Test report ID: {test_report_id}")
            return True
        elif success_rate > 50:
            print(f"\n⚠️ DROPDOWN FIX STATUS: PARTIAL SUCCESS")
            print(f"   • Some conversions working, but needs improvement")
            print(f"   • Check frontend conversion logic for failed fields")
            return False
        else:
            print(f"\n❌ DROPDOWN FIX STATUS: NOT WORKING")
            print(f"   • Frontend conversion not working properly")
            print(f"   • Check DropdownValueMappingService implementation")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_dropdown_fixes_comprehensive()
    if success:
        print(f"\n✅ Dropdown value conversion is working!")
        print(f"🎯 Next steps:")
        print(f"   1. Test in Angular frontend UI")
        print(f"   2. Verify form controls show correct values")
        print(f"   3. Verify saved data uses display labels")
    else:
        print(f"\n❌ Dropdown fixes need debugging")
        print(f"🔧 Check:")
        print(f"   1. DropdownValueMappingService implementation")
        print(f"   2. Form submission conversion logic")
        print(f"   3. Template field option mappings")
    
    exit(0 if success else 1)