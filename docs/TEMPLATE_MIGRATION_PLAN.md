# 📋 Migration Plan: MongoDB Template → New C# Structure

## 📊 Current Structure Analysis

### **Current MongoDB Structure (As-Is)**

The SBI Land template is stored in `valuation_admin` database with:

```
sbi_land_property_details (Single Document)
├── _id
├── metadata (generation info, version, refreshDate)
├── templateMetadata
│   ├── templateId: "SBI_LAND_TEMPLATE_V1"
│   ├── templateName: "SBI Land Property Valuation"
│   ├── bankCode: "SBI"
│   ├── propertyType: "Land"
│   ├── version: "2.0"
│   └── tabs[] (5 tabs):
│       ├── property_details (hasSections: true, 4 sections)
│       ├── site_characteristics (hasSections: true, 2 sections)
│       ├── valuation (hasSections: true, 2 sections)
│       ├── construction_specifications (hasSections: true, 3 sections)
│       └── detailed_valuation (hasSections: false)
│
├── documents[] (5 separate template documents)
│   ├── [0] SBI_LAND_PROPERTY_DETAILS_V1
│   │   ├── templateId
│   │   ├── sections[] (4 sections with fields)
│   │   └── fields[]
│   ├── [1] SBI_LAND_SITE_CHARACTERISTICS_V1
│   ├── [2] SBI_LAND_VALUATION_V1
│   ├── [3] SBI_LAND_CONSTRUCTION_SPECS_V1
│   └── [4] SBI_LAND_DETAILED_VALUATION_V1
│
└── fields[] (BankBranch selector - 1 field)
```

### **Additional Collections**
- `common_form_fields`: Contains fields shared across all templates
- `document_types`: Document upload type definitions
- Bank-specific collections for other banks (BOB, BOI, CBI, etc.)

---

## 🎯 Target Structure (C# Model)

```
ValuationTemplate
├── TemplateId: "SBI_LAND_TEMPLATE_V1"
├── TemplateName: "SBI Land Property Valuation"
├── TemplateDescription: "..."
├── BankDetails: { BankCode: "SBI", BankName: "State Bank of India" }
├── PropertyType: Land
├── Elements[] (Mixed array of fields + containers)
│   ├── Common Fields (from common_form_fields)
│   │   ├── report_reference_number (InputField)
│   │   ├── valuation_date (InputField)
│   │   ├── inspection_date (InputField)
│   │   ├── applicant_name (InputField)
│   │   ├── bank_branch (InputField - Dropdown)
│   │   └── valuation_purpose (InputField - Dropdown)
│   │
│   └── Bank-Specific Tabs (from documents[])
│       ├── ContainerField (Tab: "Property Details")
│       │   └── Children[] (Groups/Sections)
│       │       ├── ContainerField (Group: "Part A - Documents")
│       │       │   └── Children[] (Fields from section)
│       │       ├── ContainerField (Group: "Part B - Address")
│       │       ├── ContainerField (Group: "Part C - Property Info")
│       │       └── ContainerField (Group: "Part D - Others")
│       │
│       ├── ContainerField (Tab: "Site Characteristics")
│       ├── ContainerField (Tab: "Valuation")
│       ├── ContainerField (Tab: "Construction Specs")
│       └── ContainerField (Tab: "Detailed Valuation")
│
└── CalculationRules[] (Extracted from field.formula)
    ├── Rule 1: estimated_land_value = total_extent_plot * valuation_rate
    ├── Rule 2: land_total = ...
    └── Rule N: ...
```

---

## 🔄 Migration Strategy

