#!/usr/bin/env python3
"""
Batch Migration Script - Migrate All Templates to New C# Structure
This script migrates all bank templates from MongoDB to the new unified structure
"""

import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
import json
from datetime import datetime
import re

# Load environment variables
load_dotenv()

# Template collection mapping
TEMPLATES_TO_MIGRATE = [
    # Already done: ('sbi_land_property_details', 'SBI_LAND_TEMPLATE_V1'),
    ('sbi_apartment_property_details', 'SBI_APARTMENT_TEMPLATE_V1'),
    ('bob_land_property_details', 'BOB_LAND_TEMPLATE_V1'),
    ('boi_land_property_details', 'BOI_LAND_TEMPLATE_V1'),
    ('boi_apartment_property_details', 'BOI_APARTMENT_TEMPLATE_V1'),
    ('uco_land_property_details', 'UCO_LAND_TEMPLATE_V1'),
    ('uco_apartment_property_details', 'UCO_APARTMENT_TEMPLATE_V1'),
    ('ubi_land_property_details', 'UBI_LAND_TEMPLATE_V1'),
    ('ubi_apartment_property_details', 'UBI_APARTMENT_TEMPLATE_V1'),
    ('pnb_land_property_details', 'PNB_ALL_TEMPLATE_V1'),
    ('cbi_all_property_details', 'CBI_ALL_TEMPLATE_V1'),
    ('hdfc_all_property_details', 'HDFC_ALL_TEMPLATE_V1'),
]

def connect_to_mongodb():
    """Connect to MongoDB Atlas"""
    mongo_uri = os.getenv('MONGODB_URI')
    if not mongo_uri:
        print("❌ MONGODB_URI not found in environment variables")
        sys.exit(1)
    
    try:
        client = MongoClient(mongo_uri)
        client.admin.command('ping')
        return client
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        sys.exit(1)

def map_field_type(old_type):
    """Map old field types to new C# types"""
    type_mapping = {
        'text': 'Text',
        'textarea': 'Text',
        'number': 'Number',
        'currency': 'Number',
        'date': 'Date',
        'dropdown': 'Dropdown',
        'radio': 'Radio',
        'checkbox': 'Checkbox',
        'file': 'File',
        'signature': 'Signature',
    }
    return type_mapping.get(old_type, 'Text')

def extract_calculation_rules(fields, depth=0):
    """Extract calculation rules from fields with formulas"""
    rules = []
    
    for field in fields:
        # Check if field has formula
        if field.get('formula'):
            formula = field['formula']
            field_id = field.get('fieldId', '')
            
            # Extract dependencies from formula
            dependencies = re.findall(r'\b[a-z_]+[a-z0-9_]*\b', formula)
            dependencies = [d for d in dependencies if d != field_id]
            
            rule = {
                'RuleId': f"calc_{field_id}",
                'TriggerFieldIds': dependencies,
                'Formula': formula,
                'TargetFieldId': field_id,
                'Description': field.get('calculationMetadata', {}).get('description', 
                                        f"Calculate {field.get('label', field_id)}")
            }
            rules.append(rule)
        
        # Check subFields (nested fields)
        if field.get('subFields'):
            rules.extend(extract_calculation_rules(field['subFields'], depth + 1))
        
        # Check table columns
        if field.get('fieldType') == 'table' and field.get('columns'):
            rules.extend(extract_calculation_rules(field['columns'], depth + 1))
    
    return rules

def transform_field_to_input(field):
    """Transform a field to InputField format"""
    input_field = {
        '$type': 'input',
        'FieldId': field.get('fieldId', ''),
        'Label': field.get('label', ''),
        'SpecificType': map_field_type(field.get('fieldType', 'text')),
        'DisplayOrder': field.get('displayOrder', 1),
        'IsRequired': field.get('required', False),
        'IsVisible': field.get('visible', True),
        'DefaultValue': field.get('defaultValue'),
        'HelpText': field.get('helpText'),
        'PlaceholderText': field.get('placeholder')
    }
    
    # Add options for dropdown/radio
    if field.get('options'):
        input_field['Options'] = field['options']
    
    # Mark as readonly if has formula
    if field.get('formula'):
        input_field['IsReadonly'] = True
    
    return input_field

def transform_table_field(field):
    """Transform a table field to TableField format"""
    table_field = {
        '$type': 'table',
        'FieldId': field.get('fieldId', ''),
        'Label': field.get('label', ''),
        'DisplayOrder': field.get('displayOrder', 1),
        'Columns': [],
        'MinRows': field.get('minRows', 1),
        'ShowFooter': field.get('showFooter', True),
        'Summaries': field.get('summaries', [])
    }
    
    # Transform columns
    for col in field.get('columns', []):
        column = {
            'FieldId': col.get('fieldId', ''),
            'Label': col.get('label', ''),
            'FieldType': map_field_type(col.get('fieldType', 'text')),
            'DisplayOrder': col.get('displayOrder', 1),
            'IsReadonly': col.get('isReadonly', False)
        }
        if col.get('options'):
            column['Options'] = col['options']
        table_field['Columns'].append(column)
    
    return table_field

