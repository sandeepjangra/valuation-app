#!/usr/bin/env python3
"""
Script to recreate UBI Land Property Details collection with comprehensive template documents.
Based on the SBI collection structure but customized for UBI bank requirements.
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

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'backend', 'data', 'ubi_land_property_details.json')

#!/usr/bin/env python3
"""
Script to recreate UBI Land Property Details collection with comprehensive template documents.
Based on the SBI collection structure but customized for UBI bank requirements.
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

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'backend', 'data', 'ubi_land_property_details.json')


def build_property_details_document():
    """Build the basic property details document"""
    return {
        "_id": ObjectId(),
        "templateName": "UBI Land Property Details - Basic Information",
        "bankCode": "UBI",
        "propertyType": "land",
        "description": "Basic property information and details for UBI land valuation",
        "category": "property_details",
        "version": "1.0",
        "isActive": True,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "sections": [
            {
                "sectionId": "property_basic",
                "sectionName": "Property Basic Information",
                "sectionOrder": 1,
                "fields": [
                    {
                        "fieldName": "property_address",
                        "uiDisplayName": "Property Address",
                        "fieldType": "textarea",
                        "isRequired": True,
                        "sortOrder": 1,
                        "validation": {"minLength": 10, "maxLength": 500}
                    },
                    {
                        "fieldName": "property_type_detail",
                        "uiDisplayName": "Property Type Detail",
                        "fieldType": "select",
                        "isRequired": True,
                        "sortOrder": 2,
                        "options": ["Agricultural Land", "Residential Plot", "Commercial Land", "Industrial Land", "Mixed Use Land"]
                    },
                    {
                        "fieldName": "survey_number",
                        "uiDisplayName": "Survey Number",
                        "fieldType": "text",
                        "isRequired": True,
                        "sortOrder": 3,
                        "validation": {"maxLength": 50}
                    },
                    {
                        "fieldName": "sub_division",
                        "uiDisplayName": "Sub Division",
                        "fieldType": "text",
                        "isRequired": False,
                        "sortOrder": 4,
                        "validation": {"maxLength": 50}
                    },
                    {
                        "fieldName": "village_town",
                        "uiDisplayName": "Village/Town",
                        "fieldType": "text",
                        "isRequired": True,
                        "sortOrder": 5,
                        "validation": {"maxLength": 100}
                    },
                    {
                        "fieldName": "taluka_tehsil",
                        "uiDisplayName": "Taluka/Tehsil",
                        "fieldType": "text",
                        "isRequired": True,
                        "sortOrder": 6,
                        "validation": {"maxLength": 100}
                    },
                    {
                        "fieldName": "district",
                        "uiDisplayName": "District",
                        "fieldType": "text",
                        "isRequired": True,
                        "sortOrder": 7,
                        "validation": {"maxLength": 100}
                    },
                    {
                        "fieldName": "state",
                        "uiDisplayName": "State",
                        "fieldType": "select",
                        "isRequired": True,
                        "sortOrder": 8,
                        "options": ["Andhra Pradesh", "Gujarat", "Karnataka", "Maharashtra", "Tamil Nadu", "Telangana", "Other"]
                    },
                    {
                        "fieldName": "pin_code",
                        "uiDisplayName": "PIN Code",
                        "fieldType": "text",
                        "isRequired": True,
                        "sortOrder": 9,
                        "validation": {"pattern": "^[0-9]{6}$"}
                    },
                    {
                        "fieldName": "total_area",
                        "uiDisplayName": "Total Area",
                        "fieldType": "number_with_unit",
                        "isRequired": True,
                        "sortOrder": 10,
                        "unit": "sq ft",
                        "validation": {"min": 1}
                    },
                    {
                        "fieldName": "area_unit",
                        "uiDisplayName": "Area Unit",
                        "fieldType": "select",
                        "isRequired": True,
                        "sortOrder": 11,
                        "options": ["Sq Ft", "Sq Meter", "Acres", "Hectares", "Guntha", "Bigha"]
                    },
                    {
                        "fieldName": "boundaries_north",
                        "uiDisplayName": "North Boundary",
                        "fieldType": "text",
                        "isRequired": True,
                        "sortOrder": 12,
                        "validation": {"maxLength": 200}
                    },
                    {
                        "fieldName": "boundaries_south",
                        "uiDisplayName": "South Boundary",
                        "fieldType": "text",
                        "isRequired": True,
                        "sortOrder": 13,
                        "validation": {"maxLength": 200}
                    },
                    {
                        "fieldName": "boundaries_east",
                        "uiDisplayName": "East Boundary",
                        "fieldType": "text",
                        "isRequired": True,
                        "sortOrder": 14,
                        "validation": {"maxLength": 200}
                    },
                    {
                        "fieldName": "boundaries_west",
                        "uiDisplayName": "West Boundary",
                        "fieldType": "text",
                        "isRequired": True,
                        "sortOrder": 15,
                        "validation": {"maxLength": 200}
                    },
                    {
                        "fieldName": "property_owner",
                        "uiDisplayName": "Property Owner Name",
                        "fieldType": "text",
                        "isRequired": True,
                        "sortOrder": 16,
                        "validation": {"maxLength": 200}
                    },
                    {
                        "fieldName": "ownership_type",
                        "uiDisplayName": "Ownership Type",
                        "fieldType": "select",
                        "isRequired": True,
                        "sortOrder": 17,
                        "options": ["Freehold", "Leasehold", "Joint Ownership", "Power of Attorney", "Other"]
                    }
                ]
            }
        ]
    }


