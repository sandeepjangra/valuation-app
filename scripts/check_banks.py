#!/usr/bin/env python3
"""
Check what banks exist in the banks collection
"""

import os
import sys
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# Add parent directory to path to import backend modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

async def check_existing_banks():
    """Check what banks exist in the collection"""
    connection_string = os.getenv("MONGODB_URI")
    admin_db_name = os.getenv("MONGODB_ADMIN_DB_NAME", "valuation_admin")
    
    client = AsyncIOMotorClient(
        connection_string,
        serverSelectionTimeoutMS=30000,
        tlsAllowInvalidCertificates=True
    )
    
    try:
        db = client[admin_db_name]
        banks_collection = db["banks"]
        
        # Get all bank codes
        banks = await banks_collection.find({}, {"bankCode": 1, "bankName": 1}).to_list(length=None)
        
        print("📋 Existing banks in collection:")
        for bank in banks:
            print(f"   • {bank.get('bankCode')} - {bank.get('bankName')}")
        
        return [bank.get('bankCode') for bank in banks]
        
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(check_existing_banks())