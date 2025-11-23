#!/usr/bin/env python3

"""
Safe script to replace the existing banks document
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

async def replace_banks_document():
    """Safely replace the existing banks document"""
    try:
        print("🔄 Safely replacing banks document...")
        
        # Load the JSON document
        with open('/Users/sandeepjangra/Downloads/development/ValuationAppV1/unified_banks_document.json', 'r') as f:
            new_document = json.load(f)
        
        async with MultiDatabaseSession() as db:
            
            # Check if document exists
            existing_doc = await db.find_one("admin", "banks", {"_id": "all_banks_unified_v2"})
            if existing_doc:
                print(f"📄 Found existing document with _id: all_banks_unified_v2")
                
                # Replace the existing document
                await db.replace_one("admin", "banks", {"_id": "all_banks_unified_v2"}, new_document)
                print(f"✅ Successfully REPLACED existing document")
            else:
                print(f"📄 No existing document found, inserting new one")
                
                # Insert new document
                await db.insert_one("admin", "banks", new_document)
                print(f"✅ Successfully INSERTED new document")
            
            # Verify the final result
            final_doc = await db.find_one("admin", "banks", {"_id": "all_banks_unified_v2"})
            if final_doc and "banks" in final_doc:
                total_banks = len(final_doc["banks"])
                total_branches = sum(len(bank.get("bankBranches", [])) for bank in final_doc["banks"])
                total_templates = sum(len(bank.get("templates", [])) for bank in final_doc["banks"])
                
                print(f"\n✅ Final verification:")
                print(f"   🏦 Total Banks: {total_banks}")
                print(f"   🏢 Total Branches: {total_branches}")
                print(f"   📄 Total Templates: {total_templates}")
                
                # Show active counts
                active_banks = [bank for bank in final_doc["banks"] if bank.get("isActive")]
                active_branches = sum(
                    len([branch for branch in bank.get("bankBranches", []) if branch.get("isActive")])
                    for bank in final_doc["banks"]
                )
                
                print(f"   ✅ Active Banks: {len(active_banks)}")
                print(f"   ✅ Active Branches: {active_branches}")
                
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
    success = asyncio.run(replace_banks_document())
    if success:
        print(f"\n🎉 SUCCESS: Banks document safely updated!")
        print(f"📡 You can now test the API endpoints:")
        print(f"   - GET /api/banks")
        print(f"   - GET /api/templates/SBI/land-property/aggregated-fields")
    else:
        print(f"\n❌ FAILED to update document!")
        sys.exit(1)