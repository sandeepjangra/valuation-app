# 📊 Table Fields Analysis Report

**Generated:** November 28, 2025  
**Purpose:** Identify and standardize table fields across bank templates

---

## 🔍 FINDINGS SUMMARY

### **Total Table Fields Found:** 8 unique table fields
- **Static Tables (with predefined rows):** 5 fields
- **Dynamic Tables (user can add/remove rows):** 3 fields

### **Templates with Tables:** 6 out of 12
- ✅ BOB Land (1 table)
- ✅ BOI Apartment (2 tables)
- ✅ BOI Land (3 tables: 1 static, 2 dynamic)
- ✅ SBI Apartment (2 tables)
- ✅ UCO Apartment (2 tables)
- ✅ UCO Land (3 tables: 1 static, 2 dynamic)

### **Templates WITHOUT Tables:** 6 out of 12
- ❌ CBI All Property
- ❌ HDFC All Property
- ❌ PNB Land
- ❌ SBI Land
- ❌ UBI Apartment
- ❌ UBI Land

---

## 📋 STATIC TABLES (Predefined Rows)

### 1. **boundaries_dimensions_table** ⭐ MOST COMMON
**Appears in:** 5 templates (BOB Land, BOI Apartment, BOI Land, SBI Apartment, UCO Land)

**Purpose:** Define property boundaries with directions (North, South, East, West)

**Structure:**
```json
{
  "fieldId": "boundaries_dimensions_table",
  "fieldType": "table",
  "columns": [
    {
      "columnId": "direction",
      "columnName": "Direction",
      "fieldType": "text",
      "isReadonly": true
    },
    {
      "columnId": "boundaries_per_documents",
      "columnName": "Boundaries As Per Documents",
      "fieldType": "text"
    },
    {
      "columnId": "boundaries_actual",
      "columnName": "Boundaries Actual",
      "fieldType": "text"
    }
  ],
  "rows": [
    {"direction": "North", "boundaries_per_documents": "", "boundaries_actual": ""},
    {"direction": "South", "boundaries_per_documents": "", "boundaries_actual": ""},
    {"direction": "East", "boundaries_per_documents": "", "boundaries_actual": ""},
    {"direction": "West", "boundaries_per_documents": "", "boundaries_actual": ""}
  ]
}
```

**Status:** ✅ Consistent across all 5 templates

---

### 2. **valuation_table**
**Appears in:** 2 templates (BOI Apartment, SBI Apartment)

**Purpose:** Breakdown of valuation details for apartment properties

**Structure:**
- **Columns:** 5 (sr_no, description, qty, rate_per_unit, estimated_value)
- **Rows:** 11 predefined rows (wardrobes, showcases, kitchen, superfine finish, interior decorations, electrical fittings, gates/grills, potential value, others, total)
- **Last row:** Read-only total row

**Status:** ✅ Consistent between both apartment templates

---

### 3. **dimensions_table**
**Appears in:** 1 template (UCO Apartment only)

**Purpose:** Enhanced boundaries table with dimensions columns

**Structure:**
- **Columns:** 5 (direction, boundaries_per_documents, boundaries_actual, dimensions_per_documents, dimensions_actual)
- **Rows:** 4 static (North, South, East, West)

**Status:** ⚠️ Similar to `boundaries_dimensions_table` but with extra dimension columns

**Recommendation:** Should UCO Apartment use `boundaries_dimensions_table` instead, or should other templates adopt this enhanced version?

---

### 4. **details_of_valuation**
**Appears in:** 1 template (UCO Apartment only)

**Purpose:** Detailed valuation calculation table

**Structure:**
- **Columns:** 8 (sr_no, floor_level, description_of_item, plinth_covered_area, estimated_replacement_rate, estimated_replacement_cost, depreciation_percent, net_value)
- **Rows:** 1 empty row (dynamic entry expected)

**Status:** ⚠️ UCO-specific, similar purpose to `valuation_table` but different structure

**Recommendation:** Standardize with `valuation_table` or keep as UCO-specific variant?

---

## 🔄 DYNAMIC TABLES (User Can Add/Remove Rows)

### 5. **floor_wise_construction_specifications_table**
**Appears in:** 1 template (BOI Land only)

