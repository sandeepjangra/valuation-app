# Data Flow: MongoDB → Backend → Frontend

> **Complete guide to template data transformation pipeline**  
> Date: April 4, 2026  
> Component: NewReportForm (New Architecture)

---

## 📊 Overview

When you navigate to:
```
http://localhost:4200/org/system-administration/reports/create?bankCode=SBI&propertyType=land
```

The data flows through **4 major stages**:

```
MongoDB Atlas → C# Backend API → Angular TemplateService → NewReportForm Component → UI Rendering
```

---

## 🗄️ Stage 1: MongoDB Storage

### Database: `valuation_admin`
### Collection: `valuation_templates`

### Document Structure (SBI Land Template)

```javascript
{
  "_id": ObjectId("..."),
  "templateId": "SBI_LAND_TEMPLATE_V1",
  "templateName": "SBI Land Property Valuation",
  "templateDescription": "Property valuation template for land properties",
  "bankDetails": {
    "bankName": "State Bank of India",
    "bankCode": "SBI"
  },
  "propertyType": 3, // Enum: 1=House, 2=Apartment, 3=Land, 4=Commercial
  
  // ROOT LEVEL ELEMENTS ARRAY
  "elements": [
    
    // ===== COMMON FIELDS (6 fields at root level) =====
    {
      "$type": "input",
      "fieldId": "report_reference_number",
      "label": "Report Reference Number",
      "displayOrder": 1,
      "fieldType": 0, // 0=Text
      "isVisible": true,
      "specificType": 0,
      "isRequired": true,
      "isReadonly": true,
      "helpText": "Unique reference number..."
    },
    {
      "$type": "input",
      "fieldId": "valuation_date",
      "label": "Valuation Date",
      "displayOrder": 2,
      "fieldType": 2, // 2=Date
      "defaultValue": "today",
      "isRequired": true,
      "isReadonly": false
    },
    // ... 4 more common fields (inspection_date, applicant_name, valuation_purpose, bank_branch)
    
    // ===== TABGROUP CONTAINER (Bank-Specific Structure) =====
    {
      "$type": "container",
      "container": "TabGroup", // ⭐ KEY: This identifies the TabGroup
      "fieldId": "bank_specific_details",
      "label": "Bank Specific Details",
      "displayOrder": 7,
      "fieldType": 9, // 9=Container
      "isVisible": true,
      
      // CHILDREN = 5 TABS
      "children": [
        
        // ===== TAB 1: Property Details =====
        {
          "container": "Tab",
          "fieldId": "property_details",
          "label": "Property Details",
          "displayOrder": 1,
          "fieldType": 9,
          
          // TAB CHILDREN = 4 SECTIONS
          "children": [
            
            // Section: Part B - Address Details
            {
              "$type": "container",
              "container": "Section",
              "fieldId": "property_part_b",
              "label": "Part B - Address Details",
              "displayOrder": 2,
              
              // SECTION CHILDREN = FIELDS + GROUPS
              "children": [
                {
                  "$type": "input",
                  "fieldId": "owner_details",
                  "label": "Owner Details",
                  "fieldType": 0
                },
                
                // GROUP: Property Location (5 fields)
                {
                  "$type": "container",
                  "container": "Group",
                  "fieldId": "property_location",
                  "label": "Property Location",
                  "children": [
                    { "$type": "input", "fieldId": "plot_survey_no", ... },
                    { "$type": "input", "fieldId": "door_no", ... },
                    // ... 3 more fields
                  ]
                }
              ]
            },
            
            // Section: Part D - Others (Contains Boundaries Table!)
            {
              "$type": "container",
              "container": "Section",
              "fieldId": "property_part_d",
              "label": "Part D - Others",
              "displayOrder": 4,
              
              "children": [
                
                // ⭐⭐⭐ BOUNDARIES TABLE WITH PRE-FILLED ROWS ⭐⭐⭐
                {
                  "$type": "table",
                  "fieldId": "boundaries_dimensions_table",
                  "label": "Boundaries and Dimensions Table",
                  "displayOrder": 1,
                  "fieldType": 10, // 10=Table
                  "isVisible": true,
                  
                  "columns": [
                    {
                      "fieldId": "direction",
                      "label": "Direction",
                      "fieldType": 0, // Text
                      "isReadonly": true // ⭐ Direction column is readonly
                    },
                    {
                      "fieldId": "boundaries_per_documents",
                      "label": "Boundaries As Per Documents",
                      "fieldType": 0,
                      "isReadonly": false
                    },
                    {
                      "fieldId": "boundaries_actual",
                      "label": "Boundaries Actual",
                      "fieldType": 0,
                      "isReadonly": false
                    },
                    {
                      "fieldId": "dimensions_per_documents",
                      "label": "Dimensions As Per Documents",
                      "fieldType": 0, // Changed from 1 (Number) to 0 (Text) to allow "NA"
                      "isReadonly": false
                    },
                    {
                      "fieldId": "dimensions_actuals",
                      "label": "Dimensions Actuals",
                      "fieldType": 0, // Changed from 1 (Number) to 0 (Text)
                      "isReadonly": false
                    }
                  ],
                  
                  // ⭐⭐⭐ PRE-FILLED ROWS FROM MONGODB ⭐⭐⭐
                  "rows": [
                    {
                      "direction": "North",
                      "boundaries_per_documents": "",
                      "boundaries_actual": "",
                      "dimensions_per_documents": "",
                      "dimensions_actuals": ""
                    },
                    {
                      "direction": "South",
                      "boundaries_per_documents": "",
                      "boundaries_actual": "",
                      "dimensions_per_documents": "",
                      "dimensions_actuals": ""
                    },
                    {
                      "direction": "East",
                      "boundaries_per_documents": "",
                      "boundaries_actual": "",
                      "dimensions_per_documents": "",
                      "dimensions_actuals": ""
                    },
                    {
                      "direction": "West",
                      "boundaries_per_documents": "",
                      "boundaries_actual": "",
                      "dimensions_per_documents": "",
                      "dimensions_actuals": ""
                    }
                  ],
                  
                  "summaries": [],
                  "minRows": 1,
                  "allowAddRows": false,
                  "allowDeleteRows": false,
                  "showFooter": true
                }
              ]
            }
          ]
        },
        
        // ===== TAB 2: Site Characteristics =====
        // ===== TAB 3: Valuation =====
        // ===== TAB 4: Construction Specifications =====
        // ===== TAB 5: Detailed Valuation =====
        // ... (similar structure with sections, groups, fields, tables)
      ]
    }
  ],
  
  "calculationRules": [...],
  "version": "1.0",
  "status": "Active",
  "isActive": true,
  "createdAt": "2026-03-28T17:48:50.089Z",
  "updatedAt": "2026-04-03T21:13:36.063Z"
}
```

