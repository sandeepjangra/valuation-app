#!/bin/bash

# Test script for .NET Backend API

echo "🧪 Testing Valuation App .NET Backend API"
echo "==========================================="
echo ""

# Test 1: Root endpoint
echo "Test 1: Root Endpoint"
echo "GET http://localhost:8000/"
curl -s http://localhost:8000/ | python3 -m json.tool
echo ""
echo ""

# Test 2: Health check
echo "Test 2: Health Check"
echo "GET http://localhost:8000/api/auth/health"
curl -s http://localhost:8000/api/auth/health | python3 -m json.tool
echo ""
echo ""

# Test 3: Login with admin credentials
echo "Test 3: Login with Admin Credentials"
echo "POST http://localhost:8000/api/auth/login"
echo "Body: {\"email\":\"admin@system.com\",\"password\":\"admin123\"}"
curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@system.com","password":"admin123","rememberMe":false}' | python3 -m json.tool
echo ""
echo ""

# Test 4: Login with invalid credentials
echo "Test 4: Login with Invalid Credentials"
echo "POST http://localhost:8000/api/auth/login"
echo "Body: {\"email\":\"wrong@email.com\",\"password\":\"wrongpass\"}"
curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"wrong@email.com","password":"wrongpass","rememberMe":false}' | python3 -m json.tool
echo ""
echo ""

echo "==========================================="
echo "✅ Tests completed"
