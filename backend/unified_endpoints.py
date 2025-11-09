"""
Updated Backend Endpoint for Unified Bank Structure

This module contains the updated endpoint that works with the consolidated
unified_banks collection instead of separate bank documents.
"""

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

async def get_aggregated_template_fields_unified(bank_code: str, template_id: str) -> JSONResponse:
    """
    Updated endpoint that works with unified bank collection structure.
    
    This replaces the original complex aggregation with simplified unified queries.
    """
    try:
        logger.info(f"🔄 Unified Aggregation API call for template: {bank_code}/{template_id}")
        
        async with MultiDatabaseSession() as db:
            # Step 1: Get unified banks document
            unified_banks = await db.find_one(
                "main", 
                "unified_banks", 
                {"_id": "unified_banks_v2"}
            )
            
            if not unified_banks:
                logger.error("❌ Unified banks collection not found - consolidation may not have been run")
                raise HTTPException(
                    status_code=500, 
                    detail="Banks collection not properly consolidated. Please run consolidation first."
                )
            
            # Step 2: Find the specific bank
            target_bank = None
            banks = unified_banks.get("banks", [])
            
            for bank in banks:
                if bank.get("bankCode", "").upper() == bank_code.upper():
                    target_bank = bank
                    break
            
            if not target_bank:
                logger.warning(f"❌ Bank not found: {bank_code}")
                raise HTTPException(status_code=404, detail=f"Bank {bank_code} not found")
            
            if not target_bank.get("isActive", True):
                logger.warning(f"❌ Bank is inactive: {bank_code}")
                raise HTTPException(status_code=404, detail=f"Bank {bank_code} is inactive")
            
            # Step 3: Find the specific template
            target_template = None
            templates = target_bank.get("templates", [])
            
            for template in templates:
                if (template.get("templateCode", "").upper() == template_id.upper() or 
                    template.get("templateId", "").upper() == template_id.upper()):
                    target_template = template
                    break
            
            if not target_template:
                logger.warning(f"❌ Template not found: {template_id} for bank {bank_code}")
                raise HTTPException(
                    status_code=404, 
                    detail=f"Template {template_id} not found for bank {bank_code}"
                )
            
            # Step 4: Get common form fields (these remain the same)
            common_fields_docs = await db.find_many(
                "main",
                "common_form_fields",
                {"isActive": True}
            )
            
            # Step 5: Process the template fields (simple field names)
            template_fields = target_template.get("fields", [])
            
            # Step 6: Build the response structure
            # For now, we'll return the field names and let the frontend handle the form structure
            # This matches the current simple structure where fields are just category names
            
            fields_structure = {
                "sections": []
            }
            
            # Create sections based on field categories
            for i, field_category in enumerate(template_fields):
                section = {
                    "sectionId": f"section_{i+1}",
                    "sectionName": field_category.replace("_", " ").title(),
                    "sectionOrder": i + 1,
                    "fields": [
                        {
                            "fieldId": f"{field_category}_field",
                            "fieldName": field_category,
                            "fieldDisplayName": field_category.replace("_", " ").title(),
                            "fieldType": "text",  # Default to text, can be enhanced later
                            "isRequired": True,
                            "sortOrder": 1,
                            "validation": {
                                "minLength": 1,
                                "maxLength": 1000
                            }
                        }
                    ]
                }
                fields_structure["sections"].append(section)
            
            # Step 7: Build comprehensive response
            response_data = {
                "bankInfo": {
                    "bankCode": target_bank.get("bankCode", ""),
                    "bankName": target_bank.get("bankName", ""),
                    "bankShortName": target_bank.get("bankShortName", ""),
                    "bankType": target_bank.get("bankType", ""),
                    "headquarters": target_bank.get("headquarters", {}),
                    "totalBranches": target_bank.get("totalBranches", 0)
                },
                "templateInfo": {
                    "templateId": target_template.get("templateId", ""),
                    "templateCode": target_template.get("templateCode", ""),
                    "templateName": target_template.get("templateName", ""),
                    "templateType": target_template.get("templateType", ""),
                    "propertyType": target_template.get("propertyType", ""),
                    "description": target_template.get("description", ""),
                    "version": target_template.get("version", "1.0")
                },
                "fieldsStructure": fields_structure,
                "metadata": {
                    "architecture": "unified_simple",
                    "consolidationVersion": unified_banks.get("version", "2.0"),
                    "totalSections": len(fields_structure["sections"]),
                    "totalFields": len(template_fields),
                    "generatedAt": "2025-11-09T15:22:00Z",
                    "source": "unified_banks_collection"
                }
            }
            
            logger.info(f"✅ Successfully aggregated {len(template_fields)} fields for {bank_code}/{template_id}")
            
            return JSONResponse(
                content={
                    "success": True,
                    "message": f"Template fields aggregated successfully using unified structure",
                    "data": response_data
                },
                status_code=200
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in unified aggregation: {str(e)}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Failed to aggregate template fields: {str(e)}",
                "data": None
            },
            status_code=500
        )


async def list_available_banks_unified() -> JSONResponse:
    """
    Get list of all available banks from unified collection.
    """
    try:
        async with MultiDatabaseSession() as db:
            unified_banks = await db.find_one(
                "main", 
                "unified_banks", 
                {"_id": "unified_banks_v2"}
            )
            
            if not unified_banks:
                return JSONResponse(
                    content={
                        "success": False,
                        "message": "Unified banks collection not found",
                        "data": []
                    },
                    status_code=500
                )
            
            banks_list = []
            for bank in unified_banks.get("banks", []):
                if bank.get("isActive", True):
                    bank_info = {
                        "bankCode": bank.get("bankCode", ""),
                        "bankName": bank.get("bankName", ""),
                        "bankShortName": bank.get("bankShortName", ""),
                        "bankType": bank.get("bankType", ""),
                        "templateCount": len(bank.get("templates", [])),
                        "templates": [
                            {
                                "templateId": template.get("templateId", ""),
                                "templateCode": template.get("templateCode", ""),
                                "templateName": template.get("templateName", ""),
                                "propertyType": template.get("propertyType", ""),
                                "fieldCount": len(template.get("fields", []))
                            }
                            for template in bank.get("templates", [])
                        ]
                    }
                    banks_list.append(bank_info)
            
            return JSONResponse(
                content={
                    "success": True,
                    "message": f"Found {len(banks_list)} active banks",
                    "data": {
                        "banks": banks_list,
                        "statistics": unified_banks.get("statistics", {}),
                        "consolidationInfo": unified_banks.get("consolidationInfo", {})
                    }
                },
                status_code=200
            )
            
    except Exception as e:
        logger.error(f"❌ Error listing banks: {str(e)}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Failed to list banks: {str(e)}",
                "data": []
            },
            status_code=500
        )


# Add these routes to main.py:
"""
# Replace the existing endpoint in main.py with:

@app.get("/api/templates/{bank_code}/{template_id}/aggregated-fields")
async def get_template_aggregated_fields(bank_code: str, template_id: str):
    return await get_aggregated_template_fields_unified(bank_code, template_id)

@app.get("/api/banks")
async def list_banks():
    return await list_available_banks_unified()
"""