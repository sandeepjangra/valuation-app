#!/usr/bin/env python3
"""
Fix Bank Templates - Add templates to correct database (valuation_admin)
"""

import os
import sys
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_mongodb_connection():
    """Get MongoDB connection using Atlas connection string"""
    try:
        connection_string = os.getenv("MONGODB_URI")
        if not connection_string:
            print("❌ MONGODB_URI environment variable not found")
            return None
        
        client = MongoClient(
            connection_string,
            serverSelectionTimeoutMS=5000,
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True
        )
        
        # Test the connection
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas!")
        
        return client
        
    except ConnectionFailure as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def get_bank_templates_config():
    """Define templates configuration for each bank"""
    current_time = datetime.utcnow()
    
    templates_config = {
        "SBI": [
            {
                "templateId": "SBI_LAND_001",
                "templateCode": "land",
                "templateName": "Land Property Valuation",
                "templateType": "property_valuation",
                "propertyType": "land",
                "description": "Template for land property valuation as per SBI guidelines",
                "version": "1.0",
                "isActive": True,
                "fields": [
                    "property_description", "location_details", "land_area", 
                    "boundaries", "legal_documents", "market_analysis", 
                    "valuation_method", "final_valuation"
                ],
                "validationRules": {
                    "required_fields": ["property_description", "land_area", "legal_documents"],
                    "minimum_documents": 3
                },
                "createdAt": current_time,
                "updatedAt": current_time
            },
            {
                "templateId": "SBI_APARTMENT_001",
                "templateCode": "apartment",
                "templateName": "Apartment/Flat Property Valuation",
                "templateType": "property_valuation",
                "propertyType": "apartment",
                "description": "Template for apartment/flat property valuation as per SBI guidelines",
                "version": "1.0",
                "isActive": True,
                "fields": [
                    "property_description", "location_details", "built_area",
                    "carpet_area", "floor_details", "amenities", "legal_documents",
                    "market_comparison", "valuation_method", "final_valuation"
                ],
                "validationRules": {
                    "required_fields": ["property_description", "built_area", "legal_documents"],
                    "minimum_documents": 4
                },
                "createdAt": current_time,
                "updatedAt": current_time
            }
        ],
        "UNION": [
            {
                "templateId": "UNION_LAND_001",
                "templateCode": "land",
                "templateName": "Land Property Valuation",
                "templateType": "property_valuation",
                "propertyType": "land",
                "description": "Template for land property valuation as per Union Bank guidelines",
                "version": "1.0",
                "isActive": True,
                "fields": [
                    "property_description", "location_details", "land_area",
                    "survey_details", "boundaries", "legal_documents",
                    "market_analysis", "valuation_method", "final_valuation"
                ],
                "validationRules": {
                    "required_fields": ["property_description", "land_area", "survey_details"],
                    "minimum_documents": 3
                },
                "createdAt": current_time,
                "updatedAt": current_time
            },
            {
                "templateId": "UNION_APARTMENT_001",
                "templateCode": "apartment",
                "templateName": "Apartment/Flat Property Valuation",
                "templateType": "property_valuation",
                "propertyType": "apartment",
                "description": "Template for apartment/flat property valuation as per Union Bank guidelines",
                "version": "1.0",
                "isActive": True,
                "fields": [
                    "property_description", "location_details", "built_area",
                    "super_area", "floor_details", "parking", "amenities",
                    "legal_documents", "market_comparison", "valuation_method",
                    "final_valuation"
                ],
                "validationRules": {
                    "required_fields": ["property_description", "built_area", "legal_documents"],
                    "minimum_documents": 4
                },
                "createdAt": current_time,
                "updatedAt": current_time
            }
        ],
        "PNB": [
            {
                "templateId": "PNB_STANDARD_001",
                "templateCode": "standard",
                "templateName": "Standard Property Valuation",
                "templateType": "property_valuation",
                "propertyType": "all",
                "description": "Standard template for all property types as per PNB guidelines",
                "version": "1.0",
                "isActive": True,
                "fields": [
                    "property_description", "location_details", "property_area",
                    "construction_details", "legal_documents", "market_analysis",
                    "valuation_method", "final_valuation"
                ],
                "validationRules": {
                    "required_fields": ["property_description", "property_area", "legal_documents"],
                    "minimum_documents": 3
                },
                "allowCustomFields": True,
                "maxCustomFields": 10,
                "createdAt": current_time,
                "updatedAt": current_time
            }
        ]
    }
    
    return templates_config

