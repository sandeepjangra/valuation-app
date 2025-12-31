#!/usr/bin/env python3
"""
Test script to verify PDF generation system functionality.
"""

import os
import sys
import requests
import json
from datetime import datetime

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_pdf_generation_api():
    """Test the PDF generation API endpoint."""
    
    base_url = "http://localhost:8000"
    
    # Sample report data structure based on the frontend implementation
    sample_report_data = {
        "reportId": "test_report_123",
        "bankCode": "SBI",
        "propertyType": "land",
        "templateData": {
            "bankCode": "SBI",
            "templateName": "SBI Land Property Valuation",
            "propertyType": "land",
            "documents": [
                {
                    "sections": [
                        {
                            "title": "Property Information",
                            "fields": [
                                {"fieldId": "property_address", "label": "Property Address", "value": "123 Test Street, Mumbai"},
                                {"fieldId": "survey_number", "label": "Survey Number", "value": "123/1A"},
                                {"fieldId": "total_area", "label": "Total Area (sq.ft)", "value": "2500"}
                            ]
                        },
                        {
                            "title": "Valuation Details",
                            "fields": [
                                {"fieldId": "market_value_per_sqft", "label": "Market Value per sq.ft (₹)", "value": "5000"},
                                {"fieldId": "estimated_value_land", "label": "Estimated Value of Land (₹)", "value": "12500000"}
                            ]
                        }
                    ]
                }
            ]
        },
        "formValues": {
            "property_address": "123 Test Street, Mumbai",
            "survey_number": "123/1A",
            "total_area": "2500",
            "market_value_per_sqft": "5000",
            "estimated_value_land": "12500000"
        },
        "reportReferenceNumber": "REF-2024-001",
        "organizationShortName": "TestOrg"
    }
    
    try:
        print("🔍 Testing PDF generation API...")
        
        # Test the PDF generation endpoint
        response = requests.post(
            f"{base_url}/api/reports/test_report_123/generate-pdf",
            json=sample_report_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ PDF generation API working!")
            
            # Save the PDF file for verification
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_filename = f"test_sbi_land_valuation_{timestamp}.pdf"
            
            with open(pdf_filename, "wb") as f:
                f.write(response.content)
            
            print(f"📄 PDF saved as: {pdf_filename}")
            print(f"📏 PDF size: {len(response.content)} bytes")
            
            return True
        else:
            print(f"❌ PDF generation failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the backend server is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_pdf_templates_list():
    """Test the PDF templates list endpoint."""
    
    base_url = "http://localhost:8000"
    
    try:
        print("\n🔍 Testing PDF templates list API...")
        
        response = requests.get(f"{base_url}/api/pdf-templates")
        
        if response.status_code == 200:
            templates = response.json()
            print("✅ PDF templates API working!")
            print(f"📋 Available templates: {json.dumps(templates, indent=2)}")
            return True
        else:
            print(f"❌ Templates list failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_health_check():
    """Test the backend health check."""
    
    base_url = "http://localhost:8000"
    
    try:
        print("\n🔍 Testing backend health check...")
        
        response = requests.get(f"{base_url}/api/health")
        
        if response.status_code == 200:
            print("✅ Backend is healthy!")
            return True
        else:
            print(f"❌ Health check failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function."""
    
    print("🚀 Starting PDF Generation System Tests")
    print("=" * 50)
    
    # Test backend health
    if not test_health_check():
        print("\n❌ Backend not available. Please start the backend server first:")
        print("   cd backend && python main.py")
        return
    
    # Test PDF templates list
    test_pdf_templates_list()
    
    # Test PDF generation
    success = test_pdf_generation_api()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All PDF generation tests passed!")
        print("\n📝 Next steps:")
        print("1. Check the generated PDF file")
        print("2. Test from the frontend UI")
        print("3. Customize templates as needed")
    else:
        print("❌ Some tests failed. Check the backend logs and dependencies.")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure WeasyPrint is installed: pip install weasyprint")
        print("2. Check backend logs for detailed error messages")
        print("3. Verify MongoDB connection is working")

if __name__ == "__main__":
    main()