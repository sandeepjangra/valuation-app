#!/usr/bin/env python3
"""
Script to create sbi_apartment_property_details collection
Based on sbi_land_property_details but modified for apartment properties
"""

import os
import sys
import json
from datetime import datetime, timezone
from pymongo import MongoClient
from bson import ObjectId

# Load env
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    print('MONGODB_URI not set in environment. Aborting.')
    sys.exit(1)

def create_apartment_property_details():
    """Create apartment property details document"""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "_id": str(ObjectId()),
        "templateId": "SBI_APARTMENT_PROPERTY_DETAILS_V1",
        "templateName": "SBI Apartment Property Details",
        "bankCode": "SBI",
        "propertyType": "Apartment",
        "templateCategory": "property_details",
        "createdAt": now,
        "updatedAt": now,
        "isActive": True,
        "fields": [
            {
                "fieldId": "list_of_documents",
                "uiDisplayName": "List of Documents",
                "fieldType": "multiselect",
                "options": [
                    {"value": "sale_deed", "label": "Sale Deed"},
                    {"value": "occupancy_certificate", "label": "Occupancy Certificate"},
                    {"value": "society_share_certificate", "label": "Society Share Certificate"},
                    {"value": "building_plan_approval", "label": "Building Plan Approval"}
                ],
                "helpText": "Select applicable documents for apartment",
                "isRequired": False,
                "sortOrder": 1
            },
            {
                "fieldId": "postal_address",
                "uiDisplayName": "Property Address",
                "fieldType": "textarea",
                "isRequired": False,
                "placeholder": "Enter complete apartment address",
                "sortOrder": 2
            },
            {
                "fieldId": "property_description",
                "uiDisplayName": "Apartment Description",
                "fieldType": "textarea",
                "isRequired": False,
                "placeholder": "Describe the apartment details",
                "sortOrder": 3
            },
            {
                "fieldId": "apartment_location",
                "uiDisplayName": "Apartment Location Details",
                "fieldType": "group",
                "isRequired": False,
                "sortOrder": 4,
                "subFields": [
                    {"fieldId": "building_name", "uiDisplayName": "Building/Society Name", "fieldType": "text", "sortOrder": 1},
                    {"fieldId": "flat_number", "uiDisplayName": "Flat Number", "fieldType": "text", "sortOrder": 2},
                    {"fieldId": "floor_number", "uiDisplayName": "Floor Number", "fieldType": "number", "sortOrder": 3},
                    {"fieldId": "wing_block", "uiDisplayName": "Wing/Block", "fieldType": "text", "sortOrder": 4},
                    {"fieldId": "society_registration", "uiDisplayName": "Society Registration No.", "fieldType": "text", "sortOrder": 5}
                ]
            },
            {
                "fieldId": "area_type",
                "uiDisplayName": "Area Type",
                "fieldType": "select",
                "options": [
                    {"value": "residential", "label": "Residential"},
                    {"value": "commercial", "label": "Commercial"},
                    {"value": "mixed_use", "label": "Mixed Use"}
                ],
                "isRequired": True,
                "sortOrder": 5
            },
            {
                "fieldId": "apartment_configuration",
                "uiDisplayName": "Apartment Configuration",
                "fieldType": "group",
                "sortOrder": 6,
                "subFields": [
                    {"fieldId": "bedrooms", "uiDisplayName": "Number of Bedrooms", "fieldType": "number", "sortOrder": 1},
                    {"fieldId": "bathrooms", "uiDisplayName": "Number of Bathrooms", "fieldType": "number", "sortOrder": 2},
                    {"fieldId": "living_rooms", "uiDisplayName": "Living Rooms", "fieldType": "number", "sortOrder": 3},
                    {"fieldId": "kitchen_type", "uiDisplayName": "Kitchen Type", "fieldType": "select", "options": [
                        {"value": "modular", "label": "Modular"},
                        {"value": "semi_modular", "label": "Semi-Modular"},
                        {"value": "traditional", "label": "Traditional"}
                    ], "sortOrder": 4}
                ]
            },
            {
                "fieldId": "area_details",
                "uiDisplayName": "Area Details",
                "fieldType": "group",
                "sortOrder": 7,
                "subFields": [
                    {"fieldId": "carpet_area", "uiDisplayName": "Carpet Area (sq ft)", "fieldType": "number", "sortOrder": 1},
                    {"fieldId": "built_up_area", "uiDisplayName": "Built-up Area (sq ft)", "fieldType": "number", "sortOrder": 2},
                    {"fieldId": "super_built_up_area", "uiDisplayName": "Super Built-up Area (sq ft)", "fieldType": "number", "sortOrder": 3},
                    {"fieldId": "balcony_area", "uiDisplayName": "Balcony Area (sq ft)", "fieldType": "number", "sortOrder": 4}
                ]
            },
            {
                "fieldId": "building_amenities",
                "uiDisplayName": "Building Amenities",
                "fieldType": "multiselect",
                "options": [
                    {"value": "elevator", "label": "Elevator/Lift"},
                    {"value": "generator", "label": "Power Backup"},
                    {"value": "security", "label": "24x7 Security"},
                    {"value": "parking", "label": "Car Parking"},
                    {"value": "gym", "label": "Gymnasium"},
                    {"value": "swimming_pool", "label": "Swimming Pool"},
                    {"value": "playground", "label": "Children's Play Area"}
                ],
                "sortOrder": 8
            },
            {
                "fieldId": "parking_details",
                "uiDisplayName": "Parking Details",
                "fieldType": "group",
                "sortOrder": 9,
                "subFields": [
                    {"fieldId": "car_parking_slots", "uiDisplayName": "Car Parking Slots", "fieldType": "number", "sortOrder": 1},
                    {"fieldId": "two_wheeler_parking", "uiDisplayName": "Two-Wheeler Parking", "fieldType": "select", "options": [
                        {"value": "available", "label": "Available"},
                        {"value": "not_available", "label": "Not Available"}
                    ], "sortOrder": 2},
                    {"fieldId": "parking_type", "uiDisplayName": "Parking Type", "fieldType": "select", "options": [
                        {"value": "covered", "label": "Covered"},
                        {"value": "open", "label": "Open"},
                        {"value": "stilt", "label": "Stilt Parking"}
                    ], "sortOrder": 3}
                ]
            },
            {
                "fieldId": "maintenance_details",
                "uiDisplayName": "Maintenance Details",
                "fieldType": "group",
                "sortOrder": 10,
                "subFields": [
                    {"fieldId": "monthly_maintenance", "uiDisplayName": "Monthly Maintenance (Rs)", "fieldType": "currency", "sortOrder": 1},
                    {"fieldId": "maintenance_includes", "uiDisplayName": "Maintenance Includes", "fieldType": "multiselect", "options": [
                        {"value": "water", "label": "Water Supply"},
                        {"value": "electricity_common", "label": "Common Area Electricity"},
                        {"value": "security", "label": "Security Services"},
                        {"value": "cleaning", "label": "Cleaning Services"},
                        {"value": "lift_maintenance", "label": "Lift Maintenance"}
                    ], "sortOrder": 2}
                ]
            }
        ],
        "uiName": "Property Details"
    }