def build_site_characteristics_document():
    """Build the site characteristics document"""
    return {
        "_id": ObjectId(),
        "templateName": "UBI Land Property Details - Site Characteristics",
        "bankCode": "UBI",
        "propertyType": "land",
        "description": "Site characteristics and accessibility details for UBI land valuation",
        "category": "site_characteristics",
        "version": "1.0",
        "isActive": True,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "sections": [
            {
                "sectionId": "site_features",
                "sectionName": "Site Features and Accessibility",
                "sectionOrder": 1,
                "fields": [
                    {
                        "fieldName": "road_width",
                        "uiDisplayName": "Road Width (in feet)",
                        "fieldType": "number",
                        "isRequired": True,
                        "sortOrder": 1,
                        "validation": {"min": 1, "max": 200}
                    },
                    {
                        "fieldName": "road_type",
                        "uiDisplayName": "Road Type",
                        "fieldType": "select",
                        "isRequired": True,
                        "sortOrder": 2,
                        "options": ["Paved/Metalled", "Unpaved/Kachha", "Semi-Paved", "Highway", "Internal Road"]
                    },
                    {
                        "fieldName": "distance_main_road",
                        "uiDisplayName": "Distance from Main Road (in meters)",
                        "fieldType": "number",
                        "isRequired": True,
                        "sortOrder": 3,
                        "validation": {"min": 0}
                    },
                    {
                        "fieldName": "public_transport",
                        "uiDisplayName": "Public Transport Availability",
                        "fieldType": "select",
                        "isRequired": True,
                        "sortOrder": 4,
                        "options": ["Excellent", "Good", "Fair", "Poor", "Not Available"]
                    },
                    {
                        "fieldName": "water_supply",
                        "uiDisplayName": "Water Supply",
                        "fieldType": "multiselect",
                        "isRequired": True,
                        "sortOrder": 5,
                        "options": ["Municipal Water", "Borewell", "Well", "Tanker Supply", "None"]
                    },
                    {
                        "fieldName": "electricity_connection",
                        "uiDisplayName": "Electricity Connection",
                        "fieldType": "select",
                        "isRequired": True,
                        "sortOrder": 6,
                        "options": ["Available", "Not Available", "Can be Arranged"]
                    },
                    {
                        "fieldName": "drainage_system",
                        "uiDisplayName": "Drainage System",
                        "fieldType": "select",
                        "isRequired": True,
                        "sortOrder": 7,
                        "options": ["Good", "Average", "Poor", "Not Available"]
                    },
                    {
                        "fieldName": "sewerage_system",
                        "uiDisplayName": "Sewerage System",
                        "fieldType": "select",
                        "isRequired": True,
                        "sortOrder": 8,
                        "options": ["Available", "Not Available", "Under Development"]
                    },
                    {
                        "fieldName": "topography",
                        "uiDisplayName": "Topography",
                        "fieldType": "select",
                        "isRequired": True,
                        "sortOrder": 9,
                        "options": ["Level", "Slightly Sloped", "Moderately Sloped", "Steep", "Undulating"]
                    },
                    {
                        "fieldName": "soil_type",
                        "uiDisplayName": "Soil Type",
                        "fieldType": "select",
                        "isRequired": True,
                        "sortOrder": 10,
                        "options": ["Black Cotton", "Red Soil", "Sandy", "Clay", "Loamy", "Rocky", "Other"]
                    },
                    {
                        "fieldName": "land_use_zoning",
                        "uiDisplayName": "Land Use Zoning",
                        "fieldType": "select",
                        "isRequired": True,
                        "sortOrder": 11,
                        "options": ["Residential", "Commercial", "Industrial", "Agricultural", "Mixed Use", "Green Belt"]
                    },
                    {
                        "fieldName": "development_potential",
                        "uiDisplayName": "Development Potential",
                        "fieldType": "select",
                        "isRequired": True,
                        "sortOrder": 12,
                        "options": ["High", "Medium", "Low", "Restricted"]
                    },
                    {
                        "fieldName": "locality_status",
                        "uiDisplayName": "Locality Status",
                        "fieldType": "select",
                        "isRequired": True,
                        "sortOrder": 13,
                        "options": ["Fully Developed", "Developing", "Under Development", "Undeveloped"]
                    },
                    {
                        "fieldName": "nearby_landmarks",
                        "uiDisplayName": "Nearby Landmarks",
                        "fieldType": "textarea",
                        "isRequired": False,
                        "sortOrder": 14,
                        "validation": {"maxLength": 500}
                    },
                    {
                        "fieldName": "distance_railway_station",
                        "uiDisplayName": "Distance from Railway Station (km)",
                        "fieldType": "number",
                        "isRequired": False,
                        "sortOrder": 15,
                        "validation": {"min": 0}
                    },
                    {
                        "fieldName": "distance_airport",
                        "uiDisplayName": "Distance from Airport (km)",
                        "fieldType": "number",
                        "isRequired": False,
                        "sortOrder": 16,
                        "validation": {"min": 0}
                    },
                    {
                        "fieldName": "distance_city_center",
                        "uiDisplayName": "Distance from City Center (km)",
                        "fieldType": "number",
                        "isRequired": False,
                        "sortOrder": 17,
                        "validation": {"min": 0}
                    },
                    {
                        "fieldName": "flood_risk",
                        "uiDisplayName": "Flood Risk Assessment",
                        "fieldType": "select",
                        "isRequired": True,
                        "sortOrder": 18,
                        "options": ["No Risk", "Low Risk", "Medium Risk", "High Risk"]
                    },
                    {
                        "fieldName": "environmental_clearance",
                        "uiDisplayName": "Environmental Clearance Required",
                        "fieldType": "select",
                        "isRequired": True,
                        "sortOrder": 19,
                        "options": ["Yes", "No", "Not Applicable"]
                    }
                ]
            }
        ]
    }


