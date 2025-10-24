#!/usr/bin/env python3
"""
Create sample collection files for testing (no MongoDB required)
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime, timezone

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_sample_collections():
    """Create sample collection files for testing"""
    print("🧪 Creating sample collection files for testing...")
    
    # Setup data directory
    data_dir = Path(__file__).parent / "backend" / "data"
    data_dir.mkdir(exist_ok=True)
    
    def write_collection_file(collection_name: str, documents: list, database: str, description: str):
        """Write a collection file with metadata"""
        metadata = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "collection_name": collection_name,
            "total_documents": len(documents),
            "version": "1.0",
            "database": database
        }
        
        data = {
            "metadata": metadata,
            "documents": documents
        }
        
        file_path = data_dir / f"{collection_name}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Created {collection_name}.json with {len(documents)} documents")
    
    # Sample banks data
    banks_data = [
        {
            "_id": "bank_001",
            "bankCode": "SBI",
            "bankName": "State Bank of India",
            "branches": [
                {"branchId": "SBI001", "branchName": "Mumbai Main", "ifscCode": "SBIN0000001"},
                {"branchId": "SBI002", "branchName": "Delhi Main", "ifscCode": "SBIN0000002"}
            ]
        },
        {
            "_id": "bank_002",
            "bankCode": "HDFC",
            "bankName": "HDFC Bank",
            "branches": [
                {"branchId": "HDFC001", "branchName": "Bandra West", "ifscCode": "HDFC0000001"},
                {"branchId": "HDFC002", "branchName": "CP Delhi", "ifscCode": "HDFC0000002"}
            ]
        },
        {
            "_id": "bank_003",
            "bankCode": "ICICI",
            "bankName": "ICICI Bank",
            "branches": [
                {"branchId": "ICICI001", "branchName": "Andheri East", "ifscCode": "ICIC0000001"},
                {"branchId": "ICICI002", "branchName": "Gurgaon Sector 14", "ifscCode": "ICIC0000002"}
            ]
        }
    ]
    
    # Sample users data
    users_data = [
        {
            "_id": "user_001",
            "username": "admin",
            "email": "admin@valuation.com",
            "role": "admin",
            "firstName": "System",
            "lastName": "Administrator",
            "createdAt": "2024-01-01T00:00:00Z",
            "isActive": True
        },
        {
            "_id": "user_002",
            "username": "valuator1",
            "email": "valuator1@valuation.com",
            "role": "valuator",
            "firstName": "John",
            "lastName": "Smith",
            "createdAt": "2024-01-15T09:30:00Z",
            "isActive": True
        },
        {
            "_id": "user_003",
            "username": "valuator2",
            "email": "valuator2@valuation.com",
            "role": "valuator",
            "firstName": "Sarah",
            "lastName": "Johnson",
            "createdAt": "2024-02-01T14:20:00Z",
            "isActive": True
        }
    ]
    
    # Sample properties data
    properties_data = [
        {
            "_id": "prop_001",
            "address": "123 Sample Street, Bandra West, Mumbai",
            "propertyType": "residential",
            "area": 1200,
            "bedrooms": 3,
            "bathrooms": 2,
            "status": "pending_valuation",
            "createdAt": "2024-03-01T10:00:00Z"
        },
        {
            "_id": "prop_002",
            "address": "456 Test Avenue, Connaught Place, Delhi",
            "propertyType": "commercial",
            "area": 2500,
            "floors": 2,
            "status": "valuated",
            "createdAt": "2024-03-05T11:30:00Z"
        },
        {
            "_id": "prop_003",
            "address": "789 Demo Road, Whitefield, Bangalore",
            "propertyType": "residential",
            "area": 1800,
            "bedrooms": 4,
            "bathrooms": 3,
            "status": "in_progress",
            "createdAt": "2024-03-10T09:15:00Z"
        }
    ]
    
    # Sample valuations data
    valuations_data = [
        {
            "_id": "val_001",
            "propertyId": "prop_001",
            "valuatorId": "user_002",
            "estimatedValue": 12500000,
            "currency": "INR",
            "valuationDate": "2024-03-15T00:00:00Z",
            "status": "completed",
            "methodology": "comparative_market_analysis"
        },
        {
            "_id": "val_002",
            "propertyId": "prop_002",
            "valuatorId": "user_003",
            "estimatedValue": 35000000,
            "currency": "INR",
            "valuationDate": "2024-03-20T00:00:00Z",
            "status": "completed",
            "methodology": "income_approach"
        }
    ]
    
    # Sample valuation reports data
    valuation_reports_data = [
        {
            "_id": "report_001",
            "valuationId": "val_001",
            "reportType": "detailed",
            "generatedAt": "2024-03-16T12:00:00Z",
            "fileSize": 2456789,
            "status": "generated"
        },
        {
            "_id": "report_002",
            "valuationId": "val_002",
            "reportType": "summary",
            "generatedAt": "2024-03-21T10:30:00Z",
            "fileSize": 1234567,
            "status": "generated"
        }
    ]
    
    # Sample audit logs data
    audit_logs_data = [
        {
            "_id": "audit_001",
            "operation": "CREATE",
            "database": "main",
            "collection": "properties",
            "documentId": "prop_001",
            "userId": "user_001",
            "userName": "admin",
            "timestamp": "2024-03-01T10:00:00Z",
            "changes": {"address": "123 Sample Street, Bandra West, Mumbai"}
        },
        {
            "_id": "audit_002",
            "operation": "UPDATE",
            "database": "main",
            "collection": "valuations",
            "documentId": "val_001",
            "userId": "user_002",
            "userName": "valuator1",
            "timestamp": "2024-03-15T15:30:00Z",
            "changes": {"status": "completed"}
        },
        {
            "_id": "audit_003",
            "operation": "CREATE",
            "database": "reports",
            "collection": "valuation_reports",
            "documentId": "report_001",
            "userId": "user_002",
            "userName": "valuator1",
            "timestamp": "2024-03-16T12:00:00Z",
            "changes": {"reportType": "detailed"}
        }
    ]
    
    # Create all collection files
    collections = [
        ("banks", banks_data, "admin", "Bank and branch information"),
        ("users", users_data, "main", "User accounts and profiles"),
        ("properties", properties_data, "main", "Property records"),
        ("valuations", valuations_data, "main", "Valuation assessments"),
        ("valuation_reports", valuation_reports_data, "reports", "Generated valuation reports"),
        ("audit_logs", audit_logs_data, "reports", "System audit trails")
    ]
    
    for collection_name, data, database, description in collections:
        write_collection_file(collection_name, data, database, description)
    
    print(f"\n🎯 Sample collection files created successfully in {data_dir}")
    print(f"📊 Total collections: {len(collections)}")
    
    # Show summary
    total_docs = sum(len(data) for _, data, _, _ in collections)
    print(f"📋 Total documents: {total_docs}")
    print("\n📁 Files created:")
    for collection_name, data, database, description in collections:
        print(f"   • {collection_name}.json ({len(data)} docs) - {database} DB")

if __name__ == "__main__":
    create_sample_collections()