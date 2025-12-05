#!/usr/bin/env python3
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test_direct():
    # MongoDB connection
    uri = "mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster"
    client = AsyncIOMotorClient(uri)
    admin_db = client.valuation_admin
    
    try:
        # Test document types query
        query = {
            "applicableBanks": {"$in": ["SBI", "*"]},
            "applicablePropertyTypes": {"$in": ["land-property", "Land", "*"]}
        }
        
        print("🔍 Testing document types query:")
        print(f"Query: {query}")
        
        docs = await admin_db.document_types.find(query).to_list(None)
        print(f"📊 Found {len(docs)} matching documents")
        
        for doc in docs[:3]:
            print(f"  - {doc.get('id')}: {doc.get('name')}")
            print(f"    Banks: {doc.get('applicableBanks')}")
            print(f"    Property Types: {doc.get('applicablePropertyTypes')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(test_direct())