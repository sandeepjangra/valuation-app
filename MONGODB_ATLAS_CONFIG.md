# 🌐 MongoDB Atlas Cloud Configuration

## 📊 **Complete Collection Schema Design**

### **4. Users Collection**
```json
{
  "_id": ObjectId("..."),
  "userId": "EMP001",
  "email": "valuator1@company.com",
  "password": "$2b$12$hashedPassword",
  "profile": {
    "firstName": "Rajesh",
    "lastName": "Kumar",
    "displayName": "Rajesh Kumar",
    "phone": "+91-9876543210",
    "avatar": "https://cdn.example.com/avatars/rajesh.jpg"
  },
  "role": "EMPLOYEE", // EMPLOYEE, MANAGER, ADMIN
  "permissions": {
    "canCreateReports": true,
    "canApproveReports": false,
    "canManageUsers": false,
    "canViewAllReports": false,
    "assignedBanks": ["SBI", "PNB"] // Which banks this user can create reports for
  },
  "valuationLicense": {
    "licenseNumber": "REG/VAL/2024/001",
    "issuedBy": "Government Approved Valuation Institute",
    "validFrom": new Date("2024-01-01"),
    "validUntil": new Date("2026-12-31"),
    "isActive": true
  },
  "managerId": ObjectId("manager_user_id"), // For EMPLOYEE role
  "lastLogin": new Date("2025-10-17T10:30:00Z"),
  "isActive": true,
  "createdAt": new Date("2025-01-01"),
  "updatedAt": new Date("2025-10-17")
}
```

### **5. Valuation Reports Collection**
```json
{
  "_id": ObjectId("..."),
  "reportId": "SBI_2025_001234",
  "templateId": ObjectId("template_id"),
  "bankId": ObjectId("bank_id"),
  "propertyTypeId": ObjectId("property_type_id"),
  "reportMetadata": {
    "title": "Residential Flat Valuation - Sector 62, Noida",
    "reportType": "HOME_LOAN_VALUATION",
    "urgency": "NORMAL", // URGENT, NORMAL, LOW
    "estimatedValue": 8500000,
    "currency": "INR"
  },
  "borrowerInfo": {
    "name": "Amit Sharma",
    "contact": "9876543210",
    "email": "amit.sharma@email.com",
    "address": "123, Green Avenue, Sector 62, Noida",
    "loanAmount": 6800000,
    "loanType": "HOME_LOAN"
  },
  "propertyDetails": {
    // Dynamic fields based on template
    "property_address": "Flat No. 1205, Tower A, Supertech Emerald Court, Sector 93A, Noida",
    "property_pincode": "201304",
    "property_type_detail": "3BHK",
    "floor_number": 12,
    "carpet_area": 1250,
    "built_up_area": 1450,
    "super_built_up_area": 1812.5,
    "market_rate_per_sqft": 6800,
    "distress_sale_rate": 5440,
    "fair_market_value": 8500000,
    "forced_sale_value": 6800000,
    "valuer_opinion": "The property is well-maintained with good market prospects...",
    "final_property_value": 8500000
  },
  "attachments": [
    {
      "fileId": ObjectId("gridfs_file_id"),
      "fileName": "property_front_view.jpg",
      "fileType": "image/jpeg",
      "fileSize": 2048576,
      "uploadedAt": new Date("2025-10-17"),
      "category": "PROPERTY_PHOTOS"
    }
  ],
  "workflow": {
    "status": "APPROVED", // DRAFT, SUBMITTED, UNDER_REVIEW, APPROVED, REJECTED, DELIVERED
    "submittedBy": ObjectId("employee_user_id"),
    "submittedAt": new Date("2025-10-17T09:00:00Z"),
    "reviewedBy": ObjectId("manager_user_id"),
    "reviewedAt": new Date("2025-10-17T11:30:00Z"),
    "approvalComments": "Report is comprehensive and valuation is appropriate for the location.",
    "deliveryStatus": "PENDING", // PENDING, SENT, DELIVERED, ACKNOWLEDGED
    "deliveryMode": "HARDCOPY" // HARDCOPY, EMAIL, PORTAL_UPLOAD
  },
  "auditTrail": [
    {
      "action": "CREATED",
      "performedBy": ObjectId("employee_user_id"),
      "timestamp": new Date("2025-10-17T08:00:00Z"),
      "details": "Report created"
    },
    {
      "action": "SUBMITTED",
      "performedBy": ObjectId("employee_user_id"),
      "timestamp": new Date("2025-10-17T09:00:00Z"),
      "details": "Report submitted for approval"
    },
    {
      "action": "APPROVED",
      "performedBy": ObjectId("manager_user_id"),
      "timestamp": new Date("2025-10-17T11:30:00Z"),
      "details": "Report approved with comments"
    }
  ],
  "reportGeneration": {
    "generatedPdfPath": "/reports/2025/SBI_2025_001234.pdf",
    "generatedAt": new Date("2025-10-17T11:35:00Z"),
    "reportSize": "2.4MB",
    "digitalSignature": {
      "isSigned": true,
      "signedBy": ObjectId("manager_user_id"),
      "signedAt": new Date("2025-10-17T11:35:00Z"),
      "certificateHash": "SHA256:abc123..."
    }
  },
  "createdAt": new Date("2025-10-17T08:00:00Z"),
  "updatedAt": new Date("2025-10-17T11:35:00Z")
}
```

