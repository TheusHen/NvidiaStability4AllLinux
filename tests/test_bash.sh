#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

source "$PROJECT_ROOT/bin/nvidia-stability.sh"

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

assert_equals() {
    local expected="$1"
    local actual="$2"
    local message="$3"

    TESTS_RUN=$((TESTS_RUN + 1))

    if [[ "$expected" == "$actual" ]]; then
        echo -e "${GREEN}[PASS]${NC} $message"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}[FAIL]${NC} $message"
        echo "  Expected: $expected"
        echo "  Actual: $actual"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

assert_contains() {
    local haystack="$1"
    local needle="$2"
    local message="$3"

    TESTS_RUN=$((TESTS_RUN + 1))

    if [[ "$haystack" == *"$needle"* ]]; then
        echo -e "${GREEN}[PASS]${NC} $message"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}[FAIL]${NC} $message"
        echo "  String does not contain: $needle"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

assert_not_empty() {
    local value="$1"
    local message="$2"

    TESTS_RUN=$((TESTS_RUN + 1))

    if [[ -n "$value" ]]; then
        echo -e "${GREEN}[PASS]${NC} $message"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}[FAIL]${NC} $message"
        echo "  Value is empty"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

test_detect_distro_returns_values() {
    echo "Testing detect_distro..."
    local result
    result=$(detect_distro)

    IFS='|' read -r distro_id distro_name distro_version distro_family <<< "$result"

    assert_not_empty "$distro_id" "detect_distro returns distro_id"
    assert_not_empty "$distro_family" "detect_distro returns distro_family"
}

test_get_gpu_specs_rtx_4090() {
    echo "Testing get_gpu_specs for RTX 4090..."
    local result
    result=$(get_gpu_specs "RTX 4090")

    IFS='|' read -r tdp mem_clock graphics_clock <<< "$result"

    assert_equals "450" "$tdp" "RTX 4090 TDP is 450W"
    assert_equals "1313" "$mem_clock" "RTX 4090 mem_clock is 1313"
    assert_equals "2520" "$graphics_clock" "RTX 4090 graphics_clock is 2520"
}

test_get_gpu_specs_rtx_3080() {
    echo "Testing get_gpu_specs for RTX 3080..."
    local result
    result=$(get_gpu_specs "RTX 3080")

    IFS='|' read -r tdp mem_clock graphics_clock <<< "$result"

    assert_equals "320" "$tdp" "RTX 3080 TDP is 320W"
    assert_equals "1188" "$mem_clock" "RTX 3080 mem_clock is 1188"
    assert_equals "1710" "$graphics_clock" "RTX 3080 graphics_clock is 1710"
}

test_get_gpu_specs_gtx_1080() {
    echo "Testing get_gpu_specs for GTX 1080..."
    local result
    result=$(get_gpu_specs "GTX 1080")

    IFS='|' read -r tdp mem_clock graphics_clock <<< "$result"

    assert_equals "180" "$tdp" "GTX 1080 TDP is 180W"
    assert_equals "1251" "$mem_clock" "GTX 1080 mem_clock is 1251"
    assert_equals "1733" "$graphics_clock" "GTX 1080 graphics_clock is 1733"
}

test_get_gpu_specs_gtx_1660_super() {
    echo "Testing get_gpu_specs for GTX 1660 SUPER..."
    local result
    result=$(get_gpu_specs "GTX 1660 SUPER")

    IFS='|' read -r tdp mem_clock graphics_clock <<< "$result"

    assert_equals "125" "$tdp" "GTX 1660 SUPER TDP is 125W"
    assert_equals "1750" "$mem_clock" "GTX 1660 SUPER mem_clock is 1750"
    assert_equals "1785" "$graphics_clock" "GTX 1660 SUPER graphics_clock is 1785"
}

test_get_gpu_specs_unknown() {
    echo "Testing get_gpu_specs for unknown GPU..."
    local result
    result=$(get_gpu_specs "Unknown GPU")

    IFS='|' read -r tdp mem_clock graphics_clock <<< "$result"

    assert_equals "150" "$tdp" "Unknown GPU defaults to 150W TDP"
    assert_equals "1000" "$mem_clock" "Unknown GPU defaults to 1000 mem_clock"
    assert_equals "1500" "$graphics_clock" "Unknown GPU defaults to 1500 graphics_clock"
}

test_log_functions_exist() {
    echo "Testing log functions exist..."

    local output
    output=$(log_info "test" 2>&1)
    assert_contains "$output" "test" "log_info works"

    output=$(log_warn "warning" 2>&1)
    assert_contains "$output" "warning" "log_warn works"

    output=$(log_error "error" 2>&1)
    assert_contains "$output" "error" "log_error works"
}

run_all_tests() {
    echo "========================================"
    echo "Running Bash Unit Tests"
    echo "========================================"
    echo ""

    test_detect_distro_returns_values
    echo ""

    test_get_gpu_specs_rtx_4090
    echo ""

    test_get_gpu_specs_rtx_3080
    echo ""

    test_get_gpu_specs_gtx_1080
    echo ""

    test_get_gpu_specs_gtx_1660_super
    echo ""

    test_get_gpu_specs_unknown
    echo ""

    test_log_functions_exist
    echo ""

    echo "========================================"
    echo "Test Summary"
    echo "========================================"
    echo "Tests Run: $TESTS_RUN"
    echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
    echo ""

    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}All tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}Some tests failed!${NC}"
        exit 1
    fi
}

run_all_tests
