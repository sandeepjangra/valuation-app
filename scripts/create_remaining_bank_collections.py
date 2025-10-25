#!/usr/bin/env python3
"""
Create unified property details collections for HDFC, UCO, and CBI banks
"""
import json
import os
from datetime import datetime, timezone

def create_unified_bank_collection(bank_code, bank_full_name):
    """Create unified property collection for a bank"""
    
    # Read PNB template as base
    with open('/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend/data/pnb/pnb_all_property_details.json', 'r') as f:
        pnb_data = json.load(f)
    
    # Create bank-specific version
    bank_data = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "collection_name": f"{bank_code.lower()}_all_property_details",
            "total_documents": pnb_data["metadata"]["total_documents"],
            "version": "1.0",
            "database": "valuation_admin"
        },
        "documents": []
    }
    
    # Convert each document from PNB to the target bank
    for i, doc in enumerate(pnb_data["documents"]):
        bank_doc = convert_pnb_to_bank(doc, bank_code, bank_full_name, i)
        bank_data["documents"].append(bank_doc)
    
    # Create directory and save collection
    os.makedirs(f'/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend/data/{bank_code.lower()}', exist_ok=True)
    
    with open(f'/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend/data/{bank_code.lower()}/{bank_code.lower()}_all_property_details.json', 'w') as f:
        json.dump(bank_data, f, indent=2)
    
    print(f"✅ Created {bank_code} all property details collection")

def convert_pnb_to_bank(pnb_doc, bank_code, bank_full_name, doc_index):
    """Convert PNB document to target bank format"""
    bank_doc = json.loads(json.dumps(pnb_doc))  # Deep copy
    
    # Update basic fields
    bank_doc["templateId"] = bank_doc["templateId"].replace("PNB_", f"{bank_code}_")
    bank_doc["templateName"] = bank_doc["templateName"].replace("PNB", bank_code)
    bank_doc["bankCode"] = bank_code
    bank_doc["createdAt"] = datetime.now(timezone.utc).isoformat()
    bank_doc["updatedAt"] = datetime.now(timezone.utc).isoformat()
    
    # Generate new ObjectId
    import random
    bank_doc["_id"] = f"68fa78b4e25b49fc725d{(370 + doc_index + ord(bank_code[0]) * 10):03x}"
    
    # Update bank-specific options
    update_bank_specific_options(bank_doc, bank_code, bank_full_name)
    
    return bank_doc

def update_bank_specific_options(doc, bank_code, bank_full_name):
    """Update bank-specific field options"""
    
    # Update document options
    if "templateCategory" in doc and doc["templateCategory"] == "property_details":
        for field in doc.get("fields", []):
            if field.get("fieldId") == "list_of_documents":
                # Add bank-specific document requirements
                additional_docs = get_bank_specific_documents(bank_code)
                field["options"].extend(additional_docs)
                field["helpText"] = f"Select all applicable documents for {bank_code} valuation"
    
    # Update state options based on bank's regional presence
    update_state_options(doc, bank_code)

def get_bank_specific_documents(bank_code):
    """Get bank-specific document requirements"""
    bank_docs = {
        "HDFC": [
            {"value": "income_proof", "label": "Income Proof Documents"},
            {"value": "bank_statements", "label": "Bank Statements"},
            {"value": "insurance_policy", "label": "Property Insurance Policy"}
        ],
        "UCO": [
            {"value": "revenue_survey", "label": "Revenue Survey Records"},
            {"value": "patta_documents", "label": "Patta Documents"},
            {"value": "agricultural_records", "label": "Agricultural Land Records"}
        ],
        "CBI": [
            {"value": "government_approval", "label": "Government Approval Letters"},
            {"value": "clearance_certificate", "label": "Clearance Certificates"},
            {"value": "valuation_certificate", "label": "Previous Valuation Certificate"}
        ]
    }
    return bank_docs.get(bank_code, [])

def update_state_options(doc, bank_code):
    """Update state options based on bank's presence"""
    state_options = {
        "HDFC": [
            {"value": "maharashtra", "label": "Maharashtra"},
            {"value": "gujarat", "label": "Gujarat"},
            {"value": "karnataka", "label": "Karnataka"},
            {"value": "tamil_nadu", "label": "Tamil Nadu"},
            {"value": "delhi", "label": "Delhi"},
            {"value": "other", "label": "Other"}
        ],
        "UCO": [
            {"value": "west_bengal", "label": "West Bengal"},
            {"value": "odisha", "label": "Odisha"},
            {"value": "jharkhand", "label": "Jharkhand"},
            {"value": "bihar", "label": "Bihar"},
            {"value": "assam", "label": "Assam"},
            {"value": "other", "label": "Other"}
        ],
        "CBI": [
            {"value": "kerala", "label": "Kerala"},
            {"value": "tamil_nadu", "label": "Tamil Nadu"},
            {"value": "karnataka", "label": "Karnataka"},
            {"value": "andhra_pradesh", "label": "Andhra Pradesh"},
            {"value": "telangana", "label": "Telangana"},
            {"value": "other", "label": "Other"}
        ]
    }
    
    if "templateCategory" in doc and doc["templateCategory"] == "property_details":
        for field in doc.get("fields", []):
            if field.get("fieldId") == "property_location_details":
                for subfield in field.get("subFields", []):
                    if subfield.get("fieldId") == "state":
                        subfield["options"] = state_options.get(bank_code, [])

def main():
    """Create collections for all remaining banks"""
    banks = [
        ("HDFC", "HDFC Bank"),
        ("UCO", "UCO Bank"),
        ("CBI", "Central Bank of India")
    ]
    
    for bank_code, bank_name in banks:
        create_unified_bank_collection(bank_code, bank_name)

if __name__ == "__main__":
    main()