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

async def check_all_templates():
    async with MultiDatabaseSession() as db:
        # Get all banks
        banks_collection = db.get_collection('admin', 'banks')
        banks = await banks_collection.find({'isActive': True}).to_list(100)
        
        for bank in banks:
            bank_code = bank.get('bankCode', 'N/A')
            print(f'\n🏦 {bank_code} Templates:')
            
            templates = bank.get('templates', [])
            if not templates:
                print('   ❌ No templates found')
                continue
                
            for i, template in enumerate(templates):
                template_id = template.get('templateId', 'N/A')
                template_code = template.get('templateCode', 'N/A')
                template_name = template.get('templateName', 'N/A')
                property_type = template.get('propertyType', 'N/A')
                has_pipeline = "✅ Present" if template.get("aggregationPipeline") else "❌ Missing"
                
                print(f'   {i+1}. templateId: {template_id}')
                print(f'      templateCode: {template_code}')
                print(f'      templateName: {template_name}')
                print(f'      propertyType: {property_type}')
                print(f'      aggregationPipeline: {has_pipeline}')
                print()

if __name__ == "__main__":
    asyncio.run(check_all_templates())