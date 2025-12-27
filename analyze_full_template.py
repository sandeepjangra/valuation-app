#!/usr/bin/env python3
"""
Analyze template structure to see group fields in sections
"""

import requests
import json

def analyze_template_structure():
    """Analyze the full template structure"""
    
    try:
        response = requests.get("http://localhost:8000/api/templates/SBI/land-property/aggregated-fields", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Failed to get template: {response.status_code}")
            return
        
        data = response.json()
        
        print("🔍 TEMPLATE STRUCTURE ANALYSIS")
        print("=" * 80)
        
        # Check if we have tabs
        tabs = data.get('tabs', [])
        if tabs:
            print(f"📂 Found {len(tabs)} tabs")
            
            for tab in tabs:
                tab_id = tab.get('tabId', 'unknown')
                tab_name = tab.get('tabName', 'unknown')
                print(f"\n📁 TAB: {tab_id} - {tab_name}")
                
                sections = tab.get('sections', [])
                print(f"   📄 Sections: {len(sections)}")
                
                for section in sections:
                    section_id = section.get('sectionId', 'unknown')
                    section_name = section.get('sectionName', 'unknown')
                    print(f"   📋 SECTION: {section_id} - {section_name}")
                    
                    fields = section.get('fields', [])
                    print(f"      🔧 Fields: {len(fields)}")
                    
                    group_count = 0
                    regular_count = 0
                    
                    for field in fields:
                        field_id = field.get('fieldId', 'unknown')
                        field_type = field.get('fieldType', 'unknown')
                        display_name = field.get('uiDisplayName', 'unknown')
                        
                        if field_type == 'group':
                            group_count += 1
                            subfields = field.get('subFields', [])
                            print(f"         🔗 GROUP: {field_id} ({display_name}) - {len(subfields)} subfields")
                            
                            for subfield in subfields[:3]:  # Show first 3 subfields
                                sub_id = subfield.get('fieldId', 'unknown')
                                sub_name = subfield.get('uiDisplayName', 'unknown')
                                print(f"            ↳ {sub_id} ({sub_name})")
                            
                            if len(subfields) > 3:
                                print(f"            ↳ ... and {len(subfields) - 3} more")
                        else:
                            regular_count += 1
                            print(f"         📄 {field_id} ({field_type}): {display_name}")
                    
                    print(f"      📊 Summary: {group_count} groups, {regular_count} regular fields")
        else:
            print("❌ No tabs found in template")
            
            # Check if data has fields directly
            if 'fields' in data:
                print("🔧 Found direct fields structure")
                fields = data['fields']
                print(f"Total fields: {len(fields)}")
            
            # Check other keys
            print("Available keys:", list(data.keys()))
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    analyze_template_structure()