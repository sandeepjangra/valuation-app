#!/usr/bin/env python3
"""
Debug script to check template configuration
"""
import asyncio
from backend.database.multi_db_manager import MultiDatabaseSession

async def debug_template():
    try:
        async with MultiDatabaseSession() as db:
            # Get SBI bank
            bank = await db.find_one('admin', 'banks', {'bankCode': 'SBI'})
            if bank:
                print('SBI Templates:')
                templates = bank.get('templates', [])
                for template in templates:
                    if template.get('propertyType') == 'land':
                        print(f"Template: {template.get('templateName')}")
                        fields_config = template.get('fields', {})
                        
                        print("\nCommon Fields Config:")
                        common_config = fields_config.get('commonFields', {})
                        print(f"  Collection: {common_config.get('collectionRef')}")
                        print(f"  Filter: {common_config.get('filter')}")
                        
                        print("\nBank Fields Config:")
                        bank_config = fields_config.get('bankSpecificFields', {})
                        print(f"  Collection: {bank_config.get('collectionRef')}")
                        print(f"  Filter: {bank_config.get('filter')}")
                        break
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    asyncio.run(debug_template())