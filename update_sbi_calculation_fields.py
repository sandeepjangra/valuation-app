#!/usr/bin/env python3
"""
Update SBI Land template to include enhanced calculation features
"""
import os
import sys
from datetime import datetime, timezone
from pymongo import MongoClient
from bson import ObjectId

# Load environment
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    print('❌ MONGODB_URI not set in environment. Aborting.')
    sys.exit(1)

def update_valuation_fields():
    """Update the valuation fields with enhanced calculation features"""
    
    # Enhanced calculation fields for the Valuation tab
    enhanced_valuation_fields = [
        {
            "fieldId": "total_extent_plot",
            "technicalName": "total_extent_plot",
            "uiDisplayName": "Total Extent of the Plot",
            "fieldType": "number_with_unit",
            "units": ["sqyd", "sqm", "sqft", "acres"],
            "isRequired": True,
            "sortOrder": 2,
            "validation": {
                "min": 1,
                "max": 999999,
                "step": 0.01
            },
            "calculationTrigger": True,
            "dependentFields": ["estimated_land_value"],
            "uiHints": {
                "highlightOnFocus": True,
                "showInCalculation": True
            }
        },
        {
            "fieldId": "valuation_rate", 
            "technicalName": "valuation_rate",
            "uiDisplayName": "Valuation Rate (per unit)",
            "fieldType": "currency",
            "isRequired": True,
            "placeholder": "Enter rate per sq unit",
            "sortOrder": 5,
            "validation": {
                "min": 1,
                "max": 999999999
            },
            "calculationTrigger": True,
            "dependentFields": ["estimated_land_value"],
            "uiHints": {
                "highlightOnFocus": True,
                "showInCalculation": True,
                "currencySymbol": "₹"
            }
        },
        {
            "fieldId": "estimated_land_value",
            "technicalName": "estimated_land_value", 
            "uiDisplayName": "Estimated Value of Land",
            "fieldType": "calculated",
            "isReadonly": True,
            "sortOrder": 6,
            "calculation": {
                "formula": "total_extent_plot * valuation_rate",
                "dependencies": ["total_extent_plot", "valuation_rate"],
                "displayFormat": "currency",
                "precision": 2,
                "realTimeUpdate": True,
                "showCalculationSteps": True,
                "calculationDisplay": {
                    "showFormula": True,
                    "formulaTemplate": "{total_extent_plot} × {valuation_rate} = ₹{result}",
                    "showInRealTime": True,
                    "highlightOnUpdate": True
                }
            },
            "autoPopulate": {
                "targetField": "land_total",
                "targetSection": "total",
                "targetCategory": "detailed_valuation", 
                "enabled": True,
                "triggerOnChange": True
            },
            "uiHints": {
                "showCalculationBox": True,
                "highlightResult": True,
                "animateChanges": True,
                "backgroundColor": "#f0f9ff"
            }
        }
    ]
    
    return enhanced_valuation_fields

def update_detailed_valuation_fields():
    """Update the detailed valuation land field to show auto-population"""
    
    enhanced_land_field = {
        "fieldId": "land_total",
        "technicalName": "land_total",
        "uiDisplayName": "Land", 
        "fieldType": "currency",
        "placeholder": "Amount in Rs",
        "sortOrder": 1,
        "autoPopulated": {
            "sourceField": "estimated_land_value",
            "sourceCategory": "valuation",
            "enabled": True,
            "allowManualOverride": True,
            "showSourceInfo": True
        },
        "uiHints": {
            "showAutoPopulateIcon": True,
            "sourceReferenceText": "Auto-calculated from Valuation → Estimated Value of Land",
            "highlightIfAutoFilled": True,
            "allowEdit": True,
            "confirmOverride": False
        },
        "validation": {
            "min": 0,
            "max": 999999999999
        }
    }
    
    return enhanced_land_field

async def update_mongodb_collection():
    """Update the MongoDB collection with enhanced calculation fields"""
    
    try:
        print("🔗 Connecting to MongoDB Atlas...")
        client = MongoClient(MONGODB_URI)
        db = client['valuation_admin']
        collection = db['sbi_land_property_details']
        
        print("📝 Updating Valuation document...")
        
        # Update the valuation document with enhanced fields
        valuation_filter = {
            "templateCategory": "valuation",
            "bankCode": "SBI"
        }
        
        enhanced_valuation_fields = update_valuation_fields()
        
        # Find and update Part A fields in valuation document  
        valuation_update = {
            "$set": {
                "sections.0.fields": enhanced_valuation_fields,
                "calculationConfig": {
                    "enabled": True,
                    "realTimeUpdates": True,
                    "showCalculationSteps": True,
                    "autoPopulateEnabled": True
                },
                "updatedAt": datetime.now(timezone.utc).isoformat()
            }
        }
        
        result = collection.update_one(valuation_filter, valuation_update)
        
        if result.modified_count > 0:
            print("✅ Valuation document updated successfully")
        else:
            print("⚠️  No valuation document found or no changes made")
            
        # Update the detailed valuation document 
        print("📝 Updating Detailed Valuation document...")
        
        detailed_valuation_filter = {
            "templateCategory": "detailed_valuation", 
            "bankCode": "SBI"
        }
        
        enhanced_land_field = update_detailed_valuation_fields()
        
        # Update the land_total field in the total section
        detailed_valuation_update = {
            "$set": {
                "sections.$[totalSection].fields.$[landField]": enhanced_land_field,
                "autoPopulationConfig": {
                    "enabled": True,
                    "showSourceReferences": True,
                    "allowOverrides": True
                },
                "updatedAt": datetime.now(timezone.utc).isoformat()
            }
        }
        
        array_filters = [
            {"totalSection.sectionId": "total"},
            {"landField.fieldId": "land_total"}
        ]
        
        result = collection.update_one(
            detailed_valuation_filter, 
            detailed_valuation_update,
            array_filters=array_filters
        )
        
        if result.modified_count > 0:
            print("✅ Detailed Valuation document updated successfully")
        else:
            print("⚠️  No detailed valuation document found or no changes made")
            
        # Verify the updates
        print("\n🔍 Verifying updates...")
        
        valuation_doc = collection.find_one(valuation_filter)
        if valuation_doc:
            print(f"✅ Found valuation document with {len(valuation_doc['sections'][0]['fields'])} fields")
            
            # Check if calculation field exists
            calc_field = next((f for f in valuation_doc['sections'][0]['fields'] 
                             if f['fieldId'] == 'estimated_land_value'), None)
            if calc_field and 'calculation' in calc_field:
                print("✅ Calculation configuration found")
                print(f"   Formula: {calc_field['calculation']['formula']}")
            else:
                print("❌ Calculation configuration missing")
        
        detailed_doc = collection.find_one(detailed_valuation_filter)
        if detailed_doc:
            total_section = next((s for s in detailed_doc['sections'] 
                                if s['sectionId'] == 'total'), None)
            if total_section:
                land_field = next((f for f in total_section['fields']
                                 if f['fieldId'] == 'land_total'), None)
                if land_field and 'autoPopulated' in land_field:
                    print("✅ Auto-population configuration found")
                    print(f"   Source: {land_field['autoPopulated']['sourceField']}")
                else:
                    print("❌ Auto-population configuration missing")
                    
        print("\n🎉 MongoDB collection update completed!")
        
    except Exception as e:
        print(f"❌ Error updating MongoDB collection: {str(e)}")
        return False
        
    finally:
        if 'client' in locals():
            client.close()
            
    return True

if __name__ == "__main__":
    import asyncio
    asyncio.run(update_mongodb_collection())