#!/usr/bin/env python3
"""
MongoDB Migration Script: Convert to Container Structure
---------------------------------------------------------
This script migrates templates from the old structure to the new container-based structure:
- Changes $type from "tab", "section", "group", "tabgroup" to "container"
- Adds "container" property with string values: "Tab", "Section", "Group", "TabGroup"
- Adds initial rows data to boundaries_dimensions_table

Usage:
    python scripts/migrate_to_container_structure.py
"""

import os
import sys
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# MongoDB connection string - update if needed
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = 'valuation_templates'  # Correct database name
COLLECTION_NAME = 'templates'


def connect_to_mongodb():
    """Connect to MongoDB and return database instance"""
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        # Verify connection
        client.admin.command('ping')
        print(f"✅ Connected to MongoDB at {MONGODB_URI}")
        return client[DATABASE_NAME]
    except ConnectionFailure as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        sys.exit(1)


def transform_element(element):
    """
    Recursively transform an element from old structure to new structure
    
    Old: {"$type": "tab", ...}
    New: {"$type": "container", "container": "Tab", ...}
    """
    if not isinstance(element, dict):
        return element
    
    # Map old $type values to new container values
    type_mapping = {
        "tab": "Tab",
        "section": "Section", 
        "group": "Group",
        "tabgroup": "TabGroup"
    }
    
    # Check if this element needs transformation
    current_type = element.get("$type")
    
    if current_type in type_mapping:
        print(f"  🔄 Transforming: {element.get('fieldId', 'unknown')} from $type='{current_type}' to container='{type_mapping[current_type]}'")
        # Transform to new structure
        element["$type"] = "container"
        element["container"] = type_mapping[current_type]
    elif current_type == "container" and "container" not in element:
        # Handle case where $type is already "container" but container property is missing
        # Try to infer from fieldType or skip
        print(f"  ⚠️  Element {element.get('fieldId', 'unknown')} has $type='container' but no container property - needs manual review")

    
    # Handle boundaries table - add initial rows (check both PascalCase and camelCase)
    field_id = element.get("FieldId") or element.get("fieldId")
    if field_id == "boundaries_dimensions_table":
        print(f"  📊 Adding rows to boundaries_dimensions_table")
        # Use PascalCase for MongoDB (it will be converted to camelCase by C# backend)
        element["Rows"] = [
            {
                "direction": "North",
                "boundaries_per_documents": "",
                "boundaries_actual": "",
                "dimensions_per_documents": "",
                "dimensions_actuals": ""
            },
            {
                "direction": "South",
                "boundaries_per_documents": "",
                "boundaries_actual": "",
                "dimensions_per_documents": "",
                "dimensions_actuals": ""
            },
            {
                "direction": "East",
                "boundaries_per_documents": "",
                "boundaries_actual": "",
                "dimensions_per_documents": "",
                "dimensions_actuals": ""
            },
            {
                "direction": "West",
                "boundaries_per_documents": "",
                "boundaries_actual": "",
                "dimensions_per_documents": "",
                "dimensions_actuals": ""
            }
        ]
    
    # Recursively process children (check both PascalCase and camelCase)
    children = element.get("Children") or element.get("children")
    if children and isinstance(children, list):
        transformed_children = [transform_element(child) for child in children]
        # Keep the same case as original
        if "Children" in element:
            element["Children"] = transformed_children
        elif "children" in element:
            element["children"] = transformed_children
    
    return element


def migrate_template(db, template_id):
    """Migrate a single template"""
    print(f"\n📄 Migrating template: {template_id}")
    
    collection = db[COLLECTION_NAME]
    
    # Find the template (using PascalCase field name)
    template = collection.find_one({"TemplateId": template_id})
    
    if not template:
        print(f"  ⚠️  Template '{template_id}' not found")
        return False
    
    # Transform all elements (using PascalCase field name)
    if "Elements" in template and isinstance(template["Elements"], list):
        print(f"  Processing {len(template['Elements'])} top-level elements...")
        template["Elements"] = [transform_element(elem) for elem in template["Elements"]]
    
    # Update the template (using PascalCase field name)
    template["UpdatedAt"] = datetime.utcnow()
    
    result = collection.replace_one(
        {"TemplateId": template_id},
        template
    )
    
    if result.modified_count > 0:
        print(f"  ✅ Template '{template_id}' migrated successfully")
        return True
    else:
        print(f"  ℹ️  Template '{template_id}' - no changes needed")
        return False


