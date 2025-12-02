#!/usr/bin/env python3
"""
Table Standardization Script

This script standardizes table fields across all bank templates:
1. Adds missing boundaries_dimensions_table to templates that don't have it
2. Standardizes dynamic table structures for consistency
3. Ensures all similar tables have identical schemas

Usage:
    python standardize_tables.py --dry-run
    python standardize_tables.py --apply
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import argparse

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent / "backend" / "data"

# Standard table definitions
STANDARD_TABLES = {
    "boundaries_dimensions_table": {
        "fieldId": "boundaries_dimensions_table",
        "uiDisplayName": "Boundaries and Dimensions Table",
        "fieldType": "table",
        "isRequired": False,
        "sortOrder": 999,  # Will be adjusted based on section
        "columns": [
            {
                "columnId": "direction",
                "columnName": "Direction",
                "fieldType": "text",
                "isReadonly": True
            },
            {
                "columnId": "boundaries_per_documents",
                "columnName": "Boundaries As Per Documents",
                "fieldType": "text",
                "isRequired": False,
                "isEditable": True
            },
            {
                "columnId": "boundaries_actual",
                "columnName": "Boundaries Actual",
                "fieldType": "text",
                "isRequired": False,
                "isEditable": True
            },
            {
                "columnId": "dimensions_per_documents",
                "columnName": "Dimensions As Per Documents",
                "fieldType": "number",
                "isRequired": False,
                "isEditable": True
            },
            {
                "columnId": "dimensions_actuals",
                "columnName": "Dimensions Actuals",
                "fieldType": "number",
                "isRequired": False,
                "isEditable": True
            }
        ],
        "rows": [
            {
                "direction": "North",
                "boundaries_per_documents": "",
                "boundaries_actual": "",
                "dimensions_per_documents": "",
                "dimensions_actuals": ""
            },
            {
                "direction": "South",
                "boundaries_per_documents": "",
                "boundaries_actual": "",
                "dimensions_per_documents": "",
                "dimensions_actuals": ""
            },
            {
                "direction": "East",
                "boundaries_per_documents": "",
                "boundaries_actual": "",
                "dimensions_per_documents": "",
                "dimensions_actuals": ""
            },
            {
                "direction": "West",
                "boundaries_per_documents": "",
                "boundaries_actual": "",
                "dimensions_per_documents": "",
                "dimensions_actuals": ""
            }
        ],
        "placeholder": "",
        "includeInCustomTemplate": True
    },
    
    "building_specifications_table": {
        "fieldId": "building_specifications_table",
        "uiDisplayName": "Building Specifications",
        "fieldType": "dynamic_table",
        "isRequired": False,
        "sortOrder": 999,
        "tableConfig": {
            "tableType": "column_dynamic",
            "fixedColumns": [
                {
                    "columnId": "sr_no",
                    "columnName": "Sr. No.",
                    "fieldType": "text",
                    "isReadonly": True
                },
                {
                    "columnId": "description",
                    "columnName": "Description",
                    "fieldType": "text",
                    "isReadonly": True
                }
            ],
            "dynamicColumns": {
                "columnType": "floor",
                "defaultColumns": [
                    {
                        "columnId": "ground_floor",
                        "columnName": "Ground Floor",
                        "fieldType": "text",
                        "isRequired": False
                    }
                ],
                "addColumnConfig": {
                    "buttonText": "Add Floor",
                    "columnNamePattern": "Floor {number}",
                    "maxColumns": 10
                }
            },
            "rows": [
                {"sr_no": "1.", "description": "Description"},
                {"sr_no": "2.", "description": "Foundation"},
                {"sr_no": "3.", "description": "Basement"},
                {"sr_no": "4.", "description": "Superstructure"},
                {"sr_no": "5.", "description": "Joinery/Door and Windows"},
                {"sr_no": "6.", "description": "RCC Works"},
                {"sr_no": "7.", "description": "Plastering"},
                {"sr_no": "8.", "description": "Flooring/Skirting"},
                {"sr_no": "9.", "description": "Any Special Finishing"},
                {"sr_no": "10.", "description": "Water Proof Course"},
                {"sr_no": "11.", "description": "Drainage"},
                {"sr_no": "12.", "description": "Compound Wall"},
                {"sr_no": "13.", "description": "Electrical Installation"},
                {"sr_no": "14.", "description": "Plumbing Installation"},
                {"sr_no": "15.", "description": "Bore Well"},
                {"sr_no": "16.", "description": "Wardrobes"},
                {"sr_no": "17.", "description": "Development of Open Areas"}
            ]
        },
        "placeholder": "",
        "includeInCustomTemplate": True
    },
    
    "floor_wise_valuation_table": {
        "fieldId": "floor_wise_valuation_table",
        "uiDisplayName": "Floor-wise Valuation Details",
        "fieldType": "dynamic_table",
        "isRequired": False,
        "sortOrder": 999,
        "tableConfig": {
            "tableType": "row_dynamic",
            "fixedColumns": [
                {
                    "columnId": "sr_no",
                    "columnName": "Sr. No.",
                    "fieldType": "text",
                    "isReadonly": True
                },
                {
                    "columnId": "floors_level",
                    "columnName": "Floors/Level",
                    "fieldType": "text",
                    "isRequired": False
                },
                {
                    "columnId": "particulars_description",
                    "columnName": "Particulars/Description of the Items",
                    "fieldType": "textarea",
                    "isRequired": False
                },
                {
                    "columnId": "plinth_covered_area",
                    "columnName": "Plinth/Covered Area (in Sq.ft.)",
                    "fieldType": "number",
                    "isRequired": False
                },
                {
                    "columnId": "estimated_replacement_rate",
                    "columnName": "Estimated Replacement Rate per Sq.ft. (in Rs.)",
                    "fieldType": "currency",
                    "isRequired": False
                },
                {
                    "columnId": "estimated_replacement_cost",
                    "columnName": "Estimated Replacement Cost",
                    "fieldType": "currency",
                    "isRequired": False
                },
                {
                    "columnId": "depreciation",
                    "columnName": "Depreciation @ 1.5% per year",
                    "fieldType": "currency",
                    "isRequired": False
                },
                {
                    "columnId": "net_value",
                    "columnName": "Net Value",
                    "fieldType": "currency",
                    "isRequired": False
                }
            ],
            "maxRows": 10,
            "addRowConfig": {
                "buttonText": "Add Row"
            },
            "rows": [
                {
                    "sr_no": "1.",
                    "floors_level": "",
                    "particulars_description": "",
                    "plinth_covered_area": "",
                    "estimated_replacement_rate": "",
                    "estimated_replacement_cost": "",
                    "depreciation": "",
                    "net_value": ""
                }
            ]
        },
        "placeholder": "",
        "includeInCustomTemplate": True
    }
}

# Template collections to process
TEMPLATES = {
    "bob/bob_land_property_details.json": {"name": "BOB Land", "add_tables": ["boundaries_dimensions_table"]},
    "boi/boi_apartment_property_details.json": {"name": "BOI Apartment", "add_tables": []},
    "boi/boi_land_property_details.json": {"name": "BOI Land", "add_tables": [], "standardize": ["building_specifications_table", "floor_wise_valuation_table"]},
    "cbi/cbi_all_property_details.json": {"name": "CBI All", "add_tables": ["boundaries_dimensions_table"]},
    "hdfc/hdfc_all_property_details.json": {"name": "HDFC All", "add_tables": ["boundaries_dimensions_table"]},
    "pnb/pnb_land_property_details.json": {"name": "PNB Land", "add_tables": ["boundaries_dimensions_table"]},
    "sbi/apartment/sbi_apartment_property_details.json": {"name": "SBI Apartment", "add_tables": []},
    "sbi/land/sbi_land_property_details.json": {"name": "SBI Land", "add_tables": ["boundaries_dimensions_table", "building_specifications_table", "floor_wise_valuation_table"]},
    "ubi/apartment/ubi_apartment_property_details.json": {"name": "UBI Apartment", "add_tables": ["boundaries_dimensions_table"]},
    "ubi/land/ubi_land_property_details.json": {"name": "UBI Land", "add_tables": ["boundaries_dimensions_table", "building_specifications_table", "floor_wise_valuation_table"]},
    "uco/apartment/uco_apartment_property_details.json": {"name": "UCO Apartment", "add_tables": []},
    "uco/land/uco_land_property_details.json": {"name": "UCO Land", "add_tables": [], "standardize": ["building_specifications_table", "floor_wise_valuation_table"]},
}


class TableStandardizer:
    """Standardize table fields across templates"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "templates_processed": [],
            "tables_added": {},
            "tables_standardized": {},
            "errors": []
        }
    
    def json_serializer(self, obj):
        """Handle datetime for JSON serialization"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    def find_best_section_for_table(self, doc: Dict[str, Any], table_id: str) -> int:
        """Find the best section to add a table to"""
        # Prefer sections with "Part B", "Part D", "Location", "Others" in the name
        preferred_keywords = {
            "boundaries_dimensions_table": ["location", "part b", "property details"],
            "building_specifications_table": ["building", "construction", "part b"],
            "floor_wise_valuation_table": ["valuation", "part c"]
        }
        
        keywords = preferred_keywords.get(table_id, [])
        
        if "sections" in doc and doc["sections"]:
            for idx, section in enumerate(doc["sections"]):
                section_name = section.get("sectionName", "").lower()
                if any(kw in section_name for kw in keywords):
                    return idx
            # If no match, return last section
            return len(doc["sections"]) - 1
        
        return 0
    
    def add_table_to_template(self, template_path: str, table_ids: List[str]) -> bool:
        """Add missing tables to a template"""
        file_path = BASE_DIR / template_path
        
        if not file_path.exists():
            self.report["errors"].append(f"File not found: {template_path}")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            changes_made = []
            
            for table_id in table_ids:
                # Check if table already exists
                table_exists = False
                if "documents" in data:
                    for doc in data["documents"]:
                        if "sections" in doc:
                            for section in doc["sections"]:
                                if "fields" in section:
                                    if any(f.get("fieldId") == table_id for f in section["fields"]):
                                        table_exists = True
                                        break
                        elif "fields" in doc:
                            if any(f.get("fieldId") == table_id for f in doc["fields"]):
                                table_exists = True
                                break
                
                if table_exists:
                    print(f"   ⚠️  {table_id} already exists, skipping")
                    continue
                
                # Add table to appropriate section
                if "documents" in data and data["documents"]:
                    doc = data["documents"][0]  # Add to first document
                    
                    # Create sections if they don't exist
                    if "sections" not in doc:
                        doc["sections"] = [{
                            "sectionId": "part_d_others",
                            "sectionName": "Part D - Others",
                            "sortOrder": 999,
                            "fields": []
                        }]
                    
                    # Find best section
                    section_idx = self.find_best_section_for_table(doc, table_id)
                    section = doc["sections"][section_idx]
                    
                    # Initialize fields if needed
                    if "fields" not in section:
                        section["fields"] = []
                    
                    # Add table
                    table_def = STANDARD_TABLES[table_id].copy()
                    table_def["sortOrder"] = len(section["fields"]) + 1
                    section["fields"].append(table_def)
                    
                    changes_made.append(f"Added {table_id} to section '{section.get('sectionName')}'")
                    print(f"   ✅ Added {table_id}")
            
            if changes_made:
                self.report["tables_added"][template_path] = changes_made
                
                # Save file
                if not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, default=self.json_serializer, ensure_ascii=False)
                    print(f"   💾 Saved changes")
                else:
                    print(f"   🔍 [DRY-RUN] Would save changes")
            
            return True
            
        except Exception as e:
            error_msg = f"Error processing {template_path}: {str(e)}"
            self.report["errors"].append(error_msg)
            print(f"   ❌ {error_msg}")
            return False
    
    def standardize_table_in_template(self, template_path: str, table_ids: List[str]) -> bool:
        """Standardize existing tables in a template"""
        file_path = BASE_DIR / template_path
        
        if not file_path.exists():
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            changes_made = []
            
            for table_id in table_ids:
                # Find and update table
                if "documents" in data:
                    for doc in data["documents"]:
                        if "sections" in doc:
                            for section in doc["sections"]:
                                if "fields" in section:
                                    for idx, field in enumerate(section["fields"]):
                                        if field.get("fieldId") == table_id:
                                            # Replace with standard definition
                                            old_sort_order = field.get("sortOrder", 1)
                                            new_field = STANDARD_TABLES[table_id].copy()
                                            new_field["sortOrder"] = old_sort_order
                                            section["fields"][idx] = new_field
                                            changes_made.append(f"Standardized {table_id}")
                                            print(f"   🔧 Standardized {table_id}")
            
            if changes_made:
                self.report["tables_standardized"][template_path] = changes_made
                
                if not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, default=self.json_serializer, ensure_ascii=False)
                    print(f"   💾 Saved changes")
                else:
                    print(f"   🔍 [DRY-RUN] Would save changes")
            
            return True
            
        except Exception as e:
            error_msg = f"Error standardizing {template_path}: {str(e)}"
            self.report["errors"].append(error_msg)
            print(f"   ❌ {error_msg}")
            return False
    
    def process_all_templates(self):
        """Process all templates"""
        print("=" * 80)
        print("TABLE STANDARDIZATION")
        print("=" * 80)
        print(f"Mode: {'DRY-RUN (No changes will be made)' if self.dry_run else 'APPLY (Changes will be saved)'}")
        print("=" * 80)
        
        for template_path, config in TEMPLATES.items():
            print(f"\n📋 {config['name']}")
            
            # Add missing tables
            if config.get("add_tables"):
                print(f"   Adding tables: {', '.join(config['add_tables'])}")
                self.add_table_to_template(template_path, config["add_tables"])
            
            # Standardize existing tables
            if config.get("standardize"):
                print(f"   Standardizing tables: {', '.join(config['standardize'])}")
                self.standardize_table_in_template(template_path, config["standardize"])
            
            if not config.get("add_tables") and not config.get("standardize"):
                print(f"   ✅ No changes needed")
            
            self.report["templates_processed"].append(template_path)
        
        # Save report
        report_file = BASE_DIR.parent / "reports" / "table_standardization_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, default=self.json_serializer, ensure_ascii=False)
        
        print("\n" + "=" * 80)
        print("STANDARDIZATION COMPLETE")
        print("=" * 80)
        print(f"Templates processed: {len(self.report['templates_processed'])}")
        print(f"Tables added: {sum(len(v) for v in self.report['tables_added'].values())}")
        print(f"Tables standardized: {sum(len(v) for v in self.report['tables_standardized'].values())}")
        print(f"Errors: {len(self.report['errors'])}")
        print(f"\n📄 Report saved to: {report_file}")
        print("=" * 80)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Standardize table fields across templates")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    parser.add_argument("--apply", action="store_true", help="Apply changes")
    
    args = parser.parse_args()
    
    dry_run = args.dry_run or not args.apply
    
    standardizer = TableStandardizer(dry_run=dry_run)
    standardizer.process_all_templates()


if __name__ == "__main__":
    main()