### Key Points:
- ✅ **6 common fields** at root level (outside TabGroup)
- ✅ **1 TabGroup container** with 5 Tab children
- ✅ **Boundaries table has 4 pre-filled rows** with Direction values
- ✅ **All dimension columns are Text type** (fieldType: 0) to allow "NA"
- ✅ **Direction column is readonly** (isReadonly: true)

---

## 🔌 Stage 2: C# Backend API

### File: `backend-dotnet/ValuationApp.API/Controllers/TemplatesController.cs`

### Endpoint
```
GET http://localhost:8000/api/templates/{bankCode}/{propertyType}
Example: GET http://localhost:8000/api/templates/SBI/Land
```

### Controller Action
```csharp
[HttpGet("{bankCode}/{propertyType}")]
public async Task<ActionResult<ApiResponse<AggregatedTemplateDto>>> GetAggregatedTemplateFields(
    string bankCode, 
    string propertyType)
{
    try
    {
        // Convert string to enum (e.g., "Land" -> PropertyType.Land = 3)
        if (!Enum.TryParse<PropertyType>(propertyType, ignoreCase: true, out var parsedPropertyType))
        {
            return BadRequest(ApiResponse<AggregatedTemplateDto>.Failure(
                $"Invalid property type: {propertyType}. Valid values: House, Apartment, Land, Commercial"
            ));
        }

        // Call service to get template from MongoDB
        var template = await _templateService.GetAggregatedTemplateAsync(bankCode, parsedPropertyType);
        
        if (template == null)
        {
            return NotFound(ApiResponse<AggregatedTemplateDto>.Failure(
                $"Template not found for bank {bankCode} and property type {propertyType}"
            ));
        }

        // Wrap in ApiResponse<T> and return
        return Ok(ApiResponse<AggregatedTemplateDto>.Success(
            template, 
            "Template retrieved successfully"
        ));
    }
    catch (Exception ex)
    {
        return StatusCode(500, ApiResponse<AggregatedTemplateDto>.Failure(
            "An error occurred while retrieving the template",
            ex.Message
        ));
    }
}
```

### Service Layer
**File**: `backend-dotnet/ValuationApp.Core/Services/TemplateService.cs`

```csharp
public async Task<AggregatedTemplateDto?> GetAggregatedTemplateAsync(
    string bankCode, 
    PropertyType propertyType)
{
    // Find template in MongoDB
    var filter = Builders<AggregatedTemplateDto>.Filter.And(
        Builders<AggregatedTemplateDto>.Filter.Eq("bankDetails.bankCode", bankCode),
        Builders<AggregatedTemplateDto>.Filter.Eq(t => t.PropertyType, propertyType),
        Builders<AggregatedTemplateDto>.Filter.Eq(t => t.IsActive, true)
    );

    var template = await _templatesCollection
        .Find(filter)
        .FirstOrDefaultAsync();

    return template; // Returns the template AS-IS from MongoDB (no transformation)
}
```

### API Response Format
```json
{
  "success": true,
  "message": "Template retrieved successfully",
  "data": {
    "templateId": "SBI_LAND_TEMPLATE_V1",
    "templateName": "SBI Land Property Valuation",
    "elements": [
      {
        "$type": "input",
        "fieldId": "report_reference_number",
        "label": "Report Reference Number",
        "displayOrder": 1,
        "fieldType": 0,
        "isVisible": true,
        "specificType": 0,
        "isRequired": true,
        "isReadonly": true
      },
      // ... 5 more common fields
      {
        "$type": "container",
        "container": "TabGroup",
        "fieldId": "bank_specific_details",
        "label": "Bank Specific Details",
        "displayOrder": 7,
        "fieldType": 9,
        "children": [
          // ... 5 tabs with sections, groups, fields, tables
        ]
      }
    ]
  },
  "errors": null
}
```

### Key Points:
- ✅ **No transformation** - backend returns MongoDB document structure as-is
- ✅ Wrapped in `ApiResponse<T>` with `success`, `message`, `data` properties
- ✅ **All 4 table rows are preserved** in the response
- ✅ CORS configured to allow `http://localhost:4200`

---

## 🔄 Stage 3: Frontend TemplateService (Transformation Layer)

### File: `valuation-frontend/src/app/services/template.service.ts`

This is where **ALL transformations** happen to convert backend DTO to frontend format.

### 3.1 Entry Point: `getAggregatedTemplateFields()`

```typescript
getAggregatedTemplateFields(bankCode: string, templateCode: string): Observable<AggregatedTemplateResponse> {
  // Capitalize first letter: "land" -> "Land"
  const propertyType = templateCode.charAt(0).toUpperCase() + templateCode.slice(1).toLowerCase();
  
  // Build API URL
  const url = `${this.API_BASE_URL}/templates/${bankCode}/${propertyType}`;
  // Example: http://localhost:8000/api/templates/SBI/Land
  
  console.log(`🌐 TemplateService: Making API call to ${url}`);
  
  return this.http.get<any>(url).pipe(
    map((apiResponse: any) => {
      console.log('📦 Backend API Response:', apiResponse);
      
      // Extract template data from ApiResponse wrapper
      const templateData = apiResponse.data || apiResponse;
      
      // ⭐ TRANSFORM: Backend DTO → Frontend Format
      return this.transformBackendDtoToFrontend(templateData, bankCode);
    }),
    catchError(error => {
      console.error(`❌ API call failed for ${bankCode}/${propertyType}:`, error);
      return throwError(() => error);
    })
  );
}
```

### 3.2 Main Transformation: `transformBackendDtoToFrontend()`

