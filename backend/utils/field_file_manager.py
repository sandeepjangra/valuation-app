"""
Field File Manager - Handles local JSON file operations for form fields
"""

import json
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timezone
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class FieldFileManager:
    """Manages local JSON file storage for form fields"""
    
    def __init__(self, file_path: Optional[str] = None):
        # Default to backend/data directory
        if file_path is None:
            backend_dir = Path(__file__).parent.parent
            self.file_path = backend_dir / "data" / "common_fields.json"
        else:
            self.file_path = Path(file_path)
        
        # Ensure directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📁 Field file manager initialized: {self.file_path}")
    
    def write_fields(self, fields: List[Dict[str, Any]]) -> bool:
        """Write fields data to local JSON file"""
        try:
            # Prepare data with metadata
            file_data = {
                "metadata": {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "total_fields": len(fields),
                    "version": "1.0"
                },
                "fields": fields
            }
            
            # Write to temporary file first, then move (atomic operation)
            temp_file = self.file_path.with_suffix('.tmp')
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(file_data, f, indent=2, ensure_ascii=False, default=str)
            
            # Atomic move
            temp_file.replace(self.file_path)
            
            logger.info(f"✅ Successfully wrote {len(fields)} fields to {self.file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to write fields to file: {e}")
            # Clean up temp file if it exists
            temp_file = self.file_path.with_suffix('.tmp')
            if temp_file.exists():
                temp_file.unlink()
            return False
    
    def read_fields(self) -> Optional[List[Dict[str, Any]]]:
        """Read fields data from local JSON file"""
        try:
            if not self.file_path.exists():
                logger.warning(f"⚠️ Fields file does not exist: {self.file_path}")
                return None
            
            with open(self.file_path, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
            
            # Extract fields from the structure
            if isinstance(file_data, dict) and 'fields' in file_data:
                fields = file_data['fields']
                metadata = file_data.get('metadata', {})
                logger.info(f"📋 Successfully read {len(fields)} fields from file (generated: {metadata.get('generated_at', 'unknown')})")
                return fields
            elif isinstance(file_data, list):
                # Handle legacy format
                logger.info(f"📋 Successfully read {len(file_data)} fields from legacy format")
                return file_data
            else:
                logger.error(f"❌ Invalid file format in {self.file_path}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to read fields from file: {e}")
            return None
    
    def get_file_info(self) -> Dict[str, Any]:
        """Get information about the fields file"""
        try:
            if not self.file_path.exists():
                return {
                    "exists": False,
                    "path": str(self.file_path),
                    "size": 0,
                    "modified": None,
                    "field_count": 0,
                    "generated_at": None
                }
            
            # Get file stats
            stat = self.file_path.stat()
            
            # Try to read metadata
            metadata = {}
            field_count = 0
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                    if isinstance(file_data, dict):
                        metadata = file_data.get('metadata', {})
                        field_count = len(file_data.get('fields', []))
                    elif isinstance(file_data, list):
                        field_count = len(file_data)
            except:
                pass
            
            return {
                "exists": True,
                "path": str(self.file_path),
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                "field_count": field_count,
                "generated_at": metadata.get('generated_at'),
                "version": metadata.get('version')
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get file info: {e}")
            return {
                "exists": False,
                "error": str(e)
            }
    
    def delete_file(self) -> bool:
        """Delete the fields file"""
        try:
            if self.file_path.exists():
                self.file_path.unlink()
                logger.info(f"🗑️ Successfully deleted fields file: {self.file_path}")
                return True
            else:
                logger.warning(f"⚠️ File does not exist, nothing to delete: {self.file_path}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to delete fields file: {e}")
            return False

# Create a global instance
field_file_manager = FieldFileManager()