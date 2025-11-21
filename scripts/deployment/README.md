# Deployment Scripts

Scripts for deploying the application to various environments.

## Scripts Overview

### `deploy-amplify.sh`
Deploys the application to AWS Amplify hosting.

**Prerequisites:**
- AWS CLI installed and configured
- Amplify app created in AWS console
- Proper AWS credentials set

**Usage:**
```bash
./scripts/deployment/deploy-amplify.sh
```

### `setup-github-deployment.sh`
Configures GitHub Actions for automated deployment.

**What it does:**
- Sets up GitHub Actions workflow
- Configures deployment secrets
- Enables automated CI/CD pipeline

**Usage:**
```bash
./scripts/deployment/setup-github-deployment.sh
```

### `activate-dev-env.sh`
Activates the Python virtual environment for development.

**Usage:**
```bash
source ./scripts/deployment/activate-dev-env.sh
# or
. ./scripts/deployment/activate-dev-env.sh
```

**Note:** Must be sourced (not executed) to activate in current shell.

### `verify-tech-stack.sh`
Verifies that all required technologies are installed.

**Checks:**
- Python version and packages
- Node.js and npm versions
- Angular CLI
- MongoDB connection
- Docker/Podman (if used)

**Usage:**
```bash
./scripts/deployment/verify-tech-stack.sh
```

## Deployment Workflow

1. **Verify Stack:** Run `verify-tech-stack.sh` to ensure all dependencies are installed
2. **Activate Environment:** Source `activate-dev-env.sh` to use Python virtual environment
3. **Test Locally:** Ensure application runs correctly
4. **Deploy:** Run appropriate deployment script (`deploy-amplify.sh`)
5. **Verify Deployment:** Check logs and test deployed application

## Environment Variables

Ensure these are set before deployment:

```bash
# MongoDB Atlas
MONGODB_URI=mongodb+srv://...
MONGODB_DATABASE=valuationapp

# AWS (for Amplify)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=...

# GitHub (for Actions)
GITHUB_TOKEN=...
```

## Troubleshooting

**Deployment fails:** Check AWS credentials and Amplify app configuration
**GitHub Actions not working:** Verify secrets are set in repository settings
**Environment not activating:** Ensure Python virtual environment exists in `valuation_env/`
