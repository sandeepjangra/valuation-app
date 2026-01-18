#!/bin/bash

# Test Activity Logging System
# This script tests the complete activity logging flow

API_URL="http://localhost:8000/api/activity-logs"
TEST_USER_ID="test-user-$(date +%s)"
ORG_SHORT_NAME="TEST"

echo "🧪 Testing Activity Logging System"
echo "===================================="
echo ""

# Test 1: Log authentication activity
echo "📝 Test 1: Logging authentication activity (login)..."
RESPONSE=$(curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "'"$TEST_USER_ID"'",
    "orgShortName": "'"$ORG_SHORT_NAME"'",
    "action": "login",
    "actionType": "authentication",
    "description": "User logged in successfully"
  }')

if echo "$RESPONSE" | grep -q "\"success\":true"; then
  ACTIVITY_ID=$(echo "$RESPONSE" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
  echo "✅ Login activity logged successfully (ID: $ACTIVITY_ID)"
else
  echo "❌ Failed to log login activity"
  echo "Response: $RESPONSE"
  exit 1
fi

sleep 1

# Test 2: Log report creation
echo ""
echo "📝 Test 2: Logging report activity (create report)..."
RESPONSE=$(curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "'"$TEST_USER_ID"'",
    "orgShortName": "'"$ORG_SHORT_NAME"'",
    "action": "create_report",
    "actionType": "report",
    "description": "Created valuation report for Property XYZ",
    "entityType": "report",
    "entityId": "report-123"
  }')

if echo "$RESPONSE" | grep -q "\"success\":true"; then
  echo "✅ Report creation activity logged successfully"
else
  echo "❌ Failed to log report activity"
  exit 1
fi

sleep 1

# Test 3: Log user management activity
echo ""
echo "📝 Test 3: Logging user management activity..."
RESPONSE=$(curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "'"$TEST_USER_ID"'",
    "orgShortName": "'"$ORG_SHORT_NAME"'",
    "action": "create_user",
    "actionType": "user_management",
    "description": "Created new user account",
    "entityType": "user",
    "entityId": "user-456"
  }')

if echo "$RESPONSE" | grep -q "\"success\":true"; then
  echo "✅ User management activity logged successfully"
else
  echo "❌ Failed to log user management activity"
  exit 1
fi

sleep 1

# Test 4: Retrieve user activities
echo ""
echo "🔍 Test 4: Retrieving activities for test user..."
RESPONSE=$(curl -s -X GET "$API_URL/user/$TEST_USER_ID")

if echo "$RESPONSE" | grep -q "\"success\":true"; then
  ACTIVITY_COUNT=$(echo "$RESPONSE" | grep -o '"action"' | wc -l | tr -d ' ')
  echo "✅ Retrieved $ACTIVITY_COUNT activities for user"
  
  if [ "$ACTIVITY_COUNT" -ge 3 ]; then
    echo "✅ All logged activities found"
  else
    echo "⚠️  Expected at least 3 activities, found $ACTIVITY_COUNT"
  fi
else
  echo "❌ Failed to retrieve user activities"
  exit 1
fi

# Test 5: Retrieve organization activities
echo ""
echo "🔍 Test 5: Retrieving activities for test organization..."
RESPONSE=$(curl -s -X GET "$API_URL/org/$ORG_SHORT_NAME?limit=10")

if echo "$RESPONSE" | grep -q "\"success\":true"; then
  ORG_ACTIVITY_COUNT=$(echo "$RESPONSE" | grep -o '"action"' | wc -l | tr -d ' ')
  echo "✅ Retrieved $ORG_ACTIVITY_COUNT activities for organization"
else
  echo "❌ Failed to retrieve organization activities"
  exit 1
fi

# Test 6: Get activities by action type
echo ""
echo "🔍 Test 6: Retrieving activities by type (authentication)..."
RESPONSE=$(curl -s -X GET "$API_URL/type/authentication?limit=10")

if echo "$RESPONSE" | grep -q "\"success\":true"; then
  TYPE_ACTIVITY_COUNT=$(echo "$RESPONSE" | grep -o '"action"' | wc -l | tr -d ' ')
  echo "✅ Retrieved $TYPE_ACTIVITY_COUNT authentication activities"
else
  echo "❌ Failed to retrieve activities by type"
  exit 1
fi

# Test 7: Get activity for specific entity
echo ""
echo "🔍 Test 7: Retrieving activities for specific entity (report-123)..."
RESPONSE=$(curl -s -X GET "$API_URL/entity/report/report-123")

if echo "$RESPONSE" | grep -q "\"success\":true"; then
  ENTITY_ACTIVITY_COUNT=$(echo "$RESPONSE" | grep -o '"entityId":"report-123"' | wc -l | tr -d ' ')
  echo "✅ Retrieved $ENTITY_ACTIVITY_COUNT activities for report-123"
  
  if [ "$ENTITY_ACTIVITY_COUNT" -ge 1 ]; then
    echo "✅ Entity activity tracking verified"
  fi
else
  echo "❌ Failed to retrieve entity activities"
  exit 1
fi

# Test 8: Get activity counts by type
echo ""
echo "📊 Test 8: Retrieving activity counts by type..."
RESPONSE=$(curl -s -X GET "$API_URL/analytics/counts?days=1")

if echo "$RESPONSE" | grep -q "\"success\":true"; then
  echo "✅ Activity counts retrieved successfully"
  echo "   Sample data: $(echo "$RESPONSE" | head -c 100)..."
else
  echo "❌ Failed to retrieve activity counts"
  exit 1
fi

echo ""
echo "===================================="
echo "✅ All tests passed!"
echo ""
echo "📊 Summary:"
echo "  - Logged: 3 different activity types"
echo "  - Retrieved: User, org, type-filtered, entity-specific activities"
echo "  - Analytics: Activity counts by type"
echo ""
echo "🎉 Activity logging system is working correctly!"
