#!/usr/bin/env python3
"""
Migrate SBI Land Template to New C# Structure
This script transforms the existing MongoDB template to the new unified structure
"""

import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
import json
from datetime import datetime
from collections import defaultdict

# Load environment variables
load_dotenv()

def connect_to_mongodb():
    """Connect to MongoDB Atlas"""
    mongo_uri = os.getenv('MONGODB_URI')
    if not mongo_uri:
        print("❌ MONGODB_URI not found in environment variables")
        sys.exit(1)
    
    try:
        client = MongoClient(mongo_uri)
        client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas")
        return client
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        sys.exit(1)

def map_field_type(mongodb_type):
    """Map MongoDB fieldType to C# FieldType enum"""
    type_mapping = {
        'text': 'Text',
        'textarea': 'Text',
        'number': 'Number',
        'currency': 'Number',
        'date': 'Date',
        'select': 'Dropdown',
        'dropdown': 'Dropdown',
        'file_upload': 'FileUpload',
        'group': 'Group',
        'table': 'Table',
        'dynamic_table': 'Table'
    }
    return type_mapping.get(mongodb_type, 'Text')

def extract_calculation_rules(fields, rules_list, parent_path=""):
    """Recursively extract calculation rules from fields with formulas"""
    for field in fields:
        field_id = field.get('fieldId', '')
        formula = field.get('formula')
        
        if formula:
            # Extract dependencies from calculationMetadata or formula
            dependencies = []
            calc_metadata = field.get('calculationMetadata', {})
            
            if calc_metadata.get('dependencies'):
                dependencies = calc_metadata['dependencies']
            else:
                # Try to extract from formula string
                import re
                potential_deps = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', formula)
                js_keywords = ['return', 'function', 'if', 'else', 'for', 'while', 'var', 'let', 'const']
                dependencies = [dep for dep in potential_deps if dep not in js_keywords]
            
            rule = {
                "RuleId": f"calc_{field_id}",
                "TriggerFieldIds": dependencies,
                "Formula": formula,
                "TargetFieldId": field_id,
                "Description": field.get('helpText', f"Calculate {field.get('uiDisplayName', field_id)}")
            }
            rules_list.append(rule)
            print(f"      🧮 Extracted formula: {field_id} = {formula}")
        
        # Check subFields (for group fields)
        if field.get('subFields'):
            extract_calculation_rules(
                field['subFields'], 
                rules_list, 
                f"{parent_path}/{field_id}" if parent_path else field_id
            )

def transform_field_to_input(field, display_order):
    """Transform MongoDB field to InputField structure"""
    field_id = field.get('fieldId', '')
    field_type = field.get('fieldType', 'text')
    
    input_field = {
        "$type": "input",
        "FieldId": field_id,
        "Label": field.get('uiDisplayName', field_id),
        "SpecificType": map_field_type(field_type),
        "DisplayOrder": display_order,
        "IsRequired": field.get('isRequired', False),
        "IsVisible": not field.get('isHidden', False),
        "DefaultValue": field.get('defaultValue') or field.get('value'),
        "HelpText": field.get('helpText'),
        "PlaceholderText": field.get('placeholder')
    }
    
    # Add options for dropdown/select
    if field_type in ['select', 'dropdown'] and field.get('options'):
        input_field['Options'] = field['options']
    
    # Mark calculated fields as readonly
    if field.get('formula') or field.get('isReadonly'):
        input_field['IsReadonly'] = True
    
    # Add visibility rules if conditional logic exists
    if field.get('conditionalLogic'):
        input_field['Visibility'] = transform_conditional_logic(field['conditionalLogic'])
    
    return input_field

def transform_conditional_logic(conditional_logic):
    """Transform MongoDB conditionalLogic to VisibilityRule"""
    # Simplified version - expand based on actual structure
    return {
        "SourceFieldId": conditional_logic.get('fieldId', ''),
        "Operator": conditional_logic.get('operator', 'Equals'),
        "TargetValue": conditional_logic.get('value', '')
    }

