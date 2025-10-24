#!/usr/bin/env python3
"""
MongoDB Collections Refresh Script
Standalone script to refresh all collections from MongoDB to local JSON files
"""

import logging
import sys
import json
import requests
import re
from datetime import datetime
from pathlib import Path
from typing import Tuple, Dict, List, Optional, Union

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/refresh_collections.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Backend API configuration
API_BASE_URL = "http://localhost:8000/api"
TIMEOUT = 30

class CollectionOrganizer:
    """Handles collection naming pattern analysis and folder organization"""
    
    def __init__(self, base_data_path: Union[str, Path]) -> None:
        self.base_data_path = Path(base_data_path)
        self.collection_pattern = re.compile(r'^([a-zA-Z]+)_([a-zA-Z]+)_(.+)$')
        
    def parse_collection_name(self, collection_name: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Parse collection name to extract bank, template_type, and description
        Expected pattern: {bank}_{template_type}_{description}
        
        Returns:
            tuple: (bank, template_type, description) or (None, None, None) if no match
        """
        match = self.collection_pattern.match(collection_name)
        if match:
            bank = match.group(1).lower()
            template_type = match.group(2).lower()
            description = match.group(3)
            return bank, template_type, description
        return None, None, None
    
    def get_collection_path(self, collection_name: str) -> Path:
        """
        Determine the appropriate path for storing collection data
        
        Returns:
            Path: Full path where the collection JSON should be stored
        """
        bank, template_type, _ = self.parse_collection_name(collection_name)
        
        if bank and template_type:
            # Organized path: data/{bank}/{template_type}/{collection_name}.json
            folder_path = self.base_data_path / bank / template_type
            folder_path.mkdir(parents=True, exist_ok=True)
            file_path = folder_path / f"{collection_name}.json"
            logger.info(f"📁 Organized path for {collection_name}: {bank}/{template_type}/")
        else:
            # Fallback to root data folder for unmatched patterns
            file_path = self.base_data_path / f"{collection_name}.json"
            logger.info(f"📁 Fallback path for {collection_name}: root data folder")
        
        return file_path
    
    def get_folder_structure_info(self) -> Dict[str, Dict[str, List[str]]]:
        """Get information about the current folder structure"""
        structure: Dict[str, Dict[str, List[str]]] = {}
        
        # Scan for organized folders
        for bank_folder in self.base_data_path.iterdir():
            if bank_folder.is_dir() and not bank_folder.name.startswith('.'):
                bank_name = bank_folder.name
                structure[bank_name] = {}
                
                for template_folder in bank_folder.iterdir():
                    if template_folder.is_dir():
                        template_name = template_folder.name
                        collections: List[str] = []
                        
                        for json_file in template_folder.glob("*.json"):
                            collections.append(json_file.stem)
                        
                        structure[bank_name][template_name] = collections
        
        return structure

def ensure_logs_directory() -> None:
    """Ensure logs directory exists"""
    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)

def check_backend_status() -> bool:
    """Check if backend server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def get_collections_list() -> List[str]:
    """Get list of all collections from the backend"""
    try:
        response = requests.get(f"{API_BASE_URL}/admin/collections-status", timeout=10)
        if response.status_code == 200:
            collections_data = response.json()
            return list(collections_data.keys())
        return []
    except Exception as e:
        logger.error(f"Error getting collections list: {e}")
        return []

def refresh_single_collection_organized(collection_name: str, organizer: CollectionOrganizer) -> Tuple[bool, int]:
    """Refresh a single collection from MongoDB and store it in organized folder structure"""
    try:
        logger.info(f"🔄 Refreshing collection from MongoDB: {collection_name}")
        
        # Use the existing refresh API to pull from MongoDB
        response = requests.post(
            f"{API_BASE_URL}/admin/refresh-collection/{collection_name}",
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            doc_count = data.get('documents_count', 0)
            logger.info(f"✅ {collection_name} refreshed from MongoDB!")
            logger.info(f"📊 {doc_count} documents pulled from MongoDB")
            
            # Now organize the file that was created in root folder
            organize_existing_file(collection_name, organizer)
            
            return True, doc_count
        else:
            logger.error(f"❌ Failed to refresh {collection_name}: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False, 0
            
    except Exception as e:
        logger.error(f"❌ Error refreshing {collection_name}: {e}")
        return False, 0

def organize_existing_file(collection_name: str, organizer: CollectionOrganizer) -> None:
    """Move an existing file from root to organized folder structure"""
    try:
        # Source file (current location in root)
        source_file = organizer.base_data_path / f"{collection_name}.json"
        
        # Determine target location
        target_file = organizer.get_collection_path(collection_name)
        
        # If source exists and target is different from source, move it
        if source_file.exists() and source_file != target_file:
            # Read the content
            with open(source_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Write to organized location
            with open(target_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Remove from root folder
            source_file.unlink()
            
            logger.info(f"� Moved {collection_name}.json to organized folder: {target_file}")
        elif target_file.exists():
            logger.info(f"📁 {collection_name} already in organized location: {target_file}")
        else:
            logger.warning(f"⚠️ Source file not found: {source_file}")
            
    except Exception as e:
        logger.error(f"❌ Error organizing file {collection_name}: {e}")

def refresh_all_collections_organized() -> bool:
    """Refresh all collections from MongoDB and organize them in folder structure"""
    try:
        logger.info("🔄 Starting enhanced refresh from MongoDB...")
        
        # First, refresh all collections from MongoDB using existing API
        logger.info("📡 Step 1: Refreshing all collections from MongoDB...")
        response = requests.post(f"{API_BASE_URL}/admin/refresh-collections", timeout=TIMEOUT)
        
        if response.status_code != 200:
            logger.error(f"❌ Failed to refresh from MongoDB: {response.status_code}")
            return False
        
        refresh_data = response.json()
        logger.info(f"✅ MongoDB refresh completed: {refresh_data.get('successful_count', 0)}/{refresh_data.get('total_count', 0)} collections")
        
        # Initialize organizer
        base_data_path = Path(__file__).parent.parent / "backend" / "data"
        organizer = CollectionOrganizer(base_data_path)
        
        # Step 2: Organize the refreshed files into proper folder structure
        logger.info("📁 Step 2: Organizing files into folder structure...")
        
        # First organize all existing files (including ones not refreshed)
        organize_all_existing_files(organizer)
        
        successful_organized = 0
        total_documents = 0
        organization_results = {}
        
        # Get the list of refreshed collections
        refreshed_collections = refresh_data.get('results', {})
        
        for collection_name, was_refreshed in refreshed_collections.items():
            if was_refreshed:
                try:
                    # Organize the file that was refreshed from MongoDB
                    organize_existing_file(collection_name, organizer)
                    organization_results[collection_name] = True
                    successful_organized += 1
                    
                    # Get document count from the organized file
                    target_file = organizer.get_collection_path(collection_name)
                    if target_file.exists():
                        with open(target_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                total_documents += len(data)
                            elif isinstance(data, dict) and 'data' in data:
                                total_documents += len(data.get('data', []))
                                
                except Exception as e:
                    logger.error(f"❌ Failed to organize {collection_name}: {e}")
                    organization_results[collection_name] = False
            else:
                organization_results[collection_name] = False
        
        # Show results summary
        logger.info("✅ Enhanced refresh and organization completed!")
        logger.info(f"📊 MongoDB Refresh: {refresh_data.get('successful_count', 0)}/{refresh_data.get('total_count', 0)} collections")
        logger.info(f"📁 Organization: {successful_organized}/{len(refreshed_collections)} files organized")
        logger.info(f"📄 Total documents: {total_documents}")
        
        # Show organization structure
        logger.info("� Current folder organization:")
        structure = organizer.get_folder_structure_info()
        if structure:
            for bank, templates in structure.items():
                logger.info(f"   📂 {bank}/")
                for template, collections_list in templates.items():
                    logger.info(f"      📂 {template}/ ({len(collections_list)} collections)")
                    for collection in collections_list:
                        logger.info(f"         📄 {collection}.json")
        
        # Show detailed results
        logger.info("📋 Collection organization results:")
        for collection, success in organization_results.items():
            status = "✅" if success else "❌"
            # Analyze organization
            bank, template_type, _ = organizer.parse_collection_name(collection)
            if bank and template_type:
                location = f"{bank}/{template_type}/"
            else:
                location = "root/"
            logger.info(f"   {status} {collection:<30} → {location}")
        
        return refresh_data.get('successful_count', 0) == refresh_data.get('total_count', 0)
        
    except Exception as e:
        logger.error(f"❌ Error in enhanced refresh: {e}")
        return False

def organize_all_existing_files(organizer: CollectionOrganizer) -> int:
    """Organize all existing files in the data directory based on naming patterns"""
    try:
        logger.info("📁 Organizing all existing files based on naming patterns...")
        
        organized_count = 0
        
        # Get all JSON files in the root data directory
        for json_file in organizer.base_data_path.glob("*.json"):
            collection_name = json_file.stem
            
            # Parse the collection name to see if it matches the pattern
            bank, template_type, _ = organizer.parse_collection_name(collection_name)
            
            if bank and template_type:
                # This file should be organized
                target_file = organizer.get_collection_path(collection_name)
                
                # If the target is different from source, move it
                if json_file != target_file:
                    try:
                        # Read the content
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Write to organized location
                        with open(target_file, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)
                        
                        # Remove from root folder
                        json_file.unlink()
                        
                        logger.info(f"📁 Moved {collection_name}.json to organized folder: {target_file}")
                        organized_count += 1
                        
                    except Exception as e:
                        logger.error(f"❌ Error moving {collection_name}.json: {e}")
                else:
                    logger.info(f"📁 {collection_name} already in correct location")
            else:
                logger.info(f"📁 {collection_name} stays in root folder (no pattern match)")
        
        logger.info(f"✅ Organization complete: {organized_count} files moved")
        return organized_count
        
    except Exception as e:
        logger.error(f"❌ Error organizing existing files: {e}")
        return 0

def refresh_all_collections_api() -> bool:
    """Refresh all collections using the REST API"""
    try:
        logger.info("🔄 Starting refresh of all collections via API...")
        
        response = requests.post(
            f"{API_BASE_URL}/admin/refresh-collections",
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ All collections refreshed successfully!")
            logger.info(f"📊 Results: {data.get('successful_count', 0)}/{data.get('total_count', 0)} collections")
            
            # Show detailed results
            results = data.get('results', {})
            for collection, success in results.items():
                status = "✅" if success else "❌"
                logger.info(f"   {status} {collection}")
            
            return True
        else:
            logger.error(f"❌ API call failed with status {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error calling refresh API: {e}")
        return False

def refresh_single_collection_api(collection_name: str) -> bool:
    """Refresh a single collection using the REST API"""
    try:
        logger.info(f"🔄 Refreshing collection: {collection_name}")
        
        response = requests.post(
            f"{API_BASE_URL}/admin/refresh-collection/{collection_name}",
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ {collection_name} refreshed successfully!")
            logger.info(f"📊 {data.get('documents_count', 0)} documents updated")
            return True
        else:
            logger.error(f"❌ Failed to refresh {collection_name}: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error refreshing {collection_name}: {e}")
        return False

def get_collections_status() -> Optional[Dict[str, Dict]]:
    """Get status of all collections"""
    try:
        response = requests.get(f"{API_BASE_URL}/admin/collections-status", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        logger.error(f"Error getting collections status: {e}")
        return None

def print_collections_status() -> None:
    """Print current status of all collections with organization info"""
    logger.info("📋 Getting collections status...")
    status = get_collections_status()
    
    if not status:
        logger.error("❌ Failed to get collections status")
        return
    
    # Initialize organizer for path analysis
    base_data_path = Path(__file__).parent.parent / "backend" / "data"
    organizer = CollectionOrganizer(base_data_path)
    
    logger.info("📊 Collections Status & Organization:")
    logger.info("-" * 100)
    
    for collection_name, info in status.items():
        # Analyze organization
        bank, template_type, _ = organizer.parse_collection_name(collection_name)
        
        if info.get('file_exists', False):
            docs = info.get('total_documents', 0)
            last_mod = info.get('last_modified', 'Unknown')
            if last_mod != 'Unknown':
                try:
                    dt = datetime.fromisoformat(last_mod.replace('Z', '+00:00'))
                    last_mod = dt.strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    pass
            
            if bank and template_type:
                org_path = f"{bank}/{template_type}/"
                pattern_match = "✅ Organized"
            else:
                org_path = "root/"
                pattern_match = "⚪ Root folder"
            
            logger.info(f"{pattern_match} {collection_name:<25} | {docs:>4} docs | {org_path:<15} | {last_mod}")
        else:
            logger.info(f"❌ Missing   {collection_name:<25} | File not found")
    
    logger.info("-" * 100)
    
    # Show folder structure summary
    logger.info("📁 Current Folder Structure:")
    structure = organizer.get_folder_structure_info()
    if structure:
        for bank, templates in structure.items():
            logger.info(f"   📂 data/{bank}/")
            for template, collections_list in templates.items():
                logger.info(f"      📂 {template}/ ({len(collections_list)} files)")
    else:
        logger.info("   No organized folder structure found")

def interactive_menu() -> None:
    """Interactive menu for refresh operations with enhanced organization"""
    collections = [
        "common_fields",
        "sbi_land_property_details", 
        "banks",
        "users",
        "properties",
        "valuations",
        "valuation_reports",
        "audit_logs"
    ]
    
    while True:
        print("\n" + "="*70)
        print("🔄 Enhanced MongoDB Collections Refresh Tool")
        print("="*70)
        print("1. Enhanced refresh ALL collections (organized)")
        print("2. Refresh specific collection (organized)")
        print("3. Show collections status & organization")
        print("4. Show folder structure")
        print("5. Test collection name parsing")
        print("6. Legacy refresh all collections")
        print("7. Test backend connection")
        print("8. Exit")
        print("-"*70)
        
        choice = input("Enter your choice (1-8): ").strip()
        
        if choice == "1":
            print("\n🔄 Enhanced refresh of all collections...")
            success = refresh_all_collections_organized()
            if success:
                print("\n🎉 All collections refreshed and organized successfully!")
            else:
                print("\n❌ Some collections failed to refresh. Check logs for details.")
                
        elif choice == "2":
            print("\nAvailable collections:")
            for i, collection in enumerate(collections, 1):
                print(f"{i:2d}. {collection}")
            
            try:
                coll_choice = int(input(f"\nEnter collection number (1-{len(collections)}): "))
                if 1 <= coll_choice <= len(collections):
                    collection_name = collections[coll_choice - 1]
                    base_data_path = Path(__file__).parent.parent / "backend" / "data"
                    organizer = CollectionOrganizer(base_data_path)
                    success, doc_count = refresh_single_collection_organized(collection_name, organizer)
                    if success:
                        print(f"✅ {collection_name} refreshed successfully! ({doc_count} documents)")
                    else:
                        print(f"❌ Failed to refresh {collection_name}")
                else:
                    print("❌ Invalid collection number")
            except ValueError:
                print("❌ Please enter a valid number")
                
        elif choice == "3":
            print_collections_status()
            
        elif choice == "4":
            print("\n� Current Folder Structure:")
            base_data_path = Path(__file__).parent.parent / "backend" / "data"
            organizer = CollectionOrganizer(base_data_path)
            structure = organizer.get_folder_structure_info()
            
            if structure:
                for bank, templates in structure.items():
                    print(f"   📂 data/{bank}/")
                    for template, collections_list in templates.items():
                        print(f"      📂 {template}/ ({len(collections_list)} files)")
                        for collection in collections_list:
                            print(f"         📄 {collection}.json")
            else:
                print("   No organized folder structure found")
                
        elif choice == "5":
            print("\n🧪 Test Collection Name Parsing:")
            test_names = [
                "sbi_land_property_details",
                "icici_apartment_valuation_template", 
                "hdfc_commercial_assessment_form",
                "common_fields",
                "banks",
                "ubi_land_details"
            ]
            
            base_data_path = Path(__file__).parent.parent / "backend" / "data"
            organizer = CollectionOrganizer(base_data_path)
            
            for name in test_names:
                bank, template_type, description = organizer.parse_collection_name(name)
                if bank and template_type:
                    path = f"data/{bank}/{template_type}/{name}.json"
                    print(f"✅ {name:<30} → {path}")
                else:
                    path = f"data/{name}.json"
                    print(f"⚪ {name:<30} → {path} (fallback)")
                    
        elif choice == "6":
            print("\n🔄 Legacy refresh all collections...")
            success = refresh_all_collections_api()
            if success:
                print("\n🎉 Legacy refresh completed!")
            else:
                print("\n❌ Legacy refresh failed. Check logs for details.")
                
        elif choice == "7":
            print("\n�🔍 Testing backend connection...")
            if check_backend_status():
                print("✅ Backend is running and accessible")
                collections_list = get_collections_list()
                print(f"📋 Found {len(collections_list)} collections")
            else:
                print("❌ Backend is not accessible")
                print("💡 Make sure the backend server is running on port 8000")
                
        elif choice == "8":
            print("\n👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-8.")

def main() -> None:
    """Main function"""
    ensure_logs_directory()
    
    logger.info("🚀 Enhanced MongoDB Collections Refresh Script Started")
    logger.info(f"🎯 Target API: {API_BASE_URL}")
    logger.info("📁 Enhanced with automatic folder organization")
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--enhanced-all":
            # Enhanced refresh all collections
            if not check_backend_status():
                logger.error("❌ Backend server is not running. Please start it first.")
                sys.exit(1)
            
            success = refresh_all_collections_organized()
            sys.exit(0 if success else 1)
            
        elif sys.argv[1] == "--all":
            # Legacy refresh all collections
            if not check_backend_status():
                logger.error("❌ Backend server is not running. Please start it first.")
                sys.exit(1)
            
            success = refresh_all_collections_api()
            sys.exit(0 if success else 1)
            
        elif sys.argv[1] == "--status":
            # Show status only
            if not check_backend_status():
                logger.error("❌ Backend server is not running.")
                sys.exit(1)
            
            print_collections_status()
            sys.exit(0)
            
        elif sys.argv[1] == "--organize":
            # Organize existing files only (no MongoDB refresh)
            if not check_backend_status():
                logger.error("❌ Backend server is not running.")
                sys.exit(1)
            
            base_data_path = Path(__file__).parent.parent / "backend" / "data"
            organizer = CollectionOrganizer(base_data_path)
            organized_count = organize_all_existing_files(organizer)
            
            logger.info(f"✅ Organization complete: {organized_count} files moved")
            sys.exit(0)
            
        elif sys.argv[1] == "--collection":
            # Refresh specific collection with organization
            if len(sys.argv) < 3:
                logger.error("❌ Please specify collection name: --collection <name>")
                sys.exit(1)
            
            collection_name = sys.argv[2]
            if not check_backend_status():
                logger.error("❌ Backend server is not running.")
                sys.exit(1)
            
            base_data_path = Path(__file__).parent.parent / "backend" / "data"
            organizer = CollectionOrganizer(base_data_path)
            success, _ = refresh_single_collection_organized(collection_name, organizer)
            sys.exit(0 if success else 1)
            
        elif sys.argv[1] in ["--help", "-h"]:
            print("Enhanced MongoDB Collections Refresh Script")
            print("\nUsage:")
            print("  python refresh_collections.py                        # Interactive mode")
            print("  python refresh_collections.py --enhanced-all         # Enhanced refresh all")
            print("  python refresh_collections.py --all                  # Legacy refresh all")
            print("  python refresh_collections.py --organize             # Organize existing files only")
            print("  python refresh_collections.py --status               # Show status")
            print("  python refresh_collections.py --collection <name>    # Refresh specific")
            print("  python refresh_collections.py --help                 # Show this help")
            print("\nFeatures:")
            print("  • Automatic folder organization based on collection names")
            print("  • Pattern: {bank}_{template_type}_{description}")
            print("  • Creates folder structure: data/{bank}/{template_type}/")
            print("  • Fallback to root folder for unmatched patterns")
            print("\nExamples:")
            print("  python refresh_collections.py --collection sbi_land_property_details")
            print("  python refresh_collections.py --enhanced-all")
            print("  python refresh_collections.py --organize")
            sys.exit(0)
        else:
            logger.error(f"❌ Unknown argument: {sys.argv[1]}")
            logger.error("Use --help for usage information")
            sys.exit(1)
    
    # Interactive mode
    if not check_backend_status():
        logger.error("❌ Backend server is not running on port 8000")
        logger.error("💡 Please start the backend server first:")
        logger.error("   cd /path/to/project && source valuation_env/bin/activate")
        logger.error("   python -m uvicorn backend.main:app --port 8000")
        sys.exit(1)
    
    # Run interactive menu
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Script interrupted by user. Goodbye!")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()