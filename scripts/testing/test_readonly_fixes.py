#!/usr/bin/env python3
"""
Test the readonly field fixes by creating a sample report with calculated values
"""
import os
import sys
sys.path.append('/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend')

import requests
import json

def test_readonly_fields():
    print("🧪 Testing readonly field fixes...")
    
    # Test backend is running
    try:
        response = requests.get('http://localhost:8000/health')
        print("✅ Backend is running")
    except:
        print("❌ Backend not accessible at http://localhost:8000")
        return
    
    # Create a test report with calculated values to see if they display
    test_report_data = {
        "bank_code": "SBI",
        "template_code": "land-property", 
        "property_type": "land",
        "report_data": {
            "common_fields": {
                "valuation_date": "2025-12-31",
                "applicant_name": "Test User",
                "valuation_purpose": "Home Loan"
            },
            "data": {
                # Add some calculated field values for testing
                "land_area": "1000",
                "land_rate_per_sq_unit": "5000",
                "estimated_value_of_land": "5000000",  # This should show in readonly field
                "total_land_value": "5000000"
            }
        }
    }
    
    print("📝 Creating test report with calculated values...")
    try:
        response = requests.post(
            'http://localhost:8000/api/reports',
            json=test_report_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            report_id = result.get('report_id') or result.get('_id')
            reference_number = result.get('reference_number')
            
            print(f"✅ Test report created:")
            print(f"   Report ID: {report_id}")
            print(f"   Reference Number: {reference_number}")
            
            print(f"\n🌐 Test the fixes in your browser:")
            print(f"   1. Navigate to: http://localhost:4200")
            print(f"   2. Go to Reports page")
            print(f"   3. Open report: {reference_number}")
            print(f"   4. Check if Report Reference Number field shows: {reference_number}")
            print(f"   5. Check if Estimated Value of Land shows: 5000000")
            print(f"   6. Verify information icons are smaller and only use helpText")
            
        else:
            print(f"❌ Failed to create test report: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error creating test report: {e}")

if __name__ == "__main__":
    test_readonly_fields()