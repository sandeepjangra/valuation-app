#!/usr/bin/env python3
"""
Script to recreate the sbi_land_property_details collection in valuation_admin
and refresh the backend/data/sbi_land_property_details.json file.

This script will delete existing documents in the collection and insert a
single template document describing the form fields. The API provides multiple
forms per template so storing a single template document is sufficient.
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

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'backend', 'data', 'sbi_land_property_details.json')


def build_property_details_document():
    now = datetime.now(timezone.utc).isoformat()
    return {
        "_id": str(ObjectId()),
        "templateId": "SBI_LAND_PROPERTY_DETAILS_V1",
        "templateName": "SBI Land Property Details",
        "bankCode": "SBI",
        "propertyType": "Land",
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
                    {"value": "sales_deed", "label": "Sales Deed"},
                    {"value": "layout_plan", "label": "Layout Plan"},
                    {"value": "allotment_letter", "label": "Allotment Letter"}
                ],
                "helpText": "Select applicable documents",
                "isRequired": False,
                "sortOrder": 1
            },
            {
                "fieldId": "postal_address",
                "uiDisplayName": "Postal Address",
                "fieldType": "textarea",
                "isRequired": False,
                "placeholder": "Enter postal address",
                "sortOrder": 2
            },
            {
                "fieldId": "property_description",
                "uiDisplayName": "Property Description",
                "fieldType": "textarea",
                "isRequired": False,
                "placeholder": "Describe the property",
                "sortOrder": 3
            },
            {
                "fieldId": "property_location",
                "uiDisplayName": "Property Location",
                "fieldType": "group",
                "isRequired": False,
                "sortOrder": 4,
                "subFields": [
                    {"fieldId": "plot_survey_no", "uiDisplayName": "Plot No./Survey No.", "fieldType": "text", "sortOrder": 1},
                    {"fieldId": "door_no", "uiDisplayName": "Door No.", "fieldType": "text", "sortOrder": 2},
                    {"fieldId": "ts_no_village", "uiDisplayName": "T.S. No./Village", "fieldType": "text", "sortOrder": 3},
                    {"fieldId": "ward_taluka_tehsil", "uiDisplayName": "Ward/Taluka/Tehsil", "fieldType": "text", "sortOrder": 4},
                    {"fieldId": "mandal_district", "uiDisplayName": "Mandal/District", "fieldType": "text", "sortOrder": 5}
                ]
            },
            {
                "fieldId": "city_town_village",
                "uiDisplayName": "City/Town/Village",
                "fieldType": "select",
                "options": [
                    {"value": "city", "label": "City"},
                    {"value": "town", "label": "Town"},
                    {"value": "village", "label": "Village"}
                ],
                "isRequired": True,
                "sortOrder": 5
            },
            {
                "fieldId": "area_type",
                "uiDisplayName": "Area Type",
                "fieldType": "select",
                "options": [
                    {"value": "residential", "label": "Residential"},
                    {"value": "commercial", "label": "Commercial"},
                    {"value": "industrial", "label": "Industrial"}
                ],
                "isRequired": True,
                "sortOrder": 6
            },
            {
                "fieldId": "area_classification",
                "uiDisplayName": "Area Classification",
                "fieldType": "group",
                "sortOrder": 7,
                "subFields": [
                    {"fieldId": "socio_economic_class", "uiDisplayName": "High/Middle/Poor", "fieldType": "select", "options": [
                        {"value": "high", "label": "High"},
                        {"value": "middle", "label": "Middle"},
                        {"value": "poor", "label": "Poor"}
                    ], "isRequired": True, "sortOrder": 1},
                    {"fieldId": "urban_rural", "uiDisplayName": "Urban/Semi Urban/Rural", "fieldType": "select", "options": [
                        {"value": "urban", "label": "Urban"},
                        {"value": "semi_urban", "label": "Semi Urban"},
                        {"value": "rural", "label": "Rural"}
                    ], "isRequired": True, "sortOrder": 2}
                ]
            },
            {
                "fieldId": "municipal_corporation",
                "uiDisplayName": "Municipal Corporation",
                "fieldType": "select",
                "options": [
                    {"value": "panchkula", "label": "Municipal Corporation Panchkula"},
                    {"value": "chandigarh", "label": "Municipal Corporation Chandigarh"}
                ],
                "isRequired": False,
                "sortOrder": 8
            },
            {
                "fieldId": "state_enactments",
                "uiDisplayName": "State/Central Govt Enactments",
                "fieldType": "textarea",
                "isRequired": False,
                "defaultValue": "NA",
                "helpText": "Whether covered under any State/ Central Govt. enactments...",
                "sortOrder": 9
            },
            {
                "fieldId": "agriculture_conversion",
                "uiDisplayName": "Agricultural Conversion",
                "fieldType": "textarea",
                "isRequired": False,
                "defaultValue": "NA",
                "helpText": "In case it is an agricultural land, any conversion to house site plots is contemplated",
                "sortOrder": 10
            },
            {
                "fieldId": "boundaries",
                "uiDisplayName": "Boundaries of the Property",
                "fieldType": "group",
                "sortOrder": 11,
                "subFields": [
                    {"fieldId": "north_boundary", "uiDisplayName": "North", "fieldType": "textarea", "sortOrder": 1},
                    {"fieldId": "south_boundary", "uiDisplayName": "South", "fieldType": "textarea", "sortOrder": 2},
                    {"fieldId": "east_boundary", "uiDisplayName": "East", "fieldType": "textarea", "sortOrder": 3},
                    {"fieldId": "west_boundary", "uiDisplayName": "West", "fieldType": "textarea", "sortOrder": 4}
                ]
            },
            {
                "fieldId": "dimensions",
                "uiDisplayName": "Dimensions of the Site",
                "fieldType": "group",
                "sortOrder": 12,
                "subFields": [
                    {"fieldId": "north_dimension", "uiDisplayName": "North (m)", "fieldType": "number", "sortOrder": 1},
                    {"fieldId": "south_dimension", "uiDisplayName": "South (m)", "fieldType": "number", "sortOrder": 2},
                    {"fieldId": "east_dimension", "uiDisplayName": "East (m)", "fieldType": "number", "sortOrder": 3},
                    {"fieldId": "west_dimension", "uiDisplayName": "West (m)", "fieldType": "number", "sortOrder": 4}
                ]
            },
            {"fieldId": "longitude", "uiDisplayName": "Longitude", "fieldType": "decimal", "isRequired": False, "sortOrder": 13},
            {"fieldId": "latitude", "uiDisplayName": "Latitude", "fieldType": "decimal", "isRequired": False, "sortOrder": 14},
            {"fieldId": "site_area", "uiDisplayName": "Site Area", "fieldType": "number_with_unit", "units": ["sqyd", "sqm", "sqft"], "isRequired": False, "sortOrder": 15},
            {"fieldId": "valuation_area", "uiDisplayName": "Valuation Area", "fieldType": "number_with_unit", "units": ["sqyd", "sqm", "sqft"], "isRequired": False, "sortOrder": 16},
            {"fieldId": "occupied_by", "uiDisplayName": "Occupied By", "fieldType": "textarea", "isRequired": False, "sortOrder": 17}
        ]
    }


def build_site_characteristics_document():
    now = datetime.now(timezone.utc).isoformat()
    return {
        "_id": str(ObjectId()),
        "templateId": "SBI_LAND_SITE_CHARACTERISTICS_V1",
        "templateName": "SBI Land Site Characteristics",
        "bankCode": "SBI",
        "propertyType": "Land",
        "templateCategory": "site_characteristics",
        "createdAt": now,
        "updatedAt": now,
        "isActive": True,
        "fields": [
            {
                "fieldId": "locality_classification",
                "technicalName": "locality_classification",
                "uiDisplayName": "Classification of Locality",
                "fieldType": "select",
                "options": [
                    {"value": "residential", "label": "Residential"},
                    {"value": "commercial", "label": "Commercial"}
                ],
                "isRequired": True,
                "sortOrder": 1
            },
            {
                "fieldId": "surrounding_area",
                "technicalName": "surrounding_area",
                "uiDisplayName": "Surrounding Area",
                "fieldType": "select",
                "options": [
                    {"value": "developed", "label": "Developed"},
                    {"value": "under_developed", "label": "Under Developed"}
                ],
                "isRequired": True,
                "sortOrder": 2
            },
            {
                "fieldId": "flooding_possibility",
                "technicalName": "flooding_possibility",
                "uiDisplayName": "Possibility of Frequent Flooding/Sub-merging",
                "fieldType": "textarea",
                "isRequired": False,
                "placeholder": "Describe flooding/sub-merging possibilities",
                "sortOrder": 3
            },
            {
                "fieldId": "civic_amenities_feasibility",
                "technicalName": "civic_amenities_feasibility",
                "uiDisplayName": "Feasibility to Civic Amenities",
                "fieldType": "textarea",
                "isRequired": False,
                "placeholder": "Describe feasibility to schools, hospitals, bus stops, markets etc.",
                "helpText": "Access to civic amenities like school, hospitals, bus stop, market etc.",
                "sortOrder": 4
            },
            {
                "fieldId": "land_level_topography",
                "technicalName": "land_level_topography",
                "uiDisplayName": "Level of Land with Topographical Conditions",
                "fieldType": "text",
                "isRequired": False,
                "placeholder": "Describe land level and topographical conditions",
                "sortOrder": 5
            },
            {
                "fieldId": "land_shape",
                "technicalName": "land_shape",
                "uiDisplayName": "Shape of Land",
                "fieldType": "text",
                "isRequired": False,
                "placeholder": "Describe the shape of the land",
                "sortOrder": 6
            },
            {
                "fieldId": "usage_type",
                "technicalName": "usage_type",
                "uiDisplayName": "Type of Use to Which it can be Put",
                "fieldType": "text",
                "isRequired": False,
                "placeholder": "Describe potential usage types",
                "sortOrder": 7
            },
            {
                "fieldId": "usage_restrictions",
                "technicalName": "usage_restrictions",
                "uiDisplayName": "Any Usage Restrictions",
                "fieldType": "text",
                "isRequired": False,
                "placeholder": "Describe any usage restrictions",
                "sortOrder": 8
            },
            {
                "fieldId": "town_planning_approved",
                "technicalName": "town_planning_approved",
                "uiDisplayName": "Is Plot in Town Planning Approved Layout?",
                "fieldType": "select",
                "options": [
                    {"value": "yes", "label": "Yes"},
                    {"value": "no", "label": "No"}
                ],
                "isRequired": True,
                "sortOrder": 9
            },
            {
                "fieldId": "corner_or_intermittent",
                "technicalName": "corner_or_intermittent",
                "uiDisplayName": "Corner or Intermittent House/Flat/Plot?",
                "fieldType": "text",
                "isRequired": False,
                "placeholder": "Specify if corner or intermittent",
                "sortOrder": 10
            },
            {
                "fieldId": "road_facilities",
                "technicalName": "road_facilities",
                "uiDisplayName": "Road Facilities",
                "fieldType": "select",
                "options": [
                    {"value": "yes", "label": "Yes"},
                    {"value": "no", "label": "No"}
                ],
                "isRequired": True,
                "sortOrder": 11
            },
            {
                "fieldId": "road_type_present",
                "technicalName": "road_type_present",
                "uiDisplayName": "Type of Road Available at Present",
                "fieldType": "text",
                "isRequired": False,
                "placeholder": "Describe the type of road available",
                "sortOrder": 12
            },
            {
                "fieldId": "road_width",
                "technicalName": "road_width",
                "uiDisplayName": "Width of Road - Below 20 ft or More than 20 ft",
                "fieldType": "text",
                "isRequired": False,
                "placeholder": "Specify road width details",
                "sortOrder": 13
            },
            {
                "fieldId": "landlocked_status",
                "technicalName": "landlocked_status",
                "uiDisplayName": "Is it a Land-locked Land?",
                "fieldType": "select",
                "options": [
                    {"value": "yes", "label": "Yes"},
                    {"value": "no", "label": "No"}
                ],
                "isRequired": True,
                "sortOrder": 14
            },
            {
                "fieldId": "water_potentiality",
                "technicalName": "water_potentiality",
                "uiDisplayName": "Water Potentiality",
                "fieldType": "select",
                "options": [
                    {"value": "yes", "label": "Yes"},
                    {"value": "no", "label": "No"}
                ],
                "isRequired": True,
                "sortOrder": 15
            },
            {
                "fieldId": "underground_sewerage",
                "technicalName": "underground_sewerage",
                "uiDisplayName": "Underground Sewerage System",
                "fieldType": "select",
                "options": [
                    {"value": "yes", "label": "Yes"},
                    {"value": "no", "label": "No"}
                ],
                "isRequired": True,
                "sortOrder": 16
            },
            {
                "fieldId": "power_supply_available",
                "technicalName": "power_supply_available",
                "uiDisplayName": "Is Power Supply Available at the Site?",
                "fieldType": "select",
                "options": [
                    {"value": "yes", "label": "Yes"},
                    {"value": "no", "label": "No"}
                ],
                "isRequired": True,
                "sortOrder": 17
            },
            {
                "fieldId": "site_advantages",
                "technicalName": "site_advantages",
                "uiDisplayName": "Advantages of the Site",
                "fieldType": "text",
                "isRequired": False,
                "placeholder": "Describe the advantages of the site",
                "sortOrder": 18
            },
            {
                "fieldId": "special_remarks",
                "technicalName": "special_remarks",
                "uiDisplayName": "Special Remarks",
                "fieldType": "text",
                "isRequired": False,
                "placeholder": "Any special remarks or additional notes",
                "sortOrder": 19
            }
        ]
    }


def build_valuation_document():
    now = datetime.now(timezone.utc).isoformat()
    return {
        "_id": str(ObjectId()),
        "templateId": "SBI_LAND_VALUATION_V1",
        "templateName": "SBI Land Valuation",
        "bankCode": "SBI",
        "propertyType": "Land",
        "templateCategory": "valuation",
        "createdAt": now,
        "updatedAt": now,
        "isActive": True,
        "sections": [
            {
                "sectionId": "part_a",
                "sectionName": "Part A - Land Valuation",
                "sortOrder": 1,
                "fields": [
                    {
                        "fieldId": "plot_size",
                        "technicalName": "plot_size",
                        "uiDisplayName": "Plot Size",
                        "fieldType": "group",
                        "sortOrder": 1,
                        "subFields": [
                            {"fieldId": "north_south_dimension", "uiDisplayName": "North & South (ft)", "fieldType": "number", "sortOrder": 1},
                            {"fieldId": "east_west_dimension", "uiDisplayName": "East & West (ft)", "fieldType": "number", "sortOrder": 2}
                        ]
                    },
                    {
                        "fieldId": "total_extent_plot",
                        "technicalName": "total_extent_plot",
                        "uiDisplayName": "Total Extent of the Plot",
                        "fieldType": "number_with_unit",
                        "units": ["sqyd", "sqm", "sqft", "acres"],
                        "isRequired": True,
                        "sortOrder": 2
                    },
                    {
                        "fieldId": "market_rate",
                        "technicalName": "market_rate",
                        "uiDisplayName": "Market Rate (Min - Max)",
                        "fieldType": "group",
                        "sortOrder": 3,
                        "subFields": [
                            {"fieldId": "market_rate_min", "uiDisplayName": "Min Rate (Rs)", "fieldType": "currency", "sortOrder": 1},
                            {"fieldId": "market_rate_max", "uiDisplayName": "Max Rate (Rs)", "fieldType": "currency", "sortOrder": 2}
                        ]
                    },
                    {
                        "fieldId": "registrar_rate",
                        "technicalName": "registrar_rate",
                        "uiDisplayName": "Registrar's Rate",
                        "fieldType": "currency",
                        "isRequired": True,
                        "placeholder": "Enter amount in Rs",
                        "sortOrder": 4
                    },
                    {
                        "fieldId": "valuation_rate",
                        "technicalName": "valuation_rate",
                        "uiDisplayName": "Valuation Rate",
                        "fieldType": "currency",
                        "isRequired": True,
                        "placeholder": "Enter amount in Rs",
                        "sortOrder": 5
                    },
                    {
                        "fieldId": "estimated_land_value",
                        "technicalName": "estimated_land_value",
                        "uiDisplayName": "Estimated Value of Land",
                        "fieldType": "calculated",
                        "formula": "total_extent_plot * valuation_rate",
                        "displayFormat": "currency",
                        "isReadonly": True,
                        "sortOrder": 6
                    }
                ]
            },
            {
                "sectionId": "part_b",
                "sectionName": "Part B - Building Details",
                "sortOrder": 2,
                "fields": [
                    {
                        "fieldId": "building_type",
                        "technicalName": "building_type",
                        "uiDisplayName": "Type of Building",
                        "fieldType": "select",
                        "options": [
                            {"value": "residential", "label": "Residential"},
                            {"value": "commercial", "label": "Commercial"},
                            {"value": "industrial", "label": "Industrial"}
                        ],
                        "isRequired": True,
                        "sortOrder": 1
                    },
                    {
                        "fieldId": "construction_type",
                        "technicalName": "construction_type",
                        "uiDisplayName": "Type of Construction",
                        "fieldType": "text",
                        "placeholder": "Describe construction type",
                        "sortOrder": 2
                    },
                    {
                        "fieldId": "construction_year",
                        "technicalName": "construction_year",
                        "uiDisplayName": "Year of Construction",
                        "fieldType": "year",
                        "validation": {"min": 1900, "max": 2030},
                        "sortOrder": 3
                    },
                    {
                        "fieldId": "number_of_floors",
                        "technicalName": "number_of_floors",
                        "uiDisplayName": "Number of Floors",
                        "fieldType": "number",
                        "validation": {"min": 1, "max": 50},
                        "sortOrder": 4
                    },
                    {
                        "fieldId": "floor_height",
                        "technicalName": "floor_height",
                        "uiDisplayName": "Height of Floors (ft)",
                        "fieldType": "number",
                        "placeholder": "Enter height in feet",
                        "sortOrder": 5
                    },
                    {
                        "fieldId": "plinth_area_floorwise",
                        "technicalName": "plinth_area_floorwise",
                        "uiDisplayName": "Plinth Area Floor-wise",
                        "fieldType": "number",
                        "placeholder": "Enter plinth area",
                        "sortOrder": 6
                    },
                    {
                        "fieldId": "building_condition",
                        "technicalName": "building_condition",
                        "uiDisplayName": "Condition of the Building",
                        "fieldType": "group",
                        "sortOrder": 7,
                        "subFields": [
                            {"fieldId": "exterior_condition", "uiDisplayName": "Exterior", "fieldType": "select", "options": [
                                {"value": "excellent", "label": "Excellent"},
                                {"value": "good", "label": "Good"},
                                {"value": "normal", "label": "Normal"},
                                {"value": "poor", "label": "Poor"}
                            ], "sortOrder": 1},
                            {"fieldId": "interior_condition", "uiDisplayName": "Interior", "fieldType": "select", "options": [
                                {"value": "excellent", "label": "Excellent"},
                                {"value": "good", "label": "Good"},
                                {"value": "normal", "label": "Normal"},
                                {"value": "poor", "label": "Poor"}
                            ], "sortOrder": 2}
                        ]
                    },
                    {
                        "fieldId": "approved_map_date_validity",
                        "technicalName": "approved_map_date_validity",
                        "uiDisplayName": "Date of Issue and Validity of Layout/Approved Map/Plan",
                        "fieldType": "text",
                        "placeholder": "Enter date and validity details",
                        "sortOrder": 8
                    },
                    {
                        "fieldId": "approved_map_authority",
                        "technicalName": "approved_map_authority",
                        "uiDisplayName": "Approved Map/Plan Issuing Authority",
                        "fieldType": "text",
                        "placeholder": "Enter issuing authority",
                        "sortOrder": 9
                    },
                    {
                        "fieldId": "map_authenticity_verified",
                        "technicalName": "map_authenticity_verified",
                        "uiDisplayName": "Genuineness/Authenticity of Approved Map/Plan Verified",
                        "fieldType": "text",
                        "placeholder": "Enter verification details",
                        "sortOrder": 10
                    },
                    {
                        "fieldId": "valuer_comments_authenticity",
                        "technicalName": "valuer_comments_authenticity",
                        "uiDisplayName": "Valuer Comments on Plan Authenticity",
                        "fieldType": "text",
                        "placeholder": "Any other comments by empanelled valuers",
                        "sortOrder": 11
                    }
                ]
            }
        ]
    }


def build_construction_specifications_document():
    now = datetime.now(timezone.utc).isoformat()
    return {
        "_id": str(ObjectId()),
        "templateId": "SBI_LAND_CONSTRUCTION_SPECS_V1",
        "templateName": "SBI Land Construction Specifications",
        "bankCode": "SBI",
        "propertyType": "Land",
        "templateCategory": "construction_specifications",
        "createdAt": now,
        "updatedAt": now,
        "isActive": True,
        "fields": [
            {"fieldId": "foundation", "technicalName": "foundation", "uiDisplayName": "Foundation", "fieldType": "text", "sortOrder": 1},
            {"fieldId": "basement", "technicalName": "basement", "uiDisplayName": "Basement", "fieldType": "text", "sortOrder": 2},
            {"fieldId": "superstructure", "technicalName": "superstructure", "uiDisplayName": "Superstructure", "fieldType": "text", "sortOrder": 3},
            {"fieldId": "joinery_doors_windows", "technicalName": "joinery_doors_windows", "uiDisplayName": "Joinery/Doors & Windows", "fieldType": "textarea", "helpText": "Details about size of frames, shutters, glazing, fitting etc. and timber species", "sortOrder": 4},
            {"fieldId": "rcc_works", "technicalName": "rcc_works", "uiDisplayName": "RCC Works", "fieldType": "text", "sortOrder": 5},
            {"fieldId": "plastering", "technicalName": "plastering", "uiDisplayName": "Plastering", "fieldType": "text", "sortOrder": 6},
            {"fieldId": "flooring_skirting_dadoing", "technicalName": "flooring_skirting_dadoing", "uiDisplayName": "Flooring, Skirting, Dadoing", "fieldType": "text", "sortOrder": 7},
            {"fieldId": "special_finish", "technicalName": "special_finish", "uiDisplayName": "Special Finish", "fieldType": "text", "helpText": "Marble, granite, wooden paneling, grills, etc.", "sortOrder": 8},
            {"fieldId": "roofing_weatherproof", "technicalName": "roofing_weatherproof", "uiDisplayName": "Roofing including Weather Proof Course", "fieldType": "text", "sortOrder": 9},
            {"fieldId": "drainage", "technicalName": "drainage", "uiDisplayName": "Drainage", "fieldType": "text", "sortOrder": 10},
            {"fieldId": "compound_wall", "technicalName": "compound_wall", "uiDisplayName": "Compound Wall", "fieldType": "text", "sortOrder": 11},
            {"fieldId": "height", "technicalName": "height", "uiDisplayName": "Height", "fieldType": "text", "sortOrder": 12},
            {"fieldId": "length", "technicalName": "length", "uiDisplayName": "Length", "fieldType": "text", "sortOrder": 13},
            {"fieldId": "construction_type", "technicalName": "construction_type", "uiDisplayName": "Type of Construction", "fieldType": "text", "sortOrder": 14},
            {
                "fieldId": "electrical_installation",
                "technicalName": "electrical_installation",
                "uiDisplayName": "Electrical Installation",
                "fieldType": "group",
                "sortOrder": 15,
                "subFields": [
                    {"fieldId": "wiring_type", "uiDisplayName": "Type of Wiring", "fieldType": "text", "sortOrder": 1},
                    {"fieldId": "fittings_class", "uiDisplayName": "Class of Fittings", "fieldType": "select", "options": [
                        {"value": "superior", "label": "Superior"},
                        {"value": "ordinary", "label": "Ordinary"},
                        {"value": "poor", "label": "Poor"}
                    ], "sortOrder": 2},
                    {"fieldId": "fan_points", "uiDisplayName": "Fan Points", "fieldType": "number", "sortOrder": 3},
                    {"fieldId": "spare_plug_points", "uiDisplayName": "Spare Plug Points", "fieldType": "number", "sortOrder": 4}
                ]
            },
            {
                "fieldId": "plumbing_installation",
                "technicalName": "plumbing_installation",
                "uiDisplayName": "Plumbing Installation",
                "fieldType": "group",
                "sortOrder": 16,
                "subFields": [
                    {"fieldId": "water_closets", "uiDisplayName": "No. of Water Closets and Type", "fieldType": "text", "sortOrder": 1},
                    {"fieldId": "wash_basins", "uiDisplayName": "No. of Wash Basins", "fieldType": "number", "sortOrder": 2},
                    {"fieldId": "urinals", "uiDisplayName": "No. of Urinals", "fieldType": "number", "sortOrder": 3},
                    {"fieldId": "bath_tubs", "uiDisplayName": "No. of Bath Tubs", "fieldType": "number", "sortOrder": 4},
                    {"fieldId": "water_meter_taps", "uiDisplayName": "Water Meter, Taps, etc.", "fieldType": "text", "sortOrder": 5},
                    {"fieldId": "other_fixtures_sink", "uiDisplayName": "Other Fixtures - Sink", "fieldType": "text", "sortOrder": 6}
                ]
            }
        ]
    }


def build_detailed_valuation_document():
    now = datetime.now(timezone.utc).isoformat()
    return {
        "_id": str(ObjectId()),
        "templateId": "SBI_LAND_DETAILED_VALUATION_V1",
        "templateName": "SBI Land Detailed Valuation",
        "bankCode": "SBI",
        "propertyType": "Land",
        "templateCategory": "detailed_valuation",
        "createdAt": now,
        "updatedAt": now,
        "isActive": True,
        "sections": [
            {
                "sectionId": "extra_items",
                "sectionName": "Extra Items",
                "sortOrder": 1,
                "fields": [
                    {"fieldId": "portico", "technicalName": "portico", "uiDisplayName": "Portico", "fieldType": "currency", "placeholder": "Amount in Rs", "sortOrder": 1},
                    {"fieldId": "ornamental_front_door", "technicalName": "ornamental_front_door", "uiDisplayName": "Ornamental Front Door", "fieldType": "currency", "placeholder": "Amount in Rs", "sortOrder": 2},
                    {"fieldId": "sitout_verandah_grills", "technicalName": "sitout_verandah_grills", "uiDisplayName": "Sit out/Verandah with Steel Grills", "fieldType": "currency", "placeholder": "Amount in Rs", "sortOrder": 3},
                    {"fieldId": "overhead_water_tank", "technicalName": "overhead_water_tank", "uiDisplayName": "Overhead Water Tank", "fieldType": "currency", "placeholder": "Amount in Rs", "sortOrder": 4},
                    {"fieldId": "extra_steel_gates", "technicalName": "extra_steel_gates", "uiDisplayName": "Extra Steel/Collapsible Gates", "fieldType": "currency", "placeholder": "Amount in Rs", "sortOrder": 5}
                ]
            },
            {
                "sectionId": "amenities",
                "sectionName": "Amenities",
                "sortOrder": 2,
                "fields": [
                    {"fieldId": "wardrobes", "technicalName": "wardrobes", "uiDisplayName": "Wardrobes", "fieldType": "currency", "placeholder": "Amount in Rs", "sortOrder": 1},
                    {"fieldId": "glazed_tiles", "technicalName": "glazed_tiles", "uiDisplayName": "Glazed Tiles", "fieldType": "currency", "placeholder": "Amount in Rs", "sortOrder": 2},
                    {"fieldId": "extra_sinks_bathtubs", "technicalName": "extra_sinks_bathtubs", "uiDisplayName": "Extra Sinks & Bath Tubs", "fieldType": "currency", "placeholder": "Amount in Rs", "sortOrder": 3},
                    {"fieldId": "marble_ceramic_flooring", "technicalName": "marble_ceramic_flooring", "uiDisplayName": "Marble/Ceramic Tiles Flooring", "fieldType": "currency", "placeholder": "Amount in Rs", "sortOrder": 4},
                    {"fieldId": "interior_decorations", "technicalName": "interior_decorations", "uiDisplayName": "Interior Decorations", "fieldType": "currency", "placeholder": "Amount in Rs", "sortOrder": 5},
                    {"fieldId": "architectural_elevation", "technicalName": "architectural_elevation", "uiDisplayName": "Architectural Elevation Works", "fieldType": "currency", "placeholder": "Amount in Rs", "sortOrder": 6},
                    {"fieldId": "paneling_works", "technicalName": "paneling_works", "uiDisplayName": "Paneling Works", "fieldType": "currency", "placeholder": "Amount in Rs", "sortOrder": 7},
                    {"fieldId": "aluminum_works", "technicalName": "aluminum_works", "uiDisplayName": "Aluminum Works", "fieldType": "currency", "placeholder": "Amount in Rs", "sortOrder": 8},
                    {"fieldId": "aluminum_handrails", "technicalName": "aluminum_handrails", "uiDisplayName": "Aluminum Hand Rails", "fieldType": "currency", "placeholder": "Amount in Rs", "sortOrder": 9},
                    {"fieldId": "false_ceiling", "technicalName": "false_ceiling", "uiDisplayName": "False Ceiling", "fieldType": "currency", "placeholder": "Amount in Rs", "sortOrder": 10}
                ]
            },
            {
                "sectionId": "miscellaneous",
                "sectionName": "Miscellaneous",
                "sortOrder": 3,
                "fields": [
                    {"fieldId": "separate_toilet", "technicalName": "separate_toilet", "uiDisplayName": "Separate Toilet Room", "fieldType": "currency", "placeholder": "Amount in Rs", "sortOrder": 1},
                    {"fieldId": "separate_lumber_room", "technicalName": "separate_lumber_room", "uiDisplayName": "Separate Lumber Room", "fieldType": "currency", "placeholder": "Amount in Rs", "sortOrder": 2},
                    {"fieldId": "separate_water_tank_sump", "technicalName": "separate_water_tank_sump", "uiDisplayName": "Separate Water Tank/Sump", "fieldType": "currency", "placeholder": "Amount in Rs", "sortOrder": 3},
                    {"fieldId": "trees_gardening", "technicalName": "trees_gardening", "uiDisplayName": "Trees, Gardening", "fieldType": "currency", "placeholder": "Amount in Rs", "sortOrder": 4}
                ]
            },
            {
                "sectionId": "services",
                "sectionName": "Services",
                "sortOrder": 4,
                "fields": [
                    {"fieldId": "water_supply_arrangements", "technicalName": "water_supply_arrangements", "uiDisplayName": "Water Supply Arrangements", "fieldType": "currency", "placeholder": "Amount in Rs", "sortOrder": 1},
                    {"fieldId": "drainage_arrangements", "technicalName": "drainage_arrangements", "uiDisplayName": "Drainage Arrangements", "fieldType": "currency", "placeholder": "Amount in Rs", "sortOrder": 2},
                    {"fieldId": "compound_wall", "technicalName": "compound_wall", "uiDisplayName": "Compound Wall", "fieldType": "currency", "placeholder": "Amount in Rs", "sortOrder": 3},
                    {"fieldId": "cb_deposits_fittings", "technicalName": "cb_deposits_fittings", "uiDisplayName": "C.B. Deposits, Fittings etc.", "fieldType": "currency", "placeholder": "Amount in Rs", "sortOrder": 4},
                    {"fieldId": "pavement", "technicalName": "pavement", "uiDisplayName": "Pavement", "fieldType": "currency", "placeholder": "Amount in Rs", "sortOrder": 5}
                ]
            },
            {
                "sectionId": "total",
                "sectionName": "Total Valuation",
                "sortOrder": 5,
                "fields": [
                    {"fieldId": "land_total", "technicalName": "land_total", "uiDisplayName": "Land", "fieldType": "currency", "placeholder": "Amount in Rs", "sortOrder": 1},
                    {"fieldId": "building_total", "technicalName": "building_total", "uiDisplayName": "Building", "fieldType": "currency", "placeholder": "Amount in Rs", "sortOrder": 2},
                    {"fieldId": "extra_items_total", "technicalName": "extra_items_total", "uiDisplayName": "Extra Items", "fieldType": "calculated", "formula": "sum_section_extra_items", "displayFormat": "currency", "isReadonly": True, "sortOrder": 3},
                    {"fieldId": "amenities_total", "technicalName": "amenities_total", "uiDisplayName": "Amenities", "fieldType": "calculated", "formula": "sum_section_amenities", "displayFormat": "currency", "isReadonly": True, "sortOrder": 4},
                    {"fieldId": "miscellaneous_total", "technicalName": "miscellaneous_total", "uiDisplayName": "Miscellaneous", "fieldType": "calculated", "formula": "sum_section_miscellaneous", "displayFormat": "currency", "isReadonly": True, "sortOrder": 5},
                    {"fieldId": "services_total", "technicalName": "services_total", "uiDisplayName": "Services", "fieldType": "calculated", "formula": "sum_section_services", "displayFormat": "currency", "isReadonly": True, "sortOrder": 6},
                    {"fieldId": "grand_total", "technicalName": "grand_total", "uiDisplayName": "Total", "fieldType": "calculated", "formula": "land_total + building_total + extra_items_total + amenities_total + miscellaneous_total + services_total", "displayFormat": "currency", "isReadonly": True, "sortOrder": 7}
                ]
            }
        ]
    }


def main():
    client = None
    try:
        client = MongoClient(MONGODB_URI, tlsAllowInvalidCertificates=True)
        db = client['valuation_admin']
        collection = db['sbi_land_property_details']

        print('Clearing existing documents in sbi_land_property_details collection...')
        collection.delete_many({})

        # Build all five documents
        property_details_doc = build_property_details_document()
        site_characteristics_doc = build_site_characteristics_document()
        valuation_doc = build_valuation_document()
        construction_specs_doc = build_construction_specifications_document()
        detailed_valuation_doc = build_detailed_valuation_document()
        
        # Insert all documents
        collection.insert_one(property_details_doc)
        collection.insert_one(site_characteristics_doc)
        collection.insert_one(valuation_doc)
        collection.insert_one(construction_specs_doc)
        collection.insert_one(detailed_valuation_doc)

        # Write to JSON file
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "collection_name": "sbi_land_property_details",
                    "total_documents": 5,
                    "version": "1.0",
                    "database": "valuation_admin",
                    "source": "recreate_script"
                },
                "documents": [
                    property_details_doc, 
                    site_characteristics_doc, 
                    valuation_doc, 
                    construction_specs_doc, 
                    detailed_valuation_doc
                ]
            }, f, indent=2, ensure_ascii=False)

        print('Recreated collection and wrote JSON file successfully.')

    except Exception as e:
        print('Error:', e)
    finally:
        if client:
            client.close()

if __name__ == '__main__':
    main()