# Valuation Application - Management Commands Quick Reference

## 🚀 **Full Stack Management** (Recommended)

### Unified Script (`./scripts/manage_app.sh`)
```bash
# Start both frontend and backend
./scripts/manage_app.sh start

# Stop both services
./scripts/manage_app.sh stop

# Restart both services
./scripts/manage_app.sh restart

# Check status of both services
./scripts/manage_app.sh status

# Quick health check
./scripts/manage_app.sh health

# View logs from both services
./scripts/manage_app.sh logs

# View only backend logs
./scripts/manage_app.sh logs backend

# View only frontend logs
./scripts/manage_app.sh logs frontend

# Install dependencies for both services
./scripts/manage_app.sh install

# Complete development setup (first time)
./scripts/manage_app.sh setup
```

---

## 🔧 **Individual Service Management**

### Backend API (`./scripts/manage_server.sh`)
```bash
# Backend operations
./scripts/manage_server.sh start      # Start FastAPI backend
./scripts/manage_server.sh stop       # Stop backend
./scripts/manage_server.sh restart    # Restart backend
./scripts/manage_server.sh status     # Backend status
./scripts/manage_server.sh logs       # Backend logs
./scripts/manage_server.sh test       # Test endpoints
```

### Frontend (`./scripts/manage_frontend.sh`)
```bash
# Frontend operations
./scripts/manage_frontend.sh start           # Start Angular dev server
./scripts/manage_frontend.sh stop            # Stop frontend
./scripts/manage_frontend.sh restart         # Restart frontend
./scripts/manage_frontend.sh status          # Frontend status
./scripts/manage_frontend.sh logs            # Frontend logs
./scripts/manage_frontend.sh install         # Install npm dependencies
./scripts/manage_frontend.sh clean-install   # Clean install dependencies
```

---

## 🌐 **Application URLs**

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:4200 | Angular application |
| **Backend API** | http://localhost:8000 | FastAPI backend |
| **API Documentation** | http://localhost:8000/api/docs | Swagger UI docs |

---

## 📋 **Common Workflows**

### 🎯 **First Time Setup**
```bash
# Complete environment setup
./scripts/manage_app.sh setup
```

### 🔄 **Daily Development**
```bash
# Start development environment
./scripts/manage_app.sh start

# Check if everything is running
./scripts/manage_app.sh status

# Stop when done
./scripts/manage_app.sh stop
```

### 🐛 **Debugging Issues**
```bash
# Check service health
./scripts/manage_app.sh health

# View logs for troubleshooting
./scripts/manage_app.sh logs

# Restart if needed
./scripts/manage_app.sh restart
```

### 📦 **Dependency Management**
```bash
# Install/update all dependencies
./scripts/manage_app.sh install

# Clean install frontend dependencies
./scripts/manage_frontend.sh clean-install
```

---

## ⚡ **Quick Commands**

```bash
# Start everything
./scripts/manage_app.sh start

# Check status
./scripts/manage_app.sh status

# Stop everything
./scripts/manage_app.sh stop
```

---

## 🆘 **Troubleshooting**

### Port Already in Use
```bash
# Stop services and try again
./scripts/manage_app.sh stop
./scripts/manage_app.sh start
```

### Dependencies Issues
```bash
# Reinstall all dependencies
./scripts/manage_app.sh install
```

### Services Not Responding
```bash
# Health check
./scripts/manage_app.sh health

# Force restart
./scripts/manage_app.sh restart
```

### View Detailed Logs
```bash
# All logs
./scripts/manage_app.sh logs

# Specific service logs
./scripts/manage_app.sh logs backend
./scripts/manage_app.sh logs frontend
```

---

## 📁 **Important Files**

- **Scripts**: `./scripts/`
  - `manage_app.sh` - Unified management
  - `manage_server.sh` - Backend management  
  - `manage_frontend.sh` - Frontend management
  
- **Logs**: `./logs/`
  - `backend.log` - Backend logs
  - `frontend.log` - Frontend logs
  
- **PID Files**: 
  - `.backend.pid` - Backend process ID
  - `.frontend.pid` - Frontend process ID