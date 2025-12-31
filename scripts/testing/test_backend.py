#!/usr/bin/env python3
"""
Test script to verify backend endpoints work with new MongoDB collection structure
"""
import asyncio
import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Set environment variable
os.environ['MONGODB_URI'] = "mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster"

async def test_custom_template_endpoints():
    """Test the custom template endpoints"""
    try:
        from database.multi_db_manager import MultiDatabaseManager
        
        print("🔍 Testing MongoDB connection...")
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        # Test 1: Check if valuation_admin database exists
        print("\n📋 Test 1: Checking valuation_admin database...")
        # Access valuation_admin database directly through client
        admin_db = db_manager.client["valuation_admin"]
        collections = await admin_db.list_collection_names()
        print(f"Collections in valuation_admin: {collections}")
        
        # Test 2: Check if bank_custom_template collection exists
        print("\n📋 Test 2: Checking bank_custom_template collection...")
        if "bank_custom_template" in collections:
            template_config = await admin_db.bank_custom_template.find_one({"isActive": True})
            if template_config:
                print("✅ Found active template configuration")
                print(f"Template ID: {template_config.get('templateId')}")
                print(f"Banks count: {len(template_config.get('banks', []))}")
                
                # Test 3: Check banks structure
                print("\n📋 Test 3: Checking banks structure...")
                for bank in template_config.get("banks", []):
                    if bank.get("isActive", True):
                        bank_code = bank.get("bankCode")
                        property_types = list(bank.get("propertyTypes", {}).keys())
                        print(f"  Bank: {bank_code} - Property Types: {property_types}")
                        
                        # Test 4: Check fields for first property type
                        if property_types:
                            first_prop_type = property_types[0]
                            prop_config = bank.get("propertyTypes", {}).get(first_prop_type, {})
                            if prop_config.get("isActive", True):
                                fields = prop_config.get("fields", [])
                                active_fields = [f for f in fields if f.get("isActive", True)]
                                print(f"    {first_prop_type}: {len(active_fields)} active fields")
                                
                                # Show first few fields
                                for i, field in enumerate(active_fields[:3]):
                                    print(f"      Field {i+1}: {field.get('fieldId')} - {field.get('uiDisplayName')}")
            else:
                print("❌ No active template configuration found")
        else:
            print("❌ bank_custom_template collection not found")
        
        # Test 5: Simulate the banks endpoint
        print("\n📋 Test 5: Simulating /api/custom-templates/banks endpoint...")
        if "bank_custom_template" in collections:
            template_config = await admin_db.bank_custom_template.find_one({"isActive": True})
            if template_config:
                bank_list = []
                for bank in template_config.get("banks", []):
                    if bank.get("isActive", True):
                        property_types = []
                        for prop_type, config in bank.get("propertyTypes", {}).items():
                            if config.get("isActive", True):
                                property_types.append(prop_type)
                        
                        bank_list.append({
                            "bankCode": bank["bankCode"],
                            "bankName": bank.get("bankName", bank["bankCode"]),
                            "propertyTypes": property_types
                        })
                
                print(f"✅ Banks endpoint would return {len(bank_list)} banks:")
                for bank in bank_list:
                    print(f"  {bank['bankCode']}: {bank['propertyTypes']}")
        
        # Test 6: Simulate the fields endpoint
        print("\n📋 Test 6: Simulating /api/custom-templates/fields endpoint...")
        if template_config and template_config.get("banks"):
            # Test with SBI and land
            test_bank = "SBI"
            test_property_type = "land"
            
            bank_config = None
            for bank in template_config.get("banks", []):
                if bank.get("bankCode") == test_bank and bank.get("isActive", True):
                    bank_config = bank
                    break
            
            if bank_config:
                property_config = bank_config.get("propertyTypes", {}).get(test_property_type)
                if property_config and property_config.get("isActive", True):
                    active_fields = [field for field in property_config["fields"] if field.get("isActive", True)]
                    print(f"✅ Fields endpoint for {test_bank}/{test_property_type} would return {len(active_fields)} fields:")
                    for field in active_fields[:5]:  # Show first 5
                        print(f"  {field.get('fieldId')}: {field.get('uiDisplayName')} ({field.get('fieldType')})")
                else:
                    print(f"❌ Property type {test_property_type} not found or inactive for {test_bank}")
            else:
                print(f"❌ Bank {test_bank} not found or inactive")
        
        await db_manager.disconnect()
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_custom_template_endpoints())