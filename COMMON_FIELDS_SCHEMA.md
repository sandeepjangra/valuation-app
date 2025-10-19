# 🗄️ MongoDB Collection Design - Common Fields

## **Collection: `common_form_fields`**

This collection will store the standardized field definitions that are common across all valuation reports, regardless of bank or property type.

### **Document Structure:**

```json
{
  "_id": ObjectId("..."),
  "fieldId": "report_date",
  "fieldGroup": "basic_info",
  "technicalName": "report_date",
  "uiDisplayName": "Report Date",
  "fieldType": "date",
  "isRequired": true,
  "validationRules": {
    "minDate": "2020-01-01",
    "maxDate": "2030-12-31"
  },
  "placeholder": "Select report preparation date",
  "helpText": "Date when the valuation report is prepared",
  "gridSize": 6,
  "sortOrder": 1,
  "isActive": true,
  "createdAt": new Date(),
  "updatedAt": new Date()
}
```

---

## **Complete Field Definitions:**

### **1. Basic Information Group**

```json
[
  {
    "fieldId": "report_date",
    "fieldGroup": "basic_info",
    "technicalName": "report_date",
    "uiDisplayName": "Report Date",
    "fieldType": "date",
    "isRequired": true,
    "validationRules": {
      "minDate": "2020-01-01",
      "maxDate": "2030-12-31"
    },
    "placeholder": "Select report preparation date",
    "helpText": "Date when the valuation report is prepared",
    "gridSize": 6,
    "sortOrder": 1
  },
  {
    "fieldId": "inspection_date",
    "fieldGroup": "basic_info", 
    "technicalName": "inspection_date",
    "uiDisplayName": "Inspection Date",
    "fieldType": "date",
    "isRequired": true,
    "validationRules": {
      "minDate": "2020-01-01",
      "maxDate": "2025-12-31"
    },
    "placeholder": "Select property inspection date",
    "helpText": "Date when the property was physically inspected",
    "gridSize": 6,
    "sortOrder": 2
  },
  {
    "fieldId": "valuation_purpose",
    "fieldGroup": "basic_info",
    "technicalName": "valuation_purpose",
    "uiDisplayName": "Purpose of Valuation",
    "fieldType": "select",
    "isRequired": true,
    "options": [
      {"value": "mortgage_loan", "label": "Mortgage/Home Loan"},
      {"value": "sale_transaction", "label": "Sale Transaction"},
      {"value": "insurance_coverage", "label": "Insurance Coverage"},
      {"value": "taxation_assessment", "label": "Taxation Assessment"},
      {"value": "investment_analysis", "label": "Investment Analysis"},
      {"value": "legal_proceedings", "label": "Legal Proceedings"}
    ],
    "placeholder": "Select purpose of valuation",
    "helpText": "Primary reason for conducting the property valuation",
    "gridSize": 12,
    "sortOrder": 3
  }
]
```

### **2. Bank & Branch Details Group**

```json
[
  {
    "fieldId": "bank_name",
    "fieldGroup": "bank_details",
    "technicalName": "bank_name",
    "uiDisplayName": "Bank Name",
    "fieldType": "select",
    "isRequired": true,
    "options": [
      {"value": "SBI", "label": "State Bank of India"},
      {"value": "PNB", "label": "Punjab National Bank"},
      {"value": "HDFC", "label": "HDFC Bank"},
      {"value": "ICICI", "label": "ICICI Bank"},
      {"value": "AXIS", "label": "Axis Bank"},
      {"value": "BOI", "label": "Bank of India"},
      {"value": "CANARA", "label": "Canara Bank"}
    ],
    "placeholder": "Select bank name",
    "helpText": "Name of the lending bank/financial institution",
    "gridSize": 6,
    "sortOrder": 1
  },
  {
    "fieldId": "branch_name",
    "fieldGroup": "bank_details",
    "technicalName": "branch_name", 
    "uiDisplayName": "Branch Name",
    "fieldType": "text",
    "isRequired": true,
    "validationRules": {
      "minLength": 2,
      "maxLength": 100,
      "pattern": "^[a-zA-Z0-9\\s\\-\\.]+$"
    },
    "placeholder": "Enter branch name",
    "helpText": "Name of the specific bank branch",
    "gridSize": 6,
    "sortOrder": 2
  },
  {
    "fieldId": "branch_code",
    "fieldGroup": "bank_details",
    "technicalName": "branch_code",
    "uiDisplayName": "Branch Code/IFSC",
    "fieldType": "text",
    "isRequired": false,
    "validationRules": {
      "minLength": 4,
      "maxLength": 20,
      "pattern": "^[A-Z0-9]+$"
    },
    "placeholder": "Enter branch code or IFSC",
    "helpText": "Branch identification code or IFSC code",
    "gridSize": 6,
    "sortOrder": 3
  }
]
```

