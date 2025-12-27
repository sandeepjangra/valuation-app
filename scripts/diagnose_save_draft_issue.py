#!/usr/bin/env python3
"""
Diagnostic script to identify why draft reports are not being saved to database.

This script will:
1. Check MongoDB connection and collections
2. Test API endpoints for creating/updating reports
3. Analyze recent save requests and responses
4. Check for common issues like authentication, validation, etc.
"""

import sys
import os
import asyncio
import requests
import json
from datetime import datetime, timezone
import pymongo
from pymongo import MongoClient

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def check_mongodb_connection():
    """Check if MongoDB is running and accessible"""
    print_header("MongoDB Connection Check")
    
    try:
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB is running and accessible")
        
        # Check available databases
        databases = client.list_database_names()
        print(f"📋 Available databases: {databases}")
        
        # Check valuation_db specifically
        if 'valuation_db' in databases:
            db = client['valuation_db']
            collections = db.list_collection_names()
            print(f"📦 Collections in valuation_db: {collections}")
            
            # Check reports collection
            if 'reports' in collections:
                reports_count = db.reports.count_documents({})
                print(f"📄 Total reports in database: {reports_count}")
                
                # Get recent reports
                recent_reports = list(db.reports.find({}).sort('created_at', -1).limit(3))
                print(f"🕐 Recent reports: {len(recent_reports)} found")
                
                for i, report in enumerate(recent_reports):
                    print(f"   Report {i+1}: {report.get('reference_number', 'N/A')} - {report.get('status', 'N/A')}")
                
                return True, db
            else:
                print("❌ 'reports' collection not found in valuation_db")
                return False, None
        else:
            print("❌ 'valuation_db' database not found")
            return False, None
            
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False, None

def check_backend_api():
    """Check if backend API is running"""
    print_header("Backend API Check")
    
    base_url = "http://localhost:8000"
    
    try:
        # Check health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend API is running")
            print(f"📡 Health check response: {response.json()}")
            return True
        else:
            print(f"❌ Backend API health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend API - is it running on port 8000?")
        return False
    except Exception as e:
        print(f"❌ Backend API check failed: {e}")
        return False