### **6. Report Drafts Collection** (Separate for Performance)
```json
{
  "_id": ObjectId("..."),
  "userId": ObjectId("employee_user_id"),
  "templateId": ObjectId("template_id"),
  "draftData": {
    // Partially filled form data
    "property_address": "Flat No. 1205, Tower A, Supertech Emerald Court",
    "borrower_name": "Amit Sharma",
    // ... other partial data
  },
  "lastSavedAt": new Date("2025-10-17T10:15:00Z"),
  "expiresAt": new Date("2025-11-16T10:15:00Z"), // 30 days from creation
  "autoSaveVersion": 15
}
```

### **7. Audit Logs Collection**
```json
{
  "_id": ObjectId("..."),
  "userId": ObjectId("user_id"),
  "action": "REPORT_APPROVED",
  "resourceType": "VALUATION_REPORT",
  "resourceId": ObjectId("report_id"),
  "ipAddress": "192.168.1.100",
  "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
  "sessionId": "sess_abc123",
  "details": {
    "reportId": "SBI_2025_001234",
    "previousStatus": "UNDER_REVIEW",
    "newStatus": "APPROVED",
    "comments": "Report approved after review"
  },
  "timestamp": new Date("2025-10-17T11:30:00Z")
}
```

## 🚀 **MongoDB Atlas Setup Configuration**

### **1. Cluster Configuration**
```javascript
// Recommended MongoDB Atlas Configuration
{
  "clusterName": "ValuationApp-Production",
  "tier": "M10", // For production (2GB RAM, 10GB Storage)
  "region": "AP-SOUTH-1", // Mumbai region for Indian users
  "version": "7.0",
  "features": {
    "backupEnabled": true,
    "performanceAdvisorEnabled": true,
    "realtimePerformancePanelEnabled": true
  }
}
```

### **2. Database Structure**
```javascript
// Database: valuation_app_prod
{
  collections: [
    "banks",
    "property_types", 
    "templates",
    "users",
    "valuation_reports",
    "report_drafts",
    "audit_logs",
    "fs.files",      // GridFS for file storage
    "fs.chunks"      // GridFS chunks
  ]
}
```

### **3. Indexes for Performance**
```javascript
// Critical indexes for MongoDB Atlas
db.valuation_reports.createIndex({ "reportId": 1 }, { unique: true })
db.valuation_reports.createIndex({ "bankId": 1, "workflow.status": 1 })
db.valuation_reports.createIndex({ "workflow.submittedBy": 1, "createdAt": -1 })
db.valuation_reports.createIndex({ "borrowerInfo.contact": 1 })

db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "role": 1, "isActive": 1 })

db.templates.createIndex({ "bankId": 1, "propertyTypeId": 1, "isActive": 1 })

db.report_drafts.createIndex({ "userId": 1, "templateId": 1 })
db.report_drafts.createIndex({ "expiresAt": 1 }, { expireAfterSeconds: 0 })

db.audit_logs.createIndex({ "userId": 1, "timestamp": -1 })
db.audit_logs.createIndex({ "resourceType": 1, "resourceId": 1 })
```

### **4. Security Configuration**
```javascript
// Database Users and Roles
{
  "users": [
    {
      "username": "app_user",
      "password": "securePassword123!",
      "roles": [
        {
          "role": "readWrite",
          "db": "valuation_app_prod"
        }
      ]
    },
    {
      "username": "readonly_user", 
      "password": "readOnlyPass456!",
      "roles": [
        {
          "role": "read",
          "db": "valuation_app_prod"
        }
      ]
    }
  ]
}

// Network Access
{
  "ipWhitelist": [
    "0.0.0.0/0" // Initially allow all, restrict in production
  ]
}
```

## 🔧 **Connection Configuration**

### **Environment Variables (.env)**
```bash
# MongoDB Atlas Configuration
MONGODB_URI=mongodb+srv://app_user:securePassword123!@valuationapp-production.abcde.mongodb.net/valuation_app_prod?retryWrites=true&w=majority
MONGODB_DB_NAME=valuation_app_prod

# Application Configuration
JWT_SECRET=your-super-secret-jwt-key-here
JWT_EXPIRE_IN=24h
BCRYPT_ROUNDS=12

# File Upload Configuration  
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=jpg,jpeg,png,pdf,doc,docx

# Email Configuration (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# Application Settings
NODE_ENV=production
PORT=3000
BASE_URL=https://your-domain.com
```

### **MongoDB Connection (Python/FastAPI)**
```python
# config/database.py
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import gridfs

class MongoDB:
    client: AsyncIOMotorClient = None
    database = None
    gridfs_bucket = None

# MongoDB connection setup
async def connect_to_mongo():
    MongoDB.client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
    MongoDB.database = MongoDB.client[os.getenv("MONGODB_DB_NAME")]
    
    # Test connection
    await MongoDB.client.admin.command('ping')
    print("✅ Connected to MongoDB Atlas successfully!")
    
    # Setup GridFS for file storage
    MongoDB.gridfs_bucket = gridfs.GridFSBucket(MongoDB.database)
    
async def close_mongo_connection():
    MongoDB.client.close()
    print("❌ Disconnected from MongoDB Atlas")

# Usage in FastAPI
from fastapi import FastAPI

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown") 
async def shutdown_event():
    await close_mongo_connection()
```

## 📈 **Next Implementation Steps**

1. **Setup MongoDB Atlas Cluster** - Create account and configure cluster
2. **Create Initial Collections** - Run setup scripts to create collections with indexes
3. **Implement User Authentication** - JWT-based authentication system
4. **Build Template Engine** - Dynamic form generation from MongoDB templates
5. **File Upload System** - GridFS integration for document storage
6. **Report Generation** - PDF generation from submitted data
7. **Approval Workflow** - Manager approval system implementation

Would you like me to create the actual MongoDB Atlas setup scripts and connection code for your cloud database?