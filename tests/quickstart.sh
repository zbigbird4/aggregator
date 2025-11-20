#!/bin/bash

# Aggregator Functional Test - Quick Start Script
# This script automates the complete testing workflow

set -e

PROJECT_DIR="/home/engine/project"
TESTS_DIR="$PROJECT_DIR/tests"
OUTPUT_DIR="$TESTS_DIR/output"
LOGS_DIR="$TESTS_DIR/logs"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Aggregator Functional Test - Quick Start${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo

# Check if we're in the right directory
if [ ! -d "$TESTS_DIR" ]; then
    echo -e "${RED}Error: Tests directory not found at $TESTS_DIR${NC}"
    exit 1
fi

cd "$PROJECT_DIR"

# Step 1: Create necessary directories
echo -e "${BLUE}Step 1: Setting up directories...${NC}"
mkdir -p "$OUTPUT_DIR" "$LOGS_DIR"
echo -e "${GREEN}✓ Directories ready${NC}"
echo

# Step 2: Install dependencies (if needed)
echo -e "${BLUE}Step 2: Checking dependencies...${NC}"
if ! python3 -c "import tqdm" 2>/dev/null; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install --break-system-packages -q -r requirements.txt
fi
echo -e "${GREEN}✓ Dependencies ready${NC}"
echo

# Step 3: Generate test data (if not exists)
echo -e "${BLUE}Step 3: Preparing test data...${NC}"
if [ ! -f "$TESTS_DIR/data/test_proxies_100.json" ]; then
    echo "Generating test proxy dataset..."
    python3 "$TESTS_DIR/generate_test_proxies.py"
fi
echo -e "${GREEN}✓ Test data ready${NC}"
echo

# Step 4: Run functional test
echo -e "${BLUE}Step 4: Running functional test...${NC}"
echo "This may take a few moments..."
python3 "$TESTS_DIR/run_functional_test.py" 2>&1 | tee "$LOGS_DIR/test_execution.log"
TEST_EXIT=$?

if [ $TEST_EXIT -eq 0 ]; then
    echo -e "${GREEN}✓ Functional test passed${NC}"
else
    echo -e "${RED}✗ Functional test failed${NC}"
    exit $TEST_EXIT
fi
echo

# Step 5: Generate HTML report
echo -e "${BLUE}Step 5: Generating HTML report...${NC}"
python3 "$TESTS_DIR/generate_html_report.py"
echo -e "${GREEN}✓ HTML report generated${NC}"
echo

# Step 6: Display summary
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Test Execution Complete!${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo

echo "📊 Output Files:"
echo "  • Text Report:     $OUTPUT_DIR/test_report.txt"
echo "  • HTML Report:     $OUTPUT_DIR/test_report.html"
echo "  • Verified Data:   $OUTPUT_DIR/verified_proxies.json"
echo "  • Tested Data:     $OUTPUT_DIR/tested_proxies.json"
echo "  • Final Data:      $OUTPUT_DIR/final_proxies.json"
echo "  • Clash Config:    $OUTPUT_DIR/clash.yaml"
echo "  • Execution Log:   $LOGS_DIR/test_execution.log"
echo

# Read test results
if [ -f "$OUTPUT_DIR/test_report.txt" ]; then
    echo "📈 Key Metrics:"
    grep -E "Overall Pass Rate|Final Proxies|Execution Time" "$OUTPUT_DIR/test_report.txt" | sed 's/^/  /'
fi

echo
echo "💡 Next steps:"
echo "  1. View the HTML report: $OUTPUT_DIR/test_report.html"
echo "  2. Review test results: cat $OUTPUT_DIR/test_report.txt"
echo "  3. Check output proxies: jq '.[0]' $OUTPUT_DIR/final_proxies.json"
echo "  4. Test with Clash: clash -f $OUTPUT_DIR/clash.yaml"
echo

echo -e "${GREEN}All tests completed successfully!${NC}"
