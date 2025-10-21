#!/usr/bin/env python3
"""
Fix field ordering issues in common_form_fields collection
"""

import asyncio
import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))

from database.multi_db_manager import MultiDatabaseSession

async def fix_field_ordering():
    """Fix the sortOrder gap in applicant_details group"""
    print('🔧 Fixing field ordering issues...')
    
    try:
        async with MultiDatabaseSession() as db:
            # Fix 1: Update Loan Amount Requested from sortOrder 4 to 3 to close the gap
            result = await db.update_one(
                'admin', 
                'common_form_fields',
                {'technicalName': 'loan_amount_requested'},
                {'$set': {'sortOrder': 3}}
            )
            print(f'✅ Update result: {result.modified_count} document(s) modified')
            
            # Also ensure the field is in the correct group (it might be misnamed)
            # Let's check for any similar fields
            all_fields = await db.find_many(
                'admin', 
                'common_form_fields', 
                {}, 
                sort=[('fieldGroup', 1), ('sortOrder', 1)]
            )
            
            print('🔍 Looking for loan/amount related fields:')
            for field in all_fields:
                if 'loan' in field['technicalName'].lower() or 'amount' in field['technicalName'].lower():
                    print(f'  Found: {field["technicalName"]} in {field["fieldGroup"]} with sortOrder {field["sortOrder"]}')
            
            # Verify applicant_details group order
            applicant_fields = await db.find_many(
                'admin', 
                'common_form_fields', 
                {'fieldGroup': 'applicant_details'}, 
                sort=[('sortOrder', 1)]
            )
            
            print('📋 Current Applicant Details order:')
            for field in applicant_fields:
                print(f'  {field["sortOrder"]}: {field["uiDisplayName"]} ({field["technicalName"]})')
            
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