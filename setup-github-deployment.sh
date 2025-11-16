#!/bin/bash

echo "🔗 Setting up GitHub-based deployment for Amplify..."

# App ID from your existing Amplify app
APP_ID="dqv91ku45c0m9"
REPO_URL="https://github.com/sandeepjangra/valuation-app.git"

echo "📋 Steps to complete setup:"
echo ""
echo "1. Create GitHub Personal Access Token:"
echo "   - Go to: https://github.com/settings/tokens"
echo "   - Click 'Generate new token (classic)'"
echo "   - Select scopes: repo, admin:repo_hook"
echo "   - Copy the token"
echo ""
echo "2. Run this command with your token:"
echo "   aws amplify update-app --app-id $APP_ID --repository $REPO_URL --oauth-token YOUR_GITHUB_TOKEN"
echo ""
echo "3. Create branch connected to GitHub:"
echo "   aws amplify create-branch --app-id $APP_ID --branch-name main --enable-auto-build"
echo ""
echo "4. Start deployment:"
echo "   aws amplify start-job --app-id $APP_ID --branch-name main --job-type RELEASE"
echo ""
echo "🌐 Your app will be available at: https://$APP_ID.amplifyapp.com"
echo ""
echo "Alternative: Use Amplify Console UI:"
echo "https://us-east-1.console.aws.amazon.com/amplify/home?region=us-east-1#/$APP_ID"