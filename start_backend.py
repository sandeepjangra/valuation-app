#!/usr/bin/env python3
import os
import subprocess
import sys

# Set the MongoDB URI
os.environ["MONGODB_URI"] = "mongodb+srv://app_user:KOtsC5qeCc78icks@valuationreportcluster.5ixm1s7.mongodb.net/?retryWrites=true&w=majority&appName=ValuationReportCluster"

# Change to backend directory
backend_dir = "/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend"
os.chdir(backend_dir)

# Python path
python_path = "/Users/sandeepjangra/Downloads/development/ValuationAppV1/valuation_env/bin/python"

# Start uvicorn
cmd = [python_path, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
print("🚀 Starting backend server...")
print(f"📂 Directory: {os.getcwd()}")
print(f"🐍 Command: {' '.join(cmd)}")
print()

try:
    subprocess.run(cmd)
except KeyboardInterrupt:
    print("\n⏹️ Server stopped by user")
except Exception as e:
    print(f"❌ Error starting server: {e}")
    sys.exit(1)