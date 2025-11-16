#!/usr/bin/env python3
"""
Organization Collections Setup Script
Creates and initializes all organization-related collections with proper indexes
"""

import asyncio
import sys
import os
import logging
from datetime import datetime, timezone

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.multi_db_manager import MultiDatabaseManager
from database.organization_models import (
    ORGANIZATION_COLLECTIONS,
    create_organization_indexes,
    OrganizationSchema,
    UserSchema,
    validate_organization_id,
    validate_email
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('organization_setup.log')
    ]
)
logger = logging.getLogger(__name__)

async def create_system_admin_organization(db_manager: MultiDatabaseManager):
    """Create the default system admin organization"""
    try:
        # Check if system admin org already exists
        existing_org = await db_manager.find_one(
            "admin", "organizations", 
            {"organization_id": "system_admin"}, 
            include_inactive=True
        )
        
        if existing_org:
            logger.info("🔧 System admin organization already exists")
            return existing_org["_id"]
        
        # Create system admin organization
        org_data = OrganizationSchema.create_document(
            organization_id="system_admin",
            name="System Administration",
            contact_email="admin@valuationapp.com",
            created_by="system",
            settings={
                "max_users": 10,
                "features_enabled": ["all"],
                "s3_prefix": "system_admin"
            }
        )
        
        org_id = await db_manager.insert_one("admin", "organizations", org_data)
        logger.info(f"✅ Created system admin organization: {org_id}")
        return org_id
        
    except Exception as e:
        logger.error(f"❌ Failed to create system admin organization: {e}")
        raise

async def create_demo_organization(db_manager: MultiDatabaseManager):
    """Create a demo organization for testing"""
    try:
        # Check if demo org already exists
        existing_org = await db_manager.find_one(
            "admin", "organizations", 
            {"organization_id": "demo_org_001"}, 
            include_inactive=True
        )
        
        if existing_org:
            logger.info("🔧 Demo organization already exists")
            return existing_org["_id"]
        
        # Create demo organization
        org_data = OrganizationSchema.create_document(
            organization_id="demo_org_001",
            name="Demo Valuation Company",
            contact_email="demo@valuationcompany.com",
            created_by="system",
            settings={
                "max_users": 25,
                "features_enabled": ["reports", "templates", "file_upload"],
                "s3_prefix": "demo_org_001"
            }
        )
        
        org_id = await db_manager.insert_one("admin", "organizations", org_data)
        logger.info(f"✅ Created demo organization: {org_id}")
        return org_id
        
    except Exception as e:
        logger.error(f"❌ Failed to create demo organization: {e}")
        raise

async def create_sample_users(db_manager: MultiDatabaseManager):
    """Create sample users for testing"""
    try:
        # System Admin User
        existing_admin = await db_manager.find_one(
            "admin", "users", 
            {"email": "admin@valuationapp.com"}, 
            include_inactive=True
        )
        
        if not existing_admin:
            admin_user = UserSchema.create_document(
                cognito_user_id="system_admin_user_001",
                email="admin@valuationapp.com",
                organization_id="system_admin",
                role="system_admin",
                created_by="system",
                profile={
                    "first_name": "System",
                    "last_name": "Administrator",
                    "display_name": "System Admin"
                }
            )
            
            admin_id = await db_manager.insert_one("admin", "users", admin_user)
            logger.info(f"✅ Created system admin user: {admin_id}")
        
        # Demo Manager User
        existing_manager = await db_manager.find_one(
            "admin", "users", 
            {"email": "manager@valuationcompany.com"}, 
            include_inactive=True
        )
        
        if not existing_manager:
            manager_user = UserSchema.create_document(
                cognito_user_id="demo_manager_user_001",
                email="manager@valuationcompany.com",
                organization_id="demo_org_001",
                role="manager",
                created_by="system",
                profile={
                    "first_name": "Demo",
                    "last_name": "Manager",
                    "display_name": "Demo Manager",
                    "department": "Valuation"
                }
            )
            
            manager_id = await db_manager.insert_one("admin", "users", manager_user)
            logger.info(f"✅ Created demo manager user: {manager_id}")
        
        # Demo Employee User
        existing_employee = await db_manager.find_one(
            "admin", "users", 
            {"email": "employee@valuationcompany.com"}, 
            include_inactive=True
        )
        
        if not existing_employee:
            employee_user = UserSchema.create_document(
                cognito_user_id="demo_employee_user_001",
                email="employee@valuationcompany.com",
                organization_id="demo_org_001",
                role="employee",
                created_by="system",
                profile={
                    "first_name": "Demo",
                    "last_name": "Employee",
                    "display_name": "Demo Employee",
                    "department": "Valuation"
                }
            )
            
            employee_id = await db_manager.insert_one("admin", "users", employee_user)
            logger.info(f"✅ Created demo employee user: {employee_id}")
            
    except Exception as e:
        logger.error(f"❌ Failed to create sample users: {e}")
        raise

