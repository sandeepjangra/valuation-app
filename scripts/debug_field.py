#!/usr/bin/env python3
"""
Debug what's preventing the sortOrder update
"""

import asyncio
import os
import sys
from typing import Any, Dict, List, Optional

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
sys.path.insert(0, backend_path)

try:
    from database.multi_db_manager import MultiDatabaseSession
except ImportError as e:
    print(f"❌ Error importing database manager: {e}")
    print("Please ensure you're running this from the project root and the backend dependencies are installed.")
    sys.exit(1)

async def debug_field() -> None:
    """Debug the loan amount field"""
    print('🔍 Debugging loan amount field...')
    
    try:
        async with MultiDatabaseSession() as db:
            # Find ALL records for this field
            all_records: List[Dict[str, Any]] = await db.find_many(
                'admin', 
                'common_form_fields',
                {'technicalName': 'loan_amount_requested'}
            )
            
            print(f'Found {len(all_records)} records:')
            for i, record in enumerate(all_records):
                print(f'  Record {i+1}:')
                print(f'    _id: {record.get("_id", "Unknown")}')
                print(f'    sortOrder: {record.get("sortOrder", "Not set")}')
                print(f'    isActive: {record.get("isActive", "Not set")}')
                print(f'    version: {record.get("version", "Not set")}')
                print(f'    uiDisplayName: {record.get("uiDisplayName", "Unknown")}')
                print()
                
            # Try to find the active one if versioning is used
            if len(all_records) > 1:
                active_record: Optional[Dict[str, Any]] = await db.find_one(
                    'admin', 
                    'common_form_fields',
                    {'technicalName': 'loan_amount_requested', 'isActive': True}
                )
                if active_record:
                    print(f'Active record: {active_record.get("_id", "Unknown")}')
                else:
                    print('Active record: None')
                
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(debug_field())