def create_apartment_site_characteristics():
    """Create apartment site characteristics document"""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "_id": str(ObjectId()),
        "templateId": "SBI_APARTMENT_SITE_CHARACTERISTICS_V1",
        "templateName": "SBI Apartment Site Characteristics", 
        "bankCode": "SBI",
        "propertyType": "Apartment",
        "templateCategory": "site_characteristics",
        "createdAt": now,
        "updatedAt": now,
        "isActive": True,
        "fields": [
            {
                "fieldId": "locality_classification",
                "uiDisplayName": "Locality Classification",
                "fieldType": "select",
                "options": [
                    {"value": "prime_residential", "label": "Prime Residential"},
                    {"value": "residential", "label": "Residential"},
                    {"value": "commercial", "label": "Commercial"},
                    {"value": "mixed_development", "label": "Mixed Development"}
                ],
                "isRequired": True,
                "sortOrder": 1
            },
            {
                "fieldId": "neighborhood_quality",
                "uiDisplayName": "Neighborhood Quality",
                "fieldType": "select",
                "options": [
                    {"value": "excellent", "label": "Excellent"},
                    {"value": "good", "label": "Good"},
                    {"value": "average", "label": "Average"},
                    {"value": "below_average", "label": "Below Average"}
                ],
                "isRequired": True,
                "sortOrder": 2
            },
            {
                "fieldId": "connectivity",
                "uiDisplayName": "Transport Connectivity",
                "fieldType": "group",
                "sortOrder": 3,
                "subFields": [
                    {"fieldId": "nearest_metro", "uiDisplayName": "Nearest Metro Station (km)", "fieldType": "decimal", "sortOrder": 1},
                    {"fieldId": "nearest_bus_stop", "uiDisplayName": "Nearest Bus Stop (km)", "fieldType": "decimal", "sortOrder": 2},
                    {"fieldId": "nearest_railway", "uiDisplayName": "Nearest Railway Station (km)", "fieldType": "decimal", "sortOrder": 3},
                    {"fieldId": "airport_distance", "uiDisplayName": "Airport Distance (km)", "fieldType": "decimal", "sortOrder": 4}
                ]
            },
            {
                "fieldId": "civic_amenities",
                "uiDisplayName": "Civic Amenities Proximity",
                "fieldType": "group",
                "sortOrder": 4,
                "subFields": [
                    {"fieldId": "schools_nearby", "uiDisplayName": "Schools within 2km", "fieldType": "number", "sortOrder": 1},
                    {"fieldId": "hospitals_nearby", "uiDisplayName": "Hospitals within 5km", "fieldType": "number", "sortOrder": 2},
                    {"fieldId": "shopping_malls", "uiDisplayName": "Shopping Centers within 3km", "fieldType": "number", "sortOrder": 3},
                    {"fieldId": "banks_atms", "uiDisplayName": "Banks/ATMs within 1km", "fieldType": "number", "sortOrder": 4}
                ]
            },
            {
                "fieldId": "road_infrastructure",
                "uiDisplayName": "Road Infrastructure",
                "fieldType": "group",
                "sortOrder": 5,
                "subFields": [
                    {"fieldId": "road_width", "uiDisplayName": "Approach Road Width (ft)", "fieldType": "number", "sortOrder": 1},
                    {"fieldId": "road_condition", "uiDisplayName": "Road Condition", "fieldType": "select", "options": [
                        {"value": "excellent", "label": "Excellent"},
                        {"value": "good", "label": "Good"},
                        {"value": "average", "label": "Average"},
                        {"value": "poor", "label": "Poor"}
                    ], "sortOrder": 2},
                    {"fieldId": "traffic_congestion", "uiDisplayName": "Traffic Congestion Level", "fieldType": "select", "options": [
                        {"value": "low", "label": "Low"},
                        {"value": "medium", "label": "Medium"},
                        {"value": "high", "label": "High"}
                    ], "sortOrder": 3}
                ]
            }
        ],
        "uiName": "Site Characteristics"
    }

