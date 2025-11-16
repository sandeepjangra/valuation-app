# AWS Amplify Setup for Valuation Application

## Overview
Your Valuation Application is now configured for AWS Amplify deployment with the following services:

### Services Configured:
- **Authentication**: Amazon Cognito (User Pool + Identity Pool)
- **API**: API Gateway with Lambda integration
- **Storage**: Amazon S3 for file uploads
- **Hosting**: Amplify Hosting with CI/CD
- **Database**: MongoDB Atlas (external)

## Prerequisites

1. **AWS Account**: Ensure you have an AWS account
2. **AWS CLI**: Install and configure AWS CLI
   ```bash
   aws configure
   ```
3. **Amplify CLI**: Already installed (v14.2.2)

## Deployment Steps

### 1. Configure AWS Credentials
```bash
amplify configure
```

### 2. Deploy Backend Services
```bash
amplify push --yes
```

### 3. Deploy Complete Application
```bash
./deploy-amplify.sh
```

## Configuration Files Created:

### Frontend Configuration:
- `amplify.yml` - Build configuration
- `valuation-frontend/amplify.yml` - Frontend-specific build config
- `valuation-frontend/src/aws-exports.ts` - AWS configuration
- `valuation-frontend/src/environments/` - Environment configs

### Backend Configuration:
- `amplify/backend/auth/valuationapp/` - Cognito authentication
- `amplify/backend/api/valuationapi/` - API Gateway configuration
- `amplify/backend/storage/valuationstorage/` - S3 storage
- `amplify/backend/function/valuationlambda/` - Lambda function
- `amplify/backend/hosting/amplifyhosting/` - Hosting configuration

## Cost Estimation (Monthly):

### Free Tier Eligible:
- **Cognito**: 50,000 MAUs free
- **Lambda**: 1M requests free
- **S3**: 5GB storage free
- **API Gateway**: 1M requests free

### Estimated Costs (after free tier):
- **Amplify Hosting**: $1-5/month
- **S3 Storage**: $1-3/month
- **Lambda**: $0.20 per 1M requests
- **API Gateway**: $3.50 per 1M requests
- **Cognito**: $0.0055 per MAU after 50k

**Total Estimated**: $5-15/month for small to medium usage

## Next Steps:

1. **Update MongoDB Connection**: 
   - Add your MongoDB Atlas connection string to Lambda environment variables
   - Update `amplify/backend/function/valuationlambda/cli-inputs.json`

2. **Configure Domain**: 
   - Add custom domain in Amplify Console
   - Configure SSL certificate

3. **Environment Variables**:
   - Set production MongoDB URI
   - Configure email settings for Cognito

4. **CI/CD Setup**:
   - Connect GitHub repository to Amplify
   - Configure automatic deployments

## Integration with Existing Backend:

Your existing FastAPI backend can be:
1. **Containerized** and deployed to AWS ECS/Fargate
2. **Converted** to Lambda functions
3. **Kept separate** and proxied through API Gateway

## Security Considerations:

- Enable MFA for production users
- Configure proper CORS settings
- Set up CloudWatch monitoring
- Enable AWS WAF for API protection
- Use environment-specific configurations

## Monitoring & Logging:

- CloudWatch Logs for Lambda functions
- X-Ray tracing for API Gateway
- Amplify Console for deployment logs
- CloudWatch metrics for all services

## Support:

For issues or questions:
1. Check AWS Amplify documentation
2. Use AWS Support (if you have a support plan)
3. Community forums and GitHub issues