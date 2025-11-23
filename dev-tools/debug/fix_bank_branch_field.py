#!/usr/bin/env python3

"""
Directly update the bank_branch field configuration in MongoDB
"""

import asyncio
import sys
import os
from datetime import datetime, timezone

# Set MongoDB URI
os.environ['MONGODB_URI'] = "mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster"

# Add backend path
sys.path.insert(0, '/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend')

from database.multi_db_manager import MultiDatabaseSession

async def fix_bank_branch_field():
    """Update bank_branch field using MongoDB update operations"""
    try:
        print("🔧 Fixing bank_branch field configuration...")
        
        async with MultiDatabaseSession() as db:
            
            # Use MongoDB update operations to modify the field in place
            update_operations = {
                "$set": {
                    "fields.$[elem].dataSourceConfig": {
                        "collection": "banks",
                        "documentId": "all_banks_unified_v3",
                        "nestedPath": "banks.bankBranches",
                        "valueField": "branchId",
                        "labelField": "branchName",
                        "displayTemplate": "{branchName} - {branchAddress.city}",
                        "filter": {
                            "banks.bankCode": "{selected_bank_code}",
                            "banks.isActive": True,
                            "banks.bankBranches.isActive": True
                        },
                        "sortBy": "banks.bankBranches.branchName",
                        "dependsOn": "selected_bank",
                        "cascadeFields": {
                            "ifscCode": "banks.bankBranches.ifscCode",
                            "branchAddress": "banks.bankBranches.branchAddress",
                            "contactDetails": "banks.bankBranches.contactDetails"
                        }
                    },
                    "fields.$[elem].helpText": "Choose the specific bank branch from the selected bank's active branches",
                    "fields.$[elem].updatedAt": datetime.now(timezone.utc).isoformat(),
                    "updatedAt": datetime.now(timezone.utc).isoformat()
                }
            }
            
            array_filters = [{"elem.fieldId": "bank_branch"}]
            
            # Update the document
            result = await db.update_one(
                "admin",
                "common_form_fields", 
                {"_id": "common_fields"},
                update_operations,
                array_filters=array_filters
            )
            
            if result and result.modified_count > 0:
                print(f"✅ Successfully updated bank_branch field configuration")
                
                # Verify the update
                updated_doc = await db.find_one("admin", "common_form_fields", {"_id": "common_fields"})
                if updated_doc:
                    bank_branch_field = None
                    for field in updated_doc.get("fields", []):
                        if field.get("fieldId") == "bank_branch":
                            bank_branch_field = field
                            break
                    
                    if bank_branch_field:
                        config = bank_branch_field.get("dataSourceConfig", {})
                        print(f"\n📋 Updated Bank Branch Field Configuration:")
                        print(f"   🏦 Collection: {config.get('collection')}")
                        print(f"   📄 Document ID: {config.get('documentId')}")
                        print(f"   🔗 Nested Path: {config.get('nestedPath')}")
                        print(f"   🏷️  Value Field: {config.get('valueField')}")
                        print(f"   📝 Label Field: {config.get('labelField')}")
                        print(f"   🎯 Display: {config.get('displayTemplate')}")
                        
                        filters = config.get("filter", {})
                        print(f"   🔍 Filters:")
                        for key, value in filters.items():
                            print(f"      - {key}: {value}")
                        
                        cascade = config.get("cascadeFields", {})
                        print(f"   📞 Cascade Fields: {', '.join(cascade.keys())}")
                    
                return True
            else:
                print("❌ No documents were modified")
                return False
            
    except Exception as e:
        print(f"❌ Error fixing bank_branch field: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(fix_bank_branch_field())
    if success:
        print(f"\n🎉 SUCCESS: Bank branch field updated!")
        print(f"🔗 Now correctly references:")
        print(f"   📂 Collection: banks")
        print(f"   📄 Document: all_banks_unified_v3")
        print(f"   🌳 Path: banks.bankBranches (array)")
        print(f"   🎯 Filters by: bank code + active status")
        print(f"   📱 Shows: Branch Name - City")
        print(f"   📞 Auto-fills: IFSC, address, contacts")
    else:
        print(f"\n❌ FAILED to update bank branch field!")
        sys.exit(1)