def transform_group_to_container(field):
    """Transform a group field to ContainerField format"""
    container = {
        '$type': 'container',
        'FieldId': field.get('fieldId', ''),
        'Label': field.get('label', ''),
        'Container': 'Group',
        'DisplayOrder': field.get('displayOrder', 1),
        'IsVisible': field.get('visible', True),
        'Children': []
    }
    
    # Transform subFields
    if field.get('subFields'):
        container['Children'], _ = transform_fields(field['subFields'], 1)
    
    return container

def transform_fields(fields, depth=0):
    """Recursively transform fields to new structure"""
    transformed = []
    rules = []
    
    for field in fields:
        field_type = field.get('fieldType', '')
        
        if field_type == 'table' or field_type == 'dynamic_table':
            transformed.append(transform_table_field(field))
        elif field_type == 'group':
            container = transform_group_to_container(field)
            transformed.append(container)
            # Get rules from nested fields
            if field.get('subFields'):
                _, nested_rules = transform_fields(field['subFields'], depth + 1)
                rules.extend(nested_rules)
        else:
            transformed.append(transform_field_to_input(field))
            # Check for formula
            if field.get('formula'):
                field_rules = extract_calculation_rules([field], depth)
                rules.extend(field_rules)
    
    return transformed, rules

def migrate_template(client, collection_name, template_id):
    """Migrate a single template"""
    print(f"\n{'=' * 80}")
    print(f"📋 MIGRATING: {collection_name}")
    print(f"{'=' * 80}")
    
    try:
        # Fetch source template
        db = client['valuation_admin']
        collection = db[collection_name]
        
        template_doc = collection.find_one({})
        if not template_doc:
            print(f"❌ No template found in collection: {collection_name}")
            return None
        
        template_metadata = template_doc.get('templateMetadata', {})
        documents = template_doc.get('documents', [])
        
        print(f"✅ Found template: {template_metadata.get('templateName', 'Unknown')}")
        print(f"   Bank: {template_metadata.get('bankCode', 'Unknown')}")
        print(f"   Property Type: {template_metadata.get('propertyType', 'Unknown')}")
        print(f"   Documents: {len(documents)}")
        
        # Fetch common fields
        common_fields_doc = db['common_form_fields'].find_one({})
        common_field_list = common_fields_doc.get('fields', []) if common_fields_doc else []
        
        # Transform common fields
        common_fields, common_rules = transform_fields(common_field_list, 0)
        print(f"✅ Common fields: {len(common_fields)}")
        
        # Create new template structure
        new_template = {
            'TemplateId': template_id,
            'TemplateName': template_metadata.get('templateName', 'Unknown Template'),
            'TemplateDescription': template_metadata.get('description', 'Property valuation template'),
            'BankDetails': {
                'BankCode': template_metadata.get('bankCode', 'UNKNOWN').upper(),
                'BankName': template_metadata.get('bankName', 'Unknown Bank')
            },
            'PropertyType': template_metadata.get('propertyType', 'Unknown'),
            'Elements': [],
            'CalculationRules': []
        }
        
        # Add common fields
        new_template['Elements'].extend(common_fields)
        new_template['CalculationRules'].extend(common_rules)
        
        current_order = len(common_fields) + 1
        
        # Process tabs
        tabs = template_metadata.get('tabs', [])
        print(f"📑 Processing {len(tabs)} tabs...")
        
        for tab in sorted(tabs, key=lambda x: x.get('sortOrder', 0)):
            tab_id = tab.get('tabId', '')
            tab_name = tab.get('tabName', '')
            document_source = tab.get('documentSource', '')
            has_sections = tab.get('hasSections', False)
            
            # Find corresponding document
            doc = next((d for d in documents if d.get('templateId') == document_source), None)
            
            if not doc:
                print(f"   ⚠️  No document found for tab: {tab_name}")
                continue
            
            # Create tab container
            tab_container = {
                '$type': 'container',
                'FieldId': tab_id,
                'Label': tab_name,
                'Container': 'Tab',
                'DisplayOrder': current_order,
                'IsVisible': True,
                'Children': []
            }
            
            if has_sections:
                # Process sections
                sections = doc.get('sections', [])
                for section in sorted(sections, key=lambda x: x.get('sortOrder', 0)):
                    section_fields = section.get('fields', [])
                    
                    if section_fields:
                        # Transform fields
                        transformed_fields, section_rules = transform_fields(section_fields, 1)
                        new_template['CalculationRules'].extend(section_rules)
                        
                        # Create section container
                        section_container = {
                            '$type': 'container',
                            'FieldId': section.get('sectionId', ''),
                            'Label': section.get('sectionName', ''),
                            'Container': 'Section',
                            'DisplayOrder': section.get('sortOrder', 1),
                            'IsVisible': True,
                            'Children': transformed_fields
                        }
                        tab_container['Children'].append(section_container)
            else:
                # Direct fields without sections
                direct_fields = doc.get('fields', [])
                if direct_fields:
                    transformed_fields, doc_rules = transform_fields(direct_fields, 1)
                    tab_container['Children'].extend(transformed_fields)
                    new_template['CalculationRules'].extend(doc_rules)
            
            new_template['Elements'].append(tab_container)
            current_order += 1
            print(f"   ✅ {tab_name}: {len(tab_container['Children'])} children")
        
        # Count fields
        def count_fields_recursive(elements):
            count = 0
            for elem in elements:
                if elem.get('$type') == 'input':
                    count += 1
                elif elem.get('Children'):
                    count += count_fields_recursive(elem['Children'])
            return count
        
        total_fields = count_fields_recursive(new_template['Elements'])
        total_rules = len(new_template['CalculationRules'])
        
        print(f"\n📊 Migration Summary:")
        print(f"   Total Fields: {total_fields}")
        print(f"   Calculation Rules: {total_rules}")
        print(f"   Tabs: {len([e for e in new_template['Elements'] if e.get('Container') == 'Tab'])}")
        
        return new_template
        
    except Exception as e:
        print(f"❌ Migration failed for {collection_name}: {e}")
        import traceback
        traceback.print_exc()
        return None

