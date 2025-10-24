#!/usr/bin/env python3
"""
Simple test script for the file-based field management system (no database required)
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.utils.field_file_manager import FieldFileManager

def test_file_operations():
    """Test the file operations without database dependency"""
    print("🧪 Testing File Operations (No Database Required)")
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
    
    # Test 2: Create sample field data
    print("\n2️⃣ Creating sample field data...")
    sample_fields = [
        {
            "_id": "507f1f77bcf86cd799439011",
            "fieldName": "propertyAddress",
            "fieldType": "textarea",
            "label": "Property Address",
            "placeholder": "Enter complete property address",
            "isRequired": True,
            "fieldGroup": "property",
            "sortOrder": 1,
            "isActive": True
        },
        {
            "_id": "507f1f77bcf86cd799439012", 
            "fieldName": "contactNumber",
            "fieldType": "tel",
            "label": "Contact Number",
            "placeholder": "Enter contact number",
            "isRequired": True,
            "fieldGroup": "contact",
            "sortOrder": 2,
            "isActive": True
        },
        {
            "_id": "507f1f77bcf86cd799439013",
            "fieldName": "bankName",
            "fieldType": "select",
            "label": "Bank Name",
            "placeholder": "Select bank",
            "isRequired": True,
            "fieldGroup": "banking",
            "sortOrder": 3,
            "isActive": True
        }
    ]
    print(f"   ✅ Created {len(sample_fields)} sample fields")
    
    # Test 3: Save to file
    print("\n3️⃣ Saving fields to local file...")
    success = field_manager.write_fields(sample_fields)
    if success:
        print("   ✅ Successfully saved fields to local file")
        
        # Test 4: Read back from file
        print("\n4️⃣ Reading back from local file...")
        file_fields = field_manager.read_fields()
        if file_fields and len(file_fields) == len(sample_fields):
            print(f"   ✅ Successfully read {len(file_fields)} fields from local file")
            
            # Verify field data
            print("   Field details:")
            for field in file_fields:
                print(f"     - {field.get('label')} ({field.get('fieldName')})")
            
            # Test 5: File info after write
            print("\n5️⃣ File information after write...")
            final_info = field_manager.get_file_info()
            print(f"   File exists: {final_info.get('file_exists')}")
            print(f"   File size: {final_info.get('file_size')} bytes")
            print(f"   Generated at: {final_info.get('generated_at')}")
            print(f"   Version: {final_info.get('version')}")
            print(f"   Field count: {final_info.get('field_count')}")
            
            # Test 6: Delete file
            print("\n6️⃣ Testing file deletion...")
            delete_success = field_manager.delete_file()
            if delete_success:
                print("   ✅ Successfully deleted file")
                
                # Verify deletion
                after_delete_info = field_manager.get_file_info()
                print(f"   File exists after deletion: {after_delete_info.get('file_exists')}")
                
                print("\n🎉 All tests passed! File operations are working correctly.")
            else:
                print("   ⚠️ File deletion failed (file might not exist)")
        else:
            print("   ❌ Failed to read fields back from file")
    else:
        print("   ❌ Failed to save fields to local file")

if __name__ == "__main__":
    test_file_operations()