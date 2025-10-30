#!/bin/bash

# 🧪 Automated E2E Test Runner for Teams API Integration
# 
# This script runs all test scenarios from MANUAL_TEST_GUIDE.md
# and generates a comprehensive test report.
#
# Usage:
#   ./run_e2e_tests.sh                    # Run all tests
#   ./run_e2e_tests.sh --test single      # Run single test
#   ./run_e2e_tests.sh --test multiple    # Run multiple test
#   ./run_e2e_tests.sh --test dry-run     # Run dry-run test
#   ./run_e2e_tests.sh --test error       # Run error handling test
#   ./run_e2e_tests.sh --quick            # Quick test (single league only)
#
# Prerequisites:
#   - Backend virtual environment activated
#   - Environment variables set (.env file)
#   - Supabase database accessible
#
# Author: Oover Development Team
# Created: 2025-10-30

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Output directory for test results
OUTPUT_DIR="test_results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="${OUTPUT_DIR}/test_report_${TIMESTAMP}.md"

# Functions
print_header() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_test_header() {
    echo ""
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${MAGENTA}🧪 TEST $(($TESTS_TOTAL + 1)): $1${NC}"
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

record_test_result() {
    local test_name="$1"
    local status="$2"
    local details="$3"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    if [ "$status" = "PASS" ]; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        print_success "$test_name: PASSED"
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        print_error "$test_name: FAILED"
        print_error "Details: $details"
    fi
    
    # Write to report
    echo "### Test $TESTS_TOTAL: $test_name" >> "$REPORT_FILE"
    echo "- **Status**: $status" >> "$REPORT_FILE"
    echo "- **Details**: $details" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
}

check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check if we're in backend directory
    if [ ! -f "manage.py" ]; then
        print_error "Not in backend directory. Please cd to backend/"
        exit 1
    fi
    print_success "In correct directory"
    
    # Check if virtual environment is activated
    if [ -z "$VIRTUAL_ENV" ]; then
        print_warning "Virtual environment not activated"
        print_info "Attempting to activate..."
        
        if [ -d "venv" ]; then
            source venv/bin/activate
            print_success "Virtual environment activated"
        elif [ -d "../venv" ]; then
            source ../venv/bin/activate
            print_success "Virtual environment activated"
        else
            print_error "Could not find virtual environment"
            exit 1
        fi
    else
        print_success "Virtual environment active: $VIRTUAL_ENV"
    fi
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        print_error ".env file not found"
        exit 1
    fi
    print_success ".env file found"
    
    # Check if FOOTBALL_DATA_API_KEY is set
    if [ -z "$FOOTBALL_DATA_API_KEY" ]; then
        # Try to load from .env
        export $(grep -v '^#' .env | xargs)
        
        if [ -z "$FOOTBALL_DATA_API_KEY" ]; then
            print_error "FOOTBALL_DATA_API_KEY not set in environment or .env"
            exit 1
        fi
    fi
    print_success "API key configured"
    
    # Check database connectivity (optional, comment out if not needed)
    # python manage.py showmigrations > /dev/null 2>&1
    # if [ $? -eq 0 ]; then
    #     print_success "Database connection OK"
    # else
    #     print_error "Database connection failed"
    #     exit 1
    # fi
    
    print_success "All prerequisites met"
    echo ""
}

setup_test_environment() {
    print_header "Setting Up Test Environment"
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    print_success "Output directory created: $OUTPUT_DIR"
    
    # Initialize report file
    cat > "$REPORT_FILE" << EOF
# 🧪 Teams API E2E Test Report

**Date**: $(date)
**Environment**: Development
**Backend**: Django
**Database**: Supabase PostgreSQL

---

## Test Results Summary

EOF
    
    print_success "Report file initialized: $REPORT_FILE"
    echo ""
}

