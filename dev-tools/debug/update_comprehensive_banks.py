#!/usr/bin/env python3

"""
Replace the banks document with comprehensive Indian banks
"""

import asyncio
import sys
import os
import json
from datetime import datetime, timezone

# Set MongoDB URI
os.environ['MONGODB_URI'] = "mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster"

# Add backend path
sys.path.insert(0, '/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend')

from database.multi_db_manager import MultiDatabaseSession

async def update_comprehensive_banks():
    """Replace with comprehensive Indian banks document"""
    try:
        print("🏦 Updating to comprehensive Indian banks...")
        
        # Load the comprehensive banks JSON
        with open('/Users/sandeepjangra/Downloads/development/ValuationAppV1/comprehensive_indian_banks.json', 'r') as f:
            new_document = json.load(f)
        
        async with MultiDatabaseSession() as db:
            
            # Delete existing unified document and insert new one
            existing_doc = await db.find_one("admin", "banks", {"_id": {"$regex": "all_banks_unified"}})
            
            if existing_doc:
                await db.delete_one("admin", "banks", {"_id": existing_doc["_id"]})
                print(f"🗑️  Deleted existing unified document")
            
            await db.insert_one("admin", "banks", new_document)
            print(f"✅ Inserted comprehensive banks document")
            
            # Verify the final result
            final_doc = await db.find_one("admin", "banks", {"_id": {"$regex": "all_banks_unified"}})
            if final_doc and "banks" in final_doc:
                all_banks = final_doc["banks"]
                active_banks = [bank for bank in all_banks if bank.get("isActive")]
                total_templates = sum(len(bank.get("templates", [])) for bank in all_banks)
                active_templates = sum(
                    len([t for t in bank.get("templates", []) if t.get("isActive")])
                    for bank in all_banks
                )
                
                print(f"\n✅ Comprehensive Indian Banks Setup:")
                print(f"   🏦 Total Banks: {len(all_banks)}")
                print(f"   ✅ Active Banks: {len(active_banks)}")
                print(f"   📄 Total Templates: {total_templates}")
                print(f"   ✅ Active Templates: {active_templates}")
                
                # Show bank summary
                print(f"\n📋 Banks Summary:")
                for bank in all_banks:
                    bank_code = bank.get("bankCode", "")
                    bank_name = bank.get("bankName", "")
                    is_active = bank.get("isActive", False)
                    template_count = len(bank.get("templates", []))
                    status_icon = "✅" if is_active else "❌"
                    print(f"   {status_icon} {bank_code} - {bank_name} ({template_count} templates)")
                
                return True
            else:
                print(f"❌ Verification failed!")
                return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(update_comprehensive_banks())
    if success:
        print(f"\n🎉 SUCCESS: Comprehensive Indian banks updated!")
        print(f"📡 Test endpoints:")
        print(f"   - GET /api/banks (should show ~9 active banks)")
        print(f"   - GET /api/templates/PNB/land-property/aggregated-fields")
        print(f"   - GET /api/templates/CANARA/land-property/aggregated-fields")
    else:
        print(f"\n❌ FAILED to update banks!")
        sys.exit(1)