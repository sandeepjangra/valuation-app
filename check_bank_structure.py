#!/usr/bin/env python3
"""
Quick script to check the updated banks collection structure
"""
import asyncio
from backend.database.multi_db_manager import MultiDatabaseSession

async def check_banks():
    try:
        print("Connecting to database...")
        async with MultiDatabaseSession() as db:
            print("Connected! Checking banks collection...")
            # First, let's see what banks exist
            banks = await db.find_many('admin', 'banks', {})
            print(f"Found {len(banks)} banks in collection:")
            
            if banks:
                print("\nFirst bank structure:")
                import pprint
                pprint.pprint(banks[0])
                
                # Look for SBI in different ways
                print("\nLooking for banks containing 'SBI'...")
                sbi_banks = await db.find_many('admin', 'banks', {'bankCode': 'SBI'})
                if sbi_banks:
                    print(f"Found {len(sbi_banks)} banks with bankCode=SBI")
                    pprint.pprint(sbi_banks[0])
                else:
                    # Try other field names
                    sbi_banks = await db.find_many('admin', 'banks', {'name': {'$regex': 'SBI', '$options': 'i'}})
                    if sbi_banks:
                        print(f"Found {len(sbi_banks)} banks with name containing SBI")
                        pprint.pprint(sbi_banks[0])
            else:
                print("No banks found in collection!")
                
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_banks())