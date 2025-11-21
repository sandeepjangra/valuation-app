#!/usr/bin/env python3
"""
Script to fix and reformat the apartment template to resolve jq parsing issues
and improve loading performance.
"""

import json
from datetime import datetime

def fix_and_reformat_template():
    """Fix and reformat the SBI apartment template."""
    
    template_path = "/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend/data/sbi/apartment/sbi_apartment_property_details.json"
    backup_path = template_path + f".backup_reformat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print("🔍 Loading apartment template...")
    
    try:
        with open(template_path, 'r') as f:
            data = json.load(f)
        
        print(f"✅ Template loaded successfully")
        
        # Create backup
        print(f"💾 Creating backup at: {backup_path}")
        with open(backup_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Clean and validate the data structure
        print("🔧 Cleaning data structure...")
        
        cleaned_documents = []
        total_fields = 0
        
        for doc_idx, doc in enumerate(data.get('documents', [])):
            if not isinstance(doc, dict):
                print(f"⚠️ Skipping invalid document {doc_idx}: {type(doc)}")
                continue
                
            cleaned_doc = {}
            for key, value in doc.items():
                if value is not None:
                    cleaned_doc[key] = value
            
            # Clean sections
            if 'sections' in cleaned_doc:
                cleaned_sections = []
                for sec_idx, section in enumerate(cleaned_doc['sections']):
                    if not isinstance(section, dict):
                        print(f"⚠️ Skipping invalid section {sec_idx} in document {doc_idx}")
                        continue
                    
                    cleaned_section = {}
                    for key, value in section.items():
                        if value is not None:
                            cleaned_section[key] = value
                    
                    # Clean fields
                    if 'fields' in cleaned_section and cleaned_section['fields'] is not None:
                        cleaned_fields = []
                        for field_idx, field in enumerate(cleaned_section['fields']):
                            if field is None:
                                print(f"🔧 Removing null field at doc {doc_idx}, section {sec_idx}, field {field_idx}")
                                continue
                            
                            if isinstance(field, dict):
                                cleaned_field = {}
                                for key, value in field.items():
                                    if value is not None:
                                        cleaned_field[key] = value
                                
                                # Clean subFields if they exist
                                if 'subFields' in cleaned_field and cleaned_field['subFields'] is not None:
                                    cleaned_subfields = []
                                    for sub_field in cleaned_field['subFields']:
                                        if sub_field is not None:
                                            cleaned_subfields.append(sub_field)
                                    cleaned_field['subFields'] = cleaned_subfields
                                
                                cleaned_fields.append(cleaned_field)
                                total_fields += 1
                            else:
                                print(f"⚠️ Skipping invalid field type {type(field)}")
                        
                        cleaned_section['fields'] = cleaned_fields
                    
                    cleaned_sections.append(cleaned_section)
                
                cleaned_doc['sections'] = cleaned_sections
            
            cleaned_documents.append(cleaned_doc)
        
        # Update the data
        data['documents'] = cleaned_documents
        
        print(f"📊 Cleaned template stats:")
        print(f"   Documents: {len(cleaned_documents)}")
        print(f"   Total fields: {total_fields}")
        
        # Save the cleaned template with proper formatting
        print(f"💾 Saving cleaned template...")
        with open(template_path, 'w') as f:
            json.dump(data, f, indent=2, separators=(',', ': '), ensure_ascii=False)
        
        print(f"✅ Template cleaned and reformatted!")
        
        # Verify the fix
        print(f"🔍 Verifying cleaned template...")
        try:
            with open(template_path, 'r') as f:
                verified_data = json.load(f)
            
            doc_count = len(verified_data['documents'])
            field_count = 0
            for doc in verified_data['documents']:
                if 'sections' in doc:
                    for section in doc['sections']:
                        if 'fields' in section:
                            field_count += len(section['fields'])
            
            print(f"✅ Verification successful:")
            print(f"   Documents: {doc_count}")
            print(f"   Fields: {field_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Error processing template: {e}")
        return False

if __name__ == "__main__":
    print("🚀 SBI Apartment Template Cleaner & Reformatter")
    print("=" * 55)
    
    success = fix_and_reformat_template()
    
    if success:
        print("\n🎉 Template cleaning completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Test jq parsing with the cleaned template")
        print("   2. Restart the backend server")
        print("   3. Test the Valuation tab loading speed")
        print("   4. Verify all fields are now loading properly")
    else:
        print("\n❌ Template cleaning failed!")
        print("   Please check the error messages above")