# Template Quick Reference

Quick reference for all migrated C# templates.

## Template Lookup

| Bank Code | Property Type | Template ID | File Name |
|-----------|--------------|-------------|-----------|
| SBI | Land | `SBI_LAND_TEMPLATE_V1` | `sbi_land_template.json` |
| SBI | Apartment | `SBI_APARTMENT_TEMPLATE_V1` | `sbi_apartment_template_v1.json` |
| BOB | Land | `BOB_LAND_TEMPLATE_V1` | `bob_land_template_v1.json` |
| BOI | Land | `BOI_LAND_TEMPLATE_V1` | `boi_land_template_v1.json` |
| BOI | Apartment | `BOI_APARTMENT_TEMPLATE_V1` | `boi_apartment_template_v1.json` |
| UCO | Land | `UCO_LAND_TEMPLATE_V1` | `uco_land_template_v1.json` |
| UCO | Apartment | `UCO_APARTMENT_TEMPLATE_V1` | `uco_apartment_template_v1.json` |
| UBI | Land | `UBI_LAND_TEMPLATE_V1` | `ubi_land_template_v1.json` |
| UBI | Apartment | `UBI_APARTMENT_TEMPLATE_V1` | `ubi_apartment_template_v1.json` |
| PNB | All | `PNB_ALL_TEMPLATE_V1` | `pnb_all_template_v1.json` |
| CBI | All | `CBI_ALL_TEMPLATE_V1` | `cbi_all_template_v1.json` |
| HDFC | All | `HDFC_ALL_TEMPLATE_V1` | `hdfc_all_template_v1.json` |

## API Query Examples

### Fetch Template by Bank & Property Type
```javascript
// MongoDB Query
db.templates.findOne({
  'BankDetails.BankCode': 'SBI',
  'PropertyType': 'Land',
  'Status': 'Active'
})
```

### Fetch All Templates for a Bank
```javascript
// MongoDB Query
db.templates.find({
  'BankDetails.BankCode': 'SBI',
  'Status': 'Active'
})
```

### Fetch Template by ID
```javascript
// MongoDB Query
db.templates.findOne({
  'TemplateId': 'SBI_LAND_TEMPLATE_V1'
})
```

## Template Structure Overview

```typescript
interface Template {
  TemplateId: string;                    // e.g., "SBI_LAND_TEMPLATE_V1"
  TemplateName: string;                  // e.g., "SBI Land Property Valuation"
  TemplateDescription: string;
  BankDetails: {
    BankCode: string;                    // e.g., "SBI"
    BankName: string;                    // e.g., "State Bank of India"
  };
  PropertyType: string;                  // "Land", "Apartment", "All"
  Elements: FieldElement[];              // Flat array with recursive containers
  CalculationRules: CalculationRule[];   // Formula definitions
  Version: string;                       // "1.0"
  Status: string;                        // "Active"
  CreatedAt: Date;
  UpdatedAt: Date;
  MigrationDate: Date;
  MigratedFrom: string;                  // "MongoDB_Legacy_Structure"
}

interface FieldElement {
  $type: 'input' | 'container' | 'table';
  FieldId: string;
  Label: string;
  DisplayOrder: number;
  IsVisible: boolean;
  // Type-specific properties...
}

interface InputField extends FieldElement {
  $type: 'input';
  SpecificType: 'Text' | 'Number' | 'Date' | 'Dropdown' | 'Radio' | 'Checkbox';
  IsRequired: boolean;
  DefaultValue?: any;
  HelpText?: string;
  PlaceholderText?: string;
  IsReadonly?: boolean;                  // True for calculated fields
  Options?: { value: string; label: string; }[];
}

interface ContainerField extends FieldElement {
  $type: 'container';
  Container: 'Tab' | 'Section' | 'Group';
  Children: FieldElement[];
}

interface TableField extends FieldElement {
  $type: 'table';
  Columns: TableColumn[];
  MinRows: number;
  ShowFooter: boolean;
  Summaries: any[];
}

interface CalculationRule {
  RuleId: string;                        // e.g., "calc_estimated_land_value"
  TriggerFieldIds: string[];             // Fields that trigger recalculation
  Formula: string;                       // e.g., "field1 * field2"
  TargetFieldId: string;                 // Field to update with result
  Description: string;
}
```

## Common Fields (Present in All Templates)

All templates include these 6 common fields at the start:

