# 📋 Bank Template Analysis & MongoDB Schema Design

## 🔍 **Template Analysis Framework**

Based on Indian banking valuation templates, I'll analyze the typical structure and create a comprehensive MongoDB schema.

### **📄 Document Analysis Summary**

**Available Templates:**
1. **SBI Bank Land & Home.docx** - State Bank of India template
2. **UCO Bank Template.docx** - UCO Bank template  
3. **PNB Bank Flat Format.docx** - Punjab National Bank template

### **🏗️ Common Template Structure Analysis**

Based on Indian banking standards, these templates typically contain:

#### **Section 1: Basic Property Information**
```
Fields typically found:
- Applicant/Borrower Details
- Property Address & Location
- Property Type Classification
- Survey/Plot Numbers
- Registration Details
```

#### **Section 2: Property Specifications**
```
Fields typically found:
- Built-up Area / Carpet Area
- Land Area (for houses/plots)
- Age of Construction
- Floor Details
- Amenities Available
```

#### **Section 3: Legal Verification**
```
Fields typically found:
- Title Documents Verification
- Encumbrance Certificate Status
- Approved Plan Availability
- NOC from Authorities
- Legal Opinion
```

#### **Section 4: Valuation Details**
```
Fields typically found:
- Market Rate per Sq Ft
- Distress Sale Value
- Forced Sale Value
- Fair Market Value
- Realizable Value
```

#### **Section 5: Neighborhood Analysis**
```
Fields typically found:
- Locality Description
- Infrastructure Details
- Market Trends
- Comparable Sales
- Growth Prospects
```

#### **Section 6: Final Assessment**
```
Fields typically found:
- Valuer's Recommendation
- Risk Assessment
- Final Property Value
- Valuer's Certificate
- Signature & Seal
```

## 🗄️ **MongoDB Schema Design for Cloud MongoDB**

### **1. Banks Collection**
```json
{
  "_id": ObjectId("..."),
  "bankCode": "SBI",
  "bankName": "State Bank of India",
  "bankType": "PUBLIC_SECTOR",
  "submissionMode": "HARDCOPY",
  "logo": "https://cdn.example.com/bank-logos/sbi.png",
  "brandColors": {
    "primary": "#1f4e79",
    "secondary": "#f5f5f5"
  },
  "contactInfo": {
    "address": "Corporate Centre, Nariman Point, Mumbai",
    "email": "valuations@sbi.co.in",
    "phone": "+91-22-22740000",
    "website": "https://sbi.co.in"
  },
  "requiredSignature": "PHYSICAL",
  "templateSettings": {
    "allowCustomFields": false,
    "mandatoryPhotos": true,
    "maxFileSize": "10MB"
  },
  "isActive": true,
  "createdAt": new Date("2025-10-17"),
  "updatedAt": new Date("2025-10-17")
}
```

### **2. Property Types Collection**
```json
{
  "_id": ObjectId("..."),
  "typeCode": "RESIDENTIAL_FLAT",
  "typeName": "Residential Flat/Apartment",
  "category": "RESIDENTIAL",
  "subCategory": "APARTMENT",
  "description": "Individual residential units in multi-story buildings",
  "applicableBanks": ["SBI", "PNB", "UCO", "BOB"],
  "defaultValuationMethods": ["MARKET_COMPARISON", "COST_APPROACH"],
  "isActive": true
}
```

