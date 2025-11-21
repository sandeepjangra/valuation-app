#!/usr/bin/env python3
"""
True Single Document Consolidation Script

This script replaces 8 separate bank documents with 1 single unified document
in the banks collection itself (not a separate collection).
"""

import pymongo
from pymongo import MongoClient
from datetime import datetime
import json

# MongoDB configuration
MONGODB_URI = "mongodb+srv://app_user:kHxlQqJ1Uc3bmoL6@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster"
DATABASE_NAME = "valuation_app_prod"

def true_single_document_consolidation():
    """Replace 8 separate bank documents with 1 single unified document"""
    
    client = MongoClient(MONGODB_URI, 
                         serverSelectionTimeoutMS=10000,
                         tlsAllowInvalidCertificates=True)
    
    db = client[DATABASE_NAME]
    
    print("🚀 TRUE SINGLE DOCUMENT CONSOLIDATION")
    print("=" * 50)
    
    # Step 1: Get all existing separate bank documents
    banks_collection = db["banks"]
    existing_banks = list(banks_collection.find())
    
    print(f"📊 Found {len(existing_banks)} separate bank documents")
    
    # Step 2: Create final unified structure
    unified_document = {
        "_id": "all_banks_unified",
        "documentType": "unified_banks_collection",
        "version": "3.0", 
        "architecture": "single_document",
        "createdAt": datetime.utcnow(),
        "lastUpdated": datetime.utcnow(),
        "consolidationInfo": {
            "originalDocumentCount": len(existing_banks),
            "consolidatedAt": datetime.utcnow(),
            "consolidationType": "single_document_replacement",
            "reason": "Replace multiple bank documents with single unified document"
        },
        "banks": []
    }
    
    # Step 3: Process each bank and add to unified document
    total_templates = 0
    active_banks = 0
    
    for bank in existing_banks:
        bank_name = bank.get("bankName", "Unknown")
        bank_code = bank.get("bankCode", "")
        templates = bank.get("templates", [])
        is_active = len(templates) > 0  # Banks with templates are active
        
        if is_active:
            active_banks += 1
        
        total_templates += len(templates)
        
        print(f"  🏦 Processing {bank_name} ({bank_code})")
        print(f"      Templates: {len(templates)} {'✅' if is_active else '⚠️'}")
        
        # Clean up bank data (remove MongoDB _id and add consolidation metadata)
        bank_copy = dict(bank)
        bank_copy.pop("_id", None)
        
        # Mark consolidation
        bank_copy["consolidatedAt"] = datetime.utcnow()
        bank_copy["isActive"] = is_active
        bank_copy["originalId"] = str(bank.get("_id"))  # Keep reference to original
        
        unified_document["banks"].append(bank_copy)
    
    # Step 4: Add summary statistics
    unified_document["statistics"] = {
        "totalBanks": len(existing_banks),
        "activeBanks": active_banks,
        "totalTemplates": total_templates,
        "uniqueFieldTypes": len(get_all_unique_fields(existing_banks))
    }
    
    # Step 5: Backup original collection
    backup_collection = db[f"banks_backup_original_{datetime.now().strftime('%Y%m%d_%H%M%S')}"]
    backup_collection.insert_many(existing_banks)
    print(f"  💾 Backed up original banks to {backup_collection.name}")
    
    # Step 6: REPLACE the banks collection with single document
    print("🔄 Replacing banks collection with single unified document...")
    
    # Clear existing banks collection completely
    banks_collection.delete_many({})
    print("  🗑️ Cleared existing bank documents")
    
    # Insert single unified document
    banks_collection.insert_one(unified_document)
    print("  ✅ Inserted single unified document")
    
    # Step 7: Clean up the separate unified_banks collection (no longer needed)
    if "unified_banks" in db.list_collection_names():
        db["unified_banks"].drop()
        print("  🧹 Removed old unified_banks collection")
    
    print("\n✅ TRUE CONSOLIDATION COMPLETE!")
    print("=" * 35)
    print(f"📊 Replaced {len(existing_banks)} separate documents with 1 unified document")
    print(f"🏦 Active banks: {active_banks}")
    print(f"📋 Total templates: {total_templates}")
    print(f"💾 Original data backed up")
    
    # Step 8: Verification
    verify_single_document_consolidation(db, unified_document, existing_banks)
    
    client.close()
    return unified_document