def build_valuation_document():
    """Build the valuation document with Part A and Part B sections"""
    return {
        "_id": ObjectId(),
        "templateName": "UBI Land Property Details - Valuation Assessment",
        "bankCode": "UBI",
        "propertyType": "land",
        "description": "Comprehensive valuation assessment for UBI land property",
        "category": "valuation",
        "version": "1.0",
        "isActive": True,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "sections": [
            {
                "sectionId": "valuation_part_a",
                "sectionName": "Valuation Part A - Market Analysis",
                "sectionOrder": 1,
                "fields": [
                    {
                        "fieldName": "comparable_sale_1_rate",
                        "uiDisplayName": "Comparable Sale 1 - Rate per sq ft",
                        "fieldType": "currency",
                        "isRequired": True,
                        "sortOrder": 1,
                        "validation": {"min": 0}
                    },
                    {
                        "fieldName": "comparable_sale_1_details",
                        "uiDisplayName": "Comparable Sale 1 - Details",
                        "fieldType": "textarea",
                        "isRequired": True,
                        "sortOrder": 2,
                        "validation": {"maxLength": 300}
                    },
                    {
                        "fieldName": "comparable_sale_2_rate",
                        "uiDisplayName": "Comparable Sale 2 - Rate per sq ft",
                        "fieldType": "currency",
                        "isRequired": True,
                        "sortOrder": 3,
                        "validation": {"min": 0}
                    },
                    {
                        "fieldName": "comparable_sale_2_details",
                        "uiDisplayName": "Comparable Sale 2 - Details",
                        "fieldType": "textarea",
                        "isRequired": True,
                        "sortOrder": 4,
                        "validation": {"maxLength": 300}
                    },
                    {
                        "fieldName": "comparable_sale_3_rate",
                        "uiDisplayName": "Comparable Sale 3 - Rate per sq ft",
                        "fieldType": "currency",
                        "isRequired": True,
                        "sortOrder": 5,
                        "validation": {"min": 0}
                    },
                    {
                        "fieldName": "comparable_sale_3_details",
                        "uiDisplayName": "Comparable Sale 3 - Details",
                        "fieldType": "textarea",
                        "isRequired": True,
                        "sortOrder": 6,
                        "validation": {"maxLength": 300}
                    },
                    {
                        "fieldName": "average_market_rate",
                        "uiDisplayName": "Average Market Rate per sq ft",
                        "fieldType": "calculated",
                        "isRequired": False,
                        "sortOrder": 7,
                        "formula": "(comparable_sale_1_rate + comparable_sale_2_rate + comparable_sale_3_rate) / 3",
                        "validation": {"min": 0}
                    }
                ]
            },
            {
                "sectionId": "valuation_part_b",
                "sectionName": "Valuation Part B - Final Assessment",
                "sectionOrder": 2,
                "fields": [
                    {
                        "fieldName": "adopted_rate_per_sqft",
                        "uiDisplayName": "Adopted Rate per sq ft",
                        "fieldType": "currency",
                        "isRequired": True,
                        "sortOrder": 8,
                        "validation": {"min": 0}
                    },
                    {
                        "fieldName": "total_land_area_valuation",
                        "uiDisplayName": "Total Land Area for Valuation",
                        "fieldType": "number",
                        "isRequired": True,
                        "sortOrder": 9,
                        "validation": {"min": 1}
                    },
                    {
                        "fieldName": "gross_value",
                        "uiDisplayName": "Gross Value",
                        "fieldType": "calculated",
                        "isRequired": False,
                        "sortOrder": 10,
                        "formula": "adopted_rate_per_sqft * total_land_area_valuation",
                        "validation": {"min": 0}
                    },
                    {
                        "fieldName": "depreciation_percentage",
                        "uiDisplayName": "Depreciation Percentage",
                        "fieldType": "number",
                        "isRequired": False,
                        "sortOrder": 11,
                        "validation": {"min": 0, "max": 100},
                        "defaultValue": 0
                    },
                    {
                        "fieldName": "depreciation_amount",
                        "uiDisplayName": "Depreciation Amount",
                        "fieldType": "calculated",
                        "isRequired": False,
                        "sortOrder": 12,
                        "formula": "(gross_value * depreciation_percentage) / 100",
                        "validation": {"min": 0}
                    },
                    {
                        "fieldName": "net_value",
                        "uiDisplayName": "Net Value",
                        "fieldType": "calculated",
                        "isRequired": False,
                        "sortOrder": 13,
                        "formula": "gross_value - depreciation_amount",
                        "validation": {"min": 0}
                    },
                    {
                        "fieldName": "distress_sale_value",
                        "uiDisplayName": "Distress Sale Value (80% of Net Value)",
                        "fieldType": "calculated",
                        "isRequired": False,
                        "sortOrder": 14,
                        "formula": "net_value * 0.8",
                        "validation": {"min": 0}
                    },
                    {
                        "fieldName": "valuation_remarks",
                        "uiDisplayName": "Valuation Remarks",
                        "fieldType": "textarea",
                        "isRequired": False,
                        "sortOrder": 15,
                        "validation": {"maxLength": 1000}
                    },
                    {
                        "fieldName": "valuer_recommendation",
                        "uiDisplayName": "Valuer Recommendation",
                        "fieldType": "select",
                        "isRequired": True,
                        "sortOrder": 16,
                        "options": ["Recommended for Loan", "Not Recommended", "Conditional Approval"]
                    },
                    {
                        "fieldName": "recommended_loan_amount",
                        "uiDisplayName": "Recommended Loan Amount",
                        "fieldType": "currency",
                        "isRequired": True,
                        "sortOrder": 17,
                        "validation": {"min": 0}
                    }
                ]
            }
        ]
    }


