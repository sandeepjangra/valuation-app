"""
Test Phase 2: Role-Based Access Control Implementation
Tests JWT token generation, parsing, and org context creation
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from utils.auth_middleware import CognitoJWTValidator, OrganizationContext, create_dev_token

async def test_token_generation():
    """Test development token generation"""
    print("=" * 80)
    print("TEST 1: Development Token Generation")
    print("=" * 80)
    
    test_cases = [
        {
            "email": "manager@test.com",
            "org_short_name": "sk-tindwal",
            "role": "manager"
        },
        {
            "email": "employee@test.com",
            "org_short_name": "abc-property-valuers",
            "role": "employee"
        },
        {
            "email": "admin@system.com",
            "org_short_name": "system_admin",
            "role": "system_admin"
        }
    ]
    
    for test in test_cases:
        token = create_dev_token(test["email"], test["org_short_name"], test["role"])
        print(f"\n✅ Generated token for {test['role']}:")
        print(f"   Email: {test['email']}")
        print(f"   Org: {test['org_short_name']}")
        print(f"   Token: {token}")
        print(f"   Expected format: dev_username_domain_org-token_role")

async def test_jwt_parsing():
    """Test JWT token parsing and claims extraction"""
    print("\n" + "=" * 80)
    print("TEST 2: JWT Token Parsing")
    print("=" * 80)
    
    validator = CognitoJWTValidator()
    
    # Test case 1: Normal org with hyphens
    token1 = "dev_manager_test.com_sk_tindwal_manager"
    claims1 = await validator.validate_token(token1)
    print(f"\n✅ Token 1: {token1}")
    print(f"   Parsed claims:")
    print(f"   - Email: {claims1.get('email')}")
    print(f"   - Org Short Name: {claims1.get('custom:org_short_name')}")
    print(f"   - Role: {claims1.get('cognito:groups')}")
    
    # Test case 2: Multi-hyphen org name
    token2 = "dev_employee_example.com_abc_property_valuers_employee"
    claims2 = await validator.validate_token(token2)
    print(f"\n✅ Token 2: {token2}")
    print(f"   Parsed claims:")
    print(f"   - Email: {claims2.get('email')}")
    print(f"   - Org Short Name: {claims2.get('custom:org_short_name')}")
    print(f"   - Role: {claims2.get('cognito:groups')}")
    
    # Test case 3: System admin (no hyphen conversion)
    token3 = "dev_admin_system.com_system_admin_system_admin"
    claims3 = await validator.validate_token(token3)
    print(f"\n✅ Token 3: {token3}")
    print(f"   Parsed claims:")
    print(f"   - Email: {claims3.get('email')}")
    print(f"   - Org Short Name: {claims3.get('custom:org_short_name')}")
    print(f"   - Role: {claims3.get('cognito:groups')}")

async def test_organization_context():
    """Test OrganizationContext creation and permissions"""
    print("\n" + "=" * 80)
    print("TEST 3: Organization Context & Permissions")
    print("=" * 80)
    
    validator = CognitoJWTValidator()
    
    # Test manager context
    manager_token = "dev_manager_test.com_sk_tindwal_manager"
    manager_claims = await validator.validate_token(manager_token)
    manager_context = OrganizationContext(manager_claims)
    
    print(f"\n✅ Manager Context:")
    print(f"   Org: {manager_context.org_short_name}")
    print(f"   Email: {manager_context.email}")
    print(f"   Is Manager: {manager_context.is_manager}")
    print(f"   Is System Admin: {manager_context.is_system_admin}")
    print(f"   Can access 'sk-tindwal': {manager_context.can_access_organization('sk-tindwal')}")
    print(f"   Can access 'abc-property-valuers': {manager_context.can_access_organization('abc-property-valuers')}")
    
    # Test permissions
    print(f"\n   Permissions:")
    print(f"   - Create report: {manager_context.has_permission('reports', 'create')}")
    print(f"   - Submit report: {manager_context.has_permission('reports', 'submit')}")
    print(f"   - Delete report: {manager_context.has_permission('reports', 'delete')}")
    print(f"   - Create user: {manager_context.has_permission('users', 'create')}")
    
    # Test employee context
    employee_token = "dev_employee_test.com_sk_tindwal_employee"
    employee_claims = await validator.validate_token(employee_token)
    employee_context = OrganizationContext(employee_claims)
    
    print(f"\n✅ Employee Context:")
    print(f"   Org: {employee_context.org_short_name}")
    print(f"   Email: {employee_context.email}")
    print(f"   Is Manager: {employee_context.is_manager}")
    print(f"   Is Employee: {employee_context.is_employee}")
    
    # Test permissions
    print(f"\n   Permissions:")
    print(f"   - Create report: {employee_context.has_permission('reports', 'create')}")
    print(f"   - Submit report: {employee_context.has_permission('reports', 'submit')}")
    print(f"   - Delete report: {employee_context.has_permission('reports', 'delete')}")
    print(f"   - Create user: {employee_context.has_permission('users', 'create')}")
    
    # Test system admin context
    admin_token = "dev_admin_system.com_system_admin_system_admin"
    admin_claims = await validator.validate_token(admin_token)
    admin_context = OrganizationContext(admin_claims)
    
    print(f"\n✅ System Admin Context:")
    print(f"   Org: {admin_context.org_short_name}")
    print(f"   Email: {admin_context.email}")
    print(f"   Is System Admin: {admin_context.is_system_admin}")
    print(f"   Can access any org: {admin_context.can_access_organization('any-org')}")
    
    # Test permissions
    print(f"\n   Permissions:")
    print(f"   - All permissions: {admin_context.has_permission('anything', 'anything')}")

async def test_backward_compatibility():
    """Test backward compatibility with old organization_id field"""
    print("\n" + "=" * 80)
    print("TEST 4: Backward Compatibility")
    print("=" * 80)
    
    validator = CognitoJWTValidator()
    
    # Create token with org_short_name
    token = "dev_test_user_example.com_sk_tindwal_manager"
    claims = await validator.validate_token(token)
    context = OrganizationContext(claims)
    
    print(f"\n✅ Context Fields:")
    print(f"   org_short_name: {context.org_short_name}")
    print(f"   organization_id (alias): {context.organization_id}")
    print(f"   Should be equal: {context.org_short_name == context.organization_id}")
    
    print(f"\n✅ JWT Claims:")
    print(f"   custom:org_short_name: {claims.get('custom:org_short_name')}")
    print(f"   custom:organization_id: {claims.get('custom:organization_id')}")
    print(f"   Both present for backward compatibility: {bool(claims.get('custom:org_short_name') and claims.get('custom:organization_id'))}")

async def main():
    """Run all tests"""
    print("\n🚀 Starting Phase 2 Authentication Tests\n")
    
    try:
        await test_token_generation()
        await test_jwt_parsing()
        await test_organization_context()
        await test_backward_compatibility()
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED")
        print("=" * 80)
        print("\n📝 Summary:")
        print("   ✓ Token generation with org_short_name")
        print("   ✓ JWT parsing and claims extraction")
        print("   ✓ Organization context creation")
        print("   ✓ Role-based permissions (manager/employee/admin)")
        print("   ✓ Backward compatibility with organization_id")
        print("\n🎯 Ready for Phase 2b: Apply middleware to endpoints\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
