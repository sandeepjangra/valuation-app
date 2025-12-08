#!/usr/bin/env python3
"""
Server startup script with proper environment loading
"""

import os
import sys
from pathlib import Path

# Load environment variables FIRST
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
    print(f"✅ Loaded environment from: {env_path}")
except ImportError:
    print("⚠️ python-dotenv not installed, loading manually")
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        print(f"✅ Manually loaded environment from: {env_path}")

# Verify critical environment variables
required_vars = ['MONGODB_URI', 'COGNITO_USER_POOL_ID', 'COGNITO_CLIENT_ID']
missing_vars = []

for var in required_vars:
    if not os.getenv(var):
        missing_vars.append(var)

if missing_vars:
    print(f"❌ Missing required environment variables: {missing_vars}")
    sys.exit(1)

print(f"✅ MongoDB URI loaded: {os.getenv('MONGODB_URI')[:50]}...")
print(f"✅ Cognito Pool ID: {os.getenv('COGNITO_USER_POOL_ID')}")

# Now import and start the FastAPI app
if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting FastAPI server...")
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000,
        reload=False,  # Disable reload to avoid import issues
        log_level="info"
    )