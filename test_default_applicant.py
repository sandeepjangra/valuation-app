#!/usr/bin/env python3
"""
Test script to verify default applicant_name handling
"""
import os
import sys
import json
import asyncio
from datetime import datetime

# Add the backend directory to Python path
sys.path.append('/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend')

from main import transform_flat_to_template_structure

async def test_missing_applicant_name_gets_default():
    """Test that missing applicant_name gets default value"""
    
    print("🧪 Testing missing applicant_name gets default value...")
    
    # Test payload WITHOUT applicant_name
    test_payload = {
        "report_id": "test_default_123",
        "bank_id": "sbi_bank",
        "postal_address": "123 Default Test Street",
        "property_type": "residential",
        "valuation_date": "2024-01-15"
    }
    
    print(f"📥 Input payload (NO applicant_name): {json.dumps(test_payload, indent=2)}")
    
    # Transform the data (with required parameters)
    result = await transform_flat_to_template_structure(test_payload, "sbi_bank", "sbi_template", None)
    
    print(f"\n📤 Transformation result:")
    print(f"Common fields: {json.dumps(result.get('common_fields', {}), indent=2)}")
    
    # Check if applicant_name got default value
    applicant_name = result.get("common_fields", {}).get("applicant_name")
    
    if applicant_name == "N/A":
        print("✅ SUCCESS: Missing applicant_name got default value 'N/A'")
    else:
        print(f"❌ FAIL: Expected 'N/A', got '{applicant_name}'")
    
    # Check other defaults
    valuation_date = result.get("common_fields", {}).get("valuation_date")
    inspection_date = result.get("common_fields", {}).get("inspection_date") 
    valuation_purpose = result.get("common_fields", {}).get("valuation_purpose")
    
    print(f"\n📋 All common field defaults:")
    print(f"  - applicant_name: {applicant_name}")
    print(f"  - valuation_date: {valuation_date}")
    print(f"  - inspection_date: {inspection_date}")
    print(f"  - valuation_purpose: {valuation_purpose}")
    
    return result

async def test_existing_applicant_name_preserved():
    """Test that existing applicant_name is preserved"""
    
    print("\n🧪 Testing existing applicant_name is preserved...")
    
    # Test payload WITH applicant_name
    test_payload = {
        "report_id": "test_preserve_456",
        "bank_id": "sbi_bank", 
        "applicant_name": "John Doe Original Name",
        "postal_address": "456 Preserve Test Avenue",
        "property_type": "commercial"
    }
    
    print(f"📥 Input payload (WITH applicant_name): {json.dumps(test_payload, indent=2)}")
    
    # Transform the data (with required parameters)
    result = await transform_flat_to_template_structure(test_payload, "sbi_bank", "sbi_template", None)
    
    print(f"\n📤 Transformation result:")
    print(f"Common fields: {json.dumps(result.get('common_fields', {}), indent=2)}")
    
    # Check if applicant_name was preserved
    applicant_name = result.get("common_fields", {}).get("applicant_name")
    
    if applicant_name == "John Doe Original Name":
        print("✅ SUCCESS: Existing applicant_name was preserved")
    else:
        print(f"❌ FAIL: Expected 'John Doe Original Name', got '{applicant_name}'")
    
    return result

async def main():
    print("🔬 Testing default applicant_name handling...")
    print("=" * 60)
    
    # Test 1: Missing applicant_name gets default
    result1 = await test_missing_applicant_name_gets_default()
    
    # Test 2: Existing applicant_name is preserved
    result2 = await test_existing_applicant_name_preserved()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())