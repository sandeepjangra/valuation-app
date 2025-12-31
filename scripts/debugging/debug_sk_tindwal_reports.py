#!/usr/bin/env python3
"""
Debug readonly fields in sk-tindwal org reports
"""
import os
import sys
sys.path.append('/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend')

from pymongo import MongoClient
import json
from dotenv import load_dotenv

def check_sk_tindwal_reports():
    print("🔍 Checking readonly fields in sk-tindwal org reports...")
    
    # Load environment variables
    load_dotenv('/Users/sandeepjangra/Downloads/development/ValuationAppV1/.env')
    
    mongodb_uri = os.getenv('MONGODB_URI')
    if not mongodb_uri:
        print("❌ MONGODB_URI not found in environment variables")
        return
    
    # Connect to MongoDB Atlas
    try:
        client = MongoClient(mongodb_uri)
        print("✅ Connected to MongoDB Atlas")
        
        # Specific check for sk-tindwal organization
        sk_db = client['sk-tindwal']
        
        collections = sk_db.list_collection_names()
        print(f"Collections in sk-tindwal: {collections}")
        
        if 'reports' not in collections:
            print("❌ No 'reports' collection found in sk-tindwal database")
            return
            
        reports_collection = sk_db['reports']
        
        # Get report count
        total_reports = reports_collection.count_documents({})
        print(f"📊 Total reports in sk-tindwal: {total_reports}")
        
        # Find recent reports
        reports = list(reports_collection.find({}).sort('created_at', -1).limit(3))
        
        print(f"\n📄 Analyzing {len(reports)} recent reports:")
        
        for i, report in enumerate(reports, 1):
            print(f"\n{'='*50}")
            print(f"REPORT {i}")
            print(f"{'='*50}")
            print(f"ID: {report.get('_id')}")
            print(f"Status: {report.get('status')}")
            print(f"Created: {report.get('created_at')}")
            
            # Check top-level reference number
            top_ref = report.get('reference_number')
            print(f"🏷️  Top-level reference_number: {top_ref}")
            
            # Check report_data
            report_data = report.get('report_data', {})
            print(f"📊 Report data structure exists: {bool(report_data)}")
            
            if report_data:
                # Look for report_reference_number in data
                ref_num = report_data.get('report_reference_number')
                print(f"🏷️  report_reference_number in data: {ref_num}")
                
                # Look for calculated/readonly fields
                readonly_fields = [
                    'report_reference_number',
                    'estimated_value_of_land', 
                    'total_value',
                    'calculated_area',
                    'total_cost',
                    'land_area',
                    'land_rate_per_sq_unit', 
                    'total_land_value',
                    'market_value',
                    'final_valuation'
                ]
                
                print(f"\n🔒 READONLY FIELD VALUES:")
                found_readonly = False
                for field in readonly_fields:
                    value = report_data.get(field)
                    if value is not None:
                        print(f"  ✅ {field}: {value}")
                        found_readonly = True
                
                if not found_readonly:
                    print("  ❌ No readonly fields found with values")
                
                # Look for any calculation-related fields
                print(f"\n🧮 CALCULATION-RELATED FIELDS:")
                calc_fields = {}
                for key, value in report_data.items():
                    if any(term in key.lower() for term in ['total', 'calculated', 'value', 'amount', 'cost', 'price', 'rate']):
                        calc_fields[key] = value
                
                if calc_fields:
                    for k, v in list(calc_fields.items())[:10]:  # Show first 10
                        print(f"  📊 {k}: {v}")
                else:
                    print("  ❌ No calculation fields found")
                
                # Show sample of all field names for structure analysis
                all_keys = list(report_data.keys())
                print(f"\n📋 SAMPLE FIELD NAMES ({len(all_keys)} total):")
                for key in all_keys[:20]:  # Show first 20
                    value = report_data.get(key)
                    value_type = type(value).__name__
                    value_preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                    print(f"  {key} ({value_type}): {value_preview}")
                
                if len(all_keys) > 20:
                    print(f"  ... and {len(all_keys) - 20} more fields")
            else:
                print("❌ No report_data found")
        
        print(f"\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        
        # Check if reference numbers are being generated
        ref_numbers = [r.get('reference_number') for r in reports if r.get('reference_number')]
        data_ref_numbers = [r.get('report_data', {}).get('report_reference_number') for r in reports 
                          if r.get('report_data', {}).get('report_reference_number')]
        
        print(f"📊 Reports with top-level reference_number: {len(ref_numbers)}")
        print(f"📊 Reports with report_data.report_reference_number: {len(data_ref_numbers)}")
        
        if ref_numbers:
            print(f"📋 Sample reference numbers: {ref_numbers[:3]}")
        if data_ref_numbers:
            print(f"📋 Sample data reference numbers: {data_ref_numbers[:3]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_sk_tindwal_reports()