def verify_migration(db, template_id):
    """Verify that migration was successful"""
    print(f"\n🔍 Verifying migration for: {template_id}")
    
    collection = db[COLLECTION_NAME]
    template = collection.find_one({"TemplateId": template_id})
    
    if not template:
        print(f"  ❌ Template not found")
        return False
    
    # Check for old structure
    def check_elements(elements, path=""):
        issues = []
        for i, elem in enumerate(elements):
            if not isinstance(elem, dict):
                continue
                
            elem_path = f"{path}[{i}].{elem.get('FieldId') or elem.get('fieldId', 'unknown')}"
            elem_type = elem.get("$type")
            
            # Check for old types
            if elem_type in ["tab", "section", "group", "tabgroup"]:
                issues.append(f"Found old $type '{elem_type}' at {elem_path}")
            
            # Check containers have container property (check both PascalCase and camelCase)
            if elem_type == "container":
                if "Container" not in elem and "container" not in elem:
                    issues.append(f"Missing 'container' property at {elem_path}")
            
            # Recursively check children (check both PascalCase and camelCase)
            children = elem.get("Children") or elem.get("children")
            if children and isinstance(children, list):
                issues.extend(check_elements(children, elem_path))
        
        return issues
    
    issues = check_elements(template.get("Elements", []))
    
    if issues:
        print(f"  ❌ Verification failed:")
        for issue in issues:
            print(f"    - {issue}")
        return False
    
    # Check if boundaries table has rows
    def find_boundaries_table(elements):
        for elem in elements:
            if not isinstance(elem, dict):
                continue
            if elem.get("fieldId") == "boundaries_dimensions_table":
                return elem
            if "children" in elem:
                result = find_boundaries_table(elem["children"])
                if result:
                    return result
        return None
    
    boundaries_table = find_boundaries_table(template.get("elements", []))
    if boundaries_table:
        rows = boundaries_table.get("rows", [])
        if rows and len(rows) == 4:
            print(f"  ✅ Boundaries table has {len(rows)} rows")
        else:
            print(f"  ⚠️  Boundaries table has {len(rows)} rows (expected 4)")
    
    print(f"  ✅ Migration verified successfully")
    return True


def main():
    """Main migration function"""
    print("=" * 70)
    print("MongoDB Template Migration: Container Structure")
    print("=" * 70)
    
    # Connect to MongoDB
    db = connect_to_mongodb()
    
    # Get all templates (using PascalCase field name)
    collection = db[COLLECTION_NAME]
    templates = list(collection.find({}, {"TemplateId": 1, "_id": 0}))
    
    if not templates:
        print("\n⚠️  No templates found in database")
        return
    
    print(f"\n📋 Found {len(templates)} template(s) to migrate:")
    for tmpl in templates:
        print(f"  - {tmpl['TemplateId']}")
    
    # Confirm migration
    print(f"\n⚠️  This will modify templates in place (no backup)")
    response = input("Continue with migration? (yes/no): ")
    
    if response.lower() not in ['yes', 'y']:
        print("\n❌ Migration cancelled")
        return
    
    # Migrate each template
    print("\n" + "=" * 70)
    print("Starting Migration")
    print("=" * 70)
    
    migrated_count = 0
    for tmpl in templates:
        template_id = tmpl['TemplateId']  # Using PascalCase field name
        if migrate_template(db, template_id):
            migrated_count += 1
            verify_migration(db, template_id)
    
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
