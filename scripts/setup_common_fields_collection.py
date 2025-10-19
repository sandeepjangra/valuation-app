#!/usr/bin/env python3
"""
MongoDB Common Fields Collection Setup Script
Creates and populates the common_form_fields collection
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

def create_common_fields_data():
    """Create common form fields data"""
    current_time = datetime.utcnow()
    
    common_fields = [
        # Group 1: Basic Information
        {
            "fieldId": "valuation_date",
            "fieldGroup": "basic_info",
            "technicalName": "valuation_date",
            "uiDisplayName": "Date of Valuation",
            "fieldType": "date",
            "isRequired": True,
            "defaultValue": "today",
            "placeholder": "Select valuation date",
            "helpText": "Date when the property valuation was conducted",
            "validation": {
                "maxDate": "today",
                "minDate": "2020-01-01"
            },
            "gridSize": 6,
            "sortOrder": 1,
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },
        {
            "fieldId": "report_reference_number",
            "fieldGroup": "basic_info",
            "technicalName": "report_reference_number",
            "uiDisplayName": "Report Reference Number",
            "fieldType": "text",
            "isRequired": True,
            "placeholder": "Enter report reference number",
            "helpText": "Unique reference number for this valuation report",
            "validation": {
                "pattern": "^[A-Z]{2,4}[0-9]{4,8}$",
                "maxLength": 20
            },
            "gridSize": 6,
            "sortOrder": 2,
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },
        {
            "fieldId": "valuation_purpose",
            "fieldGroup": "basic_info",
            "technicalName": "valuation_purpose",
            "uiDisplayName": "Purpose of Valuation",
            "fieldType": "select",
            "isRequired": True,
            "options": [
                {"value": "home_loan", "label": "Home Loan"},
                {"value": "mortgage_loan", "label": "Mortgage Loan"},
                {"value": "insurance", "label": "Insurance Purpose"},
                {"value": "legal_settlement", "label": "Legal Settlement"},
                {"value": "sale_purchase", "label": "Sale/Purchase"},
                {"value": "stamp_duty", "label": "Stamp Duty Assessment"},
                {"value": "other", "label": "Other"}
            ],
            "placeholder": "Select valuation purpose",
            "helpText": "Reason for conducting this property valuation",
            "gridSize": 6,
            "sortOrder": 3,
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },
        {
            "fieldId": "inspection_date",
            "fieldGroup": "basic_info",
            "technicalName": "inspection_date",
            "uiDisplayName": "Date of Inspection",
            "fieldType": "date",
            "isRequired": True,
            "placeholder": "Select inspection date",
            "helpText": "Date when the property was physically inspected",
            "validation": {
                "maxDate": "today",
                "minDate": "2020-01-01"
            },
            "gridSize": 6,
            "sortOrder": 4,
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },

        # Group 2: Bank & Branch Details (Dynamic from banks collection)
        {
            "fieldId": "bank_code",
            "fieldGroup": "bank_details",
            "technicalName": "bank_code",
            "uiDisplayName": "Bank Name",
            "fieldType": "select_dynamic",
            "dataSource": "banks_collection",
            "dataSourceConfig": {
                "collection": "banks",
                "valueField": "bankCode",
                "labelField": "bankName",
                "filter": {"isActive": True},
                "sortBy": "bankName"
            },
            "isRequired": True,
            "placeholder": "Select bank name",
            "helpText": "Choose the lending bank/financial institution",
            "gridSize": 12,
            "sortOrder": 1,
            "onChange": "populate_branches",
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },
        {
            "fieldId": "branch_details",
            "fieldGroup": "bank_details",
            "technicalName": "branch_details",
            "uiDisplayName": "Branch Details",
            "fieldType": "select_dynamic",
            "dataSource": "banks_collection",
            "dataSourceConfig": {
                "collection": "banks",
                "nestedPath": "branches",
                "valueField": "branchId",
                "labelField": "branchName",
                "filter": {"bankCode": "{bank_code}", "branches.isActive": True},
                "sortBy": "branches.branchName",
                "dependsOn": "bank_code"
            },
            "isRequired": True,
            "placeholder": "Select branch (choose bank first)",
            "helpText": "Choose the specific bank branch",
            "gridSize": 6,
            "sortOrder": 2,
            "disabled": True,
            "enableWhen": "bank_code",
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },
        {
            "fieldId": "branch_ifsc",
            "fieldGroup": "bank_details",
            "technicalName": "branch_ifsc",
            "uiDisplayName": "IFSC Code",
            "fieldType": "text",
            "isRequired": False,
            "isReadonly": True,
            "autoPopulate": {
                "sourceField": "branch_details",
                "sourcePath": "branches.ifscCode"
            },
            "placeholder": "Auto-filled when branch is selected",
            "helpText": "IFSC code (auto-populated from branch selection)",
            "gridSize": 6,
            "sortOrder": 3,
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },
        {
            "fieldId": "branch_address",
            "fieldGroup": "bank_details",
            "technicalName": "branch_address",
            "uiDisplayName": "Branch Address",
            "fieldType": "textarea",
            "isRequired": False,
            "isReadonly": True,
            "autoPopulate": {
                "sourceField": "branch_details",
                "sourcePath": "branches.address",
                "format": "{street}, {city}, {state} - {pincode}"
            },
            "placeholder": "Auto-filled when branch is selected",
            "helpText": "Branch address (auto-populated from branch selection)",
            "gridSize": 12,
            "sortOrder": 4,
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },

        # Group 3: Valuer Details
        {
            "fieldId": "valuer_name",
            "fieldGroup": "valuer_details",
            "technicalName": "valuer_name",
            "uiDisplayName": "Valuer Name",
            "fieldType": "text",
            "isRequired": True,
            "placeholder": "Enter valuer's full name",
            "helpText": "Full name of the certified valuer conducting the assessment",
            "validation": {
                "minLength": 3,
                "maxLength": 100,
                "pattern": "^[a-zA-Z\\s\\.]+$"
            },
            "gridSize": 6,
            "sortOrder": 1,
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },
        {
            "fieldId": "valuer_registration_number",
            "fieldGroup": "valuer_details",
            "technicalName": "valuer_registration_number",
            "uiDisplayName": "Registration Number",
            "fieldType": "text",
            "isRequired": True,
            "placeholder": "Enter registration number",
            "helpText": "Government-issued valuer registration/license number",
            "validation": {
                "pattern": "^[A-Z0-9]{6,15}$",
                "maxLength": 15
            },
            "gridSize": 6,
            "sortOrder": 2,
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },
        {
            "fieldId": "valuer_contact",
            "fieldGroup": "valuer_details",
            "technicalName": "valuer_contact",
            "uiDisplayName": "Contact Number",
            "fieldType": "tel",
            "isRequired": True,
            "placeholder": "Enter contact number",
            "helpText": "Primary contact number of the valuer",
            "validation": {
                "pattern": "^[+]?[0-9]{10,15}$"
            },
            "gridSize": 6,
            "sortOrder": 3,
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },
        {
            "fieldId": "valuer_email",
            "fieldGroup": "valuer_details",
            "technicalName": "valuer_email",
            "uiDisplayName": "Email Address",
            "fieldType": "email",
            "isRequired": False,
            "placeholder": "Enter email address",
            "helpText": "Professional email address of the valuer",
            "validation": {
                "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
            },
            "gridSize": 6,
            "sortOrder": 4,
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },

        # Group 4: Borrower/Client Details
        {
            "fieldId": "borrower_name",
            "fieldGroup": "borrower_details",
            "technicalName": "borrower_name",
            "uiDisplayName": "Borrower/Applicant Name",
            "fieldType": "text",
            "isRequired": True,
            "placeholder": "Enter borrower's full name",
            "helpText": "Full name of the loan applicant/property owner",
            "validation": {
                "minLength": 3,
                "maxLength": 100,
                "pattern": "^[a-zA-Z\\s\\.]+$"
            },
            "gridSize": 6,
            "sortOrder": 1,
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },
        {
            "fieldId": "borrower_contact",
            "fieldGroup": "borrower_details",
            "technicalName": "borrower_contact",
            "uiDisplayName": "Contact Number",
            "fieldType": "tel",
            "isRequired": True,
            "placeholder": "Enter contact number",
            "helpText": "Primary contact number of the borrower",
            "validation": {
                "pattern": "^[+]?[0-9]{10,15}$"
            },
            "gridSize": 6,
            "sortOrder": 2,
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },
        {
            "fieldId": "borrower_email",
            "fieldGroup": "borrower_details",
            "technicalName": "borrower_email",
            "uiDisplayName": "Email Address",
            "fieldType": "email",
            "isRequired": False,
            "placeholder": "Enter email address",
            "helpText": "Email address of the borrower",
            "validation": {
                "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
            },
            "gridSize": 6,
            "sortOrder": 3,
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },
        {
            "fieldId": "loan_amount_requested",
            "fieldGroup": "borrower_details",
            "technicalName": "loan_amount_requested",
            "uiDisplayName": "Loan Amount Requested",
            "fieldType": "currency",
            "isRequired": True,
            "placeholder": "Enter loan amount",
            "helpText": "Amount of loan being applied for",
            "validation": {
                "min": 100000,
                "max": 100000000
            },
            "gridSize": 6,
            "sortOrder": 4,
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },

        # Group 5: Declaration & Certification
        {
            "fieldId": "valuation_basis",
            "fieldGroup": "declaration",
            "technicalName": "valuation_basis",
            "uiDisplayName": "Basis of Valuation",
            "fieldType": "select",
            "isRequired": True,
            "options": [
                {"value": "market_value", "label": "Market Value"},
                {"value": "forced_sale", "label": "Forced Sale Value"},
                {"value": "insurance_value", "label": "Insurance Value"},
                {"value": "rental_value", "label": "Rental Value"}
            ],
            "placeholder": "Select valuation basis",
            "helpText": "Standard basis used for property valuation",
            "gridSize": 6,
            "sortOrder": 1,
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },
        {
            "fieldId": "valuation_approach",
            "fieldGroup": "declaration",
            "technicalName": "valuation_approach",
            "uiDisplayName": "Valuation Approach",
            "fieldType": "select",
            "isRequired": True,
            "options": [
                {"value": "comparison", "label": "Sales Comparison Approach"},
                {"value": "cost", "label": "Cost Approach"},
                {"value": "income", "label": "Income Approach"},
                {"value": "hybrid", "label": "Hybrid Approach"}
            ],
            "placeholder": "Select valuation approach",
            "helpText": "Primary methodology used for valuation",
            "gridSize": 6,
            "sortOrder": 2,
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },
        {
            "fieldId": "property_inspection_status",
            "fieldGroup": "declaration",
            "technicalName": "property_inspection_status",
            "uiDisplayName": "Property Inspection",
            "fieldType": "select",
            "isRequired": True,
            "options": [
                {"value": "internally_externally", "label": "Internally & Externally Inspected"},
                {"value": "externally_only", "label": "Externally Inspected Only"},
                {"value": "desktop_valuation", "label": "Desktop Valuation"},
                {"value": "drive_by", "label": "Drive-by Inspection"}
            ],
            "placeholder": "Select inspection type",
            "helpText": "Level of property inspection conducted",
            "gridSize": 12,
            "sortOrder": 3,
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },

        # Group 6: Property Location
        {
            "fieldId": "property_address",
            "fieldGroup": "property_location",
            "technicalName": "property_address",
            "uiDisplayName": "Property Address",
            "fieldType": "textarea",
            "isRequired": True,
            "placeholder": "Enter complete property address",
            "helpText": "Full address of the property being valued",
            "validation": {
                "minLength": 10,
                "maxLength": 500
            },
            "gridSize": 12,
            "sortOrder": 1,
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },
        {
            "fieldId": "city",
            "fieldGroup": "property_location",
            "technicalName": "city",
            "uiDisplayName": "City",
            "fieldType": "text",
            "isRequired": True,
            "placeholder": "Enter city name",
            "helpText": "City where the property is located",
            "validation": {
                "minLength": 2,
                "maxLength": 50,
                "pattern": "^[a-zA-Z\\s]+$"
            },
            "gridSize": 4,
            "sortOrder": 2,
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },
        {
            "fieldId": "state",
            "fieldGroup": "property_location",
            "technicalName": "state",
            "uiDisplayName": "State",
            "fieldType": "select",
            "isRequired": True,
            "options": [
                {"value": "AN", "label": "Andaman and Nicobar Islands"},
                {"value": "AP", "label": "Andhra Pradesh"},
                {"value": "AR", "label": "Arunachal Pradesh"},
                {"value": "AS", "label": "Assam"},
                {"value": "BR", "label": "Bihar"},
                {"value": "CH", "label": "Chandigarh"},
                {"value": "CT", "label": "Chhattisgarh"},
                {"value": "DN", "label": "Dadra and Nagar Haveli"},
                {"value": "DD", "label": "Daman and Diu"},
                {"value": "DL", "label": "Delhi"},
                {"value": "GA", "label": "Goa"},
                {"value": "GJ", "label": "Gujarat"},
                {"value": "HR", "label": "Haryana"},
                {"value": "HP", "label": "Himachal Pradesh"},
                {"value": "JK", "label": "Jammu and Kashmir"},
                {"value": "JH", "label": "Jharkhand"},
                {"value": "KA", "label": "Karnataka"},
                {"value": "KL", "label": "Kerala"},
                {"value": "LD", "label": "Lakshadweep"},
                {"value": "MP", "label": "Madhya Pradesh"},
                {"value": "MH", "label": "Maharashtra"},
                {"value": "MN", "label": "Manipur"},
                {"value": "ML", "label": "Meghalaya"},
                {"value": "MZ", "label": "Mizoram"},
                {"value": "NL", "label": "Nagaland"},
                {"value": "OR", "label": "Odisha"},
                {"value": "PY", "label": "Puducherry"},
                {"value": "PB", "label": "Punjab"},
                {"value": "RJ", "label": "Rajasthan"},
                {"value": "SK", "label": "Sikkim"},
                {"value": "TN", "label": "Tamil Nadu"},
                {"value": "TG", "label": "Telangana"},
                {"value": "TR", "label": "Tripura"},
                {"value": "UP", "label": "Uttar Pradesh"},
                {"value": "UT", "label": "Uttarakhand"},
                {"value": "WB", "label": "West Bengal"}
            ],
            "placeholder": "Select state",
            "helpText": "State where the property is located",
            "gridSize": 4,
            "sortOrder": 3,
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },
        {
            "fieldId": "pincode",
            "fieldGroup": "property_location",
            "technicalName": "pincode",
            "uiDisplayName": "PIN Code",
            "fieldType": "text",
            "isRequired": True,
            "placeholder": "Enter PIN code",
            "helpText": "6-digit postal PIN code",
            "validation": {
                "pattern": "^[0-9]{6}$",
                "minLength": 6,
                "maxLength": 6
            },
            "gridSize": 4,
            "sortOrder": 4,
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },

        # Group 7: Property Classification
        {
            "fieldId": "property_type",
            "fieldGroup": "property_classification",
            "technicalName": "property_type",
            "uiDisplayName": "Property Type",
            "fieldType": "select",
            "isRequired": True,
            "options": [
                {"value": "residential", "label": "Residential"},
                {"value": "commercial", "label": "Commercial"},
                {"value": "industrial", "label": "Industrial"},
                {"value": "agricultural", "label": "Agricultural"},
                {"value": "mixed_use", "label": "Mixed Use"}
            ],
            "placeholder": "Select property type",
            "helpText": "Primary classification of the property",
            "gridSize": 6,
            "sortOrder": 1,
            "onChange": "populate_sub_types",
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },
        {
            "fieldId": "property_sub_type",
            "fieldGroup": "property_classification",
            "technicalName": "property_sub_type",
            "uiDisplayName": "Property Sub-Type",
            "fieldType": "select_dependent",
            "dependsOn": "property_type",
            "isRequired": True,
            "options": {
                "residential": [
                    {"value": "apartment", "label": "Apartment/Flat"},
                    {"value": "independent_house", "label": "Independent House"},
                    {"value": "villa", "label": "Villa"},
                    {"value": "row_house", "label": "Row House"},
                    {"value": "studio", "label": "Studio Apartment"}
                ],
                "commercial": [
                    {"value": "office_space", "label": "Office Space"},
                    {"value": "retail_shop", "label": "Retail Shop"},
                    {"value": "warehouse", "label": "Warehouse"},
                    {"value": "showroom", "label": "Showroom"},
                    {"value": "hotel", "label": "Hotel"}
                ]
            },
            "placeholder": "Select sub-type",
            "helpText": "Specific sub-category of the property",
            "gridSize": 6,
            "sortOrder": 2,
            "disabled": True,
            "enableWhen": "property_type",
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },
        {
            "fieldId": "construction_status",
            "fieldGroup": "property_classification",
            "technicalName": "construction_status",
            "uiDisplayName": "Construction Status",
            "fieldType": "select",
            "isRequired": True,
            "options": [
                {"value": "completed", "label": "Completed"},
                {"value": "under_construction", "label": "Under Construction"},
                {"value": "ready_to_move", "label": "Ready to Move"},
                {"value": "proposed", "label": "Proposed/Planned"}
            ],
            "placeholder": "Select construction status",
            "helpText": "Current stage of property construction",
            "gridSize": 6,
            "sortOrder": 3,
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },
        {
            "fieldId": "age_of_property",
            "fieldGroup": "property_classification",
            "technicalName": "age_of_property",
            "uiDisplayName": "Age of Property (Years)",
            "fieldType": "number",
            "isRequired": False,
            "placeholder": "Enter property age",
            "helpText": "Age of the property in years (0 for new construction)",
            "validation": {
                "min": 0,
                "max": 100
            },
            "gridSize": 6,
            "sortOrder": 4,
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },

        # Group 8: Coordinates & Survey Details
        {
            "fieldId": "survey_number",
            "fieldGroup": "coordinates",
            "technicalName": "survey_number",
            "uiDisplayName": "Survey Number",
            "fieldType": "text",
            "isRequired": False,
            "placeholder": "Enter survey number",
            "helpText": "Government survey number or plot number",
            "validation": {
                "maxLength": 50
            },
            "gridSize": 6,
            "sortOrder": 1,
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },
        {
            "fieldId": "sub_division",
            "fieldGroup": "coordinates",
            "technicalName": "sub_division",
            "uiDisplayName": "Sub-Division",
            "fieldType": "text",
            "isRequired": False,
            "placeholder": "Enter sub-division",
            "helpText": "Sub-division or block details",
            "validation": {
                "maxLength": 50
            },
            "gridSize": 6,
            "sortOrder": 2,
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },
        {
            "fieldId": "latitude",
            "fieldGroup": "coordinates",
            "technicalName": "latitude",
            "uiDisplayName": "Latitude",
            "fieldType": "decimal",
            "isRequired": False,
            "placeholder": "Enter latitude",
            "helpText": "GPS latitude coordinates (decimal degrees)",
            "validation": {
                "min": -90,
                "max": 90,
                "step": 0.000001
            },
            "gridSize": 6,
            "sortOrder": 3,
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        },
        {
            "fieldId": "longitude",
            "fieldGroup": "coordinates",
            "technicalName": "longitude",
            "uiDisplayName": "Longitude",
            "fieldType": "decimal",
            "isRequired": False,
            "placeholder": "Enter longitude",
            "helpText": "GPS longitude coordinates (decimal degrees)",
            "validation": {
                "min": -180,
                "max": 180,
                "step": 0.000001
            },
            "gridSize": 6,
            "sortOrder": 4,
            "isActive": True,
            "createdAt": current_time,
            "updatedAt": current_time
        }
    ]
    
    return common_fields

def setup_common_fields_collection():
    """Setup common_form_fields collection with field definitions"""
    print("🚀 Setting up Common Form Fields Collection...")
    
    # Get database connection
    db = get_mongodb_connection()
    if db is None:
        return False
    
    try:
        # Get common fields collection
        fields_collection = db['common_form_fields']
        
        # Create unique index on fieldId
        fields_collection.create_index("fieldId", unique=True)
        fields_collection.create_index([("fieldGroup", 1), ("sortOrder", 1)])
        print("✅ Created indexes for common_form_fields collection")
        
        # Get common fields data
        fields_data = create_common_fields_data()
        
        # Insert fields data
        inserted_count = 0
        for field in fields_data:
            try:
                result = fields_collection.insert_one(field)
                if result.inserted_id:
                    inserted_count += 1
                    print(f"✅ Inserted field: {field['uiDisplayName']} ({field['fieldGroup']})")
            except DuplicateKeyError:
                print(f"⚠️  Field {field['fieldId']} already exists, skipping...")
                continue
        
        print(f"\n🎉 Common Form Fields Collection Setup Complete!")
        print(f"📊 Total fields inserted: {inserted_count}")
        
        # Verify the data by field groups
        field_groups = fields_collection.aggregate([
            {"$group": {
                "_id": "$fieldGroup",
                "count": {"$sum": 1},
                "fields": {"$push": "$uiDisplayName"}
            }},
            {"$sort": {"_id": 1}}
        ])
        
        print(f"\n📈 Field Groups Summary:")
        total_fields = 0
        for group in field_groups:
            total_fields += group['count']
            print(f"   📂 {group['_id']}: {group['count']} fields")
            
        print(f"   📊 Total fields in collection: {total_fields}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up common fields collection: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("📝 MongoDB Common Form Fields Collection Setup")
    print("=" * 60)
    
    success = setup_common_fields_collection()
    
    if success:
        print("\n✅ All done! Common form fields collection is ready for use.")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)