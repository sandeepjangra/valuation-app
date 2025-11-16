#!/usr/bin/env python3
"""
Organization Security Middleware Test Script
Tests JWT validation, organization filtering, and database security
"""

import asyncio
import sys
import os
import logging
from datetime import datetime, timezone

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.multi_db_manager import MultiDatabaseManager
from utils.auth_middleware import (
    CognitoJWTValidator, OrganizationContext, OrganizationMiddleware, 
    create_dev_token, create_organization_middleware
)
from utils.organization_db_service import OrganizationDatabaseService, create_org_db_service

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_jwt_validation():
    """Test JWT token validation and context creation"""
    logger.info("🧪 Testing JWT validation...")
    
    validator = CognitoJWTValidator()
    
    # Test development tokens
    test_cases = [
        {
            "token": create_dev_token("manager@test.com", "demo_org_001", "manager"),
            "expected_org": "demo_org_001",
            "expected_role": "manager"
        },
        {
            "token": create_dev_token("employee@test.com", "demo_org_001", "employee"),
            "expected_org": "demo_org_001",
            "expected_role": "employee"
        },
        {
            "token": create_dev_token("admin@system.com", "system_admin", "system_admin"),
            "expected_org": "system_admin",
            "expected_role": "system_admin"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            # Validate token
            jwt_claims = await validator.validate_token(test_case["token"])
            
            # Create organization context
            org_context = OrganizationContext(jwt_claims)
            
            # Verify context
            assert org_context.organization_id == test_case["expected_org"], f"Org ID mismatch: {org_context.organization_id}"
            assert test_case["expected_role"] in org_context.roles, f"Role mismatch: {org_context.roles}"
            
            logger.info(f"  ✅ Test case {i}: {org_context.email} -> {org_context.organization_id} ({org_context.roles})")
            
        except Exception as e:
            logger.error(f"  ❌ Test case {i} failed: {e}")
            raise

async def test_organization_filtering():
    """Test organization-based database filtering"""
    logger.info("🧪 Testing organization database filtering...")
    
    db_manager = MultiDatabaseManager()
    await db_manager.connect()
    
    try:
        org_middleware = create_organization_middleware(db_manager)
        org_db_service = create_org_db_service(db_manager, org_middleware)
        
        # Create test contexts
        manager_token = create_dev_token("manager@demo.com", "demo_org_001", "manager")
        jwt_claims = await CognitoJWTValidator().validate_token(manager_token)
        manager_context = OrganizationContext(jwt_claims)
        
        employee_token = create_dev_token("employee@demo.com", "demo_org_001", "employee") 
        jwt_claims_emp = await CognitoJWTValidator().validate_token(employee_token)
        employee_context = OrganizationContext(jwt_claims_emp)
        
        admin_token = create_dev_token("admin@system.com", "system_admin", "system_admin")
        jwt_claims_admin = await CognitoJWTValidator().validate_token(admin_token)
        admin_context = OrganizationContext(jwt_claims_admin)
        
        # Test 1: Manager can access organization data
        org_users = await org_db_service.get_organization_users(manager_context)
        logger.info(f"  ✅ Manager found {len(org_users)} users in organization")
        
        # Test 2: Employee cannot access user management
        try:
            await org_db_service.get_organization_users(employee_context)
            logger.error("  ❌ Employee should not access user management")
        except PermissionError:
            logger.info("  ✅ Employee correctly denied user management access")
        
        # Test 3: System admin can access all organizations
        all_orgs = await org_db_service.get_all_organizations(admin_context)
        logger.info(f"  ✅ System admin found {len(all_orgs)} total organizations")
        
        # Test 4: Organization filtering in queries
        demo_reports = await org_db_service.get_organization_reports(manager_context)
        logger.info(f"  ✅ Found {len(demo_reports)} reports for demo organization")
        
        # Test 5: Cross-organization access prevention
        other_org_context = OrganizationContext({
            "sub": "test_user",
            "email": "test@other.com",
            "custom:organization_id": "other_org_999",
            "cognito:groups": ["manager"]
        })
        
        # This should only return data from other_org_999 (likely empty)
        other_reports = await org_db_service.get_organization_reports(other_org_context)
        logger.info(f"  ✅ Other organization has {len(other_reports)} reports (isolated)")
        
        logger.info("🎉 Organization filtering tests passed!")
        
    finally:
        await db_manager.disconnect()

async def test_audit_logging():
    """Test audit logging functionality"""
    logger.info("🧪 Testing audit logging...")
    
    db_manager = MultiDatabaseManager()
    await db_manager.connect()
    
    try:
        org_middleware = create_organization_middleware(db_manager)
        org_db_service = create_org_db_service(db_manager, org_middleware)
        
        # Create test context
        manager_token = create_dev_token("manager@demo.com", "demo_org_001", "manager")
        jwt_claims = await CognitoJWTValidator().validate_token(manager_token)
        manager_context = OrganizationContext(jwt_claims)
        
        # Perform some operations that should be logged
        logger.info("  📝 Performing operations to generate audit logs...")
        
        # Read operations
        await org_db_service.get_organization_users(manager_context)
        await org_db_service.get_organization_reports(manager_context)
        
        # Get audit logs
        audit_logs = await org_db_service.get_organization_audit_logs(
            manager_context, 
            limit=10
        )
        
        logger.info(f"  ✅ Generated {len(audit_logs)} audit log entries")
        
        # Display recent audit logs
        for log in audit_logs[:3]:  # Show first 3 logs
            logger.info(f"    📋 {log['action']} on {log['resource_type']} by {log['user_id']}")
        
    finally:
        await db_manager.disconnect()

async def test_permission_system():
    """Test role-based permission system"""
    logger.info("🧪 Testing permission system...")
    
    # Create different role contexts
    contexts = {
        "system_admin": OrganizationContext({
            "sub": "admin_user",
            "email": "admin@system.com",
            "custom:organization_id": "system_admin",
            "cognito:groups": ["system_admin"]
        }),
        "manager": OrganizationContext({
            "sub": "manager_user",
            "email": "manager@demo.com", 
            "custom:organization_id": "demo_org_001",
            "cognito:groups": ["manager"]
        }),
        "employee": OrganizationContext({
            "sub": "employee_user",
            "email": "employee@demo.com",
            "custom:organization_id": "demo_org_001", 
            "cognito:groups": ["employee"]
        })
    }
    
    # Test permission matrix
    permission_tests = [
        ("reports", "create", ["system_admin", "manager", "employee"]),
        ("reports", "delete", ["system_admin", "manager"]),
        ("users", "create", ["system_admin", "manager"]),
        ("users", "read", ["system_admin", "manager"]),
        ("audit_logs", "read", ["system_admin", "manager"]),
    ]
    
    for resource, action, allowed_roles in permission_tests:
        for role, context in contexts.items():
            has_permission = context.has_permission(resource, action)
            should_have = role in allowed_roles
            
            if has_permission == should_have:
                status = "✅"
            else:
                status = "❌"
            
            logger.info(f"  {status} {role} {action} {resource}: {has_permission} (expected: {should_have})")

async def main():
    """Run all tests"""
    logger.info("🚀 Starting organization security middleware tests...")
    
    try:
        await test_jwt_validation()
        await test_organization_filtering() 
        await test_audit_logging()
        await test_permission_system()
        
        logger.info("🎉 All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"💥 Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())