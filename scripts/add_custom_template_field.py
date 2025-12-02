#!/usr/bin/env python3
"""
Script to download all template collections from MongoDB and add includeInCustomTemplate field
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

# MongoDB configuration
MONGODB_URI = "mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster"
DB_NAMES = ["valuation_admin", "valuation_system"]  # Check multiple databases

# Template collections to process
TEMPLATE_COLLECTIONS = [
    "common_form_fields",
    "sbi_land_template",
    "sbi_apartment_template", 
    "ubi_land_template",
    "bob_land_template",
    "bob_apartment_template",
    "pnb_all_property_template",
    "hdfc_all_property_template",
    "uco_all_property_template",
    "cbi_all_property_template"
]

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "backend" / "data" / "templates_with_custom_field"


def json_serializer(obj):
    """Custom JSON serializer for ObjectId and datetime"""
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def process_field_document(doc, is_common_field=False):
    """Add includeInCustomTemplate field to a field document"""
    # Common fields should NOT be in custom templates (user enters them each time)
    # Bank-specific fields SHOULD be in custom templates (can have default values)
    doc['includeInCustomTemplate'] = not is_common_field
    return doc


def download_and_process_collection(client, db_name, collection_name):
    """Download collection and add includeInCustomTemplate field"""
    print(f"\n📥 Processing: {db_name}.{collection_name}")
    
    db = client[db_name]
    collection = db[collection_name]
    
    # Download all documents
    documents = list(collection.find({}))
    
    if not documents:
        print(f"   ⚠️  No documents found in {collection_name}")
        return None
    
    print(f"   📄 Found {len(documents)} documents")
    
    # Determine if this is common fields collection
    is_common = collection_name == "common_form_fields"
    
    # Process each document
    processed_docs = []
    field_count = 0
    
    for doc in documents:
        # Check if document has 'fields' array (common pattern)
        if 'fields' in doc and isinstance(doc['fields'], list):
            for field in doc['fields']:
                process_field_document(field, is_common)
                field_count += 1
        
        # Check if document itself is a field (has fieldId)
        elif 'fieldId' in doc:
            process_field_document(doc, is_common)
            field_count += 1
        
        # Check for nested structures - documents with sections
        elif 'sections' in doc and isinstance(doc['sections'], list):
            for section in doc['sections']:
                for field in section.get('fields', []):
                    process_field_document(field, is_common)
                    field_count += 1
        
        # Check for tabs with sections  
        elif 'tabs' in doc:
            for tab in doc.get('tabs', []):
                # Process tab-level fields
                for field in tab.get('fields', []):
                    process_field_document(field, is_common)
                    field_count += 1
                
                # Process section-level fields
                for section in tab.get('sections', []):
                    for field in section.get('fields', []):
                        process_field_document(field, is_common)
                        field_count += 1
        
        processed_docs.append(doc)
    
    print(f"   ✅ Processed {field_count} fields")
    print(f"   🏷️  includeInCustomTemplate = {not is_common}")
    
    return {
        'database': db_name,
        'collection_name': collection_name,
        'is_common_fields': is_common,
        'document_count': len(processed_docs),
        'field_count': field_count,
        'documents': processed_docs
    }


def save_to_file(data, collection_name):
    """Save processed data to JSON file"""
    if not data:
        return False
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    output_file = OUTPUT_DIR / f"{collection_name}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=json_serializer, ensure_ascii=False)
    
    print(f"   💾 Saved to: {output_file}")
    return True


def main():
    print("=" * 80)
    print("📦 Template Collections Download & Processing Tool")
    print("=" * 80)
    print(f"📁 Output: {OUTPUT_DIR}")
    print("=" * 80)
    
    try:
        # Connect to MongoDB
        print("\n🔌 Connecting to MongoDB...")
        client = MongoClient(
            MONGODB_URI, 
            serverSelectionTimeoutMS=5000,
            tlsAllowInvalidCertificates=True  # For development/testing only
        )
        
        # Test connection
        client.server_info()
        print("✅ Connected to MongoDB successfully!")
        
        # Find collections across all databases
        all_template_collections = []
        
        for db_name in DB_NAMES:
            db = client[db_name]
            collections = db.list_collection_names()
            print(f"\n📋 Collections in {db_name}: {len(collections)}")
            for coll in sorted(collections):
                print(f"   - {coll}")
                all_template_collections.append((db_name, coll))
        
        if not all_template_collections:
            print("\n⚠️  No collections found in any database!")
            return 1
        
        # Process each collection
        results = {
            'processed_at': datetime.now().isoformat(),
            'collections': [],
            'summary': {
                'total_collections': 0,
                'total_documents': 0,
                'total_fields_processed': 0,
                'common_fields_count': 0,
                'bank_specific_fields_count': 0
            }
        }
        
        for db_name, collection_name in all_template_collections:
            try:
                data = download_and_process_collection(client, db_name, collection_name)
                
                if data:
                    # Save to individual file
                    save_filename = f"{db_name}_{collection_name}"
                    save_to_file(data, save_filename)
                    
                    # Update summary
                    results['collections'].append({
                        'name': collection_name,
                        'is_common': data['is_common_fields'],
                        'documents': data['document_count'],
                        'fields': data['field_count']
                    })
                    
                    results['summary']['total_collections'] += 1
                    results['summary']['total_documents'] += data['document_count']
                    results['summary']['total_fields_processed'] += data['field_count']
                    
                    if data['is_common_fields']:
                        results['summary']['common_fields_count'] += data['field_count']
                    else:
                        results['summary']['bank_specific_fields_count'] += data['field_count']
                
            except Exception as e:
                print(f"   ❌ Error processing {collection_name}: {e}")
        
        # Save summary
        summary_file = OUTPUT_DIR / "_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=json_serializer)
        
        print("\n" + "=" * 80)
        print("📊 SUMMARY")
        print("=" * 80)
        print(f"✅ Total Collections Processed: {results['summary']['total_collections']}")
        print(f"📄 Total Documents: {results['summary']['total_documents']}")
        print(f"🏷️  Total Fields Processed: {results['summary']['total_fields_processed']}")
        print(f"   📝 Common Fields (includeInCustomTemplate=false): {results['summary']['common_fields_count']}")
        print(f"   🏦 Bank-Specific Fields (includeInCustomTemplate=true): {results['summary']['bank_specific_fields_count']}")
        print(f"\n💾 Summary saved to: {summary_file}")
        print("=" * 80)
        
        client.close()
        print("\n✅ All done!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