```typescript
private transformBackendDtoToFrontend(templateDto: any, bankCode: string): AggregatedTemplateResponse {
  console.log('🔄 Transforming backend DTO to frontend format');
  
  const elements = templateDto.elements || [];
  
  // Initialize result arrays
  const commonFields: TemplateField[] = [];
  const bankSpecificTabs: BankSpecificTab[] = [];
  
  // ⭐ LOOP THROUGH ROOT-LEVEL ELEMENTS
  elements.forEach((element: any, index: number) => {
    console.log(`🔍 Element ${index}: $type=${element.$type}, container=${element.container}, fieldId=${element.fieldId}`);
    
    // ===== DETECT TABGROUP =====
    if (element.$type === 'container' && element.container === 'TabGroup') {
      console.log(`📂 Found TabGroup: ${element.fieldId} - ${element.label}`);
      
      const tabs = element.children || [];
      
      // ⭐ TRANSFORM EACH TAB
      tabs.forEach((tab: any) => {
        console.log(`  📁 Processing Tab: ${tab.fieldId} - ${tab.label}`);
        const transformedTab = this.transformContainerToTab(tab);
        bankSpecificTabs.push(transformedTab);
      });
    }
    
    // ===== DETECT COMMON FIELDS (non-container at root level) =====
    else if (element.$type === 'input' || element.$type === 'table' || element.$type === 'attachment') {
      console.log(`📄 Found common field: ${element.fieldId} - ${element.label}`);
      const field = this.transformElementToField(element, true); // true = isCommonField
      commonFields.push(field);
    }
    
    else {
      console.warn('⚠️ Unknown element type at root level:', element.$type, element);
    }
  });
  
  console.log(`✅ Transformed ${commonFields.length} common fields and ${bankSpecificTabs.length} bank-specific tabs`);
  
  // ⭐ RETURN FRONTEND FORMAT
  return {
    templateInfo: {
      templateId: templateDto.templateId,
      templateName: templateDto.templateName,
      propertyType: this.mapBackendPropertyTypeToFrontend(templateDto.propertyType),
      bankCode: bankCode,
      bankName: templateDto.bankDetails?.bankName || bankCode,
      version: '1.0'
    },
    commonFields: commonFields,           // Array of TemplateField
    bankSpecificTabs: bankSpecificTabs,   // Array of BankSpecificTab
    documentTypes: [],
    aggregatedAt: new Date().toISOString()
  };
}
```

### 3.3 Tab Transformation: `transformContainerToTab()`

```typescript
private transformContainerToTab(container: any): BankSpecificTab {
  const children = container.children || [];
  
  const directFields: TemplateField[] = [];
  const sections: BankSpecificSection[] = [];
  
  // ⭐ PROCESS TAB CHILDREN
  children.forEach((child: any) => {
    console.log(`  🔍 Tab child: $type=${child.$type}, container=${child.container}, fieldId=${child.fieldId}`);
    
    // SECTION CONTAINER
    if (child.$type === 'container' && child.container === 'Section') {
      console.log(`    📑 Processing section: ${child.fieldId}`);
      sections.push(this.transformContainerToSection(child));
    }
    
    // GROUP CONTAINER (treat as section at tab level)
    else if (child.$type === 'container' && child.container === 'Group') {
      console.log(`    📦 Processing group as section: ${child.fieldId}`);
      sections.push(this.transformGroupToField(child));
    }
    
    // TABLE ELEMENT
    else if (child.$type === 'table') {
      console.log(`    📊 Processing table: ${child.fieldId}`);
      directFields.push(this.transformTableToField(child));
    }
    
    // REGULAR FIELD
    else {
      console.log(`    📄 Processing direct field: ${child.fieldId}`);
      directFields.push(this.transformElementToField(child, false));
    }
  });
  
  console.log(`  ✅ Tab ${container.fieldId}: ${directFields.length} direct fields, ${sections.length} sections`);
  
  return {
    tabId: container.fieldId,
    tabName: container.label || this.formatFieldName(container.fieldId),
    sortOrder: container.displayOrder || 0,
    fields: directFields,
    sections: sections,
    hasSections: sections.length > 0
  };
}
```

### 3.4 Section Transformation: `transformContainerToSection()`

```typescript
private transformContainerToSection(container: any): BankSpecificSection {
  const children = container.children || [];
  const fields: any[] = [];
  
  children.forEach((child: any) => {
    console.log(`      🔍 Section child: $type=${child.$type}, fieldId=${child.fieldId}`);
    
    // GROUP WITHIN SECTION
    if (child.$type === 'container' && child.container === 'Group') {
      console.log(`        📦 Processing group: ${child.fieldId}`);
      fields.push(this.transformGroupToField(child));
    }
    
    // TABLE WITHIN SECTION
    else if (child.$type === 'table') {
      console.log(`        📊 Processing table: ${child.fieldId}`);
      fields.push(this.transformTableToField(child));
    }
    
    // REGULAR FIELD
    else {
      console.log(`        📄 Processing field: ${child.fieldId}`);
      fields.push(this.transformElementToField(child, false));
    }
  });
  
  console.log(`      ✅ Section ${container.fieldId}: ${fields.length} fields`);
  
  return {
    sectionId: container.fieldId,
    sectionName: container.label || this.formatFieldName(container.fieldId),
    sortOrder: container.displayOrder || 0,
    fields: fields
  };
}
```

### 3.5 ⭐⭐⭐ TABLE TRANSFORMATION (CRITICAL!) ⭐⭐⭐

