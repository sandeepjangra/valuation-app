#!/usr/bin/env python3
"""
Add Missing Banks with Templates to valuation_admin database
"""

import os
import sys
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
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

def add_missing_banks_with_templates():
    """Add missing banks with templates to valuation_admin database"""
    client = get_mongodb_connection()
    if client is None:
        return False
    
    try:
        db = client['valuation_admin']
        banks_collection = db['banks']
        current_time = datetime.utcnow()
        
        missing_banks = [
            {
                "bankCode": "BOB",
                "bankName": "Bank of Baroda",
                "bankShortName": "BOB",
                "bankType": "public_sector",
                "isActive": True,
                "headquarters": {
                    "city": "Vadodara",
                    "state": "Gujarat",
                    "pincode": "390001"
                },
                "branches": [
                    {
                        "branchId": "BOB_MUM_OP_001",
                        "branchName": "Opera House",
                        "branchCode": "BARB0000001",
                        "ifscCode": "BARB0000001",
                        "micrCode": "400023001",
                        "address": {
                            "street": "Veer Nariman Road, Churchgate",
                            "area": "Churchgate",
                            "city": "Mumbai",
                            "district": "Mumbai City",
                            "state": "Maharashtra",
                            "pincode": "400020",
                            "landmark": "Near Opera House"
                        },
                        "contact": {
                            "phone": "+91-22-22820000",
                            "email": "bob.operahouse.mumbai@bankofbaroda.com",
                            "managerName": "Pradeep Singh",
                            "managerContact": "+91-9876543230"
                        },
                        "coordinates": {
                            "latitude": 18.9250,
                            "longitude": 72.8250
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
                "templates": [
                    {
                        "templateId": "BOB_STANDARD_001",
                        "templateCode": "standard",
                        "templateName": "Standard Property Valuation",
                        "templateType": "property_valuation",
                        "propertyType": "all",
                        "description": "Standard template for all property types as per Bank of Baroda guidelines",
                        "version": "1.0",
                        "isActive": True,
                        "fields": [
                            "property_description", "location_details", "property_area",
                            "construction_quality", "legal_documents", "market_comparison",
                            "valuation_approach", "final_valuation"
                        ],
                        "validationRules": {
                            "required_fields": ["property_description", "property_area", "legal_documents"],
                            "minimum_documents": 3
                        },
                        "allowCustomFields": True,
                        "maxCustomFields": 8,
                        "createdAt": current_time,
                        "updatedAt": current_time
                    }
                ],
                "templatesLastUpdated": current_time,
                "templatesVersion": "1.0",
                "createdAt": current_time,
                "updatedAt": current_time
            },
            {
                "bankCode": "UCO",
                "bankName": "UCO Bank",
                "bankShortName": "UCO Bank",
                "bankType": "public_sector", 
                "isActive": True,
                "headquarters": {
                    "city": "Kolkata",
                    "state": "West Bengal",
                    "pincode": "700001"
                },
                "branches": [
                    {
                        "branchId": "UCO_KOL_BBD_001",
                        "branchName": "BBD Bagh",
                        "branchCode": "UCBA0000001",
                        "ifscCode": "UCBA0000001",
                        "micrCode": "700001001",
                        "address": {
                            "street": "10, BBD Bagh East",
                            "area": "BBD Bagh",
                            "city": "Kolkata",
                            "district": "Kolkata",
                            "state": "West Bengal",
                            "pincode": "700001",
                            "landmark": "Near GPO"
                        },
                        "contact": {
                            "phone": "+91-33-22306000",
                            "email": "uco.bbdbagh.kolkata@ucobank.com",
                            "managerName": "Subrata Roy",
                            "managerContact": "+91-9876543240"
                        },
                        "coordinates": {
                            "latitude": 22.5744,
                            "longitude": 88.3629
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
                "templates": [
                    {
                        "templateId": "UCO_STANDARD_001",
                        "templateCode": "standard",
                        "templateName": "Standard Property Valuation",
                        "templateType": "property_valuation", 
                        "propertyType": "all",
                        "description": "Standard template for all property types as per UCO Bank guidelines",
                        "version": "1.0",
                        "isActive": True,
                        "fields": [
                            "property_description", "location_details", "property_dimensions",
                            "structural_details", "legal_compliance", "market_evaluation",
                            "valuation_methodology", "final_assessment"
                        ],
                        "validationRules": {
                            "required_fields": ["property_description", "property_dimensions", "legal_compliance"],
                            "minimum_documents": 3
                        },
                        "allowCustomFields": True,
                        "maxCustomFields": 12,
                        "createdAt": current_time,
                        "updatedAt": current_time
                    }
                ],
                "templatesLastUpdated": current_time,
                "templatesVersion": "1.0",
                "createdAt": current_time,
                "updatedAt": current_time
            },
            {
                "bankCode": "CBI",
                "bankName": "Central Bank of India",
                "bankShortName": "Central Bank",
                "bankType": "public_sector",
                "isActive": True,
                "headquarters": {
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "pincode": "400001"
                },
                "branches": [
                    {
                        "branchId": "CBI_MUM_NC_001",
                        "branchName": "Nariman Point",
                        "branchCode": "CBIN0000001",
                        "ifscCode": "CBIN0000001",
                        "micrCode": "400021001",
                        "address": {
                            "street": "Mittal Court, Nariman Point",
                            "area": "Nariman Point",
                            "city": "Mumbai",
                            "district": "Mumbai City",
                            "state": "Maharashtra",
                            "pincode": "400021",
                            "landmark": "Near Air India Building"
                        },
                        "contact": {
                            "phone": "+91-22-22883000",
                            "email": "cbi.narimanpoint.mumbai@centralbank.co.in",
                            "managerName": "Rajesh Patil",
                            "managerContact": "+91-9876543250"
                        },
                        "coordinates": {
                            "latitude": 18.9267,
                            "longitude": 72.8230
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
                "templates": [
                    {
                        "templateId": "CBI_STANDARD_001",
                        "templateCode": "standard",
                        "templateName": "Standard Property Valuation",
                        "templateType": "property_valuation",
                        "propertyType": "all", 
                        "description": "Standard template for all property types as per Central Bank of India guidelines",
                        "version": "1.0",
                        "isActive": True,
                        "fields": [
                            "property_details", "geographical_location", "area_measurements",
                            "construction_specifications", "documentation", "comparative_analysis",
                            "valuation_process", "concluded_value"
                        ],
                        "validationRules": {
                            "required_fields": ["property_details", "area_measurements", "documentation"],
                            "minimum_documents": 3
                        },
                        "allowCustomFields": True,
                        "maxCustomFields": 15,
                        "createdAt": current_time,
                        "updatedAt": current_time
                    }
                ],
                "templatesLastUpdated": current_time,
                "templatesVersion": "1.0",
                "createdAt": current_time,
                "updatedAt": current_time
            }
        ]
        
        added_banks = 0
        for bank_data in missing_banks:
            # Check if bank already exists
            existing_bank = banks_collection.find_one({"bankCode": bank_data["bankCode"]})
            if existing_bank:
                print(f"ℹ️  {bank_data['bankName']} already exists in valuation_admin")
                continue
            
            try:
                result = banks_collection.insert_one(bank_data)
                if result.inserted_id:
                    added_banks += 1
                    template_count = len(bank_data["templates"])
                    print(f"✅ Added {bank_data['bankName']} with {template_count} template(s)")
                else:
                    print(f"❌ Failed to add {bank_data['bankName']}")
            except DuplicateKeyError:
                print(f"⚠️  {bank_data['bankName']} already exists (duplicate key)")
            except Exception as e:
                print(f"❌ Error adding {bank_data['bankName']}: {e}")
        
        client.close()
        print(f"\n🎉 Added {added_banks} new banks to valuation_admin")
        return True
        
    except Exception as e:
        print(f"❌ Error adding missing banks: {e}")
        client.close()
        return False

def main():
    """Main function"""
    print("=" * 70)
    print("🏦 Add Missing Banks with Templates to valuation_admin")
    print("=" * 70)
    
    success = add_missing_banks_with_templates()
    
    if success:
        print("\n✅ All done! Missing banks added with templates to valuation_admin.")
        print("\n📝 Note: Run the refresh script to update banks.json file.")
    else:
        print("\n❌ Failed to add missing banks. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()