def transform_table_field(field, display_order):
    """Transform MongoDB table field to TableField structure"""
    columns = []
    
    for idx, col in enumerate(field.get('columns', [])):
        column_field = {
            "FieldId": col.get('columnId', col.get('fieldId', f"col_{idx}")),
            "Label": col.get('columnName', col.get('uiDisplayName', f"Column {idx}")),
            "SpecificType": map_field_type(col.get('fieldType', 'text')),
            "IsRequired": col.get('isRequired', False),
            "DisplayOrder": idx + 1
        }
        
        if col.get('isReadonly'):
            column_field['IsReadonly'] = True
        
        columns.append(column_field)
    
    table_field = {
        "$type": "table",
        "FieldId": field.get('fieldId', ''),
        "Label": field.get('uiDisplayName', ''),
        "DisplayOrder": display_order,
        "Columns": columns,
        "MinRows": field.get('minRows', 1),
        "ShowFooter": field.get('showFooter', True),
        "Summaries": []
    }
    
    # Add summaries if available
    if field.get('summaries'):
        table_field['Summaries'] = field['summaries']
    
    return table_field

def transform_group_to_container(field, display_order, children):
    """Transform MongoDB group field to ContainerField"""
    return {
        "$type": "container",
        "FieldId": field.get('fieldId', ''),
        "Label": field.get('uiDisplayName', ''),
        "Container": "Group",
        "DisplayOrder": display_order,
        "IsVisible": not field.get('isHidden', False),
        "Children": children
    }

def transform_section_to_container(section, section_order, fields):
    """Transform MongoDB section to ContainerField"""
    return {
        "$type": "container",
        "FieldId": section.get('sectionId', ''),
        "Label": section.get('sectionName', ''),
        "Container": "Section",
        "DisplayOrder": section_order,
        "IsVisible": True,
        "Children": fields
    }

def transform_fields(fields, starting_order=1):
    """Transform array of MongoDB fields to new structure"""
    transformed = []
    calculation_rules = []
    order = starting_order
    
    for field in fields:
        field_type = field.get('fieldType', 'text')
        
        if field_type == 'group':
            # Transform subfields first
            sub_fields, sub_rules = transform_fields(field.get('subFields', []), 1)
            calculation_rules.extend(sub_rules)
            
            # Create container for group
            group_container = transform_group_to_container(field, order, sub_fields)
            transformed.append(group_container)
        
        elif field_type in ['table', 'dynamic_table']:
            # Transform to TableField
            table = transform_table_field(field, order)
            transformed.append(table)
        
        else:
            # Regular input field
            input_field = transform_field_to_input(field, order)
            transformed.append(input_field)
        
        order += 1
    
    # Extract calculation rules
    extract_calculation_rules(fields, calculation_rules)
    
    return transformed, calculation_rules

def fetch_common_fields(db):
    """Fetch common form fields"""
    print("\n📋 Fetching common form fields...")
    
    common_doc = db['common_form_fields'].find_one({})
    if not common_doc:
        print("   ⚠️  No common fields found")
        return [], []
    
    fields = common_doc.get('fields', [])
    print(f"   ✅ Found {len(fields)} common fields")
    
    # Transform common fields
    transformed, rules = transform_fields(fields, starting_order=1)
    
    return transformed, rules

def fetch_sbi_land_template(db):
    """Fetch complete SBI Land template"""
    print("\n📋 Fetching SBI Land template...")
    
    template_doc = db['sbi_land_property_details'].find_one({})
    if not template_doc:
        print("   ❌ SBI Land template not found")
        sys.exit(1)
    
    template_metadata = template_doc.get('templateMetadata', {})
    documents = template_doc.get('documents', [])
    
    print(f"   ✅ Template: {template_metadata.get('templateName')}")
    print(f"   ✅ Tabs: {len(template_metadata.get('tabs', []))}")
    print(f"   ✅ Documents: {len(documents)}")
    
    return template_metadata, documents

