#!/usr/bin/env python3
"""
Create test users in AWS Cognito for local development
"""

import os
import sys
import asyncio
import boto3
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from auth.cognito_service import cognito_service

async def create_test_users():
    """Create test users in Cognito"""
    
    # Get Cognito config from environment
    user_pool_id = os.getenv("COGNITO_USER_POOL_ID")
    client_id = os.getenv("COGNITO_CLIENT_ID")
    
    if not user_pool_id or not client_id:
        print("❌ Please set COGNITO_USER_POOL_ID and COGNITO_CLIENT_ID in .env")
        return
    
    # Configure Cognito service
    cognito_service.configure(user_pool_id, client_id)
    
    # Test users to create
    test_users = [
        {
            "email": "admin@test.com",
            "password": "Admin123!",
            "full_name": "Test Admin",
            "role": "admin",
            "organization_id": "system-administration"
        },
        {
            "email": "manager@test.com", 
            "password": "Manager123!",
            "full_name": "Test Manager",
            "role": "manager",
            "organization_id": "demo-valuation-co"
        },
        {
            "email": "employee@test.com",
            "password": "Employee123!",
            "full_name": "Test Employee", 
            "role": "employee",
            "organization_id": "demo-valuation-co"
        }
    ]
    
    print("👥 Creating test users in Cognito...")
    
    for user_data in test_users:
        try:
            result = await cognito_service.create_user(
                email=user_data["email"],
                password=user_data["password"],
                full_name=user_data["full_name"],
                organization_id=user_data["organization_id"],
                role=user_data["role"]
            )
            print(f"✅ Created: {user_data['email']} ({user_data['role']})")
            
        except Exception as e:
            if "UsernameExistsException" in str(e):
                print(f"✅ Already exists: {user_data['email']}")
            else:
                print(f"❌ Failed to create {user_data['email']}: {e}")
    
    print("\n🔑 Test Credentials:")
    for user_data in test_users:
        print(f"  {user_data['role'].title()}: {user_data['email']} / {user_data['password']}")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / "backend" / ".env")
    
    asyncio.run(create_test_users())