# Valuation App - .NET Backend

A clean architecture .NET 8.0 backend API for the Valuation Application with MongoDB Atlas integration and JWT authentication.

## 🏗️ Architecture

```
ValuationApp.Backend/
├── ValuationApp.API/              # Web API Layer (Controllers, Middleware)
├── ValuationApp.Core/             # Business Logic (Services, Interfaces, DTOs)
├── ValuationApp.Infrastructure/   # Data Access (Repositories, MongoDB)
└── ValuationApp.Common/           # Shared Utilities (JWT, Password Helpers)
```

## 🚀 Features

- ✅ Clean Architecture with Dependency Injection
- ✅ MongoDB Atlas Integration
- ✅ JWT Authentication (Access, ID, Refresh tokens)
- ✅ BCrypt Password Hashing (compatible with Python bcrypt)
- ✅ CORS Configuration for Angular Frontend
- ✅ Swagger/OpenAPI Documentation
- ✅ Environment Variables Support (.env)
- ✅ Comprehensive Error Handling
- ✅ System Admin Full Access

## 📋 Prerequisites

- .NET 8.0 SDK or higher
- MongoDB Atlas account
- Active `.env` file in project root with MongoDB credentials

## 🔧 Configuration

### MongoDB Atlas Setup

The application reads MongoDB configuration from the `.env` file in the project root:

```bash
MONGODB_URI=mongodb+srv://USERNAME:PASSWORD@cluster.mongodb.net/...
MONGODB_ADMIN_DB_NAME=valuation_admin
MONGODB_REPORTS_DB_NAME=valuation_reports
JWT_SECRET=your-secret-key-here
```

### App Settings

Additional configuration in `appsettings.json`:

```json
{
  "JwtSettings": {
    "Issuer": "ValuationApp",
    "Audience": "ValuationApp.Frontend",
    "ExpiryHours": 24
  },
  "CorsSettings": {
    "AllowedOrigins": ["http://localhost:4200", "http://localhost:3000"]
  }
}
```

## 🏃 Running the Application

### Development Mode

```bash
cd backend-dotnet/ValuationApp.API
dotnet run
```

The API will start on `http://localhost:8000`

### Building the Solution

```bash
cd backend-dotnet
dotnet build ValuationApp.Backend.sln
```

### Running Tests

```bash
cd backend-dotnet
./test-api.sh
```

## 📚 API Endpoints

### Authentication

#### POST /api/auth/login
Login with email and password

**Request:**
```json
{
  "email": "admin@system.com",
  "password": "admin123",
  "rememberMe": false
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "accessToken": "eyJhbGc...",
    "idToken": "eyJhbGc...",
    "refreshToken": "eyJhbGc...",
    "expiresIn": 86400,
    "user": {
      "userId": "user_system_admin_001",
      "email": "admin@system.com",
      "fullName": "System Administrator",
      "role": "system_admin",
      "isSystemAdmin": true,
      "organizationId": "system_admin",
      "permissions": {
        "canSubmitReports": true,
        "canManageUsers": true,
        "isManager": true,
        "isAdmin": true
      }
    }
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "message": "Invalid email or password",
  "data": null
}
```

#### POST /api/auth/logout
Logout (client-side token removal)

#### GET /api/auth/me
Get current user information (requires JWT token)

#### GET /api/auth/health
Health check endpoint

### Root

#### GET /
API information and available endpoints

```json
{
  "success": true,
  "message": "Valuation App API is running",
  "version": "1.0.0",
  "timestamp": "2026-01-09T...",
  "endpoints": [...]
}
```

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. **Login**: User provides email/password
2. **Verification**: Password is verified using BCrypt (compatible with Python bcrypt `$2b$` format)
3. **Token Generation**: Three tokens are generated:
   - **Access Token**: Used for API requests (24h expiry, or 7 days with remember_me)
   - **ID Token**: Contains user identity claims
   - **Refresh Token**: Used to refresh access tokens (7 days expiry)
4. **Authorization**: Include `Authorization: Bearer <access_token>` header in requests

### System Admin Credentials

The system admin has **full access** to all features and components:

```
Email: admin@system.com
Password: admin123
```

**Permissions:**
- ✅ Can submit reports
- ✅ Can manage users
- ✅ Is manager
- ✅ Is admin
- ✅ Is system admin
- ✅ Access to ALL components and actions

## 🗄️ MongoDB Collections

### valuation_admin Database

