#!/usr/bin/env python3
"""
Script to check document_types collection
"""

import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv('/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend/.env')

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    print("❌ MONGODB_URI environment variable not found")
    sys.exit(1)

def check_document_types():
    """Check document_types collection"""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_URI, tlsAllowInvalidCertificates=True)
        db = client.valuation_admin
        
        print("🔍 Checking document_types collection...")
        
        # Check if collection exists
        collections = db.list_collection_names()
        print(f"📋 Available collections: {collections}")
        
        if "document_types" not in collections:
            print("❌ document_types collection not found")
            return False
        
        # Get documents
        doc_types_collection = db.document_types
        docs = list(doc_types_collection.find({}))
        
        print(f"📄 Found {len(docs)} documents in document_types")
        
        if len(docs) > 0:
            first_doc = docs[0]
            print(f"📋 First document structure: {list(first_doc.keys())}")
            print(f"📋 First document: {json.dumps(first_doc, indent=2, default=str)}")
            
            # Check for SBI land property documents
            sbi_land_docs = list(doc_types_collection.find({
                "bankCode": "SBI", 
                "propertyType": "land"
            }))
            
            print(f"\n🏦 Found {len(sbi_land_docs)} SBI land property documents")
            
            if len(sbi_land_docs) > 0:
                print("📋 SBI land document fields:")
                for doc in sbi_land_docs:
                    print(f"  - {doc.get('documentType', 'Unknown')}: {doc.get('description', 'No description')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    check_document_types()