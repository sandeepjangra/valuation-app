#!/usr/bin/env python3

import requests
import json
from datetime import datetime

def test_dropdown_value_fix():
    """
    Test the dropdown value fix by:
    1. Getting existing report rpt_c1a9c6224707 with technical values
    2. Creating a copy to test our fixes
    3. Verifying frontend converts values correctly
    """
    
    print("🔄 TESTING DROPDOWN VALUE CONVERSION FIX")
    print("=" * 50)
    
    BASE_URL = "http://localhost:8000/api"
    
    try:
        # Login
        print("🔐 Logging in...")
        login_data = {
            "email": "admin@sk-tindwal.com",
            "organizationId": "sk-tindwal",
            "role": "manager"
        }
        
        login_response = requests.post(f"{BASE_URL}/auth/dev-login", json=login_data, timeout=10)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
        
        token = login_response.json()['data']['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful")
        
        # Get existing report with dropdown issues
        report_id = "rpt_c1a9c6224707"
        print(f"\n📋 Getting existing report {report_id}...")
        
        report_response = requests.get(f"{BASE_URL}/reports/{report_id}", headers=headers, timeout=10)
        
        if report_response.status_code != 200:
            print(f"❌ Failed to get report: {report_response.status_code}")
            return False
        
        original_report = report_response.json()['data']
        print(f"✅ Retrieved report: {report_id}")
        
        # Analyze dropdown values in original report
        print(f"\n🔍 ANALYZING DROPDOWN VALUES IN ORIGINAL REPORT:")
        report_data = original_report.get('report_data', {})
        
        # Check common fields
        common_fields = report_data.get('common_fields', {})
        data_fields = report_data.get('data', {})
        
        dropdown_examples = {}
        
        # Known dropdown fields with their current values
        dropdown_fields_to_check = {
            'bank_branch': common_fields.get('bank_branch'),
            'building_constructed': data_fields.get('building_constructed'),
            'city_town_village': data_fields.get('city_town_village'),
            'socio_economic_class': data_fields.get('socio_economic_class'), 
            'urban_rural': data_fields.get('urban_rural'),
            'area_type': data_fields.get('area_type'),
            'municipal_corporation': data_fields.get('municipal_corporation'),
            'corner_or_intermittent': data_fields.get('corner_or_intermittent'),
            'road_type_present': data_fields.get('road_type_present'),
            'road_width': data_fields.get('road_width'),
            'landlocked_status': data_fields.get('landlocked_status'),
            'water_potentiality': data_fields.get('water_potentiality'),
            'underground_sewerage': data_fields.get('underground_sewerage'),
            'power_supply_available': data_fields.get('power_supply_available'),
            'flooding_possibility': data_fields.get('flooding_possibility'),
            'town_planning_approved': data_fields.get('town_planning_approved'),
            'road_facilities': data_fields.get('road_facilities'),
            'building_type': data_fields.get('building_type'),
            'construction_type': data_fields.get('construction_type'),
            'exterior_condition': data_fields.get('exterior_condition'),
            'interior_condition': data_fields.get('interior_condition')
        }
        
        for field_name, field_value in dropdown_fields_to_check.items():
            if field_value:
                dropdown_examples[field_name] = field_value
                
        print(f"📊 Found dropdown values:")
        for field, value in dropdown_examples.items():
            print(f"   • {field}: '{value}'")
        
        # Create expected conversions based on our template analysis
        expected_conversions = {
            'building_constructed': {'yes': 'Yes - Building Exists', 'no': 'No - Only Land (No Building)'},
            'corner_or_intermittent': {
                'corner': 'Corner Plot', 
                'intermittent': 'Intermittent Plot', 
                'middle': 'Middle Plot',
                'end': 'End Plot'
            },
            'road_type_present': {
                'cc_road': 'CC Road',
                'tar_road': 'Tar Road', 
                'concrete_road': 'Concrete Road',
                'metal_road': 'Metal Road',
                'kutcha_road': 'Kutcha Road'
            },
            'road_width': {
                'below_20': 'Below 20 ft',
                '20_30': '20-30 ft',
                '30_40': '30-40 ft',
                'above_40': 'Above 40 ft'
            },
            'landlocked_status': {'yes': 'Yes', 'no': 'No'},
            'water_potentiality': {'yes': 'Yes', 'no': 'No'},
            'underground_sewerage': {'yes': 'Yes', 'no': 'No'},
            'power_supply_available': {'yes': 'Yes', 'no': 'No'},
            'town_planning_approved': {'yes': 'Yes', 'no': 'No', 'applied': 'Applied For'},
            'road_facilities': {'yes': 'Yes', 'no': 'No'}
        }
        
        print(f"\n💡 EXPECTED CONVERSIONS AFTER FIX:")
        issues_found = 0
        for field_name, current_value in dropdown_examples.items():
            if field_name in expected_conversions and current_value in expected_conversions[field_name]:
                expected_label = expected_conversions[field_name][current_value]
                print(f"   • {field_name}: '{current_value}' → '{expected_label}'")
                if current_value != expected_label:
                    issues_found += 1
        
        print(f"\n📊 ISSUE SUMMARY:")
        print(f"   • Total dropdown fields checked: {len(dropdown_examples)}")
        print(f"   • Fields with conversion mappings: {len(expected_conversions)}")
        print(f"   • Values needing conversion: {issues_found}")
        
        if issues_found == 0:
            print(f"   ℹ️ No technical values found - data may already be converted")
        else:
            print(f"   🔧 Technical values found that should be converted to display labels")
        
        # Create a copy of the report to test fixes (without modifying original)
        print(f"\n📄 CREATING TEST COPY OF REPORT...")
        
        # Create new report with same data
        test_data = original_report['report_data'].copy()
        
        create_request = {
            "bank_code": original_report['bank_code'],
            "template_id": original_report['template_id'],
            "report_data": test_data
        }
        
        create_response = requests.post(f"{BASE_URL}/reports", json=create_request, headers=headers, timeout=10)
        
        if create_response.status_code == 201:
            test_report = create_response.json()
            test_report_id = test_report['data']['report_id'] if 'data' in test_report else test_report.get('report_id')
            print(f"✅ Created test report copy: {test_report_id}")
            
            print(f"\n🎯 TEST INSTRUCTIONS:")
            print(f"1. 🚀 Start Angular frontend: `cd valuation-frontend && ng serve`")
            print(f"2. 🔐 Login to the application")
            print(f"3. 📝 Edit report: {test_report_id}")
            print(f"4. 🔍 Verify dropdown fields show display labels (not technical codes)")
            print(f"5. 💾 Save the report and verify stored values are display labels")
            print(f"")
            print(f"🔍 Key fields to check:")
            for field, value in list(dropdown_examples.items())[:5]:
                expected = expected_conversions.get(field, {}).get(value, value)
                print(f"   • {field}: Should show '{expected}' (currently stored as '{value}')")
            
            print(f"\n📊 VALIDATION CHECKLIST:")
            print(f"✅ Original report preserved: {report_id}")
            print(f"✅ Test report created: {test_report_id}")
            print(f"🔄 Frontend dropdown conversion: Ready for testing")
            print(f"🔄 Backend storage conversion: Ready for testing")
            
            return True
            
        else:
            print(f"❌ Failed to create test report: {create_response.status_code}")
            print(f"Response: {create_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_dropdown_value_fix()
    
    if success:
        print(f"\n🎉 DROPDOWN VALUE FIX TESTING SETUP COMPLETE!")
        print(f"Ready to test the conversion of technical values to display labels")
    else:
        print(f"\n❌ Setup failed - check the implementation")
    
    exit(0 if success else 1)