def build_construction_specifications_document():
    """Build construction specifications document"""
    return {
        "_id": ObjectId(),
        "templateName": "UBI Land Property Details - Construction Specifications",
        "bankCode": "UBI",
        "propertyType": "land",
        "description": "Construction specifications and development details for UBI land property",
        "category": "construction_specs",
        "version": "1.0",
        "isActive": True,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "sections": [
            {
                "sectionId": "construction_details",
                "sectionName": "Construction and Development Details",
                "sectionOrder": 1,
                "fields": [
                    {
                        "fieldName": "approved_plan_status",
                        "uiDisplayName": "Approved Plan Status",
                        "fieldType": "select",
                        "isRequired": True,
                        "sortOrder": 1,
                        "options": ["Approved", "Not Approved", "In Process", "Not Applicable"]
                    },
                    {
                        "fieldName": "construction_permission",
                        "uiDisplayName": "Construction Permission",
                        "fieldType": "select",
                        "isRequired": True,
                        "sortOrder": 2,
                        "options": ["Available", "Not Available", "In Process", "Not Required"]
                    },
                    {
                        "fieldName": "building_plan_area",
                        "uiDisplayName": "Building Plan Area (sq ft)",
                        "fieldType": "number",
                        "isRequired": False,
                        "sortOrder": 3,
                        "validation": {"min": 0}
                    },
                    {
                        "fieldName": "floor_area_ratio",
                        "uiDisplayName": "Floor Area Ratio (FAR)",
                        "fieldType": "number",
                        "isRequired": False,
                        "sortOrder": 4,
                        "validation": {"min": 0, "max": 10}
                    },
                    {
                        "fieldName": "setback_requirements",
                        "uiDisplayName": "Setback Requirements Met",
                        "fieldType": "select",
                        "isRequired": False,
                        "sortOrder": 5,
                        "options": ["Yes", "No", "Partially", "Not Applicable"]
                    },
                    {
                        "fieldName": "proposed_construction_type",
                        "uiDisplayName": "Proposed Construction Type",
                        "fieldType": "select",
                        "isRequired": False,
                        "sortOrder": 6,
                        "options": ["Residential", "Commercial", "Industrial", "Mixed Use", "None Planned"]
                    },
                    {
                        "fieldName": "number_of_floors",
                        "uiDisplayName": "Number of Floors Proposed",
                        "fieldType": "number",
                        "isRequired": False,
                        "sortOrder": 7,
                        "validation": {"min": 0, "max": 50}
                    },
                    {
                        "fieldName": "parking_provision",
                        "uiDisplayName": "Parking Provision",
                        "fieldType": "select",
                        "isRequired": False,
                        "sortOrder": 8,
                        "options": ["Adequate", "Inadequate", "Not Planned", "Not Required"]
                    },
                    {
                        "fieldName": "fire_safety_compliance",
                        "uiDisplayName": "Fire Safety Compliance",
                        "fieldType": "select",
                        "isRequired": False,
                        "sortOrder": 9,
                        "options": ["Compliant", "Non-Compliant", "Not Applicable", "Under Review"]
                    },
                    {
                        "fieldName": "earthquake_resistance",
                        "uiDisplayName": "Earthquake Resistance Standards",
                        "fieldType": "select",
                        "isRequired": False,
                        "sortOrder": 10,
                        "options": ["IS Code Compliant", "Non-Compliant", "Not Applicable", "Under Review"]
                    },
                    {
                        "fieldName": "green_building_certification",
                        "uiDisplayName": "Green Building Certification",
                        "fieldType": "select",
                        "isRequired": False,
                        "sortOrder": 11,
                        "options": ["LEED", "IGBC", "GRIHA", "None", "Not Applicable"]
                    },
                    {
                        "fieldName": "rainwater_harvesting",
                        "uiDisplayName": "Rainwater Harvesting Provision",
                        "fieldType": "select",
                        "isRequired": False,
                        "sortOrder": 12,
                        "options": ["Provided", "Not Provided", "Planned", "Not Required"]
                    },
                    {
                        "fieldName": "sewage_treatment",
                        "uiDisplayName": "Sewage Treatment Facility",
                        "fieldType": "select",
                        "isRequired": False,
                        "sortOrder": 13,
                        "options": ["STP Provided", "Connected to Municipal", "None", "Not Required"]
                    },
                    {
                        "fieldName": "waste_management",
                        "uiDisplayName": "Waste Management System",
                        "fieldType": "select",
                        "isRequired": False,
                        "sortOrder": 14,
                        "options": ["Comprehensive", "Basic", "None", "Under Planning"]
                    },
                    {
                        "fieldName": "accessibility_features",
                        "uiDisplayName": "Accessibility Features",
                        "fieldType": "multiselect",
                        "isRequired": False,
                        "sortOrder": 15,
                        "options": ["Ramps", "Lifts", "Wide Doorways", "Accessible Toilets", "None"]
                    },
                    {
                        "fieldName": "construction_quality_grade",
                        "uiDisplayName": "Construction Quality Grade",
                        "fieldType": "select",
                        "isRequired": False,
                        "sortOrder": 16,
                        "options": ["Excellent", "Good", "Average", "Poor", "Not Applicable"]
                    }
                ]
            }
        ]
    }


