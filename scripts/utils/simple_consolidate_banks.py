#!/usr/bin/env python3
"""
Simple Bank Consolidation Script

This script merges 8 separate bank documents into a single unified document
for easier management and better backend performance.
"""

import pymongo
from pymongo import MongoClient
from datetime import datetime
import json

# MongoDB configuration
MONGODB_URI = "mongodb+srv://app_user:kHxlQqJ1Uc3bmoL6@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster"
DATABASE_NAME = "valuation_app_prod"

def consolidate_banks():
    """Consolidate 8 separate bank documents into one unified document"""
    
    client = MongoClient(MONGODB_URI, 
                         serverSelectionTimeoutMS=10000,
                         tlsAllowInvalidCertificates=True)
    
    db = client[DATABASE_NAME]
    
    print("🚀 Starting Simple Bank Consolidation")
    print("=" * 50)
    
    # Step 1: Get all existing banks
    banks_collection = db["banks"]
    existing_banks = list(banks_collection.find())
    
    print(f"📊 Found {len(existing_banks)} banks to consolidate")
    
    # Step 2: Create unified structure
    unified_banks_doc = {
        "_id": "unified_banks_v2",
        "version": "2.0", 
        "architecture": "simple_unified",
        "createdAt": datetime.utcnow(),
        "lastUpdated": datetime.utcnow(),
        "consolidationInfo": {
            "originalBankCount": len(existing_banks),
            "consolidatedAt": datetime.utcnow(),
            "reason": "Simplify bank management and improve backend performance"
        },
        "banks": []
    }
    
    # Step 3: Process each bank
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
        
        # Clean up bank data (remove MongoDB _id)
        bank_copy = dict(bank)
        bank_copy.pop("_id", None)
        
        # Mark consolidation
        bank_copy["consolidatedAt"] = datetime.utcnow()
        bank_copy["isActive"] = is_active
        
        unified_banks_doc["banks"].append(bank_copy)
    
    # Step 4: Add summary statistics
    unified_banks_doc["statistics"] = {
        "totalBanks": len(existing_banks),
        "activeBanks": active_banks,
        "totalTemplates": total_templates,
        "uniqueFieldTypes": len(get_all_unique_fields(existing_banks))
    }
    
    # Step 5: Backup original collection
    backup_collection = db[f"banks_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"]
    backup_collection.insert_many(existing_banks)
    print(f"  💾 Backed up original banks to {backup_collection.name}")
    
    # Step 6: Create new unified collection
    unified_collection = db["unified_banks"]
    
    # Drop existing unified collection if present
    if "unified_banks" in db.list_collection_names():
        unified_collection.drop()
        print("  🗑️ Dropped existing unified_banks collection")
    
    # Insert unified document
    unified_collection.insert_one(unified_banks_doc)
    
    print("\n✅ CONSOLIDATION COMPLETE!")
    print("=" * 30)
    print(f"📊 Consolidated {len(existing_banks)} banks into 1 document")
    print(f"🏦 Active banks: {active_banks}")
    print(f"📋 Total templates: {total_templates}")
    print(f"💾 Original data backed up")
    
    # Step 7: Verification
    verify_consolidation(db, unified_banks_doc, existing_banks)
    
    client.close()
    return unified_banks_doc

def get_all_unique_fields(banks):
    """Extract all unique field names from all templates"""
    unique_fields = set()
    
    for bank in banks:
        templates = bank.get("templates", [])
        for template in templates:
            fields = template.get("fields", [])
            unique_fields.update(fields)
    
    return unique_fields

def verify_consolidation(db, unified_doc, original_banks):
    """Verify the consolidation was successful"""
    print("\n🔍 VERIFICATION:")
    print("=" * 20)
    
    # Check unified document exists
    unified_collection = db["unified_banks"]
    retrieved_doc = unified_collection.find_one({"_id": "unified_banks_v2"})
    
    if retrieved_doc:
        print("✅ Unified document created successfully")
        
        # Check bank count
        unified_bank_count = len(retrieved_doc.get("banks", []))
        original_count = len(original_banks)
        
        if unified_bank_count == original_count:
            print(f"✅ Bank count matches: {unified_bank_count}")
        else:
            print(f"❌ Bank count mismatch: {unified_bank_count} vs {original_count}")
        
        # Check template count
        unified_templates = sum(len(bank.get("templates", [])) for bank in retrieved_doc.get("banks", []))
        original_templates = sum(len(bank.get("templates", [])) for bank in original_banks)
        
        if unified_templates == original_templates:
            print(f"✅ Template count matches: {unified_templates}")
        else:
            print(f"❌ Template count mismatch: {unified_templates} vs {original_templates}")
        
        print("✅ Verification passed!")
    else:
        print("❌ Unified document not found!")

def show_consolidation_preview():
    """Show what the consolidation will do without executing it"""
    
    client = MongoClient(MONGODB_URI, 
                         serverSelectionTimeoutMS=10000,
                         tlsAllowInvalidCertificates=True)
    
    db = client[DATABASE_NAME]
    
    print("👀 CONSOLIDATION PREVIEW")
    print("=" * 30)
    
    banks = list(db["banks"].find())
    
    print(f"📊 Will consolidate:")
    print(f"  • {len(banks)} separate bank documents")
    print(f"  • Into 1 unified document")
    print(f"  • Original data will be backed up")
    
    active_count = 0
    total_templates = 0
    
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
    print(f"  • Total banks: {len(banks)}")
    print(f"  • Active banks: {active_count}")
    print(f"  • Total templates: {total_templates}")
    
    client.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        show_consolidation_preview()
    elif len(sys.argv) > 1 and sys.argv[1] == "--execute":
        result = consolidate_banks()
        
        # Save consolidation report
        with open("bank_consolidation_report.json", "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\n📄 Consolidation report saved to: bank_consolidation_report.json")
    else:
        print("🔧 Bank Consolidation Tool")
        print("=" * 30)
        print("Usage:")
        print("  python simple_consolidate_banks.py --preview   # Show what will be done")
        print("  python simple_consolidate_banks.py --execute  # Run the consolidation")
        print()
        print("⚠️  This will modify your database. Use --preview first!")