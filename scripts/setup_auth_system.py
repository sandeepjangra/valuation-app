#!/usr/bin/env python3
"""
Authentication System Setup Script
Initializes AWS Cognito user pools, groups, and creates initial admin user
"""

import os
import sys
import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from auth.cognito_service import cognito_service
from database.multi_db_manager import MultiDatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthSystemSetup:
    """Setup authentication system with Cognito and MongoDB"""
    
    def __init__(self):
        self.db_manager = None
        
        # Load environment variables
        self.user_pool_id = os.getenv("COGNITO_USER_POOL_ID")
        self.client_id = os.getenv("COGNITO_CLIENT_ID")
        
        if not self.user_pool_id or not self.client_id:
            logger.error("❌ Cognito configuration not found in environment variables")
            logger.info("Please set COGNITO_USER_POOL_ID and COGNITO_CLIENT_ID")
            sys.exit(1)
    
    async def setup_database_connection(self):
        """Initialize database connection"""
        try:
            self.db_manager = MultiDatabaseManager()
            await self.db_manager.connect()
            logger.info("✅ Database connection established")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    async def setup_cognito_groups(self):
        """Create Cognito user groups for roles"""
        try:
            # Configure Cognito service
            cognito_service.configure(self.user_pool_id, self.client_id)
            
            # Create role groups
            roles = ["admin", "manager", "employee"]
            
            for role in roles:
                try:
                    await cognito_service._ensure_group_exists(role)
                    logger.info(f"✅ Cognito group created/verified: {role}")
                except Exception as e:
                    logger.warning(f"⚠️ Group creation failed for {role}: {e}")
            
        except Exception as e:
            logger.error(f"❌ Cognito groups setup failed: {e}")
            raise
    
    async def create_system_admin_organization(self):
        """Create system administration organization"""
        try:
            config_db = self.db_manager.client.val_app_config
            
            # Check if system org already exists
            existing_org = await config_db.organizations.find_one({
                "org_short_name": "system-administration",
                "is_system_org": True
            })
            
            if existing_org:
                logger.info("✅ System administration organization already exists")
                return str(existing_org["_id"])
            
            # Create system organization
            system_org = {
                "org_name": "System Administration",
                "org_short_name": "system-administration",
                "org_display_name": "System Administration",
                "organization_type": "system",
                "description": "System administration organization for platform management",
                "is_system_org": True,
                "is_active": True,
                "contact_info": {
                    "email": "admin@system.com",
                    "phone": None,
                    "address": None
                },
                "settings": {
                    "subscription_plan": "enterprise",
                    "max_users": -1,  # Unlimited
                    "max_reports_per_month": -1,  # Unlimited
                    "max_storage_gb": -1,  # Unlimited
                    "features_enabled": ["all"],
                    "timezone": "UTC",
                    "date_format": "DD/MM/YYYY"
                },
                "metadata": {
                    "original_organization_id": "system_admin",
                    "database_name": "system-administration",
                    "created_from": "setup_script"
                },
                "created_by": "system_setup",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            result = await config_db.organizations.insert_one(system_org)
            logger.info(f"✅ System administration organization created: {result.inserted_id}")
            
            # Initialize system organization database
            await self.db_manager.ensure_org_database_structure("system-administration")
            logger.info("✅ System organization database initialized")
            
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"❌ System organization creation failed: {e}")
            raise
    
    async def create_system_admin_user(self, org_id: str):
        """Create system administrator user"""
        try:
            admin_email = "admin@system.com"
            admin_password = "Admin123!"  # Change this in production
            
            # Create user in Cognito
            try:
                cognito_result = await cognito_service.create_user(
                    email=admin_email,
                    password=admin_password,
                    full_name="System Administrator",
                    organization_id="system-administration",
                    role="admin"
                )
                logger.info(f"✅ System admin created in Cognito: {admin_email}")
            except Exception as e:
                if "UsernameExistsException" in str(e):
                    logger.info("✅ System admin already exists in Cognito")
                else:
                    raise
            
            # Create user profile in MongoDB
            system_db = self.db_manager.client["system-administration"]
            
            existing_user = await system_db.users.find_one({"email": admin_email})
            if existing_user:
                logger.info("✅ System admin user already exists in MongoDB")
                return
            
            admin_user = {
                "_id": "system_admin_001",
                "user_id": "system_admin_001",
                "email": admin_email,
                "full_name": "System Administrator",
                "phone": "",
                "organization_id": org_id,
                "org_short_name": "system-administration",
                "role": "admin",
                "is_active": True,
                "is_system_admin": True,
                "created_by": "system_setup",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "last_login": None,
                "preferences": {
                    "theme": "light",
                    "language": "en",
                    "notifications": True
                },
                "settings": {
                    "dashboard_layout": "grid",
                    "default_bank": None,
                    "timezone": "UTC"
                }
            }
            
            await system_db.users.insert_one(admin_user)
            logger.info("✅ System admin user created in MongoDB")
            
            # Log the credentials
            logger.info("🔑 System Admin Credentials:")
            logger.info(f"   Email: {admin_email}")
            logger.info(f"   Password: {admin_password}")
            logger.info("   ⚠️  Please change the password after first login!")
            
        except Exception as e:
            logger.error(f"❌ System admin user creation failed: {e}")
            raise
    
    async def create_demo_organization(self):
        """Create a demo organization for testing"""
        try:
            config_db = self.db_manager.client.val_app_config
            
            # Check if demo org already exists
            existing_org = await config_db.organizations.find_one({
                "org_short_name": "demo-valuation-co"
            })
            
            if existing_org:
                logger.info("✅ Demo organization already exists")
                return str(existing_org["_id"])
            
            # Create demo organization
            demo_org = {
                "org_name": "Demo Valuation Company",
                "org_short_name": "demo-valuation-co",
                "org_display_name": "Demo Valuation Company",
                "organization_type": "valuation_company",
                "description": "Demo organization for testing and development",
                "is_system_org": False,
                "is_active": True,
                "contact_info": {
                    "email": "demo@valuationco.com",
                    "phone": "+1-555-0123",
                    "address": "123 Demo Street, Demo City, DC 12345"
                },
                "settings": {
                    "subscription_plan": "premium",
                    "max_users": 25,
                    "max_reports_per_month": 500,
                    "max_storage_gb": 50,
                    "features_enabled": ["reports", "templates", "file_upload", "analytics"],
                    "timezone": "UTC",
                    "date_format": "DD/MM/YYYY"
                },
                "metadata": {
                    "original_organization_id": "demo_org_001",
                    "database_name": "demo-valuation-co",
                    "created_from": "setup_script"
                },
                "created_by": "system_setup",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            result = await config_db.organizations.insert_one(demo_org)
            logger.info(f"✅ Demo organization created: {result.inserted_id}")
            
            # Initialize demo organization database
            await self.db_manager.ensure_org_database_structure("demo-valuation-co")
            logger.info("✅ Demo organization database initialized")
            
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"❌ Demo organization creation failed: {e}")
            raise
    
    async def create_demo_users(self, org_id: str):
        """Create demo users for testing"""
        try:
            demo_users = [
                {
                    "email": "manager@demo.com",
                    "password": "Manager123!",
                    "full_name": "Demo Manager",
                    "role": "manager",
                    "phone": "+1-555-0124"
                },
                {
                    "email": "employee@demo.com",
                    "password": "Employee123!",
                    "full_name": "Demo Employee",
                    "role": "employee",
                    "phone": "+1-555-0125"
                }
            ]
            
            demo_db = self.db_manager.client["demo-valuation-co"]
            
            for user_data in demo_users:
                try:
                    # Create in Cognito
                    await cognito_service.create_user(
                        email=user_data["email"],
                        password=user_data["password"],
                        full_name=user_data["full_name"],
                        organization_id="demo-valuation-co",
                        role=user_data["role"],
                        phone=user_data["phone"]
                    )
                    
                    # Create in MongoDB
                    user_profile = {
                        "user_id": f"demo_{user_data['role']}_001",
                        "email": user_data["email"],
                        "full_name": user_data["full_name"],
                        "phone": user_data["phone"],
                        "organization_id": org_id,
                        "org_short_name": "demo-valuation-co",
                        "role": user_data["role"],
                        "is_active": True,
                        "created_by": "system_setup",
                        "created_at": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc),
                        "last_login": None,
                        "preferences": {
                            "theme": "light",
                            "language": "en",
                            "notifications": True
                        },
                        "settings": {
                            "dashboard_layout": "grid",
                            "default_bank": None,
                            "timezone": "UTC"
                        }
                    }
                    
                    await demo_db.users.insert_one(user_profile)
                    logger.info(f"✅ Demo user created: {user_data['email']} ({user_data['role']})")
                    
                except Exception as e:
                    if "UsernameExistsException" in str(e):
                        logger.info(f"✅ Demo user already exists: {user_data['email']}")
                    else:
                        logger.warning(f"⚠️ Failed to create demo user {user_data['email']}: {e}")
            
            # Log demo credentials
            logger.info("🔑 Demo User Credentials:")
            for user_data in demo_users:
                logger.info(f"   {user_data['role'].title()}: {user_data['email']} / {user_data['password']}")
            
        except Exception as e:
            logger.error(f"❌ Demo users creation failed: {e}")
            raise
    
    async def run_setup(self):
        """Run complete authentication system setup"""
        try:
            logger.info("🚀 Starting authentication system setup...")
            
            # 1. Setup database connection
            await self.setup_database_connection()
            
            # 2. Setup Cognito groups
            await self.setup_cognito_groups()
            
            # 3. Create system administration organization
            system_org_id = await self.create_system_admin_organization()
            
            # 4. Create system admin user
            await self.create_system_admin_user(system_org_id)
            
            # 5. Create demo organization
            demo_org_id = await self.create_demo_organization()
            
            # 6. Create demo users
            await self.create_demo_users(demo_org_id)
            
            logger.info("✅ Authentication system setup completed successfully!")
            logger.info("")
            logger.info("🎉 Your authentication system is ready!")
            logger.info("   - AWS Cognito groups created")
            logger.info("   - System administration organization initialized")
            logger.info("   - Demo organization created for testing")
            logger.info("   - Users created with proper roles and permissions")
            logger.info("")
            logger.info("Next steps:")
            logger.info("1. Update your frontend configuration with Cognito details")
            logger.info("2. Test login with the provided credentials")
            logger.info("3. Change default passwords in production")
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            raise
        finally:
            if self.db_manager:
                await self.db_manager.disconnect()

async def main():
    """Main setup function"""
    setup = AuthSystemSetup()
    await setup.run_setup()

if __name__ == "__main__":
    asyncio.run(main())