```typescript
private transformTableToField(table: any): any {
  const fieldLabel = table.label || this.formatFieldName(table.fieldId);
  
  // ⭐ TRANSFORM COLUMNS
  const columns = (table.columns || []).map((col: any) => ({
    fieldId: col.fieldId,
    label: col.label,
    fieldType: this.mapBackendFieldTypeToFrontend(col.fieldType, 'input'),
    width: col.width || null,
    isReadonly: col.isReadonly || false,
    options: col.options ? this.transformOptions(col.options) : null,
    validationRules: col.validationRules || null
  }));
  
  // ⭐⭐⭐ PRESERVE ROWS FROM API ⭐⭐⭐
  let rows = table.rows || [];
  const minRows = table.minRows || 1;
  
  // IMPORTANT: Only create empty rows if API didn't provide any
  if (rows.length === 0 && minRows > 0) {
    rows = Array.from({ length: minRows }, () => {
      const row: any = {};
      columns.forEach((col: any) => {
        row[col.fieldId] = '';
      });
      return row;
    });
    console.log(`📊 Table ${table.fieldId}: Created ${minRows} empty rows`);
  } else {
    console.log(`📊 Table ${table.fieldId}: Using ${rows.length} rows from API`);
  }
  
  return {
    fieldId: table.fieldId,
    label: fieldLabel,
    uiDisplayName: fieldLabel,
    fieldType: 'table',
    displayOrder: table.displayOrder || 0,
    sortOrder: table.displayOrder || 0,
    isRequired: false,
    isReadonly: false,
    isVisible: table.isVisible !== false,
    columns: columns,
    rows: rows,  // ⭐⭐⭐ ROWS PRESERVED HERE! ⭐⭐⭐
    minRows: minRows,
    maxRows: table.maxRows || undefined,
    allowAddRows: table.allowAddRows !== false,
    allowDeleteRows: table.allowDeleteRows !== false,
    showFooter: table.showFooter !== false,
    gridSize: 12  // Full width
  };
}
```

### 3.6 Field Type Mapping

```typescript
private mapBackendFieldTypeToFrontend(backendFieldType: number, discriminator: string): string {
  // Use $type discriminator for base type
  if (discriminator === 'table') return 'table';
  if (discriminator === 'container') return 'container';
  if (discriminator === 'attachment') return 'attachment';
  
  // Map input field types (fieldType enum from backend)
  const fieldTypeMap: { [key: number]: string } = {
    0: 'text',       // Text
    1: 'number',     // Number  
    2: 'date',       // Date
    3: 'select',     // Dropdown
    4: 'textarea',   // TextArea
    5: 'currency',   // Currency
    6: 'checkbox',   // Checkbox
    7: 'radio',      // Radio
    8: 'email',      // Email
    9: 'phone',      // Phone
    10: 'url',       // Url
    11: 'file'       // File
  };
  
  return fieldTypeMap[backendFieldType] || 'text';
}
```

### Output Format (AggregatedTemplateResponse)

```typescript
interface AggregatedTemplateResponse {
  templateInfo: {
    templateId: string;
    templateName: string;
    propertyType: string;  // "land", "apartment", etc.
    bankCode: string;
    bankName: string;
    version: string;
  };
  
  // ⭐ 6 COMMON FIELDS (flattened from root elements)
  commonFields: TemplateField[];  // Array of 6 fields
  
  // ⭐ 5 BANK-SPECIFIC TABS (from TabGroup children)
  bankSpecificTabs: BankSpecificTab[];  // Array of 5 tabs
  
  documentTypes: any[];
  aggregatedAt: string;
}

interface BankSpecificTab {
  tabId: string;
  tabName: string;
  sortOrder: number;
  fields: TemplateField[];          // Direct fields in tab (rare)
  sections: BankSpecificSection[];  // Sections within tab
  hasSections: boolean;
}

interface BankSpecificSection {
  sectionId: string;
  sectionName: string;
  sortOrder: number;
  fields: any[];  // Can be TemplateField, Group, Table, or nested Section
}

interface TemplateField {
  fieldId: string;
  label: string;
  uiDisplayName: string;
  fieldType: string;  // 'text', 'number', 'date', 'table', etc.
  displayOrder: number;
  sortOrder: number;
  isRequired: boolean;
  isReadonly: boolean;
  isVisible: boolean;
  
  // Table-specific
  columns?: any[];
  rows?: Record<string, any>[];  // ⭐ PRE-FILLED ROWS HERE!
  
  // Group-specific
  subFields?: TemplateField[];
  
  // Other properties...
}
```

### Key Transformations:
1. ✅ **Root elements separated** into `commonFields` vs `bankSpecificTabs`
2. ✅ **TabGroup children** → `bankSpecificTabs` array
3. ✅ **Tab children** → separated into `fields` (direct) and `sections`
4. ✅ **Section children** → flattened into `fields` array (can be inputs, tables, groups)
5. ✅ **Table rows preserved** from API (`table.rows` → output `rows` property)
6. ✅ **Field types mapped** from enum numbers to strings ('text', 'select', etc.)
7. ✅ **Container types detected** via `container` property ('TabGroup', 'Tab', 'Section', 'Group')

---

## 🎯 Stage 4: NewReportForm Component

### File: `valuation-frontend/src/app/components/new-report-form/new-report-form.ts`

### 4.1 Component Initialization

```typescript
export class NewReportForm implements OnInit {
  template: ValuationTemplate | null = null;  // ⭐ Template data
  isLoading = true;
  errorMessage: string | null = null;
  
  form: FormGroup = new FormGroup({});
  tableRows: { [tableId: string]: any[] } = {};  // ⭐ Table rows storage
  collapsedMap: { [fieldId: string]: boolean } = {};
  
  constructor(
    private templateService: TemplateService,
    private route: ActivatedRoute
  ) {}
  
  ngOnInit() {
    // ⭐ GET QUERY PARAMS
    this.route.queryParams.subscribe(params => {
      const bankCode = params['bankCode'] || 'SBI';
      const propertyType = params['propertyType'] || 'land';
      
      console.log('🔄 NewReportForm: Loading template', { bankCode, propertyType });
      
      // ⭐ LOAD TEMPLATE FROM API
      this.loadTemplate(bankCode, propertyType);
    });
  }
}
```

### 4.2 Load Template from API

```typescript
private loadTemplate(bankCode: string, propertyType: string) {
  this.isLoading = true;
  this.errorMessage = null;

  // ⭐ CALL TEMPLATESERVICE (which calls backend and transforms)
  this.templateService.getAggregatedTemplateFields(bankCode, propertyType).subscribe({
    next: (response) => {
      console.log('✅ Template loaded successfully', response);
      
      // ⭐ CONVERT API RESPONSE TO VALUATION TEMPLATE FORMAT
      this.template = this.convertApiResponseToTemplate(response);
      
      // ⭐ BUILD FORM CONTROLS
      this.buildFormControls(this.template.elements);
      
      // ⭐ COLLECT TABLE ROWS (including pre-filled ones)
      this.collectTables(this.template.elements);
      
      // Initialize collapsed state for sections
      this.initCollapsedState(this.template.elements);
      
      this.isLoading = false;
      console.log('✅ Template ready for rendering', this.template);
    },
    error: (error) => {
      console.error('❌ Failed to load template:', error);
      this.errorMessage = 'Failed to load template. Please try again.';
      this.isLoading = false;
    }
  });
}
```

