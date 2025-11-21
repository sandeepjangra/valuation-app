# Server Management Scripts

Scripts for starting, stopping, and managing backend and frontend servers.

## Core Server Scripts

### `start-servers.sh`
Starts both backend (FastAPI) and frontend (Angular) servers.

**What it does:**
- Starts backend on port 8000
- Starts frontend on port 4200
- Runs in background with logging

**Usage:**
```bash
./scripts/server/start-servers.sh
```

**Logs:**
- Backend: `logs/backend_logs.txt`
- Frontend: Check terminal output

### `stop-servers.sh`
Stops all running servers.

**What it does:**
- Kills backend process (port 8000)
- Kills frontend process (port 4200)
- Cleans up PIDs

**Usage:**
```bash
./scripts/server/stop-servers.sh
```

### `restart_backend_with_logs.sh`
Restarts the backend server with enhanced logging.

**Use cases:**
- After code changes
- When debugging issues
- To see detailed logs

**Usage:**
```bash
./scripts/server/restart_backend_with_logs.sh
```

**Logs written to:** `logs/backend_logs.txt`

## Management Utilities

### `manage_server.sh`
Interactive server management utility.

**Features:**
- Start/stop servers
- Check server status
- View logs
- Restart with options

**Usage:**
```bash
./scripts/server/manage_server.sh
```

### `manage_app.sh`
Application lifecycle management.

**Features:**
- Full application control
- Database connection checks
- Environment validation
- Health checks

**Usage:**
```bash
./scripts/server/manage_app.sh [start|stop|restart|status]
```

### `manage_containers.sh`
Container management for Docker/Podman deployments.

**Features:**
- Start/stop containers
- View container status
- Container logs
- Rebuild containers

**Usage:**
```bash
./scripts/server/manage_containers.sh [start|stop|restart|logs]
```

### `manage_docker.sh`
Docker-specific management operations.

**Usage:**
```bash
./scripts/server/manage_docker.sh [up|down|build|logs]
```

## Server Ports

- **Backend (FastAPI):** Port 8000
- **Frontend (Angular):** Port 4200
- **MongoDB Atlas:** Remote (not local port)

## Common Tasks

### Start Development Servers
```bash
# Start both servers
./scripts/server/start-servers.sh

# Or individually
cd backend && uvicorn main:app --reload --port 8000
cd valuation-frontend && npm start
```

### Stop All Servers
```bash
./scripts/server/stop-servers.sh
```

### Restart Backend After Code Changes
```bash
./scripts/server/restart_backend_with_logs.sh
```

### Check Server Status
```bash
# Check if backend is running
curl http://localhost:8000/api/health

# Check if frontend is running
curl http://localhost:4200
```

### View Server Logs
```bash
# Backend logs
tail -f logs/backend_logs.txt

# Or with restart script
./scripts/server/restart_backend_with_logs.sh
# Then view: cat logs/backend_logs.txt
```

## Troubleshooting

**Port Already in Use:**
```bash
# Kill process on port 8000 (backend)
lsof -ti:8000 | xargs kill -9

# Kill process on port 4200 (frontend)
lsof -ti:4200 | xargs kill -9
```

**Backend Won't Start:**
- Check Python environment is activated
- Verify MongoDB connection in logs
- Check requirements are installed

**Frontend Won't Start:**
- Run `npm install` in valuation-frontend/
- Check Node.js version (18+ required)
- Clear npm cache if needed: `npm cache clean --force`

**Database Connection Issues:**
- Verify MONGODB_URI in environment
- Check MongoDB Atlas network access
- Ensure IP is whitelisted in Atlas

## Environment Variables

```bash
# Backend
MONGODB_URI=mongodb+srv://...
MONGODB_DATABASE=valuationapp

# Frontend (optional)
API_URL=http://localhost:8000
```

## Best Practices

1. **Always stop servers cleanly** using stop script
2. **Check logs** when issues occur
3. **Use restart script** for backend changes (auto-reload)
4. **Kill orphan processes** if ports are blocked
5. **Monitor resource usage** during development
