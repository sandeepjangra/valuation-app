# Calculated Fields Implementation

## Overview
Implemented a generic calculated field system that automatically computes field values based on formulas defined in MongoDB templates. This feature works across all bank templates and eliminates manual calculations for users.

## Features

### 1. **Generic Formula System**
- Supports multiple calculation types: `sum`, `product`, `average`, `custom`
- Works with any field marked with `calculatedField` configuration
- Handles nested fields (group subfields) using dot notation
- Currency-aware parsing (removes ₹, $, commas)

### 2. **Real-time Calculations**
- Automatic recalculation as users type in source fields
- Dependency tracking ensures calculations update when any source field changes
- Efficient: Only recalculates affected fields, not the entire form

### 3. **Tab-based Recalculation**
- Triggers recalculation when switching between tabs
- Ensures calculated values are always up-to-date when viewing different sections
- Handles cross-tab dependencies (e.g., grand_total depends on fields from other tabs)

### 4. **Readonly Enforcement**
- Calculated fields are always readonly in the UI
- Backend temporarily enables controls during calculation, then re-disables
- Prevents user from manually editing calculated values

## Implementation Details

### Frontend Components

#### 1. **Model Definition** (`template-field.model.ts`)
```typescript
export interface CalculatedFieldConfig {
  type: 'sum' | 'product' | 'average' | 'custom';
  sourceFields: string[];        // Field IDs to use in calculation
  customFormula?: string;         // For future complex formulas
  dependencies?: string[];        // Fields that trigger recalculation
}
```

Added to `TemplateField` and `BankSpecificField` interfaces:
```typescript
calculatedField?: CalculatedFieldConfig;
```

#### 2. **Calculation Service** (`calculation.service.ts`)

**Key Methods:**
- `evaluateCalculatedField()`: Evaluates formula based on configuration
- `getFieldValues()`: Retrieves values from form controls (handles nesting)
- `parseNumericValue()`: Converts currency strings to numbers
- `calculateSum()`, `calculateProduct()`, `calculateAverage()`: Formula implementations
- `getCalculatedFields()`: Extracts all calculated fields from template
- `getFieldDependencies()`: Returns fields that trigger recalculation

**Features:**
- Handles dot notation for nested fields (e.g., `extra_items.portico`)
- Null/undefined/empty value handling (defaults to 0)
- Currency string parsing (removes symbols and commas)
- Recursive processing of group fields

#### 3. **Report Form Integration** (`report-form.ts`)

**Initialization:**
1. `initializeCalculatedFields()`: Called after form build
2. Extracts calculated fields using `calculationService.getCalculatedFields()`
3. Sets up listeners for each calculated field via `setupCalculatedFieldListener()`
4. Performs initial calculation with `recalculateAllFields()`

**Real-time Updates:**
- Each calculated field subscribes to its dependencies' `valueChanges`
- When dependency changes, `calculateField()` is triggered
- Field is temporarily enabled, updated, then re-disabled

**Tab Switching:**
- `switchBankSpecificTab()` calls `recalculateAllFields()`
- Ensures values are fresh when user navigates between tabs

### Database Schema (MongoDB Template Definition)

**Example: UCO Land Property Template**

```json
{
  "fieldId": "grand_total",
  "technicalName": "grand_total",
  "uiDisplayName": "Total",
  "fieldType": "currency",
  "isReadonly": true,
  "calculatedField": {
    "type": "sum",
    "sourceFields": [
      "land_total",
      "building_total",
      "extra_items_total",
      "amenities_total",
      "services_total"
    ],
    "dependencies": [
      "land_total",
      "building_total",
      "extra_items_total",
      "amenities_total",
      "services_total"
    ]
  }
}
```

**Group Field Totals:**
```json
{
  "fieldId": "extra_items_total",
  "uiDisplayName": "Extra Items",
  "fieldType": "currency",
  "isReadonly": true,
  "calculatedField": {
    "type": "sum",
    "sourceFields": [
      "portico",
      "ornamental_front_door",
      "sitout_verandah_grills",
      "overhead_water_tank",
      "extra_steel_gates"
    ]
  }
}
```

## UCO Template Calculated Fields

Updated `backend/data/uco/uco_land_property_details.json` with:

### Detailed Valuation Tab:

1. **extra_items_total**
   - Sums: portico, ornamental_front_door, sitout_verandah_grills, overhead_water_tank, extra_steel_gates

2. **amenities_total**
   - Sums: wardrobes, glazed_tiles, interior_decorations, architectural_elevation, paneling_works, aluminum_works, aluminum_handrails, false_ceiling

3. **services_total**
   - Sums: water_supply_arrangements, drainage_arrangements, compound_wall, cb_deposits_fittings, pavement

4. **grand_total**
   - Sums: land_total, building_total, extra_items_total, amenities_total, services_total

5. **land_total** & **building_total**
   - Placeholder configurations (currently sum empty arrays)
   - Ready for future implementation when land/building calculation logic is defined

