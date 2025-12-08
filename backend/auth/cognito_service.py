"""
AWS Cognito Service for User Authentication and Management
Handles user registration, authentication, and role management with Cognito
"""

import boto3
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from botocore.exceptions import ClientError
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class CognitoService:
    """AWS Cognito service for user authentication and management"""
    
    def __init__(self):
        self.region = "us-east-1"  # Your configured region
        self.user_pool_id = None  # Will be set from environment
        self.client_id = None     # Will be set from environment
        
        # Initialize Cognito client
        try:
            self.cognito_client = boto3.client('cognito-idp', region_name=self.region)
            logger.info("✅ Cognito client initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Cognito client: {e}")
            raise
    
    def configure(self, user_pool_id: str, client_id: str):
        """Configure Cognito service with pool and client IDs"""
        self.user_pool_id = user_pool_id
        self.client_id = client_id
        logger.info(f"🔧 Cognito configured - Pool: {user_pool_id[:20]}...")
    
    async def create_user(
        self, 
        email: str, 
        password: str, 
        full_name: str,
        organization_id: str,
        role: str,
        phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new user in Cognito with custom attributes"""
        
        try:
            # Prepare user attributes
            attributes = [
                {'Name': 'email', 'Value': email},
                {'Name': 'email_verified', 'Value': 'true'},
                {'Name': 'name', 'Value': full_name},
                {'Name': 'custom:organization_id', 'Value': organization_id},
                {'Name': 'custom:role', 'Value': role},
            ]
            
            if phone:
                attributes.append({'Name': 'phone_number', 'Value': phone})
            
            # Create user in Cognito
            response = self.cognito_client.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=email,
                UserAttributes=attributes,
                TemporaryPassword=password,
                MessageAction='SUPPRESS',  # Don't send welcome email
                ForceAliasCreation=False
            )
            
            # Set permanent password
            self.cognito_client.admin_set_user_password(
                UserPoolId=self.user_pool_id,
                Username=email,
                Password=password,
                Permanent=True
            )
            
            # Add user to role group
            await self._add_user_to_group(email, role)
            
            logger.info(f"✅ User created in Cognito: {email} with role {role}")
            
            return {
                "user_id": response['User']['Username'],
                "email": email,
                "status": response['User']['UserStatus'],
                "created_at": response['User']['UserCreateDate'].isoformat()
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'UsernameExistsException':
                raise HTTPException(status_code=400, detail="User already exists")
            elif error_code == 'InvalidPasswordException':
                raise HTTPException(status_code=400, detail="Password does not meet requirements")
            else:
                logger.error(f"❌ Cognito user creation failed: {e}")
                raise HTTPException(status_code=500, detail=f"User creation failed: {error_code}")
    
    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user and return tokens"""
        
        try:
            response = self.cognito_client.admin_initiate_auth(
                UserPoolId=self.user_pool_id,
                ClientId=self.client_id,
                AuthFlow='ADMIN_NO_SRP_AUTH',
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password
                }
            )
            
            # Extract tokens
            auth_result = response['AuthenticationResult']
            
            # Get user attributes
            user_info = await self.get_user_info(email)
            
            logger.info(f"✅ User authenticated: {email}")
            
            return {
                "access_token": auth_result['AccessToken'],
                "id_token": auth_result['IdToken'],
                "refresh_token": auth_result['RefreshToken'],
                "expires_in": auth_result['ExpiresIn'],
                "user_info": user_info
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['NotAuthorizedException', 'UserNotFoundException']:
                raise HTTPException(status_code=401, detail="Invalid email or password")
            elif error_code == 'UserNotConfirmedException':
                raise HTTPException(status_code=401, detail="User account not confirmed")
            else:
                logger.error(f"❌ Authentication failed: {e}")
                raise HTTPException(status_code=500, detail="Authentication failed")
    
    async def get_user_info(self, email: str) -> Dict[str, Any]:
        """Get user information from Cognito"""
        
        try:
            response = self.cognito_client.admin_get_user(
                UserPoolId=self.user_pool_id,
                Username=email
            )
            
            # Parse user attributes
            attributes = {}
            for attr in response['UserAttributes']:
                attributes[attr['Name']] = attr['Value']
            
            # Get user groups (roles)
            groups_response = self.cognito_client.admin_list_groups_for_user(
                UserPoolId=self.user_pool_id,
                Username=email
            )
            
            roles = [group['GroupName'] for group in groups_response['Groups']]
            
            return {
                "user_id": response['Username'],
                "email": attributes.get('email'),
                "full_name": attributes.get('name'),
                "phone": attributes.get('phone_number'),
                "organization_id": attributes.get('custom:organization_id'),
                "role": attributes.get('custom:role'),
                "roles": roles,
                "status": response['UserStatus'],
                "enabled": response['Enabled'],
                "created_at": response['UserCreateDate'].isoformat(),
                "last_modified": response['UserLastModifiedDate'].isoformat()
            }
            
        except ClientError as e:
            logger.error(f"❌ Failed to get user info: {e}")
            raise HTTPException(status_code=404, detail="User not found")
    
    async def update_user_role(self, email: str, new_role: str) -> bool:
        """Update user role in Cognito"""
        
        try:
            # Get current groups
            current_groups = self.cognito_client.admin_list_groups_for_user(
                UserPoolId=self.user_pool_id,
                Username=email
            )
            
            # Remove from all current groups
            for group in current_groups['Groups']:
                self.cognito_client.admin_remove_user_from_group(
                    UserPoolId=self.user_pool_id,
                    Username=email,
                    GroupName=group['GroupName']
                )
            
            # Update custom role attribute
            self.cognito_client.admin_update_user_attributes(
                UserPoolId=self.user_pool_id,
                Username=email,
                UserAttributes=[
                    {'Name': 'custom:role', 'Value': new_role}
                ]
            )
            
            # Add to new role group
            await self._add_user_to_group(email, new_role)
            
            logger.info(f"✅ User role updated: {email} -> {new_role}")
            return True
            
        except ClientError as e:
            logger.error(f"❌ Failed to update user role: {e}")
            return False
    
    async def disable_user(self, email: str) -> bool:
        """Disable user account"""
        
        try:
            self.cognito_client.admin_disable_user(
                UserPoolId=self.user_pool_id,
                Username=email
            )
            
            logger.info(f"✅ User disabled: {email}")
            return True
            
        except ClientError as e:
            logger.error(f"❌ Failed to disable user: {e}")
            return False
    
    async def enable_user(self, email: str) -> bool:
        """Enable user account"""
        
        try:
            self.cognito_client.admin_enable_user(
                UserPoolId=self.user_pool_id,
                Username=email
            )
            
            logger.info(f"✅ User enabled: {email}")
            return True
            
        except ClientError as e:
            logger.error(f"❌ Failed to enable user: {e}")
            return False
    
    async def delete_user(self, email: str) -> bool:
        """Delete user from Cognito"""
        
        try:
            self.cognito_client.admin_delete_user(
                UserPoolId=self.user_pool_id,
                Username=email
            )
            
            logger.info(f"✅ User deleted: {email}")
            return True
            
        except ClientError as e:
            logger.error(f"❌ Failed to delete user: {e}")
            return False
    
    async def _add_user_to_group(self, email: str, role: str):
        """Add user to Cognito group based on role"""
        
        try:
            # Ensure group exists
            await self._ensure_group_exists(role)
            
            # Add user to group
            self.cognito_client.admin_add_user_to_group(
                UserPoolId=self.user_pool_id,
                Username=email,
                GroupName=role
            )
            
            logger.debug(f"✅ User added to group: {email} -> {role}")
            
        except ClientError as e:
            logger.error(f"❌ Failed to add user to group: {e}")
            raise
    
    async def _ensure_group_exists(self, group_name: str):
        """Ensure Cognito group exists for role"""
        
        try:
            # Check if group exists
            self.cognito_client.get_group(
                GroupName=group_name,
                UserPoolId=self.user_pool_id
            )
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                # Create group
                description_map = {
                    'admin': 'System administrators with full access',
                    'manager': 'Managers with report submission and user management rights',
                    'employee': 'Employees with report creation and editing rights'
                }
                
                self.cognito_client.create_group(
                    GroupName=group_name,
                    UserPoolId=self.user_pool_id,
                    Description=description_map.get(group_name, f'{group_name} role group')
                )
                
                logger.info(f"✅ Created Cognito group: {group_name}")
            else:
                raise
    
    async def list_users_by_organization(self, organization_id: str) -> List[Dict[str, Any]]:
        """List all users in an organization"""
        
        try:
            users = []
            paginator = self.cognito_client.get_paginator('list_users')
            
            for page in paginator.paginate(UserPoolId=self.user_pool_id):
                for user in page['Users']:
                    # Check if user belongs to organization
                    user_org_id = None
                    for attr in user['Attributes']:
                        if attr['Name'] == 'custom:organization_id':
                            user_org_id = attr['Value']
                            break
                    
                    if user_org_id == organization_id:
                        # Parse user attributes
                        attributes = {}
                        for attr in user['Attributes']:
                            attributes[attr['Name']] = attr['Value']
                        
                        users.append({
                            "user_id": user['Username'],
                            "email": attributes.get('email'),
                            "full_name": attributes.get('name'),
                            "role": attributes.get('custom:role'),
                            "status": user['UserStatus'],
                            "enabled": user['Enabled'],
                            "created_at": user['UserCreateDate'].isoformat()
                        })
            
            return users
            
        except ClientError as e:
            logger.error(f"❌ Failed to list users: {e}")
            return []

# Global Cognito service instance
cognito_service = CognitoService()