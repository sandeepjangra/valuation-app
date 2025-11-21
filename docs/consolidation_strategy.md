# Bank Collection Consolidation Strategy

## 🎯 Objective
Consolidate 8 separate bank documents into a unified structure to simplify backend aggregation and improve maintainability.

## 📊 Current State Analysis

### Problems:
- 8 separate bank documents in `banks` collection
- Each bank references separate collections (`bob_land_property_details`, `sbi_land_property_details`, etc.)
- Inconsistent architectures (`reference_based` vs `unknown`)
- Complex backend aggregation with multiple queries

### Collections Currently Used:
- `common_form_fields` (shared)
- `bob_land_property_details`
- `bob_apartment_property_details`
- `sbi_land_property_details`
- `sbi_apartment_property_details`
- `boi_land_property_details`
- `boi_apartment_property_details`
- `hdfc_all_property_details`
- `pnb_all_property_details`
- `cbi_all_property_details`
- `uco_all_property_details`
- `ubi_land_property_details`
- `ubi_apartment_property_details`

## 🏗️ Consolidated Architecture

### New Structure:
```json
{
  "_id": "unified_banks_v3",
  "version": "3.0",
  "architecture": "unified_reference_based",
  "lastUpdated": "2025-11-09T00:00:00Z",
  "banks": [
    {
      "bankCode": "BOB",
      "bankName": "Bank of Baroda",
      "bankType": "public_sector",
      "isActive": true,
      "headquarters": {...},
      "branches": [...],
      "templates": [
        {
          "templateId": "BOB_LAND_V3",
          "templateCode": "land",
          "propertyType": "land",
          "version": "3.0",
          "fields": {
            "commonFields": {
              "collectionRef": "common_form_fields"
            },
            "bankSpecificFields": {
              "collectionRef": "unified_bank_templates",
              "filter": {
                "bankCode": "BOB",
                "propertyType": "land",
                "isActive": true
              }
            }
          }
        }
      ]
    }
  ]
}
```

### New Collections:
1. **`unified_banks`** - Single document with all banks
2. **`unified_bank_templates`** - All bank-specific templates in one collection
3. **`common_form_fields`** - Keep as is (already shared)

## 🔄 Migration Steps

### Step 1: Create Unified Collections
1. Create `unified_bank_templates` collection
2. Migrate all bank-specific field data into unified structure
3. Update field documents to include `bankCode` and `propertyType` identifiers

### Step 2: Create Unified Banks Document
1. Merge all 8 bank documents into single `unified_banks` document
2. Update template references to use unified collections
3. Standardize all architectures to `unified_reference_based`

### Step 3: Update Backend Aggregation
1. Modify aggregation endpoint to query unified collections
2. Update filtering logic to use `bankCode` + `propertyType`
3. Simplify pipeline to single lookup per collection type

### Step 4: Test & Validate
1. Ensure all existing functionality works
2. Verify frontend compatibility
3. Performance testing

## 🚀 Implementation Plan

### Phase 1: Data Migration Script
```python
# Create migration script to:
# 1. Read all existing bank collections
# 2. Merge into unified structure
# 3. Create new collections
# 4. Validate data integrity
```

### Phase 2: Backend Updates
```python
# Update main.py aggregation logic:
# 1. Query unified_banks collection
# 2. Use unified_bank_templates collection
# 3. Simplify aggregation pipeline
```

### Phase 3: Testing
- API endpoint testing
- Frontend integration testing
- Performance comparison

## 📋 Benefits After Consolidation

✅ **Simplified Maintenance**: Single source of truth
✅ **Better Performance**: Fewer database queries
✅ **Consistent Architecture**: Unified approach across all banks
✅ **Easier Updates**: Single collection to modify
✅ **Reduced Complexity**: Simpler backend logic
✅ **Better Scalability**: Easy to add new banks/templates

## 🔧 Technical Implementation Details

### New Aggregation Logic:
1. Query `unified_banks` → Get bank info + template config
2. Query `common_form_fields` → Get common fields
3. Query `unified_bank_templates` with bankCode filter → Get bank-specific fields
4. Assemble response (same format as current)

### Data Structure:
Each document in `unified_bank_templates`:
```json
{
  "_id": "...",
  "bankCode": "BOB",
  "propertyType": "land",
  "templateId": "BOB_LAND_V3",
  "templateMetadata": {...},
  "documents": [...],
  "isActive": true,
  "version": "3.0"
}
```