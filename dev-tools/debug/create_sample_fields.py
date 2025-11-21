#!/usr/bin/env python3
"""
Create a sample fields file for testing the API
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.utils.field_file_manager import FieldFileManager

def create_sample_fields():
    """Create sample fields file for testing"""
    print("🔧 Creating sample fields file for API testing...")
    
    # Initialize the field file manager
    field_manager = FieldFileManager()
    
    # Create comprehensive sample field data matching the API interface
    sample_fields = [
        {
            "_id": "507f1f77bcf86cd799439011",
            "fieldId": "propertyAddress",
            "technicalName": "propertyAddress",
            "fieldName": "propertyAddress",  # Keep for backward compatibility
            "fieldType": "textarea",
            "label": "Property Address",  # Keep for backward compatibility
            "uiDisplayName": "Property Address",
            "placeholder": "Enter complete property address",
            "isRequired": True,
            "fieldGroup": "property",
            "sortOrder": 1,
            "gridSize": 12,
            "isActive": True,
            "validation": {
                "maxLength": 500
            }
        },
        {
            "_id": "507f1f77bcf86cd799439012", 
            "fieldId": "contactNumber",
            "technicalName": "contactNumber",
            "fieldName": "contactNumber",
            "fieldType": "tel",
            "label": "Contact Number",
            "uiDisplayName": "Contact Number",
            "placeholder": "Enter contact number",
            "isRequired": True,
            "fieldGroup": "contact",
            "sortOrder": 2,
            "gridSize": 6,
            "isActive": True,
            "validation": {
                "pattern": "^[0-9+\\-\\s\\(\\)]+$"
            }
        },
        {
            "_id": "507f1f77bcf86cd799439013",
            "fieldId": "applicantName",
            "technicalName": "applicantName",
            "fieldName": "applicantName",
            "fieldType": "text",
            "label": "Applicant Name",
            "uiDisplayName": "Applicant Name",
            "placeholder": "Enter applicant name",
            "isRequired": True,
            "fieldGroup": "contact",
            "sortOrder": 3,
            "gridSize": 6,
            "isActive": True,
            "validation": {
                "maxLength": 100
            }
        },
        {
            "_id": "507f1f77bcf86cd799439014",
            "fieldId": "bankName",
            "technicalName": "bankName",
            "fieldName": "bankName",
            "fieldType": "select",
            "label": "Bank Name",
            "uiDisplayName": "Bank Name",
            "placeholder": "Select bank",
            "isRequired": True,
            "fieldGroup": "banking",
            "sortOrder": 4,
            "gridSize": 6,
            "isActive": True,
            "options": [
                {"value": "sbi", "label": "State Bank of India"},
                {"value": "hdfc", "label": "HDFC Bank"},
                {"value": "icici", "label": "ICICI Bank"},
                {"value": "axis", "label": "Axis Bank"}
            ]
        },
        {
            "_id": "507f1f77bcf86cd799439015",
            "fieldId": "branchName",
            "technicalName": "branchName",
            "fieldName": "branchName",
            "fieldType": "text",
            "label": "Branch Name",
            "uiDisplayName": "Branch Name",
            "placeholder": "Enter branch name",
            "isRequired": True,
            "fieldGroup": "banking",
            "sortOrder": 5,
            "gridSize": 6,
            "isActive": True,
            "validation": {
                "maxLength": 100
            }
        },
        {
            "_id": "507f1f77bcf86cd799439016",
            "fieldId": "propertyType",
            "technicalName": "propertyType",
            "fieldName": "propertyType",
            "fieldType": "select",
            "label": "Property Type",
            "uiDisplayName": "Property Type",
            "placeholder": "Select property type",
            "isRequired": True,
            "fieldGroup": "property",
            "sortOrder": 6,
            "gridSize": 6,
            "isActive": True,
            "options": [
                {"value": "residential", "label": "Residential"},
                {"value": "commercial", "label": "Commercial"},
                {"value": "industrial", "label": "Industrial"},
                {"value": "agricultural", "label": "Agricultural"}
            ]
        },
        {
            "_id": "507f1f77bcf86cd799439017",
            "fieldId": "loanAmount",
            "technicalName": "loanAmount",
            "fieldName": "loanAmount",
            "fieldType": "number",
            "label": "Loan Amount",
            "uiDisplayName": "Loan Amount",
            "placeholder": "Enter loan amount",
            "isRequired": True,
            "fieldGroup": "banking",
            "sortOrder": 7,
            "gridSize": 6,
            "isActive": True,
            "validation": {
                "min": 100000,
                "max": 50000000
            }
        },
        {
            "_id": "507f1f77bcf86cd799439018",
            "fieldId": "valuationPurpose",
            "technicalName": "valuationPurpose",
            "fieldName": "valuationPurpose",
            "fieldType": "select",
            "label": "Valuation Purpose",
            "uiDisplayName": "Valuation Purpose",
            "placeholder": "Select valuation purpose",
            "isRequired": True,
            "fieldGroup": "valuation",
            "sortOrder": 8,
            "gridSize": 6,
            "isActive": True,
            "options": [
                {"value": "loan", "label": "Home Loan"},
                {"value": "sale", "label": "Sale Transaction"},
                {"value": "insurance", "label": "Insurance"},
                {"value": "legal", "label": "Legal Purpose"}
            ]
        }
    ]
    
    # Save to file
    success = field_manager.write_fields(sample_fields)
    
    if success:
        print(f"✅ Successfully created {len(sample_fields)} sample fields")
        
        # Show file info
        file_info = field_manager.get_file_info()
        print(f"📁 File location: {field_manager.file_path}")
        print(f"📊 File size: {file_info.get('file_size')} bytes")
        print(f"🕒 Generated at: {file_info.get('generated_at')}")
        print(f"📝 Field count: {file_info.get('field_count')}")
        
        print("\n🎯 Fields created by group:")
        for group in ["contact", "property", "banking", "valuation"]:
            group_fields = [f for f in sample_fields if f.get('fieldGroup') == group]
            print(f"   • {group}: {len(group_fields)} fields")
        
        print("\n✅ Sample fields file ready for API testing!")
        
    else:
        print("❌ Failed to create sample fields file")

if __name__ == "__main__":
    create_sample_fields()