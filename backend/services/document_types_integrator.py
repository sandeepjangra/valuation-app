"""
Enhanced Template Service Integration with Unified Bank Structure
Maintains compatibility with your existing unified_endpoints.py approach
"""
import logging
from typing import Dict, List, Any, Optional
from fastapi import HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

class DocumentTypesIntegrator:
    """
    Lightweight integrator for document types with existing unified bank structure
    """
    
    @staticmethod
    async def get_document_fields(db, property_type: str = "Land", bank_code: str = "*") -> List[Dict[str, Any]]:
        """
        Fetch document types from collection and format as template fields
        """
        try:
            # Map template codes to document_types property types
            property_type_mapping = {
                "land-property": "Land",
                "land": "Land", 
                "apartment-property": "Apartment",
                "apartment": "Apartment",
                "house": "House"
            }
            
            # Map the property type
            mapped_property_type = property_type_mapping.get(property_type.lower(), property_type)
            logger.info(f"📄 Mapping property_type '{property_type}' → '{mapped_property_type}'")
            
            # Check if document_types collection exists
            collections = []
            try:
                # Use admin database type (which maps to valuation_admin database)
                collections = await db.get_all_collections("admin") 
                print(f"DEBUG: Found collections in admin db: {collections}")
            except Exception as e:
                print(f"DEBUG: Error getting collections: {e}")
                # Fallback: just try to query the collection directly
                try:
                    test_query = await db.find_one("admin", "document_types", {"isActive": True})
                    if test_query:
                        collections = ["document_types"]
                        print(f"DEBUG: Fallback - found document_types collection")
                except Exception as e2:
                    print(f"DEBUG: Fallback also failed: {e2}")
            
            if "document_types" not in collections:
                print(f"DEBUG: document_types not in collections: {collections}")
                logger.warning("document_types collection not found in admin database")
                return []
            else:
                print(f"DEBUG: document_types collection found!")
            
            # Build filter for document types
            filter_query = {
                "isActive": True,
                "$and": [
                    {
                        "$or": [
                            {"applicablePropertyTypes": {"$in": [mapped_property_type]}},
                            {"applicablePropertyTypes": {"$in": ["*"]}}
                        ]
                    },
                    {
                        "$or": [
                            {"applicableBanks": {"$in": [bank_code]}},
                            {"applicableBanks": {"$in": ["*"]}}
                        ]
                    }
                ]
            }
            
            # Fetch documents  
            documents = []
            print(f"DEBUG: Querying admin.document_types with filter: {filter_query}")
            logger.info(f"📄 Querying admin.document_types with filter: {filter_query}")
            try:
                print(f"DEBUG: About to call db.find_many...")
                # Use find_many instead of find since MultiDatabaseManager doesn't have find method
                documents_result = await db.find_many("admin", "document_types", filter_query)
                if documents_result:
                    documents = list(documents_result)
                    print(f"DEBUG: Completed db.find_many, total documents: {len(documents)}")
                    for doc in documents:
                        print(f"DEBUG: Found document: {doc.get('documentId')}")
                    logger.info(f"✅ Found {len(documents)} documents from db.find_many")
                else:
                    print(f"DEBUG: No documents returned from find_many")
                    logger.info(f"✅ No documents returned from db.find_many")
            except Exception as find_error:
                logger.error(f"❌ Error with db.find_many: {find_error}")
                print(f"DEBUG: Find_many error: {find_error}")
            
            # Sort by sortOrder
            documents.sort(key=lambda x: x.get("sortOrder", 999))
            
            # Convert to field format
            fields = []
            for doc in documents:
                field = {
                    "fieldId": doc.get("documentId"),
                    "uiDisplayName": doc.get("uiDisplayName", doc.get("documentId", "")),
                    "fieldType": doc.get("fieldType", "textarea"),
                    "placeholder": doc.get("placeholder", ""),
                    "isRequired": doc.get("isRequired", False),
                    "sortOrder": doc.get("sortOrder", 1),
                    "includeInCustomTemplate": doc.get("includeInCustomTemplate", True),
                    "source": "document_types_collection"  # Mark as coming from collection
                }
                fields.append(field)
            
            logger.info(f"✅ Fetched {len(fields)} document fields for {property_type}/{bank_code}")
            return fields
            
        except Exception as e:
            logger.error(f"❌ Error fetching document types: {e}")
            return []
    
    @staticmethod
    def merge_document_fields_into_sections(sections: List[Dict], document_fields: List[Dict]) -> List[Dict]:
        """
        Merge document fields into sections that are marked for document collection usage
        """
        try:
            for section in sections:
                # Check if section should use document collection
                if section.get("useDocumentCollection", False):
                    existing_fields = section.get("fields", [])
                    
                    # If section has been migrated (has originalFields and empty fields), 
                    # use only document collection fields
                    if "originalFields" in section and len(existing_fields) == 0:
                        # Section has been migrated - use only document collection fields
                        all_fields = document_fields.copy()
                        logger.info(f"Using document collection fields only for migrated section {section.get('sectionId', 'unknown')}")
                    else:
                        # Keep existing fields and add document fields
                        all_fields = document_fields + existing_fields
                        logger.info(f"Merging document fields with existing fields for section {section.get('sectionId', 'unknown')}")
                    
                    # Merge document fields with existing fields
                    
                    # Sort by sortOrder
                    all_fields.sort(key=lambda x: x.get("sortOrder", 999))
                    
                    # Update section
                    section["fields"] = all_fields
                    section["documentFieldCount"] = len(document_fields)
                    
                    logger.info(f"✅ Merged {len(document_fields)} document fields into section {section.get('sectionId', 'unknown')}")
            
            return sections
            
        except Exception as e:
            logger.error(f"❌ Error merging document fields: {e}")
            return sections

