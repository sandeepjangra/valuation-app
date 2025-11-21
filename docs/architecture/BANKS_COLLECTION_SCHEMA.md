# 🏦 MongoDB Banks Collection Design

## **Collection: `banks`**

This collection will store all bank information with their branches. The Bank & Branch Details section in forms will dynamically populate from this data.

### **Document Structure:**

```json
{
  "_id": ObjectId("..."),
  "bankCode": "SBI",
  "bankName": "State Bank of India",
  "bankShortName": "SBI",
  "bankType": "public_sector",
  "isActive": true,
  "headquarters": {
    "city": "Mumbai",
    "state": "Maharashtra",
    "pincode": "400001"
  },
  "branches": [
    {
      "branchId": "SBI_DEL_CP_001",
      "branchName": "Connaught Place",
      "branchCode": "SBIN0000001",
      "ifscCode": "SBIN0000001",
      "micrCode": "110002001",
      "address": {
        "street": "Janpath Road, Connaught Place",
        "area": "Central Delhi",
        "city": "New Delhi",
        "district": "Central Delhi",
        "state": "Delhi",
        "pincode": "110001",
        "landmark": "Near Palika Bazaar"
      },
      "contact": {
        "phone": "+91-11-23417930",
        "email": "sbi.cp.delhi@sbi.co.in",
        "managerName": "Rajesh Kumar",
        "managerContact": "+91-9876543210"
      },
      "coordinates": {
        "latitude": 28.6315,
        "longitude": 77.2167
      },
      "services": ["home_loans", "personal_loans", "business_loans", "deposits"],
      "workingHours": {
        "weekdays": "10:00 AM - 4:00 PM",
        "saturday": "10:00 AM - 2:00 PM",
        "sunday": "Closed"
      },
      "isActive": true,
      "createdAt": new Date(),
      "updatedAt": new Date()
    }
  ],
  "totalBranches": 1,
  "createdAt": new Date(),
  "updatedAt": new Date()
}
```

---

## **Complete Banks Data:**

### **1. State Bank of India (SBI)**
```json
{
  "bankCode": "SBI",
  "bankName": "State Bank of India",
  "bankShortName": "SBI",
  "bankType": "public_sector",
  "isActive": true,
  "headquarters": {
    "city": "Mumbai",
    "state": "Maharashtra",
    "pincode": "400001"
  },
  "branches": [
    {
      "branchId": "SBI_DEL_CP_001",
      "branchName": "Connaught Place",
      "branchCode": "SBIN0000001",
      "ifscCode": "SBIN0000001",
      "address": {
        "street": "Janpath Road, Connaught Place",
        "city": "New Delhi",
        "state": "Delhi",
        "pincode": "110001"
      },
      "contact": {
        "phone": "+91-11-23417930",
        "email": "sbi.cp.delhi@sbi.co.in"
      },
      "isActive": true
    },
    {
      "branchId": "SBI_MUM_BKC_002",
      "branchName": "Bandra Kurla Complex",
      "branchCode": "SBIN0000002",
      "ifscCode": "SBIN0000002",
      "address": {
        "street": "G Block, Bandra Kurla Complex",
        "city": "Mumbai",
        "state": "Maharashtra",
        "pincode": "400051"
      },
      "contact": {
        "phone": "+91-22-26542100",
        "email": "sbi.bkc.mumbai@sbi.co.in"
      },
      "isActive": true
    },
    {
      "branchId": "SBI_BLR_MGB_003",
      "branchName": "MG Road",
      "branchCode": "SBIN0000003",
      "ifscCode": "SBIN0000003",
      "address": {
        "street": "144, Mahatma Gandhi Road",
        "city": "Bangalore",
        "state": "Karnataka",
        "pincode": "560001"
      },
      "contact": {
        "phone": "+91-80-25584567",
        "email": "sbi.mgroad.bangalore@sbi.co.in"
      },
      "isActive": true
    }
  ]
}
```