def add_templates_to_valuation_admin():
    """Add templates to banks in valuation_admin database"""
    print("🚀 Adding Templates to Banks in valuation_admin database...")
    
    client = get_mongodb_connection()
    if client is None:
        return False
    
    try:
        # Use the valuation_admin database where banks collection is located
        db = client['valuation_admin']
        banks_collection = db['banks']
        templates_config = get_bank_templates_config()
        current_time = datetime.utcnow()
        
        updated_banks = 0
        
        # Update each bank with templates
        for bank_code, templates in templates_config.items():
            try:
                # Find the bank by code
                bank_query = {"bankCode": bank_code}
                if bank_code == "UNION":
                    bank_query = {"$or": [{"bankCode": "UNION"}, {"bankCode": "UBI"}]}
                
                existing_bank = banks_collection.find_one(bank_query)
                
                if existing_bank:
                    # Update the bank with templates
                    update_data = {
                        "$set": {
                            "templates": templates,
                            "templatesLastUpdated": current_time,
                            "templatesVersion": "1.0",
                            "updatedAt": current_time
                        }
                    }
                    
                    result = banks_collection.update_one(
                        {"_id": existing_bank["_id"]},
                        update_data
                    )
                    
                    if result.modified_count > 0:
                        updated_banks += 1
                        bank_name = existing_bank.get("bankName", bank_code)
                        template_count = len(templates)
                        print(f"✅ Updated {bank_name} with {template_count} template(s)")
                    else:
                        print(f"⚠️  No changes made to {bank_code}")
                else:
                    print(f"⚠️  Bank {bank_code} not found in valuation_admin database")
                    
            except Exception as e:
                print(f"❌ Error updating bank {bank_code}: {e}")
                continue
        
        print(f"\n🎉 Template Update Complete!")
        print(f"📊 Total banks updated: {updated_banks}")
        
        # Verify the updates
        banks_with_templates = banks_collection.count_documents({"templates": {"$exists": True}})
        print(f"📈 Verification: {banks_with_templates} banks now have templates in valuation_admin")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error updating banks with templates: {e}")
        client.close()
        return False

def add_missing_banks_to_valuation_admin():
    """Add missing banks to valuation_admin database"""
    client = get_mongodb_connection()
    if client is None:
        return False
    
    try:
        db = client['valuation_admin']
        banks_collection = db['banks']
        current_time = datetime.utcnow()
        
        # Check if Union Bank exists
        union_bank = banks_collection.find_one({"bankCode": "UNION"})
        if not union_bank:
            # Add Union Bank
            union_bank_data = {
                "bankCode": "UNION",
                "bankName": "Union Bank of India", 
                "bankShortName": "Union Bank",
                "bankType": "public_sector",
                "isActive": True,
                "headquarters": {
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "pincode": "400001"
                },
                "branches": [
                    {
                        "branchId": "UNION_MUM_FC_001",
                        "branchName": "Fort Circle",
                        "branchCode": "UBIN0000001",
                        "ifscCode": "UBIN0000001",
                        "micrCode": "400026001",
                        "address": {
                            "street": "Dalal Street, Fort",
                            "area": "Fort",
                            "city": "Mumbai",
                            "district": "Mumbai City",
                            "state": "Maharashtra", 
                            "pincode": "400001",
                            "landmark": "Near Bombay Stock Exchange"
                        },
                        "contact": {
                            "phone": "+91-22-22661234",
                            "email": "union.fort.mumbai@unionbankofindia.com",
                            "managerName": "Anil Sharma",
                            "managerContact": "+91-9876543220"
                        },
                        "coordinates": {
                            "latitude": 18.9300,
                            "longitude": 72.8330
                        },
                        "services": ["home_loans", "personal_loans", "business_loans", "deposits"],
                        "workingHours": {
                            "weekdays": "10:00 AM - 4:00 PM",
                            "saturday": "10:00 AM - 2:00 PM", 
                            "sunday": "Closed"
                        },
                        "isActive": True,
                        "createdAt": current_time,
                        "updatedAt": current_time
                    }
                ],
                "totalBranches": 1,
                "createdAt": current_time,
                "updatedAt": current_time
            }
            
            result = banks_collection.insert_one(union_bank_data)
            if result.inserted_id:
                print(f"✅ Added Union Bank of India to valuation_admin")
            else:
                print(f"❌ Failed to add Union Bank of India")
        else:
            print("ℹ️  Union Bank of India already exists in valuation_admin")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error adding missing banks: {e}")
        client.close()
        return False

def main():
    """Main function"""
    print("=" * 70)
    print("🔧 Fix Bank Templates - Add to valuation_admin database")
    print("=" * 70)
    
    # Step 1: Add missing banks to valuation_admin
    print("\n📋 Step 1: Adding missing banks to valuation_admin...")
    add_missing_banks_to_valuation_admin()
    
    # Step 2: Add templates to valuation_admin
    print("\n📋 Step 2: Adding templates to banks in valuation_admin...")
    success = add_templates_to_valuation_admin()
    
    if success:
        print("\n✅ All done! Templates added to valuation_admin database.")
        print("\n📝 Note: Run the refresh script to update banks.json file.")
    else:
        print("\n❌ Template update failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()