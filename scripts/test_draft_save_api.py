#!/usr/bin/env python3
"""
Real-time diagnostic for draft save issues.
This script will test the actual API endpoints used by the frontend.
"""

import os
import sys
import json
import requests
from datetime import datetime, timezone

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_api_endpoint(method, url, headers=None, data=None):
    """Test an API endpoint and return detailed results"""
    print(f"\n🧪 Testing {method} {url}")
    print("-" * 60)
    
    try:
        if method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=30)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, headers=headers, timeout=30)
        else:
            response = requests.get(url, headers=headers, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"📊 Response Body: {json.dumps(response_json, indent=2)}")
        except:
            print(f"📊 Response Text: {response.text[:500]}...")
        
        return response.status_code, response.text
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error - Backend not running?")
        return None, None
    except requests.exceptions.Timeout:
        print("❌ Request Timeout")
        return None, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def get_auth_token():
    """Try to get an auth token - this will likely fail without proper credentials"""
    print("🔑 Authentication Test")
    print("-" * 60)
    
    # This is the usual flow - try to login first
    login_url = "http://localhost:8000/api/auth/login"
    login_data = {
        "username": "test@example.com",
        "password": "test123"
    }
    
    print("📝 Attempting login (may fail - that's OK for diagnosis)...")
    status, response = test_api_endpoint('POST', login_url, data=login_data)
    
    if status == 200:
        try:
            token_data = json.loads(response)
            token = token_data.get('access_token') or token_data.get('token')
            if token:
                print(f"✅ Got auth token: {token[:20]}...")
                return f"Bearer {token}"
        except:
            pass
    
    print("ℹ️ No auth token available - will test without authentication")
    return None

def test_create_report_api():
    """Test creating a new report"""
    print("\n" + "=" * 60)
    print("🆕 Testing CREATE REPORT API")
    print("=" * 60)
    
    # Get auth token
    auth_header = get_auth_token()
    headers = {'Content-Type': 'application/json'}
    if auth_header:
        headers['Authorization'] = auth_header
    
    # Create test report data that matches what frontend sends
    test_data = {
        "bank_code": "SBI",
        "template_id": "land-property", 
        "property_address": "API Test Address, Test City",
        "property_type": "land",
        "report_data": {
            "status": "draft",
            "bankName": "State Bank of India",
            "templateName": "SBI Land Property Template",
            "referenceNumber": f"API_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "organizationId": "sk-tindwal",
            "propertyType": "land",
            "reportType": "valuation_report",
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "updatedAt": datetime.now(timezone.utc).isoformat(),
            # Add some form data to simulate real usage
            "boundaries_and_dimensions": {
                "north": "Test North Boundary",
                "south": "Test South Boundary",
                "east": "Test East Boundary", 
                "west": "Test West Boundary"
            },
            "building_specifications": {
                "floor_area": "1000",
                "construction_type": "RCC"
            }
        }
    }
    
    print(f"📤 Request payload: {json.dumps(test_data, indent=2)}")
    
    create_url = "http://localhost:8000/api/reports"
    status, response = test_api_endpoint('POST', create_url, headers=headers, data=test_data)
    
    if status == 201:
        print("✅ Report creation successful!")
        try:
            response_data = json.loads(response)
            report_id = response_data.get('data', {}).get('report_id')
            if report_id:
                return report_id
        except:
            pass
    elif status == 401:
        print("🔐 Authentication required - this is the likely issue!")
        print("📋 Frontend may not be sending valid auth token")
    elif status == 400:
        print("📝 Bad Request - check required fields")
    elif status == 403:
        print("🔒 Permission denied - check user roles")
    
    return None

def test_update_report_api(report_id=None):
    """Test updating an existing report"""
    print("\n" + "=" * 60)
    print("📝 Testing UPDATE REPORT API")
    print("=" * 60)
    
    if not report_id:
        # Use a dummy ObjectId for testing
        report_id = "507f1f77bcf86cd799439011"
        print(f"ℹ️ Using dummy report ID: {report_id}")
    
    # Get auth token
    auth_header = get_auth_token()
    headers = {'Content-Type': 'application/json'}
    if auth_header:
        headers['Authorization'] = auth_header
    
    # Update data that matches what frontend sends
    update_data = {
        "report_data": {
            "status": "draft",
            "updatedAt": datetime.now(timezone.utc).isoformat(),
            # Updated form data
            "boundaries_and_dimensions": {
                "north": "Updated North Boundary",
                "south": "Updated South Boundary",
                "east": "Updated East Boundary",
                "west": "Updated West Boundary",
                "area": "2000 sq ft"
            },
            "building_specifications": {
                "floor_area": "1200",
                "construction_type": "RCC Frame",
                "floors": "2"
            }
        },
        "status": "draft"
    }
    
    print(f"📤 Update payload: {json.dumps(update_data, indent=2)}")
    
    update_url = f"http://localhost:8000/api/reports/{report_id}"
    status, response = test_api_endpoint('PUT', update_url, headers=headers, data=update_data)
    
    if status == 200:
        print("✅ Report update successful!")
    elif status == 404:
        print("📄 Report not found (expected for dummy ID)")
    elif status == 401:
        print("🔐 Authentication required - this is the likely issue!")
    elif status == 400:
        print("📝 Bad Request - check payload format")

def check_organization_context():
    """Test organization context endpoint"""
    print("\n" + "=" * 60)
    print("🏢 Testing ORGANIZATION CONTEXT")
    print("=" * 60)
    
    # Test org context which is required for most operations
    org_url = "http://localhost:8000/api/organizations/sk-tindwal"
    status, response = test_api_endpoint('GET', org_url)
    
    if status == 200:
        print("✅ Organization context working")
    elif status == 401:
        print("🔐 Authentication required for org access")
    elif status == 404:
        print("❌ Organization not found")

def main():
    """Run comprehensive API tests"""
    print("🚀 Draft Save API Diagnostic")
    print(f"🕐 Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)
    
    print("This script tests the exact API calls made by the frontend")
    print("when saving draft reports to identify where the issue is.")
    
    # Test organization context
    check_organization_context()
    
    # Test create report
    report_id = test_create_report_api()
    
    # Test update report
    test_update_report_api(report_id)
    
    # Final recommendations
    print("\n" + "=" * 60)
    print("🔍 DIAGNOSTIC CONCLUSIONS")
    print("=" * 60)
    
    print("Based on the API tests above, common issues are:")
    print()
    print("1. 🔐 AUTHENTICATION:")
    print("   - Frontend not sending valid JWT token")
    print("   - Token expired or malformed")
    print("   - Check browser localStorage/sessionStorage for token")
    print()
    print("2. 📝 REQUEST PAYLOAD:")
    print("   - Missing required fields (bank_code, template_id, etc.)")
    print("   - Incorrect data format")
    print("   - Check browser Network tab for actual payload")
    print()
    print("3. 🏢 ORGANIZATION CONTEXT:")
    print("   - User not authenticated for organization 'sk-tindwal'")
    print("   - Organization database access issues")
    print()
    print("4. 🔧 NEXT STEPS:")
    print("   - Open browser DevTools Network tab")
    print("   - Try to save a draft and watch the requests")
    print("   - Check if POST/PUT requests are made to /api/reports")
    print("   - Look at request headers (Authorization) and payload")
    print("   - Check Console tab for JavaScript errors")

if __name__ == "__main__":
    main()