def transform_template(template_metadata, documents, common_fields, common_rules):
    """Transform complete template to new structure"""
    print("\n🔄 Transforming template to new structure...")
    
    # Create base template
    new_template = {
        "TemplateId": template_metadata.get('templateId', 'SBI_LAND_TEMPLATE_V1'),
        "TemplateName": template_metadata.get('templateName', 'SBI Land Property Valuation'),
        "TemplateDescription": "Property valuation template for land properties",
        "BankDetails": {
            "BankCode": template_metadata.get('bankCode', 'SBI'),
            "BankName": "State Bank of India"
        },
        "PropertyType": template_metadata.get('propertyType', 'Land'),
        "Elements": [],
        "CalculationRules": []
    }
    
    # Add common fields first
    print(f"\n   📝 Adding {len(common_fields)} common fields...")
    new_template['Elements'].extend(common_fields)
    new_template['CalculationRules'].extend(common_rules)
    
    current_order = len(common_fields) + 1
    
    # Process each tab
    tabs = template_metadata.get('tabs', [])
    print(f"\n   📂 Processing {len(tabs)} tabs...")
    
    for tab in sorted(tabs, key=lambda x: x.get('sortOrder', 0)):
        tab_id = tab.get('tabId', '')
        tab_name = tab.get('tabName', '')
        has_sections = tab.get('hasSections', False)
        document_source = tab.get('documentSource', '')
        
        print(f"\n   📑 Tab: {tab_name}")
        
        # Find corresponding document by documentSource (matches templateId)
        doc = next((d for d in documents if d.get('templateId') == document_source), None)
        
        if not doc:
            print(f"      ⚠️  No document found for tab {tab_id} (looking for {document_source})")
            continue
        
        # Create tab container
        tab_container = {
            "$type": "container",
            "FieldId": tab_id,
            "Label": tab_name,
            "Container": "Tab",
            "DisplayOrder": current_order,
            "IsVisible": True,
            "Children": []
        }
        
        if has_sections:
            # Process sections
            sections = doc.get('sections', [])
            print(f"      📄 Sections: {len(sections)}")
            
            for section in sorted(sections, key=lambda x: x.get('sortOrder', 0)):
                section_fields = section.get('fields', [])
                
                if section_fields:
                    # Transform section fields
                    transformed_fields, section_rules = transform_fields(section_fields, 1)
                    new_template['CalculationRules'].extend(section_rules)
                    
                    # Create section container
                    section_container = transform_section_to_container(
                        section, 
                        section.get('sortOrder', 1), 
                        transformed_fields
                    )
                    tab_container['Children'].append(section_container)
                    
                    print(f"         ✅ {section.get('sectionName')}: {len(section_fields)} fields")
        else:
            # Tab has direct fields (no sections)
            direct_fields = doc.get('fields', [])
            if direct_fields:
                transformed_fields, tab_rules = transform_fields(direct_fields, 1)
                new_template['CalculationRules'].extend(tab_rules)
                tab_container['Children'] = transformed_fields
                print(f"      ✅ Direct fields: {len(direct_fields)}")
        
        new_template['Elements'].append(tab_container)
        current_order += 1
    
    return new_template

