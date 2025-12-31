#!/usr/bin/env python3
"""
Test script to verify Issue 1 and Issue 2 fixes
"""
import os
import sys
import json
import asyncio
from datetime import datetime

# Set environment variables before importing
os.environ.setdefault('MONGODB_URI', 'mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreports.xsnyysn.mongodb.net/')

# Add backend directory to path
sys.path.append('/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend')

from main import transform_flat_to_template_structure

async def test_fixes():
    """Test both Issue 1 (applicant_name) and Issue 2 (bank_branch) fixes"""
    
    print("🧪 Testing Issue 1 & Issue 2 fixes...")
    print("=" * 60)
    
    # Test payload with both applicant_name and bank_branch
    test_payload = {
        "report_id": "test_fixes_123",
        "bank_id": "sbi_bank",
        "applicant_name": "John Doe Test Applicant",  # Issue 1: Should go to common_fields
        "bank_branch": "SBI_BRANCH_12345",            # Issue 2: Should go to common_fields
        "postal_address": "123 Test Street, Test City",
        "property_type": "residential",
        "valuation_date": "2024-01-20"
    }
    
    print(f"📥 Input payload:")
    print(json.dumps(test_payload, indent=2))
    
    # Transform using our fixed function
    result = await transform_flat_to_template_structure(test_payload, "sbi_bank", "sbi_template", None)
    
    print(f"\n📤 Transformation result:")
    print(json.dumps(result, indent=2, default=str))
    
    print(f"\n🔍 Verification:")
    
    # Check Issue 1: applicant_name in common_fields
    applicant_name = result.get("common_fields", {}).get("applicant_name")
    if applicant_name == "John Doe Test Applicant":
        print("✅ Issue 1 FIXED: applicant_name correctly saved to common_fields")
    else:
        print(f"❌ Issue 1 FAIL: applicant_name = {applicant_name}")
    
    # Check Issue 2: bank_branch in common_fields 
    bank_branch = result.get("common_fields", {}).get("bank_branch")
    if bank_branch == "SBI_BRANCH_12345":
        print("✅ Issue 2 FIXED: bank_branch correctly saved to common_fields")
    else:
        print(f"❌ Issue 2 FAIL: bank_branch = {bank_branch}")
    
    # Check that bank_branch is NOT in data section
    data_bank_branch = result.get("data", {}).get("bank_branch")
    if data_bank_branch is None:
        print("✅ Issue 2 CONFIRMED: bank_branch NOT in data section (correct)")
    else:
        print(f"⚠️ Issue 2 WARNING: bank_branch also found in data section = {data_bank_branch}")
    
    print(f"\n📊 Summary:")
    print(f"Common Fields: {list(result.get('common_fields', {}).keys())}")
    print(f"Data Fields: {list(result.get('data', {}).keys())}")
    
    return result

if __name__ == "__main__":
    asyncio.run(test_fixes())