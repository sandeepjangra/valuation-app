"""
Template-Versioned Reports API Application
FastAPI application with template versioning support for valuation reports
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
import os
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    # If python-dotenv is not installed, try to read .env manually
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

# Import our API routers
from api.reports_api import router as reports_router
from database.mongodb_manager import MongoDBManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Valuation Reports API with Template Versioning",
    description="""
    Advanced valuation reporting system with template versioning support.
    
    ## Features
    
    * **Template Versioning**: Reports capture template snapshots for backward compatibility
    * **Dynamic Forms**: Form rendering based on versioned template definitions  
    * **Report Workflow**: Draft → Submit → Review → Approve workflow with audit trails
    * **Multi-Bank Support**: SBI, UBI, ICICI and other bank-specific templates
    * **Real-time Calculations**: Formula fields with live updates
    * **Role-based Access**: Organization-level isolation and user permissions
    
    ## Template Versioning
    
    This API implements a sophisticated template versioning system that ensures:
    - **Backward Compatibility**: Old reports continue to work even when templates evolve
    - **Content Deduplication**: Identical templates share storage via SHA256 hashing
    - **Change Tracking**: Full audit trail of template modifications
    - **Semantic Versioning**: Clear version management (1.0.0, 1.1.0, etc.)
    
    ## SBI Land Template Support
    
    Currently supports comprehensive SBI Land property templates with:
    - **Property Details**: 42 fields across 7 sections
    - **Site Characteristics**: Locality, features, utilities assessment  
    - **Valuation Details**: Land valuation with building assessment
    - **Construction Specs**: Material and structural specifications
    - **Dynamic Tables**: Boundary dimensions, floor-wise details
    - **Formula Fields**: Automatic calculations (Area × Rate = Value)
    """,
    version="1.0.0",
    contact={
        "name": "Valuation System API",
        "email": "support@valuationsystem.com",
    },
    license_info={
        "name": "Private License",
    }
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",  # Angular development
        "http://localhost:3000",  # Alternative frontend port
        "https://valuationapp.com",  # Production domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(reports_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers
    
    Returns system status, database connectivity, and template versioning status
    """
    try:
        # Test database connection
        db_manager = MongoDBManager()
        await db_manager.connect()
        
        if not db_manager.is_connected:
            raise Exception("Database connection failed")
        
        # Get system statistics
        health_info = await db_manager.health_check()
        
        # Get template versioning statistics
        template_count = await db_manager.database.template_versions.count_documents({})
        snapshot_count = await db_manager.database.template_snapshots.count_documents({})
        report_count = await db_manager.database.valuation_reports.count_documents({})
        
        await db_manager.disconnect()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "database": health_info,
            "template_versioning": {
                "template_versions": template_count,
                "template_snapshots": snapshot_count,
                "total_reports": report_count,
                "status": "operational" if template_count > 0 else "no_templates"
            },
            "features": {
                "template_versioning": True,
                "dynamic_forms": True,
                "real_time_calculations": True,
                "multi_bank_support": True,
                "role_based_access": True
            }
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
                "database": "connection_failed"
            }
        )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception in {request.url}: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    logger.info("🚀 Starting Template-Versioned Reports API")
    logger.info("📋 Template versioning system: ENABLED")
    logger.info("🏗️  SBI Land templates: READY")
    logger.info("🔄 Dynamic form rendering: READY")
    logger.info("⚡ Real-time calculations: READY")
    
    try:
        # Verify database connection
        db_manager = MongoDBManager()
        await db_manager.connect()
        
        # Verify template versioning collections exist
        collections = await db_manager.database.list_collection_names()
        required_collections = ["template_versions", "template_snapshots", "valuation_reports"]
        
        missing_collections = [col for col in required_collections if col not in collections]
        
        if missing_collections:
            logger.warning(f"⚠️  Missing collections: {missing_collections}")
            logger.warning("Run template_versioning_setup.py to initialize the system")
        else:
            # Get template statistics
            template_count = await db_manager.database.template_versions.count_documents({})
            snapshot_count = await db_manager.database.template_snapshots.count_documents({})
            
            logger.info(f"📊 Template versions available: {template_count}")
            logger.info(f"📸 Template snapshots: {snapshot_count}")
        
        await db_manager.disconnect()
        logger.info("✅ Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        logger.error("Application may not function correctly")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    logger.info("🔒 Shutting down Template-Versioned Reports API")
    logger.info("👋 Goodbye!")

# Root endpoint with API information
@app.get("/")
async def root():
    """
    API root endpoint with system information
    """
    return {
        "message": "Valuation Reports API with Template Versioning",
        "version": "1.0.0",
        "status": "operational",
        "features": {
            "template_versioning": "Advanced template evolution support with backward compatibility",
            "sbi_land_support": "Comprehensive SBI Land property templates (42+ fields)",
            "dynamic_forms": "Form rendering based on versioned template definitions",
            "real_time_calculations": "Formula fields with automatic updates",
            "multi_bank_support": "Extensible to multiple bank template systems",
            "report_workflow": "Draft → Submit → Review → Approve with audit trails"
        },
        "endpoints": {
            "health": "/health",
            "reports": {
                "create": "POST /api/v1/reports",
                "get": "GET /api/v1/reports/{id}",
                "update": "PUT /api/v1/reports/{id}",
                "submit": "POST /api/v1/reports/{id}/submit",
                "list": "GET /api/v1/reports"
            },
            "templates": {
                "snapshot": "GET /api/v1/templates/snapshot/{id}",
                "versions": "GET /api/v1/templates/versions"
            },
            "docs": "/docs"
        },
        "documentation": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "versioned_reports_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )