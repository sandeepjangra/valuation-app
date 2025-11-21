#!/usr/bin/env python3

import sys
import os
from pathlib import Path
import asyncio
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

from backend.database.multi_db_manager import MultiDatabaseSession

async def check_pnb_templates():
    async with MultiDatabaseSession() as db:
        bank = await db.find_one('admin', 'banks', {'bankCode': 'PNB'})
        if bank:
            print(f'🏦 PNB Bank found:')
            print(f'   bankName: {bank.get("bankName", "N/A")}')
            print(f'   isActive: {bank.get("isActive", "N/A")}')
            
            templates = bank.get('templates', [])
            print(f'   templates count: {len(templates)}')
            
            if templates:
                for i, template in enumerate(templates):
                    print(f'   Template {i+1}:')
                    print(f'      templateId: {template.get("templateId", "N/A")}')
                    print(f'      templateCode: {template.get("templateCode", "N/A")}')
                    print(f'      templateName: {template.get("templateName", "N/A")}')
                    print(f'      propertyType: {template.get("propertyType", "N/A")}')
                    print(f'      isActive: {template.get("isActive", "N/A")}')
                    print()
            else:
                print('   ❌ No templates found')
        else:
            print('❌ PNB bank not found')

if __name__ == "__main__":
    asyncio.run(check_pnb_templates())