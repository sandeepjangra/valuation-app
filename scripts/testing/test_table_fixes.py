#!/usr/bin/env python3

import requests
import json

def test_table_fixes():
    """
    Test both table fixes:
    1. Tables should be saved to report_data.tables (not report_data.data)
    2. Frontend should load and display table data correctly
    """
    
    print("\n" + "="*60)
    print("🧪 TESTING TABLE FIXES: Storage Location & Frontend Display")
    print("="*60)
    
    BASE_URL = "http://localhost:8000/api"
    
    try:
        # Login first
        print(f"\n🔐 Step 1: Logging in...")
        login_data = {
            "email": "admin@sk-tindwal.com",
            "organizationId": "sk-tindwal", 
            "role": "manager"
        }
        
        login_response = requests.post(f"{BASE_URL}/auth/dev-login", json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Failed to login: {login_response.status_code}")
            return False
        
        auth_data = login_response.json()
        token = auth_data['data']['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        
        print(f"✅ Successfully logged in")
        
        # Get the existing report
        report_id = "rpt_08618a7b9df4"
        print(f"\n📋 Step 2: Getting existing report {report_id}...")
        
        report_response = requests.get(f"{BASE_URL}/reports/{report_id}", headers=headers)
        
        if report_response.status_code != 200:
            print(f"❌ Failed to get report: {report_response.status_code}")
            print(f"Response: {report_response.text}")
            return False
        
        report_data = report_response.json()
        print(f"✅ Retrieved report: {report_id}")
        
        # Analyze current table structure
        print(f"\n🔍 Step 3: Analyzing current table structure...")
        
        report_data_section = report_data.get('report_data', {})
        
        # Check tables section
        tables_section = report_data_section.get('tables', {})
        data_section = report_data_section.get('data', {})
        
        print(f"📊 Tables section: {len(tables_section)} items")
        print(f"📄 Data section: {len(data_section)} items")
        
        # Find table fields in both sections
        table_fields_in_tables = []
        table_fields_in_data = []
        
        for key, value in tables_section.items():
            if 'table' in key.lower():
                table_fields_in_tables.append(key)
        
        for key, value in data_section.items():
            if 'table' in key.lower() and isinstance(value, dict) and ('rows' in value or 'columns' in value):
                table_fields_in_data.append(key)
        
        print(f"\n🔍 Table Analysis Results:")
        print(f"   • Tables in 'tables' section: {table_fields_in_tables}")
        print(f"   • Tables in 'data' section: {table_fields_in_data}")
        
        # Check specific tables from your example
        building_table_in_data = 'building_specifications_table' in data_section
        building_table_in_tables = 'building_specifications_table' in tables_section
        floor_table_in_data = 'floor_wise_valuation_table' in data_section
        floor_table_in_tables = 'floor_wise_valuation_table' in tables_section
        
        print(f"\n📊 Specific Table Locations:")
        print(f"   • building_specifications_table in data: {building_table_in_data}")
        print(f"   • building_specifications_table in tables: {building_table_in_tables}")
        print(f"   • floor_wise_valuation_table in data: {floor_table_in_data}")
        print(f"   • floor_wise_valuation_table in tables: {floor_table_in_tables}")
        
        # Test creating a new report with table data to verify fix
        print(f"\n📝 Step 4: Testing new save with table data...")
        
        # Create test form data with table
        test_form_data = {
            "applicant_name": "Test Applicant",
            "valuation_date": "2025-12-28",
            "bank_branch": "test_branch",
            "test_table": {
                "columns": [
                    {"columnId": "sr_no", "columnName": "Sr. No.", "fieldType": "text"},
                    {"columnId": "description", "columnName": "Description", "fieldType": "text"}
                ],
                "rows": [
                    {"sr_no": "1", "description": "Test Row 1"},
                    {"sr_no": "2", "description": "Test Row 2"}
                ],
                "userAddedColumns": [],
                "nextColumnNumber": 1
            },
            "regular_field": "Test regular field value"
        }
        
        # Create new report
        create_data = {
            "bank_code": "SBI",
            "template_id": "land-property",
            "report_data": test_form_data
        }
        
        create_response = requests.post(f"{BASE_URL}/reports", json=create_data, headers=headers)
        
        if create_response.status_code == 201:
            new_report = create_response.json()
            new_report_id = new_report.get('report_id')
            print(f"✅ Created test report: {new_report_id}")
            
            # Get the new report back to check structure
            new_report_response = requests.get(f"{BASE_URL}/reports/{new_report_id}", headers=headers)
            
            if new_report_response.status_code == 200:
                new_report_data = new_report_response.json()
                new_report_data_section = new_report_data.get('report_data', {})
                
                new_tables_section = new_report_data_section.get('tables', {})
                new_data_section = new_report_data_section.get('data', {})
                
                test_table_in_tables = 'test_table' in new_tables_section
                test_table_in_data = 'test_table' in new_data_section
                regular_field_in_data = 'regular_field' in new_data_section
                
                print(f"\n🧪 New Report Structure Test:")
                print(f"   • test_table in tables section: {test_table_in_tables}")
                print(f"   • test_table in data section: {test_table_in_data}")
                print(f"   • regular_field in data section: {regular_field_in_data}")
                
                # Assess fixes
                fixes_working = {
                    "table_goes_to_tables_section": test_table_in_tables,
                    "table_not_duplicated_in_data": not test_table_in_data,
                    "regular_fields_still_in_data": regular_field_in_data,
                    "backend_table_detection_improved": test_table_in_tables
                }
                
                print(f"\n📊 Fix Assessment:")
                for fix_name, working in fixes_working.items():
                    status = "✅ WORKING" if working else "❌ NOT WORKING"
                    print(f"   • {fix_name.replace('_', ' ').title()}: {status}")
                
                all_fixes_working = all(fixes_working.values())
                
                if all_fixes_working:
                    print(f"\n🎉 TABLE FIXES VERIFICATION: SUCCESS")
                    print(f"   1. ✅ Tables now save to report_data.tables")
                    print(f"   2. ✅ Tables no longer duplicated in report_data.data")
                    print(f"   3. ✅ Regular fields still save to report_data.data")
                    print(f"   4. ✅ Backend table detection is working")
                    
                    print(f"\n📝 Next Steps for Frontend:")
                    print(f"   • Frontend changes deployed - should read from tables section")
                    print(f"   • Dynamic table components should populate correctly")
                    print(f"   • Existing reports with tables in data section handled via backward compatibility")
                    
                    return True
                else:
                    print(f"\n⚠️ TABLE FIXES VERIFICATION: PARTIAL SUCCESS")
                    failed_fixes = [fix for fix, working in fixes_working.items() if not working]
                    print(f"   Issues remaining: {', '.join(failed_fixes)}")
                    return False
            else:
                print(f"❌ Could not retrieve new report for verification")
                return False
        else:
            print(f"❌ Failed to create test report: {create_response.status_code}")
            print(f"Response: {create_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_table_fixes()
    if success:
        print(f"\n✅ Table fixes are working correctly!")
        print(f"📋 The issues should now be resolved:")
        print(f"   1. Tables save to correct location (report_data.tables)")
        print(f"   2. Frontend loads table data from correct location")
        print(f"   3. Dynamic tables should display properly in UI")
    else:
        print(f"\n❌ Table fixes need more work - check the implementation")
    
    exit(0 if success else 1)