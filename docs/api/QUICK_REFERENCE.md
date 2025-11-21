# 🚀 Quick Reference - Backend & Data Management

Quick commands for daily development with the Valuation Application backend.

## ⚡ Quick Start Commands

```bash
# Complete setup (first time)
./scripts/server/manage_app.sh setup

# Daily development start
./scripts/server/restart_backend_with_logs.sh

# Interactive data refresh
./scripts/database/manage_refresh.sh interactive
```

## 🎯 Most Used Commands

| Action | Command | Description |
|--------|---------|-------------|
| **Start Backend** | `./scripts/server/restart_backend_with_logs.sh` | Quick backend restart with logs |
| **Stop Backend** | `./scripts/server/manage_app.sh stop` | Stop backend server |
| **Check Status** | `./scripts/server/manage_app.sh status` | Server and health status |
| **Refresh All Data** | `./scripts/database/manage_refresh.sh refresh-all` | Update all collections |
| **Data Status** | `./scripts/database/manage_refresh.sh status` | Check data freshness |
| **View Logs** | `tail -f logs/backend.log` | Monitor server logs |

## 🔧 Service URLs

- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/api/docs
- **Health Check:** http://localhost:8000/api/health

## 📊 Data Collections

- `common_fields` - Form fields
- `banks` - Bank data
- `sbi_land_property_details` - Property templates
- `users` - User accounts
- `properties` - Property records
- `valuations` - Assessments
- `valuation_reports` - Reports
- `audit_logs` - Activity logs

## 🚨 Troubleshooting

```bash
# Backend not starting?
lsof -i :8000                     # Check port usage
pkill -f "uvicorn.*backend.main"  # Kill processes

# Data refresh failing?
./scripts/server/manage_app.sh health     # Check backend health
curl http://localhost:8000/api/health  # Test API

# Permission issues?
chmod +x scripts/**/*.sh            # Fix script permissions
```

## 📁 Important Files

- `BACKEND_SERVER_GUIDE.md` - Complete documentation
- `logs/backend.log` - Server logs
- `.env` - Configuration
- `requirements.txt` - Dependencies

---

**For detailed documentation, see:** [BACKEND_SERVER_GUIDE.md](./BACKEND_SERVER_GUIDE.md)