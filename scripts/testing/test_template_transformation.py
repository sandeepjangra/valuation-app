#!/usr/bin/env python3
"""
Test script to verify template transformation is working correctly.
"""

import requests
import json

def test_report_transformation():
    """Test that flat data is transformed to template structure."""
    
    base_url = "http://localhost:8000"
    
    # First, authenticate to get a token
    print("🔐 Authenticating...")
    try:
        # Use dev-login for testing  
        auth_response = requests.post(f"{base_url}/api/auth/dev-login", json={
            "email": "admin@system.com",
            "organizationId": "69230833b51083d26dab6087",  # Use actual org ID from database
            "role": "system_admin"
        }, timeout=10)
        
        if auth_response.status_code != 200:
            print(f"❌ Authentication failed: {auth_response.status_code}")
            print(f"Response: {auth_response.text}")
            return
        
        token = auth_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        print("✅ Authentication successful")
        
    except Exception as e:
        print(f"❌ Auth error: {str(e)}")
        return
    
    # Sample flat data (similar to what frontend would send)
    flat_report_data = {
        "report_reference_number": "TEST-REF-12345",  # Provide a fixed reference number
        "applicant_name": "Test Applicant",
        "property_address": "Test Property Address, Test City",
        "land_area": "1000",
        "land_rate": "500",
        "land_value": "500000",
        "building_type": "Residential",
        "total_construction_area": "2000",
        "construction_rate": "1500",
        "construction_value": "3000000",
        "total_valuation": "3500000",
        "inspection_date": "2024-12-25",
        "valuation_date": "2024-12-25",
        "boundaries_dimensions_table": [
            {"direction": "North", "boundary": "Road", "dimension": "50 ft"},
            {"direction": "South", "boundary": "Plot", "dimension": "50 ft"}
        ],
        "building_specifications_table": [
            {"component": "Foundation", "specification": "RCC", "area": "200"}
        ]
    }
    
    # Test data for organization context
    org_data = {
        "organization_id": "system_org_id",
        "organization_name": "System Organization",
        "template_type": "SBI",
        "template_category": "land-property"
    }
    
    try:
        # Create a report with flat data
        print("🧪 Testing report creation with flat data...")
        print("📤 Sending flat data structure to API")
        
        # Structure the request according to ReportCreateRequest model
        request_data = {
            "bank_code": "SBI",
            "template_id": "land-property",
            "property_address": flat_report_data["property_address"],
            "report_data": flat_report_data  # This is the flat data that should be transformed
        }
        
        response = requests.post(
            "http://localhost:8000/api/reports",
            json=request_data,
            headers=headers,
            timeout=10
        )
        
        print(f"📨 Response status: {response.status_code}")
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            print("✅ Report created successfully!")
            
            # Handle different response formats
            if isinstance(result, dict):
                report_id = result.get('id') or result.get('report_id') or 'Not found'
                print(f"📋 Report ID: {report_id}")
                
                # Check if the response contains report_data or data with report_data
                report_data = None
                if 'report_data' in result:
                    report_data = result['report_data']
                elif 'data' in result and isinstance(result['data'], dict) and 'report_data' in result['data']:
                    report_data = result['data']['report_data']
                elif 'data' in result:
                    report_data = result['data']
                
                # Check if it has template structure (tab organization)
                expected_tabs = [
                    "Property Details", 
                    "Site Characteristics", 
                    "Valuation", 
                    "Construction Specifications", 
                    "Detailed Valuation"
                ]
                
                print("\n🔍 Analyzing saved report structure...")
                
                found_tabs = []
                for tab in expected_tabs:
                    if tab in report_data:
                        found_tabs.append(tab)
                        if 'documents' in report_data[tab]:
                            doc_count = len(report_data[tab]['documents'])
                            print(f"  ✅ {tab}: {doc_count} fields")
                        else:
                            print(f"  ⚠️  {tab}: No documents structure")
                    else:
                        print(f"  ❌ {tab}: Missing")
                
                if len(found_tabs) > 0:
                    print(f"\n🎉 Transformation SUCCESS! Found {len(found_tabs)}/{len(expected_tabs)} tabs")
                    
                    # Show sample of transformed data
                    for tab in found_tabs[:2]:  # Show first 2 tabs
                        if 'documents' in report_data[tab] and len(report_data[tab]['documents']) > 0:
                            print(f"\n📄 Sample from {tab}:")
                            for i, doc in enumerate(report_data[tab]['documents'][:3]):  # Show first 3 fields
                                print(f"    {i+1}. {doc.get('fieldId', 'Unknown')}: {doc.get('value', 'No value')}")
                else:
                    print("\n❌ Transformation FAILED: No template tabs found")
                    print("Raw response structure:", list(report_data.keys())[:10])
            else:
                print("⚠️  No report_data in response")
                
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")

if __name__ == "__main__":
    test_report_transformation()