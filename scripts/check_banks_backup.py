#!/usr/bin/env python3
"""
Check the banks backup collection and verify SBI data
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_banks_backup():
    uri = "mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster&tlsAllowInvalidCertificates=true"
    client = AsyncIOMotorClient(uri)
    
    try:
        db = client.valuation_admin
        
        print("🔍 CHECKING BANKS BACKUP COLLECTION")
        print("=" * 40)
        
        # Check main banks collection
        main_banks = await db.banks.find().to_list(None)
        print(f"📊 Main banks collection: {len(main_banks)} banks")
        for bank in main_banks:
            print(f"   - {bank.get('bankCode')}: {bank.get('bankName')}")
        
        # Check backup banks collection
        backup_banks = await db.banks_backup_before_move_20251109_185537.find().to_list(None)
        print(f"\n📊 Backup banks collection: {len(backup_banks)} banks")
        for bank in backup_banks:
            print(f"   - {bank.get('bankCode')}: {bank.get('bankName')}")
            if bank.get('bankCode') == 'SBI':
                templates = bank.get('templates', [])
                print(f"      🎯 SBI Templates ({len(templates)}):")
                for template in templates:
                    print(f"         - {template.get('templateCode')}: {template.get('propertyType')}")
        
        # Check document types with correct property type mapping
        print(f"\n🔍 TESTING CORRECT DOCUMENT_TYPES QUERY:")
        query = {
            "applicableBanks": {"$in": ["SBI", "*"]}, 
            "applicablePropertyTypes": {"$in": ["Land", "*"]}  # Using 'Land' not 'land-property'
        }
        
        docs = await db.document_types.find(query).limit(5).to_list(None)
        print(f"📊 Found {len(docs)} document types for SBI/Land:")
        for doc in docs:
            print(f"   📄 {doc.get('documentId')}: {doc.get('uiDisplayName')}")
            print(f"      Type: {doc.get('fieldType')}, Required: {doc.get('isRequired')}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(check_banks_backup())