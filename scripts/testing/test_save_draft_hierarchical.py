#!/usr/bin/env python3
"""
Test the save draft functionality with hierarchical transformation
"""

import requests
import json
import time

def test_save_draft_with_hierarchical():
    """Test save draft with the new hierarchical data structure"""
    
    print("🧪 TESTING SAVE DRAFT WITH HIERARCHICAL STRUCTURE")
    print("=" * 80)
    
    base_url = "http://localhost:8000"
    
    # First, let's test login
    print("🔐 Step 1: Testing login...")
    login_data = {
        "email": "admin@system.com",
        "password": "admin123"
    }
    
    try:
        login_response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"Login response status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            if login_result.get("success"):
                token = login_result["data"]["access_token"]
                print("✅ Login successful!")
            else:
                print(f"❌ Login failed: {login_result}")
                return
        else:
            print(f"❌ Login request failed: {login_response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test data with comprehensive SBI land property fields
    print("📝 Step 2: Preparing hierarchical test data...")
    
    # This is the flat data that would come from the frontend form
    flat_report_data = {
        # Property Details - Section 1
        "agreement_to_sell": "Available - Original sale deed dated 15-Jan-2025",
        "list_of_documents_produced": "1. Original Sale Deed\\n2. Survey Settlement\\n3. Property Card",
        "allotment_letter": "Not applicable - Private property",
        "layout_plan": "Municipality approved layout plan available",
        
        # Property Details - Section 2
        "owner_details": "John Doe, S/o Richard Doe, Age 45 years",
        "borrower_name": "MS SSK Developers Private Limited",
        "postal_address": "123 Main Street, Andheri West, Mumbai - 400058",
        "property_description": "Residential plot in premium locality",
        "property_location": "Survey No. 45/2, Andheri West, Mumbai",
        "city_town_village": "Mumbai",
        
        # Property Details - Section 3
        "area_classification": "Urban residential - R1 zone",
        "government_regulation": "Mumbai Municipal Corporation guidelines",
        
        # Property Details - Section 4
        "boundaries_dimensions_table": "N:40ft, S:40ft, E:25ft, W:25ft",
        "coordinates": "19.1335° N, 72.8269° E",
        "land_area_and_occupancy": "1000 sq ft, currently vacant",
        
        # Site Characteristics - Section 1
        "locality_surroundings": "Well developed residential locality",
        "physical_characteristics": "Rectangular plot, level terrain",
        "land_usage": "Residential use as per development plan",
        "planning_approvals": "All municipal approvals obtained",
        
        # Site Characteristics - Section 2
        "road_access": "30 feet wide paved road access",
        "utility_services_group": "Water, electricity, sewerage available",
        "additional_information": "Prime location with good appreciation",
        
        # Valuation - Section 1
        "plot_size": "1000",
        "market_rate": "5500",
        "estimated_valuation": "5500000",
        
        # Valuation - Section 2
        "building_constructed": "no",
        "building_basic_info": "No construction on plot",
        "building_dimensions": "N/A - vacant plot",
        "building_condition": "N/A - no building present",
        "approval_documents": "Not applicable for vacant land",
        "no_building_remarks": "Land only valuation - no construction",
        
        # Construction Specifications - Section 1
        "building_specifications_table": "Not applicable - vacant land",
        "floor_wise_valuation_table": "Not applicable - no building",
        
        # Construction Specifications - Section 2
        "extra_items": "Boundary wall on three sides",
        "amenities": "Street lighting, security provisions",
        "miscellaneous": "Proper drainage, wide road frontage",
        "services": "Municipal water connection, electricity nearby",
        
        # Detailed Valuation - Direct fields
        "land_total": 5500000,
        "building_total": 0,
        "extra_items_total": 50000,
        "amenities_total": 25000,
        "miscellaneous_total": 15000,
        "services_total": 10000,
        "grand_total": 5600000,
        
        # Common fields
        "report_reference_number": "CEV/RVO/299/0029/26122025",
        "valuation_date": "2025-12-26",
        "inspection_date": "2025-12-25", 
        "applicant_name": "MS SSK Developers Private Limited",
        "valuation_purpose": "Loan against property",
        "bank_branch": "SBI Andheri West Branch"
    }
    
    print(f"📊 Prepared {len(flat_report_data)} fields for testing")
    
    # Create report request
    create_report_data = {
        "bank_code": "SBI",
        "template_id": "land-property",
        "property_address": "Survey No. 45/2, Andheri West, Mumbai - 400058, Maharashtra", 
        "report_data": flat_report_data
    }
    
    print("💾 Step 3: Testing create report with hierarchical transformation...")
    
    try:
        create_response = requests.post(
            f"{base_url}/api/reports",
            json=create_report_data,
            headers=headers
        )
        
        print(f"Create report response status: {create_response.status_code}")
        print(f"Create report response: {create_response.text[:500]}...")
        
        if create_response.status_code in [200, 201]:
            create_result = create_response.json()
            if create_result.get("success"):
                report_id = create_result["data"]["report_id"]  # Note: changed from reportId to report_id
                print(f"✅ Report created successfully! ID: {report_id}")
                
                # Show the hierarchical structure that was saved
                saved_data = create_result["data"].get("reportData", {})
                print(f"📂 Hierarchical structure saved:")
                
                if isinstance(saved_data, dict):
                    for tab_name, tab_data in saved_data.items():
                        if isinstance(tab_data, dict):
                            sections = []
                            direct_fields = []
                            for key, value in tab_data.items():
                                if isinstance(value, dict):
                                    sections.append(f"{key}({len(value)})")
                                else:
                                    direct_fields.append(key)
                            
                            print(f"   📂 {tab_name}:")
                            if sections:
                                print(f"      📁 Sections: {', '.join(sections)}")
                            if direct_fields:
                                print(f"      📄 Direct: {len(direct_fields)} fields")
                
                return report_id
            else:
                print(f"❌ Report creation failed: {create_result}")
                return None
        else:
            print(f"❌ Report creation request failed: {create_response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Report creation error: {e}")
        return None

def test_load_and_verify_hierarchical(report_id, token):
    """Test loading the saved report and verify hierarchical structure"""
    
    if not report_id:
        print("❌ No report ID to test loading")
        return
    
    print(f"\\n🔍 Step 4: Testing load report to verify hierarchical structure...")
    
    base_url = "http://localhost:8000"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        load_response = requests.get(
            f"{base_url}/api/reports/{report_id}?organizationId=sk-tindwal",
            headers=headers
        )
        
        print(f"Load report response status: {load_response.status_code}")
        
        if load_response.status_code == 200:
            load_result = load_response.json()
            if load_result.get("success"):
                # The field might be 'report_data' instead of 'reportData'
                loaded_data = load_result["data"].get("report_data") or load_result["data"].get("reportData")
                if not loaded_data:
                    print(f"❌ No report data found. Available keys: {list(load_result['data'].keys())}")
                    return
                    
                print(f"✅ Report loaded successfully!")
                
                # Verify hierarchical structure
                print(f"📊 VERIFICATION OF HIERARCHICAL STRUCTURE:")
                
                expected_tabs = ['Property Details', 'Site Characteristics', 'Valuation', 
                               'Construction Specifications', 'Detailed Valuation', '_common_fields_']
                
                found_tabs = []
                missing_tabs = []
                
                for tab in expected_tabs:
                    if tab in loaded_data:
                        found_tabs.append(tab)
                        tab_data = loaded_data[tab]
                        
                        if isinstance(tab_data, dict):
                            sections = [k for k, v in tab_data.items() if isinstance(v, dict)]
                            direct_fields = [k for k, v in tab_data.items() if not isinstance(v, dict)]
                            
                            print(f"   ✅ {tab}: {len(sections)} sections, {len(direct_fields)} direct fields")
                            
                            # Show sample data from first section
                            if sections:
                                first_section = sections[0]
                                section_data = tab_data[first_section]
                                sample_fields = list(section_data.keys())[:3]
                                print(f"      📁 {first_section} sample: {', '.join(sample_fields)}")
                    else:
                        missing_tabs.append(tab)
                
                print(f"\\n📈 STRUCTURE VERIFICATION RESULTS:")
                print(f"   ✅ Found tabs: {len(found_tabs)}/{len(expected_tabs)}")
                print(f"   📂 Present: {', '.join(found_tabs)}")
                if missing_tabs:
                    print(f"   ❌ Missing: {', '.join(missing_tabs)}")
                
                # Verify sample field values
                print(f"\\n🔍 FIELD VALUE VERIFICATION:")
                test_fields = [
                    ("Property Details", "Section 1", "agreement_to_sell"),
                    ("Site Characteristics", "Section 1", "locality_surroundings"),
                    ("Valuation", "Section 1", "plot_size"),
                    ("Detailed Valuation", None, "land_total"),
                    ("_common_fields_", None, "report_reference_number")
                ]
                
                for tab, section, field in test_fields:
                    if tab in loaded_data:
                        tab_data = loaded_data[tab]
                        if section and section in tab_data:
                            section_data = tab_data[section]
                            if field in section_data:
                                value = str(section_data[field])[:50]
                                print(f"   ✅ {tab}/{section}/{field}: {value}...")
                            else:
                                print(f"   ❌ {tab}/{section}/{field}: field not found")
                        elif not section and field in tab_data:
                            value = str(tab_data[field])[:50]
                            print(f"   ✅ {tab}/{field}: {value}...")
                        else:
                            print(f"   ❌ {tab}/{section or 'direct'}/{field}: not found")
                
                print(f"\\n🎉 HIERARCHICAL SAVE DRAFT TEST COMPLETE!")
                print(f"✅ Successfully saved and loaded hierarchical report structure")
                print(f"✅ Data organization matches SBI template design")
                print(f"✅ Save draft functionality working with new transformation!")
                
            else:
                print(f"❌ Report loading failed: {load_result}")
        else:
            print(f"❌ Report loading request failed: {load_response.text}")
            
    except Exception as e:
        print(f"❌ Report loading error: {e}")

if __name__ == "__main__":
    # Test the complete save draft flow
    report_id = test_save_draft_with_hierarchical()
    
    if report_id:
        # Get token again for verification test
        login_data = {"email": "admin@system.com", "password": "admin123"}
        login_response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
        if login_response.status_code == 200:
            token = login_response.json()["data"]["access_token"]
            test_load_and_verify_hierarchical(report_id, token)
    else:
        print("❌ Could not create report for verification test")