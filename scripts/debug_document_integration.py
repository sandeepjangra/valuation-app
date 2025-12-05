#!/usr/bin/env python3
"""
Debug script to test document types integration manually
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append('/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend')

from database.mongodb import get_database
from services.document_types_integrator import DocumentTypesIntegrator

async def test_document_integration():
    try:
        # Get database connection
        admin_db = await get_database("valuation_admin")
        print("✅ Connected to database")
        
        # Test document types integration
        print("\n🔍 Testing DocumentTypesIntegrator...")
        
        # Test with SBI and land property
        doc_fields = await DocumentTypesIntegrator.get_document_fields(
            admin_db, property_type="land-property", bank_code="SBI"
        )
        
        print(f"📊 Found {len(doc_fields)} document type fields for SBI/land-property:")
        for field in doc_fields[:3]:  # Show first 3
            print(f"   - {field.get('fieldId')}: {field.get('uiDisplayName')}")
            
        # Also test with "Land" property type (in case the issue is property type matching)
        doc_fields2 = await DocumentTypesIntegrator.get_document_fields(
            admin_db, property_type="Land", bank_code="SBI"
        )
        
        print(f"\n📊 Found {len(doc_fields2)} document type fields for SBI/Land:")
        for field in doc_fields2[:3]:  # Show first 3
            print(f"   - {field.get('fieldId')}: {field.get('uiDisplayName')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_document_integration())