### **3. Valuer Details Group**

```json
[
  {
    "fieldId": "valuer_name",
    "fieldGroup": "valuer_details",
    "technicalName": "valuer_name",
    "uiDisplayName": "Valuer's Name",
    "fieldType": "text",
    "isRequired": true,
    "validationRules": {
      "minLength": 2,
      "maxLength": 100,
      "pattern": "^[a-zA-Z\\s\\.]+$"
    },
    "placeholder": "Enter valuer's full name",
    "helpText": "Full name of the certified valuer",
    "gridSize": 6,
    "sortOrder": 1
  },
  {
    "fieldId": "valuer_license_number",
    "fieldGroup": "valuer_details",
    "technicalName": "valuer_license_number",
    "uiDisplayName": "License/Registration Number",
    "fieldType": "text", 
    "isRequired": true,
    "validationRules": {
      "minLength": 5,
      "maxLength": 50,
      "pattern": "^[A-Z0-9\\/\\-]+$"
    },
    "placeholder": "Enter license number",
    "helpText": "Government issued valuer license number",
    "gridSize": 6,
    "sortOrder": 2
  },
  {
    "fieldId": "valuer_seal_uploaded",
    "fieldGroup": "valuer_details",
    "technicalName": "valuer_seal_uploaded",
    "uiDisplayName": "Valuer's Seal Uploaded",
    "fieldType": "checkbox",
    "isRequired": true,
    "placeholder": "",
    "helpText": "Confirm that valuer's official seal has been uploaded",
    "gridSize": 12,
    "sortOrder": 3
  }
]
```

### **4. Borrower/Owner Details Group**

```json
[
  {
    "fieldId": "borrower_name",
    "fieldGroup": "borrower_details",
    "technicalName": "borrower_name",
    "uiDisplayName": "Borrower/Owner Name",
    "fieldType": "text",
    "isRequired": true,
    "validationRules": {
      "minLength": 2,
      "maxLength": 100,
      "pattern": "^[a-zA-Z\\s\\.]+$"
    },
    "placeholder": "Enter borrower's full name",
    "helpText": "Full name of the property borrower/owner",
    "gridSize": 6,
    "sortOrder": 1
  },
  {
    "fieldId": "borrower_father_name",
    "fieldGroup": "borrower_details",
    "technicalName": "borrower_father_name",
    "uiDisplayName": "Father's/Husband's Name",
    "fieldType": "text",
    "isRequired": true,
    "validationRules": {
      "minLength": 2,
      "maxLength": 100,
      "pattern": "^[a-zA-Z\\s\\.]+$"
    },
    "placeholder": "Enter father's/husband's name",
    "helpText": "Father's or husband's name of the borrower",
    "gridSize": 6,
    "sortOrder": 2
  },
  {
    "fieldId": "borrower_contact_number",
    "fieldGroup": "borrower_details",
    "technicalName": "borrower_contact_number",
    "uiDisplayName": "Contact Number",
    "fieldType": "tel",
    "isRequired": true,
    "validationRules": {
      "pattern": "^[+]?[0-9]{10,15}$"
    },
    "placeholder": "Enter 10-digit mobile number",
    "helpText": "Primary contact number of the borrower",
    "gridSize": 6,
    "sortOrder": 3
  },
  {
    "fieldId": "borrower_email",
    "fieldGroup": "borrower_details", 
    "technicalName": "borrower_email",
    "uiDisplayName": "Email Address",
    "fieldType": "email",
    "isRequired": false,
    "validationRules": {
      "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
    },
    "placeholder": "Enter email address (optional)",
    "helpText": "Email address of the borrower (if available)",
    "gridSize": 6,
    "sortOrder": 4
  }
]
```

### **5. Declaration & Conflict Group**

