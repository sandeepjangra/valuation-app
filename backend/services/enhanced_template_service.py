"""
Enhanced template service with document_types collection integration
"""
from typing import List, Dict, Any, Optional
from pymongo.database import Database
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

class EnhancedTemplateService:
    """
    Enhanced template service that integrates document_types collection
    while maintaining backward compatibility with existing endpoints
    """
    
    def __init__(self, db: Database):
        self.db = db
        
    def get_document_types(self, property_type: str, bank_code: str) -> List[Dict[str, Any]]:
        """
        Fetch document types based on property type and bank code
        """
        try:
            # Build filter query
            filter_query = {
                "isActive": True,
                "$or": [
                    {"applicablePropertyTypes": property_type},
                    {"applicablePropertyTypes": "*"}
                ],
                "$and": [
                    {
                        "$or": [
                            {"applicableBanks": bank_code},
                            {"applicableBanks": "*"}
                        ]
                    }
                ]
            }
            
            # Fetch documents sorted by sortOrder
            documents = list(self.db.document_types.find(
                filter_query,
                {"_id": 0}  # Exclude MongoDB _id field
            ).sort("sortOrder", 1))
            
            # Convert to field format for compatibility
            fields = []
            for doc in documents:
                field = {
                    "fieldId": doc.get("documentId"),
                    "uiDisplayName": doc.get("uiDisplayName"),
                    "fieldType": doc.get("fieldType", "textarea"),
                    "placeholder": doc.get("placeholder", ""),
                    "isRequired": doc.get("isRequired", False),
                    "sortOrder": doc.get("sortOrder", 1),
                    "includeInCustomTemplate": doc.get("includeInCustomTemplate", True)
                }
                fields.append(field)
            
            return fields
            
        except Exception as e:
            logger.error(f"Error fetching document types: {e}")
            return []
    
    def merge_document_fields_into_template(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge document_types fields into template sections that use document collection
        """
        try:
            if 'documents' not in template:
                return template
            
            for document in template['documents']:
                if 'sections' not in document:
                    continue
                    
                for section in document['sections']:
                    # Check if this section uses document collection
                    if section.get('useDocumentCollection', False):
                        document_filter = section.get('documentFilter', {})
                        property_type = document_filter.get('propertyType', 'Land')
                        bank_code = document_filter.get('bankCode', '*')
                        
                        # Fetch document fields from collection
                        document_fields = self.get_document_types(property_type, bank_code)
                        
                        # Merge with existing fields (if any)
                        existing_fields = section.get('fields', [])
                        
                        # If we have originalFields (backup), use those for non-document fields
                        if 'originalFields' in section:
                            non_document_fields = [
                                field for field in section['originalFields'] 
                                if field.get('fieldId') not in [
                                    'agreement_to_sell', 'list_of_documents_produced',
                                    'allotment_letter', 'layout_plan', 'sales_deed',
                                    'title_deed', 'mortgage_deed', 'chain_of_documents',
                                    'property_card', 'mutation_records'
                                ]
                            ]
                            existing_fields.extend(non_document_fields)
                        
                        # Combine document fields with existing fields
                        all_fields = document_fields + existing_fields
                        
                        # Sort by sortOrder
                        all_fields.sort(key=lambda x: x.get('sortOrder', 999))
                        
                        # Update section fields
                        section['fields'] = all_fields
                        
                        logger.info(f"Merged {len(document_fields)} document fields into section {section.get('sectionId')}")
            
            return template
            
        except Exception as e:
            logger.error(f"Error merging document fields: {e}")
            return template
    
    def get_consolidated_templates(self, 
                                bank_code: str, 
                                property_type: str, 
                                organization_id: str = None) -> Dict[str, Any]:
        """
        Enhanced version of get_consolidated_templates that includes document_types integration
        Maintains backward compatibility with existing endpoint
        """
        try:
            # Get base templates using existing logic
            base_result = self._get_base_consolidated_templates(bank_code, property_type, organization_id)
            
            # Process each template to merge document fields
            if 'templates' in base_result:
                for template in base_result['templates']:
                    template = self.merge_document_fields_into_template(template)
            
            # Also process commonFieldGroups and bankSpecificTabs if they use documents
            if 'commonFieldGroups' in base_result:
                for group in base_result['commonFieldGroups']:
                    if 'sections' in group:
                        for section in group['sections']:
                            if section.get('useDocumentCollection', False):
                                # Apply same document merging logic
                                document_filter = section.get('documentFilter', {})
                                prop_type = document_filter.get('propertyType', property_type)
                                bank = document_filter.get('bankCode', bank_code)
                                
                                document_fields = self.get_document_types(prop_type, bank)
                                existing_fields = section.get('fields', [])
                                
                                all_fields = document_fields + existing_fields
                                all_fields.sort(key=lambda x: x.get('sortOrder', 999))
                                section['fields'] = all_fields
            
            # Same for bankSpecificTabs
            if 'bankSpecificTabs' in base_result:
                for tab in base_result['bankSpecificTabs']:
                    if 'sections' in tab:
                        for section in tab['sections']:
                            if section.get('useDocumentCollection', False):
                                document_filter = section.get('documentFilter', {})
                                prop_type = document_filter.get('propertyType', property_type)
                                bank = document_filter.get('bankCode', bank_code)
                                
                                document_fields = self.get_document_types(prop_type, bank)
                                existing_fields = section.get('fields', [])
                                
                                all_fields = document_fields + existing_fields
                                all_fields.sort(key=lambda x: x.get('sortOrder', 999))
                                section['fields'] = all_fields
            
            logger.info(f"Successfully enhanced consolidated templates for {bank_code}/{property_type}")
            return base_result
            
        except Exception as e:
            logger.error(f"Error getting enhanced consolidated templates: {e}")
            # Fallback to base templates if enhancement fails
            return self._get_base_consolidated_templates(bank_code, property_type, organization_id)
    
    def _get_base_consolidated_templates(self, 
                                       bank_code: str, 
                                       property_type: str, 
                                       organization_id: str = None) -> Dict[str, Any]:
        """
        Original consolidated templates logic - kept for backward compatibility
        This should contain your existing aggregation pipeline logic
        """
        # This is a placeholder - you should move your existing 
        # get_consolidated_templates logic here
        
        try:
            # Example structure - replace with your actual implementation
            collection_name = f"{bank_code.lower()}_{property_type.lower()}_property_details"
            collection = self.db[collection_name]
            
            # Your existing aggregation pipeline
            pipeline = [
                {"$match": {"isActive": True}},
                # Add your existing aggregation stages here
            ]
            
            result = list(collection.aggregate(pipeline))
            
            if result:
                return result[0]
            else:
                return {
                    "templates": [],
                    "commonFieldGroups": [],
                    "bankSpecificTabs": [],
                    "totalFieldCount": 0,
                    "allFields": []
                }
                
        except Exception as e:
            logger.error(f"Error in base consolidated templates: {e}")
            return {
                "templates": [],
                "commonFieldGroups": [],
                "bankSpecificTabs": [],
                "totalFieldCount": 0,
                "allFields": []
            }

# Usage example for integration with existing FastAPI endpoints
def integrate_with_existing_endpoint():
    """
    Example of how to integrate with existing endpoint
    """
    
    # In your existing FastAPI route handler:
    """
    @app.get("/api/templates/consolidated/{bank_code}/{property_type}")
    async def get_consolidated_templates(
        bank_code: str,
        property_type: str,
        organization_id: str = None
    ):
        try:
            # Use enhanced service instead of original
            template_service = EnhancedTemplateService(db)
            result = template_service.get_consolidated_templates(
                bank_code=bank_code,
                property_type=property_type,
                organization_id=organization_id
            )
            
            return {
                "success": True,
                "data": result
            }
            
        except Exception as e:
            logger.error(f"Error in consolidated templates endpoint: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    """
    pass