#!/usr/bin/env python3
"""
Fix field ordering issues in common_form_fields collection
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

async def fix_field_ordering() -> bool:
    """Fix the sortOrder gap in applicant_details group"""
    print('🔧 Fixing field ordering issues...')
    
    try:
        async with MultiDatabaseSession() as db:
            # Fix 1: Update Loan Amount Requested from sortOrder 4 to 3 to close the gap
            result = await db.update_one(
                'admin', 
                'common_form_fields',
                {'technicalName': 'loan_amount_requested'},
                {'sortOrder': 3},
                user_id='admin'
            )
            print(f'✅ Update result: {result} success')
            
            # Also ensure the field is in the correct group (it might be misnamed)
            # Let's check for any similar fields
            all_fields: List[Dict[str, Any]] = await db.find_many(
                'admin', 
                'common_form_fields', 
                {}, 
                sort=[('fieldGroup', 1), ('sortOrder', 1)]
            )
            
            print('🔍 Looking for loan/amount related fields:')
            for field in all_fields:
                technical_name = field.get('technicalName', '')
                if isinstance(technical_name, str) and ('loan' in technical_name.lower() or 'amount' in technical_name.lower()):
                    print(f'  Found: {technical_name} in {field.get("fieldGroup", "unknown")} with sortOrder {field.get("sortOrder", "?")}')
            
            # Verify applicant_details group order
            applicant_fields: List[Dict[str, Any]] = await db.find_many(
                'admin', 
                'common_form_fields', 
                {'fieldGroup': 'applicant_details'}, 
                sort=[('sortOrder', 1)]
            )
            
            print('📋 Current Applicant Details order:')
            for field in applicant_fields:
                print(f'  {field.get("sortOrder", "?")}: {field.get("uiDisplayName", "Unknown")} ({field.get("technicalName", "unknown")})')
            
            print()
            print('✅ Field ordering check complete!')
            
    except Exception as e:
        print(f'❌ Error fixing field ordering: {e}')
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = asyncio.run(fix_field_ordering())
    if not success:
        sys.exit(1)