def test_create_report_api():
    """Test the create report API endpoint"""
    print_header("Create Report API Test")
    
    # First, we need to authenticate to get a token
    # Let's try to call the API without auth first to see what happens
    
    base_url = "http://localhost:8000"
    
    # Sample report data
    test_data = {
        "bank_code": "SBI",
        "template_id": "land-property",
        "property_address": "Test Address for API Test",
        "property_type": "land",
        "report_data": {
            "test_field": "test_value",
            "status": "draft",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    }
    
    try:
        print("🧪 Testing POST /api/reports endpoint...")
        print(f"📤 Test data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(
            f"{base_url}/api/reports", 
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📨 Response status: {response.status_code}")
        print(f"📨 Response headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"📨 Response data: {json.dumps(response_data, indent=2)}")
        except:
            print(f"📨 Response text: {response.text}")
        
        if response.status_code in [200, 201]:
            print("✅ Create report API is working")
            return True
        elif response.status_code == 401:
            print("🔐 Authentication required - this is expected")
            return True  # This is actually good - means API is working but needs auth
        else:
            print(f"❌ Create report API failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Create report API test failed: {e}")
        return False

def test_update_report_api():
    """Test the update report API endpoint"""
    print_header("Update Report API Test")
    
    base_url = "http://localhost:8000"
    test_report_id = "507f1f77bcf86cd799439011"  # Sample ObjectId
    
    test_data = {
        "report_data": {
            "test_field": "updated_value",
            "status": "draft",
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        "status": "draft"
    }
    
    try:
        print(f"🧪 Testing PUT /api/reports/{test_report_id} endpoint...")
        print(f"📤 Test data: {json.dumps(test_data, indent=2)}")
        
        response = requests.put(
            f"{base_url}/api/reports/{test_report_id}", 
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📨 Response status: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"📨 Response data: {json.dumps(response_data, indent=2)}")
        except:
            print(f"📨 Response text: {response.text}")
        
        if response.status_code in [200, 404]:  # 404 expected for non-existent ID
            print("✅ Update report API is working")
            return True
        elif response.status_code == 401:
            print("🔐 Authentication required - this is expected")
            return True
        else:
            print(f"❌ Update report API failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Update report API test failed: {e}")
        return False

def analyze_logs():
    """Analyze backend logs for save-related errors"""
    print_header("Backend Logs Analysis")
    
    log_paths = [
        '/Users/sandeepjangra/Downloads/development/ValuationAppV1/logs/backend_logs.txt',
        '/Users/sandeepjangra/Downloads/development/ValuationAppV1/logs/backend_logs_new.txt',
        '/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend/logs'
    ]
    
    for log_path in log_paths:
        if os.path.exists(log_path):
            print(f"📄 Found log file: {log_path}")
            
            try:
                if os.path.isfile(log_path):
                    with open(log_path, 'r') as f:
                        lines = f.readlines()
                        
                    # Look for recent error/save related entries
                    recent_lines = lines[-50:]  # Last 50 lines
                    save_related = [line for line in recent_lines if any(keyword in line.lower() for keyword in ['save', 'draft', 'report', 'error', 'failed'])]
                    
                    if save_related:
                        print(f"🔍 Recent save-related log entries:")
                        for line in save_related[-10:]:  # Show last 10 relevant lines
                            print(f"   {line.strip()}")
                    else:
                        print("   No recent save-related log entries found")
                        
            except Exception as e:
                print(f"   ❌ Error reading log file: {e}")
        else:
            print(f"📄 Log file not found: {log_path}")

def check_frontend_network_calls():
    """Provide instructions for checking frontend network calls"""
    print_header("Frontend Network Debugging Instructions")
    
    print("To diagnose frontend save issues:")
    print()
    print("1. 🌐 Open browser and navigate to the report form")
    print("2. 🔧 Open Developer Tools (F12)")
    print("3. 📡 Go to Network tab")
    print("4. 🧹 Clear existing network calls")
    print("5. 📝 Fill some data in the form")
    print("6. 💾 Click 'Save Draft' or 'Save' button")
    print("7. 🔍 Check Network tab for:")
    print("   - Are POST/PUT requests being made to /api/reports?")
    print("   - What is the request payload?")
    print("   - What is the response status and body?")
    print("   - Any JavaScript errors in Console tab?")
    print()
    print("8. 📋 Look for these common issues:")
    print("   - 401 Unauthorized (auth token missing/expired)")
    print("   - 400 Bad Request (missing required fields)")
    print("   - 500 Internal Server Error (backend issues)")
    print("   - Network errors (CORS, connection issues)")

def main():
    """Run all diagnostic checks"""
    print("🚀 Starting Draft Report Save Diagnostic")
    print(f"🕐 Timestamp: {datetime.now().isoformat()}")
    
    # Check MongoDB
    mongo_ok, db = check_mongodb_connection()
    
    # Check Backend API
    api_ok = check_backend_api()
    
    # Test API endpoints
    if api_ok:
        create_ok = test_create_report_api()
        update_ok = test_update_report_api()
    
    # Analyze logs
    analyze_logs()
    
    # Frontend debugging instructions
    check_frontend_network_calls()
    
    # Summary
    print_header("Diagnostic Summary")
    
    print(f"📊 MongoDB Connection: {'✅ OK' if mongo_ok else '❌ FAILED'}")
    print(f"📊 Backend API: {'✅ OK' if api_ok else '❌ FAILED'}")
    
    if not mongo_ok:
        print("\n🔧 RECOMMENDED ACTIONS:")
        print("1. Start MongoDB: brew services start mongodb-community")
        print("2. Or check if MongoDB is running on different port")
    
    if not api_ok:
        print("\n🔧 RECOMMENDED ACTIONS:")
        print("1. Start backend server: cd backend && python main.py")
        print("2. Check if backend is running on port 8000")
    
    if mongo_ok and api_ok:
        print("\n✅ Basic infrastructure looks good!")
        print("🔍 Issue is likely in:")
        print("   - Frontend authentication/token handling")
        print("   - Request payload formatting")
        print("   - Backend validation logic")
        print("\nCheck browser Developer Tools Network tab while saving.")

if __name__ == "__main__":
    main()