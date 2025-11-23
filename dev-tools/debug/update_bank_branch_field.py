#!/usr/bin/env python3

"""
Update the bank_branch field to correctly reference the unified banks document structure
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

async def update_bank_branch_field():
    """Update bank_branch field to reference unified banks document structure"""
    try:
        print("🔧 Updating bank_branch field configuration...")
        
        async with MultiDatabaseSession() as db:
            
            # Find the common fields document
            common_doc = await db.find_one("admin", "common_form_fields", {"_id": "common_fields"})
            
            if not common_doc:
                print("❌ Common fields document not found")
                return False
            
            # Find the bank_branch field and update its configuration
            fields = common_doc.get("fields", [])
            updated = False
            
            for field in fields:
                if field.get("fieldId") == "bank_branch":
                    # Update the dataSourceConfig to match unified banks structure
                    field["dataSourceConfig"] = {
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
                    }
                    
                    # Update field metadata
                    field["updatedAt"] = datetime.now(timezone.utc).isoformat()
                    field["helpText"] = "Choose the specific bank branch from the selected bank's active branches"
                    
                    updated = True
                    print(f"✅ Updated bank_branch field configuration")
                    break
            
            if not updated:
                print("❌ bank_branch field not found")
                return False
            
            # Update the document's updatedAt timestamp
            common_doc["updatedAt"] = datetime.now(timezone.utc).isoformat()
            
            # Replace the document with updated configuration
            await db.delete_one("admin", "common_form_fields", {"_id": "common_fields"})
            await db.insert_one("admin", "common_form_fields", common_doc)
            
            print(f"✅ Successfully updated common_form_fields document")
            
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
                    print(f"   🎯 Filter: Bank active & Branch active")
                    print(f"   📞 Includes: IFSC Code, Address, Contact Details")
                else:
                    print("❌ Verification failed: bank_branch field not found")
                    return False
            
            return True
            
    except Exception as e:
        print(f"❌ Error updating bank_branch field: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(update_bank_branch_field())
    if success:
        print(f"\n🎉 SUCCESS: Bank branch field updated!")
        print(f"🔗 Now references: banks collection → all_banks_unified_v3 → banks.bankBranches")
        print(f"🎯 Dynamic filtering by selected bank code and active status")
        print(f"📱 UI will show: Branch Name - City format")
        print(f"📞 Auto-populates: IFSC code, address, and contact details")
    else:
        print(f"\n❌ FAILED to update bank branch field!")
        sys.exit(1)