#### users Collection
```javascript
{
  "_id": ObjectId,
  "user_id": "user_system_admin_001",
  "email": "admin@system.com",
  "full_name": "System Administrator",
  "password_hash": "$2b$12$...",
  "organization_id": "system_admin",
  "role": "system_admin",
  "roles": ["system_admin", "admin", "manager"],
  "is_active": true,
  "is_system_admin": true,
  "permissions": {
    "can_submit_reports": true,
    "can_manage_users": true,
    "is_manager": true,
    "is_admin": true
  },
  "created_at": ISODate,
  "updated_at": ISODate,
  "last_login": ISODate
}
```

## 📦 NuGet Packages

- **MongoDB.Driver** (3.5.2) - MongoDB .NET driver
- **BCrypt.Net-Next** (4.0.3) - Password hashing
- **System.IdentityModel.Tokens.Jwt** (8.15.0) - JWT tokens
- **Microsoft.AspNetCore.Authentication.JwtBearer** (8.0.0) - JWT authentication middleware
- **DotNetEnv** (3.1.1) - Environment variables support

## 🔍 Swagger Documentation

When running in Development mode, access the Swagger UI at:
```
http://localhost:8000/swagger
```

Interactive API documentation with:
- All endpoints documented
- Request/response schemas
- Test directly from browser
- JWT authentication support

## 🛠️ Development

### Project Structure

```
ValuationApp.API/
├── Controllers/
│   └── AuthController.cs           # Authentication endpoints
├── Program.cs                        # App configuration & DI
├── appsettings.json                 # Configuration
└── Properties/
    └── launchSettings.json          # Launch profiles

ValuationApp.Core/
├── Entities/
│   └── User.cs                      # User entity model
├── DTOs/
│   ├── LoginRequest.cs              # Login request DTO
│   └── LoginResponse.cs             # Login response DTO
├── Interfaces/
│   ├── IAuthService.cs              # Auth service interface
│   └── IUserRepository.cs           # User repository interface
└── Services/
    └── AuthService.cs               # Authentication business logic

ValuationApp.Infrastructure/
├── Data/
│   ├── MongoDbSettings.cs           # MongoDB configuration
│   └── MongoDbContext.cs            # MongoDB context
└── Repositories/
    └── UserRepository.cs            # User data access

ValuationApp.Common/
├── Helpers/
│   ├── JwtHelper.cs                 # JWT token generation/validation
│   └── PasswordHelper.cs            # BCrypt password operations
└── Models/
    └── ApiResponse.cs               # Standard API response wrapper
```

### Adding New Endpoints

1. Create interface in `ValuationApp.Core/Interfaces/`
2. Implement service in `ValuationApp.Core/Services/`
3. Create repository if needed in `ValuationApp.Infrastructure/Repositories/`
4. Add controller in `ValuationApp.API/Controllers/`
5. Register services in `Program.cs`

## 🧪 Testing

Use the provided test script:

```bash
cd backend-dotnet
./test-api.sh
```

Or use curl manually:

```bash
# Health check
curl http://localhost:8000/api/auth/health

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@system.com","password":"admin123"}'
```

## 🐛 Troubleshooting

### MongoDB Connection Issues

- Verify `.env` file exists in project root
- Check `MONGODB_URI` is correct
- Ensure MongoDB Atlas IP whitelist includes your IP
- Verify database user credentials

### JWT Token Issues

- Ensure `JWT_SECRET` is set in `.env`
- Check token expiry (default: 24 hours)
- Verify `Issuer` and `Audience` match in configuration

### CORS Issues

- Check `CorsSettings:AllowedOrigins` in `appsettings.json`
- Ensure frontend URL is in the allowed origins list
- Verify CORS middleware is enabled in `Program.cs`

## 📝 Notes

- **System Admin**: The `admin@system.com` user has complete access to all features
- **Password Compatibility**: BCrypt implementation is compatible with Python's bcrypt library
- **Token Security**: JWT secret should be strong and kept secure (32+ characters)
- **Database**: Uses separate databases for admin data and reports
- **Environment**: `.env` file must be in the project root directory (two levels up from API)

## 🔄 Future Enhancements

- [ ] Refresh token endpoint implementation
- [ ] Token blacklisting for logout
- [ ] Rate limiting for login attempts
- [ ] Email verification system
- [ ] Password reset functionality
- [ ] User management endpoints
- [ ] Audit logging
- [ ] API versioning
- [ ] Health check with MongoDB connection test

## 📄 License

Part of the Valuation App system.

---

**Backend Status:** ✅ Fully Operational  
**Port:** 8000  
**Database:** MongoDB Atlas  
**Authentication:** JWT with BCrypt
