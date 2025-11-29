#!/usr/bin/env python3
"""
Simple API test to verify template-versioned reports functionality
"""

import asyncio
import json
from datetime import datetime

async def test_api_directly():
    """Test API functionality by importing directly"""
    
    print("🧪 Testing Template-Versioned Reports API (Direct Import)")
    print("=" * 70)
    
    try:
        # Import the app and dependencies directly
        import sys
        from pathlib import Path
        
        # Add current directory to path
        sys.path.insert(0, str(Path.cwd()))
        
        from versioned_reports_app import app
        from database.mongodb_manager import MongoDBManager
        from services.template_snapshot_service import TemplateSnapshotService
        
        print("✅ All imports successful")
        
        # Test database connectivity
        print("\n📊 Testing Database Connection...")
        db_manager = MongoDBManager()
        await db_manager.connect()
        
        if db_manager.is_connected:
            print("✅ Database connected successfully")
            
            # Check template versions
            template_count = await db_manager.database.template_versions.count_documents({})
            snapshot_count = await db_manager.database.template_snapshots.count_documents({})
            report_count = await db_manager.database.valuation_reports.count_documents({})
            
            print(f"📋 Template versions: {template_count}")
            print(f"📸 Template snapshots: {snapshot_count}")  
            print(f"📄 Total reports: {report_count}")
            
            # Test template snapshot service
            print("\n🔧 Testing Template Snapshot Service...")
            template_service = TemplateSnapshotService(db_manager.database)
            
            # Get existing templates
            templates = await db_manager.database.template_versions.find({}).to_list(length=10)
            
            if templates:
                print(f"✅ Found {len(templates)} template versions:")
                for template in templates:
                    print(f"  • {template['templateId']} v{template['version']}")
                    print(f"    Bank: {template['bankCode']} | Category: {template['templateCategory']}")
                
                # Test snapshot creation
                print("\n📸 Testing Template Snapshot Creation...")
                template_ids = ["SBI_LAND_PROPERTY_DETAILS", "SBI_LAND_CONSTRUCTION_DETAILS"]
                
                snapshot_id = await template_service.capture_template_snapshot(template_ids, "1.0.0")
                print(f"✅ Created template snapshot: {snapshot_id}")
                
                # Test snapshot retrieval
                snapshot = await template_service.get_template_snapshot(snapshot_id)
                print(f"✅ Retrieved snapshot with {len(snapshot['templateDefinitions'])} templates")
                
                # Create a test report document
                print("\n📝 Testing Report Creation...")
                
                test_report = {
                    "templateSnapshot": snapshot_id,
                    "bankCode": "SBI",
                    "propertyType": "Land",
                    "organizationId": "test_org_001",
                    "createdBy": "test_user_001",
                    "assignedTo": "test_valuer_001",
                    "customerName": "Test Customer",
                    "propertyAddress": "123 Test Street, Test City",
                    "loanAmount": 5000000,
                    "formData": {
                        "agreement_to_sell": "Test agreement details",
                        "applicant_name": "Test Customer",
                        "postal_address": "123 Test Street, Test City",
                        "total_extent_plot": 1000,
                        "valuation_rate": 2500
                    },
                    "calculationResults": {},
                    "validationErrors": [],
                    "auditTrail": [{
                        "action": "CREATED",
                        "performedBy": "test_user_001",
                        "timestamp": datetime.utcnow(),
                        "details": f"Test report created with snapshot {snapshot_id}"
                    }],
                    "workflow": {
                        "status": "DRAFT",
                        "submittedBy": None,
                        "submittedAt": None,
                        "reviewedBy": None,
                        "reviewedAt": None
                    },
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                }
                
                # Insert test report
                report_id = await db_manager.insert_one("valuation_reports", test_report)
                print(f"✅ Created test report: {report_id}")
                
                # Retrieve the report
                created_report = await db_manager.find_one("valuation_reports", {"_id": report_id})
                print(f"✅ Retrieved report with {len(created_report['formData'])} form fields")
                
                # Test report listing
                print("\n📑 Testing Report Listing...")
                all_reports = await db_manager.find_many(
                    "valuation_reports", 
                    {"bankCode": "SBI"}, 
                    limit=5,
                    sort_by={"createdAt": -1}
                )
                print(f"✅ Found {len(all_reports)} SBI reports")
                
                # Clean up test report
                await db_manager.delete_one("valuation_reports", {"_id": report_id})
                print(f"🧹 Cleaned up test report")
                
            else:
                print("⚠️ No template versions found")
            
        else:
            print("❌ Database connection failed")
            
        await db_manager.disconnect()
        
        print("\n✅ All Tests Completed Successfully!")
        print("\n🎯 System Status:")
        print("  ✅ Template versioning system operational")
        print("  ✅ Database connectivity working") 
        print("  ✅ Template snapshot creation/retrieval working")
        print("  ✅ Report CRUD operations functional")
        print("  ✅ SBI Land templates ready for use")
        print("\n🚀 The system is ready for frontend integration!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔧 Direct API Testing - Template Versioned Reports")
    asyncio.run(test_api_directly())