#!/usr/bin/env python3
"""
Simple FastAPI server launcher for template-versioned reports
"""

import uvicorn
import os
from pathlib import Path

# Ensure we're in the right directory
os.chdir(Path(__file__).parent)

if __name__ == "__main__":
    print("🚀 Starting Template-Versioned Reports API Server")
    print("📍 Server will be available at: http://localhost:8000")
    print("📖 API Documentation at: http://localhost:8000/docs")
    print("🏥 Health check at: http://localhost:8000/health")
    print("📊 Root info at: http://localhost:8000/")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    # Run the server
    uvicorn.run(
        "versioned_reports_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )