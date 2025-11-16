# Valuation Application

## Overview
A comprehensive property valuation application with Angular frontend and FastAPI backend, deployed on AWS Amplify.

## Architecture
- **Frontend**: Angular 20 with AWS Amplify integration
- **Backend**: FastAPI with MongoDB Atlas
- **Hosting**: AWS Amplify with CI/CD
- **Database**: MongoDB Atlas (external)

## Deployment
This application is configured for Git-based deployment on AWS Amplify.

### Build Configuration
- Root: `amplify.yml`
- Frontend: `valuation-frontend/amplify.yml`
- Build output: `valuation-frontend/dist/valuation-frontend/browser`

### Environment Variables (Set in Amplify Console)
- `MONGODB_URI`: MongoDB Atlas connection string
- `NODE_ENV`: production

## Local Development
```bash
# Frontend
cd valuation-frontend
npm install
npm start

# Backend
cd backend
pip install -r ../requirements.txt
python main.py
```