### **Phase 1: Data Collection & Mapping**
1. **Fetch Common Fields** from `common_form_fields` collection
2. **Fetch Bank-Specific Documents** from `sbi_land_property_details.documents[]`
3. **Extract Calculation Rules** from fields with `formula` property
4. **Map Field Types** (MongoDB fieldType → C# FieldType)

### **Phase 2: Transform Structure**
1. **Create Root Template** (TemplateId, BankDetails, PropertyType)
2. **Add Common Fields** as top-level `Elements[]`
3. **Transform Tabs** → `ContainerField` with `Container = Tab`
4. **Transform Sections/Groups** → `ContainerField` with `Container = Group/Section`
5. **Transform Fields** → `InputField`, `TableField`, `AttachmentField`
6. **Extract Formulas** → Separate `CalculationRules[]` array

### **Phase 3: New Database Creation**
1. Create new database: `valuation_templates`
2. Create collection: `templates`
3. Create indexes for performance
4. Insert migrated template

---

## 📦 Field Type Mapping

| **MongoDB fieldType** | **C# Structure** | **Notes** |
|-----------------------|------------------|-----------|
| `text` | `InputField { SpecificType: Text }` | Simple text input |
| `textarea` | `InputField { SpecificType: Text }` | Multi-line text |
| `number` | `InputField { SpecificType: Number }` | Numeric input |
| `currency` | `InputField { SpecificType: Number }` | Number with currency display |
| `date` | `InputField { SpecificType: Date }` | Date picker |
| `select` / `dropdown` | `InputField { SpecificType: Dropdown, Options: [...] }` | Dropdown list |
| `group` | `ContainerField { Container: Group, Children: [...] }` | Groups subFields |
| `table` | `TableField { Columns: [...], Summaries: [...] }` | Table with columns |
| `dynamic_table` | `TableField { MinRows: 1, ... }` | User can add rows |
| `file_upload` | `AttachmentField { AllowedExtensions: [...] }` | File upload |

---

## 🧮 Calculation Rules Extraction

### **Current Structure (MongoDB)**
```json
{
  "fieldId": "estimated_land_value",
  "fieldType": "currency",
  "formula": "total_extent_plot * valuation_rate",
  "calculationMetadata": {
    "dependencies": ["total_extent_plot", "valuation_rate"],
    "realTimeUpdate": true
  }
}
```

### **Target Structure (C#)**
```csharp
// Field Definition (NO formula)
new InputField {
    FieldId = "estimated_land_value",
    SpecificType = FieldType.Number,
    IsReadOnly = true,  // ← Calculated fields are readonly
    DisplayOrder = ...
}

// Separate Calculation Rule
new CalculationRule {
    RuleId = "calc_estimated_land_value",
    TriggerFieldIds = ["total_extent_plot", "valuation_rate"],
    Formula = "{total_extent_plot} * {valuation_rate}",
    TargetFieldId = "estimated_land_value"
}
```

---

## 🛠️ Implementation Steps

### **Step 1: Create Migration Script**
```python
# scripts/migrate_sbi_land_to_new_structure.py
1. Connect to MongoDB
2. Fetch common_form_fields
3. Fetch sbi_land_property_details
4. Transform to new structure
5. Save to new database
```

### **Step 2: Create New Database Schema**
```javascript
// New database: valuation_templates
{
  templates: {
    // Index on templateId, bankCode, propertyType
    documents: [
      {
        templateId: "SBI_LAND_TEMPLATE_V1",
        templateName: "...",
        bankDetails: {...},
        propertyType: "Land",
        elements: [...],  // Flat array with recursive containers
        calculationRules: [...]  // Separate logic
      }
    ]
  }
}
```

### **Step 3: Validation**
1. Count total fields: Old vs New
2. Verify all formulas extracted
3. Check field type conversions
4. Validate nesting structure
5. Test with sample report creation

---

## 📈 Benefits of New Structure

### **1. Cleaner Separation**
- **Structure** (Elements) vs **Logic** (CalculationRules)
- **Presentation** (DisplayOrder, Labels) vs **Behavior** (Formulas, Validation)

### **2. Easier to Maintain**
- Update a calculation without touching field definitions
- Reuse calculation rules across templates
- Clear dependency tracking

### **3. Better Performance**
- Single document per template (no joins needed)
- Indexed for fast lookups
- Recursive structure allows deep nesting

### **4. Type Safety**
- If using TypeScript/C# backend, compile-time validation
- Polymorphic deserialization
- Schema validation

---

## 🚨 Risks & Mitigation

| **Risk** | **Impact** | **Mitigation** |
|----------|------------|----------------|
| Data loss during migration | HIGH | Backup old DB before migration, run in test environment first |
| Formula extraction errors | MEDIUM | Validate all formulas, keep original structure alongside |
| Field mapping issues | MEDIUM | Create comprehensive mapping table, test each type |
| Performance regression | LOW | Add proper indexes, test with production data volume |
| Frontend breaking | HIGH | Keep old API working during transition, gradual rollout |

---

## 📝 Migration Checklist

### **Pre-Migration**
- [ ] Backup `valuation_admin` database
- [ ] Document all current field types used
- [ ] List all templates to migrate (SBI Land, SBI Apartment, etc.)
- [ ] Set up test environment

### **Migration Execution**
- [ ] Create new database `valuation_templates`
- [ ] Fetch and transform common fields
- [ ] Fetch and transform SBI Land template
- [ ] Extract all calculation rules
- [ ] Validate transformed data
- [ ] Insert into new database
- [ ] Create indexes

### **Post-Migration**
- [ ] Compare field counts (old vs new)
- [ ] Test template loading in frontend
- [ ] Test report creation
- [ ] Test formula calculations
- [ ] Verify file uploads
- [ ] Load testing

### **Rollout**
- [ ] Deploy backend API changes
- [ ] Update frontend template service
- [ ] Monitor for errors
- [ ] Gradual rollout (one bank at a time)
- [ ] Full migration
- [ ] Deprecate old structure

---

## 🎯 Next Actions

1. **Review this plan** with the team
2. **Create Python migration script** (fetch + transform + insert)
3. **Run migration in test environment**
4. **Validate results**
5. **Update frontend to support both structures** (during transition)
6. **Execute migration for production**

---

## 📊 Estimated Effort

| **Task** | **Effort** | **Priority** |
|----------|------------|--------------|
| Create migration script | 2-3 days | P0 |
| Test & validate | 1-2 days | P0 |
| Update backend API | 2-3 days | P1 |
| Update frontend services | 3-4 days | P1 |
| Testing & debugging | 2-3 days | P1 |
| **Total** | **~2 weeks** | |

---

**Status**: ✅ Plan Complete - Ready for Review
**Created**: March 15, 2026
**Last Updated**: March 15, 2026
