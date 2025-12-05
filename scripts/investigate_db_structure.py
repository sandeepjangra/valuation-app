#!/usr/bin/env python3
"""
Investigate database and collection structure for document types
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def investigate_db_structure():
    """Investigate the actual database structure"""
    
    # MongoDB connection from .env
    uri = "mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster&tlsAllowInvalidCertificates=true"
    client = AsyncIOMotorClient(uri)
    
    try:
        print("🔍 INVESTIGATING DATABASE STRUCTURE")
        print("=" * 50)
        
        # 1. List all databases
        print("\n1️⃣ AVAILABLE DATABASES:")
        db_names = await client.list_database_names()
        for db_name in sorted(db_names):
            if not db_name.startswith(('admin', 'local', 'config')):
                print(f"   📁 {db_name}")
        
        # 2. Check each relevant database for collections
        for db_name in ['valuation_admin', 'admin']:
            if db_name in db_names:
                print(f"\n2️⃣ COLLECTIONS IN '{db_name}':")
                db = client[db_name]
                collections = await db.list_collection_names()
                for coll in sorted(collections):
                    count = await db[coll].count_documents({})
                    print(f"   📄 {coll} ({count} documents)")
                    
                    # Special check for document_types
                    if coll == 'document_types':
                        print(f"      🔍 Checking document_types structure...")
                        sample_doc = await db[coll].find_one()
                        if sample_doc:
                            print(f"      📋 Sample document keys: {list(sample_doc.keys())}")
                            if 'applicableBanks' in sample_doc:
                                print(f"      🏦 Sample applicableBanks: {sample_doc.get('applicableBanks')}")
                            if 'applicablePropertyTypes' in sample_doc:
                                print(f"      🏠 Sample applicablePropertyTypes: {sample_doc.get('applicablePropertyTypes')}")
        
        # 3. Specifically check document_types with SBI/land-property query
        print(f"\n3️⃣ TESTING DOCUMENT_TYPES QUERIES:")
        
        for db_name in ['valuation_admin', 'admin']:
            if db_name in db_names:
                db = client[db_name]
                if 'document_types' in await db.list_collection_names():
                    print(f"\n   Testing queries in {db_name}.document_types:")
                    
                    # Test different query variations
                    queries = [
                        {"applicableBanks": {"$in": ["SBI", "*"]}, "applicablePropertyTypes": {"$in": ["land-property", "*"]}},
                        {"applicableBanks": {"$in": ["SBI", "*"]}, "applicablePropertyTypes": {"$in": ["Land", "*"]}},
                        {"applicableBanks": {"$in": ["SBI", "*"]}},
                        {"applicablePropertyTypes": {"$in": ["land-property", "*"]}},
                        {}  # All documents
                    ]
                    
                    for i, query in enumerate(queries):
                        try:
                            count = await db.document_types.count_documents(query)
                            print(f"      Query {i+1}: {query}")
                            print(f"      Result: {count} documents")
                            
                            if count > 0 and count <= 3:  # Show a few sample documents
                                docs = await db.document_types.find(query).limit(2).to_list(None)
                                for doc in docs:
                                    print(f"        📄 {doc.get('id', doc.get('_id'))}: {doc.get('name', 'No name')}")
                                    print(f"           Banks: {doc.get('applicableBanks', [])}")
                                    print(f"           Types: {doc.get('applicablePropertyTypes', [])}")
                        except Exception as e:
                            print(f"      Query {i+1} failed: {e}")
        
        # 4. Check SBI template structure
        print(f"\n4️⃣ CHECKING SBI TEMPLATE STRUCTURE:")
        
        for db_name in ['valuation_admin', 'admin']:
            if db_name in db_names:
                db = client[db_name]
                collections = await db.list_collection_names()
                
                # Look for banks or templates collection
                for coll_name in ['banks', 'templates', 'sbi_land_property_details']:
                    if coll_name in collections:
                        print(f"\n   Checking {db_name}.{coll_name}:")
                        count = await db[coll_name].count_documents({})
                        print(f"   📊 Total documents: {count}")
                        
                        if coll_name == 'banks':
                            # Find SBI bank
                            sbi_bank = await db[coll_name].find_one({"bankCode": "SBI"})
                            if sbi_bank:
                                print(f"   ✅ Found SBI bank")
                                templates = sbi_bank.get('templates', [])
                                print(f"   📋 SBI Templates: {len(templates)}")
                                for template in templates:
                                    print(f"      - {template.get('templateCode')}: {template.get('templateName')}")
                            else:
                                print(f"   ❌ SBI bank not found")
                        
                        elif coll_name == 'sbi_land_property_details':
                            # Check template structure
                            sample = await db[coll_name].find_one()
                            if sample:
                                print(f"   📋 Sample template keys: {list(sample.keys())}")
                                if 'documents' in sample:
                                    print(f"   📄 Has documents array: {len(sample.get('documents', []))} docs")
                                if 'tabs' in sample:
                                    print(f"   📑 Has tabs array: {len(sample.get('tabs', []))} tabs")
        
    except Exception as e:
        print(f"❌ Investigation failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(investigate_db_structure())