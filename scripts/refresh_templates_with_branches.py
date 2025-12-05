#!/usr/bin/env python3
"""
Template Refresh Script with Bank Branch Integration
Downloads templates from MongoDB and populates BankBranch fields from Bank collection
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from pymongo import MongoClient
from bson import json_util
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB configuration
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = "valuation_admin"

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "backend" / "data" / "templates_refreshed"

# Sample bank branches data - you can expand this
BANK_BRANCHES = {
    "SBI": [
        {"branchCode": "SBI001", "branchName": "New Delhi Main Branch", "ifscCode": "SBIN0000001", "city": "New Delhi", "state": "Delhi"},
        {"branchCode": "SBI002", "branchName": "Mumbai Fort Branch", "ifscCode": "SBIN0000002", "city": "Mumbai", "state": "Maharashtra"},
        {"branchCode": "SBI003", "branchName": "Bangalore MG Road Branch", "ifscCode": "SBIN0000003", "city": "Bangalore", "state": "Karnataka"},
        {"branchCode": "SBI004", "branchName": "Chennai Anna Salai Branch", "ifscCode": "SBIN0000004", "city": "Chennai", "state": "Tamil Nadu"},
        {"branchCode": "SBI005", "branchName": "Kolkata Park Street Branch", "ifscCode": "SBIN0000005", "city": "Kolkata", "state": "West Bengal"}
    ],
    "PNB": [
        {"branchCode": "PNB001", "branchName": "Delhi Connaught Place Branch", "ifscCode": "PUNB0000001", "city": "New Delhi", "state": "Delhi"},
        {"branchCode": "PNB002", "branchName": "Mumbai Nariman Point Branch", "ifscCode": "PUNB0000002", "city": "Mumbai", "state": "Maharashtra"},
        {"branchCode": "PNB003", "branchName": "Chandigarh Sector 17 Branch", "ifscCode": "PUNB0000003", "city": "Chandigarh", "state": "Chandigarh"},
        {"branchCode": "PNB004", "branchName": "Ludhiana Civil Lines Branch", "ifscCode": "PUNB0000004", "city": "Ludhiana", "state": "Punjab"}
    ],
    "BOB": [
        {"branchCode": "BOB001", "branchName": "Vadodara Alkapuri Branch", "ifscCode": "BARB0000001", "city": "Vadodara", "state": "Gujarat"},
        {"branchCode": "BOB002", "branchName": "Mumbai Churchgate Branch", "ifscCode": "BARB0000002", "city": "Mumbai", "state": "Maharashtra"},
        {"branchCode": "BOB003", "branchName": "Delhi Karol Bagh Branch", "ifscCode": "BARB0000003", "city": "New Delhi", "state": "Delhi"}
    ],
    "UCO": [
        {"branchCode": "UCO001", "branchName": "Kolkata BBD Bagh Branch", "ifscCode": "UCBA0000001", "city": "Kolkata", "state": "West Bengal"},
        {"branchCode": "UCO002", "branchName": "Delhi Lajpat Nagar Branch", "ifscCode": "UCBA0000002", "city": "New Delhi", "state": "Delhi"}
    ],
    "BOI": [
        {"branchCode": "BOI001", "branchName": "Mumbai Fort Branch", "ifscCode": "BKID0000001", "city": "Mumbai", "state": "Maharashtra"},
        {"branchCode": "BOI002", "branchName": "Delhi CP Branch", "ifscCode": "BKID0000002", "city": "New Delhi", "state": "Delhi"}
    ],
    "UBI": [
        {"branchCode": "UBI001", "branchName": "Mumbai Ballard Estate Branch", "ifscCode": "UBIN0000001", "city": "Mumbai", "state": "Maharashtra"},
        {"branchCode": "UBI002", "branchName": "Delhi Connaught Place Branch", "ifscCode": "UBIN0000002", "city": "New Delhi", "state": "Delhi"}
    ],
    "HDFC": [
        {"branchCode": "HDFC001", "branchName": "Mumbai Bandra Kurla Complex Branch", "ifscCode": "HDFC0000001", "city": "Mumbai", "state": "Maharashtra"},
        {"branchCode": "HDFC002", "branchName": "Delhi CP Branch", "ifscCode": "HDFC0000002", "city": "New Delhi", "state": "Delhi"},
        {"branchCode": "HDFC003", "branchName": "Bangalore Koramangala Branch", "ifscCode": "HDFC0000003", "city": "Bangalore", "state": "Karnataka"}
    ],
    "CBI": [
        {"branchCode": "CBI001", "branchName": "Mumbai Fort Branch", "ifscCode": "CBIN0000001", "city": "Mumbai", "state": "Maharashtra"},
        {"branchCode": "CBI002", "branchName": "Delhi Parliament Street Branch", "ifscCode": "CBIN0000002", "city": "New Delhi", "state": "Delhi"}
    ]
}


class TemplateRefresher:
    """Handles template download and bank branch integration"""
    
    def __init__(self, mongodb_uri: str, db_name: str, output_dir: Path):
        """Initialize the refresher"""
        self.mongodb_uri = mongodb_uri
        self.db_name = db_name
        self.output_dir = Path(output_dir)
        self.client = None
        self.db = None
        
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.mongodb_uri)
            self.db = self.client[self.db_name]
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("✅ Connected to MongoDB successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            return False
    
    def get_bank_branches_from_db(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get bank branches from MongoDB banks collection"""
        try:
            banks_collection = self.db.banks
            bank_docs = list(banks_collection.find({}))
            
            bank_branches = {}
            
            for doc in bank_docs:
                if 'banks' in doc and isinstance(doc['banks'], list):
                    for bank in doc['banks']:
                        bank_code = bank.get('bankCode', '')
                        if bank_code and 'branches' in bank:
                            branches = bank.get('branches', [])
                            if branches:
                                bank_branches[bank_code] = branches
                                logger.info(f"📍 Found {len(branches)} branches for {bank_code}")
            
            return bank_branches
            
        except Exception as e:
            logger.error(f"❌ Error fetching bank branches: {e}")
            return {}
    
    def get_template_collections(self) -> List[str]:
        """Get list of template collections from MongoDB"""
        try:
            collections = self.db.list_collection_names()
            
            # Filter template collections (exclude system collections)
            template_collections = [
                col for col in collections 
                if col not in ['banks', 'organizations', 'users', 'audit_logs', 'common_form_fields', 'document_types']
                and not col.startswith('banks_backup')
                and '_property_details' in col
            ]
            
            logger.info(f"📊 Found {len(template_collections)} template collections")
            return template_collections
            
        except Exception as e:
            logger.error(f"❌ Error getting collections: {e}")
            return []
    
    def add_bank_branch_field_to_template(self, template_doc: Dict[str, Any], bank_code: str, 
                                        bank_branches: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Add BankBranch field to template sections"""
        
        branches = bank_branches.get(bank_code, BANK_BRANCHES.get(bank_code, []))
        
        if not branches:
            logger.warning(f"⚠️  No branches found for bank {bank_code}")
            return template_doc
        
        # Create BankBranch field definition
        bank_branch_field = {
            "fieldId": "bank_branch",
            "uiDisplayName": "Bank Branch",
            "fieldType": "select",
            "isRequired": True,
            "sortOrder": 1,
            "options": [
                {
                    "value": f"{branch['branchCode']}",
                    "label": f"{branch['branchName']} - {branch.get('city', 'N/A')}"
                }
                for branch in branches
            ],
            "placeholder": f"Select {bank_code} branch",
            "includeInCustomTemplate": True,
            "validation": {
                "required": True
            },
            "metadata": {
                "addedBy": "refresh_templates_with_branches.py",
                "addedAt": datetime.now().isoformat(),
                "branchCount": len(branches)
            }
        }
        
        # Add to documents sections
        if 'documents' in template_doc:
            for document in template_doc['documents']:
                if 'sections' in document:
                    for section in document['sections']:
                        if 'fields' in section:
                            # Check if bank_branch field already exists
                            existing_field = next((f for f in section['fields'] if f.get('fieldId') == 'bank_branch'), None)
                            
                            if existing_field:
                                # Update existing field
                                existing_field.update(bank_branch_field)
                                logger.info(f"🔄 Updated bank_branch field in section {section.get('sectionId', 'N/A')}")
                            else:
                                # Add new field at the beginning
                                section['fields'].insert(0, bank_branch_field)
                                logger.info(f"➕ Added bank_branch field to section {section.get('sectionId', 'N/A')}")
        
        return template_doc
    
    def download_and_process_template(self, collection_name: str, 
                                    bank_branches: Dict[str, List[Dict[str, Any]]]) -> bool:
        """Download template from MongoDB and process it"""
        try:
            collection = self.db[collection_name]
            template_doc = collection.find_one({"isActive": True})
            
            if not template_doc:
                logger.warning(f"⚠️  No active template found in {collection_name}")
                return False
            
            # Extract bank code from collection name or template metadata
            bank_code = self.extract_bank_code(collection_name, template_doc)
            
            if not bank_code:
                logger.warning(f"⚠️  Could not determine bank code for {collection_name}")
                return False
            
            # Add bank branch field
            processed_template = self.add_bank_branch_field_to_template(
                template_doc, bank_code, bank_branches
            )
            
            # Save to file
            output_file = self.output_dir / f"{collection_name}.json"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(processed_template, f, indent=2, default=json_util.default, ensure_ascii=False)
            
            logger.info(f"💾 Saved processed template: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing {collection_name}: {e}")
            return False
    
    def extract_bank_code(self, collection_name: str, template_doc: Dict[str, Any]) -> Optional[str]:
        """Extract bank code from collection name or template document"""
        
        # Method 1: From collection name pattern
        if '_' in collection_name:
            parts = collection_name.split('_')
            potential_bank_code = parts[0].upper()
            if potential_bank_code in BANK_BRANCHES:
                return potential_bank_code
        
        # Method 2: From template metadata
        if 'templateMetadata' in template_doc:
            metadata = template_doc['templateMetadata']
            if 'bankCode' in metadata:
                return metadata['bankCode'].upper()
        
        # Method 3: From documents array
        if 'documents' in template_doc:
            for doc in template_doc['documents']:
                if 'bankCode' in doc:
                    return doc['bankCode'].upper()
        
        return None
    
    def refresh_all_templates(self):
        """Main method to refresh all templates with bank branches"""
        logger.info("🚀 Starting template refresh with bank branches")
        
        # Connect to MongoDB
        if not self.connect():
            return False
        
        try:
            # Get bank branches from MongoDB (fallback to static data)
            bank_branches = self.get_bank_branches_from_db()
            if not bank_branches:
                logger.info("📍 Using static bank branches data")
                bank_branches = BANK_BRANCHES
            
            # Get template collections
            template_collections = self.get_template_collections()
            
            if not template_collections:
                logger.error("❌ No template collections found")
                return False
            
            # Process each template
            processed_count = 0
            total_count = len(template_collections)
            
            for collection_name in template_collections:
                logger.info(f"🔄 Processing {collection_name} ({processed_count + 1}/{total_count})")
                
                if self.download_and_process_template(collection_name, bank_branches):
                    processed_count += 1
                else:
                    logger.error(f"❌ Failed to process {collection_name}")
            
            logger.info(f"✅ Successfully processed {processed_count}/{total_count} templates")
            logger.info(f"📁 Templates saved to: {self.output_dir}")
            
            return processed_count > 0
            
        except Exception as e:
            logger.error(f"❌ Error during template refresh: {e}")
            return False
        
        finally:
            if self.client:
                self.client.close()


def main():
    """Main function"""
    if not MONGODB_URI:
        logger.error("❌ MONGODB_URI environment variable not set")
        return 1
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Initialize refresher
    refresher = TemplateRefresher(MONGODB_URI, DB_NAME, OUTPUT_DIR)
    
    # Refresh templates
    success = refresher.refresh_all_templates()
    
    if success:
        logger.info("🎉 Template refresh completed successfully!")
        return 0
    else:
        logger.error("💥 Template refresh failed!")
        return 1


if __name__ == "__main__":
    exit(main())