#!/usr/bin/env python3
"""
Script to recreate the common_form_field collection with new simplified structure.
This will clear the existing collection and add only the specified fields.
"""

import sys
import os
from datetime import datetime, timezone
from pymongo import MongoClient
from bson import ObjectId

def create_new_common_fields():
    """Create new common fields structure as specified by user"""
    
    # Fields in the order specified by user
    fields = [
        {
            "fieldId": "report_reference_number",
            "technicalName": "report_reference_number",
            "uiDisplayName": "Report Reference Number",
            "fieldType": "text",
            "isRequired": True,
            "placeholder": "Enter report reference number",
            "helpText": "Unique reference number for this valuation report",
            "validation": {
                "pattern": "^[A-Z]{2,4}[0-9]{4,8}$",
                "maxLength": 20
            },
            "gridSize": 6,
            "sortOrder": 1,
            "isActive": True
        },
        {
            "fieldId": "valuation_date",
            "technicalName": "valuation_date",
            "uiDisplayName": "Valuation Date",
            "fieldType": "date",
            "isRequired": True,
            "defaultValue": "today",
            "placeholder": "Select valuation date",
            "helpText": "Date when the property valuation was conducted",
            "validation": {
                "maxDate": "today",
                "minDate": "2020-01-01"
            },
            "gridSize": 6,
            "sortOrder": 2,
            "isActive": True
        },
        {
            "fieldId": "inspection_date",
            "technicalName": "inspection_date",
            "uiDisplayName": "Inspection Date",
            "fieldType": "date",
            "isRequired": True,
            "placeholder": "Select inspection date",
            "helpText": "Date when the property was physically inspected",
            "validation": {
                "maxDate": "today",
                "minDate": "2020-01-01"
            },
            "gridSize": 6,
            "sortOrder": 3,
            "isActive": True
        },
        {
            "fieldId": "valuation_purpose",
            "technicalName": "valuation_purpose",
            "uiDisplayName": "Valuation Purpose",
            "fieldType": "select",
            "isRequired": True,
            "options": [
                {"value": "home_loan", "label": "Home Loan"},
                {"value": "mortgage_loan", "label": "Mortgage Loan"},
                {"value": "insurance", "label": "Insurance Purpose"},
                {"value": "legal_settlement", "label": "Legal Settlement"},
                {"value": "sale_purchase", "label": "Sale/Purchase"},
                {"value": "stamp_duty", "label": "Stamp Duty Assessment"},
                {"value": "other", "label": "Other"}
            ],
            "placeholder": "Select valuation purpose",
            "helpText": "Reason for conducting this property valuation",
            "gridSize": 6,
            "sortOrder": 4,
            "isActive": True
        },
        {
            "fieldId": "applicant_name",
            "technicalName": "applicant_name",
            "uiDisplayName": "Applicant Name",
            "fieldType": "text",
            "isRequired": True,
            "placeholder": "Enter applicant's full name",
            "helpText": "Full name of the loan applicant/property owner",
            "validation": {
                "minLength": 3,
                "maxLength": 100,
                "pattern": "^[a-zA-Z\\s\\.]+$"
            },
            "gridSize": 6,
            "sortOrder": 5,
            "isActive": True
        },
        {
            "fieldId": "bank_name",
            "technicalName": "bank_name",
            "uiDisplayName": "Bank Name",
            "fieldType": "text",
            "isRequired": True,
            "isReadonly": True,
            "placeholder": "Bank name (selected from previous page)",
            "helpText": "Name of the lending bank/financial institution (auto-populated from selection)",
            "gridSize": 6,
            "sortOrder": 6,
            "isActive": True
        },
        {
            "fieldId": "bank_branch",
            "technicalName": "bank_branch",
            "uiDisplayName": "Bank Branch",
            "fieldType": "select_dynamic",
            "dataSource": "banks_collection",
            "dataSourceConfig": {
                "collection": "banks",
                "nestedPath": "branches",
                "valueField": "branchId",
                "labelField": "branchName",
                "filter": {
                    "bankCode": "{selected_bank_code}",
                    "branches.isActive": True
                },
                "sortBy": "branches.branchName",
                "dependsOn": "selected_bank"
            },
            "isRequired": True,
            "placeholder": "Select branch",
            "helpText": "Choose the specific bank branch for this application",
            "gridSize": 6,
            "sortOrder": 7,
            "isActive": True
        }
    ]
    
    # Add common metadata to each field
    current_time = datetime.now(timezone.utc)
    for i, field in enumerate(fields):
        field.update({
            "_id": str(ObjectId()),
            "createdAt": current_time,
            "updatedAt": current_time,
            "version": 1,
            "createdBy": "system_recreate",
            "metadata": {
                "recreated": True,
                "original_field_count": 36,
                "new_simplified_structure": True
            }
        })
    
    return fields

def main():
    """Main function to recreate the collection"""
    client = None
    try:
        print("🔄 Starting common_form_field collection recreation...")
        
        # Get MongoDB connection string from environment
        mongodb_uri = os.getenv("MONGODB_URI")
        if not mongodb_uri:
            raise ValueError("MONGODB_URI environment variable is required")
        
        # Connect to MongoDB
        print("📊 Connecting to MongoDB...")
        client = MongoClient(mongodb_uri, tlsAllowInvalidCertificates=True)
        
        # Get the valuation_admin database
        db = client['valuation_admin']
        collection = db['common_form_fields']
        
        # Clear existing collection
        print("🗑️  Clearing existing common_form_fields collection...")
        result = collection.delete_many({})
        print(f"   Deleted {result.deleted_count} existing documents")
        
        # Create new fields
        print("📝 Creating new simplified common fields...")
        new_fields = create_new_common_fields()
        
        # Insert new fields
        print(f"💾 Inserting {len(new_fields)} new fields...")
        result = collection.insert_many(new_fields)
        print(f"   Successfully inserted {len(result.inserted_ids)} documents")
        
        # Verify the insertion
        print("🔍 Verifying insertion...")
        count = collection.count_documents({})
        print(f"   Total documents in collection: {count}")
        
        # Show the new structure
        print("\n📋 New Common Fields Structure:")
        print("=" * 70)
        for field in new_fields:
            print(f"{field['sortOrder']:2}. {field['uiDisplayName']:<25} ({field['fieldType']:<15}) {'✅ Required' if field['isRequired'] else '❌ Optional'}")
        
        print(f"\n✅ Successfully recreated common_form_field collection!")
        print(f"   - Old field count: 36")
        print(f"   - New field count: {len(new_fields)}")
        print(f"   - All fields are active and properly ordered")
        print(f"   - No groupField grouping (as requested)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error recreating collection: {str(e)}")
        return False
    finally:
        if client:
            try:
                client.close()
            except:
                pass

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)