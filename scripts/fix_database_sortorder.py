#!/usr/bin/env python3
"""
Fix the actual database sortOrder gap issue
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

async def fix_database_sortorder() -> bool:
    """Fix the sortOrder gap in applicant_details group"""
    print('🔧 Fixing database sortOrder gap...')
    
    try:
        async with MultiDatabaseSession() as db:
            # Find the problematic field
            loan_field: Optional[Dict[str, Any]] = await db.find_one(
                'admin', 
                'common_form_fields',
                {'technicalName': 'loan_amount_requested'}
            )
            
            if loan_field:
                print(f'Found field: {loan_field.get("uiDisplayName", "Unknown")} with sortOrder {loan_field.get("sortOrder", "?")}')
                
                # Update to sortOrder 3 to close the gap using direct collection access
                collection = db.get_collection('admin', 'common_form_fields')
                result = await collection.update_one(
                    {'_id': loan_field['_id']},
                    {'$set': {'sortOrder': 3}, '$unset': {'$set': 1}}  # Remove the weird $set field too
                )
                
                print(f'✅ Updated field. Modified count: {getattr(result, "modified_count", 0)}')
                
                # Verify the fix
                updated_field: Optional[Dict[str, Any]] = await db.find_one(
                    'admin', 
                    'common_form_fields',
                    {'technicalName': 'loan_amount_requested'}
                )
                if updated_field:
                    print(f'✅ Verified: sortOrder is now {updated_field.get("sortOrder", "?")}')
                
                # Show all applicant_details fields
                applicant_fields: List[Dict[str, Any]] = await db.find_many(
                    'admin', 
                    'common_form_fields', 
                    {'fieldGroup': 'applicant_details'}, 
                    sort=[('sortOrder', 1)]
                )
                
                print('📋 Updated Applicant Details order:')
                for field in applicant_fields:
                    print(f'  {field.get("sortOrder", "?")}: {field.get("uiDisplayName", "Unknown")}')
                
                return True
            else:
                print('❌ Field not found')
                return False
                
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = asyncio.run(fix_database_sortorder())
    if not success:
        sys.exit(1)