def build_detailed_valuation_document():
    """Build detailed valuation document with comprehensive breakdown"""
    return {
        "_id": ObjectId(),
        "templateName": "UBI Land Property Details - Detailed Valuation",
        "bankCode": "UBI",
        "propertyType": "land", 
        "description": "Comprehensive detailed valuation breakdown for UBI land property assessment",
        "category": "detailed_valuation",
        "version": "1.0",
        "isActive": True,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "sections": [
            {
                "sectionId": "land_valuation",
                "sectionName": "Land Valuation Details",
                "sectionOrder": 1,
                "fields": [
                    {
                        "fieldName": "circle_rate",
                        "uiDisplayName": "Government Circle Rate per sq ft",
                        "fieldType": "currency",
                        "isRequired": True,
                        "sortOrder": 1,
                        "validation": {"min": 0}
                    },
                    {
                        "fieldName": "market_rate_assessment",
                        "uiDisplayName": "Market Rate Assessment per sq ft",
                        "fieldType": "currency",
                        "isRequired": True,
                        "sortOrder": 2,
                        "validation": {"min": 0}
                    },
                    {
                        "fieldName": "location_premium",
                        "uiDisplayName": "Location Premium (%)",
                        "fieldType": "number",
                        "isRequired": False,
                        "sortOrder": 3,
                        "validation": {"min": -50, "max": 100},
                        "defaultValue": 0
                    },
                    {
                        "fieldName": "development_potential_premium",
                        "uiDisplayName": "Development Potential Premium (%)",
                        "fieldType": "number",
                        "isRequired": False,
                        "sortOrder": 4,
                        "validation": {"min": -20, "max": 50},
                        "defaultValue": 0
                    },
                    {
                        "fieldName": "infrastructure_premium",
                        "uiDisplayName": "Infrastructure Premium (%)",
                        "fieldType": "number",
                        "isRequired": False,
                        "sortOrder": 5,
                        "validation": {"min": -30, "max": 30},
                        "defaultValue": 0
                    },
                    {
                        "fieldName": "adjusted_rate_per_sqft",
                        "uiDisplayName": "Adjusted Rate per sq ft",
                        "fieldType": "calculated",
                        "isRequired": False,
                        "sortOrder": 6,
                        "formula": "market_rate_assessment * (1 + (location_premium + development_potential_premium + infrastructure_premium) / 100)",
                        "validation": {"min": 0}
                    }
                ]
            },
            {
                "sectionId": "cost_breakdown",
                "sectionName": "Cost and Expense Breakdown", 
                "sectionOrder": 2,
                "fields": [
                    {
                        "fieldName": "registration_charges",
                        "uiDisplayName": "Registration Charges",
                        "fieldType": "currency",
                        "isRequired": False,
                        "sortOrder": 7,
                        "validation": {"min": 0},
                        "defaultValue": 0
                    },
                    {
                        "fieldName": "stamp_duty",
                        "uiDisplayName": "Stamp Duty",
                        "fieldType": "currency", 
                        "isRequired": False,
                        "sortOrder": 8,
                        "validation": {"min": 0},
                        "defaultValue": 0
                    },
                    {
                        "fieldName": "legal_charges",
                        "uiDisplayName": "Legal Charges",
                        "fieldType": "currency",
                        "isRequired": False,
                        "sortOrder": 9,
                        "validation": {"min": 0},
                        "defaultValue": 0
                    },
                    {
                        "fieldName": "brokerage_commission",
                        "uiDisplayName": "Brokerage/Commission",
                        "fieldType": "currency",
                        "isRequired": False,
                        "sortOrder": 10,
                        "validation": {"min": 0},
                        "defaultValue": 0
                    },
                    {
                        "fieldName": "other_expenses",
                        "uiDisplayName": "Other Expenses",
                        "fieldType": "currency",
                        "isRequired": False,
                        "sortOrder": 11,
                        "validation": {"min": 0},
                        "defaultValue": 0
                    },
                    {
                        "fieldName": "total_additional_costs",
                        "uiDisplayName": "Total Additional Costs",
                        "fieldType": "calculated",
                        "isRequired": False,
                        "sortOrder": 12,
                        "formula": "registration_charges + stamp_duty + legal_charges + brokerage_commission + other_expenses",
                        "validation": {"min": 0}
                    }
                ]
            },
            {
                "sectionId": "valuation_methods",
                "sectionName": "Valuation Methods Comparison",
                "sectionOrder": 3,
                "fields": [
                    {
                        "fieldName": "cost_approach_value",
                        "uiDisplayName": "Cost Approach Value",
                        "fieldType": "currency",
                        "isRequired": True,
                        "sortOrder": 13,
                        "validation": {"min": 0}
                    },
                    {
                        "fieldName": "market_approach_value",
                        "uiDisplayName": "Market Approach Value",
                        "fieldType": "currency",
                        "isRequired": True,
                        "sortOrder": 14,
                        "validation": {"min": 0}
                    },
                    {
                        "fieldName": "income_approach_value",
                        "uiDisplayName": "Income Approach Value",
                        "fieldType": "currency",
                        "isRequired": False,
                        "sortOrder": 15,
                        "validation": {"min": 0},
                        "defaultValue": 0
                    },
                    {
                        "fieldName": "method_weightage_cost",
                        "uiDisplayName": "Cost Method Weightage (%)",
                        "fieldType": "number",
                        "isRequired": True,
                        "sortOrder": 16,
                        "validation": {"min": 0, "max": 100},
                        "defaultValue": 30
                    },
                    {
                        "fieldName": "method_weightage_market",
                        "uiDisplayName": "Market Method Weightage (%)",
                        "fieldType": "number",
                        "isRequired": True,
                        "sortOrder": 17,
                        "validation": {"min": 0, "max": 100},
                        "defaultValue": 60
                    },
                    {
                        "fieldName": "method_weightage_income",
                        "uiDisplayName": "Income Method Weightage (%)",
                        "fieldType": "number",
                        "isRequired": False,
                        "sortOrder": 18,
                        "validation": {"min": 0, "max": 100},
                        "defaultValue": 10
                    },
                    {
                        "fieldName": "weighted_average_value",
                        "uiDisplayName": "Weighted Average Value",
                        "fieldType": "calculated",
                        "isRequired": False,
                        "sortOrder": 19,
                        "formula": "((cost_approach_value * method_weightage_cost) + (market_approach_value * method_weightage_market) + (income_approach_value * method_weightage_income)) / 100",
                        "validation": {"min": 0}
                    }
                ]
            },
            {
                "sectionId": "risk_assessment",
                "sectionName": "Risk Assessment and Adjustments",
                "sectionOrder": 4,
                "fields": [
                    {
                        "fieldName": "market_risk_factor",
                        "uiDisplayName": "Market Risk Factor (%)",
                        "fieldType": "number",
                        "isRequired": True,
                        "sortOrder": 20,
                        "validation": {"min": 0, "max": 50},
                        "defaultValue": 5
                    },
                    {
                        "fieldName": "liquidity_risk_factor",
                        "uiDisplayName": "Liquidity Risk Factor (%)",
                        "fieldType": "number",
                        "isRequired": True,
                        "sortOrder": 21,
                        "validation": {"min": 0, "max": 30},
                        "defaultValue": 10
                    },
                    {
                        "fieldName": "legal_risk_factor",
                        "uiDisplayName": "Legal Risk Factor (%)",
                        "fieldType": "number",
                        "isRequired": False,
                        "sortOrder": 22,
                        "validation": {"min": 0, "max": 25},
                        "defaultValue": 2
                    },
                    {
                        "fieldName": "total_risk_adjustment",
                        "uiDisplayName": "Total Risk Adjustment (%)",
                        "fieldType": "calculated",
                        "isRequired": False,
                        "sortOrder": 23,
                        "formula": "market_risk_factor + liquidity_risk_factor + legal_risk_factor",
                        "validation": {"min": 0}
                    },
                    {
                        "fieldName": "risk_adjusted_value",
                        "uiDisplayName": "Risk Adjusted Value",
                        "fieldType": "calculated",
                        "isRequired": False,
                        "sortOrder": 24,
                        "formula": "weighted_average_value * (1 - total_risk_adjustment / 100)",
                        "validation": {"min": 0}
                    }
                ]
            },
            {
                "sectionId": "final_valuation",
                "sectionName": "Final Valuation Summary",
                "sectionOrder": 5,
                "fields": [
                    {
                        "fieldName": "fair_market_value",
                        "uiDisplayName": "Fair Market Value",
                        "fieldType": "calculated",
                        "isRequired": False,
                        "sortOrder": 25,
                        "formula": "risk_adjusted_value",
                        "validation": {"min": 0}
                    },
                    {
                        "fieldName": "forced_sale_value",
                        "uiDisplayName": "Forced Sale Value (85% of FMV)",
                        "fieldType": "calculated",
                        "isRequired": False,
                        "sortOrder": 26,
                        "formula": "fair_market_value * 0.85",
                        "validation": {"min": 0}
                    },
                    {
                        "fieldName": "distress_sale_value_detailed",
                        "uiDisplayName": "Distress Sale Value (75% of FMV)",
                        "fieldType": "calculated",
                        "isRequired": False,
                        "sortOrder": 27,
                        "formula": "fair_market_value * 0.75",
                        "validation": {"min": 0}
                    },
                    {
                        "fieldName": "loan_to_value_ratio",
                        "uiDisplayName": "Recommended LTV Ratio (%)",
                        "fieldType": "number",
                        "isRequired": True,
                        "sortOrder": 28,
                        "validation": {"min": 30, "max": 90},
                        "defaultValue": 80
                    },
                    {
                        "fieldName": "maximum_loan_amount",
                        "uiDisplayName": "Maximum Loan Amount",
                        "fieldType": "calculated",
                        "isRequired": False,
                        "sortOrder": 29,
                        "formula": "fair_market_value * loan_to_value_ratio / 100",
                        "validation": {"min": 0}
                    },
                    {
                        "fieldName": "valuation_certainty",
                        "uiDisplayName": "Valuation Certainty Level",
                        "fieldType": "select",
                        "isRequired": True,
                        "sortOrder": 30,
                        "options": ["High", "Medium", "Low"]
                    },
                    {
                        "fieldName": "final_remarks",
                        "uiDisplayName": "Final Valuation Remarks",
                        "fieldType": "textarea",
                        "isRequired": False,
                        "sortOrder": 31,
                        "validation": {"maxLength": 1000}
                    }
                ]
            }
        ]
    }


