#!/usr/bin/env python3
"""
MongoDB Atlas Setup Script for Valuation Application
This script creates the database structure, indexes, and initial seed data
"""

import os
import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import json
import certifi

# MongoDB Atlas Configuration
MONGODB_URI = "mongodb+srv://app_user:kHxlQqJ1Uc3bmoL6@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster"
DB_NAME = "valuation_app_prod"

class MongoDBSetup:
    def __init__(self):
        self.client = None
        self.db = None
    
    async def connect(self):
        """Connect to MongoDB Atlas"""
        print("🔗 Connecting to MongoDB Atlas...")
        self.client = AsyncIOMotorClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=30000,
            tlsCAFile=certifi.where()
        )
        self.db = self.client[DB_NAME]
        
        # Test connection
        try:
            await self.client.admin.command('ping')
            print("✅ Successfully connected to MongoDB Atlas!")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
        return True
    
    async def create_indexes(self):
        """Create all necessary indexes for optimal performance"""
        print("📊 Creating database indexes...")
        
        # Banks collection indexes
        await self.db.banks.create_index("bankCode", unique=True)
        await self.db.banks.create_index([("bankType", 1), ("isActive", 1)])
        
        # Property Types collection indexes
        await self.db.property_types.create_index("typeCode", unique=True)
        await self.db.property_types.create_index([("category", 1), ("isActive", 1)])
        
        # Templates collection indexes
        await self.db.templates.create_index("templateId", unique=True)
        await self.db.templates.create_index([("bankId", 1), ("propertyTypeId", 1), ("isActive", 1)])
        
        # Users collection indexes
        await self.db.users.create_index("email", unique=True)
        await self.db.users.create_index("userId", unique=True)
        await self.db.users.create_index([("role", 1), ("isActive", 1)])
        
        # Valuation Reports collection indexes
        await self.db.valuation_reports.create_index("reportId", unique=True)
        await self.db.valuation_reports.create_index([("bankId", 1), ("workflow.status", 1)])
        await self.db.valuation_reports.create_index([("workflow.submittedBy", 1), ("createdAt", -1)])
        await self.db.valuation_reports.create_index("borrowerInfo.contact")
        await self.db.valuation_reports.create_index([("createdAt", -1)])
        
        # Report Drafts collection indexes with TTL
        await self.db.report_drafts.create_index([("userId", 1), ("templateId", 1)])
        await self.db.report_drafts.create_index("expiresAt", expireAfterSeconds=0)  # TTL index
        
        # Audit Logs collection indexes
        await self.db.audit_logs.create_index([("userId", 1), ("timestamp", -1)])
        await self.db.audit_logs.create_index([("resourceType", 1), ("resourceId", 1)])
        
        print("✅ All indexes created successfully!")
    
    async def seed_banks_data(self):
        """Insert initial bank data"""
        print("🏦 Seeding banks data...")
        
        banks_data = [
            {
                "_id": ObjectId(),
                "bankCode": "SBI",
                "bankName": "State Bank of India",
                "bankType": "PUBLIC_SECTOR",
                "submissionMode": "HARDCOPY",
                "logo": "https://cdn.example.com/bank-logos/sbi.png",
                "brandColors": {
                    "primary": "#1f4e79",
                    "secondary": "#f5f5f5"
                },
                "contactInfo": {
                    "address": "Corporate Centre, Nariman Point, Mumbai - 400021",
                    "email": "valuations@sbi.co.in",
                    "phone": "+91-22-22740000",
                    "website": "https://sbi.co.in"
                },
                "requiredSignature": "PHYSICAL",
                "templateSettings": {
                    "allowCustomFields": False,
                    "mandatoryPhotos": True,
                    "maxFileSize": "10MB"
                },
                "isActive": True,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            },
            {
                "_id": ObjectId(),
                "bankCode": "PNB",
                "bankName": "Punjab National Bank",
                "bankType": "PUBLIC_SECTOR", 
                "submissionMode": "HARDCOPY",
                "logo": "https://cdn.example.com/bank-logos/pnb.png",
                "brandColors": {
                    "primary": "#ff6600",
                    "secondary": "#ffffff"
                },
                "contactInfo": {
                    "address": "7, Bhikaiji Cama Place, New Delhi - 110066",
                    "email": "valuations@pnb.co.in",
                    "phone": "+91-11-66080666",
                    "website": "https://pnbindia.in"
                },
                "requiredSignature": "PHYSICAL",
                "templateSettings": {
                    "allowCustomFields": False,
                    "mandatoryPhotos": True,
                    "maxFileSize": "15MB"
                },
                "isActive": True,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            },
            {
                "_id": ObjectId(),
                "bankCode": "UCO",
                "bankName": "UCO Bank",
                "bankType": "PUBLIC_SECTOR",
                "submissionMode": "HARDCOPY",
                "logo": "https://cdn.example.com/bank-logos/uco.png",
                "brandColors": {
                    "primary": "#2e7d32",
                    "secondary": "#f1f8e9"
                },
                "contactInfo": {
                    "address": "10, B.T.M. Sarani, Kolkata - 700001",
                    "email": "valuations@ucobank.com",
                    "phone": "+91-33-22306154",
                    "website": "https://ucobank.com"
                },
                "requiredSignature": "PHYSICAL",
                "templateSettings": {
                    "allowCustomFields": True,
                    "mandatoryPhotos": True,
                    "maxFileSize": "8MB"
                },
                "isActive": True,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            },
            {
                "_id": ObjectId(),
                "bankCode": "HDFC",
                "bankName": "HDFC Bank Limited",
                "bankType": "PRIVATE_SECTOR",
                "submissionMode": "DIGITAL",  # Private banks prefer digital
                "logo": "https://cdn.example.com/bank-logos/hdfc.png",
                "brandColors": {
                    "primary": "#004c8c",
                    "secondary": "#ffd200"
                },
                "contactInfo": {
                    "address": "HDFC Bank House, Senapati Bapat Marg, Mumbai - 400013",
                    "email": "valuations@hdfcbank.com",
                    "phone": "+91-22-67526000",
                    "website": "https://hdfcbank.com"
                },
                "requiredSignature": "DIGITAL",
                "templateSettings": {
                    "allowCustomFields": True,
                    "mandatoryPhotos": True,
                    "maxFileSize": "20MB"
                },
                "isActive": True,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
        ]
        
        # Insert banks data
        result = await self.db.banks.insert_many(banks_data)
        print(f"✅ Inserted {len(result.inserted_ids)} banks")
        return {bank["bankCode"]: bank["_id"] for bank in banks_data}
    
    async def seed_property_types_data(self):
        """Insert initial property types data"""
        print("🏠 Seeding property types data...")
        
        property_types_data = [
            {
                "_id": ObjectId(),
                "typeCode": "RESIDENTIAL_FLAT",
                "typeName": "Residential Flat/Apartment",
                "category": "RESIDENTIAL",
                "subCategory": "APARTMENT",
                "description": "Individual residential units in multi-story buildings",
                "applicableBanks": ["SBI", "PNB", "UCO", "HDFC"],
                "defaultValuationMethods": ["MARKET_COMPARISON", "COST_APPROACH"],
                "isActive": True,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            },
            {
                "_id": ObjectId(),
                "typeCode": "INDEPENDENT_HOUSE",
                "typeName": "Independent House/Villa",
                "category": "RESIDENTIAL",
                "subCategory": "INDEPENDENT",
                "description": "Stand-alone residential properties with land",
                "applicableBanks": ["SBI", "PNB", "UCO", "HDFC"],
                "defaultValuationMethods": ["MARKET_COMPARISON", "COST_APPROACH", "LAND_RESIDUAL"],
                "isActive": True,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            },
            {
                "_id": ObjectId(),
                "typeCode": "COMMERCIAL_OFFICE",
                "typeName": "Commercial Office Space",
                "category": "COMMERCIAL",
                "subCategory": "OFFICE",
                "description": "Office spaces in commercial buildings",
                "applicableBanks": ["SBI", "PNB", "UCO", "HDFC"],
                "defaultValuationMethods": ["INCOME_APPROACH", "MARKET_COMPARISON"],
                "isActive": True,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            },
            {
                "_id": ObjectId(),
                "typeCode": "RESIDENTIAL_PLOT",
                "typeName": "Residential Plot/Land",
                "category": "LAND",
                "subCategory": "RESIDENTIAL",
                "description": "Vacant land for residential development",
                "applicableBanks": ["SBI", "PNB", "UCO", "HDFC"],
                "defaultValuationMethods": ["MARKET_COMPARISON", "DEVELOPMENT_APPROACH"],
                "isActive": True,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
        ]
        
        result = await self.db.property_types.insert_many(property_types_data)
        print(f"✅ Inserted {len(result.inserted_ids)} property types")
        return {prop_type["typeCode"]: prop_type["_id"] for prop_type in property_types_data}
    
    async def seed_admin_user(self):
        """Create initial admin user"""
        print("👤 Creating admin user...")
        
        admin_user = {
            "_id": ObjectId(),
            "userId": "ADMIN001",
            "email": "admin@valuationapp.com",
            "password": "$2b$12$LQv3c1yqBwcVsvDxjl.Mlu.dLF8MCpI9O.6SPaA0J45UyY8VX1XB2", # password: admin123
            "profile": {
                "firstName": "System",
                "lastName": "Administrator",
                "displayName": "Admin User",
                "phone": "+91-9999999999",
                "avatar": None
            },
            "role": "ADMIN",
            "permissions": {
                "canCreateReports": True,
                "canApproveReports": True,
                "canManageUsers": True,
                "canViewAllReports": True,
                "assignedBanks": ["SBI", "PNB", "UCO", "HDFC"]
            },
            "valuationLicense": {
                "licenseNumber": "ADMIN/SYSTEM/2025",
                "issuedBy": "System Generated",
                "validFrom": datetime.utcnow(),
                "validUntil": datetime.utcnow() + timedelta(days=3650), # 10 years
                "isActive": True
            },
            "managerId": None,
            "lastLogin": None,
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        result = await self.db.users.insert_one(admin_user)
        print(f"✅ Created admin user with ID: {result.inserted_id}")
        return result.inserted_id
    
    async def create_sample_template(self, bank_ids, property_type_ids):
        """Create a sample template for SBI Residential Flat"""
        print("📝 Creating sample template...")
        
        sbi_flat_template = {
            "_id": ObjectId(),
            "templateId": "SBI_RES_FLAT_V2025",
            "bankId": bank_ids["SBI"],
            "propertyTypeId": property_type_ids["RESIDENTIAL_FLAT"],
            "templateName": "SBI Residential Flat Valuation Form",
            "version": "2.0",
            "effectiveDate": datetime.utcnow(),
            "tabs": [
                {
                    "tabId": "borrower_details",
                    "tabName": "Borrower Information",
                    "displayName": "Borrower Details",
                    "order": 1,
                    "icon": "person",
                    "description": "Basic information about the loan applicant",
                    "fields": [
                        {
                            "fieldId": "borrower_name",
                            "internalName": "borrower_name",
                            "displayName": "Borrower Full Name",
                            "fieldType": "TEXT",
                            "dataType": "string",
                            "isRequired": True,
                            "minLength": 2,
                            "maxLength": 100,
                            "placeholder": "Enter borrower's full name as per documents",
                            "validationRules": ["REQUIRED", "ALPHA_SPACES_ONLY"],
                            "helpText": "Name should match with loan application",
                            "order": 1,
                            "gridSize": "col-md-6"
                        },
                        {
                            "fieldId": "borrower_contact",
                            "internalName": "borrower_contact",
                            "displayName": "Contact Number",
                            "fieldType": "PHONE",
                            "dataType": "string",
                            "isRequired": True,
                            "pattern": "^[6-9]\\d{9}$",
                            "placeholder": "10-digit mobile number",
                            "validationRules": ["REQUIRED", "INDIAN_MOBILE"],
                            "order": 2,
                            "gridSize": "col-md-6"
                        },
                        {
                            "fieldId": "loan_amount",
                            "internalName": "loan_amount",
                            "displayName": "Loan Amount (₹)",
                            "fieldType": "CURRENCY",
                            "dataType": "number",
                            "isRequired": True,
                            "minValue": 100000,
                            "maxValue": 100000000,
                            "currency": "INR",
                            "formatters": ["INDIAN_CURRENCY"],
                            "order": 3,
                            "gridSize": "col-md-6"
                        }
                    ]
                },
                {
                    "tabId": "property_details",
                    "tabName": "Property Information",
                    "displayName": "Property Details",
                    "order": 2,
                    "icon": "home",
                    "fields": [
                        {
                            "fieldId": "property_address",
                            "internalName": "property_address",
                            "displayName": "Complete Property Address",
                            "fieldType": "TEXTAREA",
                            "dataType": "string",
                            "isRequired": True,
                            "minLength": 10,
                            "maxLength": 500,
                            "rows": 3,
                            "placeholder": "Enter complete address with landmarks",
                            "validationRules": ["REQUIRED", "MIN_LENGTH:10"],
                            "order": 1,
                            "gridSize": "col-md-12"
                        },
                        {
                            "fieldId": "carpet_area",
                            "internalName": "carpet_area",
                            "displayName": "Carpet Area (sq ft)",
                            "fieldType": "NUMBER",
                            "dataType": "number",
                            "isRequired": True,
                            "minValue": 100,
                            "maxValue": 10000,
                            "decimalPlaces": 2,
                            "suffix": "sq ft",
                            "order": 2,
                            "gridSize": "col-md-4"
                        }
                    ]
                }
            ],
            "formSettings": {
                "allowDraftSave": True,
                "autoSaveInterval": 30,
                "maxDraftDays": 30,
                "requiredApproval": True,
                "approvalLevels": ["MANAGER"]
            },
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        result = await self.db.templates.insert_one(sbi_flat_template)
        print(f"✅ Created sample template with ID: {result.inserted_id}")
        return result.inserted_id
    
    async def setup_database(self):
        """Complete database setup process"""
        print("\n🚀 Starting MongoDB Atlas Database Setup...\n")
        
        # Step 1: Connect to database
        connected = await self.connect()
        if not connected:
            return False
        
        # Step 2: Create indexes
        await self.create_indexes()
        
        # Step 3: Seed initial data
        bank_ids = await self.seed_banks_data()
        property_type_ids = await self.seed_property_types_data()
        admin_user_id = await self.seed_admin_user()
        template_id = await self.create_sample_template(bank_ids, property_type_ids)
        
        print(f"\n✅ Database setup completed successfully!")
        print(f"📊 Summary:")
        print(f"   - Banks: {len(bank_ids)} created")
        print(f"   - Property Types: {len(property_type_ids)} created")
        print(f"   - Admin User ID: {admin_user_id}")
        print(f"   - Sample Template ID: {template_id}")
        print(f"   - Database: {DB_NAME}")
        
        return True
    
    async def close_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            print("🔒 Database connection closed")

async def main():
    """Main setup function"""
    setup = MongoDBSetup()
    
    try:
        success = await setup.setup_database()
        if success:
            print("\n🎉 MongoDB Atlas setup completed successfully!")
            print("\n📋 Next Steps:")
            print("1. Update your .env file with the MongoDB URI")
            print("2. Start building your FastAPI application")
            print("3. Implement user authentication")
            print("4. Create the template engine")
        else:
            print("\n❌ Setup failed. Please check your configuration.")
    except Exception as e:
        print(f"\n💥 Setup error: {e}")
    finally:
        await setup.close_connection()

if __name__ == "__main__":
    asyncio.run(main())