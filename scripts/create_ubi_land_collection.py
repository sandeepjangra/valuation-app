#!/usr/bin/env python3
"""
Create UBI Land Property Details collection based on SBI structure
"""
import json
import re
from datetime import datetime, timezone

def create_ubi_land_collection():
    """Create UBI land property details by modifying SBI structure"""
    
    # Read the SBI land collection
    with open('/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend/data/sbi/land/sbi_land_property_details.json', 'r') as f:
        sbi_data = json.load(f)
    
    # Create UBI version
    ubi_data = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "collection_name": "ubi_land_property_details",
            "total_documents": sbi_data["metadata"]["total_documents"],
            "version": "1.0",
            "database": "valuation_admin"
        },
        "documents": []
    }
    
    # Convert each document from SBI to UBI
    for doc in sbi_data["documents"]:
        ubi_doc = convert_sbi_to_ubi(doc)
        ubi_data["documents"].append(ubi_doc)
    
    # Save UBI collection
    with open('/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend/data/ubi/land/ubi_land_property_details.json', 'w') as f:
        json.dump(ubi_data, f, indent=2)
    
    print("✅ Created UBI land property details collection")

def convert_sbi_to_ubi(sbi_doc):
    """Convert SBI document to UBI format"""
    ubi_doc = json.loads(json.dumps(sbi_doc))  # Deep copy
    
    # Update basic fields
    ubi_doc["templateId"] = ubi_doc["templateId"].replace("SBI_", "UBI_")
    ubi_doc["templateName"] = ubi_doc["templateName"].replace("SBI", "UBI")
    ubi_doc["bankCode"] = "UBI"
    ubi_doc["createdAt"] = datetime.now(timezone.utc).isoformat()
    ubi_doc["updatedAt"] = datetime.now(timezone.utc).isoformat()
    
    # Generate new ObjectId
    import random
    ubi_doc["_id"] = f"68fa78b4e25b49fc725d{random.randint(400, 499):03x}"
    
    # Update UBI-specific document options
    if "templateCategory" in ubi_doc and ubi_doc["templateCategory"] == "property_details":
        # Update document options for UBI
        for field in ubi_doc.get("fields", []):
            if field.get("fieldId") == "list_of_documents":
                field["options"] = [
                    {"value": "revenue_records", "label": "Revenue Records"},
                    {"value": "survey_settlement", "label": "Survey Settlement Records"},
                    {"value": "mutation_records", "label": "Mutation Records"},
                    {"value": "title_documents", "label": "Title Documents"}
                ]
                field["helpText"] = "Select applicable UBI documents"
    
    # Update municipal corporation options for UBI areas
    if "templateCategory" in ubi_doc and ubi_doc["templateCategory"] == "property_details":
        for field in ubi_doc.get("fields", []):
            if field.get("fieldId") == "municipal_corporation":
                field["options"] = [
                    {"value": "kolkata", "label": "Kolkata Municipal Corporation"},
                    {"value": "siliguri", "label": "Siliguri Municipal Corporation"},
                    {"value": "asansol", "label": "Asansol Municipal Corporation"}
                ]
    
    return ubi_doc

if __name__ == "__main__":
    create_ubi_land_collection()