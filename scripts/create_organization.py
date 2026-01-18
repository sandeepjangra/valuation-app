#!/usr/bin/env python3
"""
Create or update organizations in MongoDB
"""
import os
import sys
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

# Get MongoDB connection string
MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    print("❌ MONGODB_URI not found in .env file")
    sys.exit(1)

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client['valuation_admin']
organizations_collection = db['organizations']

# Organization to create/update
system_admin_org = {
    "shortName": "system-administration",
    "fullName": "System Administration",
    "reportReferenceInitials": "SA",  # You can change this to whatever you want
    "lastReferenceNumber": 0,
    "isActive": True,
    "description": "System Administration Organization",
    "contactEmail": "admin@valuation-app.com",
    "contactPhone": "+1-234-567-8900",
    "createdAt": datetime.now(timezone.utc),
    "updatedAt": datetime.now(timezone.utc)
}

# Check if organization already exists
existing_org = organizations_collection.find_one({"shortName": "system-administration"})

if existing_org:
    print(f"📝 Organization 'system-administration' already exists")
    print(f"   Current reportReferenceInitials: {existing_org.get('reportReferenceInitials', 'NOT SET')}")
    print(f"   Current lastReferenceNumber: {existing_org.get('lastReferenceNumber', 0)}")
    
    # Update only if reportReferenceInitials is not set
    if not existing_org.get('reportReferenceInitials'):
        result = organizations_collection.update_one(
            {"shortName": "system-administration"},
            {
                "$set": {
                    "reportReferenceInitials": "SA",
                    "updatedAt": datetime.now(timezone.utc)
                }
            }
        )
        print(f"✅ Updated organization with reportReferenceInitials: SA")
    else:
        print(f"ℹ️  reportReferenceInitials already set, no update needed")
else:
    # Insert new organization
    result = organizations_collection.insert_one(system_admin_org)
    print(f"✅ Created new organization 'system-administration'")
    print(f"   ID: {result.inserted_id}")
    print(f"   reportReferenceInitials: SA")
    print(f"   lastReferenceNumber: 0")

print("\n📊 All organizations in database:")
for org in organizations_collection.find():
    print(f"   - {org['shortName']} ({org['fullName']})")
    print(f"     Initials: {org.get('reportReferenceInitials', 'NOT SET')}")
    print(f"     Last Ref#: {org.get('lastReferenceNumber', 0)}")
    print()

client.close()
print("✅ Done!")
