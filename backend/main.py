from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
from utils.logger import RequestResponseLogger

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    # If python-dotenv is not installed, try to read .env manually
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Valuation App API", version="1.0.0")

# Initialize request/response logger
api_logger = RequestResponseLogger()

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

@app.get("/api/banks")
async def get_all_banks(request: Request):
    """Get all active banks"""
    # Log the request
    request_data = await api_logger.log_request(request)
    
    logger.info("🏦 Fetching all banks from unified document...")
    
    try:
        from database.multi_db_manager import MultiDatabaseManager
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        # Get the unified banks document
        banks_document = await db_manager.find_one(
            "admin",
            "banks", 
            {"_id": "all_banks_unified_v3"}
        )
        
        if not banks_document:
            logger.error("❌ Unified banks document not found")
            raise HTTPException(status_code=404, detail="Banks document not found")
        
        # Extract active banks from the unified document
        all_banks = banks_document.get("banks", [])
        active_banks = [bank for bank in all_banks if bank.get("isActive", True)]
        
        logger.info(f"✅ Found {len(active_banks)} active banks out of {len(all_banks)} total banks")
        
        await db_manager.disconnect()
        
        response = JSONResponse(
            status_code=200,
            content=json.loads(json.dumps(active_banks, default=json_serializer))
        )
        
        # Log the response
        api_logger.log_response(response, request_data)
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Error fetching banks: {str(e)}")
        error_response = JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "details": str(e)}
        )
        
        # Log the error response
        api_logger.log_response(error_response, request_data)
        
        return error_response

