#!/usr/bin/env python3
"""
Script to add includeInCustomTemplate field to template JSON files

This script can:
1. Process existing local templates in backend/data
2. Download templates from MongoDB and add the field
3. Update templates in-place or save to a separate directory

Usage:
  python process_local_templates.py              # Process local files, save to templates_updated/
  python process_local_templates.py --inplace    # Process local files, update in-place
  python process_local_templates.py --download   # Download from MongoDB, add field, save to backend/data
"""

import json
import sys
from pathlib import Path
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

# MongoDB configuration
MONGODB_URI = "mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster"
DB_NAME = "valuation_admin"

# Base data directory
BASE_DIR = Path(__file__).parent.parent / "backend" / "data"
OUTPUT_DIR = BASE_DIR / "templates_updated"

# Template collections in MongoDB
TEMPLATE_COLLECTIONS = {
    'common_form_fields': {'path': 'common_fields.json', 'is_common': True},
    'sbi_land_property_details': {'path': 'sbi/land/sbi_land_property_details.json', 'is_common': False},
    'sbi_apartment_property_details': {'path': 'sbi/apartment/sbi_apartment_property_details.json', 'is_common': False},
    'ubi_land_property_details': {'path': 'ubi/land/ubi_land_property_details.json', 'is_common': False},
    'bob_land_property_details': {'path': 'bob/bob_land_property_details.json', 'is_common': False},
    'boi_land_property_details': {'path': 'boi/boi_bank_document.json', 'is_common': False},
    'cbi_all_property_details': {'path': 'cbi/cbi_all_property_details.json', 'is_common': False},
    'hdfc_all_property_details': {'path': 'hdfc/hdfc_all_property_details.json', 'is_common': False},
}

# Template files to process (bank-specific templates)
BANK_TEMPLATE_PATTERNS = [path_info['path'] for path_info in TEMPLATE_COLLECTIONS.values() if not path_info['is_common']]

# Common fields file
COMMON_FIELDS_FILE = "common_fields.json"


def process_field(field, include_in_custom=True):
    """Add includeInCustomTemplate to a field"""
    field['includeInCustomTemplate'] = include_in_custom
    return field


def process_json_file(file_path, is_common=False):
    """Process a single JSON file"""
    print(f"\n📥 Processing: {file_path.relative_to(BASE_DIR)}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    field_count = 0
    include_in_custom = not is_common
    
    # Process based on structure
    if 'documents' in data:
        for doc in data['documents']:
            # documents[x].sections[x].fields[]
            if 'sections' in doc:
                for section in doc['sections']:
                    for field in section.get('fields', []):
                        process_field(field, include_in_custom)
                        field_count += 1
    
    # Common fields format
    if 'fields' in data and isinstance(data['fields'], list):
        for field in data['fields']:
            process_field(field, include_in_custom)
            field_count += 1
    
    print(f"   ✅ Processed {field_count} fields")
    print(f"   🏷️  includeInCustomTemplate = {include_in_custom}")
    
    return data, field_count


def json_serializer(obj):
    """Custom JSON serializer for MongoDB types"""
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def save_file(data, original_path, inplace=False):
    """Save processed data"""
    if inplace:
        # Save directly to original location
        output_path = original_path
    else:
        # Save to output directory with same structure
        relative_path = original_path.relative_to(BASE_DIR)
        output_path = OUTPUT_DIR / relative_path
        # Create parent directories
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=json_serializer)
    
    if inplace:
        print(f"   💾 Updated in-place: {output_path.relative_to(BASE_DIR)}")
    else:
        print(f"   💾 Saved to: {output_path.relative_to(BASE_DIR)}")
    return output_path


def download_from_mongodb(collection_name, is_common=False):
    """Download template from MongoDB and process it"""
    print(f"\n📥 Downloading from MongoDB: {collection_name}")
    
    try:
        client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            tlsAllowInvalidCertificates=True
        )
        
        db = client[DB_NAME]
        collection = db[collection_name]
        
        documents = list(collection.find({}))
        
        if not documents:
            print(f"   ⚠️  No documents found in {collection_name}")
            return None, 0
        
        print(f"   📄 Downloaded {len(documents)} documents")
        
        # Process fields
        field_count = 0
        include_in_custom = not is_common
        
        for doc in documents:
            # documents[x].sections[x].fields[]
            if 'sections' in doc:
                for section in doc['sections']:
                    for field in section.get('fields', []):
                        process_field(field, include_in_custom)
                        field_count += 1
            
            # Common fields format
            if 'fields' in doc and isinstance(doc['fields'], list):
                for field in doc['fields']:
                    process_field(field, include_in_custom)
                    field_count += 1
        
        # Create data structure similar to local files
        data = {
            'metadata': {
                'downloaded_at': datetime.now().isoformat(),
                'collection_name': collection_name,
                'total_documents': len(documents),
                'database': DB_NAME
            },
            'documents': documents if 'sections' in documents[0] else None,
            'fields': documents[0].get('fields', []) if len(documents) == 1 and 'fields' in documents[0] else None
        }
        
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        
        print(f"   ✅ Processed {field_count} fields")
        print(f"   🏷️  includeInCustomTemplate = {include_in_custom}")
        
        client.close()
        return data, field_count
        
    except Exception as e:
        print(f"   ❌ Error downloading {collection_name}: {e}")
        return None, 0


