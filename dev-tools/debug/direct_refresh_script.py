#!/usr/bin/env python3
"""
Direct MongoDB Collection Refresh Script
Directly connects to MongoDB and refreshes common_fields and banks collections
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List
from pymongo import MongoClient
from bson import ObjectId

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB Configuration
MONGODB_URI = "mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster"
DATABASE_NAME = "valuation_admin"

# Local file paths
DATA_DIR = Path(__file__).parent / "backend" / "data"
DATA_DIR.mkdir(exist_ok=True)

def serialize_mongodb_doc(obj):
    """Convert MongoDB document to JSON serializable format"""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: serialize_mongodb_doc(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize_mongodb_doc(item) for item in obj]
    return obj

def test_connection():
    """Test MongoDB connection"""
    logger.info("🔍 Testing MongoDB connection...")
    try:
        client = MongoClient(MONGODB_URI, 
                           serverSelectionTimeoutMS=10000,
                           tlsAllowInvalidCertificates=True)
        client.admin.command('ping')
        
        # List databases
        databases = client.list_database_names()
        logger.info(f"✅ Connected to MongoDB. Available databases: {databases}")
        
        # Check specific database
        if DATABASE_NAME in databases:
            db = client[DATABASE_NAME]
            collections = db.list_collection_names()
            logger.info(f"✅ Database '{DATABASE_NAME}' exists with collections: {collections}")
            
            # Check common_form_fields collection
            if "common_form_fields" in collections:
                count = db.common_form_fields.count_documents({})
                logger.info(f"📊 common_form_fields collection has {count} documents")
                
                # Show sample document
                sample = db.common_form_fields.find_one({})
                if sample:
                    logger.info(f"📄 Sample document keys: {list(sample.keys())}")
            
            # Check banks collection
            if "banks" in collections:
                count = db.banks.count_documents({})
                logger.info(f"📊 banks collection has {count} documents")
        else:
            logger.error(f"❌ Database '{DATABASE_NAME}' not found")
            return False
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        return False

def refresh_common_fields():
    """Refresh common_fields collection from MongoDB"""
    logger.info("🔄 Refreshing common_fields from MongoDB...")
    
    try:
        client = MongoClient(MONGODB_URI, 
                           serverSelectionTimeoutMS=10000,
                           tlsAllowInvalidCertificates=True)
        db = client[DATABASE_NAME]
        
        # Fetch all common form fields
        documents = list(db.common_form_fields.find({}))
        logger.info(f"📊 Retrieved {len(documents)} documents from common_form_fields")
        
        # Sort by fieldGroup and sortOrder
        documents.sort(key=lambda x: (x.get('fieldGroup', ''), x.get('sortOrder', 0)))
        
        # Serialize documents
        serialized_docs = [serialize_mongodb_doc(doc) for doc in documents]
        
        # Create file content
        file_content = {
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "collection_name": "common_fields",
                "total_documents": len(serialized_docs),
                "version": "1.0",
                "database": DATABASE_NAME,
                "source_collection": "common_form_fields"
            },
            "documents": serialized_docs
        }
        
        # Write to file
        output_file = DATA_DIR / "common_fields.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(file_content, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Successfully wrote {len(serialized_docs)} documents to {output_file}")
        logger.info(f"📄 File size: {output_file.stat().st_size} bytes")
        
        # Show sample fields
        if serialized_docs:
            sample_fields = [doc.get('fieldId', 'unknown') for doc in serialized_docs[:5]]
            logger.info(f"📋 Sample fields: {sample_fields}")
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to refresh common_fields: {e}")
        return False

def refresh_banks():
    """Refresh banks collection from MongoDB"""
    logger.info("🔄 Refreshing banks from MongoDB...")
    
    try:
        client = MongoClient(MONGODB_URI, 
                           serverSelectionTimeoutMS=10000,
                           tlsAllowInvalidCertificates=True)
        db = client[DATABASE_NAME]
        
        # Fetch all banks
        documents = list(db.banks.find({}))
        logger.info(f"📊 Retrieved {len(documents)} documents from banks")
        
        # Serialize documents
        serialized_docs = [serialize_mongodb_doc(doc) for doc in documents]
        
        # Create file content
        file_content = {
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "collection_name": "banks",
                "total_documents": len(serialized_docs),
                "version": "1.0",
                "database": DATABASE_NAME,
                "source_collection": "banks"
            },
            "documents": serialized_docs
        }
        
        # Write to file
        output_file = DATA_DIR / "banks.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(file_content, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Successfully wrote {len(serialized_docs)} documents to {output_file}")
        logger.info(f"📄 File size: {output_file.stat().st_size} bytes")
        
        # Show sample banks
        if serialized_docs:
            sample_banks = [doc.get('bankName', doc.get('bankCode', 'unknown')) for doc in serialized_docs[:3]]
            logger.info(f"🏦 Sample banks: {sample_banks}")
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to refresh banks: {e}")
        return False

def main():
    """Main function"""
    print("="*60)
    print("🔄 MongoDB Collection Refresh Script")
    print("="*60)
    print(f"📡 Database: {DATABASE_NAME}")
    print(f"📁 Output Directory: {DATA_DIR}")
    print("="*60)
    
    # Test connection first
    if not test_connection():
        print("❌ Cannot proceed without database connection")
        return False
    
    print("\nWhat would you like to refresh?")
    print("1. Common Fields only")
    print("2. Banks only")
    print("3. Both collections")
    print("4. Test connection only")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    success = True
    
    if choice == "1":
        success = refresh_common_fields()
    elif choice == "2":
        success = refresh_banks()
    elif choice == "3":
        print("\n" + "="*40)
        print("Refreshing both collections...")
        print("="*40)
        success1 = refresh_common_fields()
        print()
        success2 = refresh_banks()
        success = success1 and success2
    elif choice == "4":
        print("✅ Connection test completed successfully")
        return True
    else:
        print("❌ Invalid choice")
        return False
    
    if success:
        print(f"\n✅ Refresh completed successfully!")
        print(f"📁 Files saved to: {DATA_DIR}")
        print(f"🌐 You can now test the API endpoints")
    else:
        print(f"\n❌ Refresh failed!")
    
    return success

if __name__ == "__main__":
    main()