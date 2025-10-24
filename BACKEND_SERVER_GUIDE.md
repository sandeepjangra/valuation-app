# 🚀 Backend Server & Data Refresh Guide

This guide provides comprehensive instructions for running the backend server and managing data refresh operations in the Valuation Application.

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Available Scripts](#-available-scripts)
- [Step-by-Step Setup](#-step-by-step-setup)
- [Data Collections](#-data-collections)
- [Service URLs](#-service-urls)
- [Troubleshooting](#-troubleshooting)
- [Development Workflow](#-development-workflow)

---

## 🎯 Quick Start

### **Fastest Way to Start Everything**

```bash
cd /Users/sandeepjangra/Downloads/development/ValuationAppV1

# Make scripts executable (one-time setup)
chmod +x ./scripts/manage_app.sh
chmod +x ./scripts/manage_refresh.sh
chmod +x ./restart_backend_with_logs.sh

# Start the complete application
./scripts/manage_app.sh setup
```

### **Quick Backend Restart**

```bash
# Restart backend with detailed logging
./restart_backend_with_logs.sh
```

---

## 📂 Available Scripts

### **1. Main Application Management (`scripts/manage_app.sh`)**

Complete application lifecycle management:

```bash
./scripts/manage_app.sh start     # Start backend server
./scripts/manage_app.sh stop      # Stop backend server  
./scripts/manage_app.sh restart   # Restart backend server
./scripts/manage_app.sh status    # Check server status
./scripts/manage_app.sh logs      # View server logs
./scripts/manage_app.sh health    # Perform health check
./scripts/manage_app.sh install   # Install dependencies
./scripts/manage_app.sh setup     # Complete development setup
./scripts/manage_app.sh help      # Show help
```

**Features:**
- ✅ Automatic dependency installation
- ✅ Service status monitoring
- ✅ Health checks
- ✅ Log management
- ✅ Environment validation

### **2. Backend Restart with Logs (`restart_backend_with_logs.sh`)**

Quick restart with enhanced logging:

```bash
./restart_backend_with_logs.sh
```

**Features:**
- ✅ Kills existing backend processes
- ✅ Creates logs directory
- ✅ Starts server with detailed logging
- ✅ Validates MongoDB configuration
- ✅ Tests server responsiveness

### **3. Data Refresh Management (`scripts/manage_refresh.sh`)**

MongoDB collections refresh operations:

```bash
./scripts/manage_refresh.sh interactive      # Interactive menu
./scripts/manage_refresh.sh refresh-all      # Refresh all collections
./scripts/manage_refresh.sh refresh <name>   # Refresh specific collection
./scripts/manage_refresh.sh status           # Show collections status
./scripts/manage_refresh.sh start-backend    # Start backend server
./scripts/manage_refresh.sh help             # Show help
```

**Available Collections:**
- `common_fields` - Common form fields
- `sbi_land_property_details` - SBI land property details
- `banks` - Bank and branch data
- `users` - User accounts
- `properties` - Property records
- `valuations` - Valuation assessments
- `valuation_reports` - Generated reports
- `audit_logs` - System audit logs

### **4. Python Data Refresh Script (`scripts/refresh_collections.py`)**

Direct Python script for data operations:

```bash
# Interactive mode (recommended)
python scripts/refresh_collections.py

# Command line options
python scripts/refresh_collections.py --all                    # Refresh all collections
python scripts/refresh_collections.py --status                 # Show collections status
python scripts/refresh_collections.py --collection banks       # Refresh specific collection
python scripts/refresh_collections.py --help                   # Show help message
```

**Features:**
- ✅ Interactive menu system
- ✅ Real-time status monitoring
- ✅ Individual collection refresh
- ✅ Comprehensive error handling
- ✅ Detailed logging

### **5. Environment Activation (`activate-dev-env.sh`)**

Development environment setup:

```bash
source ./activate-dev-env.sh
```

**Features:**
- ✅ Activates Python virtual environment
- ✅ Loads environment variables from `.env`
- ✅ Validates Python version
- ✅ Provides development tips

---

## 🔧 Step-by-Step Setup

### **Option A: Automated Complete Setup (Recommended)**

```bash
# 1. Navigate to project directory
cd /Users/sandeepjangra/Downloads/development/ValuationAppV1

# 2. Make scripts executable (one-time)
chmod +x ./scripts/manage_app.sh
chmod +x ./scripts/manage_refresh.sh
chmod +x ./restart_backend_with_logs.sh

# 3. Run complete setup
./scripts/manage_app.sh setup
```

This will:
- ✅ Install all dependencies
- ✅ Start the backend server
- ✅ Validate configuration
- ✅ Run health checks

### **Option B: Manual Step-by-Step Setup**

```bash
# 1. Activate development environment
source ./activate-dev-env.sh

# 2. Install dependencies (if needed)
pip install -r requirements.txt

# 3. Start backend server
./restart_backend_with_logs.sh

# 4. Refresh all data collections
./scripts/manage_refresh.sh refresh-all

# 5. Verify everything is working
./scripts/manage_app.sh status
```

### **Option C: Quick Development Restart**

For daily development when everything is already set up:

```bash
# Quick restart
./restart_backend_with_logs.sh

# Check if data refresh is needed
./scripts/manage_refresh.sh status
```

---

## 📊 Data Collections

### **Available Collections**

| Collection Name | Description | Purpose |
|----------------|-------------|---------|
| `common_fields` | Common form fields | Shared form elements across reports |
| `sbi_land_property_details` | SBI land property details | Bank-specific property templates |
| `banks` | Bank and branch data | Financial institutions and locations |
| `users` | User accounts | Application user management |
| `properties` | Property records | Real estate property information |
| `valuations` | Valuation assessments | Property valuation calculations |
| `valuation_reports` | Generated reports | Completed valuation documents |
| `audit_logs` | System audit logs | Application activity tracking |

### **Collection Refresh Commands**

```bash
# Refresh all collections
./scripts/manage_refresh.sh refresh-all

# Refresh specific collections
./scripts/manage_refresh.sh refresh common_fields
./scripts/manage_refresh.sh refresh banks
./scripts/manage_refresh.sh refresh sbi_land_property_details

# Check collection status
./scripts/manage_refresh.sh status
```

### **Data Flow**

```
MongoDB Atlas → Backend API → Local JSON Files → Frontend Application
```

1. **MongoDB Atlas**: Source of truth for all data
2. **Backend API**: Provides REST endpoints for data access
3. **Local JSON Files**: Cached data for development
4. **Frontend**: Consumes data via API or local files

---

## 🌐 Service URLs

After starting the backend server, these URLs will be available:

| Service | URL | Description |
|---------|-----|-------------|
| **Backend API** | http://localhost:8000 | Main API endpoint |
| **API Documentation** | http://localhost:8000/api/docs | Interactive API docs (Swagger) |
| **Health Check** | http://localhost:8000/api/health | Server health status |
| **Collections Status** | http://localhost:8000/api/admin/collections-status | Data collections info |
| **Admin Panel** | http://localhost:8000/api/admin | Admin operations |

### **API Endpoints**

```bash
# Health check
curl http://localhost:8000/api/health

# Collections status
curl http://localhost:8000/api/admin/collections-status

# Refresh all collections
curl -X POST http://localhost:8000/api/admin/refresh-collections

# Refresh specific collection
curl -X POST http://localhost:8000/api/admin/refresh-collection/banks
```

---

## 🔍 Troubleshooting

### **Common Issues & Solutions**

#### **1. Backend Server Won't Start**

```bash
# Check if port 8000 is occupied
lsof -i :8000

# Kill existing processes
pkill -f "uvicorn.*backend.main"

# Check MongoDB connection
grep MONGODB_URI .env

# Restart with logs
./restart_backend_with_logs.sh
```

#### **2. MongoDB Connection Issues**

```bash
# Verify .env file exists
ls -la .env

# Check MongoDB URI format
cat .env | grep MONGODB_URI

# Test connection
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('MongoDB URI:', os.getenv('MONGODB_URI'))
"
```

#### **3. Data Refresh Failures**

```bash
# Check backend status first
./scripts/manage_app.sh health

# Try refreshing individual collections
./scripts/manage_refresh.sh refresh common_fields

# Check logs
tail -f logs/backend.log
tail -f logs/refresh_collections.log
```

#### **4. Permission Issues**

```bash
# Make scripts executable
chmod +x ./scripts/*.sh
chmod +x ./restart_backend_with_logs.sh
chmod +x ./activate-dev-env.sh

# Check file ownership
ls -la scripts/
```

#### **5. Virtual Environment Issues**

```bash
# Recreate virtual environment
rm -rf valuation_env
python3.11 -m venv valuation_env
source valuation_env/bin/activate
pip install -r requirements.txt
```

### **Log Locations**

| Log File | Location | Purpose |
|----------|----------|---------|
| Backend Server | `logs/backend.log` | Server startup and API logs |
| Data Refresh | `logs/refresh_collections.log` | Collection refresh operations |
| Application | `logs/app.log` | General application logs |

### **Diagnostic Commands**

```bash
# Check all services
./scripts/manage_app.sh health

# View recent logs
tail -f logs/backend.log

# Test API connectivity
curl -f http://localhost:8000/api/health

# Check collections status
python scripts/refresh_collections.py --status
```

---

## 🔄 Development Workflow

### **Daily Development Routine**

```bash
# 1. Start development session
cd /Users/sandeepjangra/Downloads/development/ValuationAppV1
source ./activate-dev-env.sh

# 2. Start backend
./restart_backend_with_logs.sh

# 3. Check data freshness (if needed)
./scripts/manage_refresh.sh status

# 4. Refresh data (if needed)
./scripts/manage_refresh.sh refresh-all

# 5. Start frontend (in another terminal)
cd valuation-frontend
ng serve
```

### **Testing & Validation**

```bash
# Backend health check
./scripts/manage_app.sh health

# API documentation
open http://localhost:8000/api/docs

# Test specific endpoints
curl http://localhost:8000/api/admin/collections-status
```

### **Stopping Services**

```bash
# Stop backend
./scripts/manage_app.sh stop

# Or kill all processes
pkill -f "uvicorn.*backend.main"
pkill -f "ng serve"
```

---

## 📚 Additional Resources

### **Configuration Files**

- `.env` - Environment variables and MongoDB configuration
- `.env.example` - Template for environment setup
- `requirements.txt` - Python dependencies
- `docker-compose.yml` - Container orchestration

### **Key Directories**

- `backend/` - FastAPI application code
- `scripts/` - Management and utility scripts
- `logs/` - Application and service logs
- `backend/data/` - Local JSON data files

### **Related Documentation**

- [SETUP.md](./SETUP.md) - Complete project setup guide
- [MONGODB_ATLAS_SETUP_GUIDE.md](./MONGODB_ATLAS_SETUP_GUIDE.md) - Database setup
- [DEVELOPMENT_READY.md](./DEVELOPMENT_READY.md) - Development environment info

---

## 🤝 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review log files in the `logs/` directory
3. Verify environment configuration in `.env`
4. Test individual components using the diagnostic commands

---

**Last Updated:** October 24, 2025  
**Version:** 1.0  
**Project:** Valuation Application Backend