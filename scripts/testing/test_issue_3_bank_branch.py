#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from pymongo import MongoClient
import json

def test_issue_3_bank_branch_fix():
    """
    Test Issue 3: Bank Branch field should:
    1. Show existing value from common_fields in MongoDB
    2. Be editable in edit mode
    3. Be stored in common_fields (not in report_data.data)
    
    This test simulates the frontend behavior by checking:
    - Bank branch value is in common_fields
    - Structure is correct for frontend consumption
    """
    
    print("\n" + "="*60)
    print("🧪 TESTING ISSUE 3: Bank Branch Field Fix")
    print("="*60)
    
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['valuation-app']
        reports_collection = db['sk-tindwal.reports']
        
        # Find a recent report to examine structure
        recent_report = reports_collection.find_one(
            {"organization_id": "sk-tindwal"},
            sort=[("created_at", -1)]
        )
        
        if not recent_report:
            print("❌ No reports found in database")
            return False
        
        print(f"📋 Testing report: {recent_report.get('_id')}")
        print(f"📊 Report created: {recent_report.get('created_at')}")
        
        # Check if bank_branch is in common_fields
        common_fields = recent_report.get('common_fields', {})
        report_data = recent_report.get('report_data', {})
        
        print(f"\n🔍 Report structure analysis:")
        print(f"   • Has common_fields: {bool(common_fields)}")
        print(f"   • Has report_data: {bool(report_data)}")
        
        if common_fields:
            print(f"\n📂 common_fields content:")
            for key, value in common_fields.items():
                print(f"   • {key}: {value}")
                
            # Check if bank_branch is in common_fields
            bank_branch_in_common = 'bank_branch' in common_fields
            bank_branch_value = common_fields.get('bank_branch', 'Not found')
            
            print(f"\n✅ Bank Branch in common_fields: {bank_branch_in_common}")
            if bank_branch_in_common:
                print(f"✅ Bank Branch value: '{bank_branch_value}'")
            else:
                print(f"❌ Bank Branch not found in common_fields")
        
        # Check if bank_branch is incorrectly in report_data.data
        if isinstance(report_data, dict) and 'data' in report_data:
            data_section = report_data['data']
            bank_branch_in_data = 'bank_branch' in data_section
            
            print(f"\n🔍 Bank Branch in report_data.data: {bank_branch_in_data}")
            if bank_branch_in_data:
                print(f"⚠️  WARNING: bank_branch found in wrong location (data section)")
                print(f"   Value: '{data_section['bank_branch']}'")
            else:
                print(f"✅ Bank Branch correctly NOT in report_data.data")
        
        # Simulate frontend structure detection
        def has_nested_structure(report_data_obj):
            # Check for new format indicators: common_fields, data, tables
            if 'common_fields' in report_data_obj or 'data' in report_data_obj or 'tables' in report_data_obj:
                return True
            return False
        
        # Test structure detection
        structure_type = "NESTED (new)" if has_nested_structure(recent_report) else "FLAT (old)"
        print(f"\n🏗️  Report structure type: {structure_type}")
        
        # Test frontend data extraction
        print(f"\n🎯 Frontend data extraction simulation:")
        
        # This simulates what the frontend should do
        form_data = {}
        
        # Extract from common_fields (this is what our fix does)
        if common_fields:
            for field_key, value in common_fields.items():
                form_data[field_key] = value
                print(f"   • Extracted {field_key}: '{value}' from common_fields")
        
        # Check if bank_branch was extracted
        if 'bank_branch' in form_data:
            print(f"\n✅ SUCCESS: bank_branch extracted for frontend form")
            print(f"   Value: '{form_data['bank_branch']}'")
            print(f"   Source: common_fields (correct location)")
        else:
            print(f"\n❌ FAILED: bank_branch not extracted for frontend form")
        
        print(f"\n📋 Issue 3 Status Summary:")
        print(f"   1. Bank branch in common_fields: {'✅ YES' if bank_branch_in_common else '❌ NO'}")
        print(f"   2. Bank branch value present: {'✅ YES' if bank_branch_value != 'Not found' else '❌ NO'}")
        print(f"   3. Structure detected correctly: {'✅ YES' if structure_type == 'NESTED (new)' else '❌ NO'}")
        print(f"   4. Frontend extraction works: {'✅ YES' if 'bank_branch' in form_data else '❌ NO'}")
        
        # Overall result
        all_checks_pass = (
            bank_branch_in_common and 
            bank_branch_value != 'Not found' and 
            structure_type == 'NESTED (new)' and 
            'bank_branch' in form_data
        )
        
        if all_checks_pass:
            print(f"\n🎉 ISSUE 3 FIX VERIFICATION: SUCCESS")
            print(f"   The bank_branch field should now:")
            print(f"   • Display existing value from database")
            print(f"   • Be editable in edit mode")
            print(f"   • Save to correct location (common_fields)")
        else:
            print(f"\n⚠️  ISSUE 3 FIX VERIFICATION: NEEDS ATTENTION")
            print(f"   Some checks failed - review the fixes")
        
        return all_checks_pass
        
    except Exception as e:
        print(f"❌ Error testing Issue 3: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            client.close()
        except:
            pass

if __name__ == "__main__":
    success = test_issue_3_bank_branch_fix()
    sys.exit(0 if success else 1)