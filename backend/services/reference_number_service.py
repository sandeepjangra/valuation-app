"""
Report Reference Number Service
Handles atomic generation and validation of unique report reference numbers
Format: {initials}/{sequence:04d}/{date_DDMMYYYY}
Example: CEV/RVO/0001/02122025
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
from pymongo.collection import Collection
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

logger = logging.getLogger(__name__)


class ReferenceNumberService:
    """Service for generating and validating report reference numbers"""
    
    def __init__(self, db_manager):
        """
        Initialize the service with database manager
        
        Args:
            db_manager: Database manager instance with access to collections
        """
        self.db_manager = db_manager
    
    async def get_next_reference_number_preview(self, org_short_name: str) -> Dict[str, Any]:
        """
        Get a preview of the next reference number WITHOUT incrementing the counter
        Used when loading the report form to show what the reference number will be
        
        Args:
            org_short_name: Organization short name (URL-safe identifier)
            
        Returns:
            Dict with reference_number and breakdown of parts
            
        Raises:
            ValueError: If organization not found or missing initials configuration
        """
        try:
            # Get organization from val_app_config.organizations
            config_db = self.db_manager.client.val_app_config
            orgs_collection = config_db.organizations
            
            org = await orgs_collection.find_one({"org_short_name": org_short_name})
            
            if not org:
                raise ValueError(f"Organization '{org_short_name}' not found")
            
            # Get configuration from settings
            settings = org.get("settings", {})
            initials = settings.get("report_reference_initials")
            
            if not initials:
                raise ValueError(f"Organization '{org_short_name}' has not configured report reference initials")
            
            # Get current counter (next sequence will be current + 1)
            current_counter = settings.get("report_sequence_counter", 0)
            next_sequence = current_counter + 1
            
            # Format the reference number
            reference_number = self._format_reference_number(initials, next_sequence)
            
            logger.info(f"📋 Preview reference number for {org_short_name}: {reference_number}")
            
            return {
                "reference_number": reference_number,
                "initials": initials,
                "sequence": next_sequence,
                "formatted_sequence": f"{next_sequence:04d}",
                "date": datetime.now().strftime("%d%m%Y"),
                "preview": True
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting reference number preview: {e}")
            raise
    
    async def generate_reference_number(self, org_short_name: str) -> str:
        """
        Atomically generate next reference number and increment the counter
        This ensures thread-safety and prevents duplicate numbers
        
        Args:
            org_short_name: Organization short name
            
        Returns:
            Formatted reference number (e.g., "CEV/RVO/0001/02122025")
            
        Raises:
            ValueError: If organization not found or missing configuration
        """
        try:
            # Get organization collection
            config_db = self.db_manager.client.val_app_config
            orgs_collection = config_db.organizations
            
            # Atomically increment the counter and get the new value
            # This is thread-safe and prevents race conditions
            result = await orgs_collection.find_one_and_update(
                {"org_short_name": org_short_name},
                {"$inc": {"settings.report_sequence_counter": 1}},
                return_document=ReturnDocument.AFTER
            )
            
            if not result:
                raise ValueError(f"Organization '{org_short_name}' not found")
            
            # Get updated values
            settings = result.get("settings", {})
            initials = settings.get("report_reference_initials")
            
            if not initials:
                # Rollback the increment
                await orgs_collection.update_one(
                    {"org_short_name": org_short_name},
                    {"$inc": {"settings.report_sequence_counter": -1}}
                )
                raise ValueError(f"Organization '{org_short_name}' has not configured report reference initials")
            
            new_counter = settings.get("report_sequence_counter", 1)
            
            # Format the reference number
            reference_number = self._format_reference_number(initials, new_counter)
            
            logger.info(f"✅ Generated reference number for {org_short_name}: {reference_number} (sequence: {new_counter})")
            
            return reference_number
            
        except Exception as e:
            logger.error(f"❌ Error generating reference number: {e}")
            raise
    
    def _format_reference_number(self, initials: str, sequence: int) -> str:
        """
        Format the reference number according to pattern
        
        Args:
            initials: Organization initials (e.g., "CEV/RVO")
            sequence: Sequence number (e.g., 1, 299, 4699)
            
        Returns:
            Formatted reference number (e.g., "CEV/RVO/0001/02122025")
        """
        # Format sequence with 4 digits, zero-padded
        formatted_sequence = f"{sequence:04d}"
        
        # Get current date in DDMMYYYY format
        date_str = datetime.now().strftime("%d%m%Y")
        
        # Combine all parts
        reference_number = f"{initials}/{formatted_sequence}/{date_str}"
        
        return reference_number
    
    async def validate_reference_number_uniqueness(
        self, 
        org_short_name: str, 
        reference_number: str
    ) -> bool:
        """
        Check if a reference number already exists in the database
        
        Args:
            org_short_name: Organization short name
            reference_number: Reference number to validate
            
        Returns:
            True if unique (does not exist), False if duplicate exists
        """
        try:
            # Get the organization's database name
            config_db = self.db_manager.client.val_app_config
            orgs_collection = config_db.organizations
            
            org = await orgs_collection.find_one({"org_short_name": org_short_name})
            if not org:
                raise ValueError(f"Organization '{org_short_name}' not found")
            
            # Check in the organization's reports collection
            org_db_name = org_short_name.replace("-", "_")
            org_db = self.db_manager.client[org_db_name]
            reports_collection = org_db.reports
            
            # Check if reference number exists
            existing = await reports_collection.find_one({"reference_number": reference_number})
            
            is_unique = existing is None
            
            if not is_unique:
                logger.warning(f"⚠️ Duplicate reference number detected: {reference_number}")
            
            return is_unique
            
        except Exception as e:
            logger.error(f"❌ Error validating reference number uniqueness: {e}")
            raise
    
    async def generate_with_retry(
        self, 
        org_short_name: str, 
        max_retries: int = 3
    ) -> str:
        """
        Generate reference number with retry logic for race conditions
        If duplicate is detected, regenerate with incremented counter
        
        Args:
            org_short_name: Organization short name
            max_retries: Maximum number of retry attempts
            
        Returns:
            Unique reference number
            
        Raises:
            ValueError: If unable to generate unique number after max retries
        """
        for attempt in range(max_retries):
            try:
                # Generate reference number (atomically increments counter)
                reference_number = await self.generate_reference_number(org_short_name)
                
                # Validate uniqueness
                is_unique = await self.validate_reference_number_uniqueness(
                    org_short_name, 
                    reference_number
                )
                
                if is_unique:
                    return reference_number
                else:
                    logger.warning(
                        f"⚠️ Reference number {reference_number} already exists, "
                        f"retrying... (attempt {attempt + 1}/{max_retries})"
                    )
                    # Continue to next iteration to generate new number
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    # Last attempt failed
                    raise
                logger.warning(f"⚠️ Attempt {attempt + 1} failed: {e}, retrying...")
                continue
        
        # If we get here, all retries failed
        raise ValueError(
            f"Failed to generate unique reference number for {org_short_name} "
            f"after {max_retries} attempts"
        )
