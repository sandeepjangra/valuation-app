# Document Types Collection Integration Guide

## Overview
This guide explains how to integrate the new `document_types` collection with existing backend endpoints while maintaining backward compatibility.

## Integration Steps

### 1. Update main.py - Add Enhanced Template Service

```python
# Add to imports
from services.enhanced_template_service import EnhancedTemplateService

# Update your existing consolidated templates endpoint
@app.get("/api/templates/consolidated/{bank_code}/{property_type}")
async def get_consolidated_templates(
    bank_code: str,
    property_type: str,
    organization_id: str = Query(None)
):
    try:
        # Replace existing logic with enhanced service
        template_service = EnhancedTemplateService(db)
        result = template_service.get_consolidated_templates(
            bank_code=bank_code,
            property_type=property_type,
            organization_id=organization_id
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Templates retrieved successfully with document types integration"
        }
        
    except Exception as e:
        logger.error(f"Error in consolidated templates endpoint: {e}")
        return HTTPException(
            status_code=500,
            detail=f"Error retrieving templates: {str(e)}"
        )
```

### 2. Update Existing Aggregation Logic

**Option A: Minimal Integration (Recommended)**
```python
# In your existing aggregation pipeline, add this stage to merge document types
def add_document_types_to_pipeline(pipeline: list, bank_code: str, property_type: str):
    """Add document types lookup to existing aggregation pipeline"""
    
    # Add lookup stage for document types
    document_lookup_stage = {
        "$lookup": {
            "from": "document_types",
            "let": {
                "propertyType": property_type,
                "bankCode": bank_code
            },
            "pipeline": [
                {
                    "$match": {
                        "$expr": {
                            "$and": [
                                {"$eq": ["$isActive", True]},
                                {
                                    "$or": [
                                        {"$in": ["$$propertyType", "$applicablePropertyTypes"]},
                                        {"$in": ["*", "$applicablePropertyTypes"]}
                                    ]
                                },
                                {
                                    "$or": [
                                        {"$in": ["$$bankCode", "$applicableBanks"]},
                                        {"$in": ["*", "$applicableBanks"]}
                                    ]
                                }
                            ]
                        }
                    }
                },
                {"$sort": {"sortOrder": 1}},
                {
                    "$project": {
                        "_id": 0,
                        "fieldId": "$documentId",
                        "uiDisplayName": 1,
                        "fieldType": {"$ifNull": ["$fieldType", "textarea"]},
                        "placeholder": {"$ifNull": ["$placeholder", ""]},
                        "isRequired": {"$ifNull": ["$isRequired", False]},
                        "sortOrder": {"$ifNull": ["$sortOrder", 1]},
                        "includeInCustomTemplate": {"$ifNull": ["$includeInCustomTemplate", True]}
                    }
                }
            ],
            "as": "documentTypeFields"
        }
    }
    
    # Add field merging stage
    merge_stage = {
        "$addFields": {
            "documents": {
                "$map": {
                    "input": "$documents",
                    "as": "doc",
                    "in": {
                        "$mergeObjects": [
                            "$$doc",
                            {
                                "sections": {
                                    "$map": {
                                        "input": "$$doc.sections",
                                        "as": "section",
                                        "in": {
                                            "$cond": {
                                                "if": {"$eq": ["$$section.useDocumentCollection", True]},
                                                "then": {
                                                    "$mergeObjects": [
                                                        "$$section",
                                                        {
                                                            "fields": {
                                                                "$concatArrays": [
                                                                    "$documentTypeFields",
                                                                    {"$ifNull": ["$$section.fields", []]}
                                                                ]
                                                            }
                                                        }
                                                    ]
                                                },
                                                "else": "$$section"
                                            }
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
    }
    
    pipeline.extend([document_lookup_stage, merge_stage])
    return pipeline

# Usage in your existing endpoint
def get_existing_consolidated_templates(bank_code: str, property_type: str):
    collection_name = f"{bank_code.lower()}_{property_type.lower()}_property_details"
    
    # Your existing pipeline
    pipeline = [
        {"$match": {"isActive": True}},
        # ... your existing stages
    ]
    
    # Add document types integration
    pipeline = add_document_types_to_pipeline(pipeline, bank_code, property_type)
    
    return list(db[collection_name].aggregate(pipeline))
```

### 3. Template Migration Flags

