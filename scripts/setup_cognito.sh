#!/bin/bash

# AWS Cognito Setup for Local Development
echo "🔐 Setting up AWS Cognito for local development..."

# Create User Pool
USER_POOL=$(aws cognito-idp create-user-pool \
  --pool-name "ValuationApp-Dev" \
  --policies '{
    "PasswordPolicy": {
      "MinimumLength": 8,
      "RequireUppercase": true,
      "RequireLowercase": true,
      "RequireNumbers": true,
      "RequireSymbols": false
    }
  }' \
  --auto-verified-attributes email \
  --username-attributes email \
  --verification-message-template '{
    "DefaultEmailOption": "CONFIRM_WITH_CODE"
  }' \
  --query 'UserPool.Id' \
  --output text)

echo "✅ User Pool created: $USER_POOL"

# Create User Pool Client
CLIENT_ID=$(aws cognito-idp create-user-pool-client \
  --user-pool-id $USER_POOL \
  --client-name "ValuationApp-Dev-Client" \
  --explicit-auth-flows ADMIN_NO_SRP_AUTH ALLOW_USER_PASSWORD_AUTH ALLOW_REFRESH_TOKEN_AUTH \
  --token-validity-units '{
    "AccessToken": "hours",
    "IdToken": "hours",
    "RefreshToken": "days"
  }' \
  --access-token-validity 1 \
  --id-token-validity 1 \
  --refresh-token-validity 30 \
  --query 'UserPoolClient.ClientId' \
  --output text)

echo "✅ Client created: $CLIENT_ID"

# Create groups
aws cognito-idp create-group --group-name admin --user-pool-id $USER_POOL --description "Administrators"
aws cognito-idp create-group --group-name manager --user-pool-id $USER_POOL --description "Managers"  
aws cognito-idp create-group --group-name employee --user-pool-id $USER_POOL --description "Employees"

echo "✅ Groups created"

# Output configuration
echo ""
echo "📋 Add these to your backend/.env file:"
echo "COGNITO_USER_POOL_ID=$USER_POOL"
echo "COGNITO_CLIENT_ID=$CLIENT_ID"
echo "AWS_REGION=us-east-1"