def save_template_to_file(template, filename):
    """Save template to JSON file"""
    filepath = f"templates-csharp/migrated/{filename}"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    file_size = os.path.getsize(filepath)
    print(f"💾 Saved to: {filepath} ({file_size / 1024:.1f} KB)")
    return filepath

def upload_to_mongodb(client, template):
    """Upload template to valuation_templates database"""
    db = client['valuation_templates']
    collection = db['templates']
    
    # Add metadata
    template['CreatedAt'] = datetime.utcnow()
    template['UpdatedAt'] = datetime.utcnow()
    template['Version'] = "1.0"
    template['Status'] = "Active"
    template['MigratedFrom'] = "MongoDB_Legacy_Structure"
    template['MigrationDate'] = datetime.utcnow()
    
    # Check if exists
    existing = collection.find_one({'TemplateId': template['TemplateId']})
    
    if existing:
        # Update
        collection.replace_one({'TemplateId': template['TemplateId']}, template)
        print(f"✅ Updated in MongoDB: {template['TemplateId']}")
    else:
        # Insert
        result = collection.insert_one(template)
        print(f"✅ Inserted to MongoDB: {template['TemplateId']} (ID: {result.inserted_id})")
        
        # Create indexes (only on first insert)
        collection.create_index([('TemplateId', 1)], unique=True)
        collection.create_index([('BankDetails.BankCode', 1)])
        collection.create_index([('PropertyType', 1)])
        collection.create_index([('Status', 1)])

def main():
    print("=" * 80)
    print("🚀 BATCH TEMPLATE MIGRATION TO C# STRUCTURE")
    print("=" * 80)
    print(f"\nTemplates to migrate: {len(TEMPLATES_TO_MIGRATE)}")
    print()
    
    # Connect to MongoDB
    client = connect_to_mongodb()
    print("✅ Connected to MongoDB Atlas\n")
    
    migrated_count = 0
    failed_count = 0
    
    try:
        for collection_name, template_id in TEMPLATES_TO_MIGRATE:
            # Migrate template
            new_template = migrate_template(client, collection_name, template_id)
            
            if new_template:
                # Generate filename
                filename = f"{template_id.lower()}.json"
                
                # Save to file
                save_template_to_file(new_template, filename)
                
                # Upload to MongoDB
                upload_to_mongodb(client, new_template)
                
                migrated_count += 1
                print(f"✅ SUCCESS: {collection_name}")
            else:
                failed_count += 1
                print(f"❌ FAILED: {collection_name}")
            
            print()
    
    finally:
        client.close()
    
    # Final summary
    print("\n" + "=" * 80)
    print("📊 BATCH MIGRATION SUMMARY")
    print("=" * 80)
    print(f"Total Templates: {len(TEMPLATES_TO_MIGRATE)}")
    print(f"✅ Migrated Successfully: {migrated_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📁 Output Directory: templates-csharp/migrated/")
    print(f"🗄️  MongoDB Database: valuation_templates")
    print("=" * 80)

if __name__ == "__main__":
    main()
