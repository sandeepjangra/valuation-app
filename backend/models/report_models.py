"""
Enhanced Report Models with Template Versioning Support
"""

from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from bson import ObjectId

class TemplateSnapshot(BaseModel):
    """Template snapshot information stored with each report"""
    template_ids: List[str] = Field(..., description="List of template IDs used in this report")
    version: str = Field(..., description="Template version when report was created")
    snapshot_id: Optional[str] = Field(None, description="Reference to template snapshot")
    captured_at: Optional[datetime] = Field(None, description="When template snapshot was captured")

class MigrationStatus(BaseModel):
    """Migration status for template version upgrades"""
    current_template_version: str = Field(..., description="Latest available template version")
    is_upgrade_available: bool = Field(False, description="Whether newer template version exists")
    can_auto_migrate: bool = Field(True, description="Whether migration can be done automatically")
    conflicting_fields: List[str] = Field(default=[], description="Fields that need manual review")
    last_migration_check: Optional[datetime] = Field(None, description="Last time migration was checked")

class CustomerInfo(BaseModel):
    """Customer information for the report"""
    customer_name: str = Field(..., description="Name of the customer")
    application_id: Optional[str] = Field(None, description="Bank application ID")
    branch_code: str = Field(..., description="Bank branch code")
    branch_name: str = Field(..., description="Bank branch name")
    contact_number: Optional[str] = Field(None, description="Customer contact number")

class AuditTrailEntry(BaseModel):
    """Single audit trail entry"""
    action: str = Field(..., description="Action performed (created, updated, submitted, etc.)")
    user_id: str = Field(..., description="User who performed the action")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    changes: Dict[str, Any] = Field(default={}, description="Details of changes made")
    ip_address: Optional[str] = Field(None, description="IP address of the user")

class ReportCreate(BaseModel):
    """Request model for creating a new report"""
    bank_code: str = Field(..., description="Bank code (SBI, UBI, etc.)")
    property_type: str = Field(..., description="Property type (Land, Apartment)")
    customer_info: CustomerInfo
    report_data: Dict[str, Any] = Field(default={}, description="Initial report data")
    organization_id: str = Field(..., description="Organization ID for multi-tenant support")

class ReportUpdate(BaseModel):
    """Request model for updating an existing report"""
    report_data: Dict[str, Any] = Field(..., description="Updated report data")
    calculated_fields: Optional[Dict[str, float]] = Field(default={}, description="Calculated field values")
    completion_percentage: Optional[float] = Field(None, description="Form completion percentage")

class ValuationReport(BaseModel):
    """Complete valuation report model with versioning"""
    report_id: str = Field(..., description="Unique report identifier")
    organization_id: str = Field(..., description="Organization ID")
    
    # Template versioning information
    template_snapshot: TemplateSnapshot
    migration_status: MigrationStatus
    
    # Report data
    report_data: Dict[str, Any] = Field(default={}, description="Multi-document report data")
    calculated_fields: Dict[str, float] = Field(default={}, description="Calculated values")
    completion_percentage: float = Field(default=0.0, description="Form completion percentage")
    
    # Customer and metadata
    customer_info: CustomerInfo
    status: str = Field(default="draft", description="Report status: draft, submitted, approved, rejected")
    
    # Workflow
    created_by: str = Field(..., description="User who created the report")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    submitted_by: Optional[str] = Field(None, description="User who submitted the report")
    submitted_at: Optional[datetime] = Field(None, description="When report was submitted")
    
    # Audit trail
    audit_trail: List[AuditTrailEntry] = Field(default=[], description="Complete audit history")
    
    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat()
        }

class ReportListItem(BaseModel):
    """Lightweight model for report listing"""
    report_id: str
    customer_name: str
    bank_code: str
    property_type: str
    branch_name: str
    status: str
    template_version: str
    is_upgrade_available: bool
    completion_percentage: float
    created_at: datetime
    updated_at: datetime

class TemplateVersion(BaseModel):
    """Template version model"""
    template_id: str = Field(..., description="Base template identifier")
    version: str = Field(..., description="Semantic version (1.0.0)")
    bank_code: str = Field(..., description="Bank identifier")
    property_type: str = Field(..., description="Property type")
    template_category: str = Field(..., description="Template category")
    is_active: bool = Field(True, description="Whether version is active")
    is_latest: bool = Field(False, description="Whether this is latest version")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    deprecated_at: Optional[datetime] = Field(None, description="When version was deprecated")
    template_definition: Dict[str, Any] = Field(..., description="Complete template structure")
    version_changes: Dict[str, Any] = Field(default={}, description="Changes from previous version")

class MigrationPlan(BaseModel):
    """Template migration plan"""
    template_id: str
    from_version: str
    to_version: str
    fields_added: List[str] = Field(default=[], description="Fields added in new version")
    fields_removed: List[str] = Field(default=[], description="Fields removed in new version")
    fields_modified: List[Dict[str, Any]] = Field(default=[], description="Fields modified between versions")
    has_breaking_changes: bool = Field(False, description="Whether migration has breaking changes")
    can_auto_migrate: bool = Field(True, description="Whether migration can be automated")
    estimated_data_loss: bool = Field(False, description="Whether migration may lose data")
    migration_steps: List[str] = Field(default=[], description="Steps required for migration")

class CalculationResult(BaseModel):
    """Result of field calculation"""
    field_id: str
    calculated_value: float
    formula: str
    dependencies: List[str]
    calculation_steps: Optional[List[Dict[str, Any]]] = Field(default=None)

class ValidationError(BaseModel):
    """Field validation error"""
    field_id: str
    error_type: str
    error_message: str
    current_value: Any
    
class FormValidationResult(BaseModel):
    """Complete form validation result"""
    is_valid: bool
    errors: List[ValidationError] = Field(default=[])
    warnings: List[ValidationError] = Field(default=[])
    completion_percentage: float
    required_fields_missing: List[str] = Field(default=[])

# Utility functions for model conversion
def report_to_dict(report: ValuationReport) -> Dict[str, Any]:
    """Convert report model to MongoDB document"""
    return report.dict(by_alias=True, exclude_none=False)

def dict_to_report(doc: Dict[str, Any]) -> ValuationReport:
    """Convert MongoDB document to report model"""
    # Handle ObjectId conversion
    if "_id" in doc:
        doc.pop("_id")
    
    # Ensure all required fields have defaults
    if "template_snapshot" not in doc:
        doc["template_snapshot"] = {
            "template_ids": [],
            "version": "1.0.0",
            "snapshot_id": None,
            "captured_at": None
        }
    
    if "migration_status" not in doc:
        doc["migration_status"] = {
            "current_template_version": "1.0.0",
            "is_upgrade_available": False,
            "can_auto_migrate": True,
            "conflicting_fields": []
        }
    
    return ValuationReport(**doc)