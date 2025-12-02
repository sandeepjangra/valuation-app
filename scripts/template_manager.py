#!/usr/bin/env python3
"""
Template Manager - Comprehensive MongoDB Template Synchronization & Standardization

This script downloads, validates, standardizes, and manages bank templates from MongoDB.

Features:
- Download all templates from MongoDB with backup
- Validate structure against canonical template (UCO)
- Standardize shared fields across templates
- Add includeInCustomTemplate field
- Identify common fields
- Generate comprehensive reports
- Dry-run mode for safe testing

Usage:
    python template_manager.py download --backup
    python template_manager.py validate --canonical=uco
    python template_manager.py standardize --report
    python template_manager.py full-sync --dry-run
    python template_manager.py full-sync --apply
"""

import sys
import os
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple, Set
from collections import defaultdict
from pymongo import MongoClient
from bson import ObjectId

# MongoDB Configuration
MONGODB_URI = "mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster"
DATABASE_NAME = "valuation_admin"

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent / "backend" / "data"

# Template collections mapping
TEMPLATE_COLLECTIONS = {
    # Common fields
    "common_form_fields": {"path": "common_fields.json", "is_common": True},
    
    # Bank-specific templates
    "bob_land_property_details": {"path": "bob/bob_land_property_details.json", "is_common": False},
    "boi_apartment_property_details": {"path": "boi/boi_apartment_property_details.json", "is_common": False},
    "boi_land_property_details": {"path": "boi/boi_land_property_details.json", "is_common": False},
    "cbi_all_property_details": {"path": "cbi/cbi_all_property_details.json", "is_common": False},
    "hdfc_all_property_details": {"path": "hdfc/hdfc_all_property_details.json", "is_common": False},
    "pnb_land_property_details": {"path": "pnb/pnb_land_property_details.json", "is_common": False},
    "sbi_apartment_property_details": {"path": "sbi/apartment/sbi_apartment_property_details.json", "is_common": False},
    "sbi_land_property_details": {"path": "sbi/land/sbi_land_property_details.json", "is_common": False},
    "ubi_apartment_property_details": {"path": "ubi/apartment/ubi_apartment_property_details.json", "is_common": False},
    "ubi_land_property_details": {"path": "ubi/land/ubi_land_property_details.json", "is_common": False},
    "uco_apartment_property_details": {"path": "uco/apartment/uco_apartment_property_details.json", "is_common": False},
    "uco_land_property_details": {"path": "uco/land/uco_land_property_details.json", "is_common": False},
}

# Canonical template structure (based on UCO)
CANONICAL_STRUCTURE = {
    "template_level": [
        "_id", "metadata", "templateMetadata", "documents", 
        "isActive", "createdAt", "updatedAt", "version"
    ],
    "document_level": [
        "_id", "templateId", "templateName", "bankCode", "propertyType",
        "templateCategory", "createdAt", "updatedAt", "isActive", "uiName", "sections"
    ],
    "section_level": ["sectionId", "sectionName", "sortOrder", "fields"],
    "field_level": [
        "fieldId", "uiDisplayName", "fieldType", "isRequired", 
        "placeholder", "sortOrder"
    ]
}