def create_apartment_valuation():
    """Create apartment valuation document"""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "_id": str(ObjectId()),
        "templateId": "SBI_APARTMENT_VALUATION_V1",
        "templateName": "SBI Apartment Valuation",
        "bankCode": "SBI",
        "propertyType": "Apartment",
        "templateCategory": "valuation",
        "createdAt": now,
        "updatedAt": now,
        "isActive": True,
        "sections": [
            {
                "sectionId": "apartment_valuation",
                "sectionName": "Apartment Valuation Details",
                "sortOrder": 1,
                "fields": [
                    {
                        "fieldId": "carpet_area_rate",
                        "uiDisplayName": "Rate per sq ft (Carpet Area)",
                        "fieldType": "currency",
                        "isRequired": True,
                        "sortOrder": 1
                    },
                    {
                        "fieldId": "market_comparison",
                        "uiDisplayName": "Market Comparison Analysis",
                        "fieldType": "group",
                        "sortOrder": 2,
                        "subFields": [
                            {"fieldId": "similar_properties_rate_min", "uiDisplayName": "Similar Properties Rate (Min)", "fieldType": "currency", "sortOrder": 1},
                            {"fieldId": "similar_properties_rate_max", "uiDisplayName": "Similar Properties Rate (Max)", "fieldType": "currency", "sortOrder": 2},
                            {"fieldId": "age_factor", "uiDisplayName": "Age Factor (%)", "fieldType": "decimal", "sortOrder": 3},
                            {"fieldId": "condition_factor", "uiDisplayName": "Condition Factor (%)", "fieldType": "decimal", "sortOrder": 4}
                        ]
                    },
                    {
                        "fieldId": "estimated_apartment_value",
                        "uiDisplayName": "Estimated Apartment Value",
                        "fieldType": "calculated",
                        "formula": "carpet_area * carpet_area_rate",
                        "displayFormat": "currency",
                        "isReadonly": True,
                        "sortOrder": 3
                    }
                ]
            }
        ],
        "uiName": "Apartment Valuation"
    }

def main():
    """Main function to create all apartment collection documents"""
    try:
        client = MongoClient(MONGODB_URI)
        db = client['valuation_admin']
        collection = db['sbi_apartment_property_details']
        
        print("🔄 Creating SBI Apartment Property Details collection...")
        
        # Clear existing documents
        collection.delete_many({})
        print("✅ Cleared existing documents")
        
        # Create documents
        documents = [
            create_apartment_property_details(),
            create_apartment_site_characteristics(), 
            create_apartment_valuation()
        ]
        
        # Insert documents
        result = collection.insert_many(documents)
        print(f"✅ Created {len(result.inserted_ids)} documents in sbi_apartment_property_details collection")
        
        # Verify creation
        count = collection.count_documents({})
        print(f"✅ Total documents in collection: {count}")
        
        client.close()
        print("🎉 SBI Apartment Property Details collection created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating collection: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()