#!/usr/bin/env python3
"""
Test the simple transformation with dynamic table handling
"""

import requests
import json

def test_simple_transformation():
    """Test the new simple transformation approach"""
    
    print("🧪 TESTING SIMPLE TRANSFORMATION")
    print("=" * 80)
    
    # Login to sk-tindwal org
    login_data = {"email": "sk.tindwal@gmail.com", "password": "admin123"}
    
    try:
        login_response = requests.post("http://localhost:8000/api/auth/login", json=login_data, timeout=10)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return
        
        token = login_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        print("✅ Login successful for sk.tindwal@gmail.com")
        
        # Simple test payload with different data types including tables
        test_payload = {
            # Regular fields
            "property_address": "Simple Test Property",
            "valuation_date": "2025-12-27",
            "applicant_name": "Test User",
            "inspector_name": "Inspector Smith",
            "plot_survey_no": "Plot-123",
            "door_no": "Door-456",
            "area_type": "residential",
            "municipal_corporation": "test_corp",
            
            # Dynamic table data
            "building_specifications_table": [
                {
                    "item": "Foundation",
                    "material": "RCC", 
                    "area_sqft": 1200,
                    "rate_per_sqft": 500,
                    "total_value": 600000
                },
                {
                    "item": "Walls",
                    "material": "Brick",
                    "area_sqft": 800, 
                    "rate_per_sqft": 300,
                    "total_value": 240000
                }
            ],
            
            # Another table format
            "floor_wise_valuation": [
                {"floor": "Ground Floor", "area": 1200, "rate": 2000, "value": 2400000},
                {"floor": "First Floor", "area": 1000, "rate": 1800, "value": 1800000}
            ],
            
            # System metadata (should be filtered out)
            "status": "draft",
            "bankName": "State Bank of India", 
            "organizationId": "sk-tindwal"
        }
        
        print(f"📋 Test payload contains:")
        print(f"   📄 Regular fields: 8")
        print(f"   📊 Table fields: 2")
        print(f"   🗑️ Metadata fields: 3 (should be filtered)")
        
        # Create report to test transformation
        create_payload = {
            "bank_code": "SBI",
            "template_id": "land-property",
            "report_data": test_payload,
            "property_address": "Simple Test Property",
            "organization_id": "sk-tindwal"
        }
        
        print(f"\n🔨 Creating test report...")
        
        response = requests.post(
            "http://localhost:8000/api/reports",
            headers=headers,
            json=create_payload,
            timeout=30
        )
        
        print(f"📥 Create report response: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            if result.get("success"):
                report_id = result["data"]["report_id"]
                print(f"✅ Test report created: {report_id}")
                
                # Analyze the structure
                report_data = result["data"]["report_data"]
                
                print(f"\n📊 SIMPLE TRANSFORMATION RESULTS:")
                
                # Check for tables section
                if "tables" in report_data:
                    tables_section = report_data["tables"]
                    print(f"   📊 Tables section: {len(tables_section)} tables found")
                    for table_id, table_def in tables_section.items():
                        structure = table_def.get("structure", {})
                        rows = structure.get("rows", [])
                        columns = structure.get("columns", [])
                        print(f"      📋 {table_id}: {len(rows)} rows, {len(columns)} columns")
                else:
                    print(f"   ❌ No tables section found")
                
                # Check for regular report data
                if "report_data" in report_data:
                    main_data = report_data["report_data"]
                    print(f"   📄 Main report data: {len(main_data)} fields")
                    
                    # Check if tables are also in main data
                    table_fields_in_main = [k for k in main_data.keys() if 'table' in k.lower() or isinstance(main_data[k], list)]
                    print(f"   📊 Table fields in main data: {len(table_fields_in_main)}")
                else:
                    print(f"   ❌ No report_data section found")
                
                # Check for common fields
                if "_common_fields_" in report_data:
                    common_fields = report_data["_common_fields_"]
                    print(f"   📋 Common fields: {len(common_fields)} fields")
                else:
                    print(f"   📋 Common fields: 0 fields")
                
                # Check for _unmapped_ (should be minimal or empty)
                if "_unmapped_" in report_data:
                    unmapped = report_data["_unmapped_"]
                    print(f"   ⚠️ Unmapped fields: {len(unmapped)} (should be 0 or very few)")
                else:
                    print(f"   ✅ No unmapped fields (perfect!)")
                
                print(f"\n✅ ASSESSMENT:")
                
                # Success criteria
                success_criteria = []
                
                if "tables" in report_data and len(report_data["tables"]) > 0:
                    success_criteria.append("✅ Tables properly detected and structured")
                else:
                    success_criteria.append("❌ Tables not properly detected")
                
                if "_unmapped_" not in report_data or len(report_data.get("_unmapped_", {})) == 0:
                    success_criteria.append("✅ No unmapped fields - clean structure")
                else:
                    success_criteria.append(f"⚠️ {len(report_data.get('_unmapped_', {}))} unmapped fields")
                
                if "report_data" in report_data and len(report_data["report_data"]) > 5:
                    success_criteria.append("✅ Regular fields properly saved")
                else:
                    success_criteria.append("❌ Regular fields missing or insufficient")
                
                for criterion in success_criteria:
                    print(f"   {criterion}")
                
                return report_id
                    
        else:
            print(f"❌ Create failed: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        print(f"💡 Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_simple_transformation()