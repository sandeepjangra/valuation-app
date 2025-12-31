#!/usr/bin/env python3
"""
Analyze SBI land property template structure to understand proper data organization
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import json

async def analyze_sbi_template_structure():
    """Analyze the SBI land property template to understand the structure"""
    
    # Load environment variables
    load_dotenv('backend/.env')
    mongodb_uri = os.getenv('MONGODB_URI')
    
    if not mongodb_uri:
        print("❌ MongoDB URI not found in environment")
        return
    
    client = AsyncIOMotorClient(mongodb_uri)
    
    try:
        # Connect to admin database where templates are stored
        admin_db = client['admin']
        
        # First, find the SBI land property template reference
        banks_collection = admin_db['banks']
        unified_doc = await banks_collection.find_one({"_id": "all_banks_comprehensive_v4"})
        
        if not unified_doc:
            print("❌ Unified banks document not found")
            return
        
        # Find SBI bank and land-property template
        sbi_template_collection = None
        all_banks = unified_doc.get("banks", [])
        
        for bank in all_banks:
            if bank.get("bankCode", "").upper() == "SBI":
                print(f"✅ Found SBI bank: {bank.get('bankName')}")
                templates = bank.get("templates", [])
                
                for template in templates:
                    template_id = template.get("templateId") or template.get("templateCode")
                    if template_id and template_id.lower() == "land-property":
                        collection_ref = template.get("collectionRef")
                        print(f"✅ Found SBI land-property template")
                        print(f"📋 Collection reference: {collection_ref}")
                        
                        if collection_ref:
                            sbi_template_collection = admin_db[collection_ref]
                        break
                break
        
        if not sbi_template_collection:
            print("❌ SBI land property template collection not found")
            return
        
        # Get the template structure
        template_docs = await sbi_template_collection.find({}).to_list(length=None)
        
        if not template_docs:
            print("❌ No template documents found")
            return
        
        print(f"\n🔍 ANALYZING SBI LAND PROPERTY TEMPLATE STRUCTURE")
        print(f"📊 Found {len(template_docs)} template documents")
        print("=" * 80)
        
        # Analyze each document
        for i, doc in enumerate(template_docs):
            print(f"\n📄 Document {i+1}:")
            template_metadata = doc.get("templateMetadata", {})
            
            if not template_metadata:
                print("   ⚠️ No templateMetadata found")
                continue
            
            tabs = template_metadata.get("tabs", [])
            print(f"   📂 Total Tabs: {len(tabs)}")
            
            # Analyze each tab
            for tab_idx, tab in enumerate(tabs):
                tab_name = tab.get("tabName") or tab.get("name", f"Tab_{tab_idx}")
                sections = tab.get("sections", [])
                direct_fields = tab.get("fields", [])
                
                print(f"\n   📁 TAB: '{tab_name}'")
                print(f"      📊 Sections: {len(sections)}")
                print(f"      📊 Direct Fields: {len(direct_fields)}")
                
                # Analyze sections
                if sections:
                    for sec_idx, section in enumerate(sections):
                        section_name = section.get("name", f"Section_{sec_idx}")
                        section_type = section.get("type", "unknown")
                        fields = section.get("fields", [])
                        
                        print(f"      📁 SECTION: '{section_name}' (Type: {section_type})")
                        print(f"         📊 Fields: {len(fields)}")
                        
                        # Show field details
                        if fields and len(fields) <= 10:  # Show all if <=10, else show sample
                            for field in fields:
                                field_id = field.get("fieldId", "NO_ID")
                                field_type = field.get("fieldType", "unknown")
                                label = field.get("label", "No Label")
                                print(f"         📄 {field_id} ({field_type}): {label}")
                        elif fields:
                            print(f"         📄 Sample fields:")
                            for field in fields[:3]:
                                field_id = field.get("fieldId", "NO_ID")
                                field_type = field.get("fieldType", "unknown")
                                print(f"            {field_id} ({field_type})")
                            print(f"         📄 ... and {len(fields)-3} more fields")
                
                # Analyze direct fields
                if direct_fields:
                    print(f"      📄 DIRECT FIELDS:")
                    if len(direct_fields) <= 5:
                        for field in direct_fields:
                            field_id = field.get("fieldId", "NO_ID")
                            field_type = field.get("fieldType", "unknown")
                            print(f"         {field_id} ({field_type})")
                    else:
                        for field in direct_fields[:3]:
                            field_id = field.get("fieldId", "NO_ID")
                            field_type = field.get("fieldType", "unknown")
                            print(f"         {field_id} ({field_type})")
                        print(f"         ... and {len(direct_fields)-3} more fields")
        
        print(f"\n" + "=" * 80)
        print(f"📋 TEMPLATE STRUCTURE ANALYSIS COMPLETE")
        
        # Now propose the data storage structure
        await propose_storage_structure(template_docs)
        
    except Exception as e:
        print(f"❌ Error analyzing template: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

async def propose_storage_structure(template_docs):
    """Propose the correct data storage structure based on template analysis"""
    
    print(f"\n🎯 PROPOSED DATA STORAGE STRUCTURE")
    print("=" * 80)
    
    print(f"""
Based on the SBI template analysis, here's how reports should be stored:

STRUCTURE OPTION 1 - TAB-BASED WITH DOCUMENTS ARRAYS:
{{
  "Property Details": {{
    "documents": [
      {{"fieldId": "agreement_to_sell", "value": "Available", "sectionName": "Documents"}},
      {{"fieldId": "owner_details", "value": "John Doe", "sectionName": "Address Details"}}
    ]
  }},
  "Site Characteristics": {{
    "documents": [
      {{"fieldId": "locality_surroundings", "value": "Well developed", "sectionName": "Locality"}}
    ]
  }}
}}

STRUCTURE OPTION 2 - HIERARCHICAL SECTION-BASED:
{{
  "Property Details": {{
    "Documents": {{
      "agreement_to_sell": "Available",
      "list_of_documents_produced": "Sale deed, Patta"
    }},
    "Address Details": {{
      "owner_details": "John Doe",
      "borrower_name": "ABC Company"
    }}
  }},
  "Site Characteristics": {{
    "Locality": {{
      "locality_surroundings": "Well developed"
    }}
  }}
}}

STRUCTURE OPTION 3 - FULL HIERARCHY WITH METADATA:
{{
  "tabs": [
    {{
      "tabName": "Property Details",
      "sections": [
        {{
          "sectionName": "Documents", 
          "sectionType": "form_group",
          "fields": [
            {{"fieldId": "agreement_to_sell", "value": "Available"}},
            {{"fieldId": "list_of_documents_produced", "value": "Sale deed"}}
          ]
        }}
      ]
    }}
  ]
}}
""")
    
    print(f"🤔 RECOMMENDATION:")
    print(f"""
I recommend OPTION 2 (Hierarchical Section-Based) because:

✅ Matches your template's Tab → Section → Fields hierarchy
✅ Easy for frontend to navigate and edit
✅ Preserves logical grouping from template design
✅ Backward compatible with existing flat structure
✅ Clear separation between tabs and sections
✅ Efficient for form rendering and validation

This structure allows:
- Easy access: report_data["Property Details"]["Documents"]["agreement_to_sell"] 
- Section-level operations
- Tab-level validation
- Dynamic form generation
- Clean save/load operations
""")

if __name__ == "__main__":
    print("🔍 SBI LAND PROPERTY TEMPLATE STRUCTURE ANALYSIS")
    print("🎯 This will analyze the template and propose storage structure")
    print("-" * 80)
    asyncio.run(analyze_sbi_template_structure())