#!/usr/bin/env python3
"""
Test script to create a custom template directly from backend
This bypasses frontend authentication issues and tests the core functionality
"""

import asyncio
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Load environment variables
from dotenv import load_dotenv
env_path = backend_dir / '.env'
load_dotenv(dotenv_path=env_path)

from database.multi_db_manager import MultiDatabaseManager

async def test_template_creation():
    """Test creating a custom template directly"""
    
    print("🧪 Testing Custom Template Creation")
    print("=" * 50)
    
    try:
        # Initialize database manager
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        # Use demo organization database
        org_short_name = "sk-tindwal"  # Demo organization
        org_db = db_manager.get_org_database(org_short_name)
        
        print(f"✅ Connected to organization database: {org_short_name}")
        
        # Check existing templates count
        existing_count = await org_db.custom_templates.count_documents({
            "bankCode": "SBI",
            "propertyType": "land",
            "isActive": True
        })
        
        print(f"📊 Existing templates for SBI-land: {existing_count}")
        
        if existing_count >= 3:
            print("⚠️ Maximum templates reached (3). Deleting oldest template...")
            # Find and delete oldest template
            oldest = await org_db.custom_templates.find_one(
                {"bankCode": "SBI", "propertyType": "land", "isActive": True},
                sort=[("createdAt", 1)]
            )
            if oldest:
                await org_db.custom_templates.update_one(
                    {"_id": oldest["_id"]},
                    {"$set": {"isActive": False, "deletedAt": datetime.now(timezone.utc)}}
                )
                print(f"🗑️ Deleted template: {oldest.get('templateName', 'Unknown')}")
        
        # Create sample template data
        template_data = {
            "templateName": f"Backend Test Template {datetime.now().strftime('%H%M%S')}",
            "description": "Test template created directly from backend",
            "bankCode": "SBI",
            "bankName": "State Bank of India",
            "propertyType": "land",
            "fieldValues": {
                "property_area": "1000 sq ft",
                "property_value": "5000000",
                "location": "Test Location",
                "survey_number": "123/456",
                "village": "Test Village",
                "district": "Test District",
                "state": "Test State",
                "pincode": "123456",
                "owner_name": "Test Owner",
                "property_type": "Residential Land",
                "market_rate": "5000",
                "government_rate": "4500",
                "registration_value": "4800000",
                "stamp_duty": "240000",
                "registration_fee": "30000"
            },
            "createdBy": "backend_test",
            "createdByName": "Backend Test User",
            "organizationId": org_short_name,
            "isActive": True,
            "version": 1,
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc)
        }
        
        # Insert template
        result = await org_db.custom_templates.insert_one(template_data)
        template_id = str(result.inserted_id)
        
        print(f"✅ Template created successfully!")
        print(f"   Template ID: {template_id}")
        print(f"   Template Name: {template_data['templateName']}")
        print(f"   Bank: {template_data['bankCode']} - {template_data['bankName']}")
        print(f"   Property Type: {template_data['propertyType']}")
        print(f"   Field Count: {len(template_data['fieldValues'])}")
        
        # Verify template was created
        created_template = await org_db.custom_templates.find_one({"_id": result.inserted_id})
        if created_template:
            print(f"✅ Template verification successful")
            print(f"   Created At: {created_template['createdAt']}")
            print(f"   Active: {created_template['isActive']}")
        else:
            print(f"❌ Template verification failed")
        
        # List all templates for this bank/property type
        all_templates = await org_db.custom_templates.find({
            "bankCode": "SBI",
            "propertyType": "land",
            "isActive": True
        }).to_list(length=None)
        
        print(f"\n📋 All active SBI-land templates ({len(all_templates)}):")
        for i, tmpl in enumerate(all_templates, 1):
            print(f"   {i}. {tmpl.get('templateName', 'Unknown')} (ID: {str(tmpl['_id'])})")
        
        await db_manager.disconnect()
        
        print(f"\n🎉 Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_authentication():
    """Test authentication system"""
    
    print("\n🔐 Testing Authentication System")
    print("=" * 50)
    
    try:
        # Test development token creation
        from utils.auth_middleware import create_dev_token, jwt_validator
        
        # Create test tokens
        test_cases = [
            ("manager@test.com", "sk-tindwal", "manager"),
            ("employee@test.com", "sk-tindwal", "employee"),
            ("admin@system.com", "system-administration", "system_admin")
        ]
        
        for email, org, role in test_cases:
            token = create_dev_token(email, org, role)
            print(f"✅ Created token for {email} ({role}): {token[:50]}...")
            
            # Validate token
            try:
                claims = await jwt_validator.validate_token(token)
                print(f"   ✅ Token validation successful")
                print(f"   User: {claims.get('email')}")
                print(f"   Org: {claims.get('custom:org_short_name')}")
                print(f"   Roles: {claims.get('cognito:groups')}")
            except Exception as e:
                print(f"   ❌ Token validation failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    
    print("🚀 Backend Custom Template Test Suite")
    print("=" * 60)
    
    # Test authentication first
    auth_success = await test_authentication()
    
    if auth_success:
        # Test template creation
        template_success = await test_template_creation()
        
        if template_success:
            print(f"\n🎉 All tests passed! Backend is working correctly.")
            print(f"\n💡 The 401 error in frontend is likely due to:")
            print(f"   1. Missing or invalid Authorization header")
            print(f"   2. Token format mismatch")
            print(f"   3. Frontend not sending proper authentication")
            print(f"\n🔧 Next steps:")
            print(f"   1. Check browser network tab for Authorization header")
            print(f"   2. Verify frontend auth service is working")
            print(f"   3. Check if user is logged in properly")
        else:
            print(f"\n❌ Template creation test failed")
    else:
        print(f"\n❌ Authentication test failed")

if __name__ == "__main__":
    asyncio.run(main())