### 4.3 Convert to ValuationTemplate Format

```typescript
private convertApiResponseToTemplate(apiResponse: AggregatedTemplateResponse): ValuationTemplate {
  const elements: BaseField[] = [];
  
  // ⭐ ADD COMMON FIELDS (6 fields at top)
  if (apiResponse.commonFields && apiResponse.commonFields.length > 0) {
    apiResponse.commonFields.forEach((field: any) => {
      elements.push(this.convertFieldToBaseField(field));
    });
  }
  
  // ⭐ ADD BANK-SPECIFIC TABS AS TABGROUP
  if (apiResponse.bankSpecificTabs && apiResponse.bankSpecificTabs.length > 0) {
    const tabGroupChildren: TabField[] = [];
    
    // ⭐ LOOP THROUGH TABS (5 tabs)
    apiResponse.bankSpecificTabs.forEach((tab: any) => {
      const tabChildren: BaseField[] = [];
      
      // Process tab-level fields (rare)
      if (tab.fields && tab.fields.length > 0) {
        tab.fields.forEach((field: any) => {
          tabChildren.push(this.convertFieldToBaseField(field));
        });
      }
      
      // ⭐ PROCESS SECTIONS (most content is here)
      if (tab.sections && tab.sections.length > 0) {
        tab.sections.forEach((section: any) => {
          const sectionChildren: BaseField[] = [];
          
          // Process section fields
          if (section.fields && section.fields.length > 0) {
            section.fields.forEach((field: any) => {
              sectionChildren.push(this.convertFieldToBaseField(field));
            });
          }
          
          // Create Section container
          const sectionField: SectionField = {
            $type: 'container',
            fieldId: section.sectionId,
            container: ContainerTypeDto.Section,
            children: sectionChildren,
            label: section.sectionName,
            displayOrder: section.sortOrder,
            fieldType: FieldTypeDto.Container,
            isVisible: true,
            isCollapsible: true,
            isCollapsed: false
          };
          
          tabChildren.push(sectionField);
        });
      }
      
      // Create Tab container
      const tabField: TabField = {
        $type: 'container',
        fieldId: tab.tabId,
        container: ContainerTypeDto.Tab,
        children: tabChildren,
        label: tab.tabName,
        displayOrder: tab.sortOrder,
        fieldType: FieldTypeDto.Tab,
        isVisible: true
      };
      
      tabGroupChildren.push(tabField);
    });
    
    // Create TabGroup container
    const tabGroup: TabsField = {
      $type: 'container',
      fieldId: 'bank_specific_details',
      container: ContainerTypeDto.TabGroup,
      children: tabGroupChildren
    };
    
    elements.push(tabGroup);
  }
  
  return {
    templateId: apiResponse.templateInfo.templateId,
    templateName: apiResponse.templateInfo.templateName,
    propertyType: apiResponse.templateInfo.propertyType,
    elements: elements,  // ⭐ FINAL STRUCTURE: [6 common fields, 1 TabGroup with 5 tabs]
    bankDetails: {
      bankCode: apiResponse.templateInfo.bankCode,
      bankName: apiResponse.templateInfo.bankName
    }
  };
}
```

### 4.4 ⭐⭐⭐ Collect Table Rows (CRITICAL!) ⭐⭐⭐

```typescript
private collectTables(fields: BaseField[]) {
  for (const field of fields) {
    
    // ⭐ FOUND A TABLE!
    if (field.$type === 'table') {
      const t = field as TableField;
      
      // ⭐⭐⭐ USE ROWS FROM API IF AVAILABLE ⭐⭐⭐
      if (t.rows && t.rows.length > 0) {
        this.tableRows[t.fieldId] = t.rows;
        console.log(`📊 Table ${t.fieldId}: Using ${t.rows.length} rows from API`, t.rows);
      } else {
        // Create empty rows if API didn't provide any
        this.tableRows[t.fieldId] = Array.from({ length: t.minRows }, () =>
          Object.fromEntries(t.columns.map(c => [c.fieldId, '']))
        );
        console.log(`📊 Table ${t.fieldId}: Created ${t.minRows} empty rows`);
      }
    }
    
    // ⭐ RECURSE INTO CONTAINERS (Tab, Section, Group)
    else if (field.$type === 'container') {
      const container = field as any;
      if (container.children && Array.isArray(container.children)) {
        this.collectTables(container.children);  // Recursive call
      }
    }
  }
}
```

### 4.5 Build Form Controls

```typescript
private buildFormControls(fields: BaseField[]) {
  fields.forEach(field => {
    
    // INPUT FIELD
    if (field.$type === 'input') {
      const inputField = field as InputField;
      const validators = [];
      
      if (inputField.isRequired) {
        validators.push(Validators.required);
      }
      
      const control = new FormControl(
        { value: inputField.defaultValue || '', disabled: inputField.isReadonly },
        validators
      );
      
      this.form.addControl(inputField.fieldId, control);
      console.log(`📝 Created FormControl for: ${inputField.fieldId}`);
    }
    
    // TABLE FIELD (FormArray for table data is NOT created here)
    // Table data is stored in this.tableRows[tableId] instead
    
    // CONTAINER (recurse into children)
    else if (field.$type === 'container') {
      const container = field as any;
      if (container.children) {
        this.buildFormControls(container.children);
      }
    }
  });
}
```

---

## 🎨 Stage 5: UI Rendering

### File: `valuation-frontend/src/app/components/new-report-form/new-report-form.html`

### Main Template Structure

