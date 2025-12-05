#!/usr/bin/env python3
"""
Script to check SBI land document types with correct query
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

def check_sbi_land_documents():
    """Check SBI land documents with correct query"""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_URI, tlsAllowInvalidCertificates=True)
        db = client.valuation_admin
        
        print("🔍 Checking SBI land documents...")
        
        doc_types_collection = db.document_types
        
        # Correct query for SBI and Land
        sbi_land_docs = list(doc_types_collection.find({
            "applicableBanks": {"$in": ["SBI", "*"]},
            "applicablePropertyTypes": {"$in": ["Land", "land"]},
            "isActive": True
        }))
        
        print(f"🏦 Found {len(sbi_land_docs)} SBI land property documents")
        
        if len(sbi_land_docs) > 0:
            print("\n📋 SBI land document types:")
            for doc in sbi_land_docs:
                print(f"  - {doc.get('documentId')}: {doc.get('uiDisplayName')}")
                print(f"    Type: {doc.get('fieldType')}, Required: {doc.get('isRequired')}")
        else:
            # Check what's actually available
            print("\n🔍 All available documents:")
            all_docs = list(doc_types_collection.find({"isActive": True}))
            for doc in all_docs[:5]:  # Show first 5
                print(f"  - {doc.get('documentId')}: Banks: {doc.get('applicableBanks')}, Types: {doc.get('applicablePropertyTypes')}")
        
        return sbi_land_docs
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    docs = check_sbi_land_documents()
    print(f"\n📊 Total applicable documents: {len(docs)}")