# Test 1: Single League Fetch (Premier League)
test_single_league() {
    print_test_header "Single League Fetch (Premier League)"
    
    local start_time=$(date +%s)
    local output_file="${OUTPUT_DIR}/test1_single_league_${TIMESTAMP}.log"
    
    print_info "Running: python manage.py fetch_teams --league PL --provider football-data"
    
    if python manage.py fetch_teams --league PL --provider football-data > "$output_file" 2>&1; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        # Check if output contains expected patterns
        if grep -q "Successfully processed" "$output_file" && \
           grep -q "teams created\|teams updated" "$output_file"; then
            record_test_result "Single League Fetch" "PASS" "Executed in ${duration}s. Teams fetched successfully."
        else
            record_test_result "Single League Fetch" "FAIL" "Command executed but unexpected output format"
        fi
    else
        record_test_result "Single League Fetch" "FAIL" "Command failed with error. Check $output_file"
    fi
    
    print_info "Output saved to: $output_file"
}

# Test 2: Multiple Leagues Fetch (All European)
test_multiple_leagues() {
    print_test_header "Multiple Leagues Fetch (All European)"
    
    local start_time=$(date +%s)
    local output_file="${OUTPUT_DIR}/test2_multiple_leagues_${TIMESTAMP}.log"
    
    print_info "Running: python manage.py fetch_teams --all-european --provider football-data"
    print_warning "This may take 1-2 minutes and use 5+ API requests"
    
    if python manage.py fetch_teams --all-european --provider football-data > "$output_file" 2>&1; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        # Check if all 5 leagues were processed
        if grep -q "Processing 5 European leagues" "$output_file" && \
           grep -q "Successfully processed" "$output_file"; then
            record_test_result "Multiple Leagues Fetch" "PASS" "All 5 leagues processed in ${duration}s"
        else
            record_test_result "Multiple Leagues Fetch" "FAIL" "Not all leagues processed successfully"
        fi
    else
        record_test_result "Multiple Leagues Fetch" "FAIL" "Command failed with error. Check $output_file"
    fi
    
    print_info "Output saved to: $output_file"
}

# Test 3: Dry Run Mode
test_dry_run() {
    print_test_header "Dry Run Mode"
    
    local start_time=$(date +%s)
    local output_file="${OUTPUT_DIR}/test3_dry_run_${TIMESTAMP}.log"
    
    print_info "Running: python manage.py fetch_teams --league PL --dry-run"
    
    if python manage.py fetch_teams --league PL --dry-run > "$output_file" 2>&1; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        # Check for dry run indicators
        if grep -q "DRY RUN MODE\|Dry run\|dry-run" "$output_file" && \
           grep -q "No data will be saved\|No changes made" "$output_file"; then
            record_test_result "Dry Run Mode" "PASS" "Dry run completed successfully in ${duration}s"
        else
            record_test_result "Dry Run Mode" "FAIL" "Dry run mode not properly indicated"
        fi
    else
        record_test_result "Dry Run Mode" "FAIL" "Command failed with error. Check $output_file"
    fi
    
    print_info "Output saved to: $output_file"
}

# Test 4: Error Handling (Invalid League)
test_error_handling() {
    print_test_header "Error Handling (Invalid League)"
    
    local start_time=$(date +%s)
    local output_file="${OUTPUT_DIR}/test4_error_handling_${TIMESTAMP}.log"
    
    print_info "Running: python manage.py fetch_teams --league INVALID --provider football-data"
    
    # This test expects failure, so we invert the logic
    python manage.py fetch_teams --league INVALID --provider football-data > "$output_file" 2>&1
    local exit_code=$?
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # Check if error was handled gracefully
    if grep -q "Error\|error\|Failed\|failed" "$output_file" && \
       [ $exit_code -ne 0 ]; then
        record_test_result "Error Handling" "PASS" "Invalid input handled gracefully in ${duration}s"
    else
        record_test_result "Error Handling" "FAIL" "Error not properly handled"
    fi
    
    print_info "Output saved to: $output_file"
}

# Test 5: Database Validation
test_database_validation() {
    print_test_header "Database Validation"
    
    print_info "Checking recently created teams..."
    
    # Note: This requires psql or similar database access
    # Uncomment if you have database CLI access configured
    
    # local count=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM teams WHERE created_at > NOW() - INTERVAL '10 minutes';" 2>&1)
    
    # if [ $? -eq 0 ] && [ "$count" -gt 0 ]; then
    #     record_test_result "Database Validation" "PASS" "Found $count teams created in last 10 minutes"
    # else
    #     record_test_result "Database Validation" "FAIL" "Could not verify database state"
    # fi
    
    print_warning "Database validation skipped - requires direct database access"
    record_test_result "Database Validation" "SKIP" "Manual verification required (see MANUAL_TEST_GUIDE.md)"
}

