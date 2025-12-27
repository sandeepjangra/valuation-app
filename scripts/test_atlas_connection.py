#!/usr/bin/env python3
"""
Test MongoDB Atlas connection and basic report operations
"""

import os
import sys
import asyncio
import json
from datetime import datetime, timezone

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

def test_atlas_connection():
    """Test MongoDB Atlas connection using the configured URI"""
    print("🔍 Testing MongoDB Atlas Connection")
    print("=" * 50)
    
    try:
        from pymongo import MongoClient
        
        # Get MongoDB URI from environment
        mongodb_uri = os.getenv('MONGODB_URI')
        
        if not mongodb_uri:
            print("❌ MONGODB_URI environment variable not found")
            return False
        
        print(f"🔗 Connecting to: {mongodb_uri[:50]}...")
        
        # Create client with timeout
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=10000)
        
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB Atlas connection successful!")
        
        # List databases
        databases = client.list_database_names()
        print(f"📋 Available databases: {databases}")
        
        # Check valuation_db
        db = client['valuation_db']
        collections = db.list_collection_names()
        print(f"📦 Collections in valuation_db: {collections}")
        
        # Check reports collection
        if 'reports' in collections:
            reports_count = db.reports.count_documents({})
            print(f"📄 Total reports in database: {reports_count}")
            
            # Get a sample report
            sample_report = db.reports.find_one({})
            if sample_report:
                print(f"🔍 Sample report ID: {sample_report.get('_id')}")
                print(f"🔍 Sample report status: {sample_report.get('status')}")
                print(f"🔍 Sample report reference: {sample_report.get('reference_number')}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB Atlas connection failed: {e}")
        return False

def test_report_creation():
    """Test creating a sample report directly in database"""
    print("\n🧪 Testing Report Creation")
    print("=" * 50)
    
    try:
        from pymongo import MongoClient
        
        mongodb_uri = os.getenv('MONGODB_URI')
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=10000)
        
        db = client['valuation_db']
        
        # Create a test report
        test_report = {
            "reference_number": f"TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "bank_code": "SBI",
            "template_id": "land-property",
            "property_address": "Test Address for Diagnostic",
            "property_type": "land",
            "status": "draft",
            "report_data": {
                "test_field": "test_value",
                "diagnostic": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        print(f"📝 Creating test report: {test_report['reference_number']}")
        
        result = db.reports.insert_one(test_report)
        
        print(f"✅ Test report created with ID: {result.inserted_id}")
        
        # Verify it was saved
        saved_report = db.reports.find_one({"_id": result.inserted_id})
        if saved_report:
            print(f"✅ Report successfully retrieved from database")
            print(f"🔍 Status: {saved_report.get('status')}")
            print(f"🔍 Reference: {saved_report.get('reference_number')}")
        
        # Clean up - delete the test report
        db.reports.delete_one({"_id": result.inserted_id})
        print(f"🧹 Test report cleaned up")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Report creation test failed: {e}")
        return False

def check_backend_process():
    """Check if backend process is running"""
    print("\n🔍 Checking Backend Process")
    print("=" * 50)
    
    import subprocess
    
    try:
        # Check if python process running on port 8000
        result = subprocess.run(['lsof', '-i', ':8000'], 
                              capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0 and result.stdout:
            print("✅ Backend process found running on port 8000:")
            print(result.stdout)
            return True
        else:
            print("❌ No process found running on port 8000")
            return False
            
    except Exception as e:
        print(f"❌ Error checking backend process: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 MongoDB Atlas & Backend Diagnostic")
    print(f"🕐 Timestamp: {datetime.now().isoformat()}")
    
    # Test Atlas connection
    atlas_ok = test_atlas_connection()
    
    # Test report creation
    if atlas_ok:
        creation_ok = test_report_creation()
    
    # Check backend process
    backend_ok = check_backend_process()
    
    # Summary
    print("\n📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    print(f"MongoDB Atlas: {'✅ OK' if atlas_ok else '❌ FAILED'}")
    print(f"Report Creation: {'✅ OK' if atlas_ok and creation_ok else '❌ FAILED'}")
    print(f"Backend Process: {'✅ OK' if backend_ok else '❌ FAILED'}")
    
    if atlas_ok and backend_ok:
        print("\n✅ Infrastructure looks good!")
        print("🔍 If saves are still failing, check:")
        print("   - Frontend authentication tokens")
        print("   - Request payload validation")
        print("   - Browser network tab for errors")
    else:
        print("\n❌ Infrastructure issues found:")
        if not atlas_ok:
            print("   - Fix MongoDB Atlas connection")
        if not backend_ok:
            print("   - Start backend server: cd backend && python main.py")

if __name__ == "__main__":
    main()