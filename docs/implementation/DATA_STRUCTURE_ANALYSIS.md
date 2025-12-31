# Data Structure Mismatch Analysis

## Issue Identified

The report document `rpt_0999c923f5a9` has a **mixed data structure** that doesn't properly match the SBI Land template expectations.

## Report Data Structure (Current - PROBLEMATIC)

The report has **both nested tab structure AND flat fields at the root level**:

### ✅ Properly Nested Fields (Good):
```json
{
  "report_data": {
    "property_details": {
      "property_part_a": {
        "agreement_to_sell": "",
        "list_of_documents_produced": "",
        "allotment_letter": "",
        "layout_plan": "",
        "sales_deed": "Sale Deed No. 12670 dated 01.11.2023...",
        "ats": "Dt. 08.10.2025 between...",
        "sanctioned_building_plan": "Sanctioned by MC Kharar..."
      },
      "property_part_b": {
        "owner_details": "Test Property Owner Details",
        "borrower_name": "Test Borrower Name",
        "postal_address": "456 Test Avenue, Mumbai...",
        "property_description": "Residential plot for bank valuation",
        "property_location": "",
        "city_town_village": ""
      }
    },
    "site_characteristics": {
      "site_part_a": {...},
      "site_part_b": {...}
    },
    "valuation": {
      "valuation_part_a": {...},
      "valuation_part_b": {...}
    },
    "construction_specifications": {
      "construction_part_a": {...},
      "construction_part_b": {...}
    },
    "detailed_valuation": {
      "land_total": "8000000",
      "building_total": "2500000",
      "grand_total": "10500000"
    }
  }
}
```

### ❌ Flat Fields at Root Level (PROBLEM):
```json
{
  "report_data": {
    // ... nested structure above ...
    
    // THESE SHOULD BE NESTED, NOT AT ROOT:
    "report_reference_number": "",
    "valuation_date": "2025-12-21",
    "inspection_date": "2025-12-20",
    "applicant_name": "MS SSK Developers",
    "valuation_purpose": "bank_purpose",
    "bank_branch": "sbi_mumbai_main",
    "plot_survey_no": "House No. 53A",
    "door_no": "House No. 53A",
    "ts_no_village": "Guru Nanak Enclave, Vill. Bhago Majra",
    "ward_taluka_tehsil": "Kharar",
    "mandal_district": "Mohali",
    "longitude": "NA",
    "latitude": "NA",
    "site_area": "NA",
    // ... many more flat fields that should be nested
  }
}
```

## SBI Land Template Expected Structure

According to `sbi_land_property_details.json`, the template expects:

### Proper Tab Organization:
1. **property_details** → property_part_a, property_part_b, property_part_c, property_part_d
2. **site_characteristics** → site_part_a, site_part_b  
3. **valuation** → valuation_part_a, valuation_part_b
4. **construction_specifications** → construction_part_a, construction_part_b
5. **detailed_valuation** → (no sections, direct fields)

### Field Mapping Issues:

Many fields in the report are at the **root level** but should be **nested** in specific sections:

- `plot_survey_no`, `door_no`, `ts_no_village` → should be in `property_details.property_part_b` 
- `longitude`, `latitude`, `site_area` → should be in `property_details.property_part_d`
- `locality_classification`, `surrounding_area` → should be in `site_characteristics.site_part_a`
- `road_facilities`, `road_type_present`, `road_width` → should be in `site_characteristics.site_part_b`
- `market_rate_min`, `market_rate_max`, `registrar_rate` → should be in `valuation.valuation_part_a`

## Root Cause

The issue is in the **TemplateService.organizeReportDataByTabs()** method I just added. The field mapping is **incomplete** and doesn't cover all the fields that should be properly nested.

## Solution Required

1. **Complete the field mapping** in `organizeReportDataByTabs()` method
2. **Update the field mappings** to match the SBI template structure exactly
3. **Remove default fallback** that puts unmapped fields in `detailed_valuation`
4. **Ensure all fields** go to their proper tab sections

This will fix the "absolutely wrong saving of report" issue where fields appear flattened instead of in proper nested tabs.