```html
<div class="report-form-container">
  
  <!-- ⭐ LOADING STATE -->
  <div *ngIf="isLoading" class="loading-container">
    <div class="spinner"></div>
    <p>Loading template...</p>
  </div>

  <!-- ⭐ ERROR STATE -->
  <div *ngIf="errorMessage && !isLoading" class="error-container">
    <p class="error-message">{{ errorMessage }}</p>
    <button (click)="ngOnInit()">Retry</button>
  </div>

  <!-- ⭐ TEMPLATE LOADED - RENDER FORM -->
  <ng-container *ngIf="!isLoading && !errorMessage && template">
    
    <!-- Header -->
    <div class="form-header">
      <div class="header-meta">
        <span class="bank-badge">{{ template.bankDetails.bankCode }}</span>
        <span class="template-name">{{ template.templateName }}</span>
      </div>
      <button class="submit-btn" (click)="onSubmit()">Submit Report</button>
    </div>

    <!-- ⭐ FORM FIELDS -->
    <form [formGroup]="form" (ngSubmit)="onSubmit()" novalidate>
      
      <!-- ⭐ LOOP THROUGH ELEMENTS (6 common fields + 1 TabGroup) -->
      <app-form-field
        *ngFor="let element of template.elements"
        [field]="element"
        [form]="form"
        [tableRows]="tableRows"
        [collapsedMap]="collapsedMap">
      </app-form-field>
      
    </form>
  </ng-container>

</div>
```

### File: `valuation-frontend/src/app/components/form-field/form-field.component.ts`

This component **routes** to specific sub-components based on field type.

```typescript
@Component({
  selector: 'app-form-field',
  template: `
    <!-- ⭐ INPUT FIELD -->
    <app-input-field
      *ngIf="field.$type === 'input'"
      [field]="field"
      [form]="form">
    </app-input-field>

    <!-- ⭐ TABLE FIELD -->
    <app-table-field
      *ngIf="field.$type === 'table'"
      [field]="field"
      [rows]="tableRows[field.fieldId] || []">
    </app-table-field>

    <!-- ⭐ TABS FIELD (TabGroup with 5 tabs) -->
    <app-tabs-field
      *ngIf="field.$type === 'container' && field.container === 'TabGroup'"
      [field]="field"
      [form]="form"
      [tableRows]="tableRows"
      [collapsedMap]="collapsedMap">
    </app-tabs-field>

    <!-- ⭐ SECTION FIELD -->
    <app-section-field
      *ngIf="field.$type === 'container' && field.container === 'Section'"
      [field]="field"
      [form]="form"
      [tableRows]="tableRows"
      [collapsedMap]="collapsedMap">
    </app-section-field>

    <!-- ⭐ GROUP FIELD -->
    <app-group-field
      *ngIf="field.$type === 'container' && field.container === 'Group'"
      [field]="field"
      [form]="form"
      [tableRows]="tableRows"
      [collapsedMap]="collapsedMap">
    </app-group-field>
  `
})
export class FormFieldComponent {
  @Input() field!: BaseField;
  @Input() form!: FormGroup;
  @Input() tableRows!: { [tableId: string]: any[] };
  @Input() collapsedMap!: { [fieldId: string]: boolean };
}
```

### File: `valuation-frontend/src/app/components/table-field/table-field.component.ts`

Renders the boundaries table with 4 pre-filled rows.

```typescript
@Component({
  selector: 'app-table-field',
  template: `
    <div class="table-field">
      <label>{{ field.label }}</label>
      
      <table class="data-table">
        <thead>
          <tr>
            <!-- ⭐ COLUMN HEADERS -->
            <th *ngFor="let col of field.columns">{{ col.label }}</th>
          </tr>
        </thead>
        <tbody>
          <!-- ⭐ TABLE ROWS (4 rows for boundaries table) -->
          <tr *ngFor="let row of rows; let i = index">
            <td *ngFor="let col of field.columns">
              
              <!-- ⭐ READONLY CELL (Direction column) -->
              <span *ngIf="col.isReadonly" class="readonly-cell">
                {{ row[col.fieldId] }}
              </span>
              
              <!-- ⭐ EDITABLE CELL (Other columns) -->
              <input
                *ngIf="!col.isReadonly"
                type="text"
                [(ngModel)]="row[col.fieldId]"
                [placeholder]="col.label"
                class="table-input">
              
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  `
})
export class TableFieldComponent {
  @Input() field!: TableField;
  @Input() rows!: any[];  // ⭐ PRE-FILLED ROWS PASSED HERE!
}
```

---

## 📝 Summary: Complete Data Flow

### Step-by-Step Journey

