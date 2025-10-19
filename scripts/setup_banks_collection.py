#!/usr/bin/env python3
"""
MongoDB Banks Collection Setup Script
Creates and populates the banks collection with sample data
"""

import os
import sys
import ssl
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
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

def create_banks_data():
    """Create sample banks data"""
    current_time = datetime.utcnow()
    
    banks_data = [
        {
            "bankCode": "SBI",
            "bankName": "State Bank of India",
            "bankShortName": "SBI",
            "bankType": "public_sector",
            "isActive": True,
            "headquarters": {
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400001"
            },
            "branches": [
                {
                    "branchId": "SBI_DEL_CP_001",
                    "branchName": "Connaught Place",
                    "branchCode": "SBIN0000001",
                    "ifscCode": "SBIN0000001",
                    "micrCode": "110002001",
                    "address": {
                        "street": "Janpath Road, Connaught Place",
                        "area": "Central Delhi",
                        "city": "New Delhi",
                        "district": "Central Delhi",
                        "state": "Delhi",
                        "pincode": "110001",
                        "landmark": "Near Palika Bazaar"
                    },
                    "contact": {
                        "phone": "+91-11-23417930",
                        "email": "sbi.cp.delhi@sbi.co.in",
                        "managerName": "Rajesh Kumar",
                        "managerContact": "+91-9876543210"
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
                },
                {
                    "branchId": "SBI_MUM_BKC_002",
                    "branchName": "Bandra Kurla Complex",
                    "branchCode": "SBIN0000002",
                    "ifscCode": "SBIN0000002",
                    "micrCode": "400211002",
                    "address": {
                        "street": "G Block, Bandra Kurla Complex",
                        "area": "Bandra East",
                        "city": "Mumbai",
                        "district": "Mumbai Suburban",
                        "state": "Maharashtra",
                        "pincode": "400051",
                        "landmark": "Near SEBI Building"
                    },
                    "contact": {
                        "phone": "+91-22-26542100",
                        "email": "sbi.bkc.mumbai@sbi.co.in",
                        "managerName": "Priya Sharma",
                        "managerContact": "+91-9876543211"
                    },
                    "coordinates": {
                        "latitude": 19.0596,
                        "longitude": 72.8656
                    },
                    "services": ["home_loans", "personal_loans", "business_loans", "deposits", "forex"],
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
                    "branchId": "SBI_BLR_MGB_003",
                    "branchName": "MG Road",
                    "branchCode": "SBIN0000003",
                    "ifscCode": "SBIN0000003",
                    "micrCode": "560002003",
                    "address": {
                        "street": "144, Mahatma Gandhi Road",
                        "area": "Brigade Road",
                        "city": "Bangalore",
                        "district": "Bangalore Urban",
                        "state": "Karnataka",
                        "pincode": "560001",
                        "landmark": "Near Trinity Metro Station"
                    },
                    "contact": {
                        "phone": "+91-80-25584567",
                        "email": "sbi.mgroad.bangalore@sbi.co.in",
                        "managerName": "Suresh Reddy",
                        "managerContact": "+91-9876543212"
                    },
                    "coordinates": {
                        "latitude": 12.9716,
                        "longitude": 77.5946
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
            "totalBranches": 3,
            "createdAt": current_time,
            "updatedAt": current_time
        },
        {
            "bankCode": "PNB",
            "bankName": "Punjab National Bank",
            "bankShortName": "PNB",
            "bankType": "public_sector",
            "isActive": True,
            "headquarters": {
                "city": "New Delhi",
                "state": "Delhi",
                "pincode": "110001"
            },
            "branches": [
                {
                    "branchId": "PNB_DEL_KP_001",
                    "branchName": "Karol Bagh",
                    "branchCode": "PUNB0000001",
                    "ifscCode": "PUNB0000001",
                    "micrCode": "110024001",
                    "address": {
                        "street": "Main Karol Bagh Market",
                        "area": "Karol Bagh",
                        "city": "New Delhi",
                        "district": "Central Delhi",
                        "state": "Delhi",
                        "pincode": "110005",
                        "landmark": "Near Karol Bagh Metro Station"
                    },
                    "contact": {
                        "phone": "+91-11-25753421",
                        "email": "pnb.karolbagh.delhi@pnb.co.in",
                        "managerName": "Amit Singh",
                        "managerContact": "+91-9876543213"
                    },
                    "coordinates": {
                        "latitude": 28.6519,
                        "longitude": 77.1909
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
                    "branchId": "PNB_CHD_SC_002",
                    "branchName": "Sector 17",
                    "branchCode": "PUNB0000002",
                    "ifscCode": "PUNB0000002",
                    "micrCode": "160017002",
                    "address": {
                        "street": "SCO 125-126, Sector 17-C",
                        "area": "Sector 17",
                        "city": "Chandigarh",
                        "district": "Chandigarh",
                        "state": "Chandigarh",
                        "pincode": "160017",
                        "landmark": "Near Neelam Theatre"
                    },
                    "contact": {
                        "phone": "+91-172-2702345",
                        "email": "pnb.sector17.chandigarh@pnb.co.in",
                        "managerName": "Gurpreet Kaur",
                        "managerContact": "+91-9876543214"
                    },
                    "coordinates": {
                        "latitude": 30.7333,
                        "longitude": 76.7794
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
        },
        {
            "bankCode": "HDFC",
            "bankName": "HDFC Bank Limited",
            "bankShortName": "HDFC Bank",
            "bankType": "private_sector",
            "isActive": True,
            "headquarters": {
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400020"
            },
            "branches": [
                {
                    "branchId": "HDFC_MUM_BND_001",
                    "branchName": "Bandra West",
                    "branchCode": "HDFC0000001",
                    "ifscCode": "HDFC0000001",
                    "micrCode": "400211050",
                    "address": {
                        "street": "Turner Road, Bandra West",
                        "area": "Bandra West",
                        "city": "Mumbai",
                        "district": "Mumbai Suburban",
                        "state": "Maharashtra",
                        "pincode": "400050",
                        "landmark": "Near Bandra Railway Station"
                    },
                    "contact": {
                        "phone": "+91-22-26420000",
                        "email": "hdfc.bandra.mumbai@hdfcbank.com",
                        "managerName": "Kavita Patel",
                        "managerContact": "+91-9876543215"
                    },
                    "coordinates": {
                        "latitude": 19.0544,
                        "longitude": 72.8406
                    },
                    "services": ["home_loans", "personal_loans", "business_loans", "deposits", "forex", "nri_services"],
                    "workingHours": {
                        "weekdays": "9:30 AM - 6:00 PM",
                        "saturday": "9:30 AM - 4:00 PM",
                        "sunday": "Closed"
                    },
                    "isActive": True,
                    "createdAt": current_time,
                    "updatedAt": current_time
                },
                {
                    "branchId": "HDFC_GUR_CYB_002",
                    "branchName": "Cyber City",
                    "branchCode": "HDFC0000002",
                    "ifscCode": "HDFC0000002",
                    "micrCode": "122002050",
                    "address": {
                        "street": "DLF Cyber City, Phase 2",
                        "area": "DLF Phase 2",
                        "city": "Gurugram",
                        "district": "Gurugram",
                        "state": "Haryana",
                        "pincode": "122002",
                        "landmark": "Near Cyber Hub"
                    },
                    "contact": {
                        "phone": "+91-124-4567890",
                        "email": "hdfc.cybercity.gurgaon@hdfcbank.com",
                        "managerName": "Rohit Agarwal",
                        "managerContact": "+91-9876543216"
                    },
                    "coordinates": {
                        "latitude": 28.4595,
                        "longitude": 77.0266
                    },
                    "services": ["home_loans", "personal_loans", "business_loans", "deposits", "forex"],
                    "workingHours": {
                        "weekdays": "9:30 AM - 6:00 PM",
                        "saturday": "9:30 AM - 4:00 PM",
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
        },
        {
            "bankCode": "ICICI",
            "bankName": "ICICI Bank Limited",
            "bankShortName": "ICICI Bank",
            "bankType": "private_sector",
            "isActive": True,
            "headquarters": {
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400051"
            },
            "branches": [
                {
                    "branchId": "ICICI_BLR_KOR_001",
                    "branchName": "Koramangala",
                    "branchCode": "ICIC0000001",
                    "ifscCode": "ICIC0000001",
                    "micrCode": "560034020",
                    "address": {
                        "street": "80 Feet Road, 6th Block, Koramangala",
                        "area": "Koramangala",
                        "city": "Bangalore",
                        "district": "Bangalore Urban",
                        "state": "Karnataka",
                        "pincode": "560095",
                        "landmark": "Near Forum Mall"
                    },
                    "contact": {
                        "phone": "+91-80-25530000",
                        "email": "icici.koramangala.bangalore@icicibank.com",
                        "managerName": "Meera Krishnan",
                        "managerContact": "+91-9876543217"
                    },
                    "coordinates": {
                        "latitude": 12.9352,
                        "longitude": 77.6245
                    },
                    "services": ["home_loans", "personal_loans", "business_loans", "deposits", "investment_services"],
                    "workingHours": {
                        "weekdays": "9:30 AM - 6:00 PM",
                        "saturday": "9:30 AM - 4:00 PM",
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
    ]
    
    return banks_data

def setup_banks_collection():
    """Setup banks collection with sample data"""
    print("🚀 Setting up Banks Collection...")
    
    # Get database connection
    db = get_mongodb_connection()
    if db is None:
        return False
    
    try:
        # Get banks collection
        banks_collection = db['banks']
        
        # Create unique index on bankCode
        banks_collection.create_index("bankCode", unique=True)
        banks_collection.create_index("branches.branchId", unique=True)
        banks_collection.create_index("branches.ifscCode", unique=True)
        print("✅ Created indexes for banks collection")
        
        # Get banks data
        banks_data = create_banks_data()
        
        # Insert banks data
        inserted_count = 0
        for bank in banks_data:
            try:
                result = banks_collection.insert_one(bank)
                if result.inserted_id:
                    inserted_count += 1
                    print(f"✅ Inserted bank: {bank['bankName']} ({bank['totalBranches']} branches)")
            except DuplicateKeyError:
                print(f"⚠️  Bank {bank['bankName']} already exists, skipping...")
                continue
        
        print(f"\n🎉 Banks Collection Setup Complete!")
        print(f"📊 Total banks inserted: {inserted_count}")
        
        # Verify the data
        total_banks = banks_collection.count_documents({})
        total_branches = banks_collection.aggregate([
            {"$unwind": "$branches"},
            {"$count": "total"}
        ])
        branch_count = list(total_branches)
        branch_count = branch_count[0]['total'] if branch_count else 0
        
        print(f"📈 Verification:")
        print(f"   - Total banks in collection: {total_banks}")
        print(f"   - Total branches across all banks: {branch_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up banks collection: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🏦 MongoDB Banks Collection Setup")
    print("=" * 60)
    
    success = setup_banks_collection()
    
    if success:
        print("\n✅ All done! Banks collection is ready for use.")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)