def process_local_files(inplace=False):
    """Process existing local template files"""
    mode_text = "in-place" if inplace else "to templates_updated/"
    print(f"� Processing local files {mode_text}")
    
    total_files = 0
    total_fields = 0
    common_fields_count = 0
    bank_fields_count = 0
    
    # Process common fields
    common_path = BASE_DIR / COMMON_FIELDS_FILE
    if common_path.exists():
        data, count = process_json_file(common_path, is_common=True)
        save_file(data, common_path, inplace=inplace)
        total_files += 1
        total_fields += count
        common_fields_count += count
    else:
        print(f"\n⚠️  Common fields file not found: {COMMON_FIELDS_FILE}")
    
    # Process bank templates
    for pattern in BANK_TEMPLATE_PATTERNS:
        template_path = BASE_DIR / pattern
        if template_path.exists():
            data, count = process_json_file(template_path, is_common=False)
            save_file(data, template_path, inplace=inplace)
            total_files += 1
            total_fields += count
            bank_fields_count += count
        else:
            print(f"\n⚠️  Template file not found: {pattern}")
    
    return total_files, total_fields, common_fields_count, bank_fields_count


def download_and_process():
    """Download templates from MongoDB and process them"""
    print("📥 Downloading templates from MongoDB")
    
    total_files = 0
    total_fields = 0
    common_fields_count = 0
    bank_fields_count = 0
    
    for collection_name, info in TEMPLATE_COLLECTIONS.items():
        data, count = download_from_mongodb(collection_name, is_common=info['is_common'])
        
        if data:
            # Save directly to backend/data
            file_path = BASE_DIR / info['path']
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=json_serializer)
            
            print(f"   💾 Saved to: {info['path']}")
            
            total_files += 1
            total_fields += count
            if info['is_common']:
                common_fields_count += count
            else:
                bank_fields_count += count
    
    return total_files, total_fields, common_fields_count, bank_fields_count


def main():
    print("=" * 80)
    print("📦 Template Files Processor with includeInCustomTemplate Field")
    print("=" * 80)
    print(f"📁 Base Directory: {BASE_DIR}")
    
    # Parse command line arguments
    download_mode = '--download' in sys.argv
    inplace_mode = '--inplace' in sys.argv
    
    if download_mode:
        print("🌐 Mode: Download from MongoDB")
    elif inplace_mode:
        print("📝 Mode: Process local files (in-place)")
    else:
        print(f"📝 Mode: Process local files (save to templates_updated/)")
        print(f"📁 Output Directory: {OUTPUT_DIR}")
    
    print("=" * 80)
    
    if download_mode:
        total_files, total_fields, common_fields_count, bank_fields_count = download_and_process()
    else:
        total_files, total_fields, common_fields_count, bank_fields_count = process_local_files(inplace=inplace_mode)
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"✅ Total Files Processed: {total_files}")
    print(f"🏷️  Total Fields Processed: {total_fields}")
    print(f"   📝 Common Fields (includeInCustomTemplate=false): {common_fields_count}")
    print(f"   🏦 Bank-Specific Fields (includeInCustomTemplate=true): {bank_fields_count}")
    
    if download_mode:
        print(f"\n💾 Templates downloaded and saved to: backend/data/")
    elif inplace_mode:
        print(f"\n💾 Templates updated in-place in: backend/data/")
    else:
        print(f"\n💾 Updated templates saved to: {OUTPUT_DIR}/")
        print("\n📋 Next steps:")
        print("   1. Review the updated files in backend/data/templates_updated/")
        print("   2. Copy them to backend/data/ to replace originals:")
        print("      cd backend/data && cp -rf templates_updated/* . && rm -rf templates_updated")
    
    print("=" * 80)
    print("\n✅ All done!")


if __name__ == "__main__":
    main()
