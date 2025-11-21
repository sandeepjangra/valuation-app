# 🏦 Indian Property Valuation System - Business Requirements & Architecture

## 📋 **Clear Business Requirements**

### **🎯 Target Users:**
- **Private Property Valuers** working with multiple Indian banks
- **Two User Roles:**
  - 👤 **Employee** - Creates and saves valuation reports
  - 👨‍💼 **Manager** - Can save + submit reports (approval authority)

### **🏦 Bank Integration Model:**
- **Public Sector Banks** (SBI, PNB, UCO, etc.) → **Hardcopy + Physical Signature**
- **Private Banks** (HDFC, ICICI, Axis, etc.) → **Digital Submission + Digital Signature**

### **📋 Template Management:**
- Each bank has unique templates
- Templates vary by property type (Land, Flat, House, Commercial)
- Templates rarely change (stable configuration)
- Admin-managed template configuration

### **🔄 Workflow Process:**
```
Employee → Create Report → Save Draft → Manager Review → Submit
                ↓                           ↓
           Auto-save Progress      Final Submission
                                  (Digital/Hardcopy based on bank)
```

## 🏗️ **System Architecture Design**

### **1. User Role Management**
```json
{
  "users": {
    "_id": "ObjectId",
    "employeeId": "EMP001",
    "name": "Rajesh Kumar",
    "email": "rajesh@valuationco.com",
    "role": "EMPLOYEE | MANAGER",
    "organizationId": "ObjectId",
    "isActive": true,
    "permissions": ["CREATE_REPORT", "SAVE_DRAFT", "SUBMIT_REPORT"],
    "digitalSignature": {
      "certificateId": "DSC123",
      "validTill": "2026-03-15",
      "isActive": true
    }
  }
}
```

### **2. Bank Configuration**
```json
{
  "banks": {
    "_id": "ObjectId",
    "bankCode": "SBI",
    "bankName": "State Bank of India",
    "bankType": "PUBLIC_SECTOR | PRIVATE_SECTOR",
    "submissionMode": "HARDCOPY | DIGITAL | BOTH",
    "logo": "sbi-logo.png",
    "contactDetails": {
      "address": "Mumbai Head Office",
      "email": "valuations@sbi.co.in",
      "phone": "+91-22-12345678"
    },
    "requiredSignature": "PHYSICAL | DIGITAL",
    "isActive": true
  }
}
```

### **3. Property Types**
```json
{
  "propertyTypes": {
    "_id": "ObjectId",
    "typeCode": "RESIDENTIAL_FLAT",
    "typeName": "Residential Flat/Apartment",
    "category": "RESIDENTIAL",
    "subCategory": "FLAT",
    "description": "Individual units in apartment buildings",
    "isActive": true
  }
}
```

### **4. Dynamic Template Configuration**
```json
{
  "templates": {
    "_id": "ObjectId",
    "bankId": "ObjectId(SBI)",
    "propertyTypeId": "ObjectId(RESIDENTIAL_FLAT)",
    "templateName": "SBI Residential Flat Valuation Form",
    "templateCode": "SBI_RES_FLAT_V1",
    "version": "1.0",
    "tabs": [
      {
        "tabId": "basic_details",
        "tabName": "Basic Property Details",
        "order": 1,
        "icon": "home",
        "fields": [
          {
            "fieldId": "property_address",
            "fieldName": "Property Address",
            "fieldType": "TEXTAREA",
            "isRequired": true,
            "maxLength": 500,
            "placeholder": "Enter complete property address",
            "validationRules": ["REQUIRED", "MIN_LENGTH:10"],
            "order": 1
          },
          {
            "fieldId": "property_pincode",
            "fieldName": "PIN Code",
            "fieldType": "NUMBER",
            "isRequired": true,
            "minValue": 100000,
            "maxValue": 999999,
            "order": 2
          },
          {
            "fieldId": "property_type",
            "fieldName": "Property Type",
            "fieldType": "DROPDOWN",
            "isRequired": true,
            "options": [
              {"value": "1BHK", "label": "1 BHK"},
              {"value": "2BHK", "label": "2 BHK"},
              {"value": "3BHK", "label": "3 BHK"}
            ],
            "order": 3
          }
        ]
      },
      {
        "tabId": "valuation_details",
        "tabName": "Valuation Assessment",
        "order": 2,
        "icon": "calculator",
        "fields": [
          {
            "fieldId": "carpet_area",
            "fieldName": "Carpet Area (sq ft)",
            "fieldType": "NUMBER",
            "isRequired": true,
            "decimalPlaces": 2,
            "order": 1
          },
          {
            "fieldId": "rate_per_sqft",
            "fieldName": "Rate per Sq Ft (₹)",
            "fieldType": "CURRENCY",
            "isRequired": true,
            "currency": "INR",
            "order": 2
          },
          {
            "fieldId": "total_value",
            "fieldName": "Total Property Value (₹)",
            "fieldType": "CALCULATED",
            "formula": "carpet_area * rate_per_sqft",
            "currency": "INR",
            "isReadonly": true,
            "order": 3
          }
        ]
      }
    ],
    "submissionSettings": {
      "allowDraftSave": true,
      "autoSaveInterval": 30,
      "requiredApproval": true,
      "digitalSignatureRequired": true
    },
    "isActive": true,
    "createdBy": "admin",
    "createdDate": "2025-10-17",
    "lastModified": "2025-10-17"
  }
}
```

