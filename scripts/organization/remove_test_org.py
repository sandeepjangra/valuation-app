"""
Remove the test organization we just created
"""
import asyncio
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database.multi_db_manager import MultiDatabaseManager

async def remove_test_org():
    """Remove Test Valuation Services"""
    
    db_manager = MultiDatabaseManager()
    await db_manager.connect()
    
    try:
        config_db = db_manager.client.val_app_config
        orgs_collection = config_db.organizations
        
        # Find and deactivate the test org
        result = await orgs_collection.update_one(
            {"org_short_name": "test-valuation-services"},
            {
                "$set": {
                    "is_active": False,
                    "deactivated_at": datetime.now(timezone.utc),
                    "deactivation_reason": "Test organization - removed"
                }
            }
        )
        
        if result.modified_count > 0:
            print("✅ Test organization deactivated")
        else:
            print("⚠️ Organization not found or already deactivated")
        
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(remove_test_org())
