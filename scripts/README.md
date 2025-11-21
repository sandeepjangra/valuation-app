# Production Scripts

This directory contains production-ready scripts for deployment, database management, and server operations.

## Directory Structure

### `/deployment`
Deployment and environment setup scripts:
- `deploy-amplify.sh` - Deploy to AWS Amplify
- `setup-github-deployment.sh` - Configure GitHub Actions deployment
- `activate-dev-env.sh` - Activate development environment
- `verify-tech-stack.sh` - Verify technology stack installation

**Usage:** Run before deployment or when setting up new environments.

### `/database`
Database setup and maintenance scripts (from main scripts/ folder):
- `setup_mongodb_atlas.py` - Initial MongoDB Atlas setup
- `create_mongodb_collections.py` - Create required collections
- `migrate_databases.py` - Database migration scripts
- `setup_banks_collection.py` - Setup banks collection
- `setup_common_fields_collection.py` - Setup common fields
- `refresh_collections.py` - Refresh collection data
- `cleanup_collections.py` - Clean up unused collections

**Usage:** Run during initial setup or when database schema changes.

### `/server`
Server management scripts:
- `start-servers.sh` - Start backend and frontend servers
- `stop-servers.sh` - Stop all running servers
- `restart_backend_with_logs.sh` - Restart backend with logging
- `manage_server.sh` - Server management utility
- `manage_app.sh` - Application management utility
- `manage_containers.sh` - Container management (Docker/Podman)
- `manage_docker.sh` - Docker-specific management

**Usage:** Use for daily server operations.

### `/utils`
Utility scripts for various tasks:
- API testing utilities
- Data processing scripts
- Helper functions

## Best Practices

1. **Always backup** before running database scripts
2. **Test in development** before running in production
3. **Check logs** after running scripts
4. **Read script comments** to understand what they do
5. **Use version control** - commit before major changes

## Quick Commands

```bash
# Start servers
./scripts/server/start-servers.sh

# Stop servers  
./scripts/server/stop-servers.sh

# Setup MongoDB
python scripts/database/setup_mongodb_atlas.py

# Refresh collections
python scripts/database/refresh_collections.py
```