```json
[
  {
    "fieldId": "no_conflict_declaration",
    "fieldGroup": "declaration",
    "technicalName": "no_conflict_declaration",
    "uiDisplayName": "Declaration of No Conflict of Interest",
    "fieldType": "checkbox",
    "isRequired": true,
    "placeholder": "",
    "helpText": "I hereby declare that I have no conflict of interest in this valuation",
    "gridSize": 12,
    "sortOrder": 1
  }
]
```

### **6. Property Address & Location Group**

```json
[
  {
    "fieldId": "property_address",
    "fieldGroup": "property_location",
    "technicalName": "property_address",
    "uiDisplayName": "Complete Property Address",
    "fieldType": "textarea",
    "isRequired": true,
    "validationRules": {
      "minLength": 10,
      "maxLength": 500
    },
    "placeholder": "Enter complete address with landmarks",
    "helpText": "Full address including house number, street, landmarks",
    "gridSize": 12,
    "sortOrder": 1
  },
  {
    "fieldId": "plot_number",
    "fieldGroup": "property_location",
    "technicalName": "plot_number",
    "uiDisplayName": "Plot Number",
    "fieldType": "text",
    "isRequired": true,
    "validationRules": {
      "minLength": 1,
      "maxLength": 50,
      "pattern": "^[a-zA-Z0-9\\/\\-\\s]+$"
    },
    "placeholder": "Enter plot number",
    "helpText": "Official plot number as per revenue records",
    "gridSize": 6,
    "sortOrder": 2
  },
  {
    "fieldId": "village_area",
    "fieldGroup": "property_location", 
    "technicalName": "village_area",
    "uiDisplayName": "Village/Area",
    "fieldType": "text",
    "isRequired": true,
    "validationRules": {
      "minLength": 2,
      "maxLength": 100,
      "pattern": "^[a-zA-Z\\s\\.\\-]+$"
    },
    "placeholder": "Enter village or area name",
    "helpText": "Village name or area locality",
    "gridSize": 6,
    "sortOrder": 3
  },
  {
    "fieldId": "sector_block",
    "fieldGroup": "property_location",
    "technicalName": "sector_block",
    "uiDisplayName": "Sector/Block",
    "fieldType": "text",
    "isRequired": false,
    "validationRules": {
      "maxLength": 50,
      "pattern": "^[a-zA-Z0-9\\s\\-]+$"
    },
    "placeholder": "Enter sector or block (if applicable)",
    "helpText": "Sector or block number (for urban areas)",
    "gridSize": 6,
    "sortOrder": 4
  },
  {
    "fieldId": "district",
    "fieldGroup": "property_location",
    "technicalName": "district",
    "uiDisplayName": "District",
    "fieldType": "text",
    "isRequired": true,
    "validationRules": {
      "minLength": 2,
      "maxLength": 100,
      "pattern": "^[a-zA-Z\\s\\.\\-]+$"
    },
    "placeholder": "Enter district name",
    "helpText": "District where the property is located",
    "gridSize": 6,
    "sortOrder": 5
  },
  {
    "fieldId": "state",
    "fieldGroup": "property_location",
    "technicalName": "state",
    "uiDisplayName": "State",
    "fieldType": "select",
    "isRequired": true,
    "options": [
      {"value": "andhra_pradesh", "label": "Andhra Pradesh"},
      {"value": "delhi", "label": "Delhi"},
      {"value": "gujarat", "label": "Gujarat"},
      {"value": "haryana", "label": "Haryana"},
      {"value": "karnataka", "label": "Karnataka"},
      {"value": "maharashtra", "label": "Maharashtra"},
      {"value": "punjab", "label": "Punjab"},
      {"value": "rajasthan", "label": "Rajasthan"},
      {"value": "tamil_nadu", "label": "Tamil Nadu"},
      {"value": "uttar_pradesh", "label": "Uttar Pradesh"}
    ],
    "placeholder": "Select state",
    "helpText": "State where the property is located",
    "gridSize": 6,
    "sortOrder": 6
  },
  {
    "fieldId": "pin_code",
    "fieldGroup": "property_location",
    "technicalName": "pin_code",
    "uiDisplayName": "PIN Code",
    "fieldType": "text",
    "isRequired": true,
    "validationRules": {
      "pattern": "^[0-9]{6}$"
    },
    "placeholder": "Enter 6-digit PIN code",
    "helpText": "Postal PIN code of the property location",
    "gridSize": 6,
    "sortOrder": 7
  }
]
```

