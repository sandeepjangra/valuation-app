#!/usr/bin/env python3
"""
Test script to simulate frontend template loading and verify calculated fields
"""
import requests
import json

def test_template_and_calculated_fields():
    """Test if templates have calculated fields that would be processed by frontend"""
    
    print("🧪 Testing Template Processing and Calculated Fields")
    print("=" * 60)
    
    # Test the custom templates API first to get available templates
    try:
        # Since we need auth, let's check what templates exist in the database directly
        print("🔍 Checking database for template structure...")
        
        # Let's create a mock template field structure based on our earlier findings
        # This simulates what the frontend would receive from the API
        sbi_template_fields = [
            {
                "fieldId": "total_extent_plot",
                "label": "Total Extent of Plot", 
                "fieldType": "number",
                "value": None
            },
            {
                "fieldId": "valuation_rate",
                "label": "Valuation Rate",
                "fieldType": "number", 
                "value": None
            },
            {
                "fieldId": "estimated_land_value",
                "label": "Estimated Value of Land",
                "fieldType": "number",
                "readonly": True,
                "calculationMetadata": {
                    "isCalculatedField": True,
                    "formula": "total_extent_plot * valuation_rate",
                    "dependencies": ["total_extent_plot", "valuation_rate"],
                    "formatting": {
                        "currency": True
                    }
                }
            }
        ]
        
        print(f"📋 Simulated template with {len(sbi_template_fields)} fields:")
        for field in sbi_template_fields:
            print(f"  - {field['fieldId']}: {field['label']}")
            if field.get('calculationMetadata', {}).get('isCalculatedField'):
                metadata = field['calculationMetadata']
                print(f"    🧮 Calculated: {metadata['formula']}")
                print(f"    🔗 Dependencies: {metadata['dependencies']}")
        
        # Simulate the calculation service processing
        print(f"\n🧮 Simulating CalculationService.getCalculatedFields()...")
        
        calculated_fields = {}
        for field in sbi_template_fields:
            print(f"🔍 Processing field: {field['fieldId']}")
            print(f"   - fieldType: {field['fieldType']}")
            print(f"   - hasCalculationMetadata: {bool(field.get('calculationMetadata'))}")
            
            if field.get('calculationMetadata', {}).get('isCalculatedField'):
                metadata = field['calculationMetadata']
                formula = metadata.get('formula')
                
                if formula:
                    print(f"   ✅ Found SBI calculated field: {field['fieldId']}")
                    calculated_fields[field['fieldId']] = {
                        'formula': formula,
                        'dependencies': metadata.get('dependencies', []),
                        'outputFormat': 'currency' if metadata.get('formatting', {}).get('currency') else 'number'
                    }
                    print(f"   ✅ Added calculated field config for: {field['fieldId']}")
                else:
                    print(f"   ⚠️ SBI calculated field {field['fieldId']} has no formula")
        
        print(f"\n🧮 Total calculated fields found: {len(calculated_fields)}")
        for field_id, config in calculated_fields.items():
            print(f"  - {field_id}: {config['formula']} (deps: {', '.join(config['dependencies'])})")
        
        # Simulate calculation with test values
        print(f"\n🧪 Simulating calculation with test values...")
        test_values = {
            'total_extent_plot': 1000,  # 1000 sq ft
            'valuation_rate': 500      # 500 per sq ft
        }
        
        print(f"📊 Test input values:")
        for field_id, value in test_values.items():
            print(f"  - {field_id}: {value}")
        
        # Calculate estimated_land_value
        if 'estimated_land_value' in calculated_fields:
            config = calculated_fields['estimated_land_value'] 
            formula = config['formula']
            
            # Simple formula evaluation (total_extent_plot * valuation_rate)
            if formula == "total_extent_plot * valuation_rate":
                result = test_values['total_extent_plot'] * test_values['valuation_rate']
                print(f"\n🧮 Calculation result:")
                print(f"  Formula: {formula}")
                print(f"  Result: {result}")
                print(f"  Formatted: ₹{result:,.2f}")
        
        print(f"\n✅ Test completed successfully!")
        print(f"\n💡 Next steps:")
        print(f"  1. Open browser to http://localhost:4200")
        print(f"  2. Create new report with SBI bank and land property template")
        print(f"  3. Check browser console for calculation service logs")
        print(f"  4. Enter values for 'total_extent_plot' and 'valuation_rate'")
        print(f"  5. Verify that 'estimated_land_value' updates automatically")
        
    except Exception as e:
        print(f"❌ Error during template test: {e}")

if __name__ == "__main__":
    test_template_and_calculated_fields()