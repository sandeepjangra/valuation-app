#!/usr/bin/env python3
"""
MongoDB Banks Templates Update Script
Adds template sections to existing banks in MongoDB
"""

import os
import sys
import ssl
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to Python path to import mongodb_manager
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

def get_mongodb_connection():
    """Get MongoDB connection using Atlas connection string"""
    try:
        # MongoDB Atlas connection string from environment
        connection_string = os.getenv("MONGODB_URI")
        if not connection_string:
            print("❌ MONGODB_URI environment variable not found")
            print("   Please check your .env file")
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
        
        # Use the production database from environment
        db_name = os.getenv("MONGODB_DB_NAME", "valuation_app_prod")
        db = client[db_name]
        return db
        
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
        "SBI": {
            "templates": [
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
            ]
        },
        "UNION": {
            "templates": [
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
            ]
        },
        "PNB": {
            "templates": [
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
        },
        "BOB": {
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
            ]
        },
        "UCO": {
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
            ]
        },
        "CBI": {
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
            ]
        }
    }
    
    return templates_config

def add_union_bank():
    """Add Union Bank of India to the database if it doesn't exist"""
    db = get_mongodb_connection()
    if db is None:
        return False
    
    banks_collection = db['banks']
    current_time = datetime.utcnow()
    
    # Check if Union Bank already exists
    existing_bank = banks_collection.find_one({"bankCode": "UNION"})
    if existing_bank:
        print("ℹ️  Union Bank of India already exists in database")
        return True
    
    # Create Union Bank data
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
            },
            {
                "branchId": "UNION_DEL_CP_002",
                "branchName": "Connaught Place",
                "branchCode": "UBIN0000002",
                "ifscCode": "UBIN0000002",
                "micrCode": "110001002",
                "address": {
                    "street": "E Block, Connaught Place",
                    "area": "Connaught Place",
                    "city": "New Delhi",
                    "district": "Central Delhi",
                    "state": "Delhi",
                    "pincode": "110001",
                    "landmark": "Near Central Park"
                },
                "contact": {
                    "phone": "+91-11-23417800",
                    "email": "union.cp.delhi@unionbankofindia.com", 
                    "managerName": "Deepak Kumar",
                    "managerContact": "+91-9876543221"
                },
                "coordinates": {
                    "latitude": 28.6315,
                    "longitude": 77.2167
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
        "totalBranches": 2,
        "createdAt": current_time,
        "updatedAt": current_time
    }
    
    try:
        result = banks_collection.insert_one(union_bank_data)
        if result.inserted_id:
            print(f"✅ Added Union Bank of India with {union_bank_data['totalBranches']} branches")
            return True
        else:
            print("❌ Failed to add Union Bank of India")
            return False
    except Exception as e:
        print(f"❌ Error adding Union Bank: {e}")
        return False

def add_missing_banks():
    """Add Bank of Baroda, UCO Bank, and Central Bank of India if they don't exist"""
    db = get_mongodb_connection()
    if db is None:
        return False
    
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
            "totalBranches": 1
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
            "totalBranches": 1
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
            "totalBranches": 1
        }
    ]
    
    added_banks = 0
    for bank_data in missing_banks:
        bank_data["createdAt"] = current_time
        bank_data["updatedAt"] = current_time
        
        # Check if bank already exists
        existing_bank = banks_collection.find_one({"bankCode": bank_data["bankCode"]})
        if existing_bank:
            print(f"ℹ️  {bank_data['bankName']} already exists in database")
            continue
        
        try:
            result = banks_collection.insert_one(bank_data)
            if result.inserted_id:
                added_banks += 1
                print(f"✅ Added {bank_data['bankName']} with {bank_data['totalBranches']} branch(es)")
            else:
                print(f"❌ Failed to add {bank_data['bankName']}")
        except Exception as e:
            print(f"❌ Error adding {bank_data['bankName']}: {e}")
    
    return added_banks > 0

def update_banks_with_templates():
    """Update existing banks with templates section"""
    print("🚀 Adding Templates to Bank Documents...")
    
    # Get database connection
    db = get_mongodb_connection()
    if db is None:
        return False
    
    try:
        # Get banks collection
        banks_collection = db['banks']
        templates_config = get_bank_templates_config()
        current_time = datetime.utcnow()
        
        updated_banks = 0
        
        # Update each bank with templates
        for bank_code, config in templates_config.items():
            try:
                # Find the bank by code (handle variations)
                bank_query = {"bankCode": bank_code}
                if bank_code == "UNION":
                    bank_query = {"$or": [{"bankCode": "UNION"}, {"bankCode": "UBI"}]}
                
                existing_bank = banks_collection.find_one(bank_query)
                
                if existing_bank:
                    # Update the bank with templates
                    update_data = {
                        "$set": {
                            "templates": config["templates"],
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
                        template_count = len(config["templates"])
                        print(f"✅ Updated {bank_name} with {template_count} template(s)")
                    else:
                        print(f"⚠️  No changes made to {bank_code}")
                else:
                    print(f"⚠️  Bank {bank_code} not found in database")
                    
            except Exception as e:
                print(f"❌ Error updating bank {bank_code}: {e}")
                continue
        
        print(f"\n🎉 Template Update Complete!")
        print(f"📊 Total banks updated: {updated_banks}")
        
        # Verify the updates
        banks_with_templates = banks_collection.count_documents({"templates": {"$exists": True}})
        print(f"📈 Verification: {banks_with_templates} banks now have templates")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating banks with templates: {e}")
        return False

def main():
    """Main function to execute the template update"""
    print("=" * 70)
    print("🏦 MongoDB Banks Templates Update")
    print("=" * 70)
    
    # Step 1: Add Union Bank if it doesn't exist
    print("\n📋 Step 1: Adding Union Bank of India...")
    add_union_bank()
    
    # Step 2: Add other missing banks
    print("\n📋 Step 2: Adding missing banks (BOB, UCO, CBI)...")
    add_missing_banks()
    
    # Step 3: Update all banks with templates
    print("\n📋 Step 3: Adding templates to all banks...")
    success = update_banks_with_templates()
    
    if success:
        print("\n✅ All done! Banks now have templates configured.")
        print("\n📝 Summary of added templates:")
        print("   • SBI: Land + Apartment templates")
        print("   • Union Bank: Land + Apartment templates") 
        print("   • PNB: Standard template (extensible)")
        print("   • Bank of Baroda: Standard template (extensible)")
        print("   • UCO Bank: Standard template (extensible)")
        print("   • Central Bank: Standard template (extensible)")
    else:
        print("\n❌ Template update failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()