async def enhance_unified_template_with_documents(bank_code: str, template_data: Dict, db) -> Dict:
    """
    Enhance unified template data with document types collection fields
    Compatible with your existing unified structure
    """
    try:
        # Extract property type from template if available
        property_type = "Land"  # Default
        if "documents" in template_data:
            for doc in template_data["documents"]:
                if "sections" in doc:
                    for section in doc["sections"]:
                        if "documentFilter" in section:
                            property_type = section["documentFilter"].get("propertyType", "Land")
                            break
        
        # Get document fields
        document_fields = await DocumentTypesIntegrator.get_document_fields(
            db, property_type, bank_code
        )
        
        if not document_fields:
            logger.info("No document fields found, returning template as-is")
            return template_data
        
        # Enhance documents if they exist
        if "documents" in template_data:
            for document in template_data["documents"]:
                if "sections" in document:
                    document["sections"] = DocumentTypesIntegrator.merge_document_fields_into_sections(
                        document["sections"], document_fields
                    )
        
        # Enhance other structures if needed
        if "commonFieldGroups" in template_data:
            for group in template_data["commonFieldGroups"]:
                if "sections" in group:
                    group["sections"] = DocumentTypesIntegrator.merge_document_fields_into_sections(
                        group["sections"], document_fields
                    )
        
        if "bankSpecificTabs" in template_data:
            for tab in template_data["bankSpecificTabs"]:
                if "sections" in tab:
                    tab["sections"] = DocumentTypesIntegrator.merge_document_fields_into_sections(
                        tab["sections"], document_fields
                    )
        
        # Add metadata
        template_data["documentTypesEnhanced"] = True
        template_data["documentFieldsCount"] = len(document_fields)
        template_data["enhancedAt"] = datetime.now().isoformat()
        
        logger.info(f"✅ Enhanced template {template_data.get('templateId', 'unknown')} with {len(document_fields)} document fields")
        return template_data
        
    except Exception as e:
        logger.error(f"❌ Error enhancing template with document fields: {e}")
        return template_data

# Integration with your existing unified_endpoints.py
async def get_aggregated_template_fields_unified_enhanced(bank_code: str, template_id: str) -> JSONResponse:
    """
    Enhanced version of your unified endpoint that includes document types integration
    Drop-in replacement for your existing function
    """
    try:
        logger.info(f"🔄 Enhanced Unified Aggregation API call for template: {bank_code}/{template_id}")
        
        # Import your existing database connection
        from database.multi_db_manager import MultiDatabaseSession
        
        async with MultiDatabaseSession() as db:
            # Step 1: Get unified banks document (your existing logic)
            unified_banks = await db.find_one(
                "main", 
                "unified_banks", 
                {"_id": "unified_banks_v2"}
            )
            
            if not unified_banks:
                logger.error("❌ Unified banks collection not found")
                raise HTTPException(
                    status_code=500, 
                    detail="Banks collection not properly consolidated"
                )
            
            # Step 2: Find the specific bank (your existing logic)
            target_bank = None
            banks = unified_banks.get("banks", [])
            
            for bank in banks:
                if bank.get("bankCode", "").upper() == bank_code.upper():
                    target_bank = bank
                    break
            
            if not target_bank:
                raise HTTPException(status_code=404, detail=f"Bank {bank_code} not found")
            
            # Step 3: Find the specific template (your existing logic)
            target_template = None
            templates = target_bank.get("templates", [])
            
            for template in templates:
                if template.get("templateId") == template_id:
                    target_template = template
                    break
            
            if not target_template:
                raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
            
            # Step 4: NEW - Enhance template with document types
            enhanced_template = await enhance_unified_template_with_documents(
                bank_code, target_template, db
            )
            
            # Step 5: Return enhanced response (same format as before)
            success_response = JSONResponse(
                content={
                    "success": True,
                    "data": {
                        "templateId": template_id,
                        "bankCode": bank_code,
                        "template": enhanced_template,
                        "enhanced": True,
                        "documentTypesEnabled": True
                    },
                    "message": f"Template fields retrieved successfully with document types integration"
                },
                status_code=200
            )
            
            logger.info(f"✅ Enhanced template response for {bank_code}/{template_id}")
            return success_response
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in enhanced unified aggregation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

# Example of how to replace your existing endpoint
"""
In your main.py or wherever you have the endpoint:

# OLD:
@app.get("/api/templates/{bank_code}/{template_id}/aggregated-fields")
async def get_aggregated_template_fields(bank_code: str, template_id: str):
    return await get_aggregated_template_fields_unified(bank_code, template_id)

# NEW:
@app.get("/api/templates/{bank_code}/{template_id}/aggregated-fields")
async def get_aggregated_template_fields(bank_code: str, template_id: str):
    return await get_aggregated_template_fields_unified_enhanced(bank_code, template_id)
"""