def validate_migration(old_template_doc, new_template):
    """Validate that all fields were migrated"""
    print("\n🔍 Validating migration...")
    
    # Count fields in old structure
    old_field_count = 0
    old_formula_count = 0
    
    def count_old_fields(obj):
        nonlocal old_field_count, old_formula_count
        if isinstance(obj, dict):
            if 'fieldId' in obj:
                old_field_count += 1
                if obj.get('formula'):
                    old_formula_count += 1
            if 'subFields' in obj:
                count_old_fields(obj['subFields'])
            for value in obj.values():
                count_old_fields(value)
        elif isinstance(obj, list):
            for item in obj:
                count_old_fields(item)
    
    count_old_fields(old_template_doc)
    
    # Count fields in new structure
    new_field_count = 0
    new_formula_count = len(new_template.get('CalculationRules', []))
    
    def count_new_fields(elements):
        nonlocal new_field_count
        for elem in elements:
            if elem.get('$type') in ['input', 'table']:
                new_field_count += 1
            if elem.get('$type') == 'container' and elem.get('Children'):
                count_new_fields(elem['Children'])
            # Count table columns
            if elem.get('$type') == 'table':
                new_field_count += len(elem.get('Columns', []))
    
    count_new_fields(new_template.get('Elements', []))
    
    print(f"\n   📊 Old Structure:")
    print(f"      Total Fields: {old_field_count}")
    print(f"      Formula Fields: {old_formula_count}")
    
    print(f"\n   📊 New Structure:")
    print(f"      Total Fields: {new_field_count}")
    print(f"      Calculation Rules: {new_formula_count}")
    
    # Check if counts match (approximately)
    if abs(old_field_count - new_field_count) > 5:
        print(f"\n   ⚠️  WARNING: Field count mismatch!")
        print(f"      Difference: {abs(old_field_count - new_field_count)} fields")
    else:
        print(f"\n   ✅ Field count validation passed!")
    
    if old_formula_count != new_formula_count:
        print(f"\n   ⚠️  WARNING: Formula count mismatch!")
    else:
        print(f"   ✅ Formula count validation passed!")
    
    return {
        'old_fields': old_field_count,
        'new_fields': new_field_count,
        'old_formulas': old_formula_count,
        'new_formulas': new_formula_count
    }

def save_to_new_database(client, template):
    """Save migrated template to new database"""
    print("\n💾 Saving to new database...")
    
    # Create or use existing database
    db = client['valuation_templates']
    collection = db['templates']
    
    # Add metadata
    template['_metadata'] = {
        'migratedAt': datetime.utcnow().isoformat(),
        'migratedFrom': 'valuation_admin.sbi_land_property_details',
        'version': '1.0',
        'status': 'active'
    }
    
    # Insert or update
    result = collection.replace_one(
        {'TemplateId': template['TemplateId']},
        template,
        upsert=True
    )
    
    if result.upserted_id:
        print(f"   ✅ Template inserted with ID: {result.upserted_id}")
    else:
        print(f"   ✅ Template updated")
    
    # Create indexes
    print("\n   📑 Creating indexes...")
    collection.create_index('TemplateId', unique=True)
    collection.create_index([('BankDetails.BankCode', 1), ('PropertyType', 1)])
    print("   ✅ Indexes created")
    
    return result

def main():
    print("="*80)
    print("🚀 SBI LAND TEMPLATE MIGRATION TO NEW STRUCTURE")
    print("="*80)
    
    # Connect to MongoDB
    client = connect_to_mongodb()
    db = client['valuation_admin']
    
    # Fetch common fields
    common_fields, common_rules = fetch_common_fields(db)
    
    # Fetch SBI Land template
    template_metadata, documents = fetch_sbi_land_template(db)
    
    # Fetch full template document for validation
    old_template_doc = db['sbi_land_property_details'].find_one({})
    
    # Transform to new structure
    new_template = transform_template(
        template_metadata, 
        documents, 
        common_fields, 
        common_rules
    )
    
    # Validate migration
    validation_stats = validate_migration(old_template_doc, new_template)
    
    # Save to file for review
    output_file = 'sbi_land_template_migrated.json'
    with open(output_file, 'w') as f:
        json.dump(new_template, f, indent=2, default=str)
    print(f"\n💾 Migrated template saved to: {output_file}")
    
    # Save validation stats
    stats_file = 'migration_validation_stats.json'
    with open(stats_file, 'w') as f:
        json.dump(validation_stats, f, indent=2)
    print(f"💾 Validation stats saved to: {stats_file}")
    
    # Ask for confirmation before saving to database
    print("\n" + "="*80)
    response = input("\n❓ Save migrated template to new database 'valuation_templates'? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        save_to_new_database(client, new_template)
        print("\n✅ Migration complete!")
    else:
        print("\n⏸️  Migration saved to file only. Database not updated.")
    
    client.close()
    print("\n" + "="*80)
    print("🎉 MIGRATION PROCESS FINISHED")
    print("="*80)

if __name__ == "__main__":
    main()