```
1. User navigates to: /org/system-administration/reports/create?bankCode=SBI&propertyType=land

2. NewReportForm.ngOnInit() extracts query params:
   - bankCode = "SBI"
   - propertyType = "land"

3. NewReportForm calls: templateService.getAggregatedTemplateFields("SBI", "land")

4. TemplateService makes HTTP call:
   GET http://localhost:8000/api/templates/SBI/Land

5. Backend TemplatesController receives request:
   - Converts "Land" → PropertyType.Land (enum = 3)
   - Calls TemplateService.GetAggregatedTemplateAsync()

6. Backend TemplateService queries MongoDB:
   - Collection: valuation_templates
   - Filter: bankCode="SBI" AND propertyType=3 AND isActive=true
   - Returns: Raw document (no transformation)

7. Backend wraps response in ApiResponse<T>:
   {
     success: true,
     message: "Template retrieved successfully",
     data: { ...MongoDB document... }
   }

8. Frontend TemplateService receives response:
   - Extracts apiResponse.data
   - Calls transformBackendDtoToFrontend()

9. transformBackendDtoToFrontend() processes elements:
   - Detects 6 common fields at root → commonFields array
   - Detects 1 TabGroup container → loops through 5 Tab children
   - For each Tab: loops through Sections
   - For each Section: loops through Fields/Groups/Tables
   - For boundaries_dimensions_table:
     * Transforms columns
     * Preserves rows array (4 rows with Direction values)
   - Returns AggregatedTemplateResponse with:
     * commonFields: [6 fields]
     * bankSpecificTabs: [5 tabs with sections]

10. NewReportForm.convertApiResponseToTemplate():
    - Converts commonFields → InputField objects
    - Converts bankSpecificTabs → TabGroup container with Tab children
    - Each Tab contains Section children
    - Each Section contains Field/Group/Table children
    - Returns ValuationTemplate with elements array

11. NewReportForm.collectTables() recursively finds all tables:
    - Finds boundaries_dimensions_table
    - Checks if table.rows exists and has length > 0
    - YES! → stores in this.tableRows['boundaries_dimensions_table'] = [4 rows]
    - Logs: "📊 Table boundaries_dimensions_table: Using 4 rows from API"

12. NewReportForm.buildFormControls():
    - Creates FormControl for each input field
    - Does NOT create FormArray for tables (uses this.tableRows instead)

13. HTML template renders:
    - Shows loading spinner while isLoading=true
    - When template loads: isLoading=false, template exists
    - Loops through template.elements (6 common fields + 1 TabGroup)
    - Passes field, form, tableRows, collapsedMap to <app-form-field>

14. FormFieldComponent routes based on field.$type:
    - 6 common fields → <app-input-field>
    - 1 TabGroup → <app-tabs-field>

15. TabsFieldComponent renders 5 tabs:
    - Creates tab buttons (Property Details, Site Characteristics, etc.)
    - Loops through field.children (5 TabField objects)
    - For each tab: loops through tab.children (Section objects)
    - Passes each section to <app-section-field>

16. SectionFieldComponent renders section:
    - Shows section header (e.g., "Part D - Others")
    - Loops through section.children
    - Finds boundaries_dimensions_table (TableField)
    - Passes to <app-table-field> with:
      * field = TableField object
      * rows = this.tableRows['boundaries_dimensions_table'] (4 rows!)

17. TableFieldComponent renders table:
    - Loops through field.columns (5 columns)
    - Renders column headers
    - Loops through rows (4 rows)
    - For each cell:
      * If col.isReadonly=true (Direction column):
        Shows <span> with row[col.fieldId] = "North", "South", "East", "West"
      * If col.isReadonly=false (other 4 columns):
        Shows <input> with [(ngModel)]="row[col.fieldId]"
    - User can now enter data in editable cells!

18. ✅ RESULT: User sees form with:
    - 6 common fields at top
    - 5 tabs below
    - Property Details → Part D → Boundaries table
    - Table has 5 columns, 4 rows
    - Direction column shows North/South/East/West (readonly)
    - Other 4 columns are editable text inputs
```

---

## 🔑 Key Files Reference

### Backend Files

| File | Purpose |
|------|---------|
| `backend-dotnet/ValuationApp.API/Controllers/TemplatesController.cs` | API endpoint `/api/templates/{bankCode}/{propertyType}` |
| `backend-dotnet/ValuationApp.Core/Services/TemplateService.cs` | MongoDB query logic |
| `backend-dotnet/ValuationApp.Core/DTOs/AggregatedTemplateDto.cs` | Template data structure (matches MongoDB) |
| `backend-dotnet/ValuationApp.API/Program.cs` | CORS configuration, MongoDB connection |

### Frontend Files

| File | Purpose |
|------|---------|
| `valuation-frontend/src/app/services/template.service.ts` | **🔥 ALL TRANSFORMATIONS HAPPEN HERE** |
| `valuation-frontend/src/app/components/new-report-form/new-report-form.ts` | Main form component, loads template, converts to ValuationTemplate format |
| `valuation-frontend/src/app/components/new-report-form/new-report-form.html` | Main form HTML, shows loading/error states |
| `valuation-frontend/src/app/components/form-field/form-field.component.ts` | Router component (switches based on field.$type) |
| `valuation-frontend/src/app/components/input-field/input-field.component.ts` | Renders text/number/date/select inputs |
| `valuation-frontend/src/app/components/table-field/table-field.component.ts` | **Renders tables with pre-filled rows** |
| `valuation-frontend/src/app/components/tabs-field/tabs-field.component.ts` | Renders tab navigation and tab content |
| `valuation-frontend/src/app/components/section-field/section-field.component.ts` | Renders section headers and section fields |
| `valuation-frontend/src/app/components/group-field/group-field.component.ts` | Renders grouped fields |
| `valuation-frontend/src/app/models/valuation-template.model.ts` | TypeScript interfaces (ValuationTemplate, BaseField, TableField, etc.) |
| `valuation-frontend/src/app/models/index.ts` | Interface definitions (AggregatedTemplateResponse, BankSpecificTab, etc.) |
| `valuation-frontend/src/environments/environment.ts` | API URL configuration |
| `valuation-frontend/src/app/app.routes.ts` | Route configuration (reports/create → NewReportForm) |

---

## 🐛 Common Issues & Solutions

### Issue 1: Blank Table (No Rows Showing)

**Symptom**: Table shows headers but no rows

**Root Cause**: `table.rows` not preserved during transformation

**Solution**: Check these points:
1. ✅ MongoDB has `rows` array in table object
2. ✅ `transformTableToField()` preserves `rows` property
3. ✅ `collectTables()` uses `t.rows` if available
4. ✅ `<app-table-field>` receives `[rows]="tableRows[field.fieldId]"`

### Issue 2: Loading Spinner Stuck

**Symptom**: Page shows "Loading template..." forever

**Root Causes**:
1. Backend API not running
2. CORS error blocking request
3. API returns 404/500 error
4. Component never sets `isLoading=false`

**Debug Steps**:
1. Check backend: `curl http://localhost:8000/api/templates/SBI/Land`
2. Check browser console for errors
3. Check Network tab for failed requests
4. Add console.log in `.subscribe({ next: ...})` to see if callback fires

### Issue 3: Direction Column Not Readonly

**Symptom**: Can edit Direction values (North/South/East/West)

**Root Cause**: `col.isReadonly` not set in MongoDB or not checked in HTML

**Solution**:
1. ✅ MongoDB column has `"isReadonly": true`
2. ✅ HTML checks `*ngIf="col.isReadonly"` for readonly span
3. ✅ HTML checks `*ngIf="!col.isReadonly"` for input

### Issue 4: Dimension Columns Show Number Inputs

**Symptom**: Can't enter "NA" in dimension columns (only numbers allowed)

**Root Cause**: Column `fieldType` is `1` (Number) instead of `0` (Text)

**Solution**:
1. ✅ Update MongoDB: Change `fieldType: 1` → `fieldType: 0`
2. ✅ Refresh template in database
3. ✅ Hard refresh browser (`Cmd+Shift+R`)

