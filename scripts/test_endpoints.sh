#!/bin/bash

# API Endpoint Testing Script for Valuation Application
# This script tests all available API endpoints and verifies responses

# Set script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# API Configuration
API_BASE_URL="http://localhost:8000"
API_PREFIX="/api"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ PASS${NC} $1"
    ((PASSED_TESTS++))
}

print_failure() {
    echo -e "${RED}❌ FAIL${NC} $1"
    ((FAILED_TESTS++))
}

print_warning() {
    echo -e "${YELLOW}⚠️  WARN${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️  INFO${NC} $1"
}

print_header() {
    echo -e "${CYAN}=== $1 ===${NC}"
}

print_test() {
    echo -e "${YELLOW}🧪 TEST${NC} $1"
    ((TOTAL_TESTS++))
}

# Function to check if server is running
check_server() {
    print_header "Checking Server Availability"
    print_test "Server connectivity"
    
    if curl -s -f "$API_BASE_URL/api/health" > /dev/null 2>&1; then
        print_success "Server is running and responding"
        return 0
    else
        print_failure "Server is not running or not responding"
        print_info "Please start the server using: ./scripts/manage_server.sh start"
        return 1
    fi
}

# Function to test endpoint with expected status code
test_endpoint() {
    local method=$1
    local endpoint=$2
    local expected_status=$3
    local test_name=$4
    local post_data=$5
    
    print_test "$test_name"
    
    local curl_cmd="curl -s -w '%{http_code}' -X $method"
    if [ -n "$post_data" ]; then
        curl_cmd="$curl_cmd -H 'Content-Type: application/json' -d '$post_data'"
    fi
    curl_cmd="$curl_cmd $API_BASE_URL$endpoint"
    
    local response=$(eval $curl_cmd)
    local status_code="${response: -3}"
    local body="${response%???}"
    
    if [ "$status_code" = "$expected_status" ]; then
        print_success "$test_name (HTTP $status_code)"
        
        # Additional validation for successful responses
        if [ "$status_code" = "200" ] && [ -n "$body" ]; then
            # Check if response is valid JSON
            if echo "$body" | python3 -c "import sys, json; json.load(sys.stdin)" 2>/dev/null; then
                print_info "  → Valid JSON response"
                
                # Show response summary
                local item_count=$(echo "$body" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if isinstance(data, list):
        print(f'{len(data)} items')
    elif isinstance(data, dict):
        if 'status' in data:
            print(f'Status: {data[\"status\"]}')
        else:
            print(f'{len(data)} fields')
    else:
        print('Single value')
except:
    print('Unable to parse')
" 2>/dev/null)
                if [ -n "$item_count" ]; then
                    print_info "  → Response contains: $item_count"
                fi
            else
                print_warning "  → Response is not valid JSON"
            fi
        fi
        return 0
    else
        print_failure "$test_name (Expected: $expected_status, Got: $status_code)"
        if [ -n "$body" ] && [ ${#body} -lt 500 ]; then
            print_info "  → Response: $body"
        fi
        return 1
    fi
}

# Function to test health endpoint
test_health_endpoint() {
    print_header "Health Check Endpoint"
    test_endpoint "GET" "/api/health" "200" "Health check endpoint"
}

# Function to test common fields endpoints
test_common_fields_endpoints() {
    print_header "Common Fields Endpoints"
    
    # Test main common fields endpoint
    test_endpoint "GET" "/api/common-fields" "200" "Get all common fields"
    
    # Test common fields by group
    test_endpoint "GET" "/api/common-fields/group/basic_info" "200" "Get basic_info group fields"
    test_endpoint "GET" "/api/common-fields/group/property_details" "200" "Get property_details group fields"
    test_endpoint "GET" "/api/common-fields/group/nonexistent_group" "200" "Get nonexistent group (should return empty array)"
}

# Function to test banks endpoints
test_banks_endpoints() {
    print_header "Banks Endpoints"
    
    # Test get all banks
    test_endpoint "GET" "/api/banks" "200" "Get all banks"
    
    # Test get specific bank
    test_endpoint "GET" "/api/banks/SBI" "200" "Get SBI bank details"
    test_endpoint "GET" "/api/banks/HDFC" "200" "Get HDFC bank details"
    test_endpoint "GET" "/api/banks/NONEXISTENT" "404" "Get nonexistent bank (should return 404)"
    
    # Test bank branches
    test_endpoint "GET" "/api/banks/SBI/branches" "200" "Get SBI bank branches"
    test_endpoint "GET" "/api/banks/HDFC/branches" "200" "Get HDFC bank branches"
    test_endpoint "GET" "/api/banks/NONEXISTENT/branches" "200" "Get nonexistent bank branches (should return empty array)"
}

# Function to test templates endpoints
test_templates_endpoints() {
    print_header "Templates Endpoints"
    
    # Test get templates for bank
    test_endpoint "GET" "/api/templates/bank/SBI" "200" "Get templates for SBI"
    test_endpoint "GET" "/api/templates/bank/HDFC" "200" "Get templates for HDFC"
    
    # Test get specific template
    test_endpoint "GET" "/api/templates/property-description-v1" "200" "Get property description template"
    test_endpoint "GET" "/api/templates/SBI_RES_FLAT_V2025" "200" "Get SBI residential flat template"
    test_endpoint "GET" "/api/templates/nonexistent-template" "404" "Get nonexistent template (should return 404)"
}

# Function to test reports endpoints
test_reports_endpoints() {
    print_header "Reports Endpoints"
    
    # Test create report (this will fail without proper authentication, but we test the endpoint exists)
    local sample_report_data='{
        "templateId": "SBI_RES_FLAT_V2025",
        "bankCode": "SBI",
        "borrowerInfo": {
            "name": "Test User",
            "email": "test@example.com"
        }
    }'
    
    # Note: This will likely return 401/403 due to authentication, but tests endpoint existence
    test_endpoint "POST" "/api/reports" "500" "Create new report (without auth)" "$sample_report_data"
    
    # Test get user reports (will also fail without auth)
    test_endpoint "GET" "/api/reports/user/test-user-id" "500" "Get user reports (without auth)"
}

# Function to test file upload endpoints
test_file_endpoints() {
    print_header "File Upload Endpoints"
    
    # Note: File upload tests are complex and would require multipart form data
    # For now, we just test that the endpoint exists and returns appropriate error
    print_test "File upload endpoint availability"
    
    local response=$(curl -s -w '%{http_code}' -X POST "$API_BASE_URL/api/files/upload")
    local status_code="${response: -3}"
    
    if [ "$status_code" = "422" ] || [ "$status_code" = "400" ] || [ "$status_code" = "500" ]; then
        print_success "File upload endpoint exists (HTTP $status_code)"
    else
        print_failure "File upload endpoint test (Got: $status_code)"
    fi
}

# Function to test invalid endpoints
test_invalid_endpoints() {
    print_header "Invalid Endpoints (Should Return 404)"
    
    test_endpoint "GET" "/api/nonexistent" "404" "Nonexistent endpoint"
    test_endpoint "GET" "/invalid-path" "404" "Invalid path"
    test_endpoint "POST" "/api/health" "405" "Invalid method on health endpoint"
}

# Function to run performance tests
test_performance() {
    print_header "Performance Tests"
    
    print_test "Response time for common fields endpoint"
    local start_time=$(date +%s%N)
    curl -s "$API_BASE_URL/api/common-fields" > /dev/null
    local end_time=$(date +%s%N)
    local duration=$((($end_time - $start_time) / 1000000))
    
    if [ $duration -lt 2000 ]; then  # Less than 2 seconds
        print_success "Response time: ${duration}ms (Good)"
    elif [ $duration -lt 5000 ]; then  # Less than 5 seconds
        print_warning "Response time: ${duration}ms (Acceptable)"
    else
        print_failure "Response time: ${duration}ms (Slow)"
    fi
}

# Function to test data integrity
test_data_integrity() {
    print_header "Data Integrity Tests"
    
    print_test "Common fields data structure"
    local fields_response=$(curl -s "$API_BASE_URL/api/common-fields")
    local fields_count=$(echo "$fields_response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if isinstance(data, list):
        valid_fields = 0
        for field in data:
            if isinstance(field, dict) and 'fieldName' in field and 'fieldType' in field:
                valid_fields += 1
        print(f'{valid_fields}/{len(data)}')
    else:
        print('0/0')
except:
    print('error')
" 2>/dev/null)
    
    if echo "$fields_count" | grep -q "error"; then
        print_failure "Common fields data structure is invalid"
    elif echo "$fields_count" | grep -q "/0"; then
        print_warning "No common fields data found"
    else
        print_success "Common fields data structure ($fields_count valid fields)"
    fi
    
    print_test "Banks data structure"
    local banks_response=$(curl -s "$API_BASE_URL/api/banks")
    local banks_count=$(echo "$banks_response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if isinstance(data, list):
        valid_banks = 0
        for bank in data:
            if isinstance(bank, dict) and 'bankName' in bank and 'bankCode' in bank:
                valid_banks += 1
        print(f'{valid_banks}/{len(data)}')
    else:
        print('0/0')
except:
    print('error')
" 2>/dev/null)
    
    if echo "$banks_count" | grep -q "error"; then
        print_failure "Banks data structure is invalid"
    elif echo "$banks_count" | grep -q "/0"; then
        print_warning "No banks data found"
    else
        print_success "Banks data structure ($banks_count valid banks)"
    fi
}

# Function to show summary
show_summary() {
    print_header "Test Summary"
    
    echo -e "${CYAN}Total Tests:${NC} $TOTAL_TESTS"
    echo -e "${GREEN}Passed:${NC} $PASSED_TESTS"
    echo -e "${RED}Failed:${NC} $FAILED_TESTS"
    
    local success_rate=0
    if [ $TOTAL_TESTS -gt 0 ]; then
        success_rate=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    fi
    
    echo -e "${BLUE}Success Rate:${NC} $success_rate%"
    
    if [ $FAILED_TESTS -eq 0 ]; then
        echo -e "${GREEN}🎉 All tests passed!${NC}"
        return 0
    else
        echo -e "${RED}⚠️  Some tests failed. Check the output above for details.${NC}"
        return 1
    fi
}

# Function to show help
show_help() {
    echo "Valuation Application API Testing Script"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --quick     Run only basic tests (health, common-fields, banks)"
    echo "  --full      Run all tests including performance and data integrity"
    echo "  --health    Run only health check"
    echo "  --help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0           # Run standard test suite"
    echo "  $0 --quick   # Run basic tests only"
    echo "  $0 --full    # Run comprehensive tests"
    echo ""
}

# Main script logic
main() {
    echo -e "${CYAN}🧪 Valuation Application API Testing Suite${NC}"
    echo "=================================================="
    echo ""
    
    # Check server availability first
    if ! check_server; then
        exit 1
    fi
    
    echo ""
    
    # Parse command line arguments
    case "${1:-standard}" in
        --health)
            test_health_endpoint
            ;;
        --quick)
            test_health_endpoint
            test_common_fields_endpoints
            test_banks_endpoints
            ;;
        --full)
            test_health_endpoint
            test_common_fields_endpoints
            test_banks_endpoints
            test_templates_endpoints
            test_reports_endpoints
            test_file_endpoints
            test_invalid_endpoints
            test_performance
            test_data_integrity
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        standard|"")
            test_health_endpoint
            test_common_fields_endpoints
            test_banks_endpoints
            test_templates_endpoints
            test_invalid_endpoints
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
    
    echo ""
    show_summary
}

# Run main function with all arguments
main "$@"