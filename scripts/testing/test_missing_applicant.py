#!/usr/bin/env python3
"""
Test what happens when applicant_name is not provided in input
"""

import requests

def test_missing_applicant_name():
    """Test creating a report without applicant_name field"""
    
    print("🧪 TESTING MISSING APPLICANT_NAME IN INPUT")
    print("=" * 80)
    
    # Login
    login_data = {"email": "sk.tindwal@gmail.com", "password": "admin123"}
    login_response = requests.post("http://localhost:8000/api/auth/login", json=login_data, timeout=10)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed")
        return
    
    token = login_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print("✅ Login successful")
    
    # Test payload WITHOUT applicant_name (like the problematic report)
    test_payload = {
        "sales_deed": "Sale Deed No. 12670 dated 01.11.2023 in the name of M/S SSK Developers",
        "borrower_name": "Sushila w/o Dilbag Singh and Mohit Bamal",
        "postal_address": "House No. 53A, Guru Nanak Enclave, Test",
        "valuation_date": "2025-12-27",
        "inspection_date": "2025-12-03", 
        "valuation_purpose": "bank_purpose"
        # NOTE: applicant_name is MISSING (just like the problematic report)
    }
    
    create_payload = {
        "bank_code": "SBI",
        "template_id": "land-property", 
        "report_data": test_payload
    }
    
    print(f"\n🔨 Creating report WITHOUT applicant_name...")
    print(f"   ❌ applicant_name field intentionally omitted from input")
    print(f"   📋 Only sending: valuation_date, inspection_date, valuation_purpose")
    
    response = requests.post(
        "http://localhost:8000/api/reports",
        headers=headers,
        json=create_payload,
        timeout=30
    )
    
    if response.status_code == 201:
        result = response.json()
        if result.get("success"):
            report_id = result["data"]["report_id"]
            report_data = result["data"]["report_data"]
            
            print(f"✅ Report created: {report_id}")
            
            # Check common_fields
            common_fields = report_data.get("common_fields", {})
            print(f"\n📋 Resulting common_fields:")
            for field, value in common_fields.items():
                print(f"   {field}: '{value}'")
            
            if "applicant_name" not in common_fields:
                print(f"\n✅ CONFIRMED: applicant_name missing because it wasn't in input!")
                print(f"   🎯 This explains why rpt_cbb21f636c41 has no applicant_name")
                print(f"   🔧 Frontend needs to provide applicant_name field")
            else:
                print(f"\n❌ Unexpected: applicant_name found despite not being in input")
    
    else:
        print(f"❌ Create failed: {response.status_code}")

if __name__ == "__main__":
    test_missing_applicant_name()