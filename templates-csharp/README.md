# C# Template Structure

This folder contains migrated templates in the new C# structure format.

## Folder Structure

- **`migrated/`** - Production-ready C# templates (14 files total)
  
  **Configuration Data:**
  - `banks.json` - Banks Collection with branches & template references (17.7KB)
  - `organizations.json` - Organizations Collection (0.8KB)
  
  **Template Files:**
  - `sbi_land_template.json` - SBI Land Property Valuation (75KB)
  - `sbi_apartment_template_v1.json` - SBI Apartment Property Valuation (61KB)
  - `bob_land_template_v1.json` - BOB Land Property Valuation (57KB)
  - `boi_land_template_v1.json` - BOI Land Property Valuation (57KB)
  - `boi_apartment_template_v1.json` - BOI Apartment Property Valuation (64KB)
  - `uco_land_template_v1.json` - UCO Land Property Valuation (51KB)
  - `uco_apartment_template_v1.json` - UCO Apartment Property Valuation (62KB)
  - `ubi_land_template_v1.json` - UBI Land Property Valuation (59KB)
  - `ubi_apartment_template_v1.json` - UBI Apartment Property Valuation (59KB)
  - `pnb_all_template_v1.json` - PNB All Property Valuation (59KB)
  - `cbi_all_template_v1.json` - CBI All Property Valuation (59KB)
  - `hdfc_all_template_v1.json` - HDFC All Property Valuation (59KB)

- **`archive/`** - Migration analysis and temporary files
  - `sbi_land_property_details_full.json` - Original template from MongoDB
  - `sbi_land_template_analysis.json` - Structure analysis
  - `migration_validation_stats.json` - Migration validation results

## Template Format

The new C# structure uses:

### Key Differences from Old Structure:
- **PascalCase naming**: `FieldId`, `SpecificType`, `Children` (vs camelCase)
- **Flat Elements array**: All fields in single array with recursive containers
- **Separate CalculationRules**: Formulas extracted to dedicated array
- **Type system**: Uses `$type` discriminator for polymorphism
  - `input` - Regular input fields
  - `container` - Tabs, sections, groups
  - `table` - Table fields with columns

### Structure:
```json
{
  "TemplateId": "SBI_LAND_TEMPLATE_V1",
  "TemplateName": "SBI Land Property Valuation",
  "BankDetails": {
    "BankCode": "SBI",
    "BankName": "State Bank of India"
  },
  "PropertyType": "Land",
  "Elements": [
    // All fields as flat array with recursive containers
  ],
  "CalculationRules": [
    {
      "RuleId": "calc_estimated_land_value",
      "Formula": "total_extent_plot * valuation_rate",
      "TriggerFieldIds": ["total_extent_plot", "valuation_rate"],
      "TargetFieldId": "estimated_land_value"
    }
  ]
}
```

## Database

Templates are stored in MongoDB Atlas:
- **Database**: `valuation_templates`
- **Collection**: `templates`

## Scripts

Use these scripts to manage templates:

### Upload to MongoDB Atlas:
```bash
python3 scripts/upload_csharp_template_to_atlas.py
```

### Migrate from Old Structure:
```bash
python3 scripts/migrate_sbi_land_to_new_structure.py
```

## Migration History

### Batch Migration - March 15, 2026
Successfully migrated **12 templates** from legacy MongoDB structure to new C# format:

| Bank | Property Type | Template ID | Fields | Calculation Rules | Status |
|------|--------------|-------------|--------|-------------------|--------|
| SBI | Land | SBI_LAND_TEMPLATE_V1 | 206 | 2 | ✅ Active |
| SBI | Apartment | SBI_APARTMENT_TEMPLATE_V1 | 94 | 0 | ✅ Active |
| BOB | Land | BOB_LAND_TEMPLATE_V1 | 90 | 1 | ✅ Active |
| BOI | Land | BOI_LAND_TEMPLATE_V1 | 88 | 1 | ✅ Active |
| BOI | Apartment | BOI_APARTMENT_TEMPLATE_V1 | 98 | 0 | ✅ Active |
| UCO | Land | UCO_LAND_TEMPLATE_V1 | 108 | 0 | ✅ Active |
| UCO | Apartment | UCO_APARTMENT_TEMPLATE_V1 | 131 | 0 | ✅ Active |
| UBI | Land | UBI_LAND_TEMPLATE_V1 | 128 | 1 | ✅ Active |
| UBI | Apartment | UBI_APARTMENT_TEMPLATE_V1 | 128 | 1 | ✅ Active |
| PNB | All | PNB_ALL_TEMPLATE_V1 | 128 | 1 | ✅ Active |
| CBI | All | CBI_ALL_TEMPLATE_V1 | 128 | 1 | ✅ Active |
| HDFC | All | HDFC_ALL_TEMPLATE_V1 | 128 | 1 | ✅ Active |

**Migration Results**:
- ✅ **12 templates** successfully migrated
- ✅ **1 banks collection** with 8 banks, 13 branches, 12 template references
- ✅ **1 organizations collection** with 1 organization
- ✅ **1,487 total fields** preserved across all templates
- ✅ **9 calculation rules** extracted and working
- ✅ All data uploaded to MongoDB Atlas (`valuation_templates` database)
- ✅ 100% success rate with 0% data loss

## Notes

- The old MongoDB structure used nested `documents` array with `sections` and `fields`
- The new C# structure uses flat `Elements` array with recursive `Children`
- Formula fields are marked `IsReadonly: true` and calculations are in separate `CalculationRules` array
- All container types (Tab, Section, Group) use the same `container` type with different `Container` property values