@app.get("/api/templates/{bank_code}/{template_id}/aggregated-fields")
async def get_aggregated_template_fields(bank_code: str, template_id: str, request: Request) -> JSONResponse:
    """Get template fields using multi-collection aggregation: common_form_fields + bank-specific template collection"""
    # Log the request
    request_data = await api_logger.log_request(request)
    
    try:
        logger.info(f"🔄 Multi-Collection Aggregation API call for template: {bank_code}/{template_id}")
        
        # Ensure environment variable is set before importing database modules
        if not os.getenv('MONGODB_URI'):
            raise HTTPException(status_code=500, detail="MongoDB connection not configured")
        
        from database.multi_db_manager import MultiDatabaseSession
        
        async with MultiDatabaseSession() as db:
            # Step 1: Find the bank and template configuration from unified document
            unified_doc = await db.find_one("admin", "banks", {"_id": {"$regex": "all_banks_unified"}})
            
            if not unified_doc:
                logger.warning(f"❌ Unified banks document not found")
                raise HTTPException(status_code=404, detail="Banks configuration not found")
            
            # Find the specific bank in the banks array
            bank_doc = None
            all_banks = unified_doc.get("banks", [])
            
            for bank in all_banks:
                if bank.get("bankCode", "").upper() == bank_code.upper():
                    bank_doc = bank
                    break
            
            if not bank_doc:
                logger.warning(f"❌ Bank not found: {bank_code}")
                raise HTTPException(status_code=404, detail=f"Bank {bank_code} not found")
            
            if not bank_doc.get("isActive", True):
                logger.warning(f"❌ Bank is inactive: {bank_code}")
                raise HTTPException(status_code=404, detail=f"Bank {bank_code} is inactive")
            
            # Step 2: Find the specific template within the bank
            target_template = None
            templates = bank_doc.get("templates", [])
            
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
                
            collection_ref = target_template.get("collectionRef")
            if not collection_ref:
                logger.error(f"❌ No collection reference found for template: {bank_code}/{template_id}")
                raise HTTPException(
                    status_code=500, 
                    detail="Template collection reference not configured"
                )
            
            logger.info(f"📋 Using collection: {collection_ref}")
            
            # Step 3: Get common form fields (all active fields)
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
                
            logger.info(f"📄 Found {len(common_fields)} common fields")
            
            # Step 4: Get bank-specific template fields from the collection
            template_collection_docs = await db.find_many("admin", collection_ref, {})
            
            if not template_collection_docs:
                logger.warning(f"❌ No template data found in collection: {collection_ref}")
                raise HTTPException(
                    status_code=404, 
                    detail=f"Template data not found for {bank_code}/{template_id}"
                )
            
            # Process bank-specific fields from collection documents
            bank_specific_tabs = []
            
            for doc in template_collection_docs:
                template_metadata = doc.get("templateMetadata", {})
                
                # Build tabs structure based on template metadata
                tabs_config = template_metadata.get("tabs", [])
                
                if not tabs_config:
                    # Fallback: create a single tab from document fields
                    doc_fields = doc.get("fields", [])
                    if doc_fields:
                        bank_specific_tabs.append({
                            "tabId": "property_details",
                            "tabName": "property_details",
                            "tabTitle": "Property Details",
                            "tabOrder": 1,
                            "hasSections": False,
                            "description": "Property valuation details",
                            "fields": doc_fields,
                            "sections": []
                        })
                    continue
                
                # Process each tab from metadata
                for tab_config in sorted(tabs_config, key=lambda x: x.get("sortOrder", 0)):
                    tab_id = tab_config.get("tabId", "default_tab")
                    
                    # Build tab structure
                    tab = {
                        "tabId": tab_id,
                        "tabName": tab_config.get("tabName", tab_id),
                        "tabTitle": tab_config.get("tabName", tab_id).replace("_", " ").title(),
                        "tabOrder": tab_config.get("sortOrder", 1),
                        "hasSections": tab_config.get("hasSections", False),
                        "description": tab_config.get("description", ""),
                        "fields": [],
                        "sections": []
                    }
                    
                    # Handle tabs with sections
                    if tab_config.get("hasSections"):
                        sections_config = tab_config.get("sections", [])
                        
                        for section_config in sorted(sections_config, key=lambda x: x.get("sortOrder", 0)):
                            section_id = section_config.get("sectionId")
                            
                            # Find the corresponding section in documents array
                            document_section = None
                            for document in doc.get("documents", []):
                                for doc_section in document.get("sections", []):
                                    if doc_section.get("sectionId") == section_id:
                                        document_section = doc_section
                                        break
                                if document_section:
                                    break
                            
                            if document_section:
                                section = {
                                    "sectionId": section_config.get("sectionId"),
                                    "sectionName": section_config.get("sectionName"),
                                    "sortOrder": section_config.get("sortOrder"),
                                    "description": section_config.get("description", ""),
                                    "fields": document_section.get("fields", [])
                                }
                                tab["sections"].append(section)
                                # Also add fields to tab level for backward compatibility
                                tab["fields"].extend(document_section.get("fields", []))
                    
                    # Handle tabs without sections (normal field structure)
                    else:
                        # Get fields directly from documents array
                        all_doc_fields = []
                        for document in doc.get("documents", []):
                            doc_fields = document.get("fields", [])
                            all_doc_fields.extend(doc_fields)
                        tab["fields"] = all_doc_fields
                    
                    bank_specific_tabs.append(tab)
            
            logger.info(f"🎯 Created {len(bank_specific_tabs)} bank-specific tabs")
            
            # Step 5: Build comprehensive response (matching expected frontend format)
            response_data = {
                "templateInfo": {
                    "templateId": target_template.get("templateId", ""),
                    "templateName": target_template.get("templateName", ""),
                    "templateCode": target_template.get("templateCode", ""),
                    "templateType": target_template.get("templateType", ""),
                    "propertyType": target_template.get("propertyType", ""),
                    "description": target_template.get("description", ""),
                    "version": target_template.get("version", "1.0"),
                    "bankCode": bank_doc.get("bankCode", ""),
                    "bankName": bank_doc.get("bankName", "")
                },
                "commonFields": common_fields,
                "bankSpecificTabs": bank_specific_tabs,
                "aggregatedAt": datetime.now(timezone.utc).isoformat(),
                "metadata": {
                    "architecture": "multi_collection",
                    "commonFieldsSource": "common_form_fields",
                    "bankSpecificSource": collection_ref,
                    "totalCommonFields": len(common_fields),
                    "totalBankTabs": len(bank_specific_tabs),
                    "source": "multi_collection_aggregation"
                }
            }
            
            total_bank_fields = sum(len(tab.get("fields", [])) for tab in bank_specific_tabs)
            logger.info(f"✅ Successfully aggregated {len(common_fields)} common + {total_bank_fields} bank-specific fields for {bank_code}/{template_id}")
            
            response = JSONResponse(
                content=json.loads(json.dumps(response_data, default=json_serializer))
            )
            
            # Log the response
            api_logger.log_response(response, request_data)
            
            return response
            
    except HTTPException as http_exc:
        error_response = JSONResponse(
            status_code=http_exc.status_code,
            content={"error": http_exc.detail}
        )
        api_logger.log_response(error_response, request_data)
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Error in multi-collection aggregation: {str(e)}")
        import traceback
        traceback.print_exc()
        error_response = JSONResponse(
            status_code=500,
            content={"error": f"Failed to aggregate template fields: {str(e)}"}
        )
        api_logger.log_response(error_response, request_data)
        raise HTTPException(status_code=500, detail=f"Failed to aggregate template fields: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