def get_all_unique_fields(banks):
    """Extract all unique field names from all templates"""
    unique_fields = set()
    
    for bank in banks:
        templates = bank.get("templates", [])
        for template in templates:
            fields = template.get("fields", [])
            unique_fields.update(fields)
    
    return unique_fields

def verify_single_document_consolidation(db, unified_doc, original_banks):
    """Verify the single document consolidation was successful"""
    print("\n🔍 VERIFICATION:")
    print("=" * 20)
    
    # Check that banks collection now has only 1 document
    banks_collection = db["banks"]
    total_docs = banks_collection.count_documents({})
    
    if total_docs == 1:
        print("✅ Banks collection has exactly 1 document")
        
        # Get the single document
        single_doc = banks_collection.find_one({"_id": "all_banks_unified"})
        
        if single_doc:
            print("✅ Unified document found with correct ID")
            
            # Check bank count
            unified_bank_count = len(single_doc.get("banks", []))
            original_count = len(original_banks)
            
            if unified_bank_count == original_count:
                print(f"✅ Bank count matches: {unified_bank_count}")
            else:
                print(f"❌ Bank count mismatch: {unified_bank_count} vs {original_count}")
            
            # Check template count
            unified_templates = sum(len(bank.get("templates", [])) for bank in single_doc.get("banks", []))
            original_templates = sum(len(bank.get("templates", [])) for bank in original_banks)
            
            if unified_templates == original_templates:
                print(f"✅ Template count matches: {unified_templates}")
            else:
                print(f"❌ Template count mismatch: {unified_templates} vs {original_templates}")
            
            print("✅ Single document consolidation verified!")
        else:
            print("❌ Unified document not found!")
    else:
        print(f"❌ Banks collection has {total_docs} documents (should be 1)")

def show_consolidation_preview():
    """Show what the single document consolidation will do"""
    
    client = MongoClient(MONGODB_URI, 
                         serverSelectionTimeoutMS=10000,
                         tlsAllowInvalidCertificates=True)
    
    db = client[DATABASE_NAME]
    
    print("👀 SINGLE DOCUMENT CONSOLIDATION PREVIEW")
    print("=" * 45)
    
    banks_count = db["banks"].count_documents({})
    banks = list(db["banks"].find()) if banks_count <= 10 else []
    
    print(f"📊 Current state:")
    print(f"  • {banks_count} separate documents in banks collection")
    
    print(f"\n📊 Will consolidate to:")
    print(f"  • 1 single document in banks collection")
    print(f"  • All {banks_count} banks inside that single document")
    print(f"  • Original documents will be backed up")
    
    active_count = 0
    total_templates = 0
    
    if banks:
        print(f"\n🏦 Banks to be consolidated:")
        for bank in banks:
            name = bank.get("bankName", "Unknown")
            code = bank.get("bankCode", "")
            templates = len(bank.get("templates", []))
            
            if templates > 0:
                active_count += 1
            
            total_templates += templates
            status = "✅ Active" if templates > 0 else "⚠️ No templates"
            
            print(f"  • {name} ({code}) - {templates} templates {status}")
    
    print(f"\n📈 Summary:")
    print(f"  • Total banks: {banks_count}")
    print(f"  • Active banks: {active_count}")
    print(f"  • Total templates: {total_templates}")
    print(f"  • Final result: 1 document containing all {banks_count} banks")
    
    client.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        show_consolidation_preview()
    elif len(sys.argv) > 1 and sys.argv[1] == "--execute":
        print("⚠️  This will replace all bank documents with a single unified document.")
        print("⚠️  Original documents will be backed up.")
        confirm = input("\nContinue with single document consolidation? (y/N): ").lower().strip()
        
        if confirm == 'y':
            result = true_single_document_consolidation()
            
            # Save consolidation report
            with open("single_document_consolidation_report.json", "w") as f:
                json.dump(result, f, indent=2, default=str)
            print(f"\n📄 Consolidation report saved to: single_document_consolidation_report.json")
        else:
            print("❌ Consolidation cancelled")
    else:
        print("🔧 True Single Document Consolidation Tool")
        print("=" * 45)
        print("Usage:")
        print("  python true_single_document.py --preview   # Show what will be done")
        print("  python true_single_document.py --execute  # Run the consolidation")
        print()
        print("⚠️  This will replace multiple documents with ONE document!")
        print("⚠️  Use --preview first to see what will happen!")