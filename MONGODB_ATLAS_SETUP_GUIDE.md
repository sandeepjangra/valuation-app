# 🚀 MongoDB Atlas Cloud Setup Guide

This guide will help you set up MongoDB Atlas cloud database for your Valuation Application.

## 📋 **Step 1: Create MongoDB Atlas Account**

1. **Visit MongoDB Atlas**: Go to [https://cloud.mongodb.com](https://cloud.mongodb.com)
2. **Sign Up**: Create a free account or sign in if you already have one
3. **Create Organization**: Give it a name like "Valuation App"

## 🏗️ **Step 2: Create a New Cluster**

1. **Build a Database**: Click "Build a Database"
2. **Choose Deployment**:
   - **FREE (M0)**: For testing/development (500MB storage)
   - **SHARED (M2/M5)**: For small production (2-5GB storage)
   - **DEDICATED (M10+)**: For production (10GB+ storage, recommended)

3. **Select Provider & Region**:
   - **Provider**: AWS (recommended for India)
   - **Region**: `ap-south-1` (Mumbai) for best performance in India

4. **Cluster Name**: `ValuationApp-Production`

## 🔐 **Step 3: Create Database User**

1. **Username**: `app_user`
2. **Password**: Generate a strong password (save it securely!)
3. **Database User Privileges**: `Atlas admin` or `Read and write to any database`

## 🌐 **Step 4: Network Access**

1. **Add IP Address**:
   - For development: `0.0.0.0/0` (allows access from anywhere)
   - For production: Add your specific server IP addresses

2. **Comment**: "Development Access" or "Production Server"

## 📁 **Step 5: Get Connection String**

1. **Connect**: Click "Connect" on your cluster
2. **Connect your application**: Choose this option
3. **Driver**: Python, Version 3.11 or later
4. **Copy Connection String**: 
   ```
   mongodb+srv://app_user:<password>@valuationapp-xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

## ⚙️ **Step 6: Configure Your Application**

1. **Copy Environment File**:
   ```bash
   cp .env.example .env
   ```

2. **Update .env file** with your actual values:
   ```bash
   # Replace with your actual connection string
   MONGODB_URI=mongodb+srv://app_user:YOUR_PASSWORD@valuationapp-xxxxx.mongodb.net/valuation_app_prod?retryWrites=true&w=majority
   
   # Database name
   MONGODB_DB_NAME=valuation_app_prod
   
   # JWT Secret (generate a strong one)
   JWT_SECRET=your-super-secret-jwt-key-minimum-32-characters-long
   ```

## 🏃‍♂️ **Step 7: Run Setup Scripts**

1. **Activate Virtual Environment**:
   ```bash
   source activate-dev-env.sh
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup MongoDB Collections**:
   ```bash
   python scripts/setup_mongodb_atlas.py
   ```

## ✅ **Step 8: Verify Setup**

1. **Check Database Connection**:
   ```bash
   python -c "
   import asyncio
   from backend.database.mongodb_manager import db_manager
   
   async def test():
       connected = await db_manager.connect()
       if connected:
           print('✅ Successfully connected to MongoDB Atlas!')
           health = await db_manager.health_check()
           print(f'Database: {health[\"database\"]}')
           print(f'Status: {health[\"status\"]}')
       else:
           print('❌ Failed to connect to MongoDB Atlas')
       await db_manager.disconnect()
   
   asyncio.run(test())
   "
   ```

2. **Start FastAPI Server**:
   ```bash
   cd backend
   python main.py
   ```

3. **Test API Endpoints**:
   - Health Check: http://localhost:8000/api/health
   - API Docs: http://localhost:8000/api/docs
   - Banks: http://localhost:8000/api/banks

## 📊 **MongoDB Atlas Dashboard Features**

### **Monitor Your Database**:
- **Metrics**: Real-time performance metrics
- **Alerts**: Set up alerts for high CPU, memory usage
- **Logs**: View application and database logs

### **Security**:
- **IP Whitelist**: Restrict access to specific IPs
- **Database Users**: Manage user permissions
- **Encryption**: Data encrypted at rest and in transit

### **Backup**:
- **Continuous Backup**: Automatic point-in-time backups
- **Snapshot Backup**: Manual snapshots when needed

## 🔧 **Recommended Atlas Configuration**

### **For Development (M0 - Free)**:
```json
{
  "clusterTier": "M0",
  "region": "ap-south-1",
  "storage": "500MB",
  "backup": "Basic"
}
```

### **For Production (M10+)**:
```json
{
  "clusterTier": "M10",
  "region": "ap-south-1", 
  "storage": "10GB",
  "backup": "Continuous",
  "monitoring": "Enhanced",
  "alerts": "Enabled"
}
```

## 🔍 **Troubleshooting**

### **Connection Issues**:
1. **Check IP Whitelist**: Ensure your IP is allowed
2. **Verify Credentials**: Username/password correct
3. **Test Network**: Try from different network

### **Performance Issues**:
1. **Add Indexes**: Run the index creation script
2. **Monitor Metrics**: Check CPU/Memory usage
3. **Upgrade Tier**: Move to higher tier if needed

### **Authentication Errors**:
1. **Check User Permissions**: Ensure user has proper access
2. **Verify Database Name**: Must match in connection string
3. **Test Credentials**: Try connecting with MongoDB Compass

## 📞 **Support**

- **MongoDB Documentation**: https://docs.mongodb.com/
- **Atlas Support**: Available in your dashboard
- **Community Forum**: https://community.mongodb.com/

## 🎯 **Next Steps**

1. ✅ Set up MongoDB Atlas cluster
2. ✅ Configure environment variables
3. ✅ Run database setup script
4. 🔄 Build frontend application (Angular)
5. 🔄 Implement user authentication
6. 🔄 Create dynamic form templates
7. 🔄 Add report generation
8. 🔄 Deploy to production

---

**🔒 Security Note**: Never commit your `.env` file with real credentials to version control. Keep your database passwords secure and rotate them regularly.