def main():
    """Main execution function"""
    print("🚀 UBI Land Property Details Collection Recreation")
    print("=" * 60)
    
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_URI, tlsAllowInvalidCertificates=True)
        db = client['valuation_admin']
        
        collection_name = 'ubi_land_property_details'
        
        # Drop existing collection if it exists
        try:
            db[collection_name].drop()
            print(f"✅ Dropped existing collection: {collection_name}")
        except Exception as e:
            print(f"ℹ️  Collection {collection_name} did not exist (this is okay)")
        
        # Build template documents
        documents = [
            build_property_details_document(),
            build_site_characteristics_document(), 
            build_valuation_document(),
            build_construction_specifications_document(),
            build_detailed_valuation_document()
        ]
        
        # Insert documents
        collection = db[collection_name]
        result = collection.insert_many(documents)
        
        print(f"✅ Created collection: {collection_name}")
        print(f"✅ Inserted {len(result.inserted_ids)} template documents")
        
        # Generate JSON file for API
        documents_for_json = []
        for doc in documents:
            # Convert ObjectId to string for JSON serialization
            doc_copy = doc.copy()
            doc_copy['_id'] = str(doc_copy['_id'])
            documents_for_json.append(doc_copy)
        
        # Create the JSON structure
        json_data = {
            "collectionName": collection_name,
            "bankCode": "UBI",
            "propertyType": "land",
            "lastUpdated": datetime.now(timezone.utc).isoformat(),
            "totalDocuments": len(documents_for_json),
            "documents": documents_for_json
        }
        
        # Write to JSON file
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
            
        print(f"✅ Generated JSON file: {OUTPUT_PATH}")
        print(f"📊 Total documents in JSON: {len(documents_for_json)}")
        
        # Verify collection
        doc_count = collection.count_documents({})
        print(f"\n📊 Collection verification:")
        print(f"   Total documents: {doc_count}")
        
        # Show document categories
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        categories = list(collection.aggregate(pipeline))
        
        print(f"   Document categories:")
        for cat in categories:
            print(f"   - {cat['_id']}: {cat['count']} document(s)")
        
        print("\n🎉 UBI Land Property Details collection is ready!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
