#!/bin/bash

echo "🚀 Deploying Valuation App to AWS Amplify..."

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Deploy backend services
echo "📦 Deploying backend services..."
amplify push --yes

# Check if deployment was successful
if [ $? -eq 0 ]; then
    echo "✅ Backend deployment successful!"
    
    # Build and deploy frontend
    echo "🏗️ Building frontend..."
    cd valuation-frontend
    npm run build
    
    if [ $? -eq 0 ]; then
        echo "✅ Frontend build successful!"
        
        # Deploy to Amplify hosting
        cd ..
        amplify publish --yes
        
        if [ $? -eq 0 ]; then
            echo "🎉 Deployment completed successfully!"
            echo "📱 Your app is now live on AWS Amplify!"
            amplify status
        else
            echo "❌ Frontend deployment failed"
            exit 1
        fi
    else
        echo "❌ Frontend build failed"
        exit 1
    fi
else
    echo "❌ Backend deployment failed"
    exit 1
fi