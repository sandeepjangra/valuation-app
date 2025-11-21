# Project Cleanup and Organization Plan

## Current State Analysis

### Root Directory Issues:
- 100+ files in root directory
- Mix of Python scripts, shell scripts, test files, documentation
- Duplicate/similar scripts (e.g., multiple bank creation scripts)
- Test HTML files scattered
- Log files not organized
- No clear separation between production and development scripts

---

## Proposed New Structure

```
ValuationAppV1/
├── docs/                          # All documentation
│   ├── setup/                     # Setup guides
│   ├── architecture/              # Architecture docs
│   ├── api/                       # API documentation
│   └── testing/                   # Testing guides
│
├── scripts/                       # Production scripts (KEEP)
│   ├── deployment/                # Deployment related
│   ├── database/                  # DB setup and migration
│   ├── server/                    # Server management
│   └── utils/                     # Utility scripts
│
├── dev-tools/                     # Development tools (NEW)
│   ├── test-scripts/              # Test Python scripts
│   ├── test-pages/                # Test HTML pages
│   ├── debug/                     # Debug scripts
│   └── data-samples/              # Sample data files
│
├── logs/                          # All log files (KEEP)
│
├── backend/                       # Backend app (KEEP)
├── valuation-frontend/            # Frontend app (KEEP)
├── valuation_env/                 # Python venv (KEEP)
│
├── .env, .env.example             # Environment files (KEEP)
├── requirements.txt               # Python deps (KEEP)
├── package.json                   # Node deps (KEEP)
├── docker-compose.yml             # Docker config (KEEP)
├── README.md                      # Main readme (KEEP)
└── todo.md                        # Todo list (KEEP)
```

---

## Script Classification

### 1. PRODUCTION SCRIPTS (Keep in scripts/)

#### Deployment Scripts:
- `deploy-amplify.sh`
- `setup-github-deployment.sh`
- `activate-dev-env.sh`

#### Server Management Scripts:
- `scripts/server/manage_server.sh`
- `scripts/manage_app.sh`
- `scripts/manage_containers.sh`
- `scripts/manage_docker.sh`
- `scripts/server/start-servers.sh`
- `scripts/server/stop-servers.sh`
- `restart_backend_with_logs.sh`

#### Database Setup Scripts:
- `scripts/database/setup_mongodb_atlas.py`
- `scripts/create_mongodb_collections.py`
- `scripts/migrate_databases.py`
- `scripts/setup_banks_collection.py`
- `scripts/setup_common_fields_collection.py`

#### Database Maintenance:
- `scripts/database/refresh_collections.py`
- `scripts/cleanup_collections.py`

---

### 2. DEVELOPMENT/TEST SCRIPTS (Move to dev-tools/)

#### Test Scripts:
- `test_*.py` (all test files)
- `check_*.py` (all check files)
- `debug_*.py` (all debug files)
- `pymongo_test.py`
- `simple_connection_test.py`

#### Test HTML Pages:
- `test_*.html` (all test HTML)
- `debug_*.html` (all debug HTML)

#### Data Samples:
- `*.json` sample files
- `sample_template/` directory

#### One-time Fix Scripts (Archive):
- `fix_*.py`
- `create_*.py` (one-time creation scripts)
- `recreate_*.py`
- `update_*.py`
- `clean_*.py`
- `consolidate_*.py`
- `upload_*.py`

---

### 3. DOCUMENTATION (Move to docs/)

#### Setup Documentation:
- `SETUP.md`
- `SETUP_COMPLETE.md`
- `MONGODB_ATLAS_SETUP_GUIDE.md`
- `INTERACTIVE_ATLAS_SETUP.md`
- `AMPLIFY_SETUP.md`
- `CONTAINER_SETUP_STATUS.md`
- `DEVELOPMENT_READY.md`

#### Architecture Documentation:
- `MONGODB_SCHEMA_DESIGN.md`
- `BANKS_COLLECTION_SCHEMA.md`
- `COMMON_FIELDS_SCHEMA.md`
- `MULTI_TENANT_ARCHITECTURE_ANALYSIS.md`
- `MULTI_TENANT_IMPLEMENTATION_COMPLETE.md`

#### API Documentation:
- `BACKEND_SERVER_GUIDE.md`
- `MANAGEMENT_COMMANDS.md`
- `QUICK_REFERENCE.md`
- `ORGANIZATION_QUICK_REFERENCE.md`

#### Testing Documentation:
- `SYSTEM_ADMIN_TESTING_GUIDE.md`

#### Implementation Summaries:
- All `*_COMPLETE.md` files
- `FIXES_SUMMARY.md`
- `ANALYSIS_COMPLETION_SUMMARY.md`

---

### 4. LOG FILES (Move to logs/)

- `*.log` (all log files)
- `backend_logs*.txt`
- `.server.pid`

---

### 5. DELETE/ARCHIVE

#### Duplicate/Obsolete:
- Multiple bank creation scripts (consolidate)
- Old migration logs
- Temporary test files

---

## Implementation Steps

1. Create new folder structure
2. Move documentation files
3. Organize scripts by category
4. Move test files to dev-tools
5. Clean up log files
6. Update any hardcoded paths in scripts
7. Create README in each folder explaining contents
8. Archive obsolete files

---

## Benefits

✅ **Clear Organization** - Easy to find what you need
✅ **Separation of Concerns** - Production vs Development vs Tests
✅ **Maintainability** - Logical grouping
✅ **Onboarding** - New developers can understand structure
✅ **Clean Root** - Only essential config files in root
✅ **Reusability** - Clear locations for reusable scripts
