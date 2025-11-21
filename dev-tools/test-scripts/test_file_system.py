#!/usr/bin/env python3
"""
Test script for the new file-based field management system
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.utils.field_file_manager import FieldFileManager
from backend.database.multi_db_manager import MultiDatabaseSession

async def test_file_system():
    """Test the file-based field management system"""
    print("🧪 Testing File-Based Field Management System")
    print("=" * 50)
    
    # Initialize the field file manager
    field_manager = FieldFileManager()
    
    # Test 1: Check initial file status
    print("\n1️⃣ Checking initial file status...")
    file_info = field_manager.get_file_info()
    print(f"   File exists: {file_info.get('file_exists', False)}")
    if file_info.get('file_exists'):
        print(f"   Last modified: {file_info.get('last_modified')}")
        print(f"   File size: {file_info.get('file_size')} bytes")
    
    # Test 2: Try to read from file (should fall back to database)
    print("\n2️⃣ Reading fields from file...")
    fields = field_manager.read_fields()
    if fields:
        print(f"   ✅ Read {len(fields)} fields from local file")
    else:
        print("   ⚠️ No fields found in local file - will need database refresh")
    
    # Test 3: Fetch from database and save to file
    print("\n3️⃣ Fetching fields from database...")
    try:
        async with MultiDatabaseSession() as db:
            db_fields = await db.find_many(
                "admin", 
                "common_form_fields", 
                {"isActive": True}, 
                sort=[("fieldGroup", 1), ("sortOrder", 1)]
            )
            
            print(f"   ✅ Fetched {len(db_fields)} fields from database")
            
            # Test 4: Save to file
            print("\n4️⃣ Saving fields to local file...")
            success = field_manager.write_fields(db_fields)
            if success:
                print("   ✅ Successfully saved fields to local file")
                
                # Test 5: Read back from file
                print("\n5️⃣ Reading back from local file...")
                file_fields = field_manager.read_fields()
                if file_fields and len(file_fields) == len(db_fields):
                    print(f"   ✅ Successfully read {len(file_fields)} fields from local file")
                    
                    # Test 6: File info after write
                    print("\n6️⃣ File information after write...")
                    final_info = field_manager.get_file_info()
                    print(f"   File exists: {final_info.get('file_exists')}")
                    print(f"   File size: {final_info.get('file_size')} bytes")
                    print(f"   Generated at: {final_info.get('generated_at')}")
                    print(f"   Version: {final_info.get('version')}")
                    print(f"   Field count: {final_info.get('field_count')}")
                    
                    print("\n🎉 All tests passed! File-based system is working correctly.")
                else:
                    print("   ❌ Failed to read fields back from file")
            else:
                print("   ❌ Failed to save fields to local file")
                
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        print("   (This is expected if MongoDB is not running)")

if __name__ == "__main__":
    asyncio.run(test_file_system())