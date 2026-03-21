#!/usr/bin/env python3
"""Verify all MongoDB migrations"""

from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv('MONGODB_URI'))
db = client['valuation_templates']

print("🗄️  MONGODB ATLAS - valuation_templates Database")
print("="*80)

# Get collection names
collections = db.list_collection_names()
print(f"\n📊 Collections: {len(collections)}")
for coll_name in collections:
    coll = db[coll_name]
    count = coll.count_documents({})
    print(f"   • {coll_name}: {count} document(s)")

# Templates
print(f"\n📋 Templates Collection:")
templates = list(db.templates.find({}, {"TemplateId": 1, "BankDetails.BankCode": 1, "PropertyType": 1}))
for t in templates:
    bank = t.get('BankDetails', {}).get('BankCode', 'N/A')
    prop = t.get('PropertyType', 'N/A')
    template_id = t.get('TemplateId', 'N/A')
    print(f"   ✅ {bank} - {prop} ({template_id})")

# Banks
print(f"\n🏦 Banks Collection:")
banks_doc = db.banks.find_one({})
if banks_doc:
    banks = banks_doc.get('Banks', [])
    print(f"   Total banks: {len(banks)}")
    for bank in banks:
        code = bank.get('BankCode', 'N/A')
        name = bank.get('BankName', 'N/A')
        branches = len(bank.get('Branches', []))
        templates = len(bank.get('Templates', []))
        print(f"   ✅ {code} - {name} ({branches} branches, {templates} templates)")

# Organizations
print(f"\n🏢 Organizations Collection:")
orgs_doc = db.organizations.find_one({})
if orgs_doc:
    orgs = orgs_doc.get('Organizations', [])
    print(f"   Total organizations: {len(orgs)}")
    for org in orgs:
        short = org.get('ShortName', 'N/A')
        full = org.get('FullName', 'N/A')
        ref = org.get('ReportReferenceInitials', 'N/A')
        active = "✅ Active" if org.get('IsActive') else "⚠️ Inactive"
        print(f"   {active} {short} - {full} ({ref})")

client.close()
print(f"\n{'='*80}")
print("✅ Verification Complete")