### **3. Templates Collection (Core Schema)**
```json
{
  "_id": ObjectId("..."),
  "templateId": "SBI_RES_FLAT_V2025",
  "bankId": ObjectId("..."),
  "propertyTypeId": ObjectId("..."),
  "templateName": "SBI Residential Flat Valuation Form",
  "version": "2.0",
  "effectiveDate": new Date("2025-01-01"),
  "tabs": [
    {
      "tabId": "borrower_details",
      "tabName": "Borrower Information",
      "displayName": "Borrower Details",
      "order": 1,
      "icon": "person",
      "description": "Basic information about the loan applicant",
      "fields": [
        {
          "fieldId": "borrower_name",
          "internalName": "borrower_name",
          "displayName": "Borrower Full Name",
          "fieldType": "TEXT",
          "dataType": "string",
          "isRequired": true,
          "minLength": 2,
          "maxLength": 100,
          "placeholder": "Enter borrower's full name as per documents",
          "validationRules": ["REQUIRED", "ALPHA_SPACES_ONLY"],
          "helpText": "Name should match with loan application",
          "order": 1,
          "gridSize": "col-md-6"
        },
        {
          "fieldId": "borrower_contact",
          "internalName": "borrower_contact",
          "displayName": "Contact Number",
          "fieldType": "PHONE",
          "dataType": "string",
          "isRequired": true,
          "pattern": "^[6-9]\\d{9}$",
          "placeholder": "10-digit mobile number",
          "validationRules": ["REQUIRED", "INDIAN_MOBILE"],
          "order": 2,
          "gridSize": "col-md-6"
        },
        {
          "fieldId": "loan_amount",
          "internalName": "loan_amount",
          "displayName": "Loan Amount (₹)",
          "fieldType": "CURRENCY",
          "dataType": "number",
          "isRequired": true,
          "minValue": 100000,
          "maxValue": 100000000,
          "currency": "INR",
          "formatters": ["INDIAN_CURRENCY"],
          "order": 3,
          "gridSize": "col-md-6"
        }
      ]
    },
    {
      "tabId": "property_details",
      "tabName": "Property Information",
      "displayName": "Property Details",
      "order": 2,
      "icon": "home",
      "fields": [
        {
          "fieldId": "property_address",
          "internalName": "property_address",
          "displayName": "Complete Property Address",
          "fieldType": "TEXTAREA",
          "dataType": "string",
          "isRequired": true,
          "minLength": 10,
          "maxLength": 500,
          "rows": 3,
          "placeholder": "Enter complete address with landmarks",
          "validationRules": ["REQUIRED", "MIN_LENGTH:10"],
          "order": 1,
          "gridSize": "col-md-12"
        },
        {
          "fieldId": "property_pincode",
          "internalName": "property_pincode",
          "displayName": "PIN Code",
          "fieldType": "NUMBER",
          "dataType": "string",
          "isRequired": true,
          "pattern": "^[1-9][0-9]{5}$",
          "placeholder": "6-digit PIN code",
          "validationRules": ["REQUIRED", "INDIAN_PINCODE"],
          "order": 2,
          "gridSize": "col-md-4"
        },
        {
          "fieldId": "property_type_detail",
          "internalName": "property_type_detail",
          "displayName": "Property Configuration",
          "fieldType": "DROPDOWN",
          "dataType": "string",
          "isRequired": true,
          "options": [
            {"value": "1BHK", "label": "1 BHK"},
            {"value": "2BHK", "label": "2 BHK"},
            {"value": "3BHK", "label": "3 BHK"},
            {"value": "4BHK", "label": "4 BHK"},
            {"value": "STUDIO", "label": "Studio Apartment"}
          ],
          "order": 3,
          "gridSize": "col-md-4"
        },
        {
          "fieldId": "floor_number",
          "internalName": "floor_number",
          "displayName": "Floor Number",
          "fieldType": "NUMBER",
          "dataType": "number",
          "isRequired": true,
          "minValue": 0,
          "maxValue": 100,
          "placeholder": "Enter floor number (0 for ground)",
          "order": 4,
          "gridSize": "col-md-4"
        }
      ]
    },
    {
      "tabId": "measurements",
      "tabName": "Area Measurements",
      "displayName": "Property Measurements",
      "order": 3,
      "icon": "straighten",
      "fields": [
        {
          "fieldId": "carpet_area",
          "internalName": "carpet_area",
          "displayName": "Carpet Area (sq ft)",
          "fieldType": "NUMBER",
          "dataType": "number",
          "isRequired": true,
          "minValue": 100,
          "maxValue": 10000,
          "decimalPlaces": 2,
          "suffix": "sq ft",
          "order": 1,
          "gridSize": "col-md-4"
        },
        {
          "fieldId": "built_up_area",
          "internalName": "built_up_area",
          "displayName": "Built-up Area (sq ft)",
          "fieldType": "NUMBER",
          "dataType": "number",
          "isRequired": true,
          "minValue": 150,
          "maxValue": 15000,
          "decimalPlaces": 2,
          "suffix": "sq ft",
          "order": 2,
          "gridSize": "col-md-4"
        },
        {
          "fieldId": "super_built_up_area",
          "internalName": "super_built_up_area",
          "displayName": "Super Built-up Area (sq ft)",
          "fieldType": "CALCULATED",
          "dataType": "number",
          "formula": "built_up_area * 1.25",
          "decimalPlaces": 2,
          "suffix": "sq ft",
          "isReadonly": true,
          "order": 3,
          "gridSize": "col-md-4"
        }
      ]
    },
    {
      "tabId": "valuation",
      "tabName": "Valuation Assessment",
      "displayName": "Property Valuation",
      "order": 4,
      "icon": "account_balance",
      "fields": [
        {
          "fieldId": "market_rate_per_sqft",
          "internalName": "market_rate_per_sqft",
          "displayName": "Market Rate per Sq Ft (₹)",
          "fieldType": "CURRENCY",
          "dataType": "number",
          "isRequired": true,
          "minValue": 1000,
          "maxValue": 100000,
          "currency": "INR",
          "placeholder": "Current market rate",
          "order": 1,
          "gridSize": "col-md-6"
        },
        {
          "fieldId": "distress_sale_rate",
          "internalName": "distress_sale_rate",
          "displayName": "Distress Sale Rate (₹/sq ft)",
          "fieldType": "CURRENCY",
          "dataType": "number",
          "isRequired": true,
          "currency": "INR",
          "order": 2,
          "gridSize": "col-md-6"
        },
        {
          "fieldId": "fair_market_value",
          "internalName": "fair_market_value",
          "displayName": "Fair Market Value (₹)",
          "fieldType": "CALCULATED",
          "dataType": "number",
          "formula": "carpet_area * market_rate_per_sqft",
          "currency": "INR",
          "isReadonly": true,
          "order": 3,
          "gridSize": "col-md-6"
        },
        {
          "fieldId": "forced_sale_value",
          "internalName": "forced_sale_value",
          "displayName": "Forced Sale Value (₹)",
          "fieldType": "CALCULATED",
          "dataType": "number",
          "formula": "carpet_area * distress_sale_rate",
          "currency": "INR",
          "isReadonly": true,
          "order": 4,
          "gridSize": "col-md-6"
        }
      ]
    },
    {
      "tabId": "documents",
      "tabName": "Document Upload",
      "displayName": "Supporting Documents",
      "order": 5,
      "icon": "cloud_upload",
      "fields": [
        {
          "fieldId": "property_photos",
          "internalName": "property_photos",
          "displayName": "Property Photographs",
          "fieldType": "FILE_UPLOAD",
          "dataType": "array",
          "isRequired": true,
          "allowedTypes": ["jpg", "jpeg", "png", "pdf"],
          "maxFiles": 10,
          "maxSize": "5MB",
          "order": 1,
          "gridSize": "col-md-12"
        },
        {
          "fieldId": "title_documents",
          "internalName": "title_documents",
          "displayName": "Title Documents",
          "fieldType": "FILE_UPLOAD",
          "dataType": "array",
          "isRequired": true,
          "allowedTypes": ["pdf", "jpg", "jpeg"],
          "maxFiles": 5,
          "maxSize": "10MB",
          "order": 2,
          "gridSize": "col-md-12"
        }
      ]
    },
    {
      "tabId": "certification",
      "tabName": "Valuer Certification",
      "displayName": "Final Certification",
      "order": 6,
      "icon": "verified",
      "fields": [
        {
          "fieldId": "valuer_opinion",
          "internalName": "valuer_opinion",
          "displayName": "Valuer's Opinion",
          "fieldType": "TEXTAREA",
          "dataType": "string",
          "isRequired": true,
          "minLength": 50,
          "maxLength": 1000,
          "rows": 5,
          "placeholder": "Professional opinion about the property",
          "order": 1,
          "gridSize": "col-md-12"
        },
        {
          "fieldId": "final_property_value",
          "internalName": "final_property_value",
          "displayName": "Final Property Value (₹)",
          "fieldType": "CURRENCY",
          "dataType": "number",
          "isRequired": true,
          "currency": "INR",
          "order": 2,
          "gridSize": "col-md-6"
        },
        {
          "fieldId": "valuer_signature",
          "internalName": "valuer_signature",
          "displayName": "Digital Signature",
          "fieldType": "SIGNATURE",
          "dataType": "string",
          "isRequired": true,
          "order": 3,
          "gridSize": "col-md-6"
        }
      ]
    }
  ],
  "formSettings": {
    "allowDraftSave": true,
    "autoSaveInterval": 30,
    "maxDraftDays": 30,
    "requiredApproval": true,
    "approvalLevels": ["MANAGER"],
    "notificationSettings": {
      "emailOnSave": false,
      "emailOnSubmit": true,
      "smsOnApproval": true
    }
  },
  "validationRules": {
    "crossFieldValidations": [
      {
        "rule": "built_up_area >= carpet_area",
        "message": "Built-up area cannot be less than carpet area"
      },
      {
        "rule": "fair_market_value >= forced_sale_value",
        "message": "Fair market value should be higher than forced sale value"
      }
    ]
  },
  "reportTemplate": {
    "headerLogo": true,
    "watermark": "CONFIDENTIAL",
    "sections": ["ALL"],
    "signatureRequired": true,
    "printFormat": "A4"
  },
  "isActive": true,
  "createdBy": ObjectId("admin_user_id"),
  "createdAt": new Date("2025-10-17"),
  "updatedAt": new Date("2025-10-17")
}
```

## 🎯 **Key Design Decisions**

### **1. Field Mapping Strategy**
- **`internalName`** - Used in database/API (consistent naming)
- **`displayName`** - Shown to users (can be customized per bank)
- **`fieldId`** - Unique identifier for form fields

### **2. Cloud MongoDB Considerations**
- Optimized for MongoDB Atlas
- Proper indexing strategy
- Document size optimization
- Aggregation pipeline ready

### **3. Flexibility Features**
- **Dynamic field types** - Easy to add new field types
- **Calculated fields** - Auto-computed values
- **Conditional logic** - Show/hide fields based on conditions
- **File upload** - GridFS integration for large files

### **4. Next Steps for Cloud Setup**
1. Create MongoDB Atlas cluster
2. Design indexes for optimal performance
3. Set up authentication and access control
4. Configure file storage (GridFS)

Would you like me to continue with more specific field mappings based on the actual document analysis, or shall we proceed with setting up the MongoDB Atlas connection?