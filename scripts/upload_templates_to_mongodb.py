#!/usr/bin/env python3
"""
Upload Templates to MongoDB

This script uploads all standardized templates from local files back to MongoDB.

Usage:
    python upload_templates_to_mongodb.py --dry-run
    python upload_templates_to_mongodb.py --apply
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from pymongo import MongoClient
from bson import ObjectId

# MongoDB Configuration
MONGODB_URI = "mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster"
DATABASE_NAME = "valuation_admin"

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent / "backend" / "data"

# Template collections mapping
TEMPLATE_COLLECTIONS = {
    "common_form_fields": {
        "path": "common_fields.json",
        "collection": "common_form_fields",
        "is_common": True
    },
    "bob_land_property_details": {
        "path": "bob/bob_land_property_details.json",
        "collection": "bob_land_property_details",
        "is_common": False
    },
    "boi_apartment_property_details": {
        "path": "boi/boi_apartment_property_details.json",
        "collection": "boi_apartment_property_details",
        "is_common": False
    },
    "boi_land_property_details": {
        "path": "boi/boi_land_property_details.json",
        "collection": "boi_land_property_details",
        "is_common": False
    },
    "cbi_all_property_details": {
        "path": "cbi/cbi_all_property_details.json",
        "collection": "cbi_all_property_details",
        "is_common": False
    },
    "hdfc_all_property_details": {
        "path": "hdfc/hdfc_all_property_details.json",
        "collection": "hdfc_all_property_details",
        "is_common": False
    },
    "pnb_land_property_details": {
        "path": "pnb/pnb_land_property_details.json",
        "collection": "pnb_land_property_details",
        "is_common": False
    },
    "sbi_apartment_property_details": {
        "path": "sbi/apartment/sbi_apartment_property_details.json",
        "collection": "sbi_apartment_property_details",
        "is_common": False
    },
    "sbi_land_property_details": {
        "path": "sbi/land/sbi_land_property_details.json",
        "collection": "sbi_land_property_details",
        "is_common": False
    },
    "ubi_apartment_property_details": {
        "path": "ubi/apartment/ubi_apartment_property_details.json",
        "collection": "ubi_apartment_property_details",
        "is_common": False
    },
    "ubi_land_property_details": {
        "path": "ubi/land/ubi_land_property_details.json",
        "collection": "ubi_land_property_details",
        "is_common": False
    },
    "uco_apartment_property_details": {
        "path": "uco/apartment/uco_apartment_property_details.json",
        "collection": "uco_apartment_property_details",
        "is_common": False
    },
    "uco_land_property_details": {
        "path": "uco/land/uco_land_property_details.json",
        "collection": "uco_land_property_details",
        "is_common": False
    }
}


class MongoDBUploader:
    """Upload standardized templates to MongoDB"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.client = None
        self.db = None
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "templates_uploaded": [],
            "templates_skipped": [],
            "field_counts": {},
            "errors": []
        }
    
    def connect_mongodb(self) -> bool:
        """Connect to MongoDB"""
        try:
            print("🔌 Connecting to MongoDB...")
            self.client = MongoClient(
                MONGODB_URI,
                serverSelectionTimeoutMS=10000,
                tlsAllowInvalidCertificates=True
            )
            self.db = self.client[DATABASE_NAME]
            # Test connection
            self.db.list_collection_names()
            print("✅ Connected to MongoDB successfully")
            return True
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            return False
    
    def close_mongodb(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("🔌 MongoDB connection closed")
    
    def convert_string_to_objectid(self, data: Any) -> Any:
        """Recursively convert string '_id' fields back to ObjectId"""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if key == "_id" and isinstance(value, str):
                    # Try to convert to ObjectId if it's a valid ObjectId string
                    try:
                        result[key] = ObjectId(value)
                    except:
                        result[key] = value
                else:
                    result[key] = self.convert_string_to_objectid(value)
            return result
        elif isinstance(data, list):
            return [self.convert_string_to_objectid(item) for item in data]
        else:
            return data
    
    def count_fields(self, data: Dict[str, Any], is_common: bool) -> int:
        """Count total fields in template"""
        count = 0
        
        if is_common:
            # Common fields template
            if "fields" in data:
                count = len(data["fields"])
        else:
            # Bank templates
            if "documents" in data:
                for document in data["documents"]:
                    if "sections" in document:
                        for section in document["sections"]:
                            if "fields" in section:
                                count += len(section["fields"])
                    elif "fields" in document:
                        count += len(document["fields"])
        
        return count
    
    def upload_template(self, template_name: str, config: Dict[str, Any]) -> bool:
        """Upload a single template to MongoDB"""
        file_path = BASE_DIR / config["path"]
        collection_name = config["collection"]
        
        print(f"\n📤 Uploading: {template_name}")
        print(f"   File: {config['path']}")
        print(f"   Collection: {collection_name}")
        
        # Check if file exists
        if not file_path.exists():
            error_msg = f"File not found: {config['path']}"
            print(f"   ❌ {error_msg}")
            self.report["errors"].append(error_msg)
            self.report["templates_skipped"].append(template_name)
            return False
        
        try:
            # Read template from file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert string _id fields back to ObjectId
            data = self.convert_string_to_objectid(data)
            
            # Count fields
            field_count = self.count_fields(data, config["is_common"])
            print(f"   📊 Fields: {field_count}")
            
            # Update timestamps
            data["updatedAt"] = datetime.now()
            
            # Get existing document ID if it exists
            existing = self.db[collection_name].find_one({})
            
            if not self.dry_run:
                if existing:
                    # Update existing document
                    # Preserve the original _id
                    if "_id" in existing:
                        data["_id"] = existing["_id"]
                    
                    # Replace the entire document
                    result = self.db[collection_name].replace_one(
                        {"_id": data["_id"]},
                        data
                    )
                    
                    if result.modified_count > 0:
                        print(f"   ✅ Updated existing document (ID: {data['_id']})")
                    else:
                        print(f"   ℹ️  No changes detected (ID: {data['_id']})")
                else:
                    # Insert new document
                    # Remove _id if it's None to let MongoDB generate it
                    if data.get("_id") is None:
                        data.pop("_id", None)
                    
                    result = self.db[collection_name].insert_one(data)
                    print(f"   ✅ Inserted new document (ID: {result.inserted_id})")
                
                self.report["templates_uploaded"].append(template_name)
            else:
                if existing:
                    print(f"   🔍 [DRY-RUN] Would update existing document (ID: {existing['_id']})")
                else:
                    print(f"   🔍 [DRY-RUN] Would insert new document")
                
                self.report["templates_uploaded"].append(f"{template_name} (dry-run)")
            
            # Store field count
            self.report["field_counts"][template_name] = field_count
            
            return True
            
        except Exception as e:
            error_msg = f"Error uploading {template_name}: {str(e)}"
            print(f"   ❌ {error_msg}")
            self.report["errors"].append(error_msg)
            self.report["templates_skipped"].append(template_name)
            return False
    
    def upload_all_templates(self):
        """Upload all templates to MongoDB"""
        print("\n" + "=" * 80)
        print("📤 UPLOADING TEMPLATES TO MONGODB")
        print("=" * 80)
        print(f"Database: {DATABASE_NAME}")
        print(f"Mode: {'DRY-RUN (No changes will be made)' if self.dry_run else 'APPLY (Changes will be saved)'}")
        print("=" * 80)
        
        success_count = 0
        fail_count = 0
        
        for template_name, config in TEMPLATE_COLLECTIONS.items():
            if self.upload_template(template_name, config):
                success_count += 1
            else:
                fail_count += 1
        
        # Save report
        report_file = BASE_DIR.parent / "reports" / "mongodb_upload_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, default=str, ensure_ascii=False)
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 UPLOAD SUMMARY")
        print("=" * 80)
        print(f"✅ Successfully uploaded: {success_count}")
        print(f"⚠️  Skipped/Failed: {fail_count}")
        print(f"📄 Total fields uploaded: {sum(self.report['field_counts'].values())}")
        
        if self.report["errors"]:
            print(f"\n❌ Errors ({len(self.report['errors'])}):")
            for error in self.report["errors"]:
                print(f"   - {error}")
        
        print(f"\n📁 Report saved to: {report_file}")
        print("=" * 80)
        
        if not self.dry_run:
            print("\n✅ All templates uploaded to MongoDB successfully!")
            print("⚠️  Note: You may need to refresh your application cache/collections")
        else:
            print("\n🔍 Dry-run complete. Use --apply to upload for real.")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Upload standardized templates to MongoDB",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview uploads without making changes"
    )
    
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes (upload to MongoDB)"
    )
    
    args = parser.parse_args()
    
    # Determine dry-run mode
    dry_run = args.dry_run or not args.apply
    
    # Create uploader
    uploader = MongoDBUploader(dry_run=dry_run)
    
    try:
        # Connect to MongoDB
        if not uploader.connect_mongodb():
            sys.exit(1)
        
        # Upload all templates
        uploader.upload_all_templates()
        
        print("\n✅ Operation completed successfully")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        uploader.close_mongodb()


if __name__ == "__main__":
    main()
