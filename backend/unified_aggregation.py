"""
Updated Backend Aggregation Logic for Unified Bank Collections

This module contains the updated aggregation endpoint that works with
the consolidated bank structure instead of separate collections.
"""

from typing import Dict, List, Any, Optional
from bson import ObjectId
from database.mongodb import MultiDatabaseSession

async def get_aggregated_template_fields_unified(
    bank_name: str, 
    template_id: str, 
    session: MultiDatabaseSession
) -> Dict[str, Any]:
    """
    Updated aggregation function that works with unified bank collections.
    
    This replaces the complex multi-collection logic with simplified unified queries.
    """
    
    try:
        # Step 1: Get bank configuration from unified_banks collection
        unified_banks = session.databases['valuation_system']['unified_banks']
        bank_config = await unified_banks.find_one({"_id": "unified_banks_v3"})
        
        if not bank_config:
            raise ValueError("Unified banks configuration not found")
        
        # Find specific bank
        target_bank = None
        for bank in bank_config.get("banks", []):
            if bank.get("bankName") == bank_name:
                target_bank = bank
                break
        
        if not target_bank:
            raise ValueError(f"Bank '{bank_name}' not found in unified configuration")
        
        bank_code = target_bank.get("bankCode", bank_name.upper()[:3])
        
        # Find specific template
        target_template = None
        for template in target_bank.get("templates", []):
            if template.get("templateId") == template_id:
                target_template = template
                break
        
        if not target_template:
            raise ValueError(f"Template '{template_id}' not found for bank '{bank_name}'")
        
        # Step 2: Get common fields (unchanged)
        common_collection = session.databases['valuation_system']['common_form_fields']
        common_pipeline = [
            {"$match": {"isActive": True}},
            {"$sort": {"sortOrder": 1, "fieldName": 1}},
            {"$group": {
                "_id": "$tabName",
                "sections": {
                    "$push": {
                        "_id": "$_id",
                        "fieldName": "$fieldName",
                        "fieldType": "$fieldType",
                        "fieldDisplayName": "$fieldDisplayName",
                        "isRequired": "$isRequired",
                        "sectionName": "$sectionName",
                        "sortOrder": "$sortOrder",
                        "options": "$options",
                        "validation": "$validation"
                    }
                }
            }}
        ]
        
        common_fields = {}
        async for doc in common_collection.aggregate(common_pipeline):
            tab_name = doc["_id"]
            
            # Group by sections
            sections = {}
            for field in doc["sections"]:
                section_name = field.get("sectionName", "default")
                if section_name not in sections:
                    sections[section_name] = []
                sections[section_name].append(field)
            
            common_fields[tab_name] = sections
        
        # Step 3: Get bank-specific fields from unified collection
        bank_specific_fields = {}
        
        # Get filter criteria from template configuration
        fields_config = target_template.get("fields", {})
        bank_specific_config = fields_config.get("bankSpecificFields", {})
        filter_criteria = bank_specific_config.get("filter", {})
        
        # Default filter criteria if not specified
        if not filter_criteria:
            filter_criteria = {
                "bankCode": bank_code,
                "propertyType": target_template.get("propertyType", "land"),
                "isActive": True
            }
        
        # Query unified bank templates collection
        unified_templates = session.databases['valuation_system']['unified_bank_templates']
        
        bank_pipeline = [
            {"$match": filter_criteria},
            {"$sort": {"sortOrder": 1, "fieldName": 1}},
            {"$group": {
                "_id": {
                    "tabName": "$templateMetadata.tabName",
                    "sectionName": "$templateMetadata.sectionName"
                },
                "fields": {
                    "$push": {
                        "_id": "$_id",
                        "fieldName": "$fieldName", 
                        "fieldType": "$fieldType",
                        "fieldDisplayName": "$fieldDisplayName",
                        "isRequired": "$isRequired",
                        "sortOrder": "$sortOrder",
                        "options": "$options",
                        "validation": "$validation",
                        "templateMetadata": "$templateMetadata"
                    }
                }
            }}
        ]
        
        async for doc in unified_templates.aggregate(bank_pipeline):
            tab_name = doc["_id"]["tabName"]
            section_name = doc["_id"]["sectionName"]
            
            if tab_name not in bank_specific_fields:
                bank_specific_fields[tab_name] = {}
                
            if section_name not in bank_specific_fields[tab_name]:
                bank_specific_fields[tab_name][section_name] = []
                
            bank_specific_fields[tab_name][section_name].extend(doc["fields"])
        
        # Step 4: Merge common and bank-specific fields
        merged_fields = {}
        
        # Start with common fields
        for tab_name, sections in common_fields.items():
            merged_fields[tab_name] = {}
            for section_name, fields in sections.items():
                merged_fields[tab_name][section_name] = fields.copy()
        
        # Add bank-specific fields
        for tab_name, sections in bank_specific_fields.items():
            if tab_name not in merged_fields:
                merged_fields[tab_name] = {}
                
            for section_name, fields in sections.items():
                if section_name not in merged_fields[tab_name]:
                    merged_fields[tab_name][section_name] = []
                    
                merged_fields[tab_name][section_name].extend(fields)
        
        # Step 5: Sort all fields by sortOrder
        for tab_name in merged_fields:
            for section_name in merged_fields[tab_name]:
                merged_fields[tab_name][section_name].sort(
                    key=lambda x: x.get("sortOrder", 999)
                )
        
        # Step 6: Build response structure
        response = {
            "bankInfo": {
                "bankName": target_bank.get("bankName"),
                "bankCode": bank_code,
                "bankType": target_bank.get("bankType"),
                "headquarters": target_bank.get("headquarters", {}),
                "branches": target_bank.get("branches", [])
            },
            "templateInfo": {
                "templateId": target_template.get("templateId"),
                "templateCode": target_template.get("templateCode"),
                "propertyType": target_template.get("propertyType"),
                "version": target_template.get("version", "3.0")
            },
            "fieldsStructure": merged_fields,
            "metadata": {
                "totalTabs": len(merged_fields),
                "totalSections": sum(len(sections) for sections in merged_fields.values()),
                "totalFields": sum(
                    len(fields) 
                    for sections in merged_fields.values() 
                    for fields in sections.values()
                ),
                "architecture": "unified_reference_based",
                "generatedAt": "datetime.utcnow().isoformat()",
                "collections": {
                    "common": "common_form_fields",
                    "bankSpecific": "unified_bank_templates",
                    "bankConfig": "unified_banks"
                }
            }
        }
        
        return response
        
    except Exception as e:
        raise Exception(f"Error in unified aggregation: {str(e)}")


