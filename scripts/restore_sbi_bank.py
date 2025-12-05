#!/usr/bin/env python3
"""
Fix the banks collection by restoring SBI data from backup
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def restore_sbi_bank():
    uri = "mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster&tlsAllowInvalidCertificates=true"
    client = AsyncIOMotorClient(uri)
    
    try:
        db = client.valuation_admin
        
        print("🔍 FIXING BANKS COLLECTION")
        print("=" * 40)
        
        # Check current main banks collection
        main_banks = await db.banks.find().to_list(None)
        print(f"📊 Current main banks: {len(main_banks)}")
        for bank in main_banks:
            print(f"   - {bank.get('bankCode', 'None')}: {bank.get('bankName', 'None')}")
        
        # Get SBI from backup
        sbi_backup = await db.banks_backup_before_move_20251109_185537.find_one({"bankCode": "SBI"})
        if sbi_backup:
            print(f"\n✅ Found SBI in backup collection")
            print(f"   Templates: {len(sbi_backup.get('templates', []))}")
            
            # Check if SBI already exists in main collection
            existing_sbi = await db.banks.find_one({"bankCode": "SBI"})
            
            if existing_sbi:
                print(f"🔄 SBI exists in main collection, updating...")
                result = await db.banks.replace_one({"bankCode": "SBI"}, sbi_backup)
                print(f"✅ Updated SBI: matched={result.matched_count}, modified={result.modified_count}")
            else:
                print(f"➕ SBI not in main collection, inserting...")
                # Remove _id to avoid conflicts
                sbi_backup.pop('_id', None)
                result = await db.banks.insert_one(sbi_backup)
                print(f"✅ Inserted SBI: {result.inserted_id}")
            
            # Verify the fix
            print(f"\n🔍 VERIFICATION:")
            updated_banks = await db.banks.find().to_list(None)
            print(f"📊 Banks after fix: {len(updated_banks)}")
            for bank in updated_banks:
                if bank.get('bankCode') == 'SBI':
                    templates = bank.get('templates', [])
                    print(f"   ✅ SBI: {len(templates)} templates")
                    for template in templates:
                        print(f"      - {template.get('templateCode')}: {template.get('templateName')}")
                else:
                    print(f"   - {bank.get('bankCode', 'None')}: {bank.get('bankName', 'None')}")
        else:
            print(f"❌ SBI not found in backup collection")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(restore_sbi_bank())