### **5. Valuation Reports (User Data)**
```json
{
  "valuationReports": {
    "_id": "ObjectId",
    "reportNumber": "VAL/2025/001234",
    "templateId": "ObjectId",
    "bankId": "ObjectId",
    "propertyTypeId": "ObjectId",
    "valuerId": "ObjectId",
    "managerId": "ObjectId",
    "status": "DRAFT | PENDING_APPROVAL | APPROVED | SUBMITTED",
    "formData": {
      "basic_details": {
        "property_address": "123, MG Road, Bangalore",
        "property_pincode": 560001,
        "property_type": "2BHK"
      },
      "valuation_details": {
        "carpet_area": 950.50,
        "rate_per_sqft": 8500,
        "total_value": 8079250
      }
    },
    "attachments": [
      {
        "fileName": "property_photos.pdf",
        "fileType": "PDF",
        "fileSize": 2048576,
        "uploadDate": "2025-10-17",
        "category": "PHOTOS"
      }
    ],
    "workflow": {
      "createdBy": "ObjectId(Employee)",
      "createdDate": "2025-10-17T10:00:00Z",
      "lastSavedBy": "ObjectId(Employee)",
      "lastSavedDate": "2025-10-17T11:30:00Z",
      "approvedBy": "ObjectId(Manager)",
      "approvedDate": "2025-10-17T14:00:00Z",
      "submittedBy": "ObjectId(Manager)",
      "submittedDate": "2025-10-17T15:00:00Z"
    },
    "signatures": {
      "employeeSignature": "base64_signature_data",
      "managerSignature": "base64_signature_data",
      "digitalCertificate": "DSC_certificate_data"
    }
  }
}
```

## 🎯 **Key Features Based on Your Requirements**

### **1. 🔐 Role-Based Access Control**
- **Employee:** Create, Edit, Save drafts
- **Manager:** All employee rights + Submit reports

### **2. 📋 Smart Form Generation**
- Dynamic forms based on Bank + Property Type
- Auto-save every 30 seconds
- Client-side validation
- Progressive form completion

### **3. 📄 Dual Submission Support**
- **Digital:** PDF generation + Digital signature
- **Hardcopy:** Print-friendly format + Signature fields

### **4. 🎨 Field Types Supported**
- Text, Textarea, Number, Currency
- Dropdown, Multi-select, Radio buttons
- Date, Time, File upload
- Calculated fields (auto-computation)
- Signature capture
- Photo/Document upload

### **5. 📊 Admin Template Management**
- Drag-drop form builder
- Field configuration UI
- Template versioning
- Bank-wise template cloning

## 🚀 **Next Steps**

Now I'll analyze your Word templates to create the actual MongoDB collections. 

**Is this architecture aligned with your vision? Should I proceed with analyzing the SBI, PNB, and UCO templates?**