# Updated endpoint in main.py
@app.get("/api/templates/{bank_name}/{template_id}/aggregated-fields")
async def get_template_aggregated_fields_unified(bank_name: str, template_id: str):
    """
    Updated API endpoint that uses unified bank collections.
    
    This replaces the complex original aggregation with simplified unified logic.
    """
    try:
        # Use unified aggregation function
        session = MultiDatabaseSession()
        await session.initialize()
        
        result = await get_aggregated_template_fields_unified(
            bank_name=bank_name,
            template_id=template_id,
            session=session
        )
        
        await session.close()
        
        return {
            "success": True,
            "message": "Template fields aggregated successfully using unified collections",
            "data": result
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to aggregate template fields: {str(e)}",
            "data": None
        }


# Performance comparison function
async def compare_aggregation_performance(bank_name: str, template_id: str):
    """
    Compare performance between old and new aggregation methods.
    """
    import time
    
    session = MultiDatabaseSession()
    await session.initialize()
    
    # Test new unified method
    start_time = time.time()
    try:
        new_result = await get_aggregated_template_fields_unified(
            bank_name, template_id, session
        )
        new_time = time.time() - start_time
        new_success = True
    except Exception as e:
        new_time = time.time() - start_time
        new_success = False
        new_error = str(e)
    
    # Test old method (if available)
    start_time = time.time()
    try:
        # old_result = await get_aggregated_template_fields_original(...)  # Original function
        old_time = 0  # Placeholder
        old_success = True
    except:
        old_time = 0
        old_success = False
    
    await session.close()
    
    return {
        "performance": {
            "unified_method": {
                "execution_time": new_time,
                "success": new_success,
                "field_count": new_result.get("metadata", {}).get("totalFields", 0) if new_success else 0
            },
            "original_method": {
                "execution_time": old_time,
                "success": old_success,
                "field_count": 0  # Would need original result
            },
            "improvement": {
                "time_saved": old_time - new_time if old_time > 0 else 0,
                "percentage": ((old_time - new_time) / old_time * 100) if old_time > 0 else 0
            }
        }
    }