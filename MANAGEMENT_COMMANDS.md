# Valuation Application - Management Commands Quick Reference

## 🚀 **Backend Management** (API Only)

### Unified Script (`./scripts/manage_app.sh`)
```bash
# Start backend only
./scripts/manage_app.sh start

# Stop backend service
./scripts/manage_app.sh stop

# Restart backend service
./scripts/manage_app.sh restart

# Check status of backend service
./scripts/manage_app.sh status

# Quick health check
./scripts/manage_app.sh health

# View backend logs
./scripts/manage_app.sh logs

# View only backend logs
./scripts/manage_app.sh logs backend

# Install backend dependencies
./scripts/manage_app.sh install

# Complete development setup (first time)
./scripts/manage_app.sh setup
```

---

## 🔧 **Backend API Management**

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

---

## 🌐 **Application URLs**

| Service | URL | Description |
|---------|-----|-------------|
| **Backend API** | http://localhost:8000 | FastAPI backend |
| **API Documentation** | http://localhost:8000/api/docs | Swagger UI docs |
| **API Redoc** | http://localhost:8000/api/redoc | ReDoc documentation |

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
```

---

## ⚡ **Quick Commands**

```bash
# Start backend
./scripts/manage_app.sh start

# Check status
./scripts/manage_app.sh status

# Stop backend
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

### Service Not Responding
```bash
# Health check
./scripts/manage_app.sh health

# Force restart
./scripts/manage_app.sh restart
```

### View Detailed Logs
```bash
# Backend logs
./scripts/manage_app.sh logs
./scripts/manage_app.sh logs backend
```

---

## 📁 **Important Files**

- **Scripts**: `./scripts/`
  - `manage_app.sh` - Unified management
  - `manage_server.sh` - Backend management  
  
- **Logs**: `./logs/`
  - `backend.log` - Backend logs
  
- **PID Files**: 
  - `.backend.pid` - Backend process ID