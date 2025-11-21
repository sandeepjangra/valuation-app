#!/usr/bin/env python3

"""
Create common form fields document with 6 specified fields
"""

import asyncio
import sys
import os
import json
from datetime import datetime, timezone

# Set MongoDB URI
os.environ['MONGODB_URI'] = "mongodb+srv://app_user:kHxlQqJ1Uc3bmoL6@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster"

# Add backend path
sys.path.insert(0, '/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend')

from database.multi_db_manager import MultiDatabaseSession

async def create_common_form_fields():
    """Create common form fields document with 6 specified fields"""
    try:
        print("📝 Creating common form fields document...")
        
        async with MultiDatabaseSession() as db:
            
            # Step 1: Delete all existing documents in common_form_fields collection
            existing_docs = await db.find_many("admin", "common_form_fields", {})
            for doc in existing_docs:
                await db.delete_one("admin", "common_form_fields", {"_id": doc["_id"]})
            print(f"🗑️  Deleted {len(existing_docs)} existing common form field documents")
            
            # Step 2: Create the new common fields document
            common_fields_document = {
                "_id": "common_fields",
                "collectionName": "common_form_fields",
                "description": "Common form fields used across all bank templates",
                "version": "1.0",
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "updatedAt": datetime.now(timezone.utc).isoformat(),
                "isActive": True,
                "fields": [
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
                        "gridSize": 3,
                        "sortOrder": 1,
                        "isActive": True,
                        "createdAt": datetime.now(timezone.utc).isoformat(),
                        "updatedAt": datetime.now(timezone.utc).isoformat()
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
                        "gridSize": 3,
                        "sortOrder": 2,
                        "isActive": True,
                        "createdAt": datetime.now(timezone.utc).isoformat(),
                        "updatedAt": datetime.now(timezone.utc).isoformat()
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
                        "gridSize": 3,
                        "sortOrder": 3,
                        "isActive": True,
                        "createdAt": datetime.now(timezone.utc).isoformat(),
                        "updatedAt": datetime.now(timezone.utc).isoformat()
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
                        "gridSize": 3,
                        "sortOrder": 4,
                        "isActive": True,
                        "createdAt": datetime.now(timezone.utc).isoformat(),
                        "updatedAt": datetime.now(timezone.utc).isoformat()
                    },
                    {
                        "fieldId": "valuation_purpose",
                        "technicalName": "valuation_purpose",
                        "uiDisplayName": "Valuation Purpose",
                        "fieldType": "select",
                        "isRequired": True,
                        "options": [
                            {
                                "value": "home_loan",
                                "label": "Home Loan"
                            },
                            {
                                "value": "mortgage_loan",
                                "label": "Mortgage Loan"
                            },
                            {
                                "value": "insurance",
                                "label": "Insurance Purpose"
                            },
                            {
                                "value": "legal_settlement",
                                "label": "Legal Settlement"
                            },
                            {
                                "value": "sale_purchase",
                                "label": "Sale/Purchase"
                            },
                            {
                                "value": "stamp_duty",
                                "label": "Stamp Duty Assessment"
                            },
                            {
                                "value": "bank_purpose",
                                "label": "Bank Purpose"
                            },
                            {
                                "value": "other",
                                "label": "Other"
                            }
                        ],
                        "placeholder": "Select valuation purpose",
                        "helpText": "Reason for conducting this property valuation",
                        "gridSize": 3,
                        "sortOrder": 5,
                        "isActive": True,
                        "createdAt": datetime.now(timezone.utc).isoformat(),
                        "updatedAt": datetime.now(timezone.utc).isoformat()
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
                        "gridSize": 3,
                        "sortOrder": 6,
                        "isActive": True,
                        "createdAt": datetime.now(timezone.utc).isoformat(),
                        "updatedAt": datetime.now(timezone.utc).isoformat()
                    }
                ]
            }
            
            # Insert the new document
            await db.insert_one("admin", "common_form_fields", common_fields_document)
            
            total_fields = len(common_fields_document["fields"])
            
            print(f"\n✅ Created common form fields document:")
            print(f"   📊 Total Fields: {total_fields}")
            print(f"   🆔 Document ID: common_fields")
            print(f"   📝 All fields are active and properly ordered")
            
            # Show the fields summary
            print(f"\n📋 Fields Created:")
            for i, field in enumerate(common_fields_document["fields"], 1):
                field_id = field["fieldId"]
                display_name = field["uiDisplayName"]
                field_type = field["fieldType"]
                is_required = "Required" if field["isRequired"] else "Optional"
                print(f"   {i}. {field_id} - {display_name} ({field_type}, {is_required})")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating common form fields: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(create_common_form_fields())
    if success:
        print(f"\n🎉 SUCCESS: Common form fields document created!")
        print(f"📡 Database: valuation_admin")
        print(f"📂 Collection: common_form_fields")
        print(f"📄 Document: common_fields")
        print(f"🔗 These fields will be aggregated with bank-specific templates")
    else:
        print(f"\n❌ FAILED to create common form fields!")
        sys.exit(1)