### **7. Property Type & Classification Group**

```json
[
  {
    "fieldId": "property_type",
    "fieldGroup": "property_classification",
    "technicalName": "property_type",
    "uiDisplayName": "Property Type",
    "fieldType": "select",
    "isRequired": true,
    "options": [
      {"value": "residential", "label": "Residential"},
      {"value": "commercial", "label": "Commercial"},
      {"value": "industrial", "label": "Industrial"},
      {"value": "agricultural", "label": "Agricultural"},
      {"value": "institutional", "label": "Institutional"}
    ],
    "placeholder": "Select property type",
    "helpText": "Primary classification of the property",
    "gridSize": 6,
    "sortOrder": 1
  },
  {
    "fieldId": "tenure_type",
    "fieldGroup": "property_classification",
    "technicalName": "tenure_type",
    "uiDisplayName": "Tenure Type",
    "fieldType": "select",
    "isRequired": true,
    "options": [
      {"value": "freehold", "label": "Freehold"},
      {"value": "leasehold", "label": "Leasehold"}
    ],
    "placeholder": "Select tenure type",
    "helpText": "Legal ownership structure of the property",
    "gridSize": 6,
    "sortOrder": 2
  },
  {
    "fieldId": "area_classification",
    "fieldGroup": "property_classification",
    "technicalName": "area_classification",
    "uiDisplayName": "Area Classification",
    "fieldType": "select",
    "isRequired": true,
    "options": [
      {"value": "urban", "label": "Urban"},
      {"value": "semi_urban", "label": "Semi-Urban"},
      {"value": "rural", "label": "Rural"}
    ],
    "placeholder": "Select area classification",
    "helpText": "Geographic classification of the property location",
    "gridSize": 6,
    "sortOrder": 3
  },
  {
    "fieldId": "municipal_jurisdiction",
    "fieldGroup": "property_classification",
    "technicalName": "municipal_jurisdiction",
    "uiDisplayName": "Municipal Jurisdiction",
    "fieldType": "text",
    "isRequired": true,
    "validationRules": {
      "minLength": 2,
      "maxLength": 100,
      "pattern": "^[a-zA-Z\\s\\.\\-]+$"
    },
    "placeholder": "Enter municipal corporation/council name",
    "helpText": "Local municipal authority governing the property",
    "gridSize": 6,
    "sortOrder": 4
  }
]
```

### **8. Coordinates Group**

```json
[
  {
    "fieldId": "latitude",
    "fieldGroup": "coordinates",
    "technicalName": "latitude",
    "uiDisplayName": "Latitude",
    "fieldType": "number",
    "isRequired": false,
    "validationRules": {
      "min": -90,
      "max": 90,
      "step": 0.000001
    },
    "placeholder": "Enter latitude coordinates",
    "helpText": "GPS latitude coordinates (click location button to auto-fill)",
    "gridSize": 6,
    "sortOrder": 1
  },
  {
    "fieldId": "longitude",
    "fieldGroup": "coordinates",
    "technicalName": "longitude",
    "uiDisplayName": "Longitude", 
    "fieldType": "number",
    "isRequired": false,
    "validationRules": {
      "min": -180,
      "max": 180,
      "step": 0.000001
    },
    "placeholder": "Enter longitude coordinates",
    "helpText": "GPS longitude coordinates (click location button to auto-fill)",
    "gridSize": 6,
    "sortOrder": 2
  }
]
```

---

## **Technical Implementation:**

### **API Endpoints:**
- `GET /api/common-fields` - Get all common fields
- `GET /api/common-fields/group/{groupName}` - Get fields by group
- `POST /api/common-fields` - Create new field
- `PUT /api/common-fields/{fieldId}` - Update field
- `DELETE /api/common-fields/{fieldId}` - Delete field

### **Frontend Usage:**
- Fields will be fetched from API and rendered dynamically
- `technicalName` used for form control names and API data
- `uiDisplayName` used for form labels
- Field groups organize form sections

**This structure ensures:**
✅ Clean separation between technical and UI names  
✅ Flexible field validation and configuration  
✅ Organized grouping for better UX  
✅ Easy maintenance and updates  
✅ Standardized across all bank templates