1. `report_reference_number` - Text (readonly, auto-generated)
2. `valuation_date` - Date (required)
3. `inspection_date` - Date (required)
4. `applicant_name` - Text (required)
5. `valuation_purpose` - Dropdown (required)
6. `bank_branch` - Text (required)

## Calculation Rules Summary

| Template | Calculation Rules | Formula Fields |
|----------|-------------------|----------------|
| SBI Land | 2 | `estimated_land_value` |
| SBI Apartment | 0 | None |
| BOB Land | 1 | TBD |
| BOI Land | 1 | TBD |
| BOI Apartment | 0 | None |
| UCO Land | 0 | None |
| UCO Apartment | 0 | None |
| UBI Land | 1 | TBD |
| UBI Apartment | 1 | TBD |
| PNB All | 1 | TBD |
| CBI All | 1 | TBD |
| HDFC All | 1 | TBD |

## File Paths

### Local Files
```
templates-csharp/migrated/
├── sbi_land_template.json
├── sbi_apartment_template_v1.json
├── bob_land_template_v1.json
├── boi_land_template_v1.json
├── boi_apartment_template_v1.json
├── uco_land_template_v1.json
├── uco_apartment_template_v1.json
├── ubi_land_template_v1.json
├── ubi_apartment_template_v1.json
├── pnb_all_template_v1.json
├── cbi_all_template_v1.json
└── hdfc_all_template_v1.json
```

### MongoDB
- **Database**: `valuation_templates`
- **Collection**: `templates`
- **Connection**: Use `MONGODB_URI` from `.env`

## Usage Examples

### Load Template in Frontend
```typescript
async function loadTemplate(bankCode: string, propertyType: string) {
  const response = await fetch(`/api/templates?bank=${bankCode}&type=${propertyType}`);
  const template = await response.json();
  
  // Render common fields
  const commonFields = template.Elements.filter(e => 
    e.$type === 'input' && e.DisplayOrder <= 6
  );
  
  // Render tabs
  const tabs = template.Elements.filter(e => 
    e.$type === 'container' && e.Container === 'Tab'
  );
  
  // Setup calculation rules
  template.CalculationRules.forEach(rule => {
    setupCalculation(rule);
  });
}
```

### Implement Calculation Engine
```typescript
function setupCalculation(rule: CalculationRule) {
  // Listen to trigger fields
  rule.TriggerFieldIds.forEach(fieldId => {
    document.getElementById(fieldId)?.addEventListener('change', () => {
      calculateFormula(rule);
    });
  });
}

function calculateFormula(rule: CalculationRule) {
  // Get values
  const values: Record<string, number> = {};
  rule.TriggerFieldIds.forEach(fieldId => {
    const input = document.getElementById(fieldId) as HTMLInputElement;
    values[fieldId] = parseFloat(input?.value || '0');
  });
  
  // Evaluate formula (use safe eval or expression parser)
  const result = evaluateFormula(rule.Formula, values);
  
  // Update target field
  const targetField = document.getElementById(rule.TargetFieldId) as HTMLInputElement;
  if (targetField) {
    targetField.value = result.toString();
  }
}
```

## Migration Scripts

### Re-run Individual Migration
```bash
python3 scripts/migrate_sbi_land_to_new_structure.py
```

### Re-run Batch Migration
```bash
python3 scripts/migrate_all_templates_batch.py
```

### Upload Specific Template
```bash
python3 scripts/upload_csharp_template_to_atlas.py
```

## Troubleshooting

### Template Not Found
```bash
# Check if template exists in MongoDB
python3 -c "
from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['valuation_templates']
template = db.templates.find_one({'TemplateId': 'SBI_LAND_TEMPLATE_V1'})
print('Found:' if template else 'Not found')
client.close()
"
```

### List All Templates
```bash
python3 -c "
from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['valuation_templates']
for t in db.templates.find({}, {'TemplateId': 1, '_id': 0}):
    print(t['TemplateId'])
client.close()
"
```

### Validate Template Structure
```bash
cd templates-csharp/migrated
cat sbi_land_template.json | jq '{
  TemplateId,
  Bank: .BankDetails.BankCode,
  PropertyType,
  ElementsCount: (.Elements | length),
  CalculationRulesCount: (.CalculationRules | length),
  TabsCount: [.Elements[] | select(.Container == "Tab")] | length
}'
```

## Support

For issues or questions:
1. Check `COMPLETE_MIGRATION_SUMMARY.md` for detailed documentation
2. Review `README.md` for template structure
3. Examine individual template files in `migrated/` folder
4. Check MongoDB collection: `valuation_templates.templates`
