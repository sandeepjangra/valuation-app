"""
Analyze specific saved report rpt_1c28206782a1 to understand template ID issue
"""
import os
import sys
import json
from pymongo import MongoClient
from datetime import datetime

# Add backend directory to Python path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend')
sys.path.append(backend_dir)

from database.multi_db_manager import MultiDatabaseManager

def analyze_specific_report():
    """Analyze report rpt_1c28206782a1"""
    try:
        # Initialize multi-database manager
        db_manager = MultiDatabaseManager()
        
        # Set organization context
        organization = 'sk-tindwal'
        db_manager.set_organization(organization)
        
        print(f"🔍 Analyzing report: rpt_1c28206782a1")
        print(f"📋 Reference: CEV/RVO/299/0007/19122025")
        print(f"🏢 Organization: {organization}")
        print("=" * 60)
        
        # Get the report
        report_id = 'rpt_1c28206782a1'
        reports_collection = db_manager.get_collection('reports')
        report = reports_collection.find_one({'report_id': report_id})
        
        if not report:
            print(f"❌ Report {report_id} not found in organization {organization}")
            return
        
        print(f"✅ Found report: {report['report_id']}")
        
        # Key fields to analyze
        key_fields = [
            'bank_code', 'bank_name', 'template_id', 'template_name',
            'property_type', 'custom_template_id', 'reference_number',
            'status', 'organizationId'
        ]
        
        print("\n📊 Key Report Metadata:")
        for field in key_fields:
            value = report.get(field, 'NOT SET')
            print(f"  {field:20}: {value}")
        
        # Check template structure
        template_structure = report.get('templateStructure')
        if template_structure:
            print(f"\n📋 Template Structure:")
            print(f"  totalFieldCount: {template_structure.get('totalFieldCount', 'Unknown')}")
            
            # Try to parse template snapshot
            template_snapshot = template_structure.get('templateDataSnapshot')
            if template_snapshot:
                try:
                    parsed_snapshot = json.loads(template_snapshot)
                    template_info = parsed_snapshot.get('templateInfo', {})
                    print(f"  Template Info from Snapshot:")
                    for key, value in template_info.items():
                        print(f"    {key}: {value}")
                except json.JSONDecodeError:
                    print("  Could not parse template snapshot")
        
        # Analyze form data for template clues
        form_data = report.get('form_data', {})
        print(f"\n📝 Form Data Analysis:")
        print(f"  Total form fields: {len(form_data)}")
        
        # Look for template-related fields
        template_clues = {}
        for key, value in form_data.items():
            if any(keyword in key.lower() for keyword in ['template', 'bank', 'branch', 'sbi']):
                template_clues[key] = value
        
        if template_clues:
            print(f"  Template-related fields found:")
            for key, value in template_clues.items():
                print(f"    {key}: {value}")
        
        # Check created/updated timestamps
        created_at = report.get('createdAt', report.get('created_at'))
        updated_at = report.get('updatedAt', report.get('updated_at'))
        
        print(f"\n⏰ Timestamps:")
        print(f"  Created:  {created_at}")
        print(f"  Updated:  {updated_at}")
        
        # Look for potential template derivation
        print(f"\n🔍 Template Derivation Analysis:")
        
        # Strategy 1: Bank branch analysis
        bank_branch = form_data.get('bank_branch')
        if bank_branch:
            print(f"  Bank Branch: {bank_branch}")
            if 'sbi' in bank_branch.lower():
                print(f"  → Could derive SBI template")
        
        # Strategy 2: Reference number analysis
        ref_number = report.get('reference_number', '')
        if ref_number.startswith('CEV'):
            print(f"  Reference starts with CEV → Likely SBI template")
        
        # Strategy 3: Look for property type indicators
        property_indicators = []
        for key in form_data.keys():
            if any(prop_type in key.lower() for prop_type in ['land', 'apartment', 'property']):
                property_indicators.append(key)
        
        if property_indicators:
            print(f"  Property type indicators: {property_indicators}")
        
        print(f"\n💡 Recommended Template Derivation:")
        print(f"  Bank Code: SBI (from reference CEV pattern)")
        print(f"  Property Type: land-property (most common)")
        print(f"  Template ID: SBI/land-property")
        
    except Exception as e:
        print(f"❌ Error analyzing report: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    analyze_specific_report()