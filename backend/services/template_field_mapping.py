"""
Template Field Mapping Service

This service provides functionality to map form fields to their correct template tabs
based on the existing MongoDB template structure in valuation_admin database.
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple, Set
from database.multi_db_manager import MultiDatabaseManager

class TemplateFieldMappingService:
    def __init__(self):
        self.db_manager = MultiDatabaseManager()
        self._template_cache: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self):
        """Connect to MongoDB"""
        await self.db_manager.connect()
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        await self.db_manager.disconnect()
    
    async def get_template_structure(self, bank_code: str, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Get template structure from MongoDB admin database
        
        Args:
            bank_code: Bank code (e.g., "SBI")
            template_id: Template ID (e.g., "land-property")
            
        Returns:
            Template structure with tabs and field mapping
        """
        cache_key = f"{bank_code}_{template_id}"
        
        # Check cache first
        if cache_key in self._template_cache:
            return self._template_cache[cache_key]
        
        try:
            admin_db = self.db_manager.get_database("admin")
            
            # Try multiple approaches to find the template
            collection_ref = None
            template_name = None
            
            # Approach 1: Find via unified document
            unified_doc = await admin_db.banks.find_one({"_id": "all_banks_comprehensive_v4"})
            
            if unified_doc:
                # Find the specific bank
                bank_doc = None
                all_banks = unified_doc.get("banks", [])
                
                for bank in all_banks:
                    if bank.get("bankCode", "").upper() == bank_code.upper():
                        bank_doc = bank
                        break
                
                if bank_doc:
                    # Find the specific template
                    templates = bank_doc.get("templates", [])
                    for template in templates:
                        if (template.get("templateCode", "").upper() == template_id.upper() or 
                            template.get("templateId", "").upper() == template_id.upper()):
                            collection_ref = template.get("collectionRef")
                            template_name = template.get("templateName", "")
                            break
            
            # Approach 2: Find via banks collection
            if not collection_ref:
                banks_collection = admin_db["banks"]
                bank_doc = await banks_collection.find_one(
                    {"bankCode": {"$regex": f"^{bank_code}$", "$options": "i"}}
                )
                
                if bank_doc:
                    templates = bank_doc.get("templates", [])
                    for template in templates:
                        if (template.get("templateCode", "").upper() == template_id.upper() or 
                            template.get("templateId", "").upper() == template_id.upper()):
                            collection_ref = template.get("collectionRef")
                            template_name = template.get("templateName", "")
                            break
            
            # Approach 3: Direct collection lookup by naming convention
            if not collection_ref:
                # Try common template collection naming patterns
                possible_collections = [
                    f"{bank_code.lower()}_land_property_details",
                    f"{bank_code.lower()}_apartment_property_details",
                    f"{bank_code.lower()}_{template_id.lower()}_details",
                    f"{bank_code.lower()}_{template_id.lower()}"
                ]
                
                collections = await admin_db.list_collection_names()
                for possible_collection in possible_collections:
                    if possible_collection in collections:
                        collection_ref = possible_collection
                        template_name = f"{bank_code} {template_id.title()} Template"
                        print(f"🔍 Found template in direct collection: {collection_ref}")
                        break
            
            if not collection_ref:
                print(f"❌ Template not found: {template_id} for bank {bank_code}")
                return None
            
            # Get template structure from collection
            template_collection = admin_db[collection_ref]
            template_docs = await template_collection.find({}).to_list(length=None)
            
            if not template_docs:
                print(f"❌ No template data found in collection: {collection_ref}")
                return None
            
            # Build template structure
            template_structure = {
                "bank_code": bank_code,
                "template_id": template_id,
                "collection_ref": collection_ref,
                "tabs": {},
                "field_to_tab_mapping": {},
                "tab_order": []
            }
            
            # Process each document to build tab structure
            for doc in template_docs:
                template_metadata = doc.get("templateMetadata", {})
                tabs_config = template_metadata.get("tabs", [])
                
                if not tabs_config:
                    # Handle documents without tab metadata
                    continue
                
                # Process tabs
                for tab_config in sorted(tabs_config, key=lambda x: x.get("sortOrder", 0)):
                    tab_id = tab_config.get("tabId", "")
                    tab_name = tab_config.get("tabName", "")
                    
                    if not tab_id:
                        continue
                    
                    # Initialize tab structure
                    if tab_id not in template_structure["tabs"]:
                        template_structure["tabs"][tab_id] = {
                            "tab_id": tab_id,
                            "tab_name": tab_name,
                            "sort_order": tab_config.get("sortOrder", 0),
                            "fields": [],
                            "sections": {}
                        }
                        template_structure["tab_order"].append(tab_id)
                    
                    # Get fields from documents array (actual field data)
                    doc_fields = []
                    
                    # Look for matching document in the documents array
                    if "documents" in template_docs[0]:  # Assuming first doc has documents array
                        documents = template_docs[0]["documents"]
                        matching_doc = None
                        
                        # Try multiple matching strategies
                        for document in documents:
                                doc_id = document.get("documentId", "")
                                # Strategy 1: Exact match
                                if doc_id == tab_id:
                                    matching_doc = document
                                    break
                                # Strategy 2: Remove "_details" suffix  
                                elif doc_id.replace("_details", "") == tab_id:
                                    matching_doc = document
                                    break
                                # Strategy 3: Add "_details" suffix to tab_id
                                elif doc_id == f"{tab_id}_details":
                                    matching_doc = document
                                    break
                                # Strategy 4: Partial match for similar names
                                elif (tab_id in doc_id or doc_id.split("_")[0] == tab_id.split("_")[0]):
                                    matching_doc = document
                                    break
                        
                        if matching_doc:
                            # Extract fields from sections or direct fields
                            if "sections" in matching_doc:
                                sections = matching_doc["sections"]
                                for section in sections:
                                    section_id = section.get("sectionId", "")
                                    section_name = section.get("sectionName", "")
                                    section_fields = section.get("fields", [])
                                    
                                    if section_id:
                                        template_structure["tabs"][tab_id]["sections"][section_id] = {
                                            "section_id": section_id,
                                            "section_name": section_name,
                                            "sort_order": section.get("sortOrder", 0),
                                            "fields": section_fields
                                        }
                                    
                                    doc_fields.extend(section_fields)
                            elif "fields" in matching_doc:
                                # Direct fields without sections
                                doc_fields = matching_doc["fields"]
                    
                    # Store fields in tab structure  
                    template_structure["tabs"][tab_id]["fields"] = doc_fields
                    
                    # Add fields to field_to_tab_mapping
                    for field in doc_fields:
                        field_id = field.get("fieldId", "")
                        if field_id:
                            template_structure["field_to_tab_mapping"][field_id] = tab_id
                
                # Also process documents that might not have matching tabs in templateMetadata
                if "documents" in template_docs[0]:
                    documents = template_docs[0]["documents"]
                    processed_doc_ids = set()
                    
                    # Collect doc IDs we've already processed
                    for tab_id in template_structure["tabs"]:
                        for document in documents:
                            doc_id = document.get("documentId", "")
                            if (doc_id == tab_id or 
                                doc_id.replace("_details", "") == tab_id or
                                doc_id == f"{tab_id}_details" or
                                (tab_id in doc_id or (doc_id.split("_")[0] == tab_id.split("_")[0] and len(doc_id.split("_")) > 1))):
                                processed_doc_ids.add(doc_id)
                    
                    # Process remaining unmatched documents
                    for document in documents:
                        doc_id = document.get("documentId", "")
                        if doc_id not in processed_doc_ids:
                            doc_name = document.get("documentName", doc_id)
                            
                            # Create a new tab for this document
                            template_structure["tabs"][doc_id] = {
                                "tab_id": doc_id,
                                "tab_name": doc_name,
                                "sort_order": len(template_structure["tabs"]) + 1,
                                "sections": {},
                                "fields": []
                            }
                            template_structure["tab_order"].append(doc_id)
                            
                            # Extract fields from this document
                            doc_fields = []
                            if "sections" in document:
                                sections = document["sections"]
                                for section in sections:
                                    section_id = section.get("sectionId", "")
                                    section_name = section.get("sectionName", "")
                                    section_fields = section.get("fields", [])
                                    
                                    if section_id:
                                        template_structure["tabs"][doc_id]["sections"][section_id] = {
                                            "section_id": section_id,
                                            "section_name": section_name,
                                            "sort_order": section.get("sortOrder", 0),
                                            "fields": section_fields
                                        }
                                    
                                    doc_fields.extend(section_fields)
                            elif "fields" in document:
                                # Direct fields without sections
                                doc_fields = document["fields"]
                            
                            # Store fields and create mappings
                            template_structure["tabs"][doc_id]["fields"] = doc_fields
                            for field in doc_fields:
                                field_id = field.get("fieldId", "")
                                if field_id:
                                    template_structure["field_to_tab_mapping"][field_id] = doc_id
            
            # Sort tabs by order
            template_structure["tab_order"] = sorted(
                template_structure["tab_order"],
                key=lambda tab_id: template_structure["tabs"][tab_id]["sort_order"]
            )
            
            # Cache the result
            self._template_cache[cache_key] = template_structure
            
            print(f"✅ Template structure loaded for {bank_code}/{template_id}")
            print(f"   Tabs: {len(template_structure['tabs'])}")
            print(f"   Fields mapped: {len(template_structure['field_to_tab_mapping'])}")
            
            return template_structure
            
        except Exception as e:
            print(f"❌ Error loading template structure: {e}")
            return None
    
    def get_field_tab_mapping(self, template_structure: Dict[str, Any]) -> Dict[str, str]:
        """
        Get field to tab mapping from template structure
        
        Args:
            template_structure: Template structure from get_template_structure
            
        Returns:
            Dictionary mapping field_id to tab_id
        """
        return template_structure.get("field_to_tab_mapping", {})
    
    async def organize_form_data_by_tabs(
        self, 
        flat_form_data: Dict[str, Any], 
        bank_code: str, 
        template_id: str
    ) -> Dict[str, Any]:
        """
        Organize flat form data into tab-based nested structure
        
        Structure:
        {
            "common_field1": "value1",     # Common fields at root level
            "common_field2": "value2",
            "tab1": {                      # Tab-specific fields nested
                "field1": "value1",
                "field2": "value2"
            },
            "tab2": {
                "field3": "value3",
                "field4": "value4"
            }
        }
        
        Args:
            flat_form_data: Flat form data from frontend
            bank_code: Bank code
            template_id: Template ID
            
        Returns:
            Nested form data organized by tabs
        """
        try:
            # Get template structure
            template_structure = await self.get_template_structure(bank_code, template_id)
            
            if not template_structure:
                print(f"⚠️ Could not load template structure, keeping flat structure")
                return flat_form_data

            # Get field mappings
            field_to_tab = self.get_field_tab_mapping(template_structure)
            organized_data = {}
            
            # Initialize all tabs as empty dictionaries
            for tab_id in template_structure["tab_order"]:
                organized_data[tab_id] = {}
            
            # Get common fields from admin database
            common_field_ids = await self.get_common_field_ids()
            
            # Organize fields: common fields at root, tab fields nested
            common_count = 0
            tab_count = 0
            
            for field_id, field_value in flat_form_data.items():
                tab_id = field_to_tab.get(field_id)
                
                if field_id in common_field_ids:
                    # Common field - keep at root level
                    organized_data[field_id] = field_value
                    common_count += 1
                elif tab_id and tab_id in organized_data:
                    # Tab-specific field - nest under tab
                    organized_data[tab_id][field_id] = field_value
                    tab_count += 1
                else:
                    # Unmatched field - treat as common field for now
                    organized_data[field_id] = field_value
                    common_count += 1

            # Remove empty tabs
            tabs_to_remove = []
            for tab_id in template_structure["tab_order"]:
                if not organized_data.get(tab_id):
                    tabs_to_remove.append(tab_id)
            
            for tab_id in tabs_to_remove:
                del organized_data[tab_id]

            print(f"✅ Organized {len(flat_form_data)} fields: {common_count} common + {tab_count} tab-specific")
            
            return organized_data
            
        except Exception as e:
            print(f"❌ Error organizing form data: {e}")
            return flat_form_data

    async def get_common_field_ids(self) -> Set[str]:
        """Get set of common field IDs from admin database"""
        try:
            admin_db = self.db_manager.get_database("admin")
            
            # Get all common form fields
            common_fields_docs = await admin_db["common_form_fields"].find(
                {"isActive": True}
            ).to_list(length=None)
            
            common_field_ids = set()
            for doc in common_fields_docs:
                fields = doc.get("fields", [])
                for field in fields:
                    field_id = field.get("fieldId")
                    if field_id:
                        common_field_ids.add(field_id)
            
            print(f"📋 Found {len(common_field_ids)} common field IDs")
            return common_field_ids
            
        except Exception as e:
            print(f"❌ Error loading common field IDs: {e}")
            return set()
    
    async def extract_form_data_from_tabs(
        self, 
        nested_data: Dict[str, Any], 
        bank_code: str, 
        template_id: str
    ) -> Dict[str, Any]:
        """
        Extract form data from tab-based nested structure to flat structure
        for loading into frontend forms
        
        Args:
            nested_data: Nested data organized by tabs
            bank_code: Bank code
            template_id: Template ID
            
        Returns:
            Flat form data for frontend
        """
        try:
            # Get template structure
            template_structure = await self.get_template_structure(bank_code, template_id)
            
            if not template_structure:
                print(f"⚠️ Could not load template structure for extraction")
                return nested_data
            
            flat_data = {}
            tab_ids = set(template_structure["tabs"].keys())
            
            # Extract fields from tab sections
            for key, value in nested_data.items():
                if key in tab_ids and isinstance(value, dict):
                    # This is a tab section, extract its fields
                    for field_id, field_value in value.items():
                        flat_data[field_id] = field_value
                else:
                    # This is a direct field (common fields or unorganized)
                    flat_data[key] = value
            
            print(f"✅ Extracted {len(flat_data)} fields from nested structure")
            
            return flat_data
            
        except Exception as e:
            print(f"❌ Error extracting form data: {e}")
            return nested_data
    
    async def validate_report_structure(
        self, 
        report_data: Dict[str, Any], 
        bank_code: str, 
        template_id: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate that report data follows correct template structure
        
        Args:
            report_data: Report data to validate
            bank_code: Bank code
            template_id: Template ID
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        try:
            template_structure = await self.get_template_structure(bank_code, template_id)
            
            if not template_structure:
                return False, ["Could not load template structure for validation"]
            
            errors = []
            tab_ids = set(template_structure["tabs"].keys())
            
            # Check if report follows tab structure
            has_tab_structure = any(key in tab_ids for key in report_data.keys())
            
            if not has_tab_structure:
                errors.append("Report data does not follow tab-based structure")
            
            # Check for required tabs
            for tab_id in template_structure["tab_order"]:
                if tab_id not in report_data:
                    errors.append(f"Missing required tab: {tab_id}")
            
            # Check for fields in wrong tabs
            field_to_tab = self.get_field_tab_mapping(template_structure)
            
            for tab_id, tab_data in report_data.items():
                if tab_id in tab_ids and isinstance(tab_data, dict):
                    for field_id in tab_data.keys():
                        expected_tab = field_to_tab.get(field_id)
                        if expected_tab and expected_tab != tab_id:
                            errors.append(f"Field '{field_id}' should be in tab '{expected_tab}', not '{tab_id}'")
            
            is_valid = len(errors) == 0
            
            if is_valid:
                print(f"✅ Report structure validation passed")
            else:
                print(f"⚠️ Report structure validation failed: {len(errors)} errors")
            
            return is_valid, errors
            
        except Exception as e:
            return False, [f"Validation error: {str(e)}"]


# Utility functions for easy access
async def organize_report_data(
    flat_form_data: Dict[str, Any], 
    bank_code: str, 
    template_id: str
) -> Dict[str, Any]:
    """
    Convenience function to organize flat form data by template tabs
    """
    mapper = TemplateFieldMappingService()
    try:
        await mapper.connect()
        return await mapper.organize_form_data_by_tabs(flat_form_data, bank_code, template_id)
    finally:
        await mapper.disconnect()


async def extract_report_data(
    nested_data: Dict[str, Any], 
    bank_code: str, 
    template_id: str
) -> Dict[str, Any]:
    """
    Convenience function to extract nested data to flat structure for frontend
    """
    mapper = TemplateFieldMappingService()
    try:
        await mapper.connect()
        return await mapper.extract_form_data_from_tabs(nested_data, bank_code, template_id)
    finally:
        await mapper.disconnect()


async def validate_report_data(
    report_data: Dict[str, Any], 
    bank_code: str, 
    template_id: str
) -> Tuple[bool, List[str]]:
    """
    Convenience function to validate report structure
    """
    mapper = TemplateFieldMappingService()
    try:
        await mapper.connect()
        return await mapper.validate_report_structure(report_data, bank_code, template_id)
    finally:
        await mapper.disconnect()


# Example usage and testing
async def main():
    """Test the template field mapping service"""
    mapper = TemplateFieldMappingService()
    
    try:
        await mapper.connect()
        
        # Test template structure loading
        structure = await mapper.get_template_structure("SBI", "land-property")
        
        if structure:
            print(f"\n📋 Template Structure:")
            print(f"   Bank: {structure['bank_code']}")
            print(f"   Template: {structure['template_id']}")
            print(f"   Collection: {structure['collection_ref']}")
            print(f"   Tabs: {structure['tab_order']}")
            
            # Test form data organization
            sample_flat_data = {
                "applicant_name": "Test Applicant",
                "bank_branch": "sbi_mumbai_main",
                "plot_survey_no": "123/A",
                "site_area": "1000",
                "total_extent_of_site": "1000",
                "valuation_rate": "5000",
                "estimated_value_of_land": "5000000"
            }
            
            organized_data = await mapper.organize_form_data_by_tabs(
                sample_flat_data, "SBI", "land-property"
            )
            
            print(f"\n🔄 Organization Test:")
            print(f"   Input fields: {len(sample_flat_data)}")
            print(f"   Organized structure: {list(organized_data.keys())}")
            
            # Test extraction back to flat
            extracted_data = await mapper.extract_form_data_from_tabs(
                organized_data, "SBI", "land-property"
            )
            
            print(f"\n📤 Extraction Test:")
            print(f"   Extracted fields: {len(extracted_data)}")
            print(f"   Match original: {set(sample_flat_data.keys()) == set(extracted_data.keys())}")
        
    finally:
        await mapper.disconnect()


if __name__ == "__main__":
    asyncio.run(main())