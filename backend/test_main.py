from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any
from datetime import datetime, timezone
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Valuation App API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def json_serializer(obj):
    """JSON serializer for objects not serializable by default"""
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    return str(obj)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/api/templates/{bank_code}/{template_id}/aggregated-fields")
async def get_aggregated_template_fields(bank_code: str, template_id: str) -> JSONResponse:
    """Get template fields using consolidated single document structure"""
    try:
        logger.info(f"🔄 Consolidated Aggregation API call for template: {bank_code}/{template_id}")
        
        # Import here to avoid circular imports
        from database.multi_db_manager import MultiDatabaseSession
        
        async with MultiDatabaseSession() as db:
            # Step 1: Get the single unified banks document
            unified_banks_doc = await db.find_one(
                "admin", 
                "banks", 
                {"_id": "all_banks_unified"}
            )
            
            if not unified_banks_doc:
                logger.error("❌ Unified banks document not found - consolidation may not have been run")
                raise HTTPException(
                    status_code=500, 
                    detail="Banks collection not properly consolidated. Please run consolidation first."
                )
            
            # Step 2: Find the specific bank within the unified document
            target_bank = None
            banks = unified_banks_doc.get("banks", [])
            
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
            
            # Step 3: Find the specific template within the target bank
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
            
            # Step 4: Get common form fields
            common_fields_docs = await db.find_many(
                "admin",
                "common_form_fields",
                {"isActive": True}
            )
            
            # Process common fields
            common_fields = []
            for doc in common_fields_docs:
                doc_fields = doc.get("fields", [])
                common_fields.extend(doc_fields)
            
            # Step 5: Process the template fields (simple field names)
            template_fields = target_template.get("fields", [])
            
            # Step 6: Create sections based on field categories
            sections = []
            for i, field_category in enumerate(template_fields):
                section = {
                    "sectionName": field_category,
                    "sectionTitle": field_category.replace("_", " ").title(),
                    "sectionOrder": i + 1,
                    "description": f"Section for {field_category.replace('_', ' ')}",
                    "fields": [
                        {
                            "fieldId": f"{field_category}_field",
                            "fieldName": field_category,
                            "fieldDisplayName": field_category.replace("_", " ").title(),
                            "fieldType": "text",
                            "isRequired": True,
                            "sortOrder": 1,
                            "validation": {
                                "minLength": 1,
                                "maxLength": 1000
                            }
                        }
                    ]
                }
                sections.append(section)
            
            # Step 7: Create bank-specific tabs structure (frontend expects this format)
            bank_specific_tabs = [
                {
                    "tabName": "property_details",
                    "tabTitle": "Property Details", 
                    "tabOrder": 1,
                    "sections": sections,
                    "fields": []  # For backward compatibility
                }
            ]
            
            # Step 8: Build comprehensive response (matching expected frontend format)
            response_data = {
                "templateInfo": {
                    "templateId": target_template.get("templateId", ""),
                    "templateName": target_template.get("templateName", ""),
                    "templateCode": target_template.get("templateCode", ""),
                    "templateType": target_template.get("templateType", ""),
                    "propertyType": target_template.get("propertyType", ""),
                    "description": target_template.get("description", ""),
                    "version": target_template.get("version", "1.0"),
                    "bankCode": target_bank.get("bankCode", ""),
                    "bankName": target_bank.get("bankName", "")
                },
                "commonFields": common_fields,
                "bankSpecificTabs": bank_specific_tabs,
                "aggregatedAt": datetime.now(timezone.utc).isoformat(),
                "metadata": {
                    "architecture": "single_document",
                    "consolidationVersion": unified_banks_doc.get("version", "3.0"),
                    "totalSections": len(sections),
                    "totalFields": len(template_fields),
                    "source": "unified_single_document"
                }
            }
            
            logger.info(f"✅ Successfully aggregated {len(template_fields)} fields for {bank_code}/{template_id}")
            
            return JSONResponse(
                content=json.loads(json.dumps(response_data, default=json_serializer))
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in consolidated aggregation: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to aggregate template fields: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
