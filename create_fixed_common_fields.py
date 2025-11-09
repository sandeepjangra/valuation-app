#!/usr/bin/env python3
"""
Create new common_form_fields document with corrected bank_branch configuration
Author: System
Date: 2024-01-20
Purpose: Fix bank_branch field to reference unified banks document structure
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from database.multi_db_manager import MultiDatabaseManager
from datetime import datetime, timezone

async def main():
    print("Creating new common_form_fields document with corrected bank_branch...")
    
    # Initialize database manager
    db_manager = MultiDatabaseManager()
    await db_manager.connect()
    print("✓ Connected to MongoDB")
    
    try:
        # Define the corrected common form fields with proper bank_branch configuration
        common_fields_document = {
            "_id": "common_fields",
            "fields": [
                {
                    "fieldName": "report_reference_number",
                    "fieldType": "text",
                    "label": "Report Reference Number",
                    "required": True,
                    "sortOrder": 1,
                    "validation": {
                        "pattern": "^[A-Z0-9-/]+$",
                        "maxLength": 50
                    }
                },
                {
                    "fieldName": "valuation_date",
                    "fieldType": "date",
                    "label": "Valuation Date",
                    "required": True,
                    "sortOrder": 2,
                    "validation": {
                        "futureDate": False
                    }
                },
                {
                    "fieldName": "inspection_date",
                    "fieldType": "date",
                    "label": "Inspection Date",
                    "required": True,
                    "sortOrder": 3,
                    "validation": {
                        "futureDate": False
                    }
                },
                {
                    "fieldName": "applicant_name",
                    "fieldType": "text",
                    "label": "Applicant Name",
                    "required": True,
                    "sortOrder": 4,
                    "validation": {
                        "minLength": 2,
                        "maxLength": 100,
                        "pattern": "^[a-zA-Z\\s.]+$"
                    }
                },
                {
                    "fieldName": "valuation_purpose",
                    "fieldType": "dropdown",
                    "label": "Valuation Purpose",
                    "required": True,
                    "sortOrder": 5,
                    "options": [
                        {"value": "home_loan", "label": "Home Loan"},
                        {"value": "mortgage_loan", "label": "Mortgage Loan"},
                        {"value": "property_assessment", "label": "Property Assessment"},
                        {"value": "insurance", "label": "Insurance"},
                        {"value": "legal_matters", "label": "Legal Matters"},
                        {"value": "other", "label": "Other"}
                    ]
                },
                {
                    "fieldName": "bank_branch",
                    "fieldType": "cascading_dropdown",
                    "label": "Bank Branch",
                    "required": True,
                    "sortOrder": 6,
                    "dataSourceConfig": {
                        "collection": "banks",
                        "documentId": "all_banks_unified_v3",
                        "bankPath": "banks",
                        "branchPath": "banks.$.bankBranches", 
                        "bankField": "bankName",
                        "branchField": "branchName",
                        "cascadeMapping": {
                            "parent": "bank",
                            "child": "branch"
                        }
                    },
                    "validation": {
                        "required": True
                    }
                }
            ],
            "isActive": True,
            "createdAt": datetime.now(timezone.utc),
            "createdBy": "system_bank_branch_fix",
            "version": 2,
            "description": "Common form fields with corrected bank branch configuration referencing unified banks document"
        }
        
        print("Creating new common_form_fields document...")
        
        # First, clean up any existing inactive documents
        collection = db_manager.get_collection("admin", "common_form_fields")
        await collection.delete_many({"isActive": False})
        print("✓ Cleaned up inactive documents")
        
        # Insert new document directly using collection
        result = await collection.insert_one(common_fields_document)
        
        if result.inserted_id:
            print("✓ Successfully created common_form_fields document")
            
            # Verify the creation
            verification = await db_manager.find_one(
                "admin",
                "common_form_fields",
                {"_id": "common_fields"}
            )
            
            if verification:
                print("✓ Verification successful")
                print(f"  - Document ID: {verification['_id']}")
                print(f"  - Number of fields: {len(verification['fields'])}")
                print(f"  - Version: {verification.get('version', 'N/A')}")
                print(f"  - Active: {verification.get('isActive', False)}")
                
                # Check bank_branch field specifically
                bank_branch_field = next(
                    (field for field in verification['fields'] if field['fieldName'] == 'bank_branch'),
                    None
                )
                
                if bank_branch_field:
                    print("✓ Bank branch field configuration:")
                    config = bank_branch_field.get('dataSourceConfig', {})
                    print(f"  - Collection: {config.get('collection')}")
                    print(f"  - Document ID: {config.get('documentId')}")
                    print(f"  - Bank Path: {config.get('bankPath')}")
                    print(f"  - Branch Path: {config.get('branchPath')}")
                    print(f"  - Bank Field: {config.get('bankField')}")
                    print(f"  - Branch Field: {config.get('branchField')}")
                else:
                    print("⚠ Bank branch field not found!")
                    
            else:
                print("❌ Verification failed - document not found after creation")
                return False
        else:
            print("❌ Failed to create common_form_fields document")
            return False
            
    except Exception as e:
        print(f"❌ Error during creation: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await db_manager.disconnect()
        print("✓ Database connection closed")
    
    print("\n🎉 Common form fields creation completed successfully!")
    print("Bank branch field now references the unified banks document structure:")
    print("  - Collection: banks")
    print("  - Document: all_banks_unified_v3")
    print("  - Bank Path: banks")
    print("  - Branch Path: banks.$.bankBranches")
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)