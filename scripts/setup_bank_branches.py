#!/usr/bin/env python3
"""
Bank Branches Setup Script
Adds branch information to banks in the MongoDB banks collection
"""

import os
import sys
import json
import logging
from datetime import datetime
from pymongo import MongoClient
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

# Comprehensive bank branches data
BANK_BRANCHES_DATA = {
    "SBI": [
        {"branchCode": "SBI001", "branchName": "New Delhi Main Branch", "ifscCode": "SBIN0000001", "city": "New Delhi", "state": "Delhi", "pincode": "110001"},
        {"branchCode": "SBI002", "branchName": "Mumbai Fort Branch", "ifscCode": "SBIN0000002", "city": "Mumbai", "state": "Maharashtra", "pincode": "400001"},
        {"branchCode": "SBI003", "branchName": "Bangalore MG Road Branch", "ifscCode": "SBIN0000003", "city": "Bangalore", "state": "Karnataka", "pincode": "560001"},
        {"branchCode": "SBI004", "branchName": "Chennai Anna Salai Branch", "ifscCode": "SBIN0000004", "city": "Chennai", "state": "Tamil Nadu", "pincode": "600002"},
        {"branchCode": "SBI005", "branchName": "Kolkata Park Street Branch", "ifscCode": "SBIN0000005", "city": "Kolkata", "state": "West Bengal", "pincode": "700016"},
        {"branchCode": "SBI006", "branchName": "Pune FC Road Branch", "ifscCode": "SBIN0000006", "city": "Pune", "state": "Maharashtra", "pincode": "411004"},
        {"branchCode": "SBI007", "branchName": "Ahmedabad Ashram Road Branch", "ifscCode": "SBIN0000007", "city": "Ahmedabad", "state": "Gujarat", "pincode": "380009"}
    ],
    "PNB": [
        {"branchCode": "PNB001", "branchName": "Delhi Connaught Place Branch", "ifscCode": "PUNB0000001", "city": "New Delhi", "state": "Delhi", "pincode": "110001"},
        {"branchCode": "PNB002", "branchName": "Mumbai Nariman Point Branch", "ifscCode": "PUNB0000002", "city": "Mumbai", "state": "Maharashtra", "pincode": "400021"},
        {"branchCode": "PNB003", "branchName": "Chandigarh Sector 17 Branch", "ifscCode": "PUNB0000003", "city": "Chandigarh", "state": "Chandigarh", "pincode": "160017"},
        {"branchCode": "PNB004", "branchName": "Ludhiana Civil Lines Branch", "ifscCode": "PUNB0000004", "city": "Ludhiana", "state": "Punjab", "pincode": "141001"},
        {"branchCode": "PNB005", "branchName": "Amritsar Lawrence Road Branch", "ifscCode": "PUNB0000005", "city": "Amritsar", "state": "Punjab", "pincode": "143001"}
    ],
    "BOB": [
        {"branchCode": "BOB001", "branchName": "Vadodara Alkapuri Branch", "ifscCode": "BARB0000001", "city": "Vadodara", "state": "Gujarat", "pincode": "390007"},
        {"branchCode": "BOB002", "branchName": "Mumbai Churchgate Branch", "ifscCode": "BARB0000002", "city": "Mumbai", "state": "Maharashtra", "pincode": "400020"},
        {"branchCode": "BOB003", "branchName": "Delhi Karol Bagh Branch", "ifscCode": "BARB0000003", "city": "New Delhi", "state": "Delhi", "pincode": "110005"},
        {"branchCode": "BOB004", "branchName": "Surat Ring Road Branch", "ifscCode": "BARB0000004", "city": "Surat", "state": "Gujarat", "pincode": "395002"}
    ],
    "UCO": [
        {"branchCode": "UCO001", "branchName": "Kolkata BBD Bagh Branch", "ifscCode": "UCBA0000001", "city": "Kolkata", "state": "West Bengal", "pincode": "700001"},
        {"branchCode": "UCO002", "branchName": "Delhi Lajpat Nagar Branch", "ifscCode": "UCBA0000002", "city": "New Delhi", "state": "Delhi", "pincode": "110024"},
        {"branchCode": "UCO003", "branchName": "Mumbai Bandra Branch", "ifscCode": "UCBA0000003", "city": "Mumbai", "state": "Maharashtra", "pincode": "400050"}
    ],
    "BOI": [
        {"branchCode": "BOI001", "branchName": "Mumbai Fort Branch", "ifscCode": "BKID0000001", "city": "Mumbai", "state": "Maharashtra", "pincode": "400001"},
        {"branchCode": "BOI002", "branchName": "Delhi CP Branch", "ifscCode": "BKID0000002", "city": "New Delhi", "state": "Delhi", "pincode": "110001"},
        {"branchCode": "BOI003", "branchName": "Chennai T Nagar Branch", "ifscCode": "BKID0000003", "city": "Chennai", "state": "Tamil Nadu", "pincode": "600017"}
    ],
    "UBI": [
        {"branchCode": "UBI001", "branchName": "Mumbai Ballard Estate Branch", "ifscCode": "UBIN0000001", "city": "Mumbai", "state": "Maharashtra", "pincode": "400001"},
        {"branchCode": "UBI002", "branchName": "Delhi Connaught Place Branch", "ifscCode": "UBIN0000002", "city": "New Delhi", "state": "Delhi", "pincode": "110001"}
    ],
    "HDFC": [
        {"branchCode": "HDFC001", "branchName": "Mumbai Bandra Kurla Complex Branch", "ifscCode": "HDFC0000001", "city": "Mumbai", "state": "Maharashtra", "pincode": "400051"},
        {"branchCode": "HDFC002", "branchName": "Delhi CP Branch", "ifscCode": "HDFC0000002", "city": "New Delhi", "state": "Delhi", "pincode": "110001"},
        {"branchCode": "HDFC003", "branchName": "Bangalore Koramangala Branch", "ifscCode": "HDFC0000003", "city": "Bangalore", "state": "Karnataka", "pincode": "560034"},
        {"branchCode": "HDFC004", "branchName": "Chennai Anna Nagar Branch", "ifscCode": "HDFC0000004", "city": "Chennai", "state": "Tamil Nadu", "pincode": "600040"}
    ],
    "CBI": [
        {"branchCode": "CBI001", "branchName": "Mumbai Fort Branch", "ifscCode": "CBIN0000001", "city": "Mumbai", "state": "Maharashtra", "pincode": "400001"},
        {"branchCode": "CBI002", "branchName": "Delhi Parliament Street Branch", "ifscCode": "CBIN0000002", "city": "New Delhi", "state": "Delhi", "pincode": "110001"}
    ]
}


