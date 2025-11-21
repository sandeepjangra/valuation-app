#!/usr/bin/env python3

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from backend.database.multi_db_manager import MultiDatabaseSession

async def check_templates():
    async with MultiDatabaseSession() as db:
        # Get SBI bank
        bank = await db.find_one('admin', 'banks', {'bankCode': 'SBI'})
        if bank and 'templates' in bank:
            print('🔍 SBI Templates:')
            for i, template in enumerate(bank['templates']):
                print(f'{i+1}. templateId: {template.get("templateId", "N/A")}')
                print(f'   templateCode: {template.get("templateCode", "N/A")}')
                print(f'   templateName: {template.get("templateName", "N/A")}')
                print(f'   propertyType: {template.get("propertyType", "N/A")}')
                print(f'   aggregationPipeline: {"✅ Present" if template.get("aggregationPipeline") else "❌ Missing"}')
                print()
        else:
            print('❌ SBI bank not found or no templates')

if __name__ == "__main__":
    asyncio.run(check_templates())