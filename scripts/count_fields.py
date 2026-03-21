#!/usr/bin/env python3
"""
Count all fields in SBI Land template to understand the structure
"""

import json

def count_fields_recursive(obj, depth=0):
    """Recursively count all fields"""
    count = 0
    formulas = []
    
    if isinstance(obj, dict):
        # Check if this is a field (both old camelCase and new PascalCase)
        if 'fieldId' in obj or 'FieldId' in obj:
            count += 1
            if obj.get('formula') or obj.get('Formula'):
                field_id = obj.get('fieldId') or obj.get('FieldId')
                formulas.append(field_id)
        
        # Check subFields (both old and new formats)
        if 'subFields' in obj and obj['subFields']:
            sub_count, sub_formulas = count_fields_recursive(obj['subFields'], depth + 1)
            count += sub_count
            formulas.extend(sub_formulas)
        
        # Check Children (new format for containers)
        if 'Children' in obj and obj['Children']:
            sub_count, sub_formulas = count_fields_recursive(obj['Children'], depth + 1)
            count += sub_count
            formulas.extend(sub_formulas)
        
        # Check other nested structures
        for value in obj.values():
            if isinstance(value, (list, dict)):
                sub_count, sub_formulas = count_fields_recursive(value, depth + 1)
                count += sub_count
                formulas.extend(sub_formulas)
    
    elif isinstance(obj, list):
        for item in obj:
            sub_count, sub_formulas = count_fields_recursive(item, depth + 1)
            count += sub_count
            formulas.extend(sub_formulas)
    
    return count, formulas

# Load the original template
with open('sbi_land_property_details_full.json', 'r') as f:
    original = json.load(f)

print("="*80)
print("ORIGINAL TEMPLATE FIELD COUNT")
print("="*80)

# Count fields in documents
total_fields = 0
total_formulas = []

for idx, doc in enumerate(original.get('documents', [])):
    doc_fields, doc_formulas = count_fields_recursive(doc)
    total_fields += doc_fields
    total_formulas.extend(doc_formulas)
    print(f"\nDocument {idx + 1}: {doc.get('templateId', 'Unknown')}")
    print(f"  Fields: {doc_fields}")
    print(f"  Formulas: {len(doc_formulas)}")
    if doc_formulas:
        print(f"  Formula fields: {doc_formulas}")

print(f"\n{'='*80}")
print(f"TOTAL FIELDS: {total_fields}")
print(f"TOTAL FORMULAS: {len(total_formulas)}")
print(f"Formula fields: {total_formulas}")
print(f"{'='*80}")

# Load migrated template
with open('sbi_land_template_migrated.json', 'r') as f:
    migrated = json.load(f)

print("\n" + "="*80)
print("MIGRATED TEMPLATE FIELD COUNT")
print("="*80)

migrated_fields, migrated_formulas = count_fields_recursive(migrated.get('Elements', []))
calc_rules = len(migrated.get('CalculationRules', []))

print(f"\nTotal Fields: {migrated_fields}")
print(f"Total Formulas: {len(migrated_formulas)}")
print(f"Calculation Rules: {calc_rules}")
if migrated_formulas:
    print(f"Formula fields: {migrated_formulas}")

print(f"\n{'='*80}")
print(f"DIFFERENCE: {total_fields - migrated_fields} fields missing")
print(f"{'='*80}")