def connect_to_mongodb():
    """Connect to MongoDB"""
    try:
        client = MongoClient(MONGODB_URI)
        db = client[DB_NAME]
        
        # Test connection
        client.admin.command('ping')
        logger.info("✅ Connected to MongoDB successfully")
        return client, db
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        return None, None


def update_bank_with_branches(db, bank_code: str, branches: list) -> bool:
    """Update a specific bank with branch information"""
    try:
        # Update all bank documents that contain this bank
        banks_collection = db.banks
        
        # Find documents that contain the bank in their banks array
        query = {"banks.bankCode": bank_code}
        
        # Update the branches field for this bank
        update_result = banks_collection.update_many(
            query,
            {
                "$set": {
                    "banks.$[bank].branches": branches,
                    "banks.$[bank].branchCount": len(branches),
                    "banks.$[bank].branchesUpdatedAt": datetime.now().isoformat()
                }
            },
            array_filters=[{"bank.bankCode": bank_code}]
        )
        
        if update_result.modified_count > 0:
            logger.info(f"✅ Updated {update_result.modified_count} documents with branches for {bank_code}")
            return True
        else:
            logger.warning(f"⚠️  No documents updated for {bank_code} - bank may not exist")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error updating branches for {bank_code}: {e}")
        return False


def add_branches_to_all_banks(db) -> bool:
    """Add branch information to all banks"""
    try:
        success_count = 0
        total_banks = len(BANK_BRANCHES_DATA)
        
        logger.info(f"🏦 Starting to add branches to {total_banks} banks")
        
        for bank_code, branches in BANK_BRANCHES_DATA.items():
            logger.info(f"🔄 Processing {bank_code} with {len(branches)} branches...")
            
            if update_bank_with_branches(db, bank_code, branches):
                success_count += 1
            
        logger.info(f"✅ Successfully updated {success_count}/{total_banks} banks")
        return success_count > 0
        
    except Exception as e:
        logger.error(f"❌ Error adding branches to banks: {e}")
        return False


def verify_bank_branches(db):
    """Verify that branches were added correctly"""
    try:
        logger.info("🔍 Verifying bank branches...")
        
        banks_collection = db.banks
        bank_docs = list(banks_collection.find({}))
        
        for doc in bank_docs:
            if 'banks' in doc and isinstance(doc['banks'], list):
                logger.info(f"\\n📋 Document: {doc.get('description', 'N/A')}")
                
                for bank in doc['banks']:
                    bank_code = bank.get('bankCode', 'N/A')
                    branch_count = len(bank.get('branches', []))
                    
                    logger.info(f"  🏦 {bank_code}: {branch_count} branches")
                    
                    if branch_count > 0:
                        # Show first branch as sample
                        sample_branch = bank['branches'][0]
                        logger.info(f"      Sample: {sample_branch.get('branchName', 'N/A')} - {sample_branch.get('city', 'N/A')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verifying branches: {e}")
        return False


def main():
    """Main function"""
    if not MONGODB_URI:
        logger.error("❌ MONGODB_URI environment variable not set")
        return 1
    
    # Connect to MongoDB
    client, db = connect_to_mongodb()
    if not client or not db:
        return 1
    
    try:
        logger.info("🚀 Starting bank branches setup")
        
        # Add branches to all banks
        if add_branches_to_all_banks(db):
            logger.info("✅ Bank branches setup completed successfully!")
            
            # Verify the results
            verify_bank_branches(db)
            
            return 0
        else:
            logger.error("❌ Failed to setup bank branches")
            return 1
            
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        return 1
        
    finally:
        if client:
            client.close()


if __name__ == "__main__":
    exit(main())