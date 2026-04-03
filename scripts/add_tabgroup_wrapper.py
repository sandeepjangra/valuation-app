#!/usr/bin/env python3
"""
MongoDB Migration Script: Add TabGroup Wrapper
-----------------------------------------------
This script wraps all top-level Tab containers in a TabGroup container.

Current structure:
- input fields
- Tab: Property Details
- Tab: Site Characteristics
- Tab: Valuation
...

Target structure:
- input fields
- TabGroup: Bank Specific Details
  ├─ Tab: Property Details
  ├─ Tab: Site Characteristics
  ├─ Tab: Valuation
  ...

Usage:
    python scripts/add_tabgroup_wrapper.py
"""

import os
import sys
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = 'valuation_templates'
COLLECTION_NAME = 'templates'


def connect_to_mongodb():
    """Connect to MongoDB and return database instance"""
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print(f"✅ Connected to MongoDB at {MONGODB_URI}")
        return client[DATABASE_NAME]
    except ConnectionFailure as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        sys.exit(1)


def add_tabgroup_wrapper(template_id, db):
    """Add TabGroup wrapper around all Tab containers"""
    print(f"\n📄 Processing template: {template_id}")
    
    collection = db[COLLECTION_NAME]
    template = collection.find_one({"TemplateId": template_id})
    
    if not template:
        print(f"  ⚠️  Template '{template_id}' not found")
        return False
    
    elements = template.get("Elements", [])
    if not elements:
        print(f"  ⚠️  No elements found")
        return False
    
    # Separate common fields (inputs) from tabs
    common_fields = []
    tabs = []
    other_elements = []
    
    for elem in elements:
        elem_type = elem.get("$type")
        container = elem.get("Container")
        
        if elem_type == "input":
            common_fields.append(elem)
        elif elem_type == "container" and container == "Tab":
            tabs.append(elem)
        else:
            other_elements.append(elem)
    
    print(f"  Found: {len(common_fields)} common fields, {len(tabs)} tabs, {len(other_elements)} other elements")
    
    if len(tabs) == 0:
        print(f"  ℹ️  No tabs to wrap - skipping")
        return False
    
    # Check if TabGroup already exists
    for elem in elements:
        if elem.get("$type") == "container" and elem.get("Container") == "TabGroup":
            print(f"  ℹ️  TabGroup already exists - skipping")
            return False
    
    # Create TabGroup container
    tabgroup = {
        "$type": "container",
        "Container": "TabGroup",
        "FieldId": "bank_specific_details",
        "Label": "Bank Specific Details",
        "DisplayOrder": len(common_fields) + 1,
        "IsVisible": True,
        "Children": tabs
    }
    
    # Update DisplayOrder for tabs inside TabGroup (starting from 1)
    for i, tab in enumerate(tabs, start=1):
        tab["DisplayOrder"] = i
    
    # Rebuild elements array
    new_elements = common_fields + [tabgroup] + other_elements
    
    # Update DisplayOrder for all top-level elements
    for i, elem in enumerate(new_elements, start=1):
        elem["DisplayOrder"] = i
    
    # Update template
    template["Elements"] = new_elements
    template["UpdatedAt"] = datetime.utcnow()
    
    result = collection.replace_one(
        {"TemplateId": template_id},
        template
    )
    
    if result.modified_count > 0:
        print(f"  ✅ Successfully wrapped {len(tabs)} tabs in TabGroup")
        return True
    else:
        print(f"  ℹ️  No changes made")
        return False


def verify_structure(template_id, db):
    """Verify TabGroup structure"""
    print(f"\n🔍 Verifying structure for: {template_id}")
    
    collection = db[COLLECTION_NAME]
    template = collection.find_one({"TemplateId": template_id})
    
    if not template:
        print(f"  ❌ Template not found")
        return False
    
    elements = template.get("Elements", [])
    
    # Find TabGroup
    tabgroup = None
    for elem in elements:
        if elem.get("$type") == "container" and elem.get("Container") == "TabGroup":
            tabgroup = elem
            break
    
    if not tabgroup:
        print(f"  ❌ TabGroup not found")
        return False
    
    children = tabgroup.get("Children", [])
    tabs = [c for c in children if c.get("$type") == "container" and c.get("Container") == "Tab"]
    
    print(f"  ✅ TabGroup found with {len(tabs)} tabs:")
    for i, tab in enumerate(tabs, start=1):
        print(f"     {i}. {tab.get('Label', 'unknown')}")
    
    return True


def main():
    print("=" * 70)
    print("MongoDB Migration: Add TabGroup Wrapper")
    print("=" * 70)
    
    # Connect to MongoDB
    db = connect_to_mongodb()
    
    # Get all templates
    collection = db[COLLECTION_NAME]
    templates = list(collection.find({}, {"TemplateId": 1, "_id": 0}))
    
    if not templates:
        print("\n⚠️  No templates found in database")
        return
    
    print(f"\n📋 Found {len(templates)} template(s) to process:")
    for tmpl in templates:
        print(f"  - {tmpl['TemplateId']}")
    
    # Confirm migration
    print(f"\n⚠️  This will wrap all Tab containers in a TabGroup container")
    response = input("Continue with migration? (yes/no): ")
    
    if response.lower() not in ['yes', 'y']:
        print("\n❌ Migration cancelled")
        return
    
    # Process each template
    print("\n" + "=" * 70)
    print("Starting Migration")
    print("=" * 70)
    
    migrated_count = 0
    for tmpl in templates:
        template_id = tmpl['TemplateId']
        if add_tabgroup_wrapper(template_id, db):
            migrated_count += 1
            verify_structure(template_id, db)
    
    # Summary
    print("\n" + "=" * 70)
    print("Migration Summary")
    print("=" * 70)
    print(f"Total templates: {len(templates)}")
    print(f"Migrated: {migrated_count}")
    print(f"Skipped: {len(templates) - migrated_count}")
    print("\n✅ Migration complete!")


if __name__ == "__main__":
    main()
