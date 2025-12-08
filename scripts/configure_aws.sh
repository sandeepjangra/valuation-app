#!/bin/bash

echo "🔧 AWS Configuration for Local Development"
echo "========================================="

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Installing..."
    
    # Install AWS CLI based on OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
        sudo installer -pkg AWSCLIV2.pkg -target /
        rm AWSCLIV2.pkg
    else
        # Linux
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        unzip awscliv2.zip
        sudo ./aws/install
        rm -rf aws awscliv2.zip
    fi
fi

echo "✅ AWS CLI installed"

# Configure AWS credentials
echo ""
echo "🔑 Configure AWS Credentials"
echo "You need:"
echo "1. AWS Access Key ID"
echo "2. AWS Secret Access Key"
echo "3. Default region (us-east-1)"
echo ""

aws configure

echo ""
echo "✅ AWS configured. Test with: aws sts get-caller-identity"