# Generate final report
generate_report() {
    print_header "Generating Test Report"
    
    cat >> "$REPORT_FILE" << EOF

| Metric | Value |
|--------|-------|
| Total Tests | $TESTS_TOTAL |
| Passed | $TESTS_PASSED |
| Failed | $TESTS_FAILED |
| Success Rate | $(awk "BEGIN {printf \"%.1f\", ($TESTS_PASSED/$TESTS_TOTAL)*100}")% |

---

## Overall Status

EOF
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo "✅ **ALL TESTS PASSED**" >> "$REPORT_FILE"
        print_success "All tests passed!"
    else
        echo "❌ **SOME TESTS FAILED**" >> "$REPORT_FILE"
        print_error "$TESTS_FAILED test(s) failed"
    fi
    
    cat >> "$REPORT_FILE" << EOF

---

## Next Steps

EOF
    
    if [ $TESTS_FAILED -eq 0 ]; then
        cat >> "$REPORT_FILE" << EOF
1. Mark Phase 9.2 as complete in PROJECT_STATUS.md
2. Update feature status to 100%
3. Commit test results and report
4. Move to next feature or documentation phase
EOF
    else
        cat >> "$REPORT_FILE" << EOF
1. Review failed test logs in \`${OUTPUT_DIR}\`
2. Fix identified issues
3. Re-run tests with: \`./run_e2e_tests.sh\`
4. Update PROJECT_STATUS.md when all tests pass
EOF
    fi
    
    cat >> "$REPORT_FILE" << EOF

---

**Generated**: $(date)
**Report Location**: \`${REPORT_FILE}\`
**Test Logs**: \`${OUTPUT_DIR}/\`
EOF
    
    print_success "Report generated: $REPORT_FILE"
}

# Display final summary
display_summary() {
    echo ""
    print_header "TEST SUMMARY"
    echo ""
    echo -e "${CYAN}Total Tests:${NC}  $TESTS_TOTAL"
    echo -e "${GREEN}Passed:${NC}       $TESTS_PASSED"
    echo -e "${RED}Failed:${NC}       $TESTS_FAILED"
    echo -e "${BLUE}Success Rate:${NC} $(awk "BEGIN {printf \"%.1f\", ($TESTS_PASSED/$TESTS_TOTAL)*100}")%"
    echo ""
    echo -e "${CYAN}📄 Full Report:${NC} $REPORT_FILE"
    echo -e "${CYAN}📁 Test Logs:${NC}   $OUTPUT_DIR/"
    echo ""
}

# Main execution
main() {
    print_header "🧪 Teams API E2E Test Suite"
    echo ""
    
    check_prerequisites
    setup_test_environment
    
    # Parse command line arguments
    RUN_ALL=true
    QUICK_MODE=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --test)
                RUN_ALL=false
                TEST_NAME="$2"
                shift 2
                ;;
            --quick)
                QUICK_MODE=true
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Usage: $0 [--test single|multiple|dry-run|error] [--quick]"
                exit 1
                ;;
        esac
    done
    
    # Run tests based on arguments
    if [ "$QUICK_MODE" = true ]; then
        print_info "Running in quick mode (single test only)"
        test_single_league
    elif [ "$RUN_ALL" = true ]; then
        test_single_league
        sleep 2  # Brief pause between tests
        test_dry_run
        sleep 2
        test_error_handling
        sleep 2
        # Uncomment to run full test suite (uses more API requests)
        # print_warning "Skipping multiple leagues test to conserve API quota"
        # print_info "Run with: ./run_e2e_tests.sh --test multiple"
        test_database_validation
    else
        case $TEST_NAME in
            single)
                test_single_league
                ;;
            multiple)
                test_multiple_leagues
                ;;
            dry-run)
                test_dry_run
                ;;
            error)
                test_error_handling
                ;;
            *)
                print_error "Unknown test: $TEST_NAME"
                exit 1
                ;;
        esac
    fi
    
    generate_report
    display_summary
    
    # Exit with appropriate code
    if [ $TESTS_FAILED -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}

# Run main function
main "$@"