---

## 📊 Data Structure Comparison

### MongoDB Structure
```
elements: [
  { $type: 'input', fieldId: 'report_reference_number', ... },
  { $type: 'input', fieldId: 'valuation_date', ... },
  { $type: 'input', fieldId: 'inspection_date', ... },
  { $type: 'input', fieldId: 'applicant_name', ... },
  { $type: 'input', fieldId: 'valuation_purpose', ... },
  { $type: 'input', fieldId: 'bank_branch', ... },
  {
    $type: 'container',
    container: 'TabGroup',
    fieldId: 'bank_specific_details',
    children: [
      { container: 'Tab', fieldId: 'property_details', children: [...] },
      { container: 'Tab', fieldId: 'site_characteristics', children: [...] },
      { container: 'Tab', fieldId: 'valuation', children: [...] },
      { container: 'Tab', fieldId: 'construction_specifications', children: [...] },
      { container: 'Tab', fieldId: 'detailed_valuation', children: [...] }
    ]
  }
]
```

### After TemplateService Transformation (AggregatedTemplateResponse)
```typescript
{
  templateInfo: { ... },
  commonFields: [
    { fieldId: 'report_reference_number', ... },
    { fieldId: 'valuation_date', ... },
    { fieldId: 'inspection_date', ... },
    { fieldId: 'applicant_name', ... },
    { fieldId: 'valuation_purpose', ... },
    { fieldId: 'bank_branch', ... }
  ],
  bankSpecificTabs: [
    {
      tabId: 'property_details',
      tabName: 'Property Details',
      fields: [],
      sections: [
        { sectionId: 'property_part_b', fields: [...] },
        { sectionId: 'property_part_c', fields: [...] },
        { sectionId: 'property_part_d', fields: [
            { fieldId: 'boundaries_dimensions_table', rows: [4 rows], ... }
          ]
        }
      ]
    },
    { tabId: 'site_characteristics', ... },
    { tabId: 'valuation', ... },
    { tabId: 'construction_specifications', ... },
    { tabId: 'detailed_valuation', ... }
  ]
}
```

### After NewReportForm Conversion (ValuationTemplate)
```typescript
{
  templateId: 'SBI_LAND_TEMPLATE_V1',
  templateName: 'SBI Land Property Valuation',
  elements: [
    { $type: 'input', fieldId: 'report_reference_number', ... },
    { $type: 'input', fieldId: 'valuation_date', ... },
    { $type: 'input', fieldId: 'inspection_date', ... },
    { $type: 'input', fieldId: 'applicant_name', ... },
    { $type: 'input', fieldId: 'valuation_purpose', ... },
    { $type: 'input', fieldId: 'bank_branch', ... },
    {
      $type: 'container',
      container: 'TabGroup',
      children: [
        {
          $type: 'container',
          container: 'Tab',
          fieldId: 'property_details',
          children: [
            {
              $type: 'container',
              container: 'Section',
              fieldId: 'property_part_d',
              children: [
                {
                  $type: 'table',
                  fieldId: 'boundaries_dimensions_table',
                  columns: [5 columns],
                  rows: [
                    { direction: 'North', boundaries_per_documents: '', ... },
                    { direction: 'South', boundaries_per_documents: '', ... },
                    { direction: 'East', boundaries_per_documents: '', ... },
                    { direction: 'West', boundaries_per_documents: '', ... }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

---

## ✅ Verification Checklist

### Backend Verification
```bash
# 1. Check backend is running
curl http://localhost:8000/health

# 2. Test template API
curl http://localhost:8000/api/templates/SBI/Land | jq '.success'
# Expected: true

# 3. Check boundaries table has 4 rows
curl -s http://localhost:8000/api/templates/SBI/Land | \
  jq '.. | objects | select(.fieldId? == "boundaries_dimensions_table") | .rows | length'
# Expected: 4

# 4. Check Direction column is readonly
curl -s http://localhost:8000/api/templates/SBI/Land | \
  jq '.. | objects | select(.fieldId? == "boundaries_dimensions_table") | .columns[0].isReadonly'
# Expected: true
```

### Frontend Verification
1. Open browser: `http://localhost:4200/org/system-administration/reports/create?bankCode=SBI&propertyType=land`
2. Open DevTools Console (`F12` or `Cmd+Option+I`)
3. Look for these logs:
   ```
   🌐 TemplateService: Making API call to http://localhost:8000/api/templates/SBI/Land
   📦 Backend API Response: {...}
   🔄 Transforming backend DTO to frontend format
   📂 Found TabGroup: bank_specific_details - Bank Specific Details
     📁 Processing Tab: property_details - Property Details
       📑 Processing section: property_part_d
         📊 Processing table: boundaries_dimensions_table
   ✅ Transformed 6 common fields and 5 bank-specific tabs
   📊 Table boundaries_dimensions_table: Using 4 rows from API
   ✅ Template ready for rendering
   ```
4. Navigate to: Property Details tab → Part D section
5. Verify:
   - ✅ Table shows 5 column headers
   - ✅ Table shows 4 rows
   - ✅ Direction column shows North/South/East/West (readonly)
   - ✅ Other 4 columns are editable
   - ✅ Can enter "NA" in dimension columns

---

## 🎓 Conclusion

This document provides a complete, detailed walkthrough of the data flow from MongoDB to the rendered UI. The key transformation happens in `template.service.ts`, which converts the flat MongoDB structure into a hierarchical frontend format suitable for the component-based UI architecture.

**Most Important Files**:
1. `template.service.ts` - **ALL transformations**
2. `new-report-form.ts` - Template loading and conversion
3. `table-field.component.ts` - Table rendering with pre-filled rows

**Most Important Transformation**:
- `transformTableToField()` - Preserves `table.rows` array from API
- `collectTables()` - Stores rows in `this.tableRows[tableId]` for rendering

**Data Preservation**:
- ✅ MongoDB → Backend: No transformation (returns as-is)
- ✅ Backend → TemplateService: Transforms structure, **preserves table.rows**
- ✅ TemplateService → NewReportForm: Converts format, **preserves table.rows**
- ✅ NewReportForm → UI: Passes rows to components, **renders all 4 rows**

---

*End of Document*
