"""
Deep search for kd_tindwal and valuation organizations
"""

import os
from pymongo import MongoClient

mongodb_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongodb_uri, tlsAllowInvalidCertificates=True)

print("=" * 80)
print("🔍 SEARCHING FOR kd_tindwal AND valuation ORGANIZATIONS")
print("=" * 80)

# Get all databases
print("\n📊 All Databases:")
for db_name in client.list_database_names():
    print(f"   - {db_name}")

# Search in valuation_001 database
db = client["valuation_001"]

print("\n📊 All Collections in valuation_001:")
for coll_name in db.list_collection_names():
    print(f"   - {coll_name}")

# Search for any documents containing 'kd_tindwal' or 'valuation'
print("\n🔍 Searching for 'kd_tindwal' in all collections...")

for coll_name in db.list_collection_names():
    collection = db[coll_name]
    
    # Search in all fields
    results = collection.find({
        "$or": [
            {"organization_id": {"$regex": "kd_tindwal", "$options": "i"}},
            {"org_id": {"$regex": "kd_tindwal", "$options": "i"}},
            {"org_name": {"$regex": "kd_tindwal", "$options": "i"}},
            {"org_short_name": {"$regex": "kd_tindwal", "$options": "i"}},
            {"name": {"$regex": "kd_tindwal", "$options": "i"}},
        ]
    })
    
    count = len(list(results))
    if count > 0:
        print(f"\n✅ Found {count} documents in '{coll_name}':")
        results = collection.find({
            "$or": [
                {"organization_id": {"$regex": "kd_tindwal", "$options": "i"}},
                {"org_id": {"$regex": "kd_tindwal", "$options": "i"}},
                {"org_name": {"$regex": "kd_tindwal", "$options": "i"}},
                {"org_short_name": {"$regex": "kd_tindwal", "$options": "i"}},
                {"name": {"$regex": "kd_tindwal", "$options": "i"}},
            ]
        })
        for doc in results:
            print(f"   Document ID: {doc.get('_id')}")
            print(f"   Fields: {list(doc.keys())}")
            # Print relevant fields
            for key in ['organization_id', 'org_id', 'org_name', 'org_short_name', 'name']:
                if key in doc:
                    print(f"   {key}: {doc[key]}")

print("\n🔍 Searching for 'valuation' organization (not database name)...")

for coll_name in db.list_collection_names():
    collection = db[coll_name]
    
    # Search for organization named 'valuation'
    results = collection.find({
        "$or": [
            {"organization_id": "valuation"},
            {"org_id": "valuation"},
            {"org_name": "valuation"},
            {"org_short_name": "valuation"},
            {"name": "valuation"},
        ]
    })
    
    count = len(list(results))
    if count > 0:
        print(f"\n✅ Found {count} documents in '{coll_name}':")
        results = collection.find({
            "$or": [
                {"organization_id": "valuation"},
                {"org_id": "valuation"},
                {"org_name": "valuation"},
                {"org_short_name": "valuation"},
                {"name": "valuation"},
            ]
        })
        for doc in results:
            print(f"   Document ID: {doc.get('_id')}")
            print(f"   Fields: {list(doc.keys())}")
            for key in ['organization_id', 'org_id', 'org_name', 'org_short_name', 'name']:
                if key in doc:
                    print(f"   {key}: {doc[key]}")

# Check if there are organization-specific databases
print("\n🔍 Checking for organization-specific databases...")
for db_name in client.list_database_names():
    if 'kd_tindwal' in db_name.lower() or db_name == 'valuation':
        print(f"\n✅ Found organization database: {db_name}")
        org_db = client[db_name]
        print(f"   Collections: {org_db.list_collection_names()}")

client.close()

print("\n" + "=" * 80)
print("🔍 SEARCH COMPLETE")
print("=" * 80)