**Purpose:** Floor-wise building construction details

**Field Type:** `dynamic_table`

**Status:** ⚠️ BOI Land specific - missing column/row structure in current data

---

### 6. **valuation_floor_wise_table**
**Appears in:** 1 template (BOI Land only)

**Purpose:** Floor-wise valuation breakdown

**Field Type:** `dynamic_table`

**Status:** ⚠️ BOI Land specific - missing column/row structure in current data

---

### 7. **building_specifications_table**
**Appears in:** 1 template (UCO Land only)

**Purpose:** Building specification details per floor/section

**Field Type:** `dynamic_table`

**Status:** ⚠️ UCO Land specific - need to extract full structure

---

### 8. **floor_wise_valuation_table**
**Appears in:** 1 template (UCO Land only)

**Purpose:** Floor-wise valuation details

**Field Type:** `dynamic_table`

**Status:** ⚠️ UCO Land specific - similar to BOI's `valuation_floor_wise_table`

**Recommendation:** These two might be candidates for standardization

---

## 🎯 STANDARDIZATION RECOMMENDATIONS

### **CRITICAL - Must Standardize:**

1. **`boundaries_dimensions_table`** ✅ Already consistent
   - Action: Add to templates that don't have it (CBI, HDFC, PNB, SBI Land, UBI Apartment, UBI Land)
   - This is fundamental for property valuation

### **HIGH PRIORITY - Should Standardize:**

2. **`valuation_table`** (for Apartment properties)
   - Currently in: BOI Apartment, SBI Apartment
   - Should add to: UBI Apartment
   - UCO Apartment uses `details_of_valuation` instead - needs decision

3. **Floor-wise Valuation Dynamic Table**
   - BOI Land has: `valuation_floor_wise_table`
   - UCO Land has: `floor_wise_valuation_table`
   - Action: Standardize naming and structure, apply to all Land templates

### **MEDIUM PRIORITY - Consider Standardizing:**

4. **Building Specifications Dynamic Table**
   - BOI Land has: `floor_wise_construction_specifications_table`
   - UCO Land has: `building_specifications_table`
   - Action: Standardize naming and structure

### **LOW PRIORITY - Bank-Specific Variants:**

5. **UCO-Specific Tables**
   - `dimensions_table` (enhanced boundaries table)
   - `details_of_valuation` (different valuation structure)
   - Decision needed: Keep as UCO-specific or standardize?

---

## ❓ QUESTIONS FOR DECISION

1. **Should ALL templates have `boundaries_dimensions_table`?**
   - Currently missing from 7 templates
   - This seems fundamental for property boundaries

2. **Apartment Valuation Table:**
   - Standardize on `valuation_table` (BOI/SBI style)?
   - Or use `details_of_valuation` (UCO style)?
   - Or keep both as variants?

3. **Floor-wise Valuation for Land:**
   - Should ALL land property templates have floor-wise valuation dynamic table?
   - What should be the standard column structure?

4. **Building Specifications:**
   - Should ALL templates with buildings have building specs dynamic table?
   - What columns are essential?

5. **UCO Dimensions Table:**
   - Replace with standard `boundaries_dimensions_table`?
   - Or upgrade all templates to use enhanced `dimensions_table`?

---

## 📝 NEXT STEPS

1. **Extract Full Structure** for all dynamic tables (need column definitions)
2. **Define Standard Table Schemas** based on business requirements
3. **Create Standardization Script** to:
   - Add missing `boundaries_dimensions_table` to all templates
   - Standardize apartment valuation tables
   - Standardize land/building floor-wise tables
   - Ensure consistent column structures
4. **Validate** with business team before applying changes
5. **Apply** standardization across all templates
6. **Update MongoDB** with standardized templates

---

## 🔍 DETAILED STRUCTURE EXTRACTION NEEDED

The following dynamic tables need full structure extraction:
- `floor_wise_construction_specifications_table` (BOI Land)
- `valuation_floor_wise_table` (BOI Land)
- `building_specifications_table` (UCO Land)
- `floor_wise_valuation_table` (UCO Land)

Run dedicated extraction script to get column definitions, default rows, and validation rules.
