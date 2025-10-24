#!/usr/bin/env python3
"""
Direct MongoDB update to fix sortOrder gap
"""

import os
from typing import Any, Dict, List, Optional
from pymongo import MongoClient

def fix_sortorder() -> bool:
    """Fix the sortOrder gap directly using pymongo"""
    print('🔧 Fixing database sortOrder gap...')
    
    # Get connection string from environment
    connection_string = os.getenv("MONGODB_URI")
    if not connection_string:
        print("❌ MONGODB_URI environment variable not found")
        return False
    
    try:
        # Connect to MongoDB
        client: MongoClient[Dict[str, Any]] = MongoClient(connection_string)
        db = client['valuation_admin']
        collection = db['common_form_fields']
        
        # Find the loan amount field
        loan_field: Optional[Dict[str, Any]] = collection.find_one({'technicalName': 'loan_amount_requested'})
        
        if loan_field:
            print(f'Found field: {loan_field.get("uiDisplayName", "Unknown")} with sortOrder {loan_field.get("sortOrder", "?")}')
            print(f'Field ID: {loan_field.get("_id", "Unknown")}')
            
            # Update to sortOrder 3
            result = collection.update_one(
                {'_id': loan_field['_id']},
                {
                    '$set': {'sortOrder': 3},
                    '$unset': {'$set': 1}  # Remove the weird $set field if it exists
                }
            )
            
            print(f'✅ Update result: matched={result.matched_count}, modified={result.modified_count}')
            
            # Verify the fix
            updated_field: Optional[Dict[str, Any]] = collection.find_one({'technicalName': 'loan_amount_requested'})
            if updated_field:
                print(f'✅ Verified: sortOrder is now {updated_field.get("sortOrder", "?")}')
            
            # Show all applicant_details fields
            applicant_fields: List[Dict[str, Any]] = list(collection.find(
                {'fieldGroup': 'applicant_details'}
            ).sort('sortOrder', 1))
            
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
    success = fix_sortorder()
    if not success:
        exit(1)