### **2. Punjab National Bank (PNB)**
```json
{
  "bankCode": "PNB",
  "bankName": "Punjab National Bank",
  "bankShortName": "PNB",
  "bankType": "public_sector",
  "isActive": true,
  "headquarters": {
    "city": "New Delhi",
    "state": "Delhi",
    "pincode": "110001"
  },
  "branches": [
    {
      "branchId": "PNB_DEL_KP_001",
      "branchName": "Karol Bagh",
      "branchCode": "PUNB0000001",
      "ifscCode": "PUNB0000001",
      "address": {
        "street": "Main Karol Bagh Market",
        "city": "New Delhi",
        "state": "Delhi",
        "pincode": "110005"
      },
      "contact": {
        "phone": "+91-11-25753421",
        "email": "pnb.karolbagh.delhi@pnb.co.in"
      },
      "isActive": true
    },
    {
      "branchId": "PNB_CHD_SC_002",
      "branchName": "Sector 17",
      "branchCode": "PUNB0000002",
      "ifscCode": "PUNB0000002",
      "address": {
        "street": "SCO 125-126, Sector 17-C",
        "city": "Chandigarh",
        "state": "Chandigarh",
        "pincode": "160017"
      },
      "contact": {
        "phone": "+91-172-2702345",
        "email": "pnb.sector17.chandigarh@pnb.co.in"
      },
      "isActive": true
    }
  ]
}
```

### **3. HDFC Bank**
```json
{
  "bankCode": "HDFC",
  "bankName": "HDFC Bank Limited",
  "bankShortName": "HDFC Bank",
  "bankType": "private_sector",
  "isActive": true,
  "headquarters": {
    "city": "Mumbai",
    "state": "Maharashtra",
    "pincode": "400020"
  },
  "branches": [
    {
      "branchId": "HDFC_MUM_BND_001",
      "branchName": "Bandra West",
      "branchCode": "HDFC0000001",
      "ifscCode": "HDFC0000001",
      "address": {
        "street": "Turner Road, Bandra West",
        "city": "Mumbai",
        "state": "Maharashtra",
        "pincode": "400050"
      },
      "contact": {
        "phone": "+91-22-26420000",
        "email": "hdfc.bandra.mumbai@hdfcbank.com"
      },
      "isActive": true
    },
    {
      "branchId": "HDFC_GUR_CYB_002",
      "branchName": "Cyber City",
      "branchCode": "HDFC0000002",
      "ifscCode": "HDFC0000002",
      "address": {
        "street": "DLF Cyber City, Phase 2",
        "city": "Gurugram",
        "state": "Haryana",
        "pincode": "122002"
      },
      "contact": {
        "phone": "+91-124-4567890",
        "email": "hdfc.cybercity.gurgaon@hdfcbank.com"
      },
      "isActive": true
    }
  ]
}
```

### **4. ICICI Bank**
```json
{
  "bankCode": "ICICI",
  "bankName": "ICICI Bank Limited",
  "bankShortName": "ICICI Bank",
  "bankType": "private_sector",
  "isActive": true,
  "headquarters": {
    "city": "Mumbai",
    "state": "Maharashtra",
    "pincode": "400051"
  },
  "branches": [
    {
      "branchId": "ICICI_BLR_KOR_001",
      "branchName": "Koramangala",
      "branchCode": "ICIC0000001",
      "ifscCode": "ICIC0000001",
      "address": {
        "street": "80 Feet Road, 6th Block, Koramangala",
        "city": "Bangalore",
        "state": "Karnataka",
        "pincode": "560095"
      },
      "contact": {
        "phone": "+91-80-25530000",
        "email": "icici.koramangala.bangalore@icicibank.com"
      },
      "isActive": true
    }
  ]
}
```

---

## **Updated Common Fields Schema:**

Now the Bank & Branch Details section will be dynamic:

```json
[
  {
    "fieldId": "bank_code",
    "fieldGroup": "bank_details",
    "technicalName": "bank_code",
    "uiDisplayName": "Bank Name",
    "fieldType": "select_dynamic",
    "dataSource": "banks_collection",
    "dataSourceConfig": {
      "collection": "banks",
      "valueField": "bankCode",
      "labelField": "bankName",
      "filter": {"isActive": true},
      "sortBy": "bankName"
    },
    "isRequired": true,
    "placeholder": "Select bank name",
    "helpText": "Choose the lending bank/financial institution",
    "gridSize": 12,
    "sortOrder": 1,
    "onChange": "populate_branches"
  },
  {
    "fieldId": "branch_details",
    "fieldGroup": "bank_details",
    "technicalName": "branch_details",
    "uiDisplayName": "Branch Details",
    "fieldType": "select_dynamic",
    "dataSource": "banks_collection",
    "dataSourceConfig": {
      "collection": "banks",
      "nestedPath": "branches",
      "valueField": "branchId",
      "labelField": "branchName",
      "filter": {"bankCode": "{bank_code}", "branches.isActive": true},
      "sortBy": "branches.branchName",
      "dependsOn": "bank_code"
    },
    "isRequired": true,
    "placeholder": "Select branch (choose bank first)",
    "helpText": "Choose the specific bank branch",
    "gridSize": 6,
    "sortOrder": 2,
    "disabled": true,
    "enableWhen": "bank_code"
  },
  {
    "fieldId": "branch_ifsc",
    "fieldGroup": "bank_details",
    "technicalName": "branch_ifsc",
    "uiDisplayName": "IFSC Code",
    "fieldType": "text",
    "isRequired": false,
    "isReadonly": true,
    "autoPopulate": {
      "sourceField": "branch_details",
      "sourcePath": "branches.ifscCode"
    },
    "placeholder": "Auto-filled when branch is selected",
    "helpText": "IFSC code (auto-populated from branch selection)",
    "gridSize": 6,
    "sortOrder": 3
  },
  {
    "fieldId": "branch_address",
    "fieldGroup": "bank_details",
    "technicalName": "branch_address",
    "uiDisplayName": "Branch Address",
    "fieldType": "textarea",
    "isRequired": false,
    "isReadonly": true,
    "autoPopulate": {
      "sourceField": "branch_details",
      "sourcePath": "branches.address",
      "format": "{street}, {city}, {state} - {pincode}"
    },
    "placeholder": "Auto-filled when branch is selected",
    "helpText": "Branch address (auto-populated from branch selection)",
    "gridSize": 12,
    "sortOrder": 4
  }
]
```

---

## **API Endpoints:**

### **Banks Collection APIs:**
```javascript
// Get all active banks
GET /api/banks
Response: [
  {
    "bankCode": "SBI",
    "bankName": "State Bank of India",
    "bankShortName": "SBI",
    "totalBranches": 3
  }
]

// Get bank with all branches
GET /api/banks/{bankCode}
Response: {
  "bankCode": "SBI",
  "bankName": "State Bank of India",
  "branches": [...]
}

// Get branches for specific bank
GET /api/banks/{bankCode}/branches
Response: [
  {
    "branchId": "SBI_DEL_CP_001",
    "branchName": "Connaught Place",
    "ifscCode": "SBIN0000001",
    "address": {...}
  }
]

// Search branches by city/state
GET /api/banks/branches/search?city=Delhi&state=Delhi
GET /api/banks/branches/search?pincode=110001
```

### **Frontend Behavior:**
1. **Bank Selection**: Dropdown populated from `banks` collection
2. **Branch Selection**: Dynamically populated based on selected bank
3. **Auto-fill**: IFSC code and branch address auto-populated when branch is selected
4. **Search**: Users can search branches by city, state, or pincode

**This approach ensures:**
✅ **Centralized bank data** - Single source of truth  
✅ **Dynamic forms** - No hardcoded bank lists  
✅ **Auto-population** - Reduces data entry errors  
✅ **Easy maintenance** - Add/update banks without code changes  
✅ **Better UX** - Smart field dependencies and auto-fill

Is this clear? Would you like me to create the MongoDB setup script to insert this banks data or modify any part of the structure?