async def verify_collections(db_manager: MultiDatabaseManager):
    """Verify that all collections are created and accessible"""
    try:
        logger.info("🔍 Verifying organization collections...")
        
        for collection_name in ORGANIZATION_COLLECTIONS.keys():
            try:
                count = await db_manager.count_documents("admin", collection_name, {})
                logger.info(f"📊 {collection_name}: {count} documents")
                
                # Get collection stats
                stats = await db_manager.get_collection_stats("admin", collection_name)
                logger.info(f"   └─ Active: {stats['active_documents']}, Total: {stats['total_documents']}")
                
            except Exception as e:
                logger.warning(f"⚠️ Could not access collection {collection_name}: {e}")
        
        logger.info("✅ Collection verification completed")
        
    except Exception as e:
        logger.error(f"❌ Failed to verify collections: {e}")
        raise

async def setup_organization_structure():
    """Main setup function"""
    db_manager = MultiDatabaseManager()
    
    try:
        logger.info("🚀 Starting organization structure setup...")
        
        # Connect to database
        logger.info("📡 Connecting to MongoDB...")
        if not await db_manager.connect():
            raise RuntimeError("Failed to connect to MongoDB")
        
        # Create indexes
        logger.info("📚 Creating database indexes...")
        await create_organization_indexes(db_manager, logger)
        
        # Create system admin organization
        logger.info("🏢 Creating system admin organization...")
        await create_system_admin_organization(db_manager)
        
        # Create demo organization
        logger.info("🎮 Creating demo organization...")
        await create_demo_organization(db_manager)
        
        # Create sample users
        logger.info("👥 Creating sample users...")
        await create_sample_users(db_manager)
        
        # Verify setup
        logger.info("✅ Verifying setup...")
        await verify_collections(db_manager)
        
        logger.info("🎉 Organization structure setup completed successfully!")
        
        # Print summary
        logger.info("\n" + "="*60)
        logger.info("SETUP SUMMARY")
        logger.info("="*60)
        logger.info("✅ Organizations created:")
        logger.info("   • system_admin - System Administration")
        logger.info("   • demo_org_001 - Demo Valuation Company")
        logger.info("")
        logger.info("✅ Sample users created:")
        logger.info("   • admin@valuationapp.com (system_admin)")
        logger.info("   • manager@valuationcompany.com (manager)")
        logger.info("   • employee@valuationcompany.com (employee)")
        logger.info("")
        logger.info("✅ Collections initialized:")
        for collection_name in ORGANIZATION_COLLECTIONS.keys():
            logger.info(f"   • {collection_name}")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"💥 Setup failed: {e}")
        raise
    
    finally:
        await db_manager.disconnect()

async def reset_organization_structure():
    """Reset/clean organization structure - USE WITH CAUTION"""
    logger.warning("⚠️ RESET MODE - This will delete all organization data!")
    response = input("Are you sure you want to reset? Type 'YES' to confirm: ")
    
    if response != "YES":
        logger.info("❌ Reset cancelled")
        return
    
    db_manager = MultiDatabaseManager()
    
    try:
        if not await db_manager.connect():
            raise RuntimeError("Failed to connect to MongoDB")
        
        logger.info("🗑️ Removing organization collections...")
        
        # Drop organization collections (but keep shared template collections)
        for collection_name in ORGANIZATION_COLLECTIONS.keys():
            try:
                collection = db_manager.get_collection("admin", collection_name)
                await collection.drop()
                logger.info(f"🗑️ Dropped collection: {collection_name}")
            except Exception as e:
                logger.warning(f"⚠️ Could not drop {collection_name}: {e}")
        
        logger.info("✅ Reset completed")
        
    except Exception as e:
        logger.error(f"❌ Reset failed: {e}")
        raise
    
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Organization Collections Setup")
    parser.add_argument("--reset", action="store_true", help="Reset organization structure (DANGER!)")
    parser.add_argument("--verify", action="store_true", help="Only verify existing collections")
    
    args = parser.parse_args()
    
    if args.reset:
        asyncio.run(reset_organization_structure())
    elif args.verify:
        db_manager = MultiDatabaseManager()
        asyncio.run(verify_collections(db_manager))
    else:
        asyncio.run(setup_organization_structure())