class TemplateManager:
    """Main class for managing template operations"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.client = None
        self.db = None
        self.reports = {
            "download": {},
            "structure_validation": {},
            "field_standardization": {},
            "common_fields": {},
            "changes_summary": {}
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
    
    def json_serializer(self, obj):
        """Handle MongoDB types for JSON serialization"""
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    def create_backup(self) -> Path:
        """Create backup of existing templates"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = BASE_DIR.parent / f"data_backup_{timestamp}"
        
        print(f"\n📦 Creating backup at: {backup_dir}")
        
        if not self.dry_run:
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy all existing files
            import shutil
            if BASE_DIR.exists():
                for item in BASE_DIR.rglob("*.json"):
                    relative_path = item.relative_to(BASE_DIR)
                    backup_file = backup_dir / relative_path
                    backup_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, backup_file)
                    
            print(f"✅ Backup created successfully")
        else:
            print(f"🔍 [DRY-RUN] Would create backup at: {backup_dir}")
        
        return backup_dir
    
    def download_templates(self) -> Dict[str, Any]:
        """Download all templates from MongoDB"""
        print("\n" + "="*80)
        print("📥 DOWNLOADING TEMPLATES FROM MONGODB")
        print("="*80)
        
        download_report = {
            "timestamp": datetime.now().isoformat(),
            "total_collections": len(TEMPLATE_COLLECTIONS),
            "downloaded": [],
            "failed": [],
            "stats": {}
        }
        
        for collection_name, config in TEMPLATE_COLLECTIONS.items():
            try:
                print(f"\n📥 Downloading: {collection_name}")
                
                # Download from MongoDB
                doc = self.db[collection_name].find_one({})
                
                if not doc:
                    print(f"   ⚠️  No data found in collection")
                    download_report["failed"].append({
                        "collection": collection_name,
                        "reason": "No data found"
                    })
                    continue
                
                # Count fields
                field_count = 0
                if config["is_common"]:
                    field_count = len(doc.get("fields", []))
                else:
                    for document in doc.get("documents", []):
                        for section in document.get("sections", []):
                            field_count += len(section.get("fields", []))
                
                print(f"   ✅ Downloaded: {field_count} fields")
                
                download_report["downloaded"].append(collection_name)
                download_report["stats"][collection_name] = {
                    "field_count": field_count,
                    "is_common": config["is_common"],
                    "path": config["path"]
                }
                
                # Save to file
                file_path = BASE_DIR / config["path"]
                
                if not self.dry_run:
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(doc, f, indent=2, default=self.json_serializer, ensure_ascii=False)
                    print(f"   💾 Saved to: {config['path']}")
                else:
                    print(f"   🔍 [DRY-RUN] Would save to: {config['path']}")
                    
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                download_report["failed"].append({
                    "collection": collection_name,
                    "reason": str(e)
                })
        
        self.reports["download"] = download_report
        return download_report
    
    def load_canonical_template(self, canonical_name: str = "uco_land_property_details") -> Dict[str, Any]:
        """Load canonical template structure"""
        print(f"\n📋 Loading canonical template: {canonical_name}")
        
        try:
            doc = self.db[canonical_name].find_one({})
            if doc:
                print(f"✅ Canonical template loaded")
                return doc
            else:
                print(f"❌ Canonical template not found")
                return {}
        except Exception as e:
            print(f"❌ Failed to load canonical template: {e}")
            return {}
    
    def validate_structure(self, canonical_template: Dict[str, Any]) -> Dict[str, Any]:
        """Validate all templates against canonical structure"""
        print("\n" + "="*80)
        print("🔍 VALIDATING TEMPLATE STRUCTURES")
        print("="*80)
        
        validation_report = {
            "timestamp": datetime.now().isoformat(),
            "canonical": "uco_land_property_details",
            "templates_validated": [],
            "issues": defaultdict(list)
        }
        
        # Extract canonical structure
        canonical_keys = {
            "template": set(canonical_template.keys()),
            "document": set(canonical_template["documents"][0].keys()) if "documents" in canonical_template and canonical_template["documents"] else set(),
            "section": set(canonical_template["documents"][0]["sections"][0].keys()) if "documents" in canonical_template and canonical_template["documents"] and "sections" in canonical_template["documents"][0] else set(),
            "field": set(canonical_template["documents"][0]["sections"][0]["fields"][0].keys()) if "documents" in canonical_template and canonical_template["documents"] and "sections" in canonical_template["documents"][0] and canonical_template["documents"][0]["sections"] and "fields" in canonical_template["documents"][0]["sections"][0] and canonical_template["documents"][0]["sections"][0]["fields"] else set()
        }
        
        print(f"\n📐 Canonical structure keys:")
        print(f"   Template level: {sorted(canonical_keys['template'])}")
        print(f"   Document level: {sorted(canonical_keys['document'])}")
        print(f"   Section level: {sorted(canonical_keys['section'])}")
        print(f"   Field level: {sorted(canonical_keys['field'])}")
        
        # Validate each template
        for collection_name, config in TEMPLATE_COLLECTIONS.items():
            if config["is_common"]:
                continue  # Skip common fields template
            
            print(f"\n🔍 Validating: {collection_name}")
            
            try:
                doc = self.db[collection_name].find_one({})
                if not doc:
                    continue
                
                # Validate template level
                template_keys = set(doc.keys())
                missing_template = canonical_keys["template"] - template_keys
                extra_template = template_keys - canonical_keys["template"]
                
                if missing_template:
                    validation_report["issues"]["missing_template_keys"].append({
                        "collection": collection_name,
                        "missing_keys": list(missing_template)
                    })
                    print(f"   ⚠️  Missing template keys: {missing_template}")
                
                if extra_template:
                    validation_report["issues"]["extra_template_keys"].append({
                        "collection": collection_name,
                        "extra_keys": list(extra_template)
                    })
                    print(f"   ℹ️  Extra template keys: {extra_template}")
                
                # Validate document level
                if "documents" in doc and doc["documents"]:
                    doc_keys = set(doc["documents"][0].keys())
                    missing_doc = canonical_keys["document"] - doc_keys
                    extra_doc = doc_keys - canonical_keys["document"]
                    
                    if missing_doc:
                        validation_report["issues"]["missing_document_keys"].append({
                            "collection": collection_name,
                            "missing_keys": list(missing_doc)
                        })
                        print(f"   ⚠️  Missing document keys: {missing_doc}")
                    
                    if extra_doc:
                        validation_report["issues"]["extra_document_keys"].append({
                            "collection": collection_name,
                            "extra_keys": list(extra_doc)
                        })
                        print(f"   ℹ️  Extra document keys: {extra_doc}")
                    
                    # Validate section level
                    if "sections" in doc["documents"][0] and doc["documents"][0]["sections"]:
                        section_keys = set(doc["documents"][0]["sections"][0].keys())
                        missing_section = canonical_keys["section"] - section_keys
                        extra_section = section_keys - canonical_keys["section"]
                        
                        if missing_section:
                            validation_report["issues"]["missing_section_keys"].append({
                                "collection": collection_name,
                                "missing_keys": list(missing_section)
                            })
                            print(f"   ⚠️  Missing section keys: {missing_section}")
                        
                        if extra_section:
                            validation_report["issues"]["extra_section_keys"].append({
                                "collection": collection_name,
                                "extra_keys": list(extra_section)
                            })
                            print(f"   ℹ️  Extra section keys: {extra_section}")
                        
                        # Validate field level
                        if "fields" in doc["documents"][0]["sections"][0] and doc["documents"][0]["sections"][0]["fields"]:
                            field_keys = set(doc["documents"][0]["sections"][0]["fields"][0].keys())
                            missing_field = canonical_keys["field"] - field_keys
                            extra_field = field_keys - canonical_keys["field"]
                            
                            if missing_field:
                                validation_report["issues"]["missing_field_keys"].append({
                                    "collection": collection_name,
                                    "missing_keys": list(missing_field)
                                })
                                print(f"   ⚠️  Missing field keys: {missing_field}")
                            
                            if extra_field:
                                validation_report["issues"]["extra_field_keys"].append({
                                    "collection": collection_name,
                                    "extra_keys": list(extra_field)
                                })
                                print(f"   ℹ️  Extra field keys: {extra_field}")
                
                validation_report["templates_validated"].append(collection_name)
                
                if not missing_template and not missing_doc and not missing_section and not missing_field:
                    print(f"   ✅ Structure valid")
                    
            except Exception as e:
                print(f"   ❌ Validation failed: {e}")
                validation_report["issues"]["validation_errors"].append({
                    "collection": collection_name,
                    "error": str(e)
                })
        
        self.reports["structure_validation"] = validation_report
        return validation_report
    
    def standardize_structure(self, canonical_template: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize all templates to match canonical structure"""
        print("\n" + "="*80)
        print("🔧 STANDARDIZING TEMPLATE STRUCTURES")
        print("="*80)
        
        standardization_report = {
            "timestamp": datetime.now().isoformat(),
            "templates_updated": [],
            "changes_made": defaultdict(list)
        }
        
        # Extract canonical structure with default values
        canonical_defaults = self._extract_canonical_defaults(canonical_template)
        
        for collection_name, config in TEMPLATE_COLLECTIONS.items():
            if config["is_common"]:
                continue
            
            print(f"\n🔧 Standardizing: {collection_name}")
            
            try:
                doc = self.db[collection_name].find_one({})
                if not doc:
                    continue
                
                modified = False
                changes = []
                
                # Add missing template-level keys
                for key, default_value in canonical_defaults["template"].items():
                    if key not in doc:
                        doc[key] = default_value
                        modified = True
                        changes.append(f"Added template key: {key}")
                        print(f"   ➕ Added template key: {key}")
                
                # Update documents
                if "documents" in doc:
                    for doc_idx, document in enumerate(doc["documents"]):
                        # Add missing document-level keys
                        for key, default_value in canonical_defaults["document"].items():
                            if key not in document:
                                document[key] = default_value
                                modified = True
                                changes.append(f"Added document[{doc_idx}] key: {key}")
                                print(f"   ➕ Added document[{doc_idx}] key: {key}")
                        
                        # Update sections
                        if "sections" in document:
                            for sec_idx, section in enumerate(document["sections"]):
                                # Add missing section-level keys
                                for key, default_value in canonical_defaults["section"].items():
                                    if key not in section:
                                        section[key] = default_value
                                        modified = True
                                        changes.append(f"Added section[{sec_idx}] key: {key}")
                                
                                # Update fields
                                if "fields" in section:
                                    for field_idx, field in enumerate(section["fields"]):
                                        # Add missing field-level keys
                                        for key, default_value in canonical_defaults["field"].items():
                                            if key not in field:
                                                field[key] = default_value
                                                modified = True
                                                changes.append(f"Added field key: {key} to {field.get('fieldId', 'unknown')}")
                
                if modified:
                    standardization_report["templates_updated"].append(collection_name)
                    standardization_report["changes_made"][collection_name] = changes
                    
                    # Save standardized template
                    file_path = BASE_DIR / config["path"]
                    
                    if not self.dry_run:
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(doc, f, indent=2, default=self.json_serializer, ensure_ascii=False)
                        print(f"   ✅ Standardized and saved")
                    else:
                        print(f"   🔍 [DRY-RUN] Would save standardized template")
                else:
                    print(f"   ✅ Already standardized")
                    
            except Exception as e:
                print(f"   ❌ Standardization failed: {e}")
        
        self.reports["structure_standardization"] = standardization_report
        return standardization_report
    
    def _extract_canonical_defaults(self, canonical: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Extract default values from canonical template"""
        defaults = {
            "template": {},
            "document": {},
            "section": {},
            "field": {}
        }
        
        # Template level defaults
        for key in CANONICAL_STRUCTURE["template_level"]:
            if key in canonical:
                if key in ["_id"]:
                    defaults["template"][key] = None  # Will be auto-generated
                elif key in ["isActive"]:
                    defaults["template"][key] = True
                elif key in ["createdAt", "updatedAt"]:
                    defaults["template"][key] = datetime.now().isoformat()
                elif key in ["version"]:
                    defaults["template"][key] = "1.0"
                elif key in ["metadata", "templateMetadata"]:
                    defaults["template"][key] = {}
                else:
                    defaults["template"][key] = canonical[key] if not isinstance(canonical[key], (list, dict)) else {}
        
        # Document level defaults
        if "documents" in canonical and canonical["documents"]:
            sample_doc = canonical["documents"][0]
            for key in CANONICAL_STRUCTURE["document_level"]:
                if key in sample_doc:
                    if key in ["_id"]:
                        defaults["document"][key] = None
                    elif key in ["isActive"]:
                        defaults["document"][key] = True
                    elif key in ["createdAt", "updatedAt"]:
                        defaults["document"][key] = datetime.now().isoformat()
                    elif key not in ["sections"]:
                        defaults["document"][key] = ""
        
        # Section level defaults
        if "documents" in canonical and canonical["documents"] and "sections" in canonical["documents"][0]:
            sample_section = canonical["documents"][0]["sections"][0]
            for key in CANONICAL_STRUCTURE["section_level"]:
                if key in sample_section:
                    if key == "sortOrder":
                        defaults["section"][key] = 1
                    elif key not in ["fields"]:
                        defaults["section"][key] = ""
        
        # Field level defaults
        if "documents" in canonical and canonical["documents"] and "sections" in canonical["documents"][0] and canonical["documents"][0]["sections"] and "fields" in canonical["documents"][0]["sections"][0]:
            sample_field = canonical["documents"][0]["sections"][0]["fields"][0]
            for key in CANONICAL_STRUCTURE["field_level"]:
                if key in sample_field:
                    if key == "isRequired":
                        defaults["field"][key] = False
                    elif key == "sortOrder":
                        defaults["field"][key] = 1
                    else:
                        defaults["field"][key] = ""
        
        return defaults
    
    def analyze_shared_fields(self) -> Dict[str, Any]:
        """Analyze fields shared across multiple templates"""
        print("\n" + "="*80)
        print("🔍 ANALYZING SHARED FIELDS")
        print("="*80)
        
        fieldid_to_collections = defaultdict(list)
        fieldid_to_variations = defaultdict(list)
        
        # Collect all fields
        for collection_name, config in TEMPLATE_COLLECTIONS.items():
            if config["is_common"]:
                continue
            
            try:
                doc = self.db[collection_name].find_one({})
                if doc and "documents" in doc:
                    for document in doc["documents"]:
                        if "sections" in document:
                            for section in document["sections"]:
                                if "fields" in section:
                                    for field in section["fields"]:
                                        field_id = field.get("fieldId")
                                        if field_id:
                                            fieldid_to_collections[field_id].append(collection_name)
                                            fieldid_to_variations[field_id].append({
                                                "collection": collection_name,
                                                "uiDisplayName": field.get("uiDisplayName"),
                                                "fieldType": field.get("fieldType"),
                                                "isRequired": field.get("isRequired"),
                                                "placeholder": field.get("placeholder")
                                            })
            except Exception as e:
                print(f"⚠️  Failed to analyze {collection_name}: {e}")
        
        # Find shared fields
        shared_fields = {fid: colls for fid, colls in fieldid_to_collections.items() if len(colls) > 1}
        
        # Analyze inconsistencies
        inconsistencies = {
            "name_variations": [],
            "type_variations": [],
            "requirement_variations": []
        }
        
        for field_id, variations in fieldid_to_variations.items():
            if len(variations) > 1:
                # Check name variations
                names = set(v["uiDisplayName"] for v in variations if v["uiDisplayName"])
                if len(names) > 1:
                    inconsistencies["name_variations"].append({
                        "fieldId": field_id,
                        "collections": len(variations),
                        "variations": list(names)
                    })
                
                # Check type variations
                types = set(v["fieldType"] for v in variations if v["fieldType"])
                if len(types) > 1:
                    inconsistencies["type_variations"].append({
                        "fieldId": field_id,
                        "collections": len(variations),
                        "variations": list(types)
                    })
                
                # Check requirement variations
                requirements = set(v["isRequired"] for v in variations if v["isRequired"] is not None)
                if len(requirements) > 1:
                    inconsistencies["requirement_variations"].append({
                        "fieldId": field_id,
                        "collections": len(variations),
                        "variations": list(requirements)
                    })
        
        analysis_report = {
            "timestamp": datetime.now().isoformat(),
            "total_unique_fields": len(fieldid_to_collections),
            "shared_fields_count": len(shared_fields),
            "shared_fields": {fid: len(colls) for fid, colls in shared_fields.items()},
            "inconsistencies": inconsistencies
        }
        
        print(f"\n📊 Analysis Results:")
        print(f"   Total unique fields: {len(fieldid_to_collections)}")
        print(f"   Shared fields (2+ templates): {len(shared_fields)}")
        print(f"   Name variations: {len(inconsistencies['name_variations'])}")
        print(f"   Type variations: {len(inconsistencies['type_variations'])}")
        print(f"   Requirement variations: {len(inconsistencies['requirement_variations'])}")
        
        if inconsistencies["name_variations"]:
            print(f"\n   ⚠️  Fields with name variations:")
            for item in inconsistencies["name_variations"][:10]:
                print(f"      {item['fieldId']}: {item['variations']}")
        
        self.reports["field_standardization"] = analysis_report
        return analysis_report
    
    def add_custom_template_field(self) -> Dict[str, Any]:
        """Add includeInCustomTemplate field to all templates"""
        print("\n" + "="*80)
        print("➕ ADDING includeInCustomTemplate FIELD")
        print("="*80)
        
        addition_report = {
            "timestamp": datetime.now().isoformat(),
            "templates_updated": [],
            "field_counts": {}
        }
        
        for collection_name, config in TEMPLATE_COLLECTIONS.items():
            print(f"\n➕ Processing: {collection_name}")
            
            try:
                file_path = BASE_DIR / config["path"]
                
                # Load from file (if downloaded) or MongoDB
                if file_path.exists() and not self.dry_run:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        doc = json.load(f)
                else:
                    doc = self.db[collection_name].find_one({})
                
                if not doc:
                    print(f"   ⚠️  No data found")
                    continue
                
                field_count = 0
                include_value = False if config["is_common"] else True
                
                # Process fields
                if config["is_common"]:
                    # Common fields template
                    if "fields" in doc:
                        for field in doc["fields"]:
                            field["includeInCustomTemplate"] = include_value
                            field_count += 1
                else:
                    # Bank templates
                    if "documents" in doc:
                        for document in doc["documents"]:
                            if "sections" in document:
                                for section in document["sections"]:
                                    if "fields" in section:
                                        for field in section["fields"]:
                                            field["includeInCustomTemplate"] = include_value
                                            field_count += 1
                
                print(f"   ✅ Updated {field_count} fields (includeInCustomTemplate={include_value})")
                
                addition_report["templates_updated"].append(collection_name)
                addition_report["field_counts"][collection_name] = {
                    "count": field_count,
                    "value": include_value
                }
                
                # Save
                if not self.dry_run:
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(doc, f, indent=2, default=self.json_serializer, ensure_ascii=False)
                    print(f"   💾 Saved")
                else:
                    print(f"   🔍 [DRY-RUN] Would save updates")
                    
            except Exception as e:
                print(f"   ❌ Failed: {e}")
        
        self.reports["custom_field_addition"] = addition_report
        return addition_report
    
    def save_reports(self, output_dir: Path):
        """Save all generated reports"""
        print("\n" + "="*80)
        print("📄 SAVING REPORTS")
        print("="*80)
        
        reports_dir = output_dir / "reports"
        
        if not self.dry_run:
            reports_dir.mkdir(parents=True, exist_ok=True)
        
        for report_name, report_data in self.reports.items():
            if report_data:
                report_file = reports_dir / f"{report_name}_report.json"
                
                if not self.dry_run:
                    with open(report_file, 'w', encoding='utf-8') as f:
                        json.dump(report_data, f, indent=2, default=self.json_serializer, ensure_ascii=False)
                    print(f"   ✅ {report_name}_report.json")
                else:
                    print(f"   🔍 [DRY-RUN] Would save {report_name}_report.json")
        
        print(f"\n📁 Reports location: {reports_dir}")
    
    def full_sync(self, backup: bool = True):
        """Execute full synchronization pipeline"""
        print("\n" + "="*80)
        print("🚀 FULL SYNCHRONIZATION PIPELINE")
        print("="*80)
        print(f"Mode: {'DRY-RUN (No changes will be made)' if self.dry_run else 'APPLY (Changes will be saved)'}")
        print("="*80)
        
        # Step 1: Create backup
        if backup and not self.dry_run:
            backup_dir = self.create_backup()
        
        # Step 2: Download templates
        download_report = self.download_templates()
        
        # Step 3: Load canonical template
        canonical = self.load_canonical_template("uco_land_property_details")
        
        # Step 4: Validate structure
        validation_report = self.validate_structure(canonical)
        
        # Step 5: Standardize structure
        standardization_report = self.standardize_structure(canonical)
        
        # Step 6: Analyze shared fields
        field_analysis = self.analyze_shared_fields()
        
        # Step 7: Add custom template field
        custom_field_report = self.add_custom_template_field()
        
        # Step 8: Save reports
        self.save_reports(BASE_DIR.parent)
        
        # Final summary
        print("\n" + "="*80)
        print("✅ SYNCHRONIZATION COMPLETE")
        print("="*80)
        print(f"📥 Downloaded: {len(download_report['downloaded'])} templates")
        print(f"🔍 Validated: {len(validation_report['templates_validated'])} templates")
        print(f"🔧 Standardized: {len(standardization_report['templates_updated'])} templates")
        print(f"➕ Updated with custom field: {len(custom_field_report['templates_updated'])} templates")
        print("="*80)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Template Manager - MongoDB Template Sync & Standardization",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "command",
        choices=["download", "validate", "standardize", "analyze", "add-custom-field", "full-sync"],
        help="Command to execute"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without making any changes (preview mode)"
    )
    
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create backup before making changes"
    )
    
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes (opposite of dry-run)"
    )
    
    parser.add_argument(
        "--canonical",
        default="uco",
        help="Canonical template to use (default: uco)"
    )
    
    args = parser.parse_args()
    
    # Determine dry-run mode
    dry_run = args.dry_run or not args.apply
    
    # Create manager
    manager = TemplateManager(dry_run=dry_run)
    
    try:
        # Connect to MongoDB
        if not manager.connect_mongodb():
            sys.exit(1)
        
        # Execute command
        if args.command == "download":
            if args.backup:
                manager.create_backup()
            manager.download_templates()
            manager.save_reports(BASE_DIR.parent)
            
        elif args.command == "validate":
            canonical = manager.load_canonical_template(f"{args.canonical}_land_property_details")
            manager.validate_structure(canonical)
            manager.save_reports(BASE_DIR.parent)
            
        elif args.command == "standardize":
            canonical = manager.load_canonical_template(f"{args.canonical}_land_property_details")
            manager.standardize_structure(canonical)
            manager.save_reports(BASE_DIR.parent)
            
        elif args.command == "analyze":
            manager.analyze_shared_fields()
            manager.save_reports(BASE_DIR.parent)
            
        elif args.command == "add-custom-field":
            manager.add_custom_template_field()
            manager.save_reports(BASE_DIR.parent)
            
        elif args.command == "full-sync":
            manager.full_sync(backup=args.backup)
        
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
        manager.close_mongodb()


if __name__ == "__main__":
    main()
