#!/usr/bin/env python3
"""
Analyze Organizations Collection Structure
"""

from pymongo import MongoClient
from dotenv import load_dotenv
import os
import json

load_dotenv()

def analyze_organizations():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client['valuation_admin']
    
    print("🔍 ANALYZING ORGANIZATIONS COLLECTION\n")
    
    # Get all organizations
    orgs = list(db.organizations.find())
    
    print(f"� Total Organizations: {len(orgs)}\n")
    
    for i, org in enumerate(orgs, 1):
        print(f"{'='*80}")
        print(f"Organization #{i}: {org.get('shortName', 'N/A')}")
        print(f"{'='*80}")
        print(json.dumps(org, indent=2, default=str))
        print()
    
    if len(orgs) > 0:
        print(f"\n� Organization Fields:")
        for key in orgs[0].keys():
            print(f"   • {key}")
    
    client.close()

if __name__ == "__main__":
    analyze_organizations()
