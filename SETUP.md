# ValuationApp Development Setup

This document provides setup instructions for the Property Valuation Application development environment.

## Prerequisites

- **Node.js 20 LTS** or higher
- **.NET 8.0 SDK**
- **Python 3.11+** (for development tools)
- **MongoDB 7.0+**
- **Git**
- **VS Code** (recommended)

## Quick Start

### 1. Clone and Setup Virtual Environment

```bash
# Navigate to project directory
cd /Users/sandeepjangra/Downloads/development/ValuationAppV1

# Create and activate Python virtual environment
python3 -m venv valuation_env
source valuation_env/bin/activate  # On macOS/Linux
# valuation_env\Scripts\activate   # On Windows

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your actual configuration values
# Update database connection strings, API keys, etc.
```

### 3. Backend Setup (.NET Core)

```bash
# Navigate to server directory
cd Server

# Restore NuGet packages
dotnet restore

# Build the project
dotnet build

# Run the API (development mode)
dotnet run --project WebApiHost
```

### 4. Frontend Setup

#### Angular Frontend
```bash
# Navigate to Angular app
cd src

# Install dependencies
npm install

# Update to latest Angular version (if needed)
ng update @angular/core @angular/cli

# Start development server
ng serve
```

#### React Frontend
```bash
# Navigate to React app
cd UI/valuvation

# Install dependencies
npm install

# Update React to latest version
npm install react@latest react-dom@latest

# Start development server
npm start
```

#### Blazor Frontend
```bash
# Navigate to Blazor app
cd UI/blazorUI

# Restore packages
dotnet restore

# Run Blazor server
dotnet run
```

### 5. Database Setup

```bash
# Start MongoDB (if using local installation)
brew services start mongodb/brew/mongodb-community

# Or using Docker
docker run -d -p 27017:27017 --name mongodb mongo:7.0
```

## Development URLs

- **Backend API:** https://localhost:5001/api
- **Angular App:** http://localhost:4200
- **React App:** http://localhost:3000
- **Blazor App:** https://localhost:5000
- **MongoDB:** mongodb://localhost:27017

## Recommended VS Code Extensions

- C# for Visual Studio Code
- Angular Language Service
- ES7+ React/Redux/React-Native snippets
- Prettier - Code formatter
- GitLens
- MongoDB for VS Code
- REST Client

## Version Information

| Technology | Current Version | Latest Recommended | Status |
|------------|-----------------|-------------------|---------|
| .NET Core | 6.0.100 | 8.0 LTS | ⚠️ Update Needed |
| Node.js | 16.13.0 | 20 LTS | ⚠️ Update Needed |
| Python | 3.11.14 | 3.11+ | ✅ Current |
| Angular | 11 | 18 | ⚠️ Update Needed |
| React | 17 | 18 | ⚠️ Update Needed |
| MongoDB | - | 7.0+ | ⚠️ Setup Needed |

## Virtual Environment Status

✅ **Python Virtual Environment Created**
- **Location:** `./valuation_env/`
- **Python Version:** 3.11.14
- **Status:** Active and configured
- **Packages Installed:** 120+ packages including FastAPI, Pandas, NumPy, Jupyter

### Installed Key Packages:
- **pandas:** 2.1.4
- **numpy:** 1.26.4
- **fastapi:** 0.115.6
- **flask:** 3.0.3
- **pymongo:** 4.8.0
- **jupyter:** 1.1.1
- **pytest:** 8.3.4
- **black:** 24.10.0

## Next Steps

1. Update to latest technology versions
2. Choose primary frontend technology
3. Implement proper authentication
4. Set up CI/CD pipeline
5. Add comprehensive testing

## Troubleshooting

### Common Issues

1. **Port conflicts:** Make sure ports 3000, 4200, 5000, 5001 are available
2. **MongoDB connection:** Verify MongoDB is running and accessible
3. **CORS issues:** Configure CORS settings in the API
4. **Package conflicts:** Clear node_modules and package-lock.json, then reinstall

### Useful Commands

```bash
# Check which ports are in use
lsof -i :3000,4200,5000,5001

# Kill processes on specific ports
kill -9 $(lsof -ti:3000)

# Reset Node.js cache
npm cache clean --force

# Check .NET installation
dotnet --info
```