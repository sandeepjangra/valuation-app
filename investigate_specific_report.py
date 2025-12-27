#!/usr/bin/env python3
"""
Investigate specific report rpt_431b6b6ada7f from sk-tindwal to analyze the structure issue
"""

import requests
import json

def investigate_specific_report():
    """Investigate the specific problematic report"""
    
    print("🔍 INVESTIGATING REPORT: rpt_431b6b6ada7f")
    print("=" * 80)
    
    # Login to sk-tindwal org
    login_data = {"email": "sk.tindwal@gmail.com", "password": "admin123"}
    login_response = requests.post("http://localhost:8000/api/auth/login", json=login_data, timeout=10)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    token = login_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print("✅ Login successful for sk.tindwal@gmail.com")
    
    # Get the specific report
    try:
        response = requests.get(
            f"http://localhost:8000/api/reports/rpt_431b6b6ada7f?organization_id=sk-tindwal",
            headers=headers,
            timeout=10
        )
        
        print(f"\n📥 Get report response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                report = result["data"]
                
                print(f"✅ Report found: {report.get('report_id')}")
                print(f"📄 Reference: {report.get('reference_number')}")
                print(f"🏢 Organization: {report.get('organization_id')}")
                print(f"📅 Created: {report.get('created_at')}")
                
                # Analyze the structure in detail
                print(f"\n🔍 DETAILED STRUCTURE ANALYSIS:")
                
                # Show root level fields
                print(f"📋 Root level fields:")
                for key, value in report.items():
                    if key != "report_data":
                        print(f"   📄 {key}: {type(value).__name__} = {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}")
                
                # Analyze report_data structure
                report_data = report.get("report_data", {})
                print(f"\n📂 report_data structure ({len(report_data)} top-level keys):")
                
                duplicate_issues = []
                structure_issues = []
                
                for key, value in report_data.items():
                    if isinstance(value, dict):
                        print(f"   📁 {key}: dict with {len(value)} keys")
                        
                        # Check for nested structure issues
                        for sub_key, sub_value in value.items():
                            if isinstance(sub_value, dict):
                                print(f"      📂 {sub_key}: dict with {len(sub_value)} keys")
                                
                                # Check for group fields vs individual fields
                                for field_id, field_value in sub_value.items():
                                    if isinstance(field_value, dict):
                                        print(f"         🔗 GROUP {field_id}: {len(field_value)} subfields")
                                        for sf_id, sf_value in field_value.items():
                                            print(f"            ↳ {sf_id}: {str(sf_value)[:30]}{'...' if len(str(sf_value)) > 30 else ''}")
                                    else:
                                        print(f"         📄 {field_id}: {str(field_value)[:30]}{'...' if len(str(field_value)) > 30 else ''}")
                            else:
                                print(f"      📄 {sub_key}: {str(sub_value)[:30]}{'...' if len(str(sub_value)) > 30 else ''}")
                    else:
                        print(f"   📄 {key}: {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}")
                
                # Check for specific issues
                print(f"\n❌ PROBLEM DETECTION:")
                
                # 1. Check for duplicate status
                status_locations = []
                if "status" in report:
                    status_locations.append(f"root (value: {report['status']})")
                if "status" in report_data:
                    status_locations.append(f"report_data (value: {report_data['status']})")
                
                if len(status_locations) > 1:
                    duplicate_issues.append(f"Duplicate status fields found in: {status_locations}")
                
                # 2. Check for both property_details and Property Details
                has_property_details = "property_details" in report_data
                has_Property_Details = "Property Details" in report_data
                
                if has_property_details and has_Property_Details:
                    duplicate_issues.append("Both 'property_details' and 'Property Details' tabs exist")
                
                # 3. Check for _unmapped_ section
                if "_unmapped_" in report_data:
                    unmapped_fields = report_data["_unmapped_"]
                    if unmapped_fields:
                        structure_issues.append(f"_unmapped_ section contains {len(unmapped_fields)} fields: {list(unmapped_fields.keys())}")
                
                # 4. Check for metadata in report_data
                metadata_fields = ['status', 'bankName', 'templateName', 'organizationId', 'customTemplateId']
                found_metadata = [field for field in metadata_fields if field in report_data]
                if found_metadata:
                    structure_issues.append(f"Metadata fields in report_data: {found_metadata}")
                
                # Print all issues
                if duplicate_issues or structure_issues:
                    print(f"   ❌ Issues found:")
                    for issue in duplicate_issues:
                        print(f"      🔥 DUPLICATE: {issue}")
                    for issue in structure_issues:
                        print(f"      ⚠️ STRUCTURE: {issue}")
                else:
                    print(f"   ✅ No issues detected - structure looks correct")
                
                return report
                
        else:
            print(f"❌ Request failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    investigate_specific_report()