## Usage for Other Banks

### Step 1: Add `calculatedField` to MongoDB Template

```json
{
  "fieldId": "total_field_id",
  "fieldType": "currency",
  "isReadonly": true,
  "calculatedField": {
    "type": "sum",
    "sourceFields": ["field1", "field2", "field3"],
    "dependencies": ["field1", "field2", "field3"]
  }
}
```

### Step 2: Ensure Source Fields Exist

Make sure all fields in `sourceFields` array exist in the template (either in same tab or different tabs).

### Step 3: Deploy & Test

No code changes needed! The system automatically:
1. Detects calculated fields when template loads
2. Sets up listeners for dependencies
3. Calculates values in real-time
4. Updates on tab switches

## Calculation Types

### Sum (Current Implementation)
```json
{
  "type": "sum",
  "sourceFields": ["field1", "field2", "field3"]
}
```
Result: field1 + field2 + field3

### Product (Available)
```json
{
  "type": "product",
  "sourceFields": ["length", "width", "height"]
}
```
Result: length × width × height

### Average (Available)
```json
{
  "type": "average",
  "sourceFields": ["value1", "value2", "value3"]
}
```
Result: (value1 + value2 + value3) / 3

### Custom (Placeholder)
```json
{
  "type": "custom",
  "customFormula": "field1 * 0.85 + field2",
  "sourceFields": ["field1", "field2"]
}
```
*Note: Custom formula evaluation not yet implemented - reserved for future use*

## Architecture Benefits

### 1. **Separation of Concerns**
- Calculation logic in dedicated service
- Template metadata in database
- UI automatically adapts to configuration

### 2. **Maintainability**
- Add new calculated fields without code changes
- Formulas defined in database, easy to update
- No hardcoded field names in frontend

### 3. **Scalability**
- Works across all banks and property types
- Supports unlimited calculated fields
- Efficient dependency tracking

### 4. **User Experience**
- Real-time feedback as users type
- No manual calculations needed
- Always accurate totals

## Files Modified

### Frontend
1. `valuation-frontend/src/app/models/template-field.model.ts`
   - Added `CalculatedFieldConfig` interface
   - Updated `TemplateField` and `BankSpecificField` to include `calculatedField`

2. `valuation-frontend/src/app/services/calculation.service.ts` (NEW)
   - Complete calculation engine implementation
   - Formula evaluation, dependency tracking, value parsing

3. `valuation-frontend/src/app/components/report-form/report-form.ts`
   - Imported `CalculationService`
   - Added `calculatedFieldsMap` tracking
   - Implemented `initializeCalculatedFields()`, `setupCalculatedFieldListener()`, `calculateField()`, `recalculateAllFields()`
   - Integrated recalculation into tab switching

### Backend
1. `backend/data/uco/uco_land_property_details.json`
   - Added `calculatedField` configuration to 6 fields:
     - land_total (placeholder)
     - building_total (placeholder)
     - extra_items_total (5 source fields)
     - amenities_total (8 source fields)
     - services_total (5 source fields)
     - grand_total (5 source fields)

## Testing Checklist

- [ ] Load UCO Land template in report form
- [ ] Navigate to Construction Specifications tab
- [ ] Enter values in Extra Items fields (portico, ornamental_front_door, etc.)
- [ ] Switch to Detailed Valuation tab
- [ ] Verify `extra_items_total` shows sum of Extra Items fields
- [ ] Enter values in Amenities fields
- [ ] Verify `amenities_total` updates correctly
- [ ] Enter values in Services fields
- [ ] Verify `services_total` updates correctly
- [ ] Enter values for land_total and building_total
- [ ] Verify `grand_total` shows sum of all 5 total fields
- [ ] Switch between tabs - verify calculations persist
- [ ] Try to edit calculated fields - should be readonly
- [ ] Test with empty/null values - should default to 0
- [ ] Test with currency formatted values (₹ symbol, commas)

## Future Enhancements

1. **Custom Formula Parser**
   - Support complex expressions like `(field1 * field2) - field3`
   - Use safe expression evaluator (e.g., math.js)

2. **Conditional Calculations**
   - Calculate different formulas based on field values
   - Example: Different tax rates based on property type

3. **Cross-tab Dependencies**
   - Explicitly handle fields from different tabs
   - Optimize recalculation when switching tabs

4. **Validation Rules**
   - Min/max value checks on calculated fields
   - Warning messages if calculations seem incorrect

5. **Calculation History**
   - Show breakdown of calculation to user
   - Debugging aid for complex formulas

## Notes

- All calculated fields must be marked `isReadonly: true`
- Source fields should use correct `fieldId` (not `technicalName`)
- For group field subfields, use plain field ID (not dot notation in JSON)
- Dependencies array typically matches sourceFields (but can differ for complex scenarios)
- Empty/null values are treated as 0 in calculations
- Currency symbols and formatting are automatically stripped during calculation