**Add Migration Status Tracking**
```python
# Add this to your template documents to track migration status
migration_flags = {
    "useDocumentCollection": True,  # Enable document collection integration
    "migrationCompleted": True,     # Mark as migrated
    "migrationDate": datetime.now(),
    "originalFields": []            # Backup of original document fields
}

# Update template sections that use documents
section_update = {
    "useDocumentCollection": True,
    "documentFilter": {
        "propertyType": "Land",  # or specific property type
        "bankCode": "*"          # or specific bank
    }
}
```

### 4. Backward Compatibility Handling

```python
def ensure_backward_compatibility(template_data):
    """Ensure templates work even if document_types collection is not available"""
    
    try:
        # Check if document_types collection exists
        if "document_types" not in db.list_collection_names():
            logger.warning("document_types collection not found, using fallback")
            return template_data
            
        # Process templates with document collection integration
        return process_with_document_types(template_data)
        
    except Exception as e:
        logger.error(f"Error in document types integration: {e}")
        # Fallback to original template data
        return template_data

def process_with_document_types(template_data):
    """Process templates with document types collection"""
    # Implementation similar to enhanced_template_service.py
    pass
```

### 5. Configuration Options

Add to your configuration:

```python
# config.py or settings
DOCUMENT_TYPES_CONFIG = {
    "enabled": True,                    # Enable/disable document types integration
    "fallback_on_error": True,         # Use fallback if integration fails
    "cache_document_types": True,      # Cache document types for performance
    "cache_ttl": 300,                  # Cache TTL in seconds
    "default_property_type": "Land",   # Default property type filter
    "default_bank_code": "*"           # Default bank code filter
}
```

## Migration Execution Plan

### Phase 1: Setup (No Impact)
1. Run migration script to create document_types collection
2. Deploy enhanced template service (not used yet)
3. Add migration flags to templates (useDocumentCollection: false)

### Phase 2: Gradual Migration 
1. Enable document collection for specific sections:
   ```python
   # Update specific sections to use document collection
   db.sbi_land_property_details.updateMany(
       {"documents.sections.sectionId": "list_of_documents"},
       {"$set": {"documents.$.sections.$[section].useDocumentCollection": True}},
       {"arrayFilters": [{"section.sectionId": "list_of_documents"}]}
   )
   ```

2. Monitor and validate results

### Phase 3: Full Integration
1. Switch all endpoints to use EnhancedTemplateService
2. Enable document collection for all relevant sections
3. Remove original hardcoded document fields

## Testing Strategy

```python
# Test cases to ensure compatibility
def test_document_types_integration():
    """Test document types integration works correctly"""
    
    # Test 1: Original endpoint still works
    response = client.get("/api/templates/consolidated/sbi/land")
    assert response.status_code == 200
    
    # Test 2: Document fields are merged correctly
    data = response.json()
    document_section = find_document_section(data)
    assert len(document_section['fields']) > 0
    
    # Test 3: Field structure is correct
    for field in document_section['fields']:
        assert 'fieldId' in field
        assert 'uiDisplayName' in field
        assert 'fieldType' in field

def test_fallback_behavior():
    """Test fallback when document_types collection is unavailable"""
    
    # Temporarily disable document_types collection
    # Verify endpoint still returns data
    pass

def test_performance():
    """Test performance impact of document types integration"""
    
    # Compare response times before/after integration
    # Ensure no significant performance degradation
    pass
```

## Monitoring and Rollback

### Monitoring Points
- Response time of consolidated templates endpoint
- Error rates in document types integration
- Field count consistency
- Template structure validation

### Rollback Plan
If issues occur:
1. Set `useDocumentCollection: false` in affected templates
2. Revert to original endpoint logic
3. Fix issues and re-enable gradually

## Performance Considerations

1. **Caching**: Cache document types by property type and bank code
2. **Indexing**: Ensure proper indexes on document_types collection
3. **Aggregation**: Use MongoDB aggregation for efficient field merging
4. **Lazy Loading**: Load document types only when needed

## Next Steps

1. Review and test the migration script
2. Deploy document_types collection to development environment  
3. Update one endpoint to use enhanced template service
4. Validate results and performance
5. Gradually migrate remaining endpoints
6. Complete integration and remove legacy code

This approach ensures zero downtime and backward compatibility while providing the improved maintainability of normalized document fields.