#!/bin/bash

# Quick API Summary Script for Valuation Application
# This script provides a summary of all available endpoints and data

# Set colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

API_BASE_URL="http://localhost:8000"

echo -e "${CYAN}🔍 Valuation Application API Summary${NC}"
echo "======================================="
echo ""

# Check if server is running
if ! curl -s -f "$API_BASE_URL/api/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ Server is not running. Please start it first:${NC}"
    echo "   ./scripts/manage_server.sh start"
    exit 1
fi

echo -e "${GREEN}✅ Server is running at $API_BASE_URL${NC}"
echo ""

# Common Fields Summary
echo -e "${BLUE}📋 Common Fields Summary:${NC}"
curl -s "$API_BASE_URL/api/common-fields" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f'   Total fields: {len(data)}')
    
    # Group by fieldGroup
    groups = {}
    for field in data:
        group = field.get('fieldGroup', 'unknown')
        if group not in groups:
            groups[group] = []
        groups[group].append(field)
    
    print(f'   Field groups: {len(groups)}')
    for group, fields in sorted(groups.items()):
        print(f'     - {group}: {len(fields)} fields')
except:
    print('   Error parsing response')
"
echo ""

# Banks Summary
echo -e "${BLUE}🏦 Banks Summary:${NC}"
curl -s "$API_BASE_URL/api/banks" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f'   Total banks: {len(data)}')
    for bank in data:
        branches_count = len(bank.get('branches', []))
        print(f'     - {bank[\"bankName\"]} ({bank[\"bankCode\"]}): {branches_count} branches')
except:
    print('   Error parsing response')
"
echo ""

# Templates Summary
echo -e "${BLUE}📄 Templates Summary:${NC}"
echo "   Available templates:"
echo "     - Property Description Template (property-description-v1)"
echo "     - SBI Residential Flat Template (SBI_RES_FLAT_V2025)"
echo ""

# Available Endpoints
echo -e "${BLUE}🌐 Available Endpoints:${NC}"
echo "   Health & Status:"
echo "     GET  /api/health"
echo ""
echo "   Common Fields:"
echo "     GET  /api/common-fields"
echo "     GET  /api/common-fields/group/{group_name}"
echo ""
echo "   Banks:"
echo "     GET  /api/banks"
echo "     GET  /api/banks/{bank_code}"
echo "     GET  /api/banks/{bank_code}/branches"
echo ""
echo "   Templates:"
echo "     GET  /api/templates/bank/{bank_code}"
echo "     GET  /api/templates/{template_id}"
echo ""
echo "   Reports (Auth Required):"
echo "     POST /api/reports"
echo "     GET  /api/reports/user/{user_id}"
echo ""
echo "   Files (Auth Required):"
echo "     POST /api/files/upload"
echo ""

echo -e "${CYAN}📚 Documentation: $API_BASE_URL/api/docs${NC}"
echo -e "${CYAN}🔧 Management: ./scripts/manage_server.sh {start|stop|status}${NC}"
echo -e "${CYAN}🧪 Testing: ./scripts/test_endpoints.sh {--quick|--full}${NC}"