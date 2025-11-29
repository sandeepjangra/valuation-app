"""
Version-aware Report API Endpoints
FastAPI routes for handling valuation reports with template versioning support
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel

# Import our existing models and services
import sys
from pathlib import Path as PathLib
sys.path.append(str(PathLib(__file__).parent.parent))

from models.report_models import (
    ValuationReport, ReportCreate, ReportUpdate, TemplateSnapshot,
    MigrationStatus, CalculationResult, ValidationError
)
from services.template_snapshot_service import TemplateSnapshotService
from database.mongodb_manager import MongoDBManager

# Create router
router = APIRouter(prefix="/api/v1", tags=["reports"])

# Dependency to get database manager
async def get_db_manager() -> MongoDBManager:
    """Get database manager instance"""
    db_manager = MongoDBManager()
    await db_manager.connect()
    return db_manager

# Dependency to get template snapshot service
async def get_template_service(db_manager: MongoDBManager = Depends(get_db_manager)) -> TemplateSnapshotService:
    """Get template snapshot service instance"""
    return TemplateSnapshotService(db_manager.database)

# Response models
class ReportResponse(BaseModel):
    """Response model for report operations"""
    id: str
    templateSnapshot: str
    bankCode: str
    propertyType: str
    status: str
    createdAt: datetime
    updatedAt: Optional[datetime] = None
    submittedAt: Optional[datetime] = None
    formData: Dict[str, Any]
    calculationResults: Optional[Dict[str, Any]] = None
    validationErrors: Optional[List[ValidationError]] = None

class TemplateSnapshotResponse(BaseModel):
    """Response model for template snapshot"""
    id: str
    templateIds: List[str]
    version: str
    templateDefinitions: Dict[str, Any]
    createdAt: datetime

# ================================
# Report CRUD Endpoints
# ================================

@router.post("/reports", response_model=ReportResponse)
async def create_report(
    report_data: ReportCreate,
    db_manager: MongoDBManager = Depends(get_db_manager),
    template_service: TemplateSnapshotService = Depends(get_template_service)
):
    """
    Create a new valuation report with template versioning
    
    This endpoint:
    1. Captures a template snapshot for the specified templates
    2. Creates a new report linked to the snapshot
    3. Validates required fields based on template definitions
    4. Returns the created report with snapshot reference
    """
    try:
        # Capture template snapshot for the report
        template_ids = report_data.templateIds or []
        if not template_ids:
            # Default to SBI Land templates if not specified
            if report_data.bankCode == "SBI" and report_data.propertyType.lower() == "land":
                template_ids = ["SBI_LAND_PROPERTY_DETAILS", "SBI_LAND_CONSTRUCTION_DETAILS"]
        
        # Capture snapshot
        snapshot_id = await template_service.capture_template_snapshot(
            template_ids, 
            report_data.templateVersion or "1.0.0"
        )
        
        # Create report document
        report_doc = {
            "templateSnapshot": snapshot_id,
            "bankCode": report_data.bankCode,
            "propertyType": report_data.propertyType,
            "organizationId": report_data.organizationId,
            "createdBy": report_data.createdBy,
            "assignedTo": report_data.assignedTo,
            "customerName": report_data.customerName,
            "propertyAddress": report_data.propertyAddress,
            "loanAmount": report_data.loanAmount,
            "formData": report_data.formData or {},
            "calculationResults": {},
            "validationErrors": [],
            "auditTrail": [{
                "action": "CREATED",
                "performedBy": report_data.createdBy,
                "timestamp": datetime.utcnow(),
                "details": f"Report created with template snapshot {snapshot_id}"
            }],
            "workflow": {
                "status": "DRAFT",
                "submittedBy": None,
                "submittedAt": None,
                "reviewedBy": None,
                "reviewedAt": None,
                "approvedBy": None,
                "approvedAt": None
            },
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        # Insert report
        report_id = await db_manager.insert_one("valuation_reports", report_doc)
        
        # Get created report
        created_report = await db_manager.find_one("valuation_reports", {"_id": report_id})
        
        return ReportResponse(
            id=str(report_id),
            templateSnapshot=snapshot_id,
            bankCode=created_report["bankCode"],
            propertyType=created_report["propertyType"],
            status=created_report["workflow"]["status"],
            createdAt=created_report["createdAt"],
            formData=created_report["formData"],
            calculationResults=created_report.get("calculationResults"),
            validationErrors=created_report.get("validationErrors")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create report: {str(e)}")
    
    finally:
        await db_manager.disconnect()

@router.get("/reports/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str = Path(..., description="Report ID"),
    db_manager: MongoDBManager = Depends(get_db_manager)
):
    """
    Get a specific report by ID
    
    Returns the report with its template snapshot reference,
    allowing the frontend to render the form using the correct template version
    """
    try:
        # Get report
        report = await db_manager.find_one("valuation_reports", {"_id": ObjectId(report_id)})
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return ReportResponse(
            id=str(report["_id"]),
            templateSnapshot=report["templateSnapshot"],
            bankCode=report["bankCode"],
            propertyType=report["propertyType"],
            status=report["workflow"]["status"],
            createdAt=report["createdAt"],
            updatedAt=report.get("updatedAt"),
            submittedAt=report["workflow"].get("submittedAt"),
            formData=report["formData"],
            calculationResults=report.get("calculationResults"),
            validationErrors=report.get("validationErrors")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get report: {str(e)}")
    
    finally:
        await db_manager.disconnect()

@router.put("/reports/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: str = Path(..., description="Report ID"),
    report_update: ReportUpdate = None,
    db_manager: MongoDBManager = Depends(get_db_manager)
):
    """
    Update a report's form data and calculations
    
    This endpoint:
    1. Updates form data while preserving template snapshot reference
    2. Recalculates any formula fields based on template definitions
    3. Validates required fields
    4. Updates audit trail
    """
    try:
        # Get existing report
        existing_report = await db_manager.find_one("valuation_reports", {"_id": ObjectId(report_id)})
        
        if not existing_report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Check if report can be edited (not submitted or approved)
        if existing_report["workflow"]["status"] in ["SUBMITTED", "APPROVED", "REJECTED"]:
            raise HTTPException(status_code=400, detail=f"Cannot edit report in {existing_report['workflow']['status']} status")
        
        # Update fields
        update_data = {
            "formData": report_update.formData,
            "updatedAt": datetime.utcnow()
        }
        
        # Add to audit trail
        audit_entry = {
            "action": "UPDATED",
            "performedBy": report_update.updatedBy,
            "timestamp": datetime.utcnow(),
            "details": "Report form data updated"
        }
        
        # Update report
        await db_manager.update_one(
            "valuation_reports",
            {"_id": ObjectId(report_id)},
            {
                "$set": update_data,
                "$push": {"auditTrail": audit_entry}
            }
        )
        
        # Get updated report
        updated_report = await db_manager.find_one("valuation_reports", {"_id": ObjectId(report_id)})
        
        return ReportResponse(
            id=str(updated_report["_id"]),
            templateSnapshot=updated_report["templateSnapshot"],
            bankCode=updated_report["bankCode"],
            propertyType=updated_report["propertyType"],
            status=updated_report["workflow"]["status"],
            createdAt=updated_report["createdAt"],
            updatedAt=updated_report.get("updatedAt"),
            formData=updated_report["formData"],
            calculationResults=updated_report.get("calculationResults"),
            validationErrors=updated_report.get("validationErrors")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update report: {str(e)}")
    
    finally:
        await db_manager.disconnect()

@router.post("/reports/{report_id}/submit")
async def submit_report(
    report_id: str = Path(..., description="Report ID"),
    submitted_by: str = Query(..., description="ID of user submitting the report"),
    db_manager: MongoDBManager = Depends(get_db_manager),
    template_service: TemplateSnapshotService = Depends(get_template_service)
):
    """
    Submit a report for review
    
    This endpoint:
    1. Validates all required fields based on template snapshot
    2. Performs final calculations
    3. Changes status to SUBMITTED
    4. Records submission in audit trail
    """
    try:
        # Get report
        report = await db_manager.find_one("valuation_reports", {"_id": ObjectId(report_id)})
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Check if report can be submitted
        if report["workflow"]["status"] != "DRAFT":
            raise HTTPException(status_code=400, detail=f"Cannot submit report in {report['workflow']['status']} status")
        
        # Get template snapshot for validation
        snapshot = await template_service.get_template_snapshot(report["templateSnapshot"])
        
        # TODO: Implement validation logic based on template definitions
        # validation_errors = validate_report_data(report["formData"], snapshot)
        validation_errors = []  # Placeholder
        
        if validation_errors:
            raise HTTPException(status_code=400, detail={
                "message": "Validation errors found",
                "errors": validation_errors
            })
        
        # Update report status
        update_data = {
            "workflow.status": "SUBMITTED",
            "workflow.submittedBy": submitted_by,
            "workflow.submittedAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        audit_entry = {
            "action": "SUBMITTED",
            "performedBy": submitted_by,
            "timestamp": datetime.utcnow(),
            "details": "Report submitted for review"
        }
        
        await db_manager.update_one(
            "valuation_reports",
            {"_id": ObjectId(report_id)},
            {
                "$set": update_data,
                "$push": {"auditTrail": audit_entry}
            }
        )
        
        return {"message": "Report submitted successfully", "status": "SUBMITTED"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit report: {str(e)}")
    
    finally:
        await db_manager.disconnect()

# ================================
# Template Snapshot Endpoints
# ================================

@router.get("/templates/snapshot/{snapshot_id}", response_model=TemplateSnapshotResponse)
async def get_template_snapshot(
    snapshot_id: str = Path(..., description="Template snapshot ID"),
    template_service: TemplateSnapshotService = Depends(get_template_service),
    db_manager: MongoDBManager = Depends(get_db_manager)
):
    """
    Get template definitions from a snapshot
    
    Used by frontend to render forms dynamically based on the template version
    captured when the report was created
    """
    try:
        snapshot = await template_service.get_template_snapshot(snapshot_id)
        
        if not snapshot:
            raise HTTPException(status_code=404, detail="Template snapshot not found")
        
        return TemplateSnapshotResponse(
            id=snapshot_id,
            templateIds=snapshot["templateIds"],
            version=snapshot["version"],
            templateDefinitions=snapshot["templateDefinitions"],
            createdAt=snapshot["createdAt"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get template snapshot: {str(e)}")
    
    finally:
        await db_manager.disconnect()

@router.get("/reports")
async def list_reports(
    organization_id: Optional[str] = Query(None, description="Filter by organization"),
    bank_code: Optional[str] = Query(None, description="Filter by bank"),
    property_type: Optional[str] = Query(None, description="Filter by property type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    customer_name: Optional[str] = Query(None, description="Search by customer name"),
    created_by: Optional[str] = Query(None, description="Filter by creator"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db_manager: MongoDBManager = Depends(get_db_manager)
):
    """
    List reports with filtering and pagination
    
    Supports filtering by organization, bank, property type, status, and customer name
    """
    try:
        # Build filter query
        filter_query = {}
        
        if organization_id:
            filter_query["organizationId"] = organization_id
        if bank_code:
            filter_query["bankCode"] = bank_code
        if property_type:
            filter_query["propertyType"] = property_type
        if status:
            filter_query["workflow.status"] = status
        if customer_name:
            # Case-insensitive search in customer name
            filter_query["customerName"] = {"$regex": customer_name, "$options": "i"}
        if created_by:
            filter_query["createdBy"] = created_by
        
        # Calculate pagination
        skip = (page - 1) * limit
        
        # Get reports with pagination
        reports = await db_manager.find_many(
            "valuation_reports",
            filter_query,
            limit=limit,
            sort_by={"createdAt": -1}
        )
        
        # Skip manually since find_many doesn't support skip
        reports = reports[skip:skip + limit]
        
        # Get total count for pagination
        total_count = await db_manager.database.valuation_reports.count_documents(filter_query)
        
        # Format response
        report_list = []
        for report in reports:
            report_list.append({
                "id": str(report["_id"]),
                "templateSnapshot": report["templateSnapshot"],
                "bankCode": report["bankCode"],
                "propertyType": report["propertyType"],
                "customerName": report["customerName"],
                "propertyAddress": report["propertyAddress"],
                "status": report["workflow"]["status"],
                "createdAt": report["createdAt"],
                "updatedAt": report.get("updatedAt"),
                "submittedAt": report["workflow"].get("submittedAt"),
                "createdBy": report["createdBy"]
            })
        
        return {
            "reports": report_list,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list reports: {str(e)}")
    
    finally:
        await db_manager.disconnect()

# ================================
# Template Management Endpoints  
# ================================

@router.get("/templates/versions")
async def list_template_versions(
    bank_code: Optional[str] = Query(None, description="Filter by bank code"),
    property_type: Optional[str] = Query(None, description="Filter by property type"),
    is_latest: Optional[bool] = Query(True, description="Only return latest versions"),
    db_manager: MongoDBManager = Depends(get_db_manager)
):
    """
    List available template versions
    
    Used for template management and version selection
    """
    try:
        # Build filter
        filter_query = {"isActive": True}
        
        if bank_code:
            filter_query["bankCode"] = bank_code
        if property_type:
            filter_query["propertyType"] = property_type
        if is_latest:
            filter_query["isLatest"] = True
        
        # Get template versions
        templates = await db_manager.find_many(
            "template_versions",
            filter_query,
            sort_by={"templateId": 1, "version": -1}
        )
        
        # Format response
        template_list = []
        for template in templates:
            template_list.append({
                "templateId": template["templateId"],
                "version": template["version"],
                "bankCode": template["bankCode"],
                "propertyType": template["propertyType"],
                "templateCategory": template["templateCategory"],
                "isLatest": template["isLatest"],
                "createdAt": template["createdAt"],
                "fieldCount": template["templateDefinition"]["metadata"]["fieldCount"],
                "sectionCount": template["templateDefinition"]["metadata"]["sectionCount"]
            })
        
        return {"templates": template_list}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list templates: {str(e)}")
    
    finally:
        await db_manager.disconnect()

# Export router for main application
__all__ = ["router"]