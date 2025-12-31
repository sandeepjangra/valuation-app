#!/usr/bin/env python3
"""
Test Cognito authentication directly
"""

import os
import sys
import asyncio
import boto3
from pathlib import Path

# Load environment
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / "backend" / ".env")

async def test_cognito_direct():
    """Test Cognito authentication directly"""
    
    user_pool_id = os.getenv("COGNITO_USER_POOL_ID")
    client_id = os.getenv("COGNITO_CLIENT_ID")
    
    print(f"🔐 Testing Cognito Authentication")
    print(f"User Pool: {user_pool_id}")
    print(f"Client ID: {client_id}")
    
    # Create Cognito client
    cognito_client = boto3.client('cognito-idp', region_name='us-east-1')
    
    try:
        # Test authentication with correct auth flow
        response = cognito_client.admin_initiate_auth(
            UserPoolId=user_pool_id,
            ClientId=client_id,
            AuthFlow='ADMIN_USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': 'admin@test.com',
                'PASSWORD': 'Admin123!'
            }
        )
        
        print("✅ Cognito authentication successful!")
        print(f"Access Token: {response['AuthenticationResult']['AccessToken'][:50]}...")
        
        # Test getting user info
        user_response = cognito_client.admin_get_user(
            UserPoolId=user_pool_id,
            Username='admin@test.com'
        )
        
        print("✅ User info retrieved:")
        for attr in user_response['UserAttributes']:
            print(f"  {attr['Name']}: {attr['Value']}")
        
        # Test user groups
        groups_response = cognito_client.admin_list_groups_for_user(
            UserPoolId=user_pool_id,
            Username='admin@test.com'
        )
        
        print("✅ User groups:")
        for group in groups_response['Groups']:
            print(f"  - {group['GroupName']}")
            
        return True
        
    except Exception as e:
        print(f"❌ Cognito authentication failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_cognito_direct())
    if success:
        print("\n🎉 Cognito is working! You can now integrate it with your backend.")
    else:
        print("\n❌ Cognito test failed. Check your configuration.")