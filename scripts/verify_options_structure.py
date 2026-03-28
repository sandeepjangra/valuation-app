#!/usr/bin/env python3
"""
Quick script to verify that FieldOption data exists in MongoDB
and print the exact structure of one field with options
"""

from pymongo import MongoClient
import os
import json

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster")

client = MongoClient(MONGODB_URI)
db = client.valuation_templates
templates = db.templates

# Find the SBI Land template
template = templates.find_one({"TemplateId": "SBI_LAND_TEMPLATE_V1"})

if not template:
    print("Template not found!")
    exit(1)

print(f"Template ID: {template['TemplateId']}")
print(f"Total Elements: {len(template.get('Elements', []))}")

# Find the valuation_purpose field
valuation_purpose = None
for element in template.get("Elements", []):
    if element.get("FieldId") == "valuation_purpose":
        valuation_purpose = element
        break

if valuation_purpose:
    print(f"\nFound valuation_purpose field:")
    print(f"Type: {valuation_purpose.get('$type')}")
    print(f"FieldId: {valuation_purpose.get('FieldId')}")
    print(f"Label: {valuation_purpose.get('Label')}")
    print(f"Options present: {'Options' in valuation_purpose}")
    
    if 'Options' in valuation_purpose:
        options = valuation_purpose['Options']
        print(f"Options count: {len(options)}")
        print(f"Options type: {type(options)}")
        print(f"\nFirst 3 options (raw):")
        for i, opt in enumerate(options[:3]):
            print(f"\nOption {i}:")
            print(f"  Type: {type(opt)}")
            print(f"  Keys: {opt.keys() if isinstance(opt, dict) else 'N/A'}")
            print(f"  Raw: {opt}")
